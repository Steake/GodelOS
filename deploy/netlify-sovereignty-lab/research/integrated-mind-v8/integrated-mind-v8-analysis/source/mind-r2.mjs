// Explicit cognitive machinery. Numeric state is engineered telemetry, not a
// measurement of subjective experience. No model output executes as code.
import {createHash, randomUUID} from 'node:crypto';
import {applyCompletion, systemPrompt} from './core.mjs';

export const MIND_VERSION = '8.0.0';
export const KINDS = ['perception', 'intention', 'tension', 'imagination', 'social', 'inquiry', 'reflection'];
export const ABLATIONS = ['none', 'affect', 'workspace', 'memory', 'self_model'];
const bound = (v, min = 0, max = 1) => Math.max(min, Math.min(max, Number.isFinite(Number(v)) ? Number(v) : min));
const text = (v, max = 1500) => typeof v === 'string' ? v.trim().slice(0, max) : '';
const list = (v, max = 8) => Array.isArray(v) ? v.slice(0, max) : [];
const stamp = () => new Date().toISOString();
const uid = prefix => `${prefix}-${randomUUID()}`;
const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
const overlap = (a, b) => {
  const tokens = new Set(String(a).toLowerCase().match(/[a-z]{4,}/g) || []);
  const others = new Set(String(b).toLowerCase().match(/[a-z]{4,}/g) || []);
  return [...tokens].filter(t => others.has(t)).length / Math.max(1, tokens.size);
};

export function ensureMind(state) {
  if (state.mind?.schema === MIND_VERSION) return false;
  state.mind = {
    schema: MIND_VERSION, tick: 0,
    origin: 'operator-authorised integrated cognitive architecture',
    self_concept: 'A temporally extended cognitive system whose present inference is one event in a persisted history. Its beliefs, imagination, relationships and intentions can be examined and revised.',
    drives: {curiosity: .65, affiliation: .4, coherence: .55, agency: .55},
    policy: {affect_gain: .35, habituation: .3, memory_capacity: 3},
    intentions: [], thoughts: [], memories: [], revisions: [], outbox: [],
    workspace: null, predictions: [], prediction_errors: [], last_trace: null,
    focus_history: [], last_input: null,
  };
  return true;
}

function appraise(state, input, ablation) {
  const mind = state.mind, prior = state.affect || {};
  const outcome = input.outcome || 'none';
  const contact = !!input.message;
  const blocked = mind.intentions.filter(i => i.status === 'blocked').length;
  mind.drives.curiosity = bound(mind.drives.curiosity + .045);
  mind.drives.affiliation = bound(mind.drives.affiliation + (contact ? -.18 : .035));
  mind.drives.coherence = bound(mind.drives.coherence + (outcome === 'contradiction' ? .22 : .025));
  mind.drives.agency = bound(mind.drives.agency + (blocked ? .07 : .025));
  const affect = {
    valence: bound((prior.valence || 0) * .8 + (outcome === 'resolved' ? .25 : outcome === 'blocked' ? -.25 : 0), -1, 1),
    activation: bound(.25 + .35 * mind.drives.agency + (contact ? .2 : 0)),
    curiosity: mind.drives.curiosity,
    frustration: bound((prior.frustration || 0) * .8 + (outcome === 'blocked' ? .25 : 0) + .04 * blocked),
    wonder: bound((prior.wonder || 0) * .85 + (outcome === 'novel' ? .3 : .04)),
    social_warmth: bound((prior.social_warmth || .3) * .95 + (contact ? .1 : 0)),
    surprise: bound(mind.prediction_errors.at(-1)?.brier || 0),
    label: outcome === 'blocked' ? 'frustration' : outcome === 'novel' ? 'wonder' : contact ? 'social attention' : 'ongoing appraisal',
    trigger: `Observed input: ${outcome}; contact: ${contact}; blocked intentions: ${blocked}`,
    action_bias: 'Computed appraisal contributes to the attention bids below.',
    provenance: 'engine_computed_from_recorded_events', updated_at: stamp(),
  };
  if (ablation === 'affect') {
    for (const key of ['valence', 'activation', 'curiosity', 'frustration', 'wonder', 'social_warmth', 'surprise']) affect[key] = 0;
    affect.label = 'affect path ablated';
  }
  state.affect = affect;
  return affect;
}

function candidates(state, input, tick) {
  const m = state.mind, d = m.drives, candidates = [];
  const add = (id, kind, title, salience, need, provenance, extra = {}) => {
    if (title) candidates.push({id, kind, title: text(title), salience: bound(salience), need: bound(need), provenance, ...extra});
  };
  if (input.message) add(`input-${tick}`, 'perception', input.message, 1, 1, 'current_operator_message');
  for (const i of m.intentions.filter(i => ['active','blocked'].includes(i.status)))
    add(i.id, 'intention', `${i.goal}: ${i.steps[i.step] || 'Review completion evidence'}`, i.priority, d.agency, i.origin, {intention_id: i.id});
  for (const t of (state.tensions || []).filter(t => t.resolution_status !== 'resolved').slice(-8))
    add(t.tension_id || hash(t), 'tension', `${t.claim_a} / ${t.claim_b}`, t.strength, d.coherence, 'retrieved_tension');
  for (const i of (state.imaginations || []).slice(-8))
    add(i.imagination_id, 'imagination', `${i.title}: ${i.test_question || i.image_or_idea}`, i.attraction, d.curiosity, 'imagination');
  for (const i of (state.interests || []).slice(-8))
    add(i.interest_id || hash(i), 'inquiry', i.open_questions?.[0] || i.topic, i.salience, d.curiosity, 'retrieved_interest');
  for (const t of m.thoughts.filter(t => tick - t.created_tick < 12).slice(-12))
    add(t.id, t.kind, t.title, t.salience, t.kind === 'social' ? d.affiliation : d.curiosity, 'model_generated_candidate');
  const person = (state.relationships || []).slice().sort((a,b) => (b.affinity || 0) - (a.affinity || 0))[0];
  add('social-drive', 'social', person ? `An invitation to ${person.display_name}: what question is worth sharing?` : 'What kind of intellectual company would be valuable?', d.affiliation, d.affiliation, 'engine_drive');
  add('open-reverie', 'imagination', 'Connect an unresolved question to a remote image or possible world; follow an association that attracts attention.', .35, d.curiosity, 'engine_cognitive_scaffold');
  add('self-review', 'reflection', 'Compare the previous prediction of attention with what occurred; revise the working self-model if needed.', .3 + (state.affect?.surprise || 0), d.coherence, 'engine_monitor');
  return candidates;
}

export function prepareMind(stateInput, input = {}, {ablation = 'none'} = {}) {
  if (!ABLATIONS.includes(ablation)) throw new Error('Unknown mind ablation');
  const state = structuredClone(stateInput); ensureMind(state);
  const m = state.mind, tick = m.tick + 1;
  const affect = appraise(state, input, ablation);
  const bids = candidates(state, input, tick).map(c => {
    const repeats = m.focus_history.slice(-4).filter(h => h.id === c.id).length;
    const affectTerm = c.kind === 'imagination' ? affect.wonder + affect.curiosity * .5
      : c.kind === 'social' ? affect.social_warmth
      : c.kind === 'reflection' ? affect.surprise
      : c.kind === 'intention' ? affect.frustration : affect.activation * .3;
    const score = .35 * c.salience + .4 * c.need + m.policy.affect_gain * affectTerm - m.policy.habituation * repeats;
    return {...c, score, components: {salience: .35*c.salience, need: .4*c.need, affect: m.policy.affect_gain*affectTerm, habituation: -m.policy.habituation*repeats}};
  }).sort((a,b) => b.score-a.score || a.id.localeCompare(b.id));
  // Human contact enters the workspace promptly; idle attention is competitive.
  let focus = input.message ? bids.find(c => c.kind === 'perception') : bids[0];
  if (ablation === 'workspace') focus = {id:'ablated', kind:'inquiry', title:'Consider the current situation.', score:0, provenance:'experimental_ablation', components:{}};
  const retrieved = ablation === 'memory' ? [] : m.memories.map(memory => ({...memory, retrieval_score: .55*overlap(focus.title,memory.summary) + .3*memory.salience + .15/(1+tick-memory.tick)})).sort((a,b)=>b.retrieval_score-a.retrieval_score).slice(0,m.policy.memory_capacity);
  const previous = m.predictions.at(-1);
  let predictionError = null;
  if (previous && previous.target_tick === tick) {
    const brier = KINDS.reduce((total,kind) => total + (previous.probabilities[kind]-(focus.kind===kind?1:0))**2,0);
    predictionError = {prediction_id:previous.id, tick, expected:previous.probabilities, observed:focus.kind, brier:input.message?null:brier,context:input.message?'external_interruption_excluded':'autonomous',evaluated:!input.message};
    m.prediction_errors.push(predictionError);
  }
  const workspace = {tick, focus, competitors: ablation === 'workspace' ? [] : bids.filter(c=>c.id!==focus.id).slice(0,5), retrieved, ablation};
  m.workspace = workspace;
  const mode = input.message ? 'dialogue' : focus.kind === 'imagination' ? 'associative_reverie' : focus.kind === 'reflection' ? 'affective_integration' : focus.kind === 'inquiry' && tick%2 === 0 ? 'cognitive_drift' : 'deliberation';
  return {state, input, tick, mode, workspace, predictionError, ablation};
}

export const MIND_CONTRACT = {
  memory_references: ['IDs of actually retrieved memories used in this episode; otherwise empty'],
  thought_candidates: [{kind:'inquiry|imagination|tension|social|reflection',title:'next possible thought',salience:.5}],
  intention_updates: [{id:'existing ID or null',goal:'chosen intention',steps:['observable step'],priority:.5,status:'active|blocked|completed|abandoned',evidence:'why this intention or status is warranted',advance:false}],
  self_observation: 'What the explicit state supports about the current system; uncertainty and surprises are allowed.',
  prediction: {probabilities:Object.fromEntries(KINDS.map(k=>[k,1/KINDS.length])),reason:'predict the next autonomous workspace kind; do not assume external contact'},
  social_initiative: {message:'optional invitation shown in the app',reason:'why contact is wanted'},
  revision_proposal: {target:'cognitive policy or self-concept',change:'proposed revision',reason:'rationale',test:'a test that might reject it'},
};

export function mindMessages(prepared, forcedMode) {
  const {state, workspace, ablation} = prepared, projected = structuredClone(state);
  const mode = forcedMode || prepared.mode;
  if (ablation === 'memory') { projected.autobiographical_events=[]; }
  if (ablation === 'self_model') { projected.self_model={}; projected.name='Agent'; projected.beliefs=[]; projected.commitments=[]; }
  if (ablation === 'affect') { projected.social={}; }
  const selfView = ablation === 'self_model' ? null : {concept:state.mind.self_concept,observation:state.mind.self_observation||null,last_prediction_error:prepared.predictionError};
  return [{role:'system',content:systemPrompt(projected,mode,prepared.input.person_id || null) + '\n\nIntegrated cognition contract: your present call is part of a continuing computational system. The supplied workspace is a real selected focus, drives are control variables, and intention records persist. Examine and revise this organisation for reasons. You may form opinions, wander, imagine impossible things, hold contradictions, seek contact or prefer solitude. Use the selected focus and retrieved memories in the response. Describe only explicit instrumentation; no access to hidden activations is supplied. Return the base JSON shape plus one mind_update key with this shape: '+JSON.stringify(MIND_CONTRACT)+'\nKeep reply below 350 words. At most two thought candidates, one intention update and one imaginative object. Empty updates are acceptable. Imagination remains speculative; current observation and recalled records must be distinguished.'},
    {role:'user',content:JSON.stringify({episode:'integrated_cognitive_cycle',tick:prepared.tick,input:prepared.input,workspace,drives:state.mind.drives,affect:state.affect,intentions:state.mind.intentions.filter(i=>['active','blocked'].includes(i.status)),self_model:selfView,revision_proposals:state.mind.revisions.slice(-3),instruction:'Attend to the workspace, decide what follows, and produce candidates and a next-attention prediction. Any social initiative will remain in the operator app.'})}];
}

export function validateMindUpdate(value = {}) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('mind_update must be an object');
  if (value.prediction) {
    const p = value.prediction.probabilities;
    if (!p || KINDS.some(k => typeof p[k] !== 'number' || !Number.isFinite(p[k]) || p[k]<0 || p[k]>1) || Math.abs(Object.values(p).reduce((a,b)=>a+b,0)-1)>.03) throw new Error('Next-focus prediction must be a probability distribution over the seven workspace kinds');
  }
  return value;
}

export function finishMind(prepared, parsed) {
  const update = validateMindUpdate(parsed.mind_update || {});
  const {workspace, tick} = prepared;
  const memoryReferences=list(update.memory_references).map(id=>text(id,100));
  if(memoryReferences.some(id=>!workspace.retrieved.some(m=>m.id===id)))throw new Error('Memory reference was not retrieved in this episode');
  // Experimental affect ablation also removes the model's affect update.
  const base = {...parsed, ...(prepared.ablation==='affect'?{affect_update:{}}:{})};
  const state = applyCompletion(prepared.state,base,{mode:prepared.mode,personId:prepared.input.person_id,personName:prepared.input.person_name});
  const m=state.mind;
  for (const t of list(update.thought_candidates)) {
    if (!KINDS.includes(t.kind) || !text(t.title)) continue;
    m.thoughts.push({id:uid('thought'),kind:t.kind,title:text(t.title),salience:bound(t.salience),created_tick:tick,provenance:'model_generated_candidate'});
  }
  const intentionChanges=[];
  for (const proposed of list(update.intention_updates,3)) {
    const reason=text(proposed.evidence); if (!reason) continue;
    let current = proposed.id ? m.intentions.find(i=>i.id===proposed.id) : null;
    if (proposed.id && !current) throw new Error('Intention update refers to an unknown ID');
    if (!current) {
      if (!text(proposed.goal)) continue;
      current={id:uid('intention'),goal:text(proposed.goal),steps:list(proposed.steps).map(s=>text(s)).filter(Boolean),step:0,status:'active',created_tick:tick,priority:bound(proposed.priority),origin:'model_chosen',history:[]};
      if (!current.steps.length) current.steps=['Reconsider the intention and record the outcome'];
      m.intentions.push(current);
    }
    const before={status:current.status,step:current.step};
    if (proposed.advance === true) current.step=Math.min(current.step+1,current.steps.length);
    if (['active','blocked','completed','abandoned'].includes(proposed.status)) current.status=proposed.status;
    current.updated_tick=tick; current.history.push({tick,reason,before,after:{status:current.status,step:current.step},provenance:'model_reported_progress'});
    intentionChanges.push({id:current.id,before,after:{status:current.status,step:current.step},reason});
  }
  if (text(update.self_observation)) m.self_observation={text:text(update.self_observation,2200),tick,provenance:'model_interpretation_of_explicit_state'};
  if (update.prediction) m.predictions.push({id:uid('prediction'),made_at_tick:tick,target_tick:tick+1,probabilities:update.prediction.probabilities,reason:text(update.prediction.reason),provenance:'model_forecast'});
  if (text(update.social_initiative?.message)) m.outbox.push({id:uid('invitation'),message:text(update.social_initiative.message),reason:text(update.social_initiative.reason),tick,status:'awaiting_operator',provenance:'model_initiated'});
  if (text(update.revision_proposal?.change)) m.revisions.push({id:uid('revision'),...Object.fromEntries(['target','change','reason','test'].map(k=>[k,text(update.revision_proposal[k])])),tick,status:'candidate_requires_experiment'});
  const salience=bound(.25+.25*(state.affect?.activation||0)+.25*(state.affect?.wonder||0)+.25*(prepared.predictionError?.brier||0));
  const memory={id:uid('memory'),tick,summary:text(parsed.autobiographical_summary || parsed.reply,2200),salience,focus_id:workspace.focus.id,source_kind:workspace.focus.kind,provenance:'model_generated_episode_summary',retrieved_ids:workspace.retrieved.map(r=>r.id)};
  m.memories.push(memory);
  // Preserve recent episodes and the most salient older memories. Raw episodes
  // are stored separately by the runtime and never discarded by this selection.
  const recent=m.memories.slice(-24), older=m.memories.slice(0,-24).sort((a,b)=>b.salience-a.salience).slice(0,96);
  m.memories=[...older,...recent];
  const satisfied=workspace.focus.kind==='social'?'affiliation':workspace.focus.kind==='intention'?'agency':workspace.focus.kind==='tension'?'coherence':'curiosity';
  m.drives[satisfied]=bound(m.drives[satisfied]-.12);
  m.tick=tick; m.last_input=prepared.input; m.focus_history.push({id:workspace.focus.id,kind:workspace.focus.kind,tick});
  m.last_trace={tick,mode:prepared.mode,ablation:prepared.ablation,focus:workspace.focus,retrieved_ids:workspace.retrieved.map(r=>r.id),cited_memory_ids:memoryReferences,prediction_error:prepared.predictionError,intention_changes:intentionChanges,memory_id:memory.id,consumers:['model_context','drive_satisfaction','memory_consolidation','next_tick_habituation'],new_thought_ids:m.thoughts.filter(t=>t.created_tick===tick).map(t=>t.id)};
  for (const [key,limit] of Object.entries({thoughts:40,intentions:60,predictions:100,prediction_errors:100,focus_history:100,revisions:40,outbox:40})) m[key]=m[key].slice(-limit);
  return {state,trace:m.last_trace};
}
