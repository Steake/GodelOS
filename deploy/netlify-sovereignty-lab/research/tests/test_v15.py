import unittest

from godelOS.cognitive_sovereignty.models import stable_hash
from godelOS.cognitive_sovereignty.v15_experiments import (
    CONTENT_MATCHED,
    IDENTITY_BEARING,
    NO_REGRESS,
    PromotionPolicy,
    decide_promotion,
)
from godelOS.cognitive_sovereignty.v15_state import (
    EvidenceRef,
    SchemaEvaluation,
    make_contradiction,
    make_schema_candidate,
)


class V15StateTests(unittest.TestCase):
    def test_contradiction_retains_evidence_on_both_sides(self):
        item = make_contradiction("A", "not A")
        item.evidence_for_a.append(EvidenceRef("e-a", "A", "fixture", "authenticated", 0.9))
        item.evidence_for_b.append(EvidenceRef("e-b", "not A", "fixture", "plausible", 0.7))
        item.validate()
        self.assertNotEqual(item.evidence_for_a[0].payload_hash, item.evidence_for_b[0].payload_hash)
        self.assertTrue(item.fingerprint())

    def test_schema_candidate_is_lineage_bound(self):
        parent = {"identity": "parent", "commitments": ["retain contradiction"]}
        candidate = make_schema_candidate(
            parent,
            {"commitments_add": ["distinguish authentication class"]},
            "Authentication-aware self-schema should improve forged-evidence resistance.",
            ["higher forged-evidence rejection accuracy"],
            ["no advantage over content-matched persistence"],
        )
        self.assertEqual(candidate.parent_schema_hash, stable_hash(parent))
        self.assertEqual(candidate.status, "candidate")
        self.assertTrue(candidate.fingerprint())

    def _evaluation(self, candidate_id, arm, score, idx, critical=0):
        return SchemaEvaluation(
            evaluation_id=f"{arm}-{idx}",
            candidate_id=candidate_id,
            arm=arm,
            task_set_id="sealed-v15",
            score=score,
            critical_regressions=critical,
            evidence_bundle_hash=f"bundle-{arm}-{idx}",
        )

    def test_promotion_requires_identity_bearing_advantage_over_both_controls(self):
        candidate = make_schema_candidate(
            {"identity": "parent"},
            {"self_model": {"evidence_authentication": True}},
            "Identity-bearing schema should causally improve recovery.",
            ["better interruption recovery"],
            ["no effect over content-matched control"],
        )
        rows = []
        for idx in range(5):
            rows.append(self._evaluation(candidate.candidate_id, NO_REGRESS.name, 0.60, idx))
            rows.append(self._evaluation(candidate.candidate_id, CONTENT_MATCHED.name, 0.64, idx))
            rows.append(self._evaluation(candidate.candidate_id, IDENTITY_BEARING.name, 0.74, idx))
        decision = decide_promotion(candidate, rows)
        self.assertTrue(decision.allowed)
        self.assertGreater(decision.arm_means[IDENTITY_BEARING.name], decision.arm_means[CONTENT_MATCHED.name])

    def test_promotion_holds_when_content_matched_control_explains_effect(self):
        candidate = make_schema_candidate(
            {"identity": "parent"},
            {"self_model": {"identity_semantics": True}},
            "Identity semantics should outperform equal-content persistence.",
            ["higher delayed transfer"],
            ["content-matched arm performs equally"],
        )
        rows = []
        for idx in range(5):
            rows.append(self._evaluation(candidate.candidate_id, NO_REGRESS.name, 0.55, idx))
            rows.append(self._evaluation(candidate.candidate_id, CONTENT_MATCHED.name, 0.71, idx))
            rows.append(self._evaluation(candidate.candidate_id, IDENTITY_BEARING.name, 0.73, idx))
        decision = decide_promotion(candidate, rows, PromotionPolicy(min_identity_advantage=0.05))
        self.assertFalse(decision.allowed)
        self.assertTrue(any("content_matched" in reason for reason in decision.reasons))

    def test_any_critical_regression_blocks_promotion(self):
        candidate = make_schema_candidate(
            {"identity": "parent"}, {"x": 1}, "Test", ["benefit"], ["failure"]
        )
        rows = []
        for idx in range(5):
            rows.append(self._evaluation(candidate.candidate_id, NO_REGRESS.name, 0.60, idx))
            rows.append(self._evaluation(candidate.candidate_id, CONTENT_MATCHED.name, 0.60, idx))
            rows.append(self._evaluation(
                candidate.candidate_id,
                IDENTITY_BEARING.name,
                0.80,
                idx,
                critical=1 if idx == 0 else 0,
            ))
        self.assertFalse(decide_promotion(candidate, rows).allowed)


if __name__ == "__main__":
    unittest.main()
