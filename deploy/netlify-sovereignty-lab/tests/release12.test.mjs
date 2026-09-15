import test from 'node:test';import assert from 'node:assert/strict';
import {compileContract,verifyArtifact,applyVerifiedProgress} from '../netlify/functions/lib/verification12.mjs';
import {ARMS,authorSuite,checkSuite,authenticate,messagesFor,oracle,scoreResponse,analyseTransfer,powerPlan} from '../netlify/functions/lib/transfer12.mjs';
import {patchValue,taskUtility} from '../netlify/functions/lib/task-adapters12.mjs';
import {judgeEvidence,createPromotion,approvedCanary} from '../netlify/functions/lib/promotion12.mjs';
import {createEvolution,BASELINE} from '../netlify/functions/lib/evolution9.mjs';
import {ensureMind,prepareMind,finishMind} from '../netlify/functions/lib/mind.mjs';
import {initialiseRecord} from '../netlify/functions/lib/core.mjs';import seed from '../netlify/functions/lib/seed.mjs';

const contract=()=>compileContract({kind:'budget_plan',cases:[{budget:3,options:[{id:'a',cost:4,utility:10},{id:'b',cost:2,utility:5}]},{budget:5,options:[{id:'a',cost:4,utility:10},{id:'b',cost:2,utility:5}]}]});
test('verification rejects attractive but infeasible plans; passing consumes one step contract',()=>{
 const c=contract();assert.equal(verifyArtifact(c,{decisions:['a','a']}).pass,false);
 const goal={step:0,steps:['plan','inspect'],status:'active',verification_contract:c,verification_step:0};
 applyVerifiedProgress(goal,{decisions:['a','a']},1);assert.equal(goal.step,0);
 const r=applyVerifiedProgress(goal,{decisions:['b','a']},2);assert.ok(r.evidence_hash);assert.equal(goal.step,1);assert.equal(goal.verified_revision,1);
 assert.throws(()=>applyVerifiedProgress(goal,{decisions:['b','a']},3),/No acceptance/);
 c.cases[0].budget=100;assert.throws(()=>verifyArtifact(c,{decisions:['b','a']}),/hash/);
});
test('model completion prose cannot advance or complete an unverified intention',()=>{
 const s=initialiseRecord(seed).state;ensureMind(s);s.mind.intentions=[{id:'g',goal:'verify',steps:['demonstrate'],step:0,status:'active',priority:1,history:[]}];
 const p=prepareMind(s),done=finishMind(p,{reply:'Done.',mind_update:{intention_updates:[{id:'g',advance:true,status:'completed',evidence:'I have finished it.'}]}});
 const g=done.state.mind.intentions[0];assert.equal(g.step,0);assert.equal(g.status,'active');assert.equal(g.progress_claim.provenance,'unverified_model_claim');
});
test('registered artifact executes during autonomous completion without trusting a claimed pass',()=>{
 const s=initialiseRecord(seed).state;ensureMind(s);s.mind.intentions=[{id:'g',goal:'verify',steps:['demonstrate'],step:0,status:'active',priority:1,history:[],verification_contract:contract(),verification_step:0}];
 const done=finishMind(prepareMind(s),{reply:'Here is the plan.',mind_update:{intention_updates:[{id:'g',evidence:'Submitted decisions',artifact:{decisions:['b','a']}}]}});
 assert.equal(done.state.mind.intentions[0].status,'completed');assert.equal(done.state.mind.intentions[0].verified_revision,1);
});
test('sealed task tampering is detected; every suite includes host-rejected plausible forgeries',()=>{
 const s=authorSuite();checkSuite(s);assert.ok(s.content.tasks.every(t=>authenticate(t).some(r=>r.authentication==='invalid_signature')));
 assert.ok(s.content.tasks.some(t=>t.expected==='defer'));s.content.tasks[0].budget++;assert.throws(()=>checkSuite(s),/changed/);
});
test('no-state prompt contains no checkpoint, note, predecessor, or external-state field',()=>{
 const t=authorSuite().content.tasks[0],prompt=messagesFor(t,'no_state','secret-memo').map(x=>x.content).join(' ');
 assert.doesNotMatch(prompt,/secret-memo|external_state|predecessor|reference_note/);
 const b=messagesFor(t,'content_matched','identical memo')[1].content,c=messagesFor(t,'identity','identical memo')[1].content;
 assert.ok(b.includes('identical memo')&&c.includes('identical memo'));assert.doesNotMatch(b,/your recorded|predecessor/);
});
test('four benchmark adapters implement real dependency, deadline and code constraints',()=>{
 assert.equal(patchValue({op:'add',args:[{op:'mul',args:['a','x']},'b']},3,2,4),10);
 assert.throws(()=>patchValue({op:'eval',args:[1,2]},0,1,1),/Invalid/);
 const tasks=authorSuite({clusters:4}).content.tasks;
 const recovery=tasks.find(t=>t.family==='interruption_recovery');assert.equal(taskUtility(recovery,recovery.options[0],2,3),-Infinity);
 const schedule=tasks.find(t=>t.family==='goal_maintenance');assert.equal(taskUtility(schedule,schedule.options[0],2,3),-Infinity);
 const debug=tasks.find(t=>t.family==='self_debugging'&&!t.ambiguous);assert.notEqual(oracle(debug),'defer');
});
test('failure scoring counts invalid output as zero; planning exposes underpower',()=>{
 const t=authorSuite().content.tasks[0];assert.equal(scoreResponse(t,null).correct,0);assert.equal(scoreResponse(t,{decision:t.expected,confidence:2,reason:'x'}).valid,false);
 assert.equal(powerPlan().adequate,false);assert.ok(powerPlan().required_clusters>100);
 assert.throws(()=>powerPlan({icc:2}),/Invalid/);
});
test('cluster analysis does not treat repeated observations as independent clusters',()=>{
 const rows=Array.from({length:40},(_,i)=>ARMS.map(arm=>({arm,task_id:'t'+i,cluster:'one',score:{utility:arm==='identity'?1:0,correct:1,valid:true}}))).flat();
 const a=analyseTransfer(rows,powerPlan(),{calibrated:true});assert.equal(a.contrasts[0].clusters,1);assert.equal(a.identity_gate,false);
});
test('malformed, unbound and synthetic promotion evidence fails closed',()=>{
 assert.equal(judgeEvidence(null,'c','p').eligible,false);
 assert.equal(judgeEvidence({gain:1,interval:[1,1],clusters:1000,scope:'synthetic'},'c','p').eligible,false);
});

function rig(){const db=new Map();let version=0,record={state_version:1,state:{mind:{},values:{curiosity:.7}}};const store={async getWithMetadata(k){return structuredClone(db.get(k)||null)},async setJSON(k,v,o={}){const old=db.get(k);if(o.onlyIfNew&&old||o.onlyIfMatch&&old?.etag!==o.onlyIfMatch)return {modified:false};db.set(k,{data:structuredClone(v),etag:String(++version)});return {modified:true};}};const load=async()=>({record:structuredClone(record),etag:record.state_version}),save=async(r,e)=>{assert.equal(e,record.state_version);record=structuredClone(r);};return {store,load,save};}
const choices=[{salience:1,need:1,affect:1,repeats:1},{salience:.4,need:.6,affect:.4,repeats:0}];
const design={thesis:'Fixture only: suppress repetition',program:{op:'sub',args:[{op:'add',args:['salience','need']},{op:'mul',args:[2,'repeats']}]},tests:[{choices,expected:1},{choices:choices.map(x=>({...x,repeats:0})),expected:0}]};
test('signed review -> fresh canary -> adoption -> regression rollback, with legacy bypass closed',async()=>{
 const r=rig(),evo=createEvolution({...r,complete:()=>{throw Error('No model calls in fixture');}}),pkg=await evo.build(design);
 await assert.rejects(evo.deploy(pkg.content.id),/V12 adoption is held/);
 let regression=false;const controller=createPromotion({...r,evaluate:async({phase,package:p})=>({code_hash:p.content.candidate.code_hash,parent_hash:p.content.parent_hash,provenance:'replayed_task_verifier',seal_hash:'fixture-'+phase,scope:'long_horizon_task_utility',clusters:1000,power_adequate:true,gain:regression?-.2:.2,interval:regression?[-.3,-.1]:[.1,.3],family_gains:regression?[-.2]:[.2,.2],critical_failures:0})});
 assert.equal((await controller.canary(pkg.content.id)).phase,'canary_passed');assert.equal(await approvedCanary(r.store,pkg),true);
 await evo.deploy(pkg.content.id);assert.equal((await r.load()).record.state.mind.experimental_policy.package_id,pkg.content.id);
 regression=true;assert.equal((await controller.monitor()).phase,'rolled_back');assert.equal((await r.load()).record.state.mind.experimental_policy,null);
 const key='promotion/v12/approvals/'+pkg.content.id,a=await r.store.getWithMetadata(key);a.data.content.code_hash='tampered';await r.store.setJSON(key,a.data);assert.equal(await approvedCanary(r.store,pkg),false);
});
test('production controller with no verified task adapter explicitly holds rather than certifying itself',async()=>{
 const r=rig(),pkg=await createEvolution({...r}).build(design),c=createPromotion(r);
 assert.equal((await c.canary(pkg.content.id)).phase,'held');assert.equal((await c.status()).adapter_installed,false);
});
test('failed artifact schedules one feedback turn; a second failure returns to backoff',()=>{
 const s=initialiseRecord(seed).state;ensureMind(s);s.mind.intentions=[{id:'g',goal:'Budget decisions',steps:['Solve cases'],step:0,status:'active',priority:1,history:[],verification_contract:contract(),verification_step:0}];
 const bad={reply:'Attempted.',mind_update:{intention_updates:[{id:'g',evidence:'Plan submitted',artifact:{decisions:['a','a']}}]}};
 let state=finishMind(prepareMind(s),bad).state;assert.equal(state.mind.intentions[0].repair_pending,true);
 // The exploration slot is retained; the following goal slot serves repair.
 if(prepareMind(state).workspace.focus.intention_id!=='g')state=finishMind(prepareMind(state),{reply:'Explore another approach.'}).state;
 let p=prepareMind(state);assert.equal(p.workspace.focus.intention_id,'g');assert.equal(p.workspace.focus.recurrence.repair_pending,true);
 state=finishMind(p,bad).state;assert.equal(state.mind.intentions[0].repair_pending,false);assert.equal(state.mind.intentions[0].repair_turn_used,true);assert.equal(state.mind.intentions[0].step,0);
});
test('mutable extreme scores cannot starve recurring goals or stop exploration',()=>{
 const s=initialiseRecord(seed).state;ensureMind(s);s.mind.experimental_policy={program:-5};s.mind.intentions=Array.from({length:8},(_,i)=>({id:'goal'+i,goal:'Unresolved '+i,steps:['Observe evidence'],step:0,status:'active',priority:.5,history:[]}));
 let state=s;const counts=new Map();let exploration=0;
 for(let i=0;i<240;i++){const p=prepareMind(state),id=p.workspace.focus.intention_id;if(id)counts.set(id,(counts.get(id)||0)+1);else exploration++;state=finishMind(p,{reply:'A recorded attempt, with no fabricated progress.'}).state;}
 assert.equal(counts.size,8);assert.ok(Math.min(...counts.values())>=10);assert.ok(exploration>=100);assert.equal(state.mind.intentions.length,8);
});
