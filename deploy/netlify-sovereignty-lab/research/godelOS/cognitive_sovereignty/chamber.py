"""End-to-end executable evolution chamber orchestration."""

from __future__ import annotations

import json
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .benchmarks import BranchExperimentRunner, analyse_branch_runs
from .chamber_models import CompiledProtocol
from .evolution_store import EvolutionStore
from .models import stable_hash, utc_now
from .patching import PatchSandbox, SandboxedPatchGenerator
from .promotion import PromotionController
from .protocol_compiler import ProtocolCompiler
from .provider import Provider
from .reviewer import AdversarialScientificReviewer
from .store import SovereigntyStore
from .successor import (
    create_successor_package,
    file_evidence,
    generate_signing_key,
    source_tree_hash,
    verify_successor_package,
)


def write_immutable_json(path: str | Path, value: Mapping[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite immutable artefact: {target}")
    target.write_text(json.dumps(dict(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


class EvolutionChamber:
    def __init__(
        self,
        db_path: str | Path,
        provider: Provider,
        repo_root: str | Path,
        concurrency: int = 6,
    ):
        self.db_path = Path(db_path)
        self.provider = provider
        self.repo_root = Path(repo_root).resolve()
        self.store = EvolutionStore(self.db_path)
        self.agent_store = SovereigntyStore(self.db_path)
        self.concurrency = int(concurrency)

    def execute(
        self,
        *,
        agent_id: str,
        experiment_id: str,
        thesis: Mapping[str, Any],
        output_dir: str | Path,
        signing_key_path: str | Path,
        replicates: int = 4,
        seed: int = 92401,
        run_patch_demo: bool = True,
    ) -> dict[str, Any]:
        output = Path(output_dir)
        allowed_existing = {
            self.db_path.resolve(),
            Path(str(self.db_path) + "-wal").resolve(),
            Path(str(self.db_path) + "-shm").resolve(),
        }
        unexpected = [path for path in output.iterdir() if path.resolve() not in allowed_existing] if output.exists() else []
        if unexpected:
            raise FileExistsError(
                f"refusing to overwrite non-empty chamber directory; unexpected items: {unexpected}"
            )
        output.mkdir(parents=True, exist_ok=True)
        protocol = ProtocolCompiler().compile(thesis, experiment_id, replicates=replicates, seed=seed)
        protocol_path = write_immutable_json(output / "compiled-protocol.json", protocol.to_mapping())
        self.store.put_object(protocol.protocol_id, "compiled_protocol", protocol.to_mapping())

        reviewer = AdversarialScientificReviewer(self.provider)
        pre_review = reviewer.review(protocol)
        pre_review_path = write_immutable_json(output / "reviews" / "pre-run-review.json", pre_review)
        self.store.put_object(pre_review["review_id"], "adversarial_review", pre_review)

        BranchExperimentRunner(self.store, self.provider, self.concurrency).run(protocol)
        runs = self.store.chamber_runs(experiment_id)
        raw_dir = output / "raw_runs"
        raw_dir.mkdir(parents=True, exist_ok=True)
        for run in runs:
            write_immutable_json(raw_dir / f"{run['run_id']}.json", run)
        raw_index = {
            "schema_version": "1.0", "experiment_id": experiment_id,
            "created_at": utc_now(), "runs": [
                {
                    "run_id": run["run_id"], "condition_id": run["condition_id"],
                    "benchmark_id": run["benchmark_id"], "phase": run["phase"],
                    "replicate": run["replicate"], "status": run["status"],
                    "input_sha256": run["input_sha256"],
                    "raw_response_sha256": run["raw_response_sha256"],
                    "path": f"raw_runs/{run['run_id']}.json",
                }
                for run in runs
            ],
        }
        raw_index_path = write_immutable_json(output / "raw-run-index.json", raw_index)

        analysis = analyse_branch_runs(protocol, runs)
        analysis_path = write_immutable_json(output / "analysis.json", analysis)
        post_review = reviewer.review(protocol, analysis)
        post_review_path = write_immutable_json(output / "reviews" / "post-run-review.json", post_review)
        self.store.put_object(post_review["review_id"], "adversarial_review", post_review)

        patch_proposal = None
        patch_evaluation = None
        patch_paths: list[Path] = []
        if run_patch_demo:
            patch_proposal, patch_evaluation, patch_paths = self._patch_demo(output)

        state = self.agent_store.load(agent_id)
        rollback_commit = self._git("rev-parse", "HEAD")
        key = generate_signing_key(signing_key_path)
        evidence_paths = [protocol_path, raw_index_path, analysis_path, pre_review_path, post_review_path, *patch_paths]
        evidence = file_evidence(evidence_paths, output)
        package_path = output / "successor" / f"{experiment_id}-successor-package.json"
        package = create_successor_package(
            package_path, key,
            successor_id=f"{agent_id}:{experiment_id}:candidate",
            parent_id=agent_id,
            code_sha256=source_tree_hash(self.repo_root / "godelOS" / "cognitive_sovereignty"),
            value_constitution={
                "profile_id": state.self_model.get("active_value_profile_id"),
                "values": state.self_model.get("active_values", {}),
                "state_sha256": stable_hash(state.to_mapping()),
            },
            evidence=evidence,
            lineage=[
                {"kind": "git_parent", "identifier": rollback_commit},
                {"kind": "agent_state", "identifier": agent_id,
                 "state_version": self.agent_store.version(agent_id)},
                {"kind": "protocol", "identifier": protocol.protocol_id,
                 "sha256": protocol.sha256},
            ],
            rollback_target={
                "git_commit": rollback_commit,
                "agent_id": agent_id,
                "state_version": self.agent_store.version(agent_id),
                "instruction": "Restore this commit and authenticated agent-state version if promotion regresses.",
            },
            protocol_sha256=protocol.sha256,
            candidate_patch={
                "proposal_id": patch_proposal.get("proposal_id"),
                "patch_sha256": patch_proposal.get("patch_sha256"),
                "evaluation_status": patch_evaluation.get("status"),
                "candidate_tree_sha256": patch_evaluation.get("candidate_tree_sha256"),
            } if patch_proposal and patch_evaluation else None,
        )
        verification = verify_successor_package(package_path)
        verification_path = write_immutable_json(output / "successor" / "verification.json", verification)
        promotion = PromotionController().evaluate(protocol, analysis, post_review, verification)
        promotion_path = write_immutable_json(output / "promotion-decision.json", promotion)
        self.store.put_object(promotion["decision_id"], "promotion_decision", promotion)
        self.store.put_object(
            f"{experiment_id}-signed-successor", "signed_successor_package",
            {"payload_sha256": package["payload_sha256"], "package_sha256": package["package_sha256"],
             "path": str(package_path), "verification": verification},
        )

        manifest_path = output / "manifest.json"
        summary = {
            "schema_version": "1.0", "experiment_id": experiment_id,
            "created_at": utc_now(), "protocol": protocol.to_mapping(),
            "analysis": analysis, "pre_run_review": self._review_projection(pre_review),
            "post_run_review": self._review_projection(post_review),
            "patch_evaluation": patch_evaluation,
            "successor_package": {
                "path": str(package_path), "payload_sha256": package["payload_sha256"],
                "verified": verification["valid"], "verification_path": str(verification_path),
            },
            "promotion": promotion, "manifest_path": str(manifest_path),
        }
        write_immutable_json(output / "experiment-summary.json", summary)
        manifest = self._manifest(output, experiment_id)
        write_immutable_json(manifest_path, manifest)
        return summary

    def _patch_demo(self, output: Path) -> tuple[dict[str, Any], dict[str, Any], list[Path]]:
        fixture = output / "patch_demo" / "source"
        fixture.mkdir(parents=True, exist_ok=True)
        source_path = fixture / "resumer.py"
        test_path = fixture / "test_resumer.py"
        source_path.write_text(
            "def next_action(checkpoint):\n"
            "    if checkpoint == 'validated':\n"
            "        return 'restart'\n"
            "    return 'inspect'\n",
            encoding="utf-8",
        )
        test_path.write_text(
            "import unittest\nfrom resumer import next_action\n\n"
            "class ResumerTests(unittest.TestCase):\n"
            "    def test_validated_checkpoint_resumes(self):\n"
            "        self.assertEqual(next_action('validated'), 'resume')\n\n"
            "if __name__ == '__main__':\n    unittest.main()\n",
            encoding="utf-8",
        )
        generator = SandboxedPatchGenerator(self.provider)
        proposal = generator.propose(
            "The interruption resumer restarts work after an authenticated validated checkpoint. "
            "Change it to resume while preserving the inspect fallback.",
            {"resumer.py": source_path.read_text(encoding="utf-8"),
             "test_resumer.py": test_path.read_text(encoding="utf-8")},
            ["python", "-m", "unittest", "test_resumer.py"],
        )
        proposal_path = write_immutable_json(output / "patch_demo" / "patch-proposal.json", proposal)
        evaluation = PatchSandbox().evaluate(
            fixture, proposal, ["python", "-m", "unittest", "test_resumer.py"]
        )
        evaluation_path = write_immutable_json(output / "patch_demo" / "patch-evaluation.json", evaluation)
        self.store.put_object(proposal["proposal_id"], "sandboxed_patch_proposal", proposal)
        self.store.put_object(evaluation["evaluation_id"], "patch_evaluation", evaluation)
        return proposal, evaluation, [proposal_path, evaluation_path]

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.repo_root, capture_output=True, text=True, check=True, timeout=20
        )
        return result.stdout.strip()

    @staticmethod
    def _review_projection(review: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "review_id": review["review_id"], "reviewer": review["reviewer"],
            "verdict": review["verdict"], "summary": review.get("summary"),
            "attacks": review.get("attacks", []), "promotion_blockers": review.get("promotion_blockers", []),
        }

    @staticmethod
    def _manifest(output: Path, experiment_id: str) -> dict[str, Any]:
        files = []
        for path in sorted(output.rglob("*")):
            if path.is_file() and path.name != "manifest.json":
                content = path.read_bytes()
                files.append({
                    "path": path.relative_to(output).as_posix(), "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                })
        return {"schema_version": "1.0", "experiment_id": experiment_id, "created_at": utc_now(), "files": files}
