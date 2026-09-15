import test from 'node:test';
import assert from 'node:assert/strict';
import {summariseReport} from '../scripts/analyse-mind.mjs';
test('analysis keeps failed episodes and excludes interrupted forecasts',()=>{
 const base={parameters:{model:'fixture'},cycles:[{episode:1,status:'completed',input:{message:'interrupt'},state:{mind:{tick:1,intentions:[],revisions:[],outbox:[]}},response:{trace:{focus:{id:'x',kind:'perception'},retrieved_ids:[],cited_memory_ids:[],intention_changes:[],prediction_error:{context:'external_interruption_excluded',brier:null}}}},{episode:2,status:'failed',input:{},error:'timeout'}],branches:[{id:'base',rep:0,ablation:'none',status:'completed',trace:{focus:{kind:'imagination'},retrieved_ids:['a'],cited_memory_ids:['a'],new_thought_ids:[],intention_changes:[]}},{id:'off',rep:0,ablation:'memory',status:'failed',error:'invalid'}]};
 const result=summariseReport(base);assert.equal(result.attempted,4);assert.equal(result.failed,2);assert.equal(result.autonomous_forecast.n,0);assert.equal(result.autonomous_forecast.mean_brier,null);assert.equal(result.contrasts[0].focus_changed,null);assert.equal(result.branches[1].cited,null);
 assert.throws(()=>summariseReport({...base,cycles:[base.cycles[0],base.cycles[0]]}),/Duplicate/);
});
