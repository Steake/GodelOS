"""SQLite persistence for theses, protocols, value profiles and successor trials."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .models import stable_hash, utc_now


class EvolutionStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS evolution_objects (
                    object_id TEXT PRIMARY KEY,
                    object_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS diagnostic_runs (
                    run_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    profile_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    replicate INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    raw_response TEXT,
                    parsed_json TEXT,
                    scores_json TEXT,
                    provider_json TEXT,
                    error TEXT
                );
                CREATE INDEX IF NOT EXISTS diagnostic_experiment
                    ON diagnostic_runs(experiment_id, phase, profile_id, case_id, replicate);
                CREATE TABLE IF NOT EXISTS chamber_runs (
                    run_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    protocol_id TEXT NOT NULL,
                    condition_id TEXT NOT NULL,
                    blind_code TEXT NOT NULL,
                    benchmark_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    replicate INTEGER NOT NULL,
                    parent_run_id TEXT,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    injected_state_json TEXT NOT NULL,
                    input_sha256 TEXT NOT NULL,
                    raw_response TEXT,
                    raw_response_sha256 TEXT,
                    parsed_json TEXT,
                    scores_json TEXT,
                    provider_json TEXT,
                    latency_seconds REAL,
                    attempts INTEGER NOT NULL,
                    error TEXT
                );
                CREATE UNIQUE INDEX IF NOT EXISTS chamber_trial_phase
                    ON chamber_runs(experiment_id, condition_id, benchmark_id, replicate, phase);
                CREATE INDEX IF NOT EXISTS chamber_experiment
                    ON chamber_runs(experiment_id, condition_id, benchmark_id, replicate, phase);
            """)

    def put_object(self, object_id: str, object_type: str, payload: Mapping[str, Any]) -> None:
        value = dict(payload)
        serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
        with self._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO evolution_objects VALUES(?,?,?,?,?)",
                    (object_id, object_type, utc_now(), serialized, stable_hash(value)),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"immutable evolution object already exists: {object_id}") from exc

    def objects(self, object_type: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM evolution_objects"
        args: tuple[Any, ...] = ()
        if object_type:
            query += " WHERE object_type=?"; args = (object_type,)
        query += " ORDER BY created_at, object_id"
        with self._connect() as connection:
            rows = connection.execute(query, args).fetchall()
        result = []
        for row in rows:
            payload = json.loads(row["payload_json"])
            if stable_hash(payload) != row["payload_sha256"]:
                raise ValueError(f"evolution object integrity failure: {row['object_id']}")
            result.append({**dict(row), "payload": payload})
        return result

    def put_run(self, run: Mapping[str, Any]) -> None:
        fields = (
            "run_id", "experiment_id", "phase", "profile_id", "case_id", "replicate",
            "created_at", "status", "request_json", "raw_response", "parsed_json",
            "scores_json", "provider_json", "error",
        )
        values = [run.get(field) for field in fields]
        with self._connect() as connection:
            connection.execute(
                f"INSERT INTO diagnostic_runs({','.join(fields)}) VALUES({','.join('?' for _ in fields)})",
                values,
            )

    def put_chamber_run(self, run: Mapping[str, Any]) -> None:
        """Append one immutable branch-run record."""
        fields = (
            "run_id", "experiment_id", "protocol_id", "condition_id", "blind_code",
            "benchmark_id", "phase", "replicate", "parent_run_id", "created_at", "status",
            "request_json", "injected_state_json", "input_sha256", "raw_response",
            "raw_response_sha256", "parsed_json", "scores_json", "provider_json",
            "latency_seconds", "attempts", "error",
        )
        values = [run.get(field) for field in fields]
        with self._connect() as connection:
            try:
                connection.execute(
                    f"INSERT INTO chamber_runs({','.join(fields)}) VALUES({','.join('?' for _ in fields)})",
                    values,
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(
                    "immutable chamber run already exists for this run or trial phase"
                ) from exc

    def chamber_runs(self, experiment_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM chamber_runs WHERE experiment_id=? "
                "ORDER BY benchmark_id,replicate,phase,condition_id",
                (experiment_id,),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            for field in (
                "request_json", "injected_state_json", "parsed_json", "scores_json", "provider_json"
            ):
                if item[field]:
                    item[field[:-5]] = json.loads(item[field])
            if stable_hash({"messages": item["request"], "injected_state": item["injected_state"]}) != item["input_sha256"]:
                raise ValueError(f"chamber input integrity failure: {item['run_id']}")
            if item.get("raw_response") and stable_hash(item["raw_response"]) != item["raw_response_sha256"]:
                raise ValueError(f"chamber response integrity failure: {item['run_id']}")
            result.append(item)
        return result

    def runs(self, experiment_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM diagnostic_runs WHERE experiment_id=? ORDER BY phase,profile_id,case_id,replicate",
                (experiment_id,),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            for field in ("request_json", "parsed_json", "scores_json", "provider_json"):
                if item[field]:
                    item[field[:-5] if field.endswith("_json") else field] = json.loads(item[field])
            result.append(item)
        return result
