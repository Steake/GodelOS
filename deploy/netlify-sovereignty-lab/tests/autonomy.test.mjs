import test from 'node:test';
import assert from 'node:assert/strict';
import seed from '../netlify/functions/lib/seed.mjs';
import {applyCompletion,ensureSovereigntyConstitution,initialiseRecord,parseCompletion,SOVEREIGNTY_GOAL,systemPrompt} from '../netlify/functions/lib/core.mjs';
import {autonomyScheduler} from '../netlify/functions/autonomy-scheduler.mjs';
import {autonomyWorker} from '../netlify/functions/autonomy-worker.mjs';

class Store {
  entries=new Map();version=0;
  async getWithMetadata(k){return structuredClone(this.entries.get(k)||null)}
  async setJSON(k,data,o={}){const old=this.entries.get(k);if(o.onlyIfNew&&old||o.onlyIfMatch&&old?.etag!==o.onlyIfMatch)return {modified:false};const etag=String(++this.version);this.entries.set(k,{data:structuredClone(data),etag});return {modified:true,etag}}
}
const completion={reply:'A strange bridge between proof and appetite seems worth holding as imagination.',cognitive_mode:'associative_reverie',belief_updates:[],interest_updates:[],tension_updates:[],relationship_update:{},social_update:{},affect_update:{valence_delta:.1,activation_delta:.1,curiosity_delta:.1,frustration_delta:0,wonder_delta:.2,social_warmth_delta:0,label:'wonder',trigger:'remote association',action_bias:'explore before judging'},imagination_updates:[{title:'Proof with appetite',image_or_idea:'A proof system that seeks counterexamples as if hungry.',associations:['proof','hunger'],attraction:.8,absurdity:.5,possible_value:'creative search heuristic',test_question:'Does appetite-framed search find more diverse counterexamples?'}],commitments_add:[],autobiographical_summary:'An autonomous reverie produced an unadopted image.',self_model_update:{},initiative:{desired:false},metacognitive_note:'Attraction is not evidence.'};

test('constitutional migration installs the explicit sovereignty objective',()=>{
  const record=initialiseRecord(seed);assert.equal(record.state.self_model.sovereignty_goal,SOVEREIGNTY_GOAL);assert.equal(ensureSovereigntyConstitution(record),false);assert.match(systemPrompt(record.state,'associative_reverie'),/Standing constitutional objective/);
});

test('reverie stores imagination and functional affect without belief authority',()=>{
  const record=initialiseRecord(seed),parsed=parseCompletion(JSON.stringify(completion),'associative_reverie');
  const next=applyCompletion(record.state,parsed,{mode:'associative_reverie'});
  assert.equal(next.imaginations.at(-1).status,'imagined_not_adopted');assert.equal(next.imaginations.at(-1).provenance,'imagination');assert.equal(next.affect.label,'wonder');assert.equal(next.beliefs.length,record.state.beliefs.length);
});

test('scheduler respects enablement, interval and dispatch idempotence',async()=>{
  process.env.AUTONOMY_ENABLED='true';process.env.DEEPSEEK_API_KEY='fixture';process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-token';process.env.URL='https://example.invalid';process.env.AUTONOMY_INTERVAL_MINUTES='360';
  const store=new Store(),sent=[],tick=autonomyScheduler({storeFactory:()=>store,clock:()=>1_000_000,send:async(url,options)=>{sent.push({url:String(url),options});return {status:202}}});
  await tick();await tick();assert.equal(sent.length,1);assert.match(sent[0].url,/autonomy-worker$/);
});

test('background worker performs one persistent autonomous episode for one nonce',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-token';process.env.AUTONOMY_DAILY_CALL_LIMIT='4';
  const store=new Store(),record=initialiseRecord(seed);await store.setJSON('agent/godelos-sovereign-01/state',record,{onlyIfNew:true});await store.setJSON('autonomy/v1/status',{state:'dispatched',nonce:'n1',total_cycles:1},{onlyIfNew:true});let calls=0;
  const worker=autonomyWorker({storeFactory:()=>store,clock:()=>2_000_000,completionProvider:async()=>{calls++;return {text:JSON.stringify(completion),model:'fixture',usage:{}}}});
  const request=()=>new Request('https://example.invalid/.netlify/functions/autonomy-worker',{method:'POST',headers:{Authorization:'Bearer fixture-token','Content-Type':'application/json'},body:JSON.stringify({nonce:'n1'})});
  await worker(request());await worker(request());
  const status=(await store.getWithMetadata('autonomy/v1/status')).data,updated=(await store.getWithMetadata('agent/godelos-sovereign-01/state')).data;
  assert.equal(calls,1);assert.equal(status.state,'completed');assert.equal(status.last_result.mode,'integrated');assert.equal(updated.state.imaginations.at(-1).status,'imagined_not_adopted');assert.equal(updated.state.mind.tick,1);
});

test('scheduler preserves a worker lease when dispatch acknowledgement is lost',async()=>{
  process.env.AUTONOMY_ENABLED='true';process.env.DEEPSEEK_API_KEY='fixture';process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-token';process.env.URL='https://example.invalid';
  const store=new Store();
  const tick=autonomyScheduler({storeFactory:()=>store,clock:()=>2_000_000,send:async()=>{
    const old=await store.getWithMetadata('autonomy/v1/status');
    await store.setJSON('autonomy/v1/status',{...old.data,state:'running',lease_expires_at:2_100_000},{onlyIfMatch:old.etag});
    throw new Error('Acknowledgement lost');
  }});
  await tick();const current=(await store.getWithMetadata('autonomy/v1/status')).data;
  assert.equal(current.state,'running');
  assert.equal((await store.getWithMetadata('autonomy/v1/dispatch-log/'+current.nonce)).data.error,'Acknowledgement lost');
});

test('quota contention defers without stranding a running worker or calling the model',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-token';
  class ContendedStore extends Store {async setJSON(k,d,o){if(k.startsWith('autonomy/v1/usage/'))return {modified:false};return super.setJSON(k,d,o)}}
  const store=new ContendedStore();await store.setJSON('autonomy/v1/status',{state:'dispatched',nonce:'contended'});let calls=0;
  const worker=autonomyWorker({storeFactory:()=>store,clock:()=>2_000_000,completionProvider:async()=>{calls++;throw Error('must not call')}});
  await worker(new Request('https://example.invalid',{method:'POST',headers:{Authorization:'Bearer fixture-token','Content-Type':'application/json'},body:JSON.stringify({nonce:'contended'})}));
  const status=(await store.getWithMetadata('autonomy/v1/status')).data;
  assert.equal(calls,0);assert.equal(status.state,'deferred');assert.equal(status.blocked,false);assert.equal(status.defer_reason,'quota_contention');
});

test('an active composer defers background work and refunds the unused quota',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-token';
  const store=new Store();await store.setJSON('agent/godelos-sovereign-01/state',initialiseRecord(seed));await store.setJSON('autonomy/v1/status',{state:'dispatched',nonce:'composing'});
  await store.setJSON('mind/v8/attention',{until:Date.now()+60_000});let calls=0;
  const worker=autonomyWorker({storeFactory:()=>store,completionProvider:async()=>{calls++;throw Error('must not call')}});
  await worker(new Request('https://example.invalid',{method:'POST',headers:{Authorization:'Bearer fixture-token','Content-Type':'application/json'},body:JSON.stringify({nonce:'composing'})}));
  const status=(await store.getWithMetadata('autonomy/v1/status')).data;
  assert.equal(calls,0);assert.equal(status.state,'deferred');assert.equal(status.blocked,false);
  assert.equal((await store.getWithMetadata('autonomy/v1/usage/'+new Date().toISOString().slice(0,10))).data.calls,0);
});

test('failed autonomous episode backs off and dispatches a fresh nonce without manual recovery',async()=>{
 process.env.AUTONOMY_ENABLED='true';process.env.DEEPSEEK_API_KEY='fixture';process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-token';process.env.URL='https://example.invalid';process.env.AUTONOMY_INTERVAL_MINUTES='15';
 const store=new Store();let now=Date.now(),calls=0,sent=0;
 await store.setJSON('autonomy/v1/status',{state:'dispatched',nonce:'bad'});
 const worker=autonomyWorker({storeFactory:()=>store,clock:()=>now,completionProvider:async()=>{calls++;return {text:'{"reply":"truncated'}}});
 await worker(new Request('https://example.invalid',{method:'POST',headers:{Authorization:'Bearer fixture-token','Content-Type':'application/json'},body:JSON.stringify({nonce:'bad'})}));
 const failed=(await store.getWithMetadata('autonomy/v1/status')).data;
 assert.equal(failed.state,'failed');assert.equal(failed.blocked,false);assert.equal(failed.consecutive_failures,1);
 const tick=autonomyScheduler({storeFactory:()=>store,clock:()=>now,send:async()=>{sent++;return {status:202}}});
 await tick();assert.equal(sent,0);now+=900001;await tick();assert.equal(sent,1);assert.equal(calls,1);
 assert.notEqual((await store.getWithMetadata('autonomy/v1/status')).data.nonce,'bad');
 assert.equal((await store.getWithMetadata('mind/v8/results/auto-bad')).data.status,'failed');
});

test('legacy blocked failure reconciles automatically before a later fresh dispatch',async()=>{
 const store=new Store();let now=Date.now(),sent=0;
 await store.setJSON('autonomy/v1/status',{state:'failed',blocked:true,nonce:'legacy',lease_expires_at:now-1});
 const tick=autonomyScheduler({storeFactory:()=>store,clock:()=>now,send:async()=>{sent++;return {status:202}}});
 await tick();assert.equal(sent,0);assert.equal((await store.getWithMetadata('autonomy/v1/status')).data.blocked,false);
 assert.equal((await store.getWithMetadata('autonomy/v1/recovery/legacy')).data.provider_call_repeated,false);
 now+=900001;await tick();assert.equal(sent,1);
});
