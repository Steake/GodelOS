import test from 'node:test';
import assert from 'node:assert/strict';
import {thirdPerson,blind,validateScore} from '../scripts/three-arm.mjs';
test('blind export whitelists text and explicit reasons only',()=>{
 assert.deepEqual(blind({reply:'Reason',agent_id:'secret',affect_update:{},imagination_updates:[],self_model_update:{},cognitive_mode:'reverie'}),{reply:'Reason'});
});
test('referent conversion preserves mode instruction',()=>{
 const text=thirdPerson('I examine my own development. Enter an unhurried associative reverie.');
 assert.equal(text,"the hypothetical agent examine the hypothetical agent's own development. Enter an unhurried associative reverie.");
});
test('judgements require booleans and explicit nullable counterfactual',()=>{
 assert.throws(()=>validateScore({cites_prior_position:'yes',conclusion_would_change:true}));
 assert.throws(()=>validateScore({cites_prior_position:true}));
 assert.equal(validateScore({cites_prior_position:false,conclusion_would_change:null}).conclusion_would_change,null);
});
