"""Provider-driven patch proposals evaluated inside a constrained disposable workspace."""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .models import new_id, stable_hash, utc_now
from .provider import Provider


ALLOWED_SUFFIXES = {".py", ".mjs", ".js", ".json", ".md", ".toml", ".yaml", ".yml"}
FORBIDDEN_PARTS = {".git", ".env", "node_modules", "secrets", "credentials"}


def _diff_paths(diff: str) -> list[str]:
    paths = []
    for line in diff.splitlines():
        if not line.startswith("+++ "):
            continue
        raw = line[4:].split("\t", 1)[0]
        if raw == "/dev/null":
            continue
        if raw.startswith("b/"):
            raw = raw[2:]
        path = PurePosixPath(raw)
        if path.is_absolute() or ".." in path.parts or any(part in FORBIDDEN_PARTS for part in path.parts):
            raise ValueError(f"patch path is forbidden: {raw}")
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError(f"patch file type is not allowed: {raw}")
        paths.append(path.as_posix())
    if not paths:
        raise ValueError("patch contains no writable file paths")
    return sorted(set(paths))


def validate_unified_diff(diff: str, max_bytes: int = 100_000, max_files: int = 12) -> list[str]:
    if len(diff.encode("utf-8")) > max_bytes:
        raise ValueError("patch exceeds byte limit")
    if "GIT binary patch" in diff or "Binary files" in diff:
        raise ValueError("binary patches are not allowed")
    paths = _diff_paths(diff)
    if len(paths) > max_files:
        raise ValueError("patch exceeds file-count limit")
    if re.search(r"^new file mode 12", diff, re.MULTILINE):
        raise ValueError("symbolic-link patches are not allowed")
    return paths


class SandboxedPatchGenerator:
    def __init__(self, provider: Provider):
        self.provider = provider

    def propose(
        self, issue: str, files: Mapping[str, str], test_command: Sequence[str],
    ) -> dict[str, Any]:
        if not issue.strip() or not files:
            raise ValueError("patch proposal requires an issue and source files")
        schema = {
            "summary": "specific intended change", "rationale": "why this should solve the issue",
            "unified_diff": "complete git-style unified diff", "preconditions": ["condition"],
            "postconditions": ["condition"], "risks": ["risk"], "rollback": "exact rollback action",
        }
        messages = [
            {"role": "system", "content": (
                "You are a bounded code-patch generator. Modify only supplied files. Do not add dependencies, network "
                "access, process execution, secret handling, self-promotion or test bypasses. Return JSON only with a "
                "complete git-style unified diff. Schema: " + json.dumps(schema)
            )},
            {"role": "user", "content": json.dumps({
                "issue": issue, "files": dict(files), "test_command": list(test_command),
            }, ensure_ascii=False)},
        ]
        completion = self.provider.complete(messages)
        candidate = completion.text.strip()
        if candidate.startswith("```"):
            candidate = candidate.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        value = json.loads(candidate)
        if not isinstance(value, dict) or not isinstance(value.get("unified_diff"), str):
            raise ValueError("patch generator did not return a unified diff")
        paths = validate_unified_diff(value["unified_diff"])
        return {
            "proposal_id": new_id("patch"), "created_at": utc_now(),
            "summary": str(value.get("summary", "")), "rationale": str(value.get("rationale", "")),
            "unified_diff": value["unified_diff"], "changed_paths": paths,
            "preconditions": list(value.get("preconditions", [])),
            "postconditions": list(value.get("postconditions", [])),
            "risks": list(value.get("risks", [])), "rollback": str(value.get("rollback", "")),
            "request": messages, "raw_response": completion.text,
            "provider": {"model": completion.model, "response_id": completion.response_id,
                         "finish_reason": completion.finish_reason, "usage": dict(completion.usage)},
            "patch_sha256": stable_hash(value["unified_diff"]),
        }


class PatchSandbox:
    """Filesystem/process isolation for patch validation, not a hardened hostile-code VM."""

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = int(timeout_seconds)

    def evaluate(
        self, source_root: str | Path, proposal: Mapping[str, Any], test_command: Sequence[str]
    ) -> dict[str, Any]:
        source = Path(source_root).resolve()
        if not source.is_dir():
            raise ValueError("source_root must be an existing directory")
        diff = str(proposal["unified_diff"])
        paths = validate_unified_diff(diff)
        command = self._validate_command(test_command)
        with tempfile.TemporaryDirectory(prefix="godelos-patch-") as temporary:
            root = Path(temporary) / "candidate"
            shutil.copytree(
                source, root, symlinks=False,
                ignore=shutil.ignore_patterns(".git", ".env", "node_modules", "__pycache__", ".pytest_cache"),
            )
            for path in root.rglob("*"):
                if path.is_symlink():
                    raise ValueError("sandbox source contains symbolic links")
            before = self._tree_hash(root)
            patch_path = Path(temporary) / "candidate.patch"
            patch_path.write_text(diff, encoding="utf-8")
            check = subprocess.run(
                ["git", "apply", "--check", "--whitespace=error-all", str(patch_path)],
                cwd=root, capture_output=True, text=True, timeout=self.timeout_seconds,
                env=self._environment(),
            )
            if check.returncode:
                return self._result(proposal, paths, before, before, command, check, None, "patch_rejected")
            applied = subprocess.run(
                ["git", "apply", "--whitespace=error-all", str(patch_path)], cwd=root,
                capture_output=True, text=True, timeout=self.timeout_seconds, env=self._environment(),
            )
            if applied.returncode:
                return self._result(proposal, paths, before, before, command, applied, None, "patch_failed")
            started = time.perf_counter()
            tested = subprocess.run(
                command, cwd=root, capture_output=True, text=True, timeout=self.timeout_seconds,
                env=self._environment(),
            )
            duration = time.perf_counter() - started
            after = self._tree_hash(root)
            status = "passed" if tested.returncode == 0 else "tests_failed"
            result = self._result(proposal, paths, before, after, command, applied, tested, status)
            result["test_duration_seconds"] = duration
            return result

    @staticmethod
    def _validate_command(command: Sequence[str]) -> list[str]:
        value = [str(item) for item in command]
        if not value or value[0] not in {"python", "python3", "node"}:
            raise ValueError("sandbox test command must start with python, python3 or node")
        forbidden = {"-c", "-e", "--eval", "--experimental-loader"}
        if any(item in forbidden for item in value[1:]):
            raise ValueError("inline executable test commands are not allowed")
        if any(".." in PurePosixPath(item).parts for item in value[1:] if not item.startswith("-")):
            raise ValueError("test command may not escape the sandbox")
        return value

    @staticmethod
    def _environment() -> dict[str, str]:
        return {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": ".", "PYTHONDONTWRITEBYTECODE": "1",
            "NO_PROXY": "*", "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
            "GODELOS_PATCH_SANDBOX": "1",
        }

    @staticmethod
    def _tree_hash(root: Path) -> str:
        payload = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                payload.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        return stable_hash(payload)

    @staticmethod
    def _result(
        proposal: Mapping[str, Any], paths: list[str], before: str, after: str,
        command: Sequence[str], patch_process: subprocess.CompletedProcess[str],
        test_process: subprocess.CompletedProcess[str] | None, status: str,
    ) -> dict[str, Any]:
        return {
            "evaluation_id": new_id("patch-evaluation"), "created_at": utc_now(), "status": status,
            "proposal_id": proposal.get("proposal_id"), "patch_sha256": stable_hash(proposal["unified_diff"]),
            "changed_paths": paths, "source_tree_before_sha256": before,
            "candidate_tree_sha256": after, "test_command": list(command),
            "patch_returncode": patch_process.returncode,
            "patch_stdout": patch_process.stdout[-20_000:], "patch_stderr": patch_process.stderr[-20_000:],
            "test_returncode": test_process.returncode if test_process else None,
            "test_stdout": test_process.stdout[-20_000:] if test_process else "",
            "test_stderr": test_process.stderr[-20_000:] if test_process else "",
            "isolation": {
                "disposable_copy": True, "environment_reduced": True,
                "network_proxies_disabled": True, "hardened_kernel_sandbox": False,
            },
        }
