import test from 'node:test';import assert from 'node:assert/strict';
import {compileCandidate,compilePolicy,evaluateCandidate,evaluatePolicy,createEvolution,BASELINE} from '../netlify/functions/lib/evolution9.mjs';
const program={op:'sub',args:[{op:'add',args:['salience','need']},{op:'mul',args:[2,'repeats']}]};
const choices=[{salience:1,need:1,affect:1,repeats:1},{salience:.4,need:.6,affect:.4,repeats:0}];
const design={thesis:'Repeated focus should lose to a fresh question while important new evidence remains competitive.',program,tests:[{name:'Escape repetition',choices,expected:1},{name:'Preserve salient new evidence',choices:choices.map(x=>({...x,repeats:0})),expected:0}]};
test('compiler rejects executable strings, nonfinite constants and deep programs',()=>{
 assert.throws(()=>compilePolicy('process.env'),/Unknown/);assert.throws(()=>compilePolicy(Infinity),/finite/);
 let deep=1;for(let i=0;i<12;i++)deep={op:'add',args:[deep,1]};assert.throws(()=>compilePolicy(deep),/budget/);
 assert.equal(evaluatePolicy(compilePolicy(program),choices[1]),1);
});
test('independent gate rejects baseline and accepts the specified repetition intervention',()=>{
 assert.equal(evaluateCandidate(compileCandidate({...design,program:BASELINE})).eligible,false);
 const result=evaluateCandidate(compileCandidate(design));assert.equal(result.eligible,true);assert.equal(result.independent_clusters.length,80);assert.ok(result.interval[0]>0);
});
test('legacy synthetic winner cannot bypass V12 adoption and rejects tampering',async()=>{
 const db=new Map();let revision=0;let record={state_version:1,state:{mind:{},values:{curiosity:.7}}};
 const store={async getWithMetadata(k){return db.has(k)?{data:structuredClone(db.get(k)),etag:'1'}:null;},async setJSON(k,v,o){if(o?.onlyIfNew&&db.has(k))return {modified:false};db.set(k,structuredClone(v));return {modified:true};}};
 const engine=createEvolution({store,load:async()=>({record:structuredClone(record),etag:revision}),save:async(r,e)=>{assert.equal(e,revision);record=structuredClone(r);revision++;},complete:async()=>({text:JSON.stringify(design),model:'fixture'})});
 const pkg=await engine.propose();assert.ok(pkg.signature);assert.equal(pkg.content.value_constitution.curiosity,.7);
 await assert.rejects(engine.deploy(pkg.content.id),/V12 adoption is held/);assert.equal(record.state.mind.experimental_policy,undefined);
 db.get('evolution/v9/packages/'+pkg.content.id).content.candidate.program=0;
 await assert.rejects(engine.deploy(pkg.content.id),/signature/);
});
