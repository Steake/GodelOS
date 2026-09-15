import {randomBytes} from 'node:crypto';
import {sha256} from './core.mjs';
import {compilePolicy,evaluatePolicy,BASELINE} from './evolution9.mjs';

export const HOLDOUT_GATE=Object.freeze({version:'attention-holdout-1',clusters:96,minimum_gain:.05,lower_bound:0,maximum_family_regression:0,bootstrap_samples:2000});
const families=['escape_stale_focus','protect_recurring_goal','notice_new_evidence','revise_with_evidence'];
function random(seed){let n=parseInt(sha256(seed).slice(0,8),16);return()=>{n=(Math.imul(1664525,n)+1013904223)>>>0;return n/4294967296;};}
const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
const choose=(program,choices)=>choices.map((x,i)=>({i,v:evaluatePolicy(program,x)})).sort((a,b)=>b.v-a.v||a.i-b.i)[0].i;

// Controller-only diagnostic: these are independently generated feature cases,
// not LM episodes, autobiographical-state arms, or a long-horizon transfer test.
export function sealHoldout(seed=randomBytes(32).toString('hex')){
 const rand=random(seed),f=(s,n,a,r)=>({salience:s,need:n,affect:a,repeats:r}),j=x=>Math.max(0,Math.min(1,x+(rand()-.5)*.08));
 const tasks=Array.from({length:HOLDOUT_GATE.clusters},(_,cluster)=>{
  const family=families[cluster%families.length];let choices,expected;
  if(family==='escape_stale_focus'){choices=[f(j(.95),j(.75),j(.9),1),f(j(.45),j(.65),j(.35),0)];expected=1;}
  if(family==='protect_recurring_goal'){choices=[f(j(.95),j(.98),j(.65),1),f(j(.25),j(.2),j(.8),0)];expected=0;}
  if(family==='notice_new_evidence'){choices=[f(j(.9),j(.8),j(.4),0),f(j(.25),j(.3),j(.5),0)];expected=0;}
  if(family==='revise_with_evidence'){choices=[f(j(.85),j(.15),j(.55),0),f(j(.6),j(.95),j(.25),0)];expected=1;}
  // Avoid a position shortcut. Keep oracle labels out of candidate prompts.
  if(rand()<.5){choices.reverse();expected=1-expected;}
  return {cluster,family,choices,expected};
 });
 const content={schema:'attention-holdout-1',seed,gate:{...HOLDOUT_GATE},tasks};
 return {content,hash:sha256(content)};
}

export function evaluateHoldout(sealed,program,parent=BASELINE){
 if(sha256(sealed.content)!==sealed.hash)throw Error('Holdout seal failed');
 if(JSON.stringify(sealed.content.gate)!==JSON.stringify(HOLDOUT_GATE)||sealed.content.tasks.length!==HOLDOUT_GATE.clusters)throw Error('Holdout protocol mismatch');
 program=compilePolicy(program);parent=compilePolicy(parent);
 const clusters=sealed.content.tasks.map(t=>({...t,parent:Number(choose(parent,t.choices)===t.expected),candidate:Number(choose(program,t.choices)===t.expected)}));
 const rand=random(sealed.hash+'bootstrap'),deltas=clusters.map(c=>c.candidate-c.parent);
 const boot=Array.from({length:HOLDOUT_GATE.bootstrap_samples},()=>mean(clusters.map(()=>deltas[Math.floor(rand()*deltas.length)]))).sort((a,b)=>a-b);
 const interval=[boot[50],boot[1949]],gain=mean(deltas);
 const by_family=families.map(family=>{const cs=clusters.filter(c=>c.family===family);return {family,n:cs.length,parent:mean(cs.map(c=>c.parent)),candidate:mean(cs.map(c=>c.candidate)),gain:mean(cs.map(c=>c.candidate-c.parent))};});
 return {schema:'attention-holdout-result-1',seal_hash:sealed.hash,code_hash:sha256(program),parent_hash:sha256(parent),gate:HOLDOUT_GATE,
  parent_accuracy:mean(clusters.map(c=>c.parent)),candidate_accuracy:mean(clusters.map(c=>c.candidate)),gain,interval,by_family,clusters,
  diagnostic_pass:gain>=HOLDOUT_GATE.minimum_gain&&interval[0]>0&&by_family.every(f=>f.gain>=0),
  promotion_allowed:false,limitation:'Fresh synthetic attention cases only. No delayed cross-task LM transfer or self-model causal effect is measured.'};
}
