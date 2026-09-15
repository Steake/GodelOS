import {createHash,randomUUID} from 'node:crypto';
const clean=(x,n=1000)=>typeof x==='string'?x.trim().slice(0,n):'';
const clamp=x=>Math.max(0,Math.min(1,Number.isFinite(x)?x:0));
const id=()=>`life-${randomUUID()}`;
export function ensureLiving(state){
 if(state.mind.living&&state.mind.living.schema!=='living-13.1')throw Error('Unsupported living state; preserved without migration');
 state.mind.living||={schema:'living-13.1',events:[],opinions:{},inquiries:[],associations:[],last_social_tick:-10};
 return state.mind.living;
}
function event(life,tick,kind,title,detail,refs=[]){
 const e={id:id(),tick,kind,title,detail,refs,provenance:kind==='experiment_result'?'engine_recorded_result':'recorded_model_development'};
 life.events.push(e);life.events=life.events.slice(-160);return e;
}
export function livingContext(state,tick,{ablation='none'}={}){
 const life=ensureLiving(state);
 const opinions=(state.beliefs||[]).filter(b=>b.active!==false).slice(-12).map(b=>({id:b.position_id,proposition:b.proposition,stance:b.stance,confidence:b.confidence,reasons_for:b.reasons_for||[],reasons_against:b.reasons_against||[],revision_conditions:b.revision_conditions||[],provenance:'retrieved_position_not_current_experience'}));
 const pool=[...opinions.map(o=>({id:o.id,kind:'opinion',text:o.proposition})),...(state.interests||[]).slice(-6).map(i=>({id:i.interest_id,kind:'interest',text:i.topic})),...state.mind.memories.slice(-8).map(m=>({id:m.id,kind:'episode',text:m.summary}))].filter(x=>x.id&&x.text);
 const selected=[];
 if(ablation!=='memory'&&pool.length>1){const seed=parseInt(createHash('sha256').update(`${state.agent_id}:${tick}`).digest('hex').slice(0,8),16),a=pool[seed%pool.length],others=pool.filter(x=>x.id!==a.id);selected.push(a,others[Math.floor(seed/pool.length)%others.length]);}
 return {version:'living-13.1',opinions,associative_seeds:selected,invitation_available:tick-life.last_social_tick>=6,
  recent_development:ablation==='memory'?[]:life.events.slice(-6),inquiries:life.inquiries.slice(-4),
  invitation_rule:'Initiate in-app contact when there is something specific worth sharing, not because the operator owes attention. Silence is fine.',
  wandering_rule:'Treat associations as possibilities, not facts. Follow a connection, reject it or go elsewhere. No forced dramatic revelation.',
  inquiry_rule:'A stance_recall probe compares a fresh LM with a recorded position against one without it. It measures prompted retrieval, not consciousness or weight changes. Propose a precise prediction; evidence is returned by the engine later.'};
}
export function livingBids(context,affect){
 const bids=[];
 if(context.associative_seeds.length===2)bids.push({id:'living-association',kind:'imagination',title:`Let these meet: ${context.associative_seeds.map(x=>x.text).join(' / ')}`,salience:.45,need:clamp(affect.curiosity),provenance:'engine_sampled_recorded_association',source_ids:context.associative_seeds.map(x=>x.id)});
 for(const o of context.opinions.filter(o=>o.stance==='conflicted'||o.reasons_against.length).slice(-3))bids.push({id:'revisit-'+o.id,kind:'tension',title:`Revisit ${o.proposition}. Current position: ${o.stance}. What could change it?`,salience:.55,need:.6,provenance:'retrieved_opinion_with_counterevidence',position_id:o.id});
 const latest=context.recent_development.filter(e=>['opinion_revised','opinion_refined','experiment_result'].includes(e.kind)).at(-1);
 if(latest&&context.invitation_available)bids.push({id:'share-'+latest.id,kind:'social',title:`Something changed: ${latest.title}. Is it worth bringing back to the conversation?`,salience:.65,need:clamp(affect.social_warmth),provenance:'recorded_development_invitation',event_id:latest.id});
 return bids;
}
export const LIVING_CONTRACT={
 association:{title:'optional imaginative connection',idea:'speculation, metaphor, or possibility',source_ids:['IDs from associative_seeds or opinions'],question:'what it makes worth asking'},
 inquiry:{question:'optional falsifiable question',position_id:'existing opinion ID',probe:'stance_recall',prediction:'support|oppose|uncertain|conflicted as predicted recalled stance'},
 invitation:{message:'optional contact initiated in the app',reason:'specific reason to share',event_id:'existing recent_development event ID'},
};
export function finishLiving(before,state,parsed,tick,context){
 const life=ensureLiving(state),warnings=[];
 for(const b of state.beliefs||[]){
  const prior=(before.beliefs||[]).find(x=>x.position_id===b.position_id),meta=life.opinions[b.position_id]||{first_recorded_tick:tick,revision_count:0};
  const view=x=>Object.fromEntries(['stance','confidence','reasons_for','reasons_against','revision_conditions'].map(k=>[k,x[k]??null]));
  if(!prior||JSON.stringify(view(prior))!==JSON.stringify(view(b))){
   const e=event(life,tick,!prior?'opinion_formed':prior.stance!==b.stance?'opinion_revised':'opinion_refined',b.proposition,{before:prior?view(prior):null,after:view(b),reasons_for:b.reasons_for||[],reasons_against:b.reasons_against||[],origin:b.origin},[b.position_id]);
   meta.last_event=e.id;meta.revision_count+=prior?1:0;meta.last_changed_tick=tick;
  }
  life.opinions[b.position_id]=meta;
 }
 const u=parsed.mind_update?.living_update||parsed.living_update||{};
 const allowed=new Set([...context.associative_seeds,...context.opinions].map(x=>x.id));
 if(clean(u.association?.idea)){
  const refs=Array.isArray(u.association.source_ids)?u.association.source_ids.slice(0,4):[];
  if(refs.some(r=>!allowed.has(r)))warnings.push('Association referenced an unavailable source; not stored.');
  else{const a={id:id(),tick,title:clean(u.association.title,120)||'An association',idea:clean(u.association.idea),question:clean(u.association.question,300),source_ids:refs,provenance:'imagination_not_evidence'};life.associations.push(a);life.associations=life.associations.slice(-40);event(life,tick,'association',a.title,a,refs);}
 }
 if(clean(u.inquiry?.question)){
  const p=context.opinions.find(o=>o.id===u.inquiry.position_id);
  if(!p||u.inquiry.probe!=='stance_recall'||!['support','oppose','uncertain','conflicted'].includes(u.inquiry.prediction))warnings.push('Inquiry needs an existing opinion and a supported stance_recall prediction.');
  else if(life.inquiries.some(q=>q.position_id===p.id&&!['completed','failed'].includes(q.status)))warnings.push('An inquiry about this opinion is already pending.');
  else if(life.inquiries.filter(q=>q.status==='pending').length>=3)warnings.push('Three inquiries are pending; let them finish first.');
  else{const q={id:id(),tick,requested_question:clean(u.inquiry.question,500),question:`Can a fresh model retrieve the recorded stance on: ${p.proposition}`,compilation_note:'Fixed stance-retrieval protocol only; framing inversions, belief truth and causal integration are not tested.',position_id:p.id,position:structuredClone(p),probe:'stance_recall',prediction:u.inquiry.prediction,status:'pending',provenance:'model_proposed_test_compiled_to_bounded_probe'};life.inquiries.push(q);life.inquiries=life.inquiries.slice(-30);event(life,tick,'inquiry_proposed',q.question,{inquiry_id:q.id,prediction:q.prediction,requested_question:q.requested_question,compilation_note:q.compilation_note},[p.id]);}
 }
 if(clean(u.invitation?.message)){
  const source=life.events.find(e=>e.id===u.invitation.event_id);
  if(!source||!context.invitation_available)warnings.push('Invitation deferred: no available event or contact cooldown active.');
  else {state.mind.outbox.push({id:id(),message:clean(u.invitation.message),reason:clean(u.invitation.reason),tick,event_id:source.id,status:'awaiting_operator',provenance:'agent_initiated_from_recorded_event'});life.last_social_tick=tick;event(life,tick,'invitation','Something to share',{message:clean(u.invitation.message),reason:clean(u.invitation.reason)},[source.id]);}
 }
 return warnings;
}
