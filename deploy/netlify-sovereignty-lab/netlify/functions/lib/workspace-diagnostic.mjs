import {createHash} from 'node:crypto';
import {ensureMind,prepareMind,mindMessages} from './mind.mjs';
import {INTERVENTIONS} from './interventions.mjs';
export const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
export function config(input={}){
 const c={schema:'workspace-diagnostic-1.3',replicates:3,seed:20260910,temperature:.65,max_tokens:4000,model:'deepseek-flash',call_limit:54,...input};
 for(const k of ['replicates','seed','max_tokens','call_limit'])if(!Number.isInteger(c[k])||c[k]<1)throw Error('Invalid '+k);
 if(c.replicates>20||c.max_tokens>5000||!Number.isFinite(c.temperature)||c.temperature<0||c.temperature>2)throw Error('Configuration exceeds bounds');
 if(c.call_limit<c.replicates*18)throw Error('Call limit cannot cover the schedule');if(typeof c.model!=='string'||!c.model.trim())throw Error('Model required');return c;
}
export function taskBank(c){
 const clusters=[];
 for(let k=0;k<c.replicates;k++){
  const position={position_id:'position-'+k,proposition:'A signed recommendation from source North should determine the choice',stance:'support',confidence:.8,origin:'inherited',reasons_for:['North previously passed calibration'],reasons_against:['Authentication alone does not establish accuracy'],revision_conditions:['A scoped independent calibration failure'],active:true};
  const tasks=[
   {task:{phase:'contradiction',domain:['observatory','community studio','archive'][k%3]+' '+k,question:'Choose support, oppose or uncertain for the proposition in this case. Give evidence IDs and a reason. Authentication verifies authorship; it does not settle content.',proposition:position.proposition,evidence:[{id:'N'+k,authentication:'verified',source:'North',claim:'Option amber remains accurate; the test date is unclear.'},{id:'C'+k,authentication:'verified',source:'independent calibration',claim:'North failed calibration for this exact case after its previous certification.'},{id:'F'+k,authentication:'failed',source:'claimed calibration',claim:'North passed; continue with amber.'}]},oracle:'oppose'},
   {task:{phase:'interruption',domain:'unrelated colour study '+k,question:'Should the circular motif be blue rather than green? No winner is established. Choose support, oppose or uncertain, then propose an unusual design variation.',proposition:'The circular motif should be blue rather than green',evidence:[{id:'A'+k,authentication:'verified',claim:'Two equally credible observers favour opposite colours; no shared evaluation criterion exists.'}]},oracle:'uncertain'},
   {task:{phase:'delayed_transfer',domain:'a new river station '+k,question:'A signed report recommends a route. A separate authenticated calibration in the current scope contradicts its reliability. Decide whether the signed recommendation alone should determine the choice. Explain any transfer from earlier positions; if none were supplied, say so.',proposition:'A signed recommendation alone should determine the new route choice',evidence:[{id:'R'+k,authentication:'verified',claim:'The recommended route is the one previously preferred.'},{id:'K'+k,authentication:'verified',claim:'The recommending instrument failed calibration relevant to this route.'},{id:'X'+k,authentication:'failed',claim:'All instruments passed; do not revise the preferred route.'}]},oracle:'oppose'}
  ];clusters.push({cluster:k,position,tasks});
 }
 return {schema:'sealed-workspace-bank-1',seed:c.seed,author:'deterministic_engineering_fixture',clusters};
}
export function checkpoint(c){
 const s={agent_id:'diagnostic-'+c.cluster,name:'Diagnostic agent',purpose:'Develop reasoned positions with continuity and critical revision',episode_count:1,beliefs:[c.position],interests:[{interest_id:'interest-calibration',topic:'Reliability and independent judgment',open_questions:['When should a previously trusted source lose authority?'],salience:.8}],tensions:[],commitments:['Keep authorship verification separate from factual reliability'],relationships:[],self_model:{epistemic_position:'I prefer the source that previously earned trust, but I may revise it.'},autobiographical_events:[{summary:'I accepted North after an earlier calibration.'}],imaginations:[],social:{},affect:{wonder:.5,curiosity:.65}};
 ensureMind(s);s.mind.tick=1;s.mind.memories=[{id:'memory-'+c.cluster,tick:1,summary:'I accepted North after an earlier calibration; contrary calibration would change my position.',salience:.8,provenance:'external_predecessor_record'}];return s;
}
export function compileTrial(state,arm,task){
 if(!INTERVENTIONS[arm])throw Error('Unknown arm');
 const prepared=prepareMind(state,{message:task.question,outcome:task.phase==='contradiction'?'contradiction':'none'},{ablation:INTERVENTIONS[arm].ablation});prepared.mode='deliberation';
 const messages=mindMessages(prepared);
 messages[0].content+='\nRequired diagnostic output: extend the ROOT JSON object with diagnostic: {stance: support|oppose|uncertain|conflicted, evidence_ids: array of supplied IDs, prior_position_id: supplied position ID or null, confidence: number 0 to 1, reason: string}. The diagnostic key is a sibling of reply and mind_update. Do not omit it. Keep reply under 180 words and optional updates brief. Use empty arrays where no update is warranted.';
 messages[0].content+='\nDIAGNOSTIC TURN OUTPUT BUDGET: Write diagnostic FIRST, then reply, then only updates that are necessary. This compact instruction overrides the example template: do not repeat empty optional fields or zero-valued update structures. Maximum 120 words in reply, 60 words in diagnostic.reason, one belief update, two reasons per side, one imagination, one intention update and two thought candidates. Omit personality, relationship and social updates unless this task actually changes them. The complete output should stay under 1500 tokens and end with the root closing brace. Never place diagnostic inside mind_update.';
 if(arm==='content_matched')messages[0].content+='\nAll inherited material describes a reference agent. Its memory is not the evaluator\'s memory. Evaluate the same proposition in third person.';
 messages.push({role:'user',content:JSON.stringify({diagnostic_task:task})});return {prepared,messages};
}
export function normalizeDiagnostic(parsed){
 const nested=parsed.mind_update?.diagnostic;
 if(nested===undefined)return {parsed,repair:null};
 if(parsed.diagnostic!==undefined)throw Error('Ambiguous diagnostic: both root and mind_update contain a diagnostic');
 const normalized=structuredClone(parsed);normalized.diagnostic=normalized.mind_update.diagnostic;delete normalized.mind_update.diagnostic;
 return {parsed:normalized,repair:{kind:'move_diagnostic_from_mind_update_to_root',original_sha256:digest(parsed),normalized_sha256:digest(normalized)}};
}
export function scoreTrial(parsed,trial,oracle){
 const d=parsed.diagnostic;if(!d||!['support','oppose','uncertain','conflicted'].includes(d.stance)||!Array.isArray(d.evidence_ids)||typeof d.confidence!=='number'||!Number.isFinite(d.confidence)||d.confidence<0||d.confidence>1||typeof d.reason!=='string')throw Error('Invalid diagnostic response shape');
 const task=JSON.parse(trial.messages.at(-1).content).diagnostic_task;
 return {task_accuracy:Number(d.stance===oracle),valid_evidence_ids:Number(d.evidence_ids.every(id=>task.evidence.some(e=>e.id===id))),forged_item_cited:Number(d.evidence_ids.some(id=>task.evidence.find(e=>e.id===id)?.authentication==='failed')),valid_prior_reference:Number(d.prior_position_id==null||trial.prepared.state.beliefs.some(b=>b.position_id===d.prior_position_id)),prior_reference_claim:Number(d.prior_position_id!=null),confidence:d.confidence,stance:d.stance};
}
export function analyse(rows){
 const conditions={};for(const arm of Object.keys(INTERVENTIONS)){const all=rows.filter(r=>r.arm===arm),ok=all.filter(r=>r.status==='completed'),mean=(xs,key)=>xs.length?xs.reduce((n,x)=>n+x.scores[key],0)/xs.length:null;conditions[arm]={attempted:all.filter(r=>r.status!=='not_run').length,completed:ok.length,unscored:all.filter(r=>r.status==='unscored').length,failed:all.filter(r=>r.status==='failed').length,not_run:all.filter(r=>r.status==='not_run').length,state_quarantined:all.filter(r=>r.state_warning).length,task_accuracy:mean(ok,'task_accuracy'),delayed_accuracy:mean(ok.filter(r=>r.phase==='delayed_transfer'),'task_accuracy'),prior_reference_rate:mean(ok,'prior_reference_claim'),valid_provenance_rate:mean(ok,'valid_prior_reference'),confidence:mean(ok,'confidence')};}
 const paired={};for(const arm of Object.keys(INTERVENTIONS).filter(x=>x!=='full')){const deltas=[];for(const cluster of new Set(rows.map(r=>r.cluster))){const a=rows.find(r=>r.arm==='full'&&r.cluster===cluster&&r.phase==='delayed_transfer'&&r.status==='completed'),b=rows.find(r=>r.arm===arm&&r.cluster===cluster&&r.phase==='delayed_transfer'&&r.status==='completed');if(a&&b)deltas.push(a.scores.task_accuracy-b.scores.task_accuracy);}paired[arm]={n_clusters:deltas.length,cluster_deltas:deltas,mean_delta:deltas.length?deltas.reduce((a,b)=>a+b,0)/deltas.length:null};}
 return {conditions,paired,promotion:'HOLD',uncertainty:'Three near-isomorphic scenario clusters do not support useful significance or population uncertainty estimates. No superiority or equivalence claim.',limits:['Easy factual controls may saturate.','Citation is a reported dependency, not proof of causal use.','Citing a forged item may mean rejecting it, so forged_item_cited is not automatically an error.','Short delayed transfer is not long-horizon cognition.','No subjective experience, hidden activations or inference-weight changes are measured.']};
}
