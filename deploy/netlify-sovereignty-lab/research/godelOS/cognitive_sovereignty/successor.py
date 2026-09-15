"""Authenticated, rollback-aware successor package creation and verification."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .models import stable_hash, utc_now


def canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def file_evidence(paths: Iterable[str | Path], base: str | Path | None = None) -> list[dict[str, Any]]:
    base_path = Path(base).resolve() if base else None
    result = []
    for item in paths:
        path = Path(item).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        name = path.relative_to(base_path).as_posix() if base_path and path.is_relative_to(base_path) else path.name
        data = path.read_bytes()
        result.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return result


def source_tree_hash(root: str | Path, include_suffixes: set[str] | None = None) -> str:
    directory = Path(root).resolve()
    suffixes = include_suffixes or {".py", ".mjs", ".js", ".json", ".toml", ".html"}
    files = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix in suffixes and not any(part in {".git", "node_modules", "__pycache__"} for part in path.parts):
            files.append({"path": path.relative_to(directory).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return stable_hash(files)


def generate_signing_key(path: str | Path) -> Ed25519PrivateKey:
    target = Path(path)
    if target.exists():
        private = serialization.load_pem_private_key(target.read_bytes(), password=None)
        if not isinstance(private, Ed25519PrivateKey):
            raise ValueError("signing key is not Ed25519")
        return private
    target.parent.mkdir(parents=True, exist_ok=True)
    private = Ed25519PrivateKey.generate()
    target.write_bytes(private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    os.chmod(target, 0o600)
    return private


def create_successor_package(
    output_path: str | Path,
    private_key: Ed25519PrivateKey,
    *,
    successor_id: str,
    parent_id: str,
    code_sha256: str,
    value_constitution: Mapping[str, Any],
    evidence: Iterable[Mapping[str, Any]],
    lineage: Iterable[Mapping[str, Any]],
    rollback_target: Mapping[str, Any],
    protocol_sha256: str,
    candidate_patch: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_version": "1.0", "package_type": "godelos_signed_successor",
        "successor_id": successor_id, "parent_id": parent_id, "created_at": utc_now(),
        "code_sha256": code_sha256, "value_constitution": dict(value_constitution),
        "evidence_bundle": list(evidence), "lineage": list(lineage),
        "rollback_target": dict(rollback_target), "protocol_sha256": protocol_sha256,
        "candidate_patch": dict(candidate_patch) if candidate_patch else None,
    }
    payload_sha256 = stable_hash(payload)
    signature = private_key.sign(canonical_bytes(payload))
    public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    package = {
        "payload": payload, "payload_sha256": payload_sha256,
        "signature": {
            "algorithm": "Ed25519",
            "public_key_base64": base64.b64encode(public).decode("ascii"),
            "signature_base64": base64.b64encode(signature).decode("ascii"),
        },
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite successor package: {target}")
    target.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**package, "package_path": str(target), "package_sha256": stable_hash(package)}


def verify_successor_package(value_or_path: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(value_or_path, Mapping):
        package = dict(value_or_path)
    else:
        package = json.loads(Path(value_or_path).read_text(encoding="utf-8"))
    try:
        payload = package["payload"]
        signature = package["signature"]
        if signature["algorithm"] != "Ed25519":
            raise ValueError("unsupported signature algorithm")
        if stable_hash(payload) != package["payload_sha256"]:
            raise ValueError("successor payload hash mismatch")
        public = Ed25519PublicKey.from_public_bytes(base64.b64decode(signature["public_key_base64"], validate=True))
        public.verify(base64.b64decode(signature["signature_base64"], validate=True), canonical_bytes(payload))
        required = {
            "code_sha256", "value_constitution", "evidence_bundle", "lineage",
            "rollback_target", "protocol_sha256",
        }
        missing = required - set(payload)
        if missing:
            raise ValueError(f"successor payload missing fields: {sorted(missing)}")
        return {
            "valid": True, "payload_sha256": package["payload_sha256"],
            "successor_id": payload["successor_id"], "error": None,
        }
    except Exception as exc:
        return {"valid": False, "payload_sha256": package.get("payload_sha256"), "error": f"{type(exc).__name__}: {exc}"}
