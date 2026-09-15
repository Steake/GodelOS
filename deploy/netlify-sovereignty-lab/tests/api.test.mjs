import test from "node:test";
import assert from "node:assert/strict";
import { createHandler,readDeepSeekStream } from "../netlify/functions/api.mjs";

class MemoryStore {
  constructor() {
    this.entries = new Map();
    this.data = null;
    this.etag = null;
    this.version = 0;
  }

  async getWithMetadata(_key, options) {
    if (_key !== 'agent/godelos-sovereign-01/state') return structuredClone(this.entries.get(_key) || null);
    if (!this.data) return null;
    return { data: options?.type === "json" ? structuredClone(this.data) : JSON.stringify(this.data), etag: this.etag, metadata: {} };
  }

  async setJSON(_key, value, options = {}) {
    if (_key !== 'agent/godelos-sovereign-01/state') {
      const old=this.entries.get(_key);
      if(options.onlyIfNew&&old||options.onlyIfMatch&&old?.etag!==options.onlyIfMatch)return {modified:false};
      const etag='aux-'+(++this.version);this.entries.set(_key,{data:structuredClone(value),etag});return {modified:true,etag};
    }
    if (options.onlyIfNew && this.data) return { modified: false };
    if (options.onlyIfMatch && options.onlyIfMatch !== this.etag) return { modified: false };
    this.data = structuredClone(value);
    this.version += 1;
    this.etag = `etag-${this.version}`;
    return { modified: true, etag: this.etag };
  }
}

function request(path, method = "GET", payload = null, authorised = true) {
  const headers = {};
  if (authorised) headers.authorization = "Bearer test-access-token";
  if (payload) headers["content-type"] = "application/json";
  return new Request(`https://example.netlify.app${path}`, {
    method, headers, body: payload ? JSON.stringify(payload) : undefined,
  });
}

const modelReply = {
  text: JSON.stringify({
    reply: "The persisted record is evidence, not recollection.", cognitive_mode: "dialogue",
    belief_updates: [], interest_updates: [], tension_updates: [], relationship_update: {},
    social_update: {}, commitments_add: [], autobiographical_summary: "A deployment test occurred.",
    self_model_update: {}, initiative: { desired: false }, metacognitive_note: "Provenance remains explicit.",
  }),
  model: "mock-deepseek", response_id: "mock-1", finish_reason: "stop", usage: { total_tokens: 42 },
};

test("API gates state, initialises seed, and persists a chat transition", async () => {
  process.env.SOVEREIGNTY_ACCESS_TOKEN = "test-access-token";
  process.env.DEEPSEEK_API_KEY = "test-provider-key";
  const store = new MemoryStore();
  const handler = createHandler({ storeFactory: () => store, completionProvider: async () => modelReply });

  const health = await handler(request("/api/health", "GET", null, false));
  assert.equal(health.status, 200);
  assert.equal((await health.json()).provider_configured, true);

  const denied = await handler(request("/api/snapshot", "GET", null, false));
  assert.equal(denied.status, 401);

  const before = await handler(request("/api/snapshot"));
  const initial = await before.json();
  assert.equal(before.status, 200);
  assert.equal(initial.state_version, 11);
  assert.equal(initial.model_status.last_response,null);
  assert.equal(initial.model_status.configured,process.env.DEEPSEEK_MODEL||"deepseek-flash");
  assert.equal(initial.experiment.run_counts.completed, 120);

  const chat = await handler(request("/api/chat", "POST", {
    person_id: "deployment-test", person_name: "Verifier", message: "What persists?",
  }));
  const result = await chat.json();
  assert.equal(chat.status, 200);
  assert.equal(result.state_version, 12);
  assert.match(result.reply, /evidence, not recollection/);

  const after = await handler(request("/api/snapshot"));
  const persisted = await after.json();
  assert.equal(persisted.model_status.last_response.model,"mock-deepseek");
  assert.notEqual(persisted.model_status.last_response.model,persisted.model_status.configured);
  assert.equal(persisted.agent.episode_count, initial.agent.episode_count + 1);
  assert.equal(persisted.event_chain_valid, true);
  assert.equal(persisted.runtime.daily_calls, 1);
});

test('stream endpoint exposes tokens and persistence phases in order',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='test-access-token';
  process.env.DEEPSEEK_API_KEY='test-provider-key';
  const store=new MemoryStore();
  const completionProvider=async(_messages,options={})=>{
    await options.onPhase?.({status:'connected',requested_model:'mock-request'});
    for(const chunk of [modelReply.text.slice(0,31),modelReply.text.slice(31,117),modelReply.text.slice(117)])await options.onDelta?.(chunk);
    return modelReply;
  };
  const handler=createHandler({storeFactory:()=>store,completionProvider});
  const response=await handler(request('/api/mind/stream','POST',{kind:'chat',request_id:'stream-one',person_id:'oli',person_name:'Oli',message:'Show the live transition'}));
  assert.equal(response.status,200);assert.match(response.headers.get('content-type'),/ndjson/);
  const events=(await response.text()).trim().split('\n').map(JSON.parse);
  assert.equal(events[0].event,'accepted');
  assert.equal(events.filter(x=>x.event==='token').map(x=>x.text).join(''),modelReply.text);
  const phases=events.filter(x=>x.event==='phase').map(x=>x.phase);
  for(const phase of ['queued','reserved','context','provider','first_token','validating','state_ready','committing','committed'])assert.ok(phases.includes(phase),phase);
  assert.ok(phases.indexOf('context')<phases.indexOf('first_token'));
  assert.ok(phases.indexOf('state_ready')<phases.indexOf('committed'));
  assert.equal(events.at(-1).event,'complete');assert.equal(events.at(-1).result.state_version,12);
  assert.equal(store.data.state_version,12);assert.equal(store.data.cognition_lease,null);
});

test('DeepSeek SSE reader reassembles split events and usage',async()=>{
  const encoder=new TextEncoder();
  const chunks=['data: {"id":"r1","model":"deepseek-flash","choices":[{"delta":{"content":"{\\"reply\\":\\"Hel"},"finish_reason":null}]}\n\n','data: {"id":"r1","model":"deepseek-flash","choices":[{"delta":{"content":"lo\\"}"},"finish_reason":"stop"}]}\n\n','data: {"id":"r1","model":"deepseek-flash","choices":[],"usage":{"total_tokens":9}}\n\ndata: [DONE]\n\n'];
  const body=new ReadableStream({start(controller){for(const chunk of chunks)controller.enqueue(encoder.encode(chunk));controller.close();}}),seen=[];
  const result=await readDeepSeekStream(new Response(body),'deepseek-chat',{onDelta:text=>seen.push(text)});
  assert.equal(result.text,'{"reply":"Hello"}');assert.deepEqual(seen,['{"reply":"Hel','lo"}']);assert.equal(result.model,'deepseek-flash');assert.equal(result.finish_reason,'stop');assert.equal(result.usage.total_tokens,9);
});

test("concurrent stale write is refused", async () => {
  process.env.SOVEREIGNTY_ACCESS_TOKEN = "test-access-token";
  process.env.DEEPSEEK_API_KEY = "test-provider-key";
  const store = new MemoryStore();
  const handler = createHandler({ storeFactory: () => store, completionProvider: async () => {
    store.etag = "changed-by-another-request";
    return modelReply;
  } });
  await handler(request("/api/snapshot"));
  const response = await handler(request("/api/chat", "POST", { message: "Race the state" }));
  assert.equal(response.status, 409);
});

test("malformed provider output is preserved as a failed immutable event", async () => {
  process.env.SOVEREIGNTY_ACCESS_TOKEN = "test-access-token";
  process.env.DEEPSEEK_API_KEY = "test-provider-key";
  const store = new MemoryStore();
  const malformed = { ...modelReply, text: '{"reply":"truncated",', finish_reason: "length" };
  const handler = createHandler({ storeFactory: () => store, completionProvider: async () => malformed });

  await handler(request("/api/snapshot"));
  const response = await handler(request("/api/think", "POST", { mode: "associative_reverie" }));
  assert.equal(response.status, 500);
  assert.equal(store.data.state_version, 11);
  assert.equal(store.data.usage.calls, 1);
  const event = store.data.deployed_events.at(-1);
  assert.equal(event.event_type, "associative_reverie_failed");
  assert.equal(event.payload.raw_response, malformed.text);
  assert.equal(event.payload.provider.finish_reason, "length");
  assert.equal(event.payload.state_changed, false);
  assert.match(event.payload.parse_error, /JSON|completion/i);
});

test('V9 build supports older persisted state but cannot bypass the V12 adoption gate',async()=>{
 process.env.SOVEREIGNTY_ACCESS_TOKEN='test-access-token';const store=new MemoryStore();
 const handler=createHandler({storeFactory:()=>store,completionProvider:async()=>modelReply});
 const choices=[{salience:1,need:1,affect:1,repeats:1},{salience:.4,need:.6,affect:.4,repeats:0}];
 const response=await handler(request('/api/evolution/build','POST',{thesis:'Test older seed migration',program:{op:'sub',args:[{op:'add',args:['salience','need']},{op:'mul',args:[2,'repeats']}]},tests:[{choices,expected:1},{choices:choices.map(x=>({...x,repeats:0})),expected:0}]}));
 assert.equal(response.status,200);const pkg=await response.json();
 const deployed=await handler(request('/api/evolution/deploy','POST',{id:pkg.content.id}));assert.equal(deployed.status,422);assert.match((await deployed.json()).error,/V12 adoption is held/);
});

test('broken provider stream retains received content and records transport failure',async()=>{
 let n=0;const bytes=new TextEncoder();
 const response=new Response(new ReadableStream({pull(c){if(n++===0)c.enqueue(bytes.encode('data: '+JSON.stringify({model:'fixture',choices:[{delta:{content:'{"reply":"Complete prose.",'}}]})+'\n\n'));else c.error(new Error('connection lost'));}}));
 const result=await readDeepSeekStream(response,'fixture',{onDelta:()=>{}});
 assert.equal(result.text,'{"reply":"Complete prose.",');assert.equal(result.stream_complete,false);assert.match(result.transport_error,/connection lost/);
});
