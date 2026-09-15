import {getStore} from '@netlify/blobs';
import {randomUUID} from 'node:crypto';
import {createHandler} from './api.mjs';

export function autonomyScheduler({storeFactory=getStore,send=fetch,clock=()=>Date.now()}={}) {
  return async () => {
    if(process.env.AUTONOMY_ENABLED!=='true'||!process.env.DEEPSEEK_API_KEY||!process.env.SOVEREIGNTY_ACCESS_TOKEN||!process.env.URL)return;
    const interval=Math.max(15,Number(process.env.AUTONOMY_INTERVAL_MINUTES||15))*60000;
    const store=storeFactory({name:'godelos-sovereignty',consistency:'strong'});
    if((await store.getWithMetadata('mind/v8/settings',{type:'json'}))?.data.paused)return;
    const key='autonomy/v1/status',entry=await store.getWithMetadata(key,{type:'json'}),status=entry?.data||{};
    if(status.state==='running') {
      if(status.lease_expires_at<=clock())await store.setJSON(key,{...status,state:'outcome_unknown',blocked:true,updated_at:new Date(clock()).toISOString()},{onlyIfMatch:entry.etag});
      return;
    }
    if(status.blocked){
      // Reconcile the old reservation, then let a future tick start a fresh episode.
      // Never replay the original provider request.
      if(!['failed','outcome_unknown'].includes(status.state))return;
      if((status.lease_expires_at||0)>clock())return;
      const handler=createHandler({storeFactory:()=>store});
      const response=await handler(new Request('https://autonomous-cycle.invalid/api/mind/recover',{method:'POST',headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({request_id:'auto-'+status.nonce})}));
      if(!response.ok)return;
      await store.setJSON('autonomy/v1/recovery/'+status.nonce,{previous:status,at:new Date(clock()).toISOString(),automatic:true,provider_call_repeated:false},{onlyIfNew:true});
      await store.setJSON(key,{...status,state:'recovering',blocked:false,last_completed_at:new Date(clock()).toISOString(),next_retry_at:new Date(clock()+interval).toISOString()},{onlyIfMatch:entry.etag});
      return;
    }
    if(status.next_retry_at&&Date.parse(status.next_retry_at)>clock())return;
    const prior=status.last_completed_at||status.dispatched_at||null;
    const last=prior?Date.parse(prior):null;
    if(last!==null&&Number.isFinite(last)&&clock()-last<interval)return;
    const nonce=randomUUID(),next={...status,state:'dispatched',nonce,dispatched_at:new Date(clock()).toISOString(),blocked:false};
    const saved=await store.setJSON(key,next,{...(entry?{onlyIfMatch:entry.etag}:{onlyIfNew:true})});if(!saved.modified)return;
    try {
      const response=await send(new URL('/.netlify/functions/autonomy-worker',process.env.URL),{method:'POST',headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({nonce}),signal:AbortSignal.timeout(10000)});
      await store.setJSON('autonomy/v1/dispatch-log/'+nonce,{nonce,http_status:response.status,at:new Date(clock()).toISOString()},{onlyIfNew:true});
    } catch(error) {
      await store.setJSON('autonomy/v1/dispatch-log/'+nonce,{nonce,error:String(error.message),at:new Date(clock()).toISOString()},{onlyIfNew:true});
      // Delivery may have succeeded: preserve a worker's newer lease or outcome.
      const current=await store.getWithMetadata(key,{type:'json'});
      if(current?.data.nonce===nonce&&current.data.state==='dispatched')await store.setJSON(key,{...current.data,state:'dispatch_failed',last_error:'Background dispatch was not acknowledged; next scheduled dispatch will recheck state.'},{onlyIfMatch:current.etag});
    }
  };
}
export default autonomyScheduler();
export const config={schedule:'*/15 * * * *'};
