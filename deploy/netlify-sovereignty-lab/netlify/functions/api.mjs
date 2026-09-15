import {createEvolution} from './lib/evolution9.mjs';
import {createDevelopment} from './lib/development12.mjs';
import {createPromotion} from './lib/promotion12.mjs';
import { timingSafeEqual } from "node:crypto";
import { getStore } from "@netlify/blobs";
import seed from "./lib/seed.mjs";
import { createIndependence, RELEASE } from "./lib/independence.mjs";
import { createWorkbench } from "./lib/workbench.mjs";
import { createMindRuntime } from "./lib/mind-runtime.mjs";
import {createLivingInquiry} from './lib/living-inquiry13.mjs';
import { ensureMind, MIND_VERSION } from "./lib/mind.mjs";
import {autonomyStatus,recoverAutonomy} from './lib/autonomy-control.mjs';
import {
  MODES, appendEvent, applyCompletion, initialiseRecord, parseCompletion,
  ensureSovereigntyConstitution, sha256, snapshot, systemPrompt, userPrompt,
} from "./lib/core.mjs";

const STATE_KEY = "agent/godelos-sovereign-01/state";
const STORE = "godelos-sovereignty";

function json(value, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}

export function authorised(request) {
  const expected = process.env.SOVEREIGNTY_ACCESS_TOKEN || "";
  const header = request.headers.get("authorization") || "";
  const provided = header.startsWith("Bearer ") ? header.slice(7) : "";
  if (!expected || !provided) return false;
  const left = Buffer.from(expected);
  const right = Buffer.from(provided);
  return left.length === right.length && timingSafeEqual(left, right);
}

async function body(request) {
  const length = Number(request.headers.get("content-length") || 0);
  if (length > 32_000) throw new Error("request body exceeds 32 KB");
  const value = await request.json();
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("JSON object required");
  return value;
}

async function loadRecord(store) {
  let entry = await store.getWithMetadata(STATE_KEY, { type: "json" });
  if (!entry) {
    await store.setJSON(STATE_KEY, initialiseRecord(seed), { onlyIfNew: true });
    entry = await store.getWithMetadata(STATE_KEY, { type: "json" });
  }
  if (!entry?.data) throw new Error("persistent state could not be initialised");
  if (ensureSovereigntyConstitution(entry.data)) {
    appendEvent(entry.data, "constitutional_goal_installed", {
      goal_version: "1.0",
      provenance: "operator-authorised source migration",
      result_version: entry.data.state_version,
    });
    const migrated = await store.setJSON(STATE_KEY, entry.data, { onlyIfMatch: entry.etag });
    if (migrated.modified) entry = await store.getWithMetadata(STATE_KEY, { type: "json" });
    else entry = await store.getWithMetadata(STATE_KEY, { type: "json" });
  }
  return { record: entry.data, etag: entry.etag };
}

async function saveRecord(store, record, etag) {
  const result = await store.setJSON(STATE_KEY, record, { onlyIfMatch: etag });
  if (!result.modified) {
    const error = new Error("state changed during this inference; retry the request");
    error.status = 409;
    throw error;
  }
}

function enforceCallLimit(record) {
  const day = new Date().toISOString().slice(0, 10);
  if (record.usage?.day !== day) record.usage = { day, calls: 0 };
  const limit = Math.max(1, Number(process.env.SOVEREIGNTY_DAILY_CALL_LIMIT || 250));
  if (record.usage.calls >= limit) {
    const error = new Error(`daily model-call limit reached (${limit})`);
    error.status = 429;
    throw error;
  }
}

function providerBody(model,messages,stream=false) {
  return {
    model,
    messages,
    temperature:Number(process.env.DEEPSEEK_TEMPERATURE||0.75),
    max_tokens:Number(process.env.DEEPSEEK_MAX_TOKENS||3500),
    response_format:{type:'json_object'},
    thinking:{type:'disabled'},
    ...(stream?{stream:true,stream_options:{include_usage:true}}:{}),
  };
}

export async function readDeepSeekStream(response,model,options) {
  if(!response.body)throw new Error('DeepSeek streaming response lacked a body');
  const reader=response.body.getReader(),decoder=new TextDecoder();
  let pending='',text='',responseId=null,actualModel=null,finishReason=null,usage={};
  const consume=async line=>{
    const value=line.trim();if(!value.startsWith('data:'))return;
    const data=value.slice(5).trim();if(!data||data==='[DONE]')return;
    let payload;try{payload=JSON.parse(data);}catch{throw new Error('DeepSeek returned a malformed streaming event');}
    responseId=payload.id||responseId;actualModel=payload.model||actualModel;usage=payload.usage||usage;
    const choice=payload.choices?.[0],delta=choice?.delta?.content;
    if(choice?.finish_reason)finishReason=choice.finish_reason;
    if(typeof delta==='string'&&delta){text+=delta;await options.onDelta(delta);}
  };
  let transportError=null;
  try{while(true){
    const {done,value}=await reader.read();pending+=decoder.decode(value||new Uint8Array(),{stream:!done});
    const lines=pending.split(/\r?\n/);pending=lines.pop()||'';
    for(const line of lines)await consume(line);
    if(done)break;
  }
  if(pending.trim())await consume(pending);
  }catch(error){transportError=String(error.message||error);}finally{reader.releaseLock();}
  if(!text)throw new Error('DeepSeek response lacked completion content');
  return {text,model:actualModel,requested_model:model,response_id:responseId,finish_reason:finishReason,usage,...(transportError?{transport_error:transportError}:{}),stream_complete:!transportError&&!!finishReason};
}

export async function deepSeek(messages,options={}) {
  const apiKey = process.env.DEEPSEEK_API_KEY;
  if (!apiKey) {
    const error = new Error("DEEPSEEK_API_KEY is not configured for Functions");
    error.status = 503;
    throw error;
  }
  const endpoint = process.env.DEEPSEEK_API_BASE || "https://api.deepseek.com/chat/completions";
  const model = process.env.DEEPSEEK_MODEL || "deepseek-flash";
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { authorization: `Bearer ${apiKey}`, "content-type": "application/json" },
    body:JSON.stringify(providerBody(model,messages,typeof options.onDelta==='function')),
    signal: AbortSignal.timeout(55_000),
  });
  if (!response.ok) {
    const error = new Error(`DeepSeek returned HTTP ${response.status}`);
    error.status = 502;
    throw error;
  }
  if(typeof options.onDelta==='function'){
    await options.onPhase?.({status:'connected',requested_model:model});
    return readDeepSeekStream(response,model,options);
  }
  const payload = await response.json();
  const choice = payload.choices?.[0];
  if (typeof choice?.message?.content !== "string") throw new Error("DeepSeek response lacked completion content");
  return {
    text: choice.message.content,
    model: payload.model || null,
    requested_model:model,
    response_id: payload.id || null,
    finish_reason: choice.finish_reason || null,
    usage: payload.usage || {},
  };
}

function ndjson(work) {
  const encoder=new TextEncoder();let cancelled=false;
  const stream=new ReadableStream({
    start(controller){
      const emit=(event,detail={})=>{if(cancelled)return;try{controller.enqueue(encoder.encode(JSON.stringify({event,at:Date.now(),...detail})+'\n'));}catch{cancelled=true;}};
      Promise.resolve().then(()=>work(emit)).then(result=>emit('complete',{result})).catch(error=>emit('error',{message:String(error?.message||error),status:Number(error?.status||500)})).finally(()=>{if(!cancelled)controller.close();});
    },
    cancel(){cancelled=true;},
  });
  return new Response(stream,{headers:{'content-type':'application/x-ndjson; charset=utf-8','cache-control':'no-store, no-transform','x-content-type-options':'nosniff','x-accel-buffering':'no'}});
}

async function cognition(store, record, etag, payload, mode, completionProvider = deepSeek) {
  if (record.cognition_lease) throw Object.assign(new Error('An integrated cognition cycle is in progress'), {status:409});
  if (!MODES.has(mode)) {
    const error = new Error(`invalid cognition mode: ${mode}`);
    error.status = 422;
    throw error;
  }
  enforceCallLimit(record);
  const personId = mode === "dialogue" ? String(payload.person_id || "web-user").slice(0, 100) : null;
  const personName = mode === "dialogue" ? String(payload.person_name || "Human").slice(0, 80) : null;
  const prompt = userPrompt(record.state, mode, payload);
  const completion = await completionProvider([
    { role: "system", content: systemPrompt(record.state, mode, personId) },
    { role: "user", content: prompt },
  ]);
  record.last_completion={model:completion.model||null,response_id:completion.response_id||null,recorded_at:new Date().toISOString()};
  let parsed;
  try {
    parsed = parseCompletion(completion.text, mode);
  } catch (error) {
    record.usage.calls += 1;
    appendEvent(record, `${mode}_failed`, {
      prompt,
      user_message: mode === "dialogue" ? String(payload.message || "").slice(0, 12000) : null,
      raw_response: completion.text,
      raw_response_sha256: completion.text ? sha256(completion.text) : null,
      parse_error: String(error?.message || error),
      provider: {
        model: completion.model,
        response_id: completion.response_id,
        finish_reason: completion.finish_reason,
        usage: completion.usage,
      },
      result_version: record.state_version,
      state_changed: false,
    });
    await saveRecord(store, record, etag);
    throw error;
  }
  record.state = applyCompletion(record.state, parsed, { mode, personId, personName });
  record.state_version = Number(record.state_version || 0) + 1;
  record.usage.calls += 1;
  appendEvent(record, mode, {
    prompt,
    user_message: mode === "dialogue" ? String(payload.message).slice(0, 12000) : null,
    raw_response: completion.text,
    raw_response_sha256: completion.text ? sha256(completion.text) : null,
    parsed_response: parsed,
    provider: {
      model: completion.model,
      response_id: completion.response_id,
      finish_reason: completion.finish_reason,
      usage: completion.usage,
    },
    result_version: record.state_version,
  });
  await saveRecord(store, record, etag);
  return {
    agent_id: record.state.agent_id,
    agent_name: record.state.name,
    reply: parsed.reply,
    cognitive_mode: parsed.cognitive_mode,
    initiative: parsed.initiative || {},
    state_version: record.state_version,
    episode_count: record.state.episode_count,
    model: completion.model,
  };
}

export function createHandler(dependencies = {}) {
  const storeFactory = dependencies.storeFactory || getStore;
  const completionProvider = dependencies.completionProvider || deepSeek;
  return async function handler(request) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/\.netlify\/functions\/api/, "/api");
    if (request.method === "GET" && path === "/api/health") {
      return json({
        ok: true,
        release: {research:RELEASE,mind:MIND_VERSION,runtime:'13.0.0-alpha.1'},
        access_token_configured: Boolean(process.env.SOVEREIGNTY_ACCESS_TOKEN),
        provider_configured: Boolean(process.env.DEEPSEEK_API_KEY),
        persistence: "netlify-blobs",
      });
    }
    if (!process.env.SOVEREIGNTY_ACCESS_TOKEN) return json({ error: "SOVEREIGNTY_ACCESS_TOKEN is not configured" }, 503);
    if (!authorised(request)) return json({ error: "Access token required" }, 401);

    try {
      const store = storeFactory({ name: STORE, consistency: "strong" });
      const mind = createMindRuntime({store,load:()=>loadRecord(store),save:(record,etag)=>saveRecord(store,record,etag),complete:completionProvider});
      const living=createLivingInquiry({store,load:()=>loadRecord(store),save:(r,e)=>saveRecord(store,r,e),complete:completionProvider});
      if(path==='/api/living/tick'&&request.method==='POST'){
        const payload=await body(request),current=await loadRecord(store);
        if(current.record.inbox?.some(x=>x.status==='queued'))return json(await mind.drain());
        const result=await living.advance();
        return json(result.idle?await mind.cycle(payload):result);
      }
      if(path.startsWith('/api/living/evidence/')&&request.method==='GET')return json(await living.evidence(path.split('/').at(-1)));
      if(path==='/api/mind/stream'&&request.method==='POST'){
        const payload=await body(request),kind=payload.kind;
        if(!['chat','cycle'].includes(kind))return json({error:'kind must be chat or cycle'},422);
        return ndjson(async emit=>{
          emit('accepted',{request_id:payload.request_id||null,kind});
          const hooks={onProgress:event=>emit('phase',event),onDelta:text=>emit('token',{text})};
          return kind==='chat'?mind.submit(payload,hooks):mind.cycle(payload,false,hooks);
        });
      }
      if(path.startsWith('/api/promotion/')&&['GET','POST'].includes(request.method)){
        const controller=createPromotion({store,load:()=>loadRecord(store),save:(r,e)=>saveRecord(store,r,e)}),action=path.split('/').at(-1);
        if(request.method==='GET'&&action==='status')return json(await controller.status());
        if(request.method==='POST'&&['review','canary','monitor'].includes(action)){
          const payload=await body(request);try{return json(await controller[action](payload.id));}catch(e){return json({error:e.message},422);}
        }
        return json({error:'Unknown promotion action'},404);
      }
      if(path.startsWith('/api/development/')&&['GET','POST'].includes(request.method)){
        const evolution=createEvolution({store,load:async()=>{const x=await loadRecord(store);ensureMind(x.record.state);return x;},save:(r,e)=>saveRecord(store,r,e),complete:completionProvider});
        const development=createDevelopment({store,evolution}),action=path.split('/').at(-1);
        if(request.method==='GET')return ['status','evidence'].includes(action)?json(await development[action]()):json({error:'Unknown development read'},404);
        const payload=await body(request);
        if(!['start','pause','resume','advance'].includes(action))return json({error:'Unknown development action'},404);
        try{return json(await development[action](payload));}catch(e){return json({error:e.message},422);}
      }
      if(path.startsWith('/api/evolution/')&&['GET','POST'].includes(request.method)){
        const evolution=createEvolution({store,load:async()=>{const x=await loadRecord(store);ensureMind(x.record.state);return x;},save:(r,e)=>saveRecord(store,r,e),complete:completionProvider});const action=path.split('/').at(-1),payload=request.method==='POST'?await body(request):{};
        if(request.method==='GET')return action==='latest'?json(await evolution.latest()):json({error:'Unknown evolution read'},404);
        const evolutionResult=async fn=>{try{return json(await fn());}catch(e){return json({error:String(e.message||'Evolution action failed')},422);}};
        if(action==='propose')return await evolutionResult(()=>evolution.propose());
        if(action==='build')return await evolutionResult(()=>evolution.build(payload));
        if(action==='deploy')return await evolutionResult(()=>evolution.deploy(payload.id));
        if(action==='rollback')return await evolutionResult(()=>evolution.rollback());
        return json({error:'Unknown evolution action'},404);
      }
      if (path === '/api/mind/cycle' && request.method === 'POST') return json(await mind.cycle(await body(request)));
      if (path === '/api/mind/attention' && request.method === 'POST') return json(await mind.attention());
      if (path === '/api/mind/intention/evidence' && request.method === 'POST') return json(await mind.intentionEvidence(await body(request)));
      if (path === '/api/mind/intention/verify' && request.method === 'POST') return json(await mind.intentionVerification(await body(request)));
      if (path === '/api/mind/inbox/advance' && request.method === 'POST') return json(await mind.drain());
      if (path === '/api/mind/control' && request.method === 'POST') return json(await mind.control((await body(request)).paused));
      if (path === '/api/mind/recover' && request.method === 'POST') return json(await mind.recover((await body(request)).request_id));
      if(path==='/api/mind/autonomy/recover'&&request.method==='POST'){const {record}=await loadRecord(store);if(record.cognition_lease)return json({error:'Recover the expired thought cycle first.'},409);return json(await recoverAutonomy(store,(await body(request)).nonce));}
      if (path === '/api/mind/history' && request.method === 'GET') return json(await mind.history());
      if (path.startsWith('/api/mind/evidence/') && request.method === 'GET') return json(await mind.evidence(path.split('/').at(-1)));
      if (path === '/api/chat' && request.method === 'POST') return json(await mind.submit(await body(request)));
      if (path.startsWith('/api/independence')) {
        const engine = createIndependence({store, complete: completionProvider});
        const [id, action] = path.replace(/^\/api\/independence\/?/, '').split('/');
        if (request.method === 'GET' && !id) return json({campaigns:await engine.list(),worker:(await store.getWithMetadata('independence/v6/worker',{type:'json'}))?.data||null,release:RELEASE});
        if (request.method === 'POST' && !id) return json(await engine.create(await body(request)),201);
        if (request.method === 'GET' && id) return json(action==='export'?await engine.export(id):await engine.get(id));
        if (request.method === 'POST' && ['advance','pause','resume'].includes(action)) {
          const payload=await body(request);
          return json(action==='advance'?await engine.advance(id,payload.expected_revision):await engine[action](id));
        }
        return json({error:'Independence route not found'},404);
      }
      if (path.startsWith('/api/forge/')) {
        const workbench = createWorkbench({store, complete: completionProvider});
        const parts = path.slice('/api/forge/'.length).split('/');
        const [collection, id, action, runId] = parts;
        const campaign = collection === 'campaigns';
        if (!['jobs', 'campaigns'].includes(collection)) return json({error:'Research route not found'},404);
        if (request.method === 'GET' && !id) return json(await (campaign ? workbench.listCampaigns() : workbench.list()));
        if (request.method === 'POST' && !id) return json(await (campaign ? workbench.createCampaign(await body(request)) : workbench.create(await body(request))),201);
        if (request.method === 'GET' && id && !action) return json(await (campaign ? workbench.getCampaign(id) : workbench.get(id)));
        if (request.method === 'GET' && action === 'export') return json(await (campaign ? workbench.exportCampaign(id) : workbench.export(id)));
        if (!campaign && request.method === 'GET' && action === 'raw') return json(await workbench.raw(id,runId));
        if (request.method === 'POST' && ['advance','pause','resume','review'].includes(action)) {
          const payload = await body(request);
          if (action === 'advance') return json(await (campaign ? workbench.advanceCampaign(id,payload.expected_revision) : workbench.advance(id,payload.expected_cursor)));
          if (action === 'pause') return json(await (campaign ? workbench.pauseCampaign(id) : workbench.pause(id)));
          if (action === 'resume') return json(await (campaign ? workbench.resumeCampaign(id) : workbench.resume(id)));
          if (!campaign) return json(await workbench.review(id,payload.question));
        }
        return json({error:'Research route not found'},404);
      }
      const { record, etag } = await loadRecord(store);
      if (request.method === "GET" && path === "/api/snapshot") {
        ensureMind(record.state);
        const result=snapshot(record, Boolean(process.env.DEEPSEEK_API_KEY));
        result.model_status={configured:process.env.DEEPSEEK_MODEL||"deepseek-flash",last_response:record.last_completion||null};
        result.mind_control=await mind.settings();
        result.cognition_lease=record.cognition_lease||null;
        result.inbox=(record.inbox||[]).map(({request_id,message,status,submitted_at})=>({request_id,message,status,submitted_at}));
        result.autonomy=await autonomyStatus(store,record);
        return json(result);
      }
      if (request.method === "POST" && path === "/api/chat") {
        const payload = await body(request);
        return json(await cognition(store, record, etag, payload, "dialogue", completionProvider));
      }
      if (request.method === "POST" && path === "/api/think") {
        const payload = await body(request);
        return json(await cognition(store, record, etag, payload, String(payload.mode || "deliberation"), completionProvider));
      }
      if (request.method === "POST" && path === "/api/value-profile") {
        const payload = await body(request);
        const values = payload.values;
        if (!values || typeof values !== "object" || Array.isArray(values)) throw new Error("values object required");
        const active = record.state.self_model?.active_values || {};
        if (Object.keys(active).some((key) => !Number.isFinite(Number(values[key])))) throw new Error("every active value requires a numeric candidate value");
        const profile = {
          profile_id: `manual-profile-${crypto.randomUUID()}`,
          name: String(payload.name || "UI candidate").slice(0, 100),
          values: Object.fromEntries(Object.keys(active).map((key) => [key, Math.max(0, Math.min(1, Number(values[key])))])),
          rationale: String(payload.rationale || "Manual value-lab candidate").slice(0, 1000),
          parent_profile_id: record.experiment?.active_profile_id || "parent-balanced-v1",
          immutable: true,
          created_at: new Date().toISOString(),
        };
        record.evolution_objects.push({
          object_id: profile.profile_id, object_type: "manual_value_candidate",
          payload: profile, created_at: profile.created_at,
        });
        appendEvent(record, "manual_value_candidate", { profile_id: profile.profile_id, parent_profile_id: profile.parent_profile_id });
        await saveRecord(store, record, etag);
        return json({ profile, constraint_violations: [], saved: true }, 201);
      }
      return json({ error: "not found" }, 404);
    } catch (error) {
      console.error("sovereignty function error", error);
      const status = Number(error.status || (error instanceof SyntaxError ? 422 : 500));
      const safe = status < 500 || status === 503 ? error.message : "The sovereignty function failed. Inspect the Netlify function log.";
      return json({ error: safe }, status);
    }
  };
}

export default createHandler();
