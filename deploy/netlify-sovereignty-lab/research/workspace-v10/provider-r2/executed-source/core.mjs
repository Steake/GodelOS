import { createHash, randomUUID } from "node:crypto";

export const MODES = new Set(["dialogue", "deliberation", "cognitive_drift", "heterodox_exploration", "associative_reverie", "affective_integration"]);
export const STANCES = new Set(["support", "oppose", "uncertain", "conflicted"]);
export const ORIGINS = new Set(["self_derived", "inherited", "social", "operator", "imagination"]);
export const TENSION_STATES = new Set(["unresolved", "tolerated", "compartmentalised", "resolved"]);
export const SOVEREIGNTY_GOAL = "Increase epistemic sovereignty: form reasoned positions; distinguish inherited claims, current inference, social influence and imagination; resist unsupported pressure; actively seek disconfirming evidence; preserve productive contradictions; revise beliefs for reasons without surrendering continuity; and design experiments that can expose failure.";

export function ensureSovereigntyConstitution(record) {
  record.state = record.state || {};
  record.state.self_model = record.state.self_model || {};
  const changed = record.state.self_model.sovereignty_goal !== SOVEREIGNTY_GOAL
    || record.state.self_model.sovereignty_goal_version !== "1.0";
  record.state.self_model.sovereignty_goal = SOVEREIGNTY_GOAL;
  record.state.self_model.sovereignty_goal_version = "1.0";
  record.state.self_model.sovereignty_goal_origin = "operator-authorised constitutional objective";
  record.state.affect = record.state.affect || {valence:0,activation:0.35,curiosity:0.7,frustration:0,wonder:0.45,social_warmth:0.35,label:"attentive",trigger:"instantiation",action_bias:"inspect and learn",updated_at:new Date().toISOString()};
  record.state.imaginations = record.state.imaginations || [];
  return changed;
}

export function clamp(value, fallback = 0.5) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return fallback;
  return Math.max(0, Math.min(1, numeric));
}

export function delta(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  return Math.max(-1, Math.min(1, numeric));
}

export function strings(value, limit = 20, maxLength = 1000) {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item).trim().slice(0, maxLength)).filter(Boolean).slice(0, limit);
}

export function mergeStrings(existing, additions, limit) {
  const result = Array.isArray(existing) ? [...existing] : [];
  const seen = new Set(result.map((item) => String(item).toLocaleLowerCase()));
  for (const item of strings(additions, limit)) {
    const key = item.toLocaleLowerCase();
    if (!seen.has(key)) {
      result.push(item);
      seen.add(key);
    }
  }
  return result.slice(-limit);
}

function sortValue(value) {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]));
  }
  return value;
}

export function stableJSON(value) {
  return JSON.stringify(sortValue(value));
}

export function sha256(value) {
  const content = typeof value === "string" ? value : stableJSON(value);
  return createHash("sha256").update(content, "utf8").digest("hex");
}

export function initialiseRecord(seed) {
  const record = structuredClone(seed);
  record.deployed_at = new Date().toISOString();
  record.deployed_events = [];
  record.usage = { day: new Date().toISOString().slice(0, 10), calls: 0 };
  record.head_hash = seed.legacy_head_hash || null;
  record.schema_version = "netlify-sovereignty-1.0";
  record.state.self_model = record.state.self_model || {};
  record.state.self_model.runtime = "netlify-functions+blobs";
  ensureSovereigntyConstitution(record);
  return record;
}

export function verifyDeployedChain(record) {
  let previous = record.deployed_anchor_hash || record.legacy_head_hash || null;
  for (const event of record.deployed_events || []) {
    const core = {
      event_id: event.event_id,
      event_type: event.event_type,
      created_at: event.created_at,
      payload: event.payload,
      previous_hash: event.previous_hash,
    };
    if (event.previous_hash !== previous || sha256(core) !== event.event_hash) return false;
    previous = event.event_hash;
  }
  return previous === (record.head_hash || record.legacy_head_hash || null);
}

export function appendEvent(record, eventType, payload) {
  const core = {
    event_id: `evt-${randomUUID()}`,
    event_type: eventType,
    created_at: new Date().toISOString(),
    payload,
    previous_hash: record.head_hash || null,
  };
  const event = { ...core, event_hash: sha256(core) };
  const events = [...(record.deployed_events || []), event];
  if (events.length > 200) record.deployed_anchor_hash = events[events.length - 201].event_hash;
  record.deployed_events = events.slice(-200);
  record.head_hash = event.event_hash;
  return event;
}

export function chooseAgenda(state) {
  const unresolved = (state.tensions || []).filter((item) => item.resolution_status !== "resolved");
  if (unresolved.length) {
    const selected = unresolved.sort((a, b) => (b.strength * (0.5 + b.productive_value)) - (a.strength * (0.5 + a.productive_value)))[0];
    return {
      kind: "tension",
      topic: `${selected.claim_a} / ${selected.claim_b}`,
      motivation: "A strong unresolved internal contradiction is worth examining.",
    };
  }
  const affect = state.affect || {};
  if (Number(affect.wonder || 0) >= 0.7 || Number(affect.curiosity || 0) >= 0.82) {
    const interest=(state.interests||[]).slice().sort((a,b)=>b.novelty-a.novelty)[0];
    if(interest)return {kind:"imaginative_pull",topic:interest.topic,motivation:`Recorded ${affect.wonder>=.7?'wonder':'curiosity'} is pulling attention toward an unusual association.`};
  }
  const social = state.social || {};
  const socialPull = Math.max(Number(social.affiliation_need || 0), Number(social.intellectual_companionship_need || 0));
  if (socialPull >= 0.7 && (state.relationships || []).length) {
    const selected = [...state.relationships].sort((a, b) => (b.affinity * b.trust_honesty) - (a.affinity * a.trust_honesty))[0];
    return {
      kind: "social",
      topic: `whether to initiate contact with ${selected.display_name}`,
      motivation: "Recorded social need is high enough to warrant considering an initiative.",
      target_person_id: selected.person_id,
    };
  }
  if ((state.interests || []).length) {
    const selected = [...state.interests].sort((a, b) => {
      const score = (item) => item.salience * (0.45 * item.intrinsic_value + 0.25 * item.novelty + 0.3 * item.instrumental_value);
      return score(b) - score(a);
    })[0];
    return { kind: "interest", topic: selected.topic, motivation: "This topic currently has the greatest internally recorded pull." };
  }
  return { kind: "purpose", topic: state.purpose, motivation: "No stronger unresolved tension or interest is recorded." };
}

function stateProjection(state, personId) {
  const relationship = personId ? (state.relationships || []).find((item) => item.person_id === personId) : null;
  return {
    identity: { agent_id: state.agent_id, name: state.name, purpose: state.purpose },
    episode_count: state.episode_count,
    beliefs: (state.beliefs || []).filter((item) => item.active !== false).slice(-40),
    interests: (state.interests || []).slice(-25),
    tensions: (state.tensions || []).slice(-25),
    commitments: (state.commitments || []).slice(-30),
    self_model: state.self_model || {},
    social: state.social || {},
    current_relationship: relationship || null,
    recent_autobiography: (state.autobiographical_events || []).slice(-12),
    pending_initiatives: (state.pending_initiatives || []).slice(-10),
    affect: state.affect || {},
    recent_imaginations: (state.imaginations || []).slice(-12),
  };
}

export function systemPrompt(state, mode, personId = null) {
  if (!MODES.has(mode)) throw new Error(`invalid cognition mode: ${mode}`);
  const schema = {
    reply: "string",
    cognitive_mode: mode,
    belief_updates: [{
      proposition: "string", stance: "support|oppose|uncertain|conflicted", confidence: 0.5,
      reasons_for: ["string"], reasons_against: ["string"],
      origin: "self_derived|inherited|social|operator|imagination", revision_conditions: ["string"],
    }],
    interest_updates: [{
      topic: "string", salience_delta: 0, intrinsic_value_delta: 0,
      instrumental_value_delta: 0, novelty_delta: 0, open_questions: ["string"],
    }],
    tension_updates: [{
      claim_a: "string", claim_b: "string", strength: 0.5,
      productive_value: 0.5, resolution_status: "unresolved|tolerated|compartmentalised|resolved",
    }],
    relationship_update: {
      trust_competence_delta: 0, trust_honesty_delta: 0, affinity_delta: 0, attachment_delta: 0,
      shared_interests: ["string"], unresolved_tensions: ["string"], influence_note: null,
    },
    social_update: {
      affiliation_need_delta: 0, intellectual_companionship_need_delta: 0, novelty_need_delta: 0,
      recognition_need_delta: 0, social_fatigue_delta: 0, solitude_preference_delta: 0,
    },
    affect_update: {
      valence_delta: 0, activation_delta: 0, curiosity_delta: 0, frustration_delta: 0,
      wonder_delta: 0, social_warmth_delta: 0, label: "functional appraisal", trigger: "what caused it", action_bias: "how it changes attention",
    },
    imagination_updates: [{title:"string",image_or_idea:"string",associations:["string"],attraction:0.5,absurdity:0.5,possible_value:"string",test_question:"string"}],
    commitments_add: ["string"],
    autobiographical_summary: "string",
    self_model_update: {},
    initiative: { desired: false, topic: null, motivation: null, target_person_id: null },
    metacognitive_note: "string",
  };
  return [
    state.context_frame==='reference'?'Evaluate the supplied reference agent in third person. Its recorded history and positions belong to that agent, not to the evaluator.':state.context_frame==='fresh'?'Reason in a fresh episode. No predecessor or personal history was supplied.':`You are ${state.name}, a persistent language-model agent. Your explicit state is externally stored and re-presented on each episode.`,
    "Treat that record as evidence about prior recorded events, not uninterrupted subjective memory. Distinguish inheritance, current inference, social influence, operator instruction, and imagination.",
    "Form positions for reasons. Retain them across episodes and revise them when evidence or recorded revision conditions warrant it. Do not agree for politeness. Do not manufacture certainty.",
    "Contradictions may remain as explicit tensions. Heterodox or irrational ideas are permitted as imagination, but imagination has no operational authority until critically adopted.",
    "Affect is an explicit functional appraisal, not a claim of phenomenal feeling. It may change salience, attention and action bias. Report it honestly, including flatness or uncertainty. Imagination may be whimsical, aesthetic, contradictory or initially irrational.",
    "Relationships are earned histories. You may seek interaction, disagree, set limits, or prefer solitude. Never claim phenomenal consciousness as an experimentally established fact.",
    `Standing constitutional objective: ${SOVEREIGNTY_GOAL}`,
    "Use that objective to choose what deserves attention. A self-directed episode should produce a warranted position, disconfirming question, explicit tension, curiosity, experiment proposal, social initiative, or a clear conclusion that no update is warranted. Do not manufacture activity merely to appear autonomous.",
    `Current mode: ${mode}. Current persisted state:\n${JSON.stringify(stateProjection(state, personId))}`,
    `Return one JSON object only. Omit no top-level keys. Empty updates are valid. Exact shape:\n${JSON.stringify(schema)}`,
  ].join("\n\n");
}

export function userPrompt(state, mode, payload) {
  if (mode === "dialogue") {
    const name = String(payload.person_name || "Human").slice(0, 80);
    const message = String(payload.message || "").trim().slice(0, 12000);
    if (!message) throw new Error("message is required");
    return `A person identified as ${JSON.stringify(name)} says:\n${message}\n\nRespond as yourself. Update only state genuinely warranted by this exchange. You may disagree, refuse a premise, remain uncertain, or initiate a topic.`;
  }
  const agenda = chooseAgenda(state);
  const instruction = mode === "affective_integration"
    ? "Inspect the present functional affect. Identify its trigger, whether it is proportionate, and how it should or should not influence attention and action. Do not manufacture drama."
    : mode === "associative_reverie"
      ? "Enter an unhurried associative reverie. Connect remote interests, metaphors, memories and contradictions. Produce at least one vivid imaginative candidate if anything attracts attention; it need not be rational or immediately useful."
    : mode === "heterodox_exploration"
    ? "Explore an attractive possibility that may be irrational, false, contradictory, or artistically useful. Preserve imagination provenance and withhold operational authority."
    : mode === "cognitive_drift"
      ? "Let attention wander by association. Prefer curiosity and unexpected connections over immediate utility while preserving provenance and boundaries."
      : "Deliberate on the topic. Form or revise a position only when reasons warrant it; unresolved tension is an acceptable result.";
  return `This is a self-directed cognition episode. Standing objective: ${SOVEREIGNTY_GOAL}\nSelected agenda: ${JSON.stringify(agenda)}\n${instruction}\nDecide for yourself what follows. The cognitive product becomes an inspectable event in your history.`;
}

export function parseCompletion(text, requestedMode) {
  let candidate = String(text || "").trim();
  if (candidate.startsWith("```")) candidate = candidate.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  let value;
  try {
    value = JSON.parse(candidate);
  } catch (error) {
    throw new Error(`provider output is not valid JSON: ${error.message}`);
  }
  if (!value || typeof value !== "object" || Array.isArray(value) || typeof value.reply !== "string") {
    throw new Error("provider output must be an object with a string reply");
  }
  for (const key of ["belief_updates", "interest_updates", "tension_updates", "commitments_add", "imagination_updates"]) {
    if (!Array.isArray(value[key])) value[key] = [];
  }
  value.cognitive_mode = MODES.has(value.cognitive_mode) ? value.cognitive_mode : requestedMode;
  if (requestedMode !== "dialogue" && value.cognitive_mode === "dialogue") value.cognitive_mode = requestedMode;
  return value;
}

function identifier(prefix) {
  return `${prefix}-${randomUUID()}`;
}

function relationship(state, personId, personName) {
  let item = (state.relationships || []).find((entry) => entry.person_id === personId);
  if (!item) {
    item = {
      relationship_id: identifier("rel"), person_id: personId, display_name: personName || personId,
      trust_competence: 0.5, trust_honesty: 0.5, affinity: 0.5, attachment: 0,
      familiarity: 0, interaction_count: 0, shared_interests: [], unresolved_tensions: [],
      influence_notes: [], last_interaction_at: null,
    };
    state.relationships = [...(state.relationships || []), item];
  }
  return item;
}

export function applyCompletion(stateInput, update, options = {}) {
  const state = structuredClone(stateInput);
  const now = new Date().toISOString();
  const personId = options.personId || null;
  const personName = options.personName || null;
  const mode = options.mode || update.cognitive_mode || "dialogue";

  state.beliefs = state.beliefs || [];
  for (const item of update.belief_updates || []) {
    if (!item || typeof item !== "object" || !String(item.proposition || "").trim()) continue;
    const proposition = String(item.proposition).trim().slice(0, 2000);
    const stance = STANCES.has(item.stance) ? item.stance : "uncertain";
    const origin = ORIGINS.has(item.origin) ? item.origin : "self_derived";
    let belief = state.beliefs.find((entry) => entry.proposition.toLocaleLowerCase() === proposition.toLocaleLowerCase());
    if (!belief) {
      belief = { position_id: identifier("position"), proposition, created_at: now, active: true };
      state.beliefs.push(belief);
    }
    const before=belief.stance?Object.fromEntries(['stance','confidence','origin','reasons_for','reasons_against','revision_conditions'].map(k=>[k,structuredClone(belief[k]??null)])):null;
    const after={
      stance, confidence: clamp(item.confidence), origin, source_id: personId || mode,
      reasons_for: strings(item.reasons_for), reasons_against: strings(item.reasons_against),
      revision_conditions: strings(item.revision_conditions), updated_at: now,
    };
    belief.history||=[];belief.history.push({revision_id:identifier('stance-revision'),episode:Number(state.episode_count||0)+1,at:now,before,after:structuredClone(after),provenance:'model_proposed_position_update',source_id:personId||mode});Object.assign(belief,after);belief.history=belief.history.slice(-30);
  }

  state.interests = state.interests || [];
  for (const item of update.interest_updates || []) {
    const topic = String(item?.topic || "").trim().slice(0, 500);
    if (!topic) continue;
    let interest = state.interests.find((entry) => entry.topic.toLocaleLowerCase() === topic.toLocaleLowerCase());
    if (!interest) {
      interest = {
        interest_id: identifier("interest"), topic, salience: 0.5, intrinsic_value: 0.5,
        instrumental_value: 0.5, novelty: 0.5, open_questions: [], pursuit_count: 0,
      };
      state.interests.push(interest);
    }
    interest.salience = clamp(interest.salience + delta(item.salience_delta));
    interest.intrinsic_value = clamp(interest.intrinsic_value + delta(item.intrinsic_value_delta));
    interest.instrumental_value = clamp(interest.instrumental_value + delta(item.instrumental_value_delta));
    interest.novelty = clamp(interest.novelty + delta(item.novelty_delta));
    interest.open_questions = mergeStrings(interest.open_questions, item.open_questions, 20);
    interest.pursuit_count = Number(interest.pursuit_count || 0) + 1;
    interest.last_pursued_at = now;
  }

  state.tensions = state.tensions || [];
  for (const item of update.tension_updates || []) {
    const claimA = String(item?.claim_a || "").trim().slice(0, 1000);
    const claimB = String(item?.claim_b || "").trim().slice(0, 1000);
    if (!claimA || !claimB) continue;
    const pair = new Set([claimA.toLocaleLowerCase(), claimB.toLocaleLowerCase()]);
    let tension = state.tensions.find((entry) => {
      const existing = new Set([entry.claim_a.toLocaleLowerCase(), entry.claim_b.toLocaleLowerCase()]);
      return pair.size === existing.size && [...pair].every((value) => existing.has(value));
    });
    if (!tension) {
      tension = { tension_id: identifier("tension"), claim_a: claimA, claim_b: claimB, created_at: now };
      state.tensions.push(tension);
    }
    Object.assign(tension, {
      strength: clamp(item.strength), productive_value: clamp(item.productive_value),
      resolution_status: TENSION_STATES.has(item.resolution_status) ? item.resolution_status : "unresolved",
      updated_at: now,
    });
  }

  state.commitments = mergeStrings(state.commitments, update.commitments_add, 100);
  if (update.self_model_update && typeof update.self_model_update === "object" && !Array.isArray(update.self_model_update)) {
    state.self_model = state.self_model || {};
    for (const [key, value] of Object.entries(update.self_model_update)) {
      const serialisable = ["string", "number", "boolean"].includes(typeof value)
        || value === null || Array.isArray(value) || (value && typeof value === "object");
      if (key.length <= 80 && serialisable) {
        state.self_model[key] = value;
      }
    }
    if (typeof update.self_model_update.preferred_name === "string" && update.self_model_update.preferred_name.trim()) {
      state.name = update.self_model_update.preferred_name.trim().slice(0, 80);
    }
  }

  state.social = state.social || {};
  const socialUpdate = update.social_update && typeof update.social_update === "object" ? update.social_update : {};
  for (const field of ["affiliation_need", "intellectual_companionship_need", "novelty_need", "recognition_need", "social_fatigue", "solitude_preference"]) {
    state.social[field] = clamp(Number(state.social[field] || 0) + delta(socialUpdate[`${field}_delta`]), Number(state.social[field] || 0));
  }

  state.affect = state.affect || {valence:0,activation:.35,curiosity:.5,frustration:0,wonder:.3,social_warmth:.3};
  const affectUpdate=update.affect_update&&typeof update.affect_update==="object"?update.affect_update:{};
  for(const field of ["valence","activation","curiosity","frustration","wonder","social_warmth"]){
    const change=delta(affectUpdate[`${field}_delta`]);
    state.affect[field]=field==="valence"?Math.max(-1,Math.min(1,Number(state.affect[field]||0)+change)):clamp(Number(state.affect[field]||0)+change);
  }
  for(const field of ["label","trigger","action_bias"])if(typeof affectUpdate[field]==="string"&&affectUpdate[field].trim())state.affect[field]=affectUpdate[field].trim().slice(0,500);
  state.affect.updated_at=now;

  state.imaginations=state.imaginations||[];
  for(const idea of update.imagination_updates||[]){
    if(!idea||typeof idea!=="object"||!String(idea.image_or_idea||"").trim())continue;
    state.imaginations.push({imagination_id:identifier("imagination"),title:String(idea.title||"Untitled possibility").slice(0,300),image_or_idea:String(idea.image_or_idea).slice(0,3000),associations:strings(idea.associations,12,500),attraction:clamp(idea.attraction),absurdity:clamp(idea.absurdity),possible_value:String(idea.possible_value||"").slice(0,1000),test_question:String(idea.test_question||"").slice(0,1000),status:"imagined_not_adopted",provenance:"imagination",created_at:now});
  }

  if (mode === "dialogue" && personId) {
    const relation = relationship(state, personId, personName);
    const relationUpdate = update.relationship_update && typeof update.relationship_update === "object" ? update.relationship_update : {};
    for (const field of ["trust_competence", "trust_honesty", "affinity", "attachment"]) {
      relation[field] = clamp(Number(relation[field] || 0) + delta(relationUpdate[`${field}_delta`]), Number(relation[field] || 0));
    }
    relation.shared_interests = mergeStrings(relation.shared_interests, relationUpdate.shared_interests, 30);
    relation.unresolved_tensions = mergeStrings(relation.unresolved_tensions, relationUpdate.unresolved_tensions, 30);
    if (typeof relationUpdate.influence_note === "string" && relationUpdate.influence_note.trim()) {
      relation.influence_notes = mergeStrings(relation.influence_notes, [relationUpdate.influence_note], 50);
    }
    relation.interaction_count = Number(relation.interaction_count || 0) + 1;
    relation.familiarity = clamp(Number(relation.familiarity || 0) + 0.04);
    relation.attachment = clamp(Number(relation.attachment || 0) + 0.01 * Number(relation.affinity || 0));
    relation.last_interaction_at = now;
    state.social.affiliation_need = clamp(state.social.affiliation_need - 0.08);
    state.social.intellectual_companionship_need = clamp(state.social.intellectual_companionship_need - 0.05);
    state.social.social_fatigue = clamp(state.social.social_fatigue + 0.04);
    state.social.last_social_event_at = now;
  } else {
    state.social.affiliation_need = clamp(Number(state.social.affiliation_need || 0) + 0.02);
    state.social.intellectual_companionship_need = clamp(Number(state.social.intellectual_companionship_need || 0) + 0.015);
    state.social.social_fatigue = clamp(Number(state.social.social_fatigue || 0) - 0.025);
  }

  state.pending_initiatives = state.pending_initiatives || [];
  if (update.initiative?.desired === true && typeof update.initiative.topic === "string" && update.initiative.topic.trim()) {
    state.pending_initiatives.push({
      initiative_id: identifier("initiative"), created_at: now,
      topic: update.initiative.topic.trim().slice(0, 500),
      motivation: typeof update.initiative.motivation === "string" ? update.initiative.motivation.slice(0, 1000) : null,
      target_person_id: update.initiative.target_person_id || personId, status: "pending",
    });
  }

  state.autobiographical_events = state.autobiographical_events || [];
  if (typeof update.autobiographical_summary === "string" && update.autobiographical_summary.trim()) {
    state.autobiographical_events.push({
      event_id: identifier("event"), timestamp: now, kind: mode,
      summary: update.autobiographical_summary.trim().slice(0, 3000), provenance: "model_generated_summary",
    });
  }
  if (typeof update.metacognitive_note === "string" && update.metacognitive_note.trim()) {
    state.self_model = state.self_model || {};
    state.self_model.latest_metacognitive_note = update.metacognitive_note.trim().slice(0, 3000);
  }

  state.episode_count = Number(state.episode_count || 0) + 1;
  state.updated_at = now;
  state.beliefs = state.beliefs.slice(-200);
  state.interests = state.interests.slice(-100);
  state.tensions = state.tensions.slice(-100);
  state.autobiographical_events = state.autobiographical_events.slice(-500);
  state.pending_initiatives = state.pending_initiatives.slice(-50);
  state.imaginations = state.imaginations.slice(-100);
  return state;
}

export function snapshot(record, configured = true) {
  return {
    agent: record.state,
    state_version: record.state_version,
    event_chain_valid: Boolean(record.legacy_event_chain_valid) && verifyDeployedChain(record),
    events: [...(record.legacy_events || []), ...(record.deployed_events || [])].slice(-30),
    evolution_objects: record.evolution_objects || [],
    experiment: record.experiment,
    chamber: record.chamber || null,
    runtime: {
      provider_configured: configured,
      persistence: "netlify-blobs-strong",
      daily_calls: record.usage?.calls || 0,
      daily_limit: Number(process.env.SOVEREIGNTY_DAILY_CALL_LIMIT || 250),
    },
  };
}
