"""Export a stopped forge pilot without modifying its raw database or seals."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from godelOS.cognitive_sovereignty.adaptive_forge import analyse_forge_runs, write_once
from godelOS.cognitive_sovereignty.evolution_store import EvolutionStore
from godelOS.cognitive_sovereignty.models import stable_hash, utc_now


def finalize(output, experiment_id):
    pilot = json.loads((output / 'pilot-summary.json').read_text())
    power_path = output / 'power-plan.json'
    power = json.loads(power_path.read_text()) if power_path.exists() else None
    store = EvolutionStore(output / 'evolution.sqlite3')
    runs = [run for r in pilot['rounds'] for run in store.chamber_runs(r['experiment_id'])]
    for run in runs:
        write_once(output / 'raw_runs' / (run['run_id'] + '.json'), run)
    authors = [json.loads(p.read_text()) for p in sorted((output / 'authoring').rglob('*.json'))]
    analysis = analyse_forge_runs(runs)
    calls = sum(r['attempts'] for r in runs) + sum(len(a['attempts']) for a in authors)
    summary = {
        'experiment_id': experiment_id, 'created_at': utc_now(), 'status': 'HOLD',
        'explanation': 'Pilot calibrated; main study blocked by the cluster-power budget.' if pilot['eligible'] else 'Pilot did not reach its registered accuracy band.',
        'pilot': pilot, 'power': power, 'analysis': analysis,
        'execution': {'author_tasks': len(authors), 'solver_phases': len(runs), 'recorded_call_attempts': calls, 'main_study_calls': 0},
        'promotion': {'decision': 'hold', 'active_loop_entry': False, 'failed_checks': ['main-study-not-executed']},
        'limitations': [
            'Analysis aggregates adaptive pilot rounds and is not a confirmatory treatment comparison.',
            'Identity-bearing and no-state branches were registered but not executed: the main-study gate stopped them.',
            'Power is a normal-approximation planning heuristic from only four selected pilot clusters, not a validated paired-difference variance estimate.',
            'Authenticity labels are disclosed: this tests provenance use, not cryptographic forgery discovery.',
            'Author and solver share a model family. Author-proposed answer keys lack independent validation.',
            'Retry failures in this collection retain errors but may not retain invalid raw model responses.',
        ],
    }
    summary['summary_sha256'] = stable_hash(summary)
    write_once(output / 'experiment-summary.json', summary)
    print(json.dumps({'calls': calls, 'phases': len(runs), 'promotion': 'hold'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--experiment-id', default='deepseek-adaptive-forge-v4')
    args = parser.parse_args()
    finalize(args.output, args.experiment_id)
