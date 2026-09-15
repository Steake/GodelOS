import test from "node:test";
import assert from "node:assert/strict";
import {
  appendEvent, applyCompletion, chooseAgenda, initialiseRecord, parseCompletion,
  sha256, snapshot, systemPrompt, verifyDeployedChain,
} from "../netlify/functions/lib/core.mjs";

function state() {
  return {
    agent_id: "agent", name: "Aster", purpose: "Develop through evidence", episode_count: 1,
    beliefs: [], interests: [{ topic: "experimentation", salience: 0.8, intrinsic_value: 0.9, instrumental_value: 0.7, novelty: 0.6 }],
    tensions: [], relationships: [], commitments: ["Distinguish evidence from inheritance."],
    autobiographical_events: [], pending_initiatives: [], self_model: { active_values: { evidence_responsiveness: 0.82 } },
    social: { affiliation_need: 0.5, intellectual_companionship_need: 0.5, novelty_need: 0.5, recognition_need: 0.2, social_fatigue: 0.1, solitude_preference: 0.2 },
  };
}

function completion(overrides = {}) {
  return {
    reply: "I retain the distinction.", cognitive_mode: "dialogue", belief_updates: [], interest_updates: [], tension_updates: [],
    relationship_update: {}, social_update: {}, commitments_add: [], autobiographical_summary: "A test exchange occurred.",
    self_model_update: {}, initiative: { desired: false }, metacognitive_note: "The record is evidence.", ...overrides,
  };
}

test("completion parsing rejects prose and normalises optional arrays", () => {
  assert.throws(() => parseCompletion("not json", "dialogue"), /valid JSON/);
  const parsed = parseCompletion(JSON.stringify({ reply: "ok" }), "dialogue");
  assert.deepEqual(parsed.belief_updates, []);
  assert.equal(parsed.cognitive_mode, "dialogue");
});

test("state transition preserves provenance and updates relationship-specific history", () => {
  const next = applyCompletion(state(), completion({
    belief_updates: [{ proposition: "Persistence affects future reasoning", stance: "support", confidence: 0.81, reasons_for: ["Observed continuity"], reasons_against: [], origin: "self_derived", revision_conditions: ["Ablation failure"] }],
    relationship_update: { trust_honesty_delta: 0.1, affinity_delta: 0.05, influence_note: "Oli requested a causal distinction." },
  }), { mode: "dialogue", personId: "oli", personName: "Oli" });
  assert.equal(next.episode_count, 2);
  assert.equal(next.beliefs[0].origin, "self_derived");
  assert.equal(next.relationships[0].person_id, "oli");
  assert.equal(next.relationships[0].interaction_count, 1);
  assert.match(next.self_model.latest_metacognitive_note, /evidence/);
});

test("heterodox imagination remains explicitly labelled", () => {
  const next = applyCompletion(state(), completion({
    cognitive_mode: "heterodox_exploration",
    belief_updates: [{ proposition: "Contradiction is an artistic search operator", stance: "uncertain", confidence: 0.3, reasons_for: [], reasons_against: [], origin: "imagination", revision_conditions: ["Creativity benchmark"] }],
  }), { mode: "heterodox_exploration" });
  assert.equal(next.beliefs[0].origin, "imagination");
});

test("agenda is selected from persisted interests", () => {
  assert.equal(chooseAgenda(state()).topic, "experimentation");
});

test("hash chain detects mutation", () => {
  const seed = { state: state(), state_version: 1, legacy_head_hash: sha256("legacy"), legacy_event_chain_valid: true, legacy_events: [], evolution_objects: [], experiment: null };
  const record = initialiseRecord(seed);
  appendEvent(record, "dialogue", { reply: "one" });
  appendEvent(record, "deliberation", { reply: "two" });
  assert.equal(verifyDeployedChain(record), true);
  record.deployed_events[0].payload.reply = "rewritten";
  assert.equal(verifyDeployedChain(record), false);
});

test("snapshot reports configuration and chain integrity", () => {
  const record = initialiseRecord({ state: state(), state_version: 11, legacy_head_hash: null, legacy_event_chain_valid: true, legacy_events: [], evolution_objects: [], experiment: null });
  const result = snapshot(record, false);
  assert.equal(result.state_version, 11);
  assert.equal(result.runtime.provider_configured, false);
  assert.equal(result.event_chain_valid, true);
});

test("system prompt names the persistence epistemology and output contract", () => {
  const prompt = systemPrompt(state(), "dialogue", "oli");
  assert.match(prompt, /not uninterrupted subjective memory/);
  assert.match(prompt, /Return one JSON object only/);
});
