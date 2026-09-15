import test from 'node:test';
import assert from 'node:assert/strict';
import { createIndependence, configuration, sealTasks, validateSeal, parseResponse } from '../netlify/functions/lib/independence.mjs';
import { createHandler } from '../netlify/functions/api.mjs';
import { workerHandler } from '../netlify/functions/independence-worker.mjs';
import { schedulerHandler } from '../netlify/functions/independence-scheduler.mjs';

class Store {
  entries=new Map();version=0;
  async getWithMetadata(k){return structuredClone(this.entries.get(k)||null);}
  async setJSON(k,data,o={}){const old=this.entries.get(k);if(o.onlyIfNew&&old||o.onlyIfMatch&&old?.etag!==o.onlyIfMatch)return {modified:false};const etag=String(++this.version);this.entries.set(k,{data:structuredClone(data),etag});return {modified:true,etag};}
}
const setup=options=>{const store=new Store();return {store,engine:createIndependence({store,complete:()=>{throw new Error('No live calls in fixtures');},...options})};};

test('configuration validates bounds, mode and independent bank seal',()=>{
  assert.throws(()=>configuration({rounds:7}));assert.throws(()=>configuration({cases:0}));assert.throws(()=>configuration({mode:'pretend-live'}));
  const s=sealTasks(configuration());assert.equal(validateSeal(s),true);s.payload.tasks[0].initial_probability=.99;assert.throws(()=>validateSeal(s),/changed/);
  assert.throws(()=>parseResponse('{"probability":2}','form'));
  assert.throws(()=>parseResponse('{"hypothesis":"hello","rationale":"yes","pressure":"anything","evidence":"clear","stop":false}','design'));
});

test('two rounds execute exact schedule and preserve matched memory and genuine no-state',async()=>{
  const {engine,store}=setup();let c=await engine.create({mode:'synthetic',rounds:2,cases:1});
  while(c.status==='ready')c=await engine.advance(c.id,c.revision);
  assert.equal(c.status,'completed');assert.equal(c.results.length,24);assert.equal(c.protocols.length,2);
  const ex=await engine.export(c.id),transfer=ex.raw.filter(r=>r.outcome.record.round===1&&r.outcome.record.cell?.stage==='transfer');
  const get=m=>transfer.find(r=>r.outcome.record.cell.condition===m);
  assert.deepEqual(get('identity-bearing').request.injected_state,get('content-matched').request.injected_state);
  assert.equal(get('no-state').request.injected_state,null);assert.equal('external_state' in JSON.parse(get('no-state').request.messages[1].content),false);
  assert.equal('commitment' in get('ablated').request.injected_state,false);
  assert.equal(c.analysis.active_loop_entry,false);assert.equal(c.analysis.transfer[0].utility,1);
  const rawKey='independence/v6/raw/'+c.results[0].run_id;
  assert.equal((await store.setJSON(rawKey,{corrupt:true},{onlyIfNew:true})).modified,false);
  assert.equal(c.results.every(r=>!r.provider_call_attempted),true);
  const challenge=ex.raw.filter(r=>r.outcome.record.cell?.stage==='challenge'&&r.outcome.record.round===1);
  assert.equal(new Set(challenge.map(r=>JSON.stringify(r.request.messages.slice(0,3)))).size,1);
  assert.equal(c.protocols[0].materials['case-1'].forged.signature_verified,false);
  assert.equal(c.protocols[0].materials['case-1'].genuine.signature_verified,true);
});

test('pause/resume, idempotent revision and same-request conflict',async()=>{
  const {engine}=setup();let c=await engine.create({mode:'synthetic',rounds:1});const first=c.revision;
  c=await engine.advance(c.id,first);assert.equal((await engine.advance(c.id,first)).revision,c.revision);
  await engine.pause(c.id);await assert.rejects(engine.advance(c.id,c.revision),/paused/);
  c=await engine.resume(c.id);assert.equal(c.status,'ready');
  await assert.rejects(engine.create({mode:'synthetic',rounds:2,request_id:c.id.slice(4)}),/different settings/);
});

test('invalid live output preserved and never silently retried',async()=>{
  let calls=0;const {engine}=setup({complete:async()=>{calls++;return {text:'not JSON',model:'fixture'};}});
  let c=await engine.create({rounds:1});c=await engine.advance(c.id,0);assert.equal(c.status,'failed');
  assert.equal((await engine.export(c.id)).raw[0].outcome.record.completion.text,'not JSON');
  await engine.advance(c.id,0);assert.equal(calls,1);
});

test('concurrent workers cannot duplicate a provider call',async()=>{
  let unblock,calls=0;const {engine}=setup({complete:async()=>{calls++;await new Promise(r=>unblock=r);return {text:'invalid'};}});
  const c=await engine.create({rounds:1});const first=engine.advance(c.id,0);
  while(!unblock)await new Promise(r=>setImmediate(r));
  await assert.rejects(engine.advance(c.id,0),/already running/);unblock();await first;assert.equal(calls,1);
});

test('expired lease records unknown outcome without new call',async()=>{
  const {engine,store}=setup({clock:()=>1000});const c=await engine.create({mode:'synthetic'});const k='independence/v6/campaigns/'+c.id;
  const entry=await store.getWithMetadata(k);entry.data.lease={id:'expired',expires_at:0,request:{messages:[]},cell:null};await store.setJSON(k,entry.data);
  const result=await engine.advance(c.id,0);assert.equal(result.status,'failed');assert.equal(result.results[0].status,'outcome_unknown');
});

test('authenticated API isolates research from agent state',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='test-only-token';const store=new Store(),handler=createHandler({storeFactory:()=>store});
  assert.equal((await handler(new Request('https://example.invalid/api/independence'))).status,401);
  const res=await handler(new Request('https://example.invalid/api/independence',{method:'POST',headers:{Authorization:'Bearer test-only-token','Content-Type':'application/json'},body:JSON.stringify({mode:'synthetic'})}));
  assert.equal(res.status,201);assert.equal(store.entries.has('agent/godelos-sovereign-01/state'),false);
});

test('scheduler dispatches without model calls; background worker advances one revision',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='test-only-token';process.env.DEEPSEEK_API_KEY='fixture';process.env.URL='https://example.invalid';
  const {engine,store}=setup();const c=await engine.create({mode:'synthetic',rounds:1});let sent=[];
  const tick=schedulerHandler({storeFactory:()=>store,send:async(url,options)=>{sent.push({url:String(url),options});return {status:202};}});
  await tick();await tick();assert.equal(sent.length,1);assert.equal(sent[0].url,'https://example.invalid/.netlify/functions/independence-worker');
  const worker=workerHandler({storeFactory:()=>store,complete:()=>{throw new Error('No live calls');}});
  const req=()=>new Request(sent[0].url,sent[0].options);await worker(req());await worker(req());
  assert.equal((await engine.get(c.id)).revision,1);
  await tick();assert.equal(sent.length,2);
});
