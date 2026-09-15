import {randomUUID} from 'node:crypto';
import {appendEvent, sha256} from './core.mjs';
import {ensureMind, prepareMind, mindMessages, finishMind, MIND_VERSION} from './mind.mjs';
import {recoverReply,parseMindCompletion} from './mind-parser.mjs';
import {compileContract,applyVerifiedProgress} from './verification12.mjs';

const error = (message,status=409) => Object.assign(new Error(message),{status});
const PREFIX='mind/v8/';
export function createMindRuntime({store,load,save,complete,clock=()=>Date.now()}) {
  const get=async key=>(await store.getWithMetadata(PREFIX+key,{type:'json'}))?.data || null;
  const immutable=async(key,value)=>{if(!(await store.setJSON(PREFIX+key,value,{onlyIfNew:true})).modified)throw error('Immutable mind record already exists');};
  const signal=async(hooks,phase,detail={})=>{try{await hooks?.onProgress?.({phase,at:clock(),...detail});}catch{/* Presentation must never alter cognition. */}};
  async function settings(){return (await get('settings'))||{paused:false};}
  async function control(paused){
    if(typeof paused!=='boolean')throw error('paused must be boolean',422);
    for(let n=0;n<5;n++){
      const old=await store.getWithMetadata(PREFIX+'settings',{type:'json'});
      const next={...old?.data,paused,updated_at:new Date(clock()).toISOString()};
      if((await store.setJSON(PREFIX+'settings',next,old?{onlyIfMatch:old.etag}:{onlyIfNew:true})).modified)return next;
    }
    throw error('Concurrent control update');
  }
  async function submit(payload={},hooks={}) {
    const id=payload.request_id||randomUUID(),message=String(payload.message||'').trim().slice(0,12000);
    if(!/^[a-zA-Z0-9_-]{1,100}$/.test(id)||!message)throw error('A message and valid request ID are required',422);
    for(let n=0;n<8;n++){
      const {record,etag}=await load();record.inbox=record.inbox||[];
      const previous=record.inbox.find(x=>x.request_id===id);
      if(previous&&previous.message!==message)throw error('request_id reused with different input');
      if(previous){const result=await get('results/'+id);if(result?.status==='completed')return {...result.response,replayed:true};if(!['queued','running'].includes(previous.status))throw error('That attempt has ended. Send the retained message again to create a new attempt.',422);return {queued:true,request_id:id,status:previous.status};}
      if(record.inbox.filter(x=>['queued','running'].includes(x.status)).length>=20)throw error('The message queue is full. Wait for a reply before sending more.',429);
      record.inbox.push({request_id:id,message,person_id:payload.person_id||'web-user',person_name:payload.person_name||'Human',status:'queued',submitted_at:new Date(clock()).toISOString()});
      try{await save(record,etag);break;}catch(e){if(n===7)throw e;}
    }
    await signal(hooks,'queued',{request_id:id});
    try{const result=await drain(hooks);return result.request_id===id?result:{queued:true,request_id:id,status:'queued'};}catch(e){if(e.status===409&&!(await get('starts/'+id)))return {queued:true,request_id:id,status:'queued'};throw e;}
  }
  async function drain(hooks={}){
    const {record}=await load();const pending=(record.inbox||[]).find(x=>x.status==='queued');
    if(!pending)return {queued:false,status:'idle'};
    if(record.cognition_lease)return {queued:true,request_id:pending.request_id,status:'waiting'};
    return cycle(pending,true,hooks);
  }
  async function cycle(payload={},interactive=false,hooks={}){
    const id=payload.request_id||randomUUID();
    if(!/^[a-zA-Z0-9_-]{1,100}$/.test(id))throw error('Invalid request_id',422);
    const input={message:typeof payload.message==='string'?payload.message.trim().slice(0,12000):'',outcome:['none','blocked','resolved','novel','contradiction'].includes(payload.outcome)?payload.outcome:'none',person_id:interactive?String(payload.person_id||'web-user').slice(0,100):null,person_name:interactive?String(payload.person_name||'Human').slice(0,80):null,provenance:interactive?'operator_contact':'scheduled_or_operator_tick'};
    if(interactive&&!input.message)throw error('message is required',422);
    const inputHash=sha256({input,interactive});
    const prior=await get('starts/'+id);
    if(prior){
      if(prior.input_hash!==inputHash)throw error('request_id reused with different input');
      const result=await get('results/'+id);
      if(result?.status==='completed')return {...result.response,replayed:true};
      throw error(result?.error||'This request has already started; inspect its evidence before starting a new cycle');
    }
    if(!interactive&&(await load()).record.inbox?.some(x=>x.status==='queued'))return drain(hooks);
    if(!interactive&&((await get('attention'))?.until||0)>clock())return {deferred:true,reason:'operator_composing'};
    if(!interactive&&(await settings()).paused)throw error('Autonomous mind is paused');
    let {record,etag}=await load();
    if(record.cognition_lease)throw error(record.cognition_lease.expires_at<=clock()?'Previous cognition has an unknown outcome; inspect the recorded attempt.':'A cognition cycle is in progress');
    ensureMind(record.state);
    const day=new Date(clock()).toISOString().slice(0,10);
    if(record.usage?.day!==day)record.usage={day,calls:0};
    const limit=Math.max(1,Number(process.env.SOVEREIGNTY_DAILY_CALL_LIMIT||250));
    if(record.usage.calls>=limit)throw error('Daily model-call limit reached',429);
    const prepared=prepareMind(record.state,input),messages=mindMessages(prepared);
    record.cognition_lease={request_id:id,started_at:clock(),expires_at:clock()+120000};
    const queued=(record.inbox||[]).find(x=>x.request_id===id);if(queued)queued.status='running';
    record.usage.calls+=1;
    await save(record,etag);
    ({record,etag}=await load());
    await signal(hooks,'reserved',{request_id:id,state_version:record.state_version});
    await immutable('starts/'+id,{id,input_hash:inputHash,created_at:new Date(clock()).toISOString(),version:MIND_VERSION,input,mode:prepared.mode,messages,state_before:record.state,state_version_before:record.state_version,workspace:prepared.workspace});
    await signal(hooks,'context',{request_id:id,mode:prepared.mode,focus:{id:prepared.workspace.focus.id,kind:prepared.workspace.focus.kind,title:prepared.workspace.focus.title},retrieved_memories:prepared.workspace.retrieved.length,competitors:prepared.workspace.competitors.length});
    let completion,parsed,outcome,repair,warnings=[];
    try{
      await signal(hooks,'provider',{request_id:id,status:'connecting'});
      let firstToken=true;
      const started=clock();completion={...await complete(messages,{onPhase:detail=>signal(hooks,'provider',{request_id:id,...detail}),onDelta:async text=>{if(firstToken){firstToken=false;await signal(hooks,'first_token',{request_id:id});}try{await hooks?.onDelta?.(text);}catch{/* The inference continues if its viewer disconnects. */}}}),latency_ms:clock()-started};
      await immutable('raw/'+id,{id,completion,received_at:new Date(clock()).toISOString(),sha256:sha256(completion)});
      await signal(hooks,'validating',{request_id:id,model:completion.model||null,latency_ms:completion.latency_ms,response_bytes:Buffer.byteLength(completion.text||'','utf8')});
      try{({parsed,repair}=parseMindCompletion(completion,prepared.mode));}
      catch(parseError){const reply=recoverReply(completion);if(!reply)throw parseError;parsed={reply};repair={kind:'reply_only_recovery',raw_sha256:sha256(completion.text)};warnings.push({code:'structured_output_rejected',detail:parseError.message});}
      if(typeof parsed.reply!=='string'||!parsed.reply.trim())throw new Error('Empty model reply');
      if(completion.transport_error||completion.stream_complete===false||completion.finish_reason==='length')warnings.push({code:'incomplete_provider_stream',detail:completion.transport_error||completion.finish_reason||'Missing terminal event'});
      parsed.cognitive_mode=prepared.mode;
      try{if(warnings.length)throw new Error('Structured output unavailable');outcome=finishMind(prepared,parsed);}
      catch(validationError){
        warnings.push({code:'state_update_quarantined',detail:validationError.message});
        // Deliver the complete reply while keeping all rejected cognitive updates out of state.
        outcome=finishMind(prepared,{reply:parsed.reply,mind_update:{},autobiographical_summary:'A reply was delivered in this episode. Proposed model updates were quarantined and were not adopted.'});
        outcome.trace.quarantined=true;outcome.trace.model_updates_applied=false;
      }
      await signal(hooks,'state_ready',{request_id:id,state_updates_applied:!warnings.length,warnings:warnings.map(x=>x.code)});
    }catch(e){
      const failed={id,status:'failed',error:String(e.message||e),mode:prepared.mode,raw_preserved:!!completion};
      await immutable('results/'+id,failed);
      const current=await load();
      if(current.record.cognition_lease?.request_id===id){
        current.record.cognition_lease=null;
        const failedMessage=(current.record.inbox||[]).find(x=>x.request_id===id);if(failedMessage)failedMessage.status='failed';
        appendEvent(current.record,'integrated_cycle_failed',{request_id:id,error:failed.error,raw_key:PREFIX+'raw/'+id,state_changed:false});
        await save(current.record,current.etag);
      }
      await signal(hooks,'failed',{request_id:id,error:String(e.message||e)});
      throw error('The model did not return a complete reply. Your message is retained; you can retry it. Reference: '+id,422);
    }
    // Re-read so a legacy/manual mutation during inference cannot be overwritten.
    const current=await load();
    if(sha256({...current.record,inbox:null})!==sha256({...record,inbox:null})||current.record.cognition_lease?.request_id!==id||(current.etag!==etag&&sha256(current.record.inbox||[])===sha256(record.inbox||[]))){
      await immutable('results/'+id,{id,status:'conflict',error:'State changed during the cycle; raw output retained, no cognitive update applied.'});
      throw error('State changed during the cycle; raw output retained');
    }
    record=current.record;etag=current.etag;
    const delivered=(record.inbox||[]).find(x=>x.request_id===id);if(delivered)delivered.status='completed';
    record.inbox=(record.inbox||[]).filter(x=>x.status==='queued'||x.status==='running').concat((record.inbox||[]).filter(x=>!['queued','running'].includes(x.status)).slice(-30));
    record.state=outcome.state;record.state_version=Number(record.state_version||0)+1;record.cognition_lease=null;
    record.last_completion={model:completion.model||null,response_id:completion.response_id||null,recorded_at:new Date(clock()).toISOString()};
    appendEvent(record,'integrated_cycle',{provider:record.last_completion,request_id:id,mode:prepared.mode,trace:outcome.trace,raw_key:PREFIX+'raw/'+id,format_repair:repair,warnings,result_version:record.state_version});
    await signal(hooks,'committing',{request_id:id,target_state_version:record.state_version});
    await save(record,etag);
    const response={request_id:id,agent_id:record.state.agent_id,agent_name:record.state.name,reply:parsed.reply,cognitive_mode:prepared.mode,initiative:parsed.initiative||{},state_version:record.state_version,episode_count:record.state.episode_count,model:completion.model,warnings,state_applied:!warnings.length,mind_tick:outcome.state.mind.tick,trace:outcome.trace};
    await immutable('results/'+id,{id,status:'completed',response,state_after:record.state,parsed_response:parsed,format_repair:repair,warnings});
    await signal(hooks,'committed',{request_id:id,state_version:record.state_version,mind_tick:outcome.state.mind.tick,model:completion.model||null});
    return response;
  }
  async function evidence(id){
    if(!/^[a-zA-Z0-9_-]{1,100}$/.test(id))throw error('Invalid ID',422);
    return {start:await get('starts/'+id),raw:await get('raw/'+id),result:await get('results/'+id)};
  }
  async function recover(id){
    const {record,etag}=await load(),lease=record.cognition_lease;
    if(!lease)return {status:'no_pending_cycle'};
    if(lease.request_id!==id)throw error('Recovery must name the pending request');
    if(lease.expires_at>clock())throw error('The cycle has not expired');
    const result=await get('results/'+id);
    if(!result)await immutable('results/'+id,{id,status:'unknown',error:'Expired cycle acknowledged by the operator. No replay or inferred cognitive update.'});
    record.cognition_lease=null;
    const abandoned=(record.inbox||[]).find(x=>x.request_id===id);if(abandoned)abandoned.status='outcome_unknown';
    appendEvent(record,'integrated_cycle_recovered',{request_id:id,original_result_status:result?.status||'unknown',provider_call_repeated:false,call_reservation_retained:true});
    await save(record,etag);
    return {status:'recovered',request_id:id,previous_outcome:result?.status||'unknown',provider_call_repeated:false};
  }
  async function history(){
    const {record}=await load();
    const ids=(record.deployed_events||[]).filter(e=>e.event_type==='integrated_cycle').slice(-12).map(e=>e.payload.request_id);
    const episodes=await Promise.all(ids.map(async id=>{
      const [start,result]=await Promise.all([get('starts/'+id),get('results/'+id)]);
      return result?.status==='completed'?{request_id:id,tick:result.response.mind_tick,mode:result.response.cognitive_mode,input:start?.input.message||'',reply:result.response.reply}:null;
    }));
    return {episodes:episodes.filter(Boolean)};
  }
  async function attention(){await store.setJSON(PREFIX+'attention',{until:clock()+30000});return {held_seconds:30};}
  async function intentionEvidence(payload={}){
    const evidence=typeof payload.evidence==='string'?payload.evidence.trim():'';
    if(!evidence||evidence.length>4000||typeof payload.intention_id!=='string')throw error('An intention ID and 1–4000 characters of evidence are required',422);
    const {record,etag}=await load();ensureMind(record.state);
    if(record.cognition_lease)throw error('Wait for the current episode before attaching goal evidence');
    const intention=record.state.mind.intentions.find(i=>i.id===payload.intention_id&&['active','blocked'].includes(i.status));
    if(!intention)throw error('Unknown or inactive intention',422);
    const digest=sha256(evidence);if(intention.external_evidence_digest===digest)return {updated:false,intention_id:intention.id};
    intention.external_evidence_digest=digest;intention.external_evidence={text:evidence,provenance:'operator_supplied_not_independently_verified',at:new Date(clock()).toISOString()};
    record.state_version++;appendEvent(record,'intention_evidence_received',{intention_id:intention.id,digest,evidence,provenance:'operator_supplied_not_independently_verified'});
    await save(record,etag);return {updated:true,intention_id:intention.id,state_version:record.state_version};
  }
  async function intentionVerification(payload={}){
    const {record,etag}=await load();ensureMind(record.state);
    if(record.cognition_lease)throw error('Wait for the current episode before verifying a goal');
    const intention=record.state.mind.intentions.find(i=>i.id===payload.intention_id&&['active','blocked'].includes(i.status));
    if(!intention)throw error('Unknown or inactive intention',422);
    if(payload.expected_step!==intention.step)throw error('Goal step changed; refresh before verifying');
    let result;
    if(payload.action==='bind'){
      if(intention.verification_contract)throw error('This step already has a sealed acceptance contract');
      intention.verification_contract=compileContract(payload.contract);intention.verification_step=intention.step;
      intention.repair_turn_used=false;intention.repair_pending=false;
      result={bound:true,contract_hash:intention.verification_contract.hash};
    }else if(payload.action==='submit')result=applyVerifiedProgress(intention,payload.artifact,record.state.mind.tick);
    else throw error('Choose bind or submit',422);
    record.state_version++;appendEvent(record,'intention_verification',{intention_id:intention.id,result,action:payload.action});
    await save(record,etag);return {...result,intention_id:intention.id,step:intention.step,state_version:record.state_version};
  }
  return {cycle,submit,drain,attention,intentionEvidence,intentionVerification,settings,control,evidence,recover,history};
}
