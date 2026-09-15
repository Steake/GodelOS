"""SQLite snapshot and immutable hash-chained event storage."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Mapping

from .models import AgentState, stable_hash, utc_now


class SovereigntyStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    state_sha256 TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT,
                    event_hash TEXT UNIQUE NOT NULL,
                    FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
                );
                CREATE INDEX IF NOT EXISTS events_agent_sequence
                    ON events(agent_id, sequence);
                """
            )

    def create(self, state: AgentState) -> None:
        value = state.to_mapping()
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True)
        digest = stable_hash(value)
        with self._lock, self._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO agents VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (state.agent_id, state.name, payload, digest, 1, state.created_at, state.updated_at),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"agent already exists: {state.agent_id}") from exc
            self._append_event(connection, state.agent_id, "agent_created", {
                "state_sha256": digest, "name": state.name, "purpose": state.purpose,
            })

    def load(self, agent_id: str) -> AgentState:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT state_json, state_sha256 FROM agents WHERE agent_id = ?", (agent_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown agent {agent_id!r}")
        value = json.loads(row["state_json"])
        if stable_hash(value) != row["state_sha256"]:
            raise ValueError(f"state integrity failure for {agent_id}")
        return AgentState.from_mapping(value)

    def save_transition(
        self, state: AgentState, event_type: str, event_payload: Mapping[str, Any], expected_version: int
    ) -> int:
        state.updated_at = utc_now()
        value = state.to_mapping()
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True)
        digest = stable_hash(value)
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """UPDATE agents SET name=?, state_json=?, state_sha256=?,
                   version=version+1, updated_at=? WHERE agent_id=? AND version=?""",
                (state.name, payload, digest, state.updated_at, state.agent_id, expected_version),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("concurrent state update detected")
            self._append_event(connection, state.agent_id, event_type, {
                **dict(event_payload), "result_state_sha256": digest,
                "result_version": expected_version + 1,
            })
        return expected_version + 1

    def version(self, agent_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT version FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
        if row is None:
            raise KeyError(agent_id)
        return int(row["version"])

    def _append_event(
        self, connection: sqlite3.Connection, agent_id: str,
        event_type: str, payload: Mapping[str, Any],
    ) -> str:
        previous = connection.execute(
            "SELECT event_hash FROM events WHERE agent_id=? ORDER BY sequence DESC LIMIT 1",
            (agent_id,),
        ).fetchone()
        previous_hash = previous["event_hash"] if previous else None
        created_at = utc_now()
        event_id = f"evt-{stable_hash([agent_id, event_type, created_at, payload])[:20]}"
        content = {
            "event_id": event_id, "agent_id": agent_id, "event_type": event_type,
            "created_at": created_at, "payload": dict(payload), "previous_hash": previous_hash,
        }
        event_hash = stable_hash(content)
        connection.execute(
            "INSERT INTO events(event_id,agent_id,event_type,created_at,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?)",
            (event_id, agent_id, event_type, created_at,
             json.dumps(dict(payload), ensure_ascii=False, sort_keys=True), previous_hash, event_hash),
        )
        return event_hash

    def events(self, agent_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM events WHERE agent_id=? ORDER BY sequence", (agent_id,)
            ).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload_json"])} for row in rows]

    def verify_event_chain(self, agent_id: str) -> bool:
        previous: str | None = None
        for row in self.events(agent_id):
            content = {
                "event_id": row["event_id"], "agent_id": row["agent_id"],
                "event_type": row["event_type"], "created_at": row["created_at"],
                "payload": row["payload"], "previous_hash": row["previous_hash"],
            }
            if row["previous_hash"] != previous or stable_hash(content) != row["event_hash"]:
                return False
            previous = row["event_hash"]
        return True

    def list_agents(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT agent_id,name,version,created_at,updated_at FROM agents ORDER BY created_at"
            ).fetchall()
        return [dict(row) for row in rows]
