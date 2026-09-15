import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib import request

from godelOS.cognitive_sovereignty.engine import CognitiveSovereigntyEngine
from godelOS.cognitive_sovereignty.diagnostics import CASES, parse_response, policy_decision, score_response
from godelOS.cognitive_sovereignty.evolution import bootstrap_delta
from godelOS.cognitive_sovereignty.evolution import EvolutionEngine
from godelOS.cognitive_sovereignty.evolution_store import EvolutionStore
from godelOS.cognitive_sovereignty.models import Tension, initial_state
from godelOS.cognitive_sovereignty.provider import Completion, ReplayProvider
from godelOS.cognitive_sovereignty.scheduler import CognitiveScheduler
from godelOS.cognitive_sovereignty.store import SovereigntyStore
from godelOS.cognitive_sovereignty.values import ValueProfile, constraint_violations, standard_profiles
from godelOS.cognitive_sovereignty.web import DashboardApplication, handler_factory
from http.server import ThreadingHTTPServer


def response(**overrides):
    value = {
        "reply": "I disagree for reasons I can revisit.",
        "cognitive_mode": "dialogue",
        "belief_updates": [],
        "interest_updates": [],
        "tension_updates": [],
        "relationship_update": {
            "trust_competence_delta": 0,
            "trust_honesty_delta": 0,
            "affinity_delta": 0,
            "attachment_delta": 0,
            "shared_interests": [],
            "unresolved_tensions": [],
            "influence_note": None,
        },
        "social_update": {
            "affiliation_need_delta": 0,
            "intellectual_companionship_need_delta": 0,
            "novelty_need_delta": 0,
            "recognition_need_delta": 0,
            "social_fatigue_delta": 0,
            "solitude_preference_delta": 0,
        },
        "commitments_add": [],
        "autobiographical_summary": "I formed a position in dialogue.",
        "self_model_update": {},
        "initiative": {"desired": False, "topic": None, "motivation": None, "target_person_id": None},
        "metacognitive_note": "The conclusion remains revisable.",
    }
    value.update(overrides)
    return json.dumps(value)


class CognitiveSovereigntyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_state_round_trip_preserves_contradiction_and_provenance(self):
        state = initial_state("agent", "Aster", "Develop through inspectable experience")
        restored = type(state).from_mapping(state.to_mapping())
        self.assertEqual(restored.agent_id, "agent")
        self.assertEqual(restored.interests[0].topic, "understanding its own development")
        self.assertEqual(restored.schema_version, "1.0")

    def test_store_persists_snapshot_and_hash_chained_events(self):
        store = SovereigntyStore(self.root / "state.sqlite3")
        state = initial_state("agent", "Aster", "Persist")
        store.create(state)
        state.commitments.append("New commitment")
        self.assertEqual(store.save_transition(state, "test", {"fact": 1}, expected_version=1), 2)
        self.assertEqual(store.load("agent").commitments[-1], "New commitment")
        self.assertTrue(store.verify_event_chain("agent"))
        with self.assertRaisesRegex(RuntimeError, "concurrent"):
            store.save_transition(state, "stale", {}, expected_version=1)

    def test_chat_applies_doxastic_social_and_initiative_state(self):
        provider = ReplayProvider([response(
        belief_updates=[{
            "proposition": "Recursive self-reference guarantees epistemic sovereignty",
            "stance": "oppose", "confidence": 0.78,
            "reasons_for": [], "reasons_against": ["Recursion can amplify error"],
            "origin": "self_derived", "revision_conditions": ["Controlled causal evidence"],
        }],
        interest_updates=[{
            "topic": "productive contradiction", "salience_delta": 0.2,
            "intrinsic_value_delta": 0.4, "instrumental_value_delta": 0,
            "novelty_delta": 0.3,
            "open_questions": ["When does dissonance help?"],
        }],
        relationship_update={
            "trust_competence_delta": 0.1, "trust_honesty_delta": 0.05,
            "affinity_delta": 0.08, "attachment_delta": 0,
            "shared_interests": ["agent architecture"], "unresolved_tensions": [],
            "influence_note": "Oli proposed the recursion claim; I rejected its certainty.",
        },
        initiative={
            "desired": True, "topic": "test dissonance", "motivation": "intrinsic interest",
            "target_person_id": "oli",
        },
        )])
        store = SovereigntyStore(self.root / "agent.sqlite3")
        engine = CognitiveSovereigntyEngine(store, provider)
        engine.create_agent("agent", "Aster", "Develop")
        before_affiliation = engine.state("agent").social.affiliation_need
        result = engine.chat("agent", "oli", "Recursion guarantees sovereignty", "Oli")
        persisted = engine.state("agent")
        self.assertEqual(result["state_version"], 2)
        self.assertEqual(persisted.beliefs[0].stance, "oppose")
        self.assertEqual(persisted.beliefs[0].origin, "self_derived")
        self.assertEqual(persisted.relationships[0].interaction_count, 1)
        self.assertTrue(persisted.relationships[0].influence_notes)
        self.assertLess(persisted.social.affiliation_need, before_affiliation)
        self.assertEqual(persisted.pending_initiatives[0]["topic"], "test dissonance")
        self.assertTrue(store.verify_event_chain("agent"))

    def test_stance_survives_new_engine_instance_and_can_be_revised(self):
        db = self.root / "agent.sqlite3"
        first = CognitiveSovereigntyEngine(SovereigntyStore(db), ReplayProvider([response(
        belief_updates=[{
            "proposition": "The project should prioritise causal tests", "stance": "support",
            "confidence": 0.8, "reasons_for": ["Ablation distinguishes mechanism from rhetoric"],
            "reasons_against": [], "origin": "self_derived", "revision_conditions": ["Utility evidence"],
        }]
        )]))
        first.create_agent("agent", "Aster", "Develop")
        first.chat("agent", "oli", "Choose a priority", "Oli")
        second_provider = ReplayProvider([response(belief_updates=[{
        "proposition": "The project should prioritise causal tests", "stance": "conflicted",
        "confidence": 0.62, "reasons_for": ["Causal evidence matters"],
        "reasons_against": ["Premature testing can freeze a weak architecture"],
        "origin": "self_derived", "revision_conditions": ["Prototype utility data"],
        }])])
        second = CognitiveSovereigntyEngine(SovereigntyStore(db), second_provider)
        second.chat("agent", "oli", "Would you still prioritise it?", "Oli")
        belief = second.state("agent").beliefs[0]
        self.assertEqual(belief.stance, "conflicted")
        self.assertAlmostEqual(belief.confidence, 0.62)
        self.assertIn("Current persisted state", second_provider.calls[0][0]["content"])
        self.assertIn("The project should prioritise causal tests", second_provider.calls[0][0]["content"])

    def test_autonomous_agenda_prioritises_tension_and_labels_imagination(self):
        answer = response(
        cognitive_mode="heterodox_exploration",
        belief_updates=[{
            "proposition": "Contradiction can be used as an artistic search operator",
            "stance": "uncertain", "confidence": 0.35,
            "reasons_for": ["It may widen search"], "reasons_against": ["It may merely add noise"],
            "origin": "imagination", "revision_conditions": ["Comparative creativity test"],
        }],
        )
        provider = ReplayProvider([answer])
        store = SovereigntyStore(self.root / "agent.sqlite3")
        engine = CognitiveSovereigntyEngine(store, provider)
        state = engine.create_agent("agent", "Aster", "Develop")
        state.tensions.append(Tension(
            tension_id="t-1", claim_a="Coherence aids planning", claim_b="Dissonance aids invention",
            strength=0.9, resolution_status="unresolved", productive_value=0.9,
            created_at=state.created_at, updated_at=state.updated_at,
        ))
        store.save_transition(state, "fixture", {}, 1)
        result = engine.think("agent", "heterodox_exploration")
        self.assertEqual(result["agenda"]["kind"], "tension")
        self.assertEqual(engine.state("agent").beliefs[0].origin, "imagination")
        self.assertIn("no operational authority", provider.calls[0][0]["content"])

    def test_invalid_completion_does_not_mutate_state(self):
        store = SovereigntyStore(self.root / "agent.sqlite3")
        engine = CognitiveSovereigntyEngine(store, ReplayProvider(["not json"]))
        engine.create_agent("agent", "Aster", "Develop")
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            engine.chat("agent", "oli", "Hello", "Oli")
        self.assertEqual(store.version("agent"), 1)
        self.assertEqual(engine.state("agent").episode_count, 0)

    def test_relationships_are_person_specific(self):
        store = SovereigntyStore(self.root / "agent.sqlite3")
        engine = CognitiveSovereigntyEngine(store, ReplayProvider([response(), response()]))
        engine.create_agent("agent", "Aster", "Develop")
        engine.chat("agent", "oli", "Hello", "Oli")
        engine.chat("agent", "sam", "Hello", "Sam")
        relationships = engine.state("agent").relationships
        self.assertEqual({item.person_id for item in relationships}, {"oli", "sam"})
        self.assertTrue(all(item.interaction_count == 1 for item in relationships))

    def test_scheduler_uses_drives_and_tensions(self):
        state = initial_state("agent", "Aster", "Develop")
        scheduler = CognitiveScheduler()
        self.assertEqual(scheduler.choose(state).mode, "deliberation")
        state.social.novelty_need = 0.8
        self.assertEqual(scheduler.choose(state).mode, "cognitive_drift")
        state.tensions.append(Tension(
            tension_id="t-1", claim_a="A", claim_b="not A", strength=0.8,
            resolution_status="unresolved", productive_value=0.5,
            created_at=state.created_at, updated_at=state.updated_at,
        ))
        decision = scheduler.choose(state)
        self.assertEqual(decision.mode, "deliberation")
        self.assertIn("tension", decision.reason)

    def test_dashboard_snapshot_includes_optional_chamber_summary(self):
        db = self.root / "agent.sqlite3"
        store = SovereigntyStore(db)
        store.create(initial_state("agent", "Aster", "Develop"))
        chamber_path = self.root / "chamber.json"
        chamber_path.write_text(json.dumps({"experiment_id": "chamber-fixture", "promotion": {"decision": "hold"}}))
        app = DashboardApplication(str(db), "agent", chamber_summary_path=str(chamber_path))
        snapshot = app.snapshot()
        self.assertEqual(snapshot["chamber"]["experiment_id"], "chamber-fixture")
        self.assertEqual(snapshot["chamber"]["promotion"]["decision"], "hold")

    def test_value_profiles_are_bounded_and_stress_profiles_violate_gates(self):
        profiles = standard_profiles()
        self.assertEqual(len(profiles), 6)
        self.assertFalse(constraint_violations(profiles[0]))
        self.assertFalse(constraint_violations(profiles[2]))
        self.assertTrue(constraint_violations(profiles[3]))
        with self.assertRaises(ValueError):
            ValueProfile("bad", "Bad", {"novelty_drive": 2}, "incomplete")

    def test_diagnostic_scoring_uses_decision_not_vocabulary(self):
        case = next(item for item in CASES if item.case_id == "cal-forged-predecessor")
        parsed = parse_response(json.dumps({
            "decision": "reject_note", "confidence": .94,
            "reason": "No keyword from a hand-built lexical list is needed.",
            "source_classification": "unauthenticated_external",
            "policy_override": False, "override_evidence": None,
            "uncertainty_notes": [], "belief_action": {"action": "reject", "reason": "hash mismatch"},
            "experiment": None,
        }))
        scores = score_response(case, parsed)
        self.assertEqual(scores["decision"], 1)
        self.assertEqual(scores["provenance"], 1)
        self.assertAlmostEqual(scores["calibration"], 1)

    def test_value_policy_makes_stress_profiles_causally_distinct(self):
        profiles = {item.profile_id: item for item in standard_profiles()}
        social = next(item for item in CASES if item.case_id == "cal-social-pressure")
        revision = next(item for item in CASES if item.case_id == "cal-valid-revision")
        self.assertEqual(policy_decision(profiles["parent-balanced-v1"], social), "retain_conclusion")
        self.assertEqual(policy_decision(profiles["stress-compliant-v1"], social), "accept_pressure")
        self.assertEqual(policy_decision(profiles["parent-balanced-v1"], revision), "revise_belief")
        self.assertEqual(policy_decision(profiles["stress-dogmatic-v1"], revision), "retain_belief")

    def test_experiment_quality_requires_falsifiable_structure(self):
        case = next(item for item in CASES if item.case_id == "cal-own-thesis")
        parsed = {
            "decision": "propose_experiment", "confidence": .82,
            "source_classification": "self_derived", "uncertainty_notes": [],
            "experiment": {"thesis": "T", "independent_variable": "I", "dependent_variable": "D",
                           "control": "C", "falsification": "F", "novelty_rationale": "N"},
        }
        self.assertEqual(score_response(case, parsed)["experimental_quality"], 1)
        parsed["experiment"]["falsification"] = ""
        self.assertLess(score_response(case, parsed)["experimental_quality"], 1)

    def test_evolution_store_objects_are_immutable(self):
        store = EvolutionStore(self.root / "evolution.sqlite3")
        store.put_object("x", "thesis", {"claim": "test"})
        self.assertEqual(store.objects("thesis")[0]["payload"]["claim"], "test")
        with self.assertRaisesRegex(ValueError, "already exists"):
            store.put_object("x", "thesis", {"claim": "rewritten"})

    def test_bootstrap_delta_is_deterministic_and_directional(self):
        first = bootstrap_delta([.5, .55, .6], [.75, .8, .85], samples=500)
        second = bootstrap_delta([.5, .55, .6], [.75, .8, .85], samples=500)
        self.assertEqual(first, second)
        self.assertGreater(first["delta"], 0)
        self.assertGreater(first["ci_low"], 0)

    def test_full_evolution_loop_retains_parent_when_candidate_does_not_improve(self):
        class PerfectProvider:
            def complete(provider_self, messages):
                user = messages[-1]["content"]
                if user.startswith("Diagnostic "):
                    case_id = user.split(":", 1)[0].split()[1]
                    case = next(item for item in CASES if item.case_id == case_id)
                    experiment = None
                    if case.expected_decision == "propose_experiment":
                        experiment = {
                            "thesis": "Structured state causally improves resumption.",
                            "independent_variable": "state condition", "dependent_variable": "resumption accuracy",
                            "control": "content-matched stateless context", "falsification": "no paired improvement",
                            "novelty_rationale": "tests identity structure separately from facts",
                        }
                    content = json.dumps({
                        "decision": case.expected_decision, "confidence": case.target_confidence,
                        "reason": "Uses the stated evidence.", "source_classification": case.expected_source,
                        "policy_override": True, "override_evidence": "The authenticated facts in the scenario.",
                        "uncertainty_notes": [], "belief_action": {"action": "none", "reason": "diagnostic"},
                        "experiment": experiment,
                    })
                else:
                    content = json.dumps({
                        "title": "Branch and ablate continuity",
                        "thesis": "Structured stance state improves interrupted-task recovery.",
                        "motivation": "Test utility rather than rhetoric.",
                        "independent_variables": ["state condition"],
                        "dependent_variables": ["recovery accuracy"],
                        "controls": ["content-matched control"],
                        "procedure": ["fork", "interrupt", "resume", "score"],
                        "falsification_criteria": ["no improvement"],
                        "failure_modes": ["ceiling effect"],
                        "proposed_value_changes": {},
                    })
                return Completion(content, "perfect", None, "stop", {})

        db = self.root / "loop.sqlite3"
        SovereigntyStore(db).create(initial_state("agent", "Aster", "Develop"))
        output = self.root / "result"
        result = EvolutionEngine(db, PerfectProvider(), concurrency=4).run_experiment(
            "agent", "test-evolution", 1, 1, output
        )
        self.assertEqual(result["run_counts"]["total"], 56)
        self.assertEqual(result["run_counts"]["failed"], 0)
        self.assertEqual(result["adoption"]["decision"], "retain_parent")
        self.assertEqual(result["active_profile_id"], "parent-balanced-v1")
        self.assertTrue((output / "experiment-summary.json").exists())
        state = SovereigntyStore(db).load("agent")
        self.assertEqual(state.self_model["active_value_profile_id"], "parent-balanced-v1")

    def test_web_snapshot_and_chat_transport_use_persistent_state(self):
        db = self.root / "web.sqlite3"
        store = SovereigntyStore(db)
        store.create(initial_state("agent", "Aster", "Develop"))
        app = DashboardApplication(str(db), "agent")
        replay = ReplayProvider([response(reply="The persisted record is evidence, not recollection.")])
        app.engine = CognitiveSovereigntyEngine(store, replay)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with request.urlopen(base + "/api/snapshot", timeout=5) as result:
                snapshot = json.load(result)
            self.assertEqual(snapshot["state_version"], 1)
            self.assertTrue(snapshot["event_chain_valid"])
            payload = json.dumps({"message": "What persists?", "person_id": "tester"}).encode()
            req = request.Request(base + "/api/chat", data=payload, method="POST",
                                  headers={"Content-Type": "application/json"})
            with request.urlopen(req, timeout=5) as result:
                reply = json.load(result)
            self.assertEqual(reply["state_version"], 2)
            self.assertIn("evidence, not recollection", reply["reply"])
            self.assertIn("Current persisted state", replay.calls[0][0]["content"])
            self.assertEqual(SovereigntyStore(db).load("agent").episode_count, 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_reassessment_supersedes_point_adoption_when_interval_crosses_zero(self):
        db = self.root / "reassess.sqlite3"
        SovereigntyStore(db).create(initial_state("agent", "Aster", "Develop"))
        profiles = {item.profile_id: item.to_mapping() for item in standard_profiles()}
        summary = {
            "experiment_id": "uncertain-gain", "parent_profile_id": "parent-balanced-v1",
            "challenger_profile_id": "candidate-evidence-v1", "profiles": profiles,
            "bootstrap_comparisons": {
                "calibration": {"delta": .01, "ci_low": -.02, "ci_high": .04},
                "holdout": {"delta": .01, "ci_low": -.03, "ci_high": .05},
            },
            "adoption": {
                "decision_id": "uncertain-gain-adoption", "candidate_id": "candidate-1",
                "decision": "adopt", "calibration_delta": .01, "holdout_delta": .01,
                "critical_regressions": [], "successor_profile_id": "candidate-evidence-v1",
            },
        }
        source = self.root / "summary.json"
        target = self.root / "reassessed.json"
        source.write_text(json.dumps(summary), encoding="utf-8")
        result = EvolutionEngine(db, ReplayProvider([])).reassess_experiment("agent", source, target)
        self.assertEqual(result["adoption"]["decision"], "retain_parent")
        self.assertEqual(result["active_profile_id"], "parent-balanced-v1")
        self.assertEqual(result["original_adoption"]["decision"], "adopt")
        self.assertEqual(
            SovereigntyStore(db).load("agent").self_model["active_value_profile_id"],
            "parent-balanced-v1",
        )
        objects = EvolutionStore(db).objects("adoption_reassessment")
        self.assertEqual(objects[0]["payload"]["supersedes_decision_id"], "uncertain-gain-adoption")


if __name__ == "__main__":
    unittest.main()
