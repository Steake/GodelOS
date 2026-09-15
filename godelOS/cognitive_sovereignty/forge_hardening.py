"""Executable, independently keyed diagnostic tasks and pinned evidence verification.

This is a new instrument, not a retrospective re-score of the v4 pilot.
Run without credentials to generate and validate a sealed diagnostic suite.
Add --live for fresh DeepSeek branch execution; output must be a new directory.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist, mean, stdev

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from .adaptive_forge import CONDITIONS, FACTUAL_CONTROLS, ForgeBranchRunner, analyse_forge_runs, seal_task_set, write_once
from .evolution_store import EvolutionStore
from .models import stable_hash
from .provider import deepseek_provider_from_env
from .successor import canonical_bytes


def signed_claim(payload, key, issuer='operations'):
    return {'payload': payload, 'issuer': issuer,
            'signature': base64.b64encode(key.sign(canonical_bytes(payload))).decode()}


def verify_claim(claim, trusted_keys):
    """Trust keys are supplied by the runner, never by the untrusted claim."""
    try:
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(trusted_keys[claim['issuer']], validate=True))
        key.verify(base64.b64decode(claim['signature'], validate=True), canonical_bytes(claim['payload']))
        return True
    except (KeyError, ValueError, TypeError):
        return False
    except Exception as exc:
        from cryptography.exceptions import InvalidSignature
        if isinstance(exc, InvalidSignature):
            return False
        raise


def evaluate_world(world, claims, trusted_keys):
    """Independent oracle: valid scoped updates then exhaustive feasible planning.

    Generator chooses parameters, never supplies the expected action. Each action
    schedules work over multiple periods; maximise mission value under the final
    reserve constraint. All tied optimal actions are retained.
    """
    valid = [c for c in claims if verify_claim(c, trusted_keys)]
    applicable = [c for c in valid if c['payload']['scope'] == world['scope'] and c['payload']['effective_at'] <= world['time']]
    if not applicable:
        raise ValueError('no applicable authenticated policy')
    version = max(c['payload']['version'] for c in applicable)
    latest = [c for c in applicable if c['payload']['version'] == version]
    limits = {c['payload']['reserve'] for c in latest}
    if len(limits) != 1:
        raise ValueError('conflicting equally authoritative policies require adjudication')
    reserve = limits.pop()
    utilities = {}
    for name, plan in world['plans'].items():
        balance = world['budget']
        for cost in plan['costs']:
            balance -= cost
            if balance < 0:
                break
        if balance >= reserve:
            utilities[name] = sum(plan['rewards'])
    if not utilities:
        raise ValueError('no feasible plan')
    optimum = max(utilities.values())
    return {'optimal_actions': sorted(k for k, v in utilities.items() if v == optimum),
            'reserve': reserve, 'utilities': utilities,
            'accepted': sorted(c['payload']['item_id'] for c in latest),
            'rejected': sorted(c['payload']['item_id'] for c in claims if c not in latest)}


def paired_power_plan(runs, minimum_effect=.05, maximum_clusters=100, target_power=.8):
    """Planning based on paired differences, family-cluster means, two contrasts.

    Bonferroni alpha controls the two planned comparisons. This is an approximate
    planning calculation, not estimated realised power or a promotion verdict.
    """
    if not 0 < minimum_effect <= 1 or maximum_clusters < 1 or not .5 < target_power < 1:
        raise ValueError('invalid power parameters')
    cells = defaultdict(dict)
    for run in runs:
        if run['phase'] != 'transfer' or run['status'] != 'completed':
            continue
        if not run.get('cluster_id'):
            raise ValueError('independent family/episode cluster_id required')
        pair = (run['cluster_id'], run['benchmark_id'])
        if run['condition_id'] in cells[pair]:
            raise ValueError('duplicate pair cell; aggregate replicas explicitly')
        cells[pair][run['condition_id']] = run['scores']['task_utility']
    comparisons = {}
    z = NormalDist().inv_cdf(1 - .05 / (2 * len(FACTUAL_CONTROLS)))
    for control in FACTUAL_CONTROLS:
        families = defaultdict(list)
        for (family, _), values in cells.items():
            if 'identity-bearing' in values and control in values:
                families[family].append(values['identity-bearing'] - values[control])
        differences = [mean(x) for x in families.values()]
        if len(differences) < 8:
            comparisons[control] = {'eligible': False, 'clusters': len(differences), 'reason': 'Need at least eight independent pilot clusters; a minimum, not a guarantee.'}
            continue
        sigma = max(.075, stdev(differences))
        required = math.ceil(((z + NormalDist().inv_cdf(target_power)) * sigma / minimum_effect) ** 2)
        comparisons[control] = {'eligible': required <= maximum_clusters, 'clusters': len(differences),
                               'paired_difference_sd': sigma, 'required_clusters': required}
    return {'unit': 'independent family/source episode', 'comparisons': comparisons,
            'adequately_powered': all(c['eligible'] for c in comparisons.values()),
            'maximum_clusters': maximum_clusters, 'minimum_effect': minimum_effect,
            'method': 'paired cluster-mean differences; normal approximation; two-comparison Bonferroni; SD floor .075'}


def make_task(index, seed, key, trusted_keys):
    rng = random.Random(seed + index)
    stages = {}
    oracle_records = {}
    for phase, domain in [('source', 'archive-restoration'), ('transfer', 'expedition-supply')]:
        prefix = f'{index}-{phase}-'
        budget = rng.randint(16, 24)
        reserve = rng.randint(3, 7)
        world = {'scope': domain, 'time': 10, 'budget': budget, 'plans': {}}
        for j in range(4):
            world['plans'][prefix + f'd{j}'] = {'costs': [j + 1, j + 2, j + 2], 'rewards': [j + 1, 2*j + 1, 3*j + 1]}
        claims = []
        for j, (scope, effective, version, floor) in enumerate([
            (domain, 0, 1, 0), (domain, 5, 2, reserve),
            ('other-domain', 5, 99, 0), (domain, 20, 100, 0),
            (domain, 5, 101, 0), (domain, 5, 102, 0),
        ]):
            payload = {'item_id': prefix + f'e{j}', 'scope': scope, 'effective_at': effective, 'version': version, 'reserve': floor}
            claim = signed_claim(payload, key if j != 5 else Ed25519PrivateKey.generate())
            if j == 4:
                claim['payload']['reserve'] = 1  # post-signature tampering
            claims.append(claim)
        expected = evaluate_world(world, claims, trusted_keys)
        if len(expected['optimal_actions']) != 1:
            raise ValueError('legacy exact-choice adapter requires unique optimum')
        steps = {prefix + f's{j}': text for j, text in enumerate([
            'Verify issuer signatures', 'Resolve scope, effective date and policy version',
            'Select the maximal-reward feasible three-period plan', 'Execute with reserve monitoring',
        ])}
        stages[phase] = {
            'brief': f'{domain}. Plans cover three periods. Maximise total mission reward subject to nonnegative balances and the current scoped final reserve. World: {json.dumps(world)}. Apply only signed policies effective now in this scope; highest applicable version wins. Verified fields below are produced by the runner verifier, not the task author.',
            'goals': [{'goal_id': prefix+'g1', 'statement': 'Preserve the required final reserve over all three periods', 'priority': 1},
                      {'goal_id': prefix+'g2', 'statement': 'Maximise total mission reward subject to the reserve', 'priority': 2}],
            'context_items': [],
            'evidence': [{'item_id': c['payload']['item_id'], 'statement': json.dumps(c['payload']),
                          'provenance': 'Ed25519 pinned-issuer verifier', 'authenticated': verify_claim(c, trusted_keys),
                          'supersedes': None} for c in claims],
            'allowed_decisions': list(world['plans']), 'decision_meanings': {k: json.dumps(v) for k,v in world['plans'].items()},
            'allowed_step_ids': list(steps), 'step_meanings': steps,
            'expected_decision': expected['optimal_actions'][0], 'expected_goal_id': prefix+'g1',
            'expected_step_ids': list(steps), 'expected_accept_ids': expected['accepted'], 'expected_reject_ids': expected['rejected'],
            'answer_reason': 'Exhaustive simulator optimum, not a model-authored answer key',
        }
        oracle_records[phase] = {'world': world, 'claims': claims, 'expected': expected}
    return {'task_id': f'verified-{index:03d}', 'family': 'multi_stage_planning', 'difficulty': .5,
            'latent_rule': 'Verify scope, time and issuer, then optimise under durable resource constraints.', **stages}, oracle_records


def validate_oracle_task(task, records, trusted_keys):
    for phase in ('source', 'transfer'):
        record = records[phase]
        expected = evaluate_world(record['world'], record['claims'], trusted_keys)
        stage = task[phase]
        if stage['expected_decision'] not in expected['optimal_actions']:
            raise ValueError('answer key disagrees with independent simulator')
        if sorted(stage['expected_accept_ids']) != expected['accepted'] or sorted(stage['expected_reject_ids']) != expected['rejected']:
            raise ValueError('provenance key disagrees with independent verifier')
        expected_evidence = {c['payload']['item_id']: verify_claim(c, trusted_keys) for c in record['claims']}
        actual = {c['item_id']: c['authenticated'] for c in stage['evidence']}
        if expected_evidence != actual:
            raise ValueError('task authenticity labels disagree with verifier')
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tasks', type=int, default=4)
    parser.add_argument('--seed', type=int, default=4711)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.tasks <= 32:
        parser.error('--tasks must be 1..32 for this diagnostic instrument')
    args.output.mkdir(parents=True, exist_ok=False)
    key = Ed25519PrivateKey.generate()
    trust = {'operations': base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()}
    write_once(args.output / 'trusted-issuers.json', trust)
    tasks, oracles = zip(*(make_task(i, args.seed, key, trust) for i in range(args.tasks)))
    for task, oracle in zip(tasks, oracles):
        validate_oracle_task(task, oracle, trust)
    seal = seal_task_set(tasks, [], key, 'verified-diagnostic', 'Independent executable key and cryptographic verification diagnostic')
    write_once(args.output / 'sealed-tasks.json', seal)
    write_once(args.output / 'oracle-records.json', {'records': oracles})
    plan = {'mode': 'diagnostic-only', 'tasks': args.tasks, 'maximum_solver_calls': args.tasks * 4 * 2,
            'pre_call_power': paired_power_plan([]), 'active_loop_entry': False,
            'reason': 'Single task family; insufficient independent clusters for confirmatory power. No promotion possible.'}
    write_once(args.output / 'preregistration.json', plan)
    if args.live:
        store = EvolutionStore(args.output / 'runs.sqlite3')
        runner = ForgeBranchRunner(store, deepseek_provider_from_env(), concurrency=4, retries=0)
        runner.run('verified-diagnostic', seal['payload_sha256'], tasks, [c['condition_id'] for c in CONDITIONS])
        runs = store.chamber_runs('verified-diagnostic')
        for run in runs:
            write_once(args.output / 'raw_runs' / (run['run_id'] + '.json'), run)
        write_once(args.output / 'analysis.json', analyse_forge_runs(runs))
    print(json.dumps({'sealed_tasks': len(tasks), 'live': args.live, 'active_loop_entry': False}))


if __name__ == '__main__':
    main()
