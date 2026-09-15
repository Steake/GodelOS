#!/usr/bin/env python3
"""Freeze the v3 evidence set, sign the final candidate and build its archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from godelOS.cognitive_sovereignty.models import stable_hash, utc_now
from godelOS.cognitive_sovereignty.successor import (
    create_successor_package,
    file_evidence,
    generate_signing_key,
    source_tree_hash,
    verify_successor_package,
)


DEFAULT_ARTIFACT = ROOT / "research_artifacts" / "cognitive_sovereignty" / "deepseek-evolution-chamber-v3"
DEFAULT_REPORT = ROOT / "output" / "pdf" / "godelos-evolution-chamber-v3-report.pdf"
DEFAULT_KEY = ROOT.parent / "private" / "godelos-evolution-chamber-ed25519.pem"
DEFAULT_ZIP = ROOT / "output" / "research" / "godelos-evolution-chamber-v3-evidence.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite final artefact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalise(
    artifact: Path, report: Path, key_path: Path, output_zip: Path, revision: int = 1,
) -> dict[str, object]:
    artifact = artifact.resolve()
    suffix = "" if revision == 1 else f"-v{revision}"
    report_copy = artifact / "report" / f"godelos-evolution-chamber-v3-report-final{suffix}.pdf"
    if report_copy.exists():
        raise FileExistsError(f"refusing to overwrite report copy: {report_copy}")
    shutil.copyfile(report, report_copy)

    evidence_paths = [
        artifact / "compiled-protocol.json",
        artifact / "raw-run-index.json",
        artifact / "analysis.json",
        artifact / "analysis-extended.json",
        artifact / "reviews" / "pre-run-review.json",
        artifact / "reviews" / "post-run-review.json",
        artifact / "review-adjudication.json",
        artifact / "patch_demo" / "patch-proposal.json",
        artifact / "patch_demo" / "patch-evaluation.json",
        artifact / "promotion-decision.json",
        report_copy,
    ]
    evidence = file_evidence(evidence_paths, base=artifact)
    index = {
        "schema_version": "1.0",
        "experiment_id": "deepseek-evolution-chamber-v3",
        "created_at": utc_now(),
        "immutability_boundary": "Raw runs are append-only. This index covers the derived decision artefacts used for final signing.",
        "evidence": evidence,
    }
    index["index_sha256"] = stable_hash(index)
    evidence_index_path = artifact / f"final-evidence-index{suffix}.json"
    write_json(evidence_index_path, index)
    evidence.append(file_evidence([evidence_index_path], base=artifact)[0])

    original = json.loads((artifact / "successor" / "deepseek-evolution-chamber-v3-successor-package.json").read_text())
    payload = original["payload"]
    protocol = json.loads((artifact / "compiled-protocol.json").read_text())
    final_package_path = artifact / "successor" / f"deepseek-evolution-chamber-v3-successor-package-final{suffix}.json"
    package = create_successor_package(
        final_package_path,
        generate_signing_key(key_path),
        successor_id="godelos-sovereign-01:deepseek-evolution-chamber-v3:final-candidate",
        parent_id="godelos-sovereign-01",
        code_sha256=source_tree_hash(ROOT / "godelOS" / "cognitive_sovereignty"),
        value_constitution=payload["value_constitution"],
        evidence=evidence,
        lineage=[
            *payload["lineage"],
            {"kind": "code_scope", "identifier": "godelOS/cognitive_sovereignty"},
            {"kind": "final_evidence_index", "identifier": index["index_sha256"]},
        ],
        rollback_target=payload["rollback_target"],
        protocol_sha256=protocol["protocol_sha256"],
        candidate_patch=payload.get("candidate_patch"),
    )
    verification = verify_successor_package(final_package_path)
    verification["package_file_sha256"] = sha256(final_package_path)
    verification_path = artifact / "successor" / f"verification-final{suffix}.json"
    write_json(verification_path, verification)
    if not verification["valid"]:
        raise RuntimeError(f"final signature failed verification: {verification['error']}")

    files = []
    for path in sorted(artifact.rglob("*")):
        if path.is_file() and path.name != f"manifest-final{suffix}.json":
            files.append({
                "path": path.relative_to(artifact).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            })
    manifest = {
        "schema_version": "1.0",
        "experiment_id": "deepseek-evolution-chamber-v3",
        "created_at": utc_now(),
        "provider": "DeepSeek",
        "model": "deepseek-v4-flash",
        "model_calls": 99,
        "branch_phases": {"completed": 96, "failed": 0},
        "promotion_decision": "hold",
        "successor_signature_valid": True,
        "source_scope": "godelOS/cognitive_sovereignty",
        "source_sha256": package["payload"]["code_sha256"],
        "files": files,
    }
    manifest["manifest_sha256"] = stable_hash(manifest)
    manifest_path = artifact / f"manifest-final{suffix}.json"
    write_json(manifest_path, manifest)

    if output_zip.exists():
        raise FileExistsError(f"refusing to overwrite evidence archive: {output_zip}")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(artifact.rglob("*")):
            if path.is_file():
                archive.write(path, Path(artifact.name) / path.relative_to(artifact))
        for path in (
            ROOT / "docs" / "EVOLUTION_CHAMBER_V3.md",
            ROOT / "experiments" / "evolution_chamber" / "README.md",
            ROOT / "experiments" / "evolution_chamber" / "registry.json",
            ROOT / "experiments" / "evolution_chamber" / "theses" / "autobiographical-lockin.agent-v1.json",
        ):
            archive.write(path, Path("repository_docs") / path.relative_to(ROOT))

    return {
        "manifest": str(manifest_path),
        "successor_package": str(final_package_path),
        "signature_valid": verification["valid"],
        "evidence_zip": str(output_zip),
        "evidence_zip_sha256": sha256(output_zip),
        "files_frozen": len(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--signing-key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--evidence-zip", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--revision", type=int, default=1)
    args = parser.parse_args()
    if args.revision < 1:
        parser.error("--revision must be at least 1")
    print(json.dumps(finalise(args.artifact, args.report, args.signing_key, args.evidence_zip, args.revision), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
