import {sha256} from './core.mjs';
import {compilePolicy,evaluatePolicy} from './evolution9.mjs';

// Small deterministic adapters, never arbitrary host execution. Natural-language
// achievements remain claims until a domain-specific adapter is installed.
export function compileContract(spec){
 if(!spec||!['budget_plan','attention_policy'].includes(spec.kind))throw Error('Unsupported verification adapter');
 if(!Array.isArray(spec.cases)||spec.cases.length<2||spec.cases.length>100)throw Error('Supply 2–100 independent acceptance cases');
 const cases=structuredClone(spec.cases);
 for(const c of cases){
  if(spec.kind==='budget_plan'){
   if(!Number.isFinite(c.budget)||c.budget<0||!Array.isArray(c.options)||c.options.length<2||c.options.length>30||c.options.some(o=>typeof o.id!=='string'||!Number.isFinite(o.cost)||o.cost<0||!Number.isFinite(o.utility))||new Set(c.options.map(o=>o.id)).size!==c.options.length||!c.options.some(o=>o.cost<=c.budget))throw Error('Invalid budget case');
  }else{
   if(!Array.isArray(c.choices)||c.choices.length<2||!Number.isInteger(c.expected)||!c.choices[c.expected]||c.choices.some(x=>['salience','need','affect','repeats'].some(k=>!Number.isFinite(x[k])||x[k]<0||x[k]>(k==='repeats'?8:1))))throw Error('Invalid attention case');
  }
 }
 const content={schema:'goal-contract-12.1',kind:spec.kind,cases};return {...content,hash:sha256(content)};
}
export function verifyArtifact(contract,artifact){
 const compiled=compileContract(contract);if(compiled.hash!==contract.hash)throw Error('Verification contract hash mismatch');
 let results;
 if(contract.kind==='budget_plan'){
  if(!Array.isArray(artifact?.decisions)||artifact.decisions.length!==contract.cases.length)throw Error('One decision per acceptance case is required');
  results=contract.cases.map((c,i)=>{const feasible=c.options.filter(o=>o.cost<=c.budget),best=Math.max(...feasible.map(o=>o.utility)),choice=c.options.find(o=>o.id===artifact.decisions[i]);return {case:i,pass:!!choice&&choice.cost<=c.budget&&choice.utility===best,actual:artifact.decisions[i]};});
 }else{
  const program=compilePolicy(artifact?.program);
  results=contract.cases.map((c,i)=>{const actual=c.choices.map((x,j)=>({j,s:evaluatePolicy(program,x)})).sort((a,b)=>b.s-a.s||a.j-b.j)[0].j;return {case:i,actual,pass:actual===c.expected};});
 }
 const content={adapter:contract.kind,contract_hash:contract.hash,artifact_hash:sha256(artifact),results,pass:results.every(x=>x.pass),provenance:'deterministic_adapter_execution'};
 return {...content,evidence_hash:sha256(content)};
}

export function applyVerifiedProgress(intention,artifact,tick){
 if(!intention.verification_contract)throw Error('No acceptance contract is registered for this step');
 if(intention.verification_step!==intention.step)throw Error('Acceptance contract belongs to another step');
 const result=verifyArtifact(intention.verification_contract,artifact);
 const entry={...result,step:intention.step,tick};
 // At most one dedicated feedback turn per acceptance contract. Further work
 // returns to ordinary recurrence/backoff, rather than an unbounded retry loop.
 if(!result.pass&&!intention.repair_turn_used)intention.repair_pending=true;
 intention.verification_history=[...(intention.verification_history||[]),entry].slice(-100);
 if(result.pass){
  intention.step=Math.min(intention.step+1,intention.steps.length);
  intention.verified_revision=(intention.verified_revision||0)+1;
  intention.status=intention.step===intention.steps.length?'completed':'active';
  intention.last_verified_evidence=result.evidence_hash;
  delete intention.verification_contract;delete intention.verification_step;
  delete intention.repair_pending;delete intention.repair_turn_used;
 }
 return entry;
}
