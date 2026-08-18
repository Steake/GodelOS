"""Protocol-level tests for the standalone recursive-feedback experiment."""

from __future__ import annotations

import unittest
from typing import Any, Dict, List, Mapping, Sequence

from recursive_feedback import (
    CONDITION_GODELOS_STATEFUL,
    CONDITION_INDEPENDENT,
    CONDITION_STATELESS,
    HISTORICAL_MODULATION_PROMPT,
    HISTORICAL_SYSTEM_PROMPT,
    ExperimentConfig,
    historical_metrics,
    run_condition,
)


class RecordingBackend:
    def __init__(self) -> None:
        self.requests: List[Dict[str, Any]] = []

    def generate(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
        parameters: Mapping[str, Any],
    ) -> str:
        self.requests.append(
            {
                "model": model,
                "messages": [dict(message) for message in messages],
                "parameters": dict(parameters),
            }
        )
        return f"output-{len(self.requests)}"


class RecursiveFeedbackProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ExperimentConfig(
            model="test-model",
            initial_seed="seed text",
            max_depth=3,
            rng_seed=41,
        )

    def test_independent_condition_resamples_original_seed(self) -> None:
        backend = RecordingBackend()
        records = run_condition(backend, self.config, CONDITION_INDEPENDENT)

        self.assertEqual([record["raw_input"] for record in records], ["seed text"] * 3)
        self.assertEqual(
            [request["messages"] for request in backend.requests],
            [[{"role": "user", "content": "seed text"}]] * 3,
        )

    def test_stateless_condition_uses_entire_previous_output(self) -> None:
        backend = RecordingBackend()
        records = run_condition(backend, self.config, CONDITION_STATELESS)

        self.assertEqual(
            [record["raw_input"] for record in records],
            ["seed text", "output-1", "output-2"],
        )
        self.assertEqual(
            backend.requests[2]["messages"],
            [{"role": "user", "content": "output-2"}],
        )
        self.assertTrue(
            all(len(request["messages"]) == 1 for request in backend.requests)
        )

    def test_stateful_condition_reconstructs_historical_wrapper(self) -> None:
        backend = RecordingBackend()
        records = run_condition(backend, self.config, CONDITION_GODELOS_STATEFUL)

        first_messages = backend.requests[0]["messages"]
        second_messages = backend.requests[1]["messages"]
        self.assertEqual(first_messages[0]["content"], HISTORICAL_SYSTEM_PROMPT)
        self.assertIn("[Recursive Reflection Layer: 1/3]", first_messages[1]["content"])
        self.assertEqual(len(first_messages), 2)
        self.assertEqual(len(second_messages), 3)
        self.assertIn(
            "Previous cognitive state:\noutput-1", second_messages[1]["content"]
        )
        self.assertIn(
            "[Recursive Reflection Layer: 2/3]", second_messages[1]["content"]
        )
        self.assertEqual(second_messages[2]["content"], HISTORICAL_MODULATION_PROMPT)
        self.assertNotIn("output-1", second_messages[0]["content"])
        self.assertEqual(records[1]["raw_output"], "output-2")

    def test_request_seeds_are_matched_by_depth(self) -> None:
        backend = RecordingBackend()
        records = run_condition(backend, self.config, CONDITION_STATELESS, repetition=2)
        self.assertEqual(
            [record["request_seed"] for record in records],
            [100041, 100042, 100043],
        )

    def test_lowercase_c_proxy_is_not_reported_as_formal_C_n(self) -> None:
        metrics = historical_metrics(
            '{"insights": ["a", "b", "c"], "depth_achieved": 2}'
        )
        self.assertIsNone(metrics["formal_C_n"])
        self.assertAlmostEqual(metrics["recovered_lowercase_c_proxy"], 0.51)
        self.assertIn("not formal C_n", metrics["recovered_lowercase_c_status"])


if __name__ == "__main__":
    unittest.main()
