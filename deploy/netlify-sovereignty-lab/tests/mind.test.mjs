import test from 'node:test';
import assert from 'node:assert/strict';
import seed from '../netlify/functions/lib/seed.mjs';
import {initialiseRecord,appendEvent,verifyDeployedChain} from '../netlify/functions/lib/core.mjs';
import {ensureMind,prepareMind,mindMessages,finishMind,KINDS} from '../netlify/functions/lib/mind.mjs';
import {createMindRuntime} from '../netlify/functions/lib/mind-runtime.mjs';

const state=()=>{const s=initialiseRecord(seed).state;ensureMind(s);return s;};
const reply=(update={})=>({reply:'Examine the selected topic.',belief_updates:[],interest_updates:[],tension_updates:[],autobiographical_summary:'Selected a thought and retained a future intention.',mind_update:update});
const prediction=kind=>({probabilities:Object.fromEntries(KINDS.map(k=>[k,k===kind?1:0])),reason:'Fixture forecast'});

test('workspace selection broadcasts the same focus to cognition and consolidation',()=>{
 const p=prepareMind(state(),{message:'A new person wants to discuss a shared question',person_id:'person'});
 assert.equal(p.mode,'dialogue');assert.equal(p.workspace.focus.kind,'perception');
 assert.ok(mindMessages(p)[1].content.includes(p.workspace.focus.id));
 const done=finishMind(p,reply());
 assert.equal(done.state.mind.memories.at(-1).focus_id,p.workspace.focus.id);
 assert.equal(done.state.mind.focus_history.at(-1).id,p.workspace.focus.id);
 assert.equal(done.trace.consumers.length,4);
});
test('affect ablation removes a numerical contribution to attention with identical input',()=>{
 const s=state(),original=structuredClone(s),full=prepareMind(s,{outcome:'novel'}),off=prepareMind(s,{outcome:'novel'},{ablation:'affect'});
 assert.ok(full.workspace.competitors.concat(full.workspace.focus).some(c=>c.components.affect>0));
 assert.ok(off.workspace.competitors.concat(off.workspace.focus).every(c=>c.components.affect===0));
 assert.deepEqual(s,original);
});
test('intention survives reconstruction and retains prose progress as an unverified claim',()=>{
 let p=prepareMind(state());let done=finishMind(p,reply({intention_updates:[{goal:'Study a surprising contradiction',steps:['Collect a counterexample','Reconcile positions'],priority:1,status:'active',evidence:'Chosen for curiosity'}]}));
 const id=done.state.mind.intentions[0].id;
 const restored=JSON.parse(JSON.stringify(done.state));p=prepareMind(restored);
 done=finishMind(p,reply({intention_updates:[{id,advance:true,priority:.3,status:'active',evidence:'A counterexample was recorded'}]}));
 assert.equal(done.state.mind.intentions[0].step,0);
 assert.equal(done.state.mind.intentions[0].progress_claim.provenance,'unverified_model_claim');
 assert.equal(done.state.mind.intentions[0].history.length,2);
 assert.equal(done.state.mind.intentions[0].priority,.3);
 const next=prepareMind(done.state);const bid=[next.workspace.focus,...next.workspace.competitors].find(c=>c.id===id);assert.ok(!bid||bid.salience===.3);
 assert.throws(()=>finishMind(p,reply({intention_updates:[{id:'invented',evidence:'unfounded'}]})),/unknown ID/);
});
test('forecast is committed before the next selection and errors are computed from observation',()=>{
 const first=finishMind(prepareMind(state()),reply({prediction:prediction('imagination')}));
 const next=prepareMind(first.state,{message:'Interrupt the prediction'});
 assert.equal(next.predictionError.observed,'perception');assert.equal(next.predictionError.brier,null);
 assert.equal(next.predictionError.context,'external_interruption_excluded');
 const idle=prepareMind(first.state);assert.equal(idle.predictionError.evaluated,true);assert.ok(Number.isFinite(idle.predictionError.brier));
});
test('retrieval has finite capacity and nonexistent memory citations are refused',()=>{
 const s=state();s.mind.memories=Array.from({length:10},(_,i)=>({id:'m'+i,tick:0,summary:'question of development',salience:i/10}));
 const p=prepareMind(s);assert.equal(p.workspace.retrieved.length,3);
 assert.equal(prepareMind(s,{}, {ablation:'memory'}).workspace.retrieved.length,0);
 assert.throws(()=>finishMind(p,reply({memory_references:['imagined-memory']})),/not retrieved/);
});
test('new imaginary objects retain provenance and have a future attention bid',()=>{
 const p=prepareMind(state());const r=reply();r.imagination_updates=[{title:'Impossible telescope',image_or_idea:'A telescope that observes its own possible histories',attraction:1}];
 const s=finishMind(p,r).state;assert.equal(s.imaginations.at(-1).status,'imagined_not_adopted');
 const next=prepareMind(s);assert.ok([next.workspace.focus,...next.workspace.competitors].some(c=>c.id===s.imaginations.at(-1).imagination_id));
});
test('habituation makes repeated focus less competitive',()=>{
 const s=state(),a=prepareMind(s);s.mind.focus_history=Array.from({length:4},()=>({id:a.workspace.focus.id}));
 const b=prepareMind(s);assert.notEqual(a.workspace.focus.id,b.workspace.focus.id);
});
test('self-observation claims must cite actual recorded event kinds',()=>{
 const s=state();s.mind.tick=3;s.mind.focus_history=[{id:'i1',tick:1,kind:'imagination'},{id:'i3',tick:3,kind:'tension'}];
 const p=prepareMind(s),context=JSON.parse(mindMessages(p)[1].content);
 assert.equal(context.observed_history[0].focus_kind,'imagination');
 assert.throws(()=>finishMind(p,reply({observed_event_references:[{tick:3,focus_kind:'reflection'}]})),/contradicts/);
 assert.equal(finishMind(p,reply({observed_event_references:[{tick:3,focus_kind:'tension'}]})).trace.observed_event_references[0].tick,3);
});
test('rolling event-chain verification remains correct beyond 200 cycles',()=>{
 const r=initialiseRecord(seed);for(let n=0;n<230;n++)appendEvent(r,'test',{n});
 assert.equal(r.deployed_events.length,200);assert.equal(verifyDeployedChain(r),true);
 r.deployed_events[10].payload.n=-1;assert.equal(verifyDeployedChain(r),false);
});

function rig(complete){
 const data=new Map();let ver=0;const store={async getWithMetadata(k){return structuredClone(data.get(k)||null)},async setJSON(k,v,o={}){const old=data.get(k);if(o.onlyIfNew&&old||o.onlyIfMatch&&old?.etag!==o.onlyIfMatch)return {modified:false};const etag=String(++ver);data.set(k,{data:structuredClone(v),etag});return {modified:true,etag}}};
 const load=async()=>{let e=await store.getWithMetadata('state');if(!e){await store.setJSON('state',initialiseRecord(seed));e=await store.getWithMetadata('state');}return {record:e.data,etag:e.etag};};
 const save=async(r,e)=>{if(!(await store.setJSON('state',r,{onlyIfMatch:e})).modified)throw Error('conflict');};
 return {engine:createMindRuntime({store,load,save,complete}),load,store};
}
test('runtime continues after a failed goal artifact and advances only the later verified artifact',async()=>{
 let stage=0,id;
 const {engine,load}=rig(async messages=>{
  if(stage===2)assert.ok(messages[1].content.includes('verification_history'));
  const update=stage++===0?{intention_updates:[{goal:'Pick feasible budget plans',steps:['Choose plans'],evidence:'Chosen test',priority:1}]}:{intention_updates:[{id,evidence:'Submitting plan',artifact:{decisions:stage===2?['a','a']:['b','a']}}]};
  return {text:JSON.stringify(reply(update)),model:'fixture'};
 });
 await engine.cycle({request_id:'goal-start'});id=(await load()).record.state.mind.intentions.at(-1).id;
 const contract={kind:'budget_plan',cases:[{budget:3,options:[{id:'a',cost:4,utility:10},{id:'b',cost:2,utility:5}]},{budget:5,options:[{id:'a',cost:4,utility:10},{id:'b',cost:2,utility:5}]}]};
 await engine.intentionVerification({action:'bind',intention_id:id,expected_step:0,contract});
 await assert.rejects(engine.intentionVerification({action:'bind',intention_id:id,expected_step:0,contract}),/already/);
 const first=await engine.cycle({request_id:'goal-failed-artifact'});assert.ok(first.reply);assert.equal((await load()).record.state.mind.intentions.at(-1).step,0);
 assert.equal((await engine.evidence('goal-failed-artifact')).result.status,'completed');
 await engine.cycle({request_id:'goal-corrected-artifact'});const g=(await load()).record.state.mind.intentions.at(-1);assert.equal(g.step,1);assert.equal(g.verified_revision,1);
 await assert.rejects(engine.intentionVerification({action:'submit',intention_id:id,expected_step:0,artifact:{decisions:['b','a']}}),/Unknown or inactive/);
 assert.equal((await load()).record.usage.calls,3);
});
test('runtime is idempotent, reserves the call and preserves raw evidence',async()=>{
 let calls=0;const {engine,load}=rig(async()=>{calls++;return {text:JSON.stringify(reply()),model:'fixture'}});
 const a=await engine.cycle({request_id:'one'}),b=await engine.cycle({request_id:'one'});
 assert.equal(calls,1);assert.equal(a.state_version,b.state_version);assert.equal(b.replayed,true);
 assert.ok((await engine.evidence('one')).raw.completion.text);
 assert.equal((await load()).record.usage.calls,1);
 assert.equal((await engine.history()).episodes[0].reply,'Examine the selected topic.');
 assert.equal((await engine.history()).episodes[0].request_id,'one');
 await assert.rejects(engine.cycle({request_id:'one',outcome:'novel'}),/different input/);
});
test('pause prevents idle calls but contact remains possible',async()=>{
 let calls=0;const {engine}=rig(async()=>{calls++;return {text:JSON.stringify(reply()),model:'fixture'}});
 await engine.control(true);await assert.rejects(engine.cycle({request_id:'idle'}),/paused/);
 await engine.cycle({request_id:'contact',message:'Hello'},true);assert.equal(calls,1);
});
test('invalid model output is retained and never applied or automatically repeated',async()=>{
 let calls=0;const {engine,load}=rig(async()=>{calls++;return {text:'truncated{',model:'fixture'}});
 await assert.rejects(engine.cycle({request_id:'failure'}));await assert.rejects(engine.cycle({request_id:'failure'}));
 assert.equal(calls,1);assert.equal((await load()).record.state_version,11);assert.equal((await engine.evidence('failure')).raw.completion.text,'truncated{');
});
test('overlapping cognition cannot issue a second provider call',async()=>{
 let release,started;const start=new Promise(r=>{started=r});const barrier=new Promise(r=>{release=r});let calls=0;
 const {engine}=rig(async()=>{calls++;started();await barrier;return {text:JSON.stringify(reply()),model:'fixture'}});
 const pending=engine.cycle({request_id:'first'});await start;
 await assert.rejects(engine.cycle({request_id:'second'}),/in progress/);release();await pending;assert.equal(calls,1);
});
test('expired cycle recovery records uncertainty and never repeats a provider call',async()=>{
 let calls=0;const {engine,store,load}=rig(async()=>{calls++;return {text:JSON.stringify(reply())}});
 const {record,etag}=await load();record.cognition_lease={request_id:'expired',expires_at:0};record.usage={day:new Date().toISOString().slice(0,10),calls:1};
 await store.setJSON('state',record,{onlyIfMatch:etag});
 await assert.rejects(engine.recover('wrong'),/pending request/);
 const result=await engine.recover('expired');assert.equal(result.previous_outcome,'unknown');assert.equal(calls,0);
 assert.equal((await load()).record.usage.calls,1);assert.equal((await engine.evidence('expired')).result.status,'unknown');
 assert.equal((await engine.recover('expired')).status,'no_pending_cycle');
});
test('recovery refuses an in-flight cycle',async()=>{
 const {engine,store,load}=rig(async()=>{}),{record,etag}=await load();
 record.cognition_lease={request_id:'active',expires_at:Date.now()+120000};await store.setJSON('state',record,{onlyIfMatch:etag});
 await assert.rejects(engine.recover('active'),/not expired/);
});

test('invalid self-observation preserves reply without applying any cognitive update',async()=>{
 const bad=reply({observed_event_references:[{tick:999,focus_kind:'social'}],self_observation:'Invented history'});
 const {engine,load}=rig(async()=>({text:JSON.stringify(bad),model:'fixture'}));
 const before=(await load()).record.state;ensureMind(before);
 const r=await engine.submit({request_id:'bad-reference',message:'Hello'});
 assert.equal(r.reply,bad.reply);assert.equal(r.state_applied,false);assert.ok(r.warnings.length);
 assert.deepEqual((await load()).record.state.beliefs,before.beliefs);
 assert.equal((await load()).record.state.mind.self_observation,undefined);
 assert.equal((await load()).record.state.mind.tick,1);
 assert.equal((await engine.history()).episodes[0].reply,bad.reply);
 assert.equal((await engine.evidence('bad-reference')).raw.completion.text,JSON.stringify(bad));
});
test('chat queues behind an idle call and is serviced before another idle call',async()=>{
 let release,started;const start=new Promise(r=>started=r),wait=new Promise(r=>release=r);let calls=0;
 const {engine,load}=rig(async messages=>{calls++;if(calls===1){started();await wait;}return {text:JSON.stringify(reply()),model:'fixture'};});
 const idle=engine.cycle({request_id:'idle-first'});await start;
 const queued=await engine.submit({request_id:'human-next',message:'Address this new evidence'});
 assert.equal(queued.queued,true);assert.equal(calls,1);
 release();await idle;
 const next=await engine.cycle({request_id:'idle-second'});
 assert.equal(next.request_id,'human-next');assert.equal(next.cognitive_mode,'dialogue');assert.equal(calls,2);
 assert.equal((await load()).record.inbox[0].status,'completed');
 const replay=await engine.submit({request_id:'human-next',message:'Address this new evidence'});assert.equal(replay.replayed,true);assert.equal(calls,2);
});
test('a composing hold defers idle provider work',async()=>{
 let calls=0;const {engine}=rig(async()=>{calls++;return {text:JSON.stringify(reply())}});
 await engine.attention();assert.equal((await engine.cycle({request_id:'held'})).deferred,true);assert.equal(calls,0);
 await engine.submit({request_id:'contact-held',message:'Answer me'});assert.equal(calls,1);
});
test('complete reply survives malformed trailing model metadata',async()=>{
 const {engine}=rig(async()=>({text:'{"reply":"A complete answer.","mind_update": broken',finish_reason:'length'}));
 const r=await engine.submit({request_id:'salvage',message:'Hello'});
 assert.equal(r.reply,'A complete answer.');assert.equal(r.state_applied,false);
});
test('renamed duplicate thoughts incur semantic habituation',()=>{
 const s=state();s.interests=[];s.tensions=[];s.imaginations=[];s.mind.thoughts=[{id:'new-id',kind:'inquiry',title:'Investigate the blocked continuity question again',salience:1,created_tick:0}];
 s.mind.focus_history=[{id:'old-id',kind:'inquiry',title:'Investigate the blocked continuity question again',tick:0}];
 s.beliefs=[]; // Isolate habituation from V13's competing opinion-revision bids.
 const p=prepareMind(s);const bid=[p.workspace.focus,...p.workspace.competitors].find(x=>x.id==='new-id');assert.ok(bid);assert.ok(bid.components.habituation<0);
});
test('personality revisions persist gradually and affect changes expression',()=>{
 const p=prepareMind(state());const done=finishMind(p,reply({personality_update:{trait:'warmth',delta:.9,reason:'A specific considerate interaction'}}));
 assert.ok(Math.abs(done.state.mind.personality.warmth-.58)<1e-9);assert.equal(done.state.mind.personality.history.length,1);
 const a=state(),b=structuredClone(a);a.affect.valence=.9;a.affect.frustration=0;b.affect.valence=-.9;b.affect.frustration=1;
 const read=s=>JSON.parse(mindMessages(prepareMind(s))[1].content).expression;
 assert.ok(read(a).playfulness>read(b).playfulness);assert.ok(read(b).directness>read(a).directness);
});

test('complete prose from a broken transport is delivered with cognitive updates quarantined',async()=>{
 const {engine}=rig(async()=>({text:JSON.stringify(reply()),transport_error:'connection lost',stream_complete:false}));
 const r=await engine.submit({request_id:'transport-recovery',message:'Hello'});
 assert.equal(r.reply,'Examine the selected topic.');assert.equal(r.state_applied,false);
 assert.equal((await engine.evidence('transport-recovery')).raw.completion.transport_error,'connection lost');
});
