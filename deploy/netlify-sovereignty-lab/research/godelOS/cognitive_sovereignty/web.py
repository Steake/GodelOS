"""Dependency-free web dashboard and chat server for the sovereignty agent."""

from __future__ import annotations

import argparse
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .engine import CognitiveSovereigntyEngine
from .evolution import EvolutionEngine
from .evolution_store import EvolutionStore
from .models import new_id
from .provider import deepseek_provider_from_env
from .store import SovereigntyStore
from .values import ValueProfile, constraint_violations


STATIC_ROOT = Path(__file__).with_name("web_assets")


class DashboardApplication:
    def __init__(
        self, db_path: str, agent_id: str, summary_path: str | None = None,
        chamber_summary_path: str | None = None,
    ):
        self.db_path = db_path
        self.agent_id = agent_id
        self.summary_path = Path(summary_path) if summary_path else None
        self.chamber_summary_path = Path(chamber_summary_path) if chamber_summary_path else None
        self.provider = deepseek_provider_from_env()
        self.engine = CognitiveSovereigntyEngine(SovereigntyStore(db_path), self.provider)
        self.evolution_store = EvolutionStore(db_path)

    def snapshot(self) -> dict[str, Any]:
        state = self.engine.state(self.agent_id).to_mapping()
        summary = None
        if self.summary_path and self.summary_path.exists():
            summary = json.loads(self.summary_path.read_text(encoding="utf-8"))
        chamber = None
        if self.chamber_summary_path and self.chamber_summary_path.exists():
            chamber = json.loads(self.chamber_summary_path.read_text(encoding="utf-8"))
        objects = self.evolution_store.objects()
        return {
            "agent": state,
            "state_version": self.engine.store.version(self.agent_id),
            "event_chain_valid": self.engine.store.verify_event_chain(self.agent_id),
            "events": self.engine.history(self.agent_id)[-30:],
            "evolution_objects": objects,
            "experiment": summary,
            "chamber": chamber,
        }

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.engine.chat(
            self.agent_id, str(payload.get("person_id", "web-user")),
            str(payload["message"]), str(payload.get("person_name", "Oli")),
        )

    def think(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.engine.think(self.agent_id, str(payload.get("mode", "deliberation")))

    def save_candidate(self, payload: dict[str, Any]) -> dict[str, Any]:
        profile = ValueProfile(
            profile_id=str(payload.get("profile_id") or new_id("manual-profile")),
            name=str(payload.get("name") or "Manual candidate"), values=dict(payload["values"]),
            rationale=str(payload.get("rationale") or "Created in the value lab."),
            parent_profile_id=str(payload.get("parent_profile_id") or "parent-balanced-v1"),
        )
        violations = constraint_violations(profile)
        self.evolution_store.put_object(profile.profile_id, "manual_value_candidate", profile.to_mapping())
        return {"profile": profile.to_mapping(), "constraint_violations": violations, "saved": True}

    def calibrate(self, payload: dict[str, Any]) -> dict[str, Any]:
        experiment_id = str(payload.get("experiment_id") or new_id("web-calibration"))
        output_dir = str(payload.get("output_dir") or f"research_artifacts/cognitive_sovereignty/{experiment_id}")
        return EvolutionEngine(self.db_path, self.provider, int(payload.get("concurrency", 6))).run_experiment(
            self.agent_id, experiment_id, int(payload.get("calibration_replicates", 2)),
            int(payload.get("holdout_replicates", 3)), output_dir,
        )


def handler_factory(application: DashboardApplication):
    class Handler(BaseHTTPRequestHandler):
        server_version = "GodelOSSovereignty/1.0"

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"[web] {self.address_string()} {fmt % args}")

        def _json(self, value: Any, status: int = 200) -> None:
            body = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers(); self.wfile.write(body)

        def _body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            value = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(value, dict):
                raise ValueError("request body must be a JSON object")
            return value

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            try:
                if path == "/api/snapshot":
                    self._json(application.snapshot()); return
                if path in {"/", "/index.html"}:
                    body = (STATIC_ROOT / "index.html").read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers(); self.wfile.write(body); return
                self._json({"error": "not found"}, 404)
            except Exception as exc:
                self._json({"error": f"{type(exc).__name__}: {exc}"}, 500)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            try:
                payload = self._body()
                if path == "/api/chat":
                    if not str(payload.get("message", "")).strip():
                        raise ValueError("message is required")
                    self._json(application.chat(payload)); return
                if path == "/api/think":
                    self._json(application.think(payload)); return
                if path == "/api/value-profile":
                    self._json(application.save_candidate(payload), HTTPStatus.CREATED); return
                if path == "/api/calibrate":
                    self._json(application.calibrate(payload), HTTPStatus.CREATED); return
                self._json({"error": "not found"}, 404)
            except (KeyError, ValueError) as exc:
                self._json({"error": str(exc)}, 422)
            except Exception as exc:
                self._json({"error": f"{type(exc).__name__}: {exc}"}, 500)

    return Handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cognitive sovereignty web dashboard")
    parser.add_argument("--db", default=os.getenv("SOVEREIGNTY_DB_PATH", "runtime/cognitive_sovereignty.sqlite3"))
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--summary")
    parser.add_argument("--chamber-summary")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--export-snapshot", help="write a standalone read-only dashboard snapshot")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    application = DashboardApplication(args.db, args.agent_id, args.summary, args.chamber_summary)
    if args.export_snapshot:
        output = Path(args.export_snapshot)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise FileExistsError(f"refusing to overwrite snapshot: {output}")
        source = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        payload = json.dumps(application.snapshot(), ensure_ascii=False).replace("</", "<\\/")
        source = source.replace("</head>", f"<script>window.__SOVEREIGNTY_SNAPSHOT__={payload};</script></head>")
        output.write_text(source, encoding="utf-8")
        print(output)
        return 0
    server = ThreadingHTTPServer((args.host, args.port), handler_factory(application))
    print(f"Cognitive Sovereignty dashboard: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
