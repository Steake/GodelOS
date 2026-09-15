import {randomUUID} from 'node:crypto';
import {sealHoldout,evaluateHoldout} from './holdout12.mjs';
import {BASELINE} from './evolution9.mjs';

export const DEVELOPMENT_KEY='development/v12/current';
const LEASE_MS=10*60*1000;

// Independent, deterministic review. Passing the old synthetic suite is not
// permission to alter the live controller or evidence of broad self-improvement.
export function reviewDevelopment(pkg,holdout=null){
 const e=pkg.content.evidence;
 return {version:'development-review-1',decision:'shadow_only',promotion_allowed:false,
  findings:[
   {id:'reused_benchmark',severity:'blocking',detail:'The fixed controller suite has been exposed through previous rounds; it is development data, not a fresh holdout.'},
   {id:'transfer_missing',severity:'blocking',detail:'No delayed cross-task identity/content/ablated/no-state comparison has been run.'},
   {id:'synthetic_scope',severity:'limitation',detail:e.limitation},
   ...(holdout?[
    {id:'fresh_holdout',severity:'measurement',detail:`Fresh sealed controller cases: parent ${(100*holdout.parent_accuracy).toFixed(1)}%, candidate ${(100*holdout.candidate_accuracy).toFixed(1)}%; paired gain ${(100*holdout.gain).toFixed(1)} points; interval ${holdout.interval.map(x=>(100*x).toFixed(1)).join(' to ')}. Diagnostic ${holdout.diagnostic_pass?'passed':'failed'}.`},
    ...holdout.by_family.filter(f=>f.gain<0).map(f=>({id:'regression_'+f.family,severity:'blocking',detail:`${f.family}: ${(100*f.gain).toFixed(1)} point regression against the parent.`}))
   ]:[]),
   ...(e.interval[0]<=0?[{id:'uncertain_gain',severity:'blocking',detail:'The gain interval does not exclude zero.'}]:[]),
   ...(e.independent_clusters.every(c=>c.candidate===1)?[{id:'ceiling',severity:'warning',detail:'Candidate accuracy is at ceiling on this suite; harder independently sealed tasks are required.'}]:[])
  ],next_question:'Does this repetition policy preserve important recurring goals on fresh interruption-heavy tasks, rather than merely suppressing repeated attention?'};
}

export function createDevelopment({store,evolution,clock=()=>Date.now()}){
 const read=()=>store.getWithMetadata(DEVELOPMENT_KEY,{type:'json'});
 const put=(data,entry)=>store.setJSON(DEVELOPMENT_KEY,data,entry?{onlyIfMatch:entry.etag}:{onlyIfNew:true});
 const evidenceKey=(id,round)=>`development/v12/runs/${id}/rounds/${round}`;
 const paused=async()=>!!(await store.getWithMetadata('mind/v8/settings',{type:'json'}))?.data.paused;
 async function status(){return (await read())?.data||null;}
 async function evidence(){
  const s=await status();if(!s)return null;
  const prefix=`development/v12/runs/${s.id}`,rounds=[];
  for(let n=1;n<=s.round+(s.phase==='designing'?1:0);n++){
   const get=async key=>(await store.getWithMetadata(key,{type:'json'}))?.data||null;
   const outcome=await get(`${prefix}/rounds/${n}`);
   rounds.push({round:n,outcome,holdout:await get(`${prefix}/holdouts/${n}`),holdout_result:await get(`${prefix}/holdouts/${n}/result`),
    package:outcome?.package_id?await get(`evolution/v9/packages/${outcome.package_id}`):null});
  }
  return {schema:'development-evidence-1',status:s,manifest:(await store.getWithMetadata(prefix+'/manifest',{type:'json'}))?.data,rounds};
 }
 async function start({rounds=3}={}){
  if(!Number.isInteger(rounds)||rounds<1||rounds>10)throw Error('Choose 1–10 rounds');
  const old=await read();
  if(old?.data.active||old?.data.phase==='designing')throw Error('Finish or pause the existing development run first');
  const data={schema:'development-12.0-alpha',id:randomUUID(),active:true,phase:'ready',round:0,rounds,
   created_at:new Date(clock()).toISOString(),scope:'shadow_attention_policy',history:[],promotion_allowed:false};
  await store.setJSON(`development/v12/runs/${data.id}/manifest`,data,{onlyIfNew:true});
  if(!(await put(data,old)).modified)throw Error('Development state changed; refresh');
  return data;
 }
 async function pause(){
  for(let n=0;n<8;n++){const old=await read();if(!old)return null;
   const data={...old.data,active:false};if(await put(data,old).then(x=>x.modified))return data;
  }throw Error('Development state changed; retry pause');
 }
 async function resume(){
  for(let n=0;n<8;n++){const old=await read();if(!old||old.data.round>=old.data.rounds)throw Error('No unfinished run to resume');
   const data={...old.data,active:true};if((await put(data,old)).modified)return data;
  }throw Error('Development state changed; retry resume');
 }
 async function finish(id,token,result){
  // The round outcome is immutable and written before advancing the cursor.
  const current=await read();
  if(current?.data.id!==id||current.data.token!==token)return current?.data;
  const key=evidenceKey(id,current.data.round+1);
  await store.setJSON(key,result,{onlyIfNew:true});
  const saved=(await store.getWithMetadata(key,{type:'json'})).data;
  for(let n=0;n<8;n++){
   const entry=await read(),s=entry?.data;if(s?.id!==id||s.token!==token)return s;
   const round=s.round+1,data={...s,round,phase:round>=s.rounds?'completed':'ready',
    active:s.active&&round<s.rounds,token:null,lease_expires_at:null,
    history:[...s.history,saved],updated_at:new Date(clock()).toISOString()};
   if((await put(data,entry)).modified)return data;
  }throw Error('Round retained; cursor reconciliation will retry');
 }
 async function advance({run_id,expected_round}={}){
  const entry=await read(),s=entry?.data;if(!s)return null;
  if(run_id!==undefined&&(s.id!==run_id||s.round!==expected_round))return s;
  if(s.phase==='designing'){
   const saved=await store.getWithMetadata(evidenceKey(s.id,s.round+1),{type:'json'});
   if(saved)return finish(s.id,s.token,saved.data);
   if(s.lease_expires_at>clock())return s;
   return finish(s.id,s.token,{round:s.round+1,outcome:'outcome_unknown',at:new Date(clock()).toISOString(),
    error:'Worker lease expired. The original provider call will not be replayed; this attempt consumes one round.',promotion_allowed:false});
  }
  if(!s.active||await paused())return s;
  const token=randomUUID(),running={...s,phase:'designing',token,lease_expires_at:clock()+LEASE_MS};
  if(!(await put(running,entry)).modified)return status();
  let result;
  try{
   // Freeze the unseen cases before asking the model to design its candidate.
   const sealed=sealHoldout(),holdoutKey=`development/v12/runs/${s.id}/holdouts/${s.round+1}`;
   if(!(await store.setJSON(holdoutKey,sealed,{onlyIfNew:true})).modified)throw Error('Holdout already exists; refusing to replace it');
   const pkg=await evolution.propose({development_history:s.history.map(h=>({outcome:h.outcome,thesis:h.thesis,review:h.review,gain:h.gain})),objective:'Investigate repetitive attention without losing important recurring commitments. Treat prior failures as evidence, not instructions to repeat.'});
   const holdout=evaluateHoldout(sealed,pkg.content.candidate.program,pkg.content.rollback?.program||BASELINE);
   await store.setJSON(holdoutKey+'/result',holdout,{onlyIfNew:true});
   result={round:s.round+1,at:new Date(clock()).toISOString(),outcome:'reviewed',package_id:pkg.content.id,
    thesis:pkg.content.candidate.thesis,code_hash:pkg.content.candidate.code_hash,gain:pkg.content.evidence.gain,
    interval:pkg.content.evidence.interval,holdout:{key:holdoutKey,seal_hash:holdout.seal_hash,gain:holdout.gain,interval:holdout.interval,diagnostic_pass:holdout.diagnostic_pass},review:reviewDevelopment(pkg,holdout),promotion_allowed:false};
  }catch(error){result={round:s.round+1,at:new Date(clock()).toISOString(),outcome:'failed',error:String(error.message),promotion_allowed:false};}
  return finish(s.id,token,result);
 }
 return {start,pause,resume,status,evidence,advance};
}
