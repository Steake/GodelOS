"""Contract tests for the recursive-feedback research harness."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.recursive_feedback.analyse import (
    analyse_records,
    read_trace,
    write_analysis,
)
from experiments.recursive_feedback.runner import (
    Condition,
    ExperimentConfig,
    ReplayAdapter,
    build_observation,
    load_config,
    run_experiment,
    verify_record_hash,
)


class RecursiveFeedbackTests(unittest.TestCase):
    def make_config(
        self,
        output_dir: str,
        condition: Condition,
        *,
        depth: int = 3,
    ) -> ExperimentConfig:
        return ExperimentConfig(
            endpoint="https://example.invalid/v1/chat/completions",
            api_key_env="TEST_API_KEY",
            model="replay-model-v1",
            prompts=("seed prompt",),
            conditions=(condition,),
            output_dir=output_dir,
            depth=depth,
            replicates=1,
            temperature=0.0,
            max_tokens=64,
            seed=101,
            timeout_seconds=5,
        )

    def test_exact_self_feed_uses_previous_output_as_next_input(self) -> None:
        condition = Condition("exact", "previous_output")
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha", "beta", "gamma"])
            trace_path, _ = run_experiment(
                self.make_config(directory, condition), adapter
            )
            records = read_trace(trace_path)

        self.assertEqual(
            [call[-1]["content"] for call in adapter.calls],
            ["seed prompt", "alpha", "beta"],
        )
        self.assertEqual(
            [record["input_text"] for record in records],
            ["seed prompt", "alpha", "beta"],
        )
        self.assertEqual(
            records[1]["parent_output_sha256"], records[0]["output_sha256"]
        )

    def test_repeated_seed_control_is_independent(self) -> None:
        condition = Condition("control", "seed")
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha", "beta", "gamma"])
            run_experiment(self.make_config(directory, condition), adapter)

        self.assertEqual(
            [call[-1]["content"] for call in adapter.calls],
            ["seed prompt", "seed prompt", "seed prompt"],
        )
        self.assertTrue(all(len(call) == 1 for call in adapter.calls))

    def test_persistent_history_is_explicit_and_accumulates(self) -> None:
        condition = Condition(
            "persistent",
            "previous_output",
            history_policy="persistent",
        )
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha", "beta", "gamma"])
            trace_path, _ = run_experiment(
                self.make_config(directory, condition), adapter
            )
            records = read_trace(trace_path)

        self.assertEqual([len(call) for call in adapter.calls], [1, 3, 5])
        self.assertEqual(
            [record["request"]["history_message_count"] for record in records],
            [1, 3, 5],
        )
        self.assertEqual(
            [message["role"] for message in adapter.calls[-1]],
            ["user", "assistant", "user", "assistant", "user"],
        )

    def test_observer_and_sham_have_same_shape_but_different_values(self) -> None:
        accurate = build_observation(
            policy="accurate",
            run_id="a" * 20,
            depth=2,
            previous_output="alpha beta",
        )
        sham = build_observation(
            policy="sham",
            run_id="a" * 20,
            depth=2,
            previous_output="alpha beta",
        )

        self.assertIsNotNone(accurate)
        self.assertIsNotNone(sham)
        self.assertEqual(set(accurate or {}), set(sham or {}))
        self.assertNotEqual(accurate, sham)
        self.assertEqual(
            build_observation(
                policy="sham",
                run_id="a" * 20,
                depth=2,
                previous_output="alpha beta",
            ),
            sham,
        )

    def test_observer_assignment_is_visible_in_trace(self) -> None:
        condition = Condition(
            "observed",
            "previous_output",
            observer_policy="accurate",
        )
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha"])
            trace_path, _ = run_experiment(
                self.make_config(directory, condition, depth=1), adapter
            )
            records = read_trace(trace_path)

        self.assertIn("[OBSERVER_STATE]", adapter.calls[0][-1]["content"])
        self.assertEqual(records[0]["observer"]["assignment"], "accurate")
        self.assertEqual(records[0]["input_text"], "seed prompt")
        self.assertNotEqual(records[0]["model_input"], records[0]["input_text"])

    def test_trace_hashes_and_parent_chain_validate(self) -> None:
        condition = Condition("exact", "previous_output")
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha", "beta", "gamma"])
            trace_path, manifest_path = run_experiment(
                self.make_config(directory, condition), adapter
            )
            records = read_trace(trace_path)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertTrue(all(verify_record_hash(record) for record in records))
        self.assertEqual(
            records[1]["parent_record_sha256"], records[0]["record_sha256"]
        )
        self.assertEqual(
            records[2]["parent_record_sha256"], records[1]["record_sha256"]
        )
        self.assertEqual(manifest["record_count"], 3)
        self.assertEqual(manifest["run_count"], 1)

    def test_analysis_detects_an_exact_two_step_cycle(self) -> None:
        condition = Condition("exact", "previous_output")
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha", "beta", "alpha"])
            trace_path, _ = run_experiment(
                self.make_config(directory, condition), adapter
            )
            records = read_trace(trace_path)
            step_rows, run_rows = analyse_records(records)

        self.assertEqual(step_rows[-1]["exact_cycle_length"], 2)
        self.assertEqual(run_rows[0]["first_exact_cycle_depth"], 2)
        self.assertEqual(run_rows[0]["first_exact_cycle_length"], 2)

    def test_analysis_writes_csv_and_json_outputs(self) -> None:
        condition = Condition("exact", "previous_output")
        with tempfile.TemporaryDirectory() as directory:
            adapter = ReplayAdapter(["alpha", "beta", "alpha"])
            trace_path, _ = run_experiment(
                self.make_config(directory, condition), adapter
            )
            analysis_dir = Path(directory) / "analysis"
            step_path, run_path, analysis_path = write_analysis(
                trace_path, analysis_dir
            )
            analysis = json.loads(analysis_path.read_text(encoding="utf-8"))

            self.assertTrue(step_path.is_file())
            self.assertTrue(run_path.is_file())
            self.assertEqual(analysis["record_count"], 3)
            self.assertEqual(analysis["run_count"], 1)

    def test_repeated_seed_with_persistent_history_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be stateless"):
            Condition(
                "invalid",
                "seed",
                history_policy="persistent",
            ).validate()

    def test_example_config_resolves_versioned_prompt_bank(self) -> None:
        config = load_config(
            Path("experiments/recursive_feedback/config.example.json")
        )

        self.assertEqual(len(config.prompts), 24)
        self.assertEqual(len(config.conditions), 5)
        self.assertEqual(
            config.prompts[0],
            "Explain why the sky can appear red near sunset to a reader who "
            "knows no atmospheric physics.",
        )


if __name__ == "__main__":
    unittest.main()
