// Recurrence management is outside the mutable scoring policy. A high or low
// experimental score cannot erase commitments or monopolise their service lane.
export const ATTENTION_POLICY={version:'recurrence-1',goal_lane_every:2,max_backoff:16};
export function ensureAttention(mind){
 mind.attention_control||={version:ATTENTION_POLICY.version,idle_cycles:0,visits:[]};
 return mind.attention_control;
}
function sameTopic(a,b){
 const tokens=x=>new Set(String(x||'').toLowerCase().match(/[a-z]{4,}/g)||[]),x=tokens(a),y=tokens(b);
 const intersection=[...x].filter(t=>y.has(t)).length;
 return x.size>2&&y.size>2&&intersection/(x.size+y.size-intersection)>.7;
}
function recordFor(control,candidate){
 return control.visits.find(v=>v.id===candidate.id)||(!candidate.intention_id?control.visits.slice().reverse().find(v=>!v.intention_id&&v.kind===candidate.kind&&sameTopic(v.title,candidate.title)):null);
}
function signature(intention){return intention?JSON.stringify([intention.verified_revision||0,intention.external_evidence_digest||null]):null;}

export function recurrence(mind,candidate,legacyRepeats=0){
 const control=ensureAttention(mind),visit=recordFor(control,candidate);
 const intention=candidate.intention_id?mind.intentions.find(i=>i.id===candidate.intention_id):null;
 const changed=!!intention&&!!visit&&signature(intention)!==visit.step_signature;
 const stalls=changed?0:visit?.stalls??(intention?0:legacyRepeats);
 return {kind:intention?(intention.status==='blocked'?'blocked_commitment':'active_commitment'):'exploration',
  stagnant_visits:stalls,eligible:!!intention?.repair_pending||changed||!visit||control.idle_cycles>=visit.retry_after,
  repair_pending:!!intention?.repair_pending,
  retry_after:changed?control.idle_cycles:visit?.retry_after??control.idle_cycles,
  last_served:visit?.idle_cycle??-1,progress_changed:changed,
  reason:changed?'Recorded step changed; revisit':stalls>=2?'No recorded step progress; reconsider the method':intention?'Unresolved commitment remains scheduled':'Competitive exploration'};
}

export function selectAttention(mind,bids,input={}){
 const control=ensureAttention(mind);
 if(input.message)return {focus:bids.find(c=>c.kind==='perception'),reason:'operator_priority'};
 const eligible=bids.filter(c=>c.recurrence.eligible),goals=eligible.filter(c=>c.intention_id);
 // Least recently served is ahead of the score, preventing goal starvation.
 goals.sort((a,b)=>Number(b.recurrence.repair_pending)-Number(a.recurrence.repair_pending)||a.recurrence.last_served-b.recurrence.last_served||b.salience-a.salience||a.id.localeCompare(b.id));
 const exploration=eligible.filter(c=>!c.intention_id);
 const goalSlot=control.idle_cycles%ATTENTION_POLICY.goal_lane_every===0;
 let focus=goalSlot&&goals.length?goals[0]:exploration[0]||goals[0];
 if(!focus)focus=bids.find(c=>c.id==='open-reverie')||bids[0];
 const reason=focus.intention_id?'scheduled_commitment':eligible.includes(focus)?'competitive_exploration':'scaffold_fallback';
 if(focus.intention_id&&(focus.recurrence.kind==='blocked_commitment'||focus.recurrence.stagnant_visits>=2))
  focus={...focus,title:`Review the blocker or change the method, rather than repeat the same attempt: ${focus.title}`,attention_action:'replan'};
 else focus={...focus,attention_action:focus.intention_id?'advance_or_test':'explore'};
 return {focus,reason};
}

export function commitAttention(mind,prepared){
 const control=ensureAttention(mind);
 if(prepared.input.message||prepared.ablation==='workspace')return;
 const focus=prepared.workspace.focus,old=recordFor(control,focus);
 const intention=focus.intention_id?mind.intentions.find(i=>i.id===focus.intention_id):null;
 const before=prepared.state.mind.intentions.find(i=>i.id===focus.intention_id);
 if(intention&&before?.repair_pending){intention.repair_pending=false;intention.repair_turn_used=true;}
 const advanced=!!intention&&!!before&&(intention.verified_revision||0)>(before.verified_revision||0);
 const stalls=advanced?0:(focus.recurrence?.progress_changed?0:old?.stalls||0)+1;
 const idle_cycle=control.idle_cycles;
 // A claimed new reason, renamed goal or priority change is not step progress.
 const delay=advanced?1:Math.min(ATTENTION_POLICY.max_backoff,2**Math.min(stalls,4));
 const visit={id:focus.id,intention_id:focus.intention_id||null,kind:focus.kind,title:focus.title,idle_cycle,stalls,retry_after:idle_cycle+delay,step_signature:signature(intention),
  progress:advanced?'verified_step_advance':'no_verified_step_advance',provenance:'engine_observed_state_delta'};
 control.visits=control.visits.filter(v=>v.id!==focus.id&&v.id!==old?.id);control.visits.push(visit);
 // Preserve all live intention service records; bound expendable topic records.
 const activeIds=new Set(mind.intentions.filter(i=>['active','blocked'].includes(i.status)).map(i=>i.id));
 control.visits=[...control.visits.filter(v=>activeIds.has(v.id)),...control.visits.filter(v=>!activeIds.has(v.id)).slice(-140)];
 control.idle_cycles++;
}
