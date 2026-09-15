export async function autonomyStatus(store,record,clock=Date.now){
 const day=new Date(clock()).toISOString().slice(0,10),[entry,quota]=await Promise.all(['autonomy/v1/status','autonomy/v1/usage/'+day].map(k=>store.getWithMetadata(k,{type:'json'}))),status=entry?.data||null,interval=Math.max(15,Number(process.env.AUTONOMY_INTERVAL_MINUTES||15)),last=status?.last_completed_at||status?.dispatched_at;
 return {enabled:process.env.AUTONOMY_ENABLED==='true',interval_minutes:interval,daily_limit:Math.max(1,Number(process.env.AUTONOMY_DAILY_CALL_LIMIT||24)),used_today:quota?.data.calls||0,total_call_limit:Math.max(1,Number(process.env.SOVEREIGNTY_DAILY_CALL_LIMIT||250)),total_calls_today:record.usage?.day===day?record.usage.calls:0,next_eligible_at:last?new Date(Date.parse(last)+interval*60000).toISOString():null,status};
}
export async function recoverAutonomy(store,nonce,clock=Date.now){
 const key='autonomy/v1/status',entry=await store.getWithMetadata(key,{type:'json'});
 if(!entry?.data.blocked)return {status:'no_blocked_worker'};
 if(entry.data.nonce!==nonce)throw Object.assign(Error('Worker changed; refresh before recovery.'),{status:409});
 if(entry.data.state==='running'&&entry.data.lease_expires_at>clock())throw Object.assign(Error('The worker is still running.'),{status:409});
 const next={...entry.data,state:'recovered',blocked:false,last_error:null,last_completed_at:new Date(clock()).toISOString()};
 await store.setJSON('autonomy/v1/recovery/'+nonce,{nonce,previous:entry.data,at:next.last_completed_at,provider_call_repeated:false},{onlyIfNew:true});
 if(!(await store.setJSON(key,next,{onlyIfMatch:entry.etag})).modified)throw Object.assign(Error('Concurrent worker update.'),{status:409});return {status:'recovered',provider_call_repeated:false};
}
