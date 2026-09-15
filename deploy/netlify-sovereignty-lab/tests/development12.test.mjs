import test from 'node:test';
import assert from 'node:assert/strict';
import {createDevelopment,DEVELOPMENT_KEY} from '../netlify/functions/lib/development12.mjs';
import {createEvolution} from '../netlify/functions/lib/evolution9.mjs';
import {developmentScheduler} from '../netlify/functions/development-scheduler.mjs';
import {createHandler} from '../netlify/functions/api.mjs';

class Store{
 db=new Map();revision=0;
 async getWithMetadata(k){return structuredClone(this.db.get(k)||null);}
 async setJSON(k,data,o={}){
  const old=this.db.get(k);if(o.onlyIfNew&&old||o.onlyIfMatch&&o.onlyIfMatch!==old?.etag)return {modified:false};
  this.db.set(k,{data:structuredClone(data),etag:String(++this.revision)});return {modified:true};
 }
}
const pkg={content:{id:'fixture',candidate:{thesis:'Try preserving recurring goals',code_hash:'fixture',program:'need'},evidence:{gain:.5,interval:[.4,.6],independent_clusters:[{candidate:1}],limitation:'Synthetic only'}}};
function fixture(propose=async()=>pkg){const store=new Store();let now=0;const engine=createDevelopment({store,evolution:{propose},clock:()=>now});return {store,engine,advanceClock:()=>now+=600001};}

test('round budget is validated before creating a run',async()=>{
 const {engine}=fixture();for(const rounds of [0,11,1.5,'3'])await assert.rejects(engine.start({rounds}),/1–10/);
 assert.equal(await engine.status(),null);
});
test('three persisted rounds inherit reviews and never call deploy',async()=>{
 const contexts=[];const {engine,store}=fixture(async c=>{contexts.push(c);return pkg;});
 await engine.start();for(let n=0;n<3;n++)await engine.advance();
 const s=await engine.status();assert.equal(s.phase,'completed');assert.equal(s.active,false);assert.equal(s.history.length,3);
 assert.equal(contexts[1].development_history[0].review.promotion_allowed,false);
 assert.ok(s.history[0].review.findings.some(f=>f.id==='ceiling'));
 assert.equal([...store.db.keys()].filter(k=>k.includes('/rounds/')).length,3);
 await engine.advance();assert.equal(contexts.length,3);
});
test('concurrent delivery reserves exactly one provider attempt',async()=>{
 let done,calls=0;const {engine}=fixture(async()=>{calls++;return new Promise(r=>done=r);});
 await engine.start();const first=engine.advance();while(!done)await new Promise(r=>setImmediate(r));
 assert.equal((await engine.advance()).phase,'designing');assert.equal(calls,1);done(pkg);await first;
});
test('a delayed duplicate delivery cannot consume the next round',async()=>{
 let calls=0;const {engine}=fixture(async()=>{calls++;return pkg;});const s=await engine.start();
 const delivery={run_id:s.id,expected_round:0};await engine.advance(delivery);await engine.advance(delivery);
 assert.equal(calls,1);assert.equal((await engine.status()).round,1);
});
test('pause during generation retains the result but prevents the next round',async()=>{
 let done;const {engine}=fixture(()=>new Promise(r=>done=r));await engine.start();const work=engine.advance();
 while(!done)await new Promise(r=>setImmediate(r));await engine.pause();done(pkg);await work;
 assert.equal((await engine.advance()).round,1);assert.equal((await engine.status()).active,false);
});
test('global thinking pause prevents generation',async()=>{
 const {engine,store}=fixture(()=>{throw Error('must not call');});await engine.start();
 await store.setJSON('mind/v8/settings',{paused:true});assert.equal((await engine.advance()).round,0);
});
test('resume continues the same run and rejects a completed run',async()=>{
 const {engine}=fixture();const s=await engine.start({rounds:1});await engine.pause();await engine.resume();
 assert.equal((await engine.advance()).id,s.id);await assert.rejects(engine.resume(),/unfinished/);
});
test('failure is retained and next round is allowed',async()=>{
 let calls=0;const {engine}=fixture(async()=>{if(++calls===1)throw Error('provider unavailable');return pkg;});
 await engine.start({rounds:2});await engine.advance();await engine.advance();const s=await engine.status();
 assert.equal(s.history[0].outcome,'failed');assert.equal(s.history[1].outcome,'reviewed');
});
test('expired unknown work consumes one round without replay; late output cannot overwrite it',async()=>{
 let done,calls=0;const {engine,advanceClock}=fixture(()=>{calls++;return new Promise(r=>done=r);});
 await engine.start();const work=engine.advance();while(!done)await new Promise(r=>setImmediate(r));
 advanceClock();await engine.advance();assert.equal(calls,1);assert.equal((await engine.status()).history[0].outcome,'outcome_unknown');
 done(pkg);await work;assert.equal((await engine.status()).round,1);assert.equal((await engine.status()).history[0].outcome,'outcome_unknown');
});
test('cursor gap recovers immutable result rather than generating again',async()=>{
 const {engine,store}=fixture(()=>{throw Error('must not call');});const s=await engine.start();
 await store.setJSON(DEVELOPMENT_KEY,{...s,phase:'designing',token:'old',lease_expires_at:100});
 await store.setJSON(`development/v12/runs/${s.id}/rounds/1`,{round:1,outcome:'reviewed',thesis:'retained'});
 assert.equal((await engine.advance()).history[0].thesis,'retained');
});
test('real compiler, signed package and reviewer run end to end with a labelled fixture LM',async()=>{
 const store=new Store();const choices=[{salience:1,need:1,affect:1,repeats:1},{salience:.4,need:.6,affect:.4,repeats:0}];
 const design={thesis:'Penalise repetition',program:{op:'sub',args:['salience','repeats']},tests:[{choices,expected:1},{choices:choices.map(x=>({...x,repeats:0})),expected:0}]};
 let calls=0;const evolution=createEvolution({store,load:async()=>({record:{state:{mind:{}}}}),save:async()=>{throw Error('Live state must not change');},complete:async messages=>{calls++;assert.ok(messages.at(-1).content.includes('development_context'));return {text:JSON.stringify(design),model:'fixture-not-live'};}});
 const engine=createDevelopment({store,evolution});await engine.start({rounds:2});await engine.advance();await engine.advance();
 assert.equal(calls,2);const s=await engine.status();assert.equal(s.history[1].outcome,'reviewed');
 const signed=(await store.getWithMetadata('evolution/v9/packages/'+s.history[0].package_id)).data;
 assert.ok(signed.signature);assert.equal(s.history[0].review.decision,'shadow_only');
});
test('scheduler dispatches active durable runs without needing an open browser',async()=>{
 const old={...process.env};Object.assign(process.env,{DEEPSEEK_API_KEY:'fixture',SOVEREIGNTY_ACCESS_TOKEN:'fixture',URL:'https://fixture.invalid'});
 try{const {engine,store}=fixture();let sent=0;const tick=developmentScheduler({storeFactory:()=>store,send:async url=>{assert.ok(String(url).endsWith('development-worker-background'));sent++;return new Response(null,{status:202});}});
 await tick();assert.equal(sent,0);await engine.start();await tick();assert.equal(sent,1);await engine.pause();await tick();assert.equal(sent,1);
 }finally{for(const key of ['DEEPSEEK_API_KEY','SOVEREIGNTY_ACCESS_TOKEN','URL']){if(old[key]===undefined)delete process.env[key];else process.env[key]=old[key];}}
});
test('development HTTP routes authenticate and preserve pause/resume state',async()=>{
 const prior=process.env.SOVEREIGNTY_ACCESS_TOKEN;process.env.SOVEREIGNTY_ACCESS_TOKEN='fixture-access';
 try{const store=new Store(),handler=createHandler({storeFactory:()=>store,completionProvider:async()=>{throw Error('Unexpected provider call');}});
  const request=(action,method='POST',auth=true)=>new Request('https://fixture.invalid/api/development/'+action,{method,headers:{'Content-Type':'application/json',...(auth?{Authorization:'Bearer fixture-access'}:{})},...(method==='POST'?{body:'{}'}:{})});
  assert.equal((await handler(request('start','POST',false))).status,401);
  const started=await handler(request('start'));assert.equal(started.status,200);const s=await started.json();
  assert.equal((await handler(request('pause')).then(r=>r.json())).active,false);
  assert.equal((await handler(request('resume')).then(r=>r.json())).id,s.id);
  assert.equal((await handler(request('status','GET')).then(r=>r.json())).active,true);
 }finally{if(prior===undefined)delete process.env.SOVEREIGNTY_ACCESS_TOKEN;else process.env.SOVEREIGNTY_ACCESS_TOKEN=prior;}
});
