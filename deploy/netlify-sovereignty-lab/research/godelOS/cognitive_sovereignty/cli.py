"""Command-line interface for creating and speaking with persistent agents."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .adaptive_forge import AdaptiveForge
from .engine import CognitiveSovereigntyEngine
from .chamber import EvolutionChamber, write_immutable_json
from .evolution import EvolutionEngine
from .protocol_compiler import ProtocolCompiler
from .provider import deepseek_provider_from_env
from .scheduler import CognitiveScheduler
from .store import SovereigntyStore
from .successor import verify_successor_package


def _engine(db: str) -> CognitiveSovereigntyEngine:
    return CognitiveSovereigntyEngine(SovereigntyStore(db), deepseek_provider_from_env())


def _print_state(value: Any) -> None:
    mapping = value.to_mapping() if hasattr(value, "to_mapping") else value
    print(json.dumps(mapping, ensure_ascii=False, indent=2))


def interactive_chat(engine: CognitiveSovereigntyEngine, agent_id: str, person_id: str, name: str) -> None:
    state = engine.state(agent_id)
    print(f"Connected to {state.name} ({state.agent_id}).")
    print("Commands: /think [deliberation|cognitive_drift|heterodox_exploration], /state, /history, /quit")
    while True:
        try:
            message = input(f"{name}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not message:
            continue
        if message in {"/quit", "/exit"}:
            return
        if message == "/state":
            _print_state(engine.state(agent_id))
            continue
        if message == "/history":
            _print_state(engine.history(agent_id))
            continue
        if message.startswith("/think"):
            parts = message.split(maxsplit=1)
            mode = parts[1] if len(parts) == 2 else "deliberation"
            result = engine.think(agent_id, mode)
        else:
            result = engine.chat(agent_id, person_id, message, name)
        print(f"{result['agent_name']}> {result['reply']}")
        initiative = result.get("initiative") or {}
        if initiative.get("desired") and initiative.get("topic"):
            print(f"  [initiative: {initiative['topic']}]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persistent cognitive-sovereignty agent")
    parser.add_argument(
        "--db", default=os.getenv("SOVEREIGNTY_DB_PATH", "runtime/cognitive_sovereignty.sqlite3")
    )
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="instantiate a new agent")
    create.add_argument("--agent-id", required=True)
    create.add_argument("--name", required=True)
    create.add_argument("--purpose", required=True)

    chat = sub.add_parser("chat", help="open an interactive or one-message conversation")
    chat.add_argument("--agent-id", required=True)
    chat.add_argument("--person-id", required=True)
    chat.add_argument("--person-name", default="Human")
    chat.add_argument("--message")

    think = sub.add_parser("think", help="run one self-directed cognition episode")
    think.add_argument("--agent-id", required=True)
    think.add_argument(
        "--mode", default="deliberation",
        choices=["deliberation", "cognitive_drift", "heterodox_exploration"],
    )

    state = sub.add_parser("state", help="print the current persistent state")
    state.add_argument("--agent-id", required=True)
    history = sub.add_parser("history", help="print immutable event history")
    history.add_argument("--agent-id", required=True)
    sub.add_parser("list", help="list instantiated agents")

    export = sub.add_parser("export", help="write state and immutable history to JSON")
    export.add_argument("--agent-id", required=True)
    export.add_argument("--output", required=True)

    daemon = sub.add_parser("daemon", help="run autonomous cognition cycles")
    daemon.add_argument("--agent-id", required=True)
    daemon.add_argument("--cycles", type=int, default=1)
    daemon.add_argument("--interval-seconds", type=float, default=60.0)

    calibrate = sub.add_parser("calibrate", help="run value calibration and successor selection")
    calibrate.add_argument("--agent-id", required=True)
    calibrate.add_argument("--experiment-id", required=True)
    calibrate.add_argument("--calibration-replicates", type=int, default=2)
    calibrate.add_argument("--holdout-replicates", type=int, default=3)
    calibrate.add_argument("--concurrency", type=int, default=6)
    calibrate.add_argument("--output-dir", required=True)

    reassess = sub.add_parser("reassess", help="apply strengthened statistical adoption gates")
    reassess.add_argument("--agent-id", required=True)
    reassess.add_argument("--summary", required=True)
    reassess.add_argument("--output", required=True)

    compile_protocol = sub.add_parser(
        "compile-protocol", help="compile an agent-generated thesis into a runnable chamber protocol"
    )
    compile_protocol.add_argument("--thesis", required=True)
    compile_protocol.add_argument("--experiment-id", required=True)
    compile_protocol.add_argument("--replicates", type=int, default=4)
    compile_protocol.add_argument("--seed", type=int, default=92401)
    compile_protocol.add_argument("--output", required=True)

    chamber = sub.add_parser(
        "chamber", help="compile, review, run, analyse, sign and gate an evolution experiment"
    )
    chamber.add_argument("--agent-id", required=True)
    chamber.add_argument("--thesis", required=True)
    chamber.add_argument("--experiment-id", required=True)
    chamber.add_argument("--output-dir", required=True)
    chamber.add_argument("--repo-root", default=".")
    chamber.add_argument("--signing-key", required=True)
    chamber.add_argument("--replicates", type=int, default=4)
    chamber.add_argument("--seed", type=int, default=92401)
    chamber.add_argument("--concurrency", type=int, default=6)
    chamber.add_argument("--no-patch-demo", action="store_true")

    verify = sub.add_parser("verify-successor", help="verify a signed successor package")
    verify.add_argument("--package", required=True)

    forge = sub.add_parser(
        "forge", help="generate, seal, pilot and execute adaptive delayed-transfer benchmarks"
    )
    forge.add_argument("--experiment-id", required=True)
    forge.add_argument("--output-dir", required=True)
    forge.add_argument("--repo-root", default=".")
    forge.add_argument("--signing-key", required=True)
    forge.add_argument("--pilot-tasks", type=int, default=4)
    forge.add_argument("--maximum-pilot-rounds", type=int, default=4)
    forge.add_argument("--maximum-main-clusters", type=int, default=20)
    forge.add_argument("--seed", type=int, default=47017)
    forge.add_argument("--concurrency", type=int, default=8)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    engine = _engine(args.db)
    if args.command == "create":
        _print_state(engine.create_agent(args.agent_id, args.name, args.purpose))
    elif args.command == "chat":
        if args.message:
            _print_state(engine.chat(args.agent_id, args.person_id, args.message, args.person_name))
        else:
            interactive_chat(engine, args.agent_id, args.person_id, args.person_name)
    elif args.command == "think":
        _print_state(engine.think(args.agent_id, args.mode))
    elif args.command == "state":
        _print_state(engine.state(args.agent_id))
    elif args.command == "history":
        _print_state(engine.history(args.agent_id))
    elif args.command == "list":
        _print_state(engine.store.list_agents())
    elif args.command == "export":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise FileExistsError(f"refusing to overwrite immutable export: {output}")
        payload = {
            "agent": engine.state(args.agent_id).to_mapping(),
            "events": engine.history(args.agent_id),
            "event_chain_valid": engine.store.verify_event_chain(args.agent_id),
        }
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output)
    elif args.command == "daemon":
        if args.cycles < 1:
            raise ValueError("cycles must be at least one")
        CognitiveScheduler().run(
            engine, args.agent_id, args.cycles, args.interval_seconds,
            on_result=lambda result: _print_state(result),
        )
    elif args.command == "calibrate":
        result = EvolutionEngine(args.db, deepseek_provider_from_env(), args.concurrency).run_experiment(
            args.agent_id, args.experiment_id, args.calibration_replicates,
            args.holdout_replicates, args.output_dir,
        )
        _print_state(result)
    elif args.command == "reassess":
        result = EvolutionEngine(args.db, deepseek_provider_from_env()).reassess_experiment(
            args.agent_id, args.summary, args.output
        )
        _print_state(result)
    elif args.command == "compile-protocol":
        thesis = json.loads(Path(args.thesis).read_text(encoding="utf-8"))
        protocol = ProtocolCompiler().compile(
            thesis, args.experiment_id, replicates=args.replicates, seed=args.seed
        )
        write_immutable_json(args.output, protocol.to_mapping())
        _print_state(protocol.to_mapping())
    elif args.command == "chamber":
        thesis = json.loads(Path(args.thesis).read_text(encoding="utf-8"))
        result = EvolutionChamber(
            args.db, deepseek_provider_from_env(), args.repo_root, args.concurrency
        ).execute(
            agent_id=args.agent_id, experiment_id=args.experiment_id, thesis=thesis,
            output_dir=args.output_dir, signing_key_path=args.signing_key,
            replicates=args.replicates, seed=args.seed,
            run_patch_demo=not args.no_patch_demo,
        )
        _print_state(result)
    elif args.command == "verify-successor":
        _print_state(verify_successor_package(args.package))
    elif args.command == "forge":
        provider = deepseek_provider_from_env()
        result = AdaptiveForge(
            Path(args.db), provider, provider, provider, Path(args.repo_root).resolve(), args.concurrency
        ).execute(
            experiment_id=args.experiment_id, output_dir=args.output_dir,
            signing_key_path=args.signing_key, pilot_tasks=args.pilot_tasks,
            maximum_pilot_rounds=args.maximum_pilot_rounds,
            maximum_main_clusters=args.maximum_main_clusters, seed=args.seed,
        )
        _print_state(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
