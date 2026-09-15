import {getStore} from '@netlify/blobs';
import {authorised,createHandler,deepSeek} from './api.mjs';

export function autonomyWorker({storeFactory=getStore,clock=()=>Date.now(),completionProvider}={}) {
  return async request => {
    if(!authorised(request))return new Response('Unauthorized',{status:401});
    const {nonce}=await request.json(),store=storeFactory({name:'godelos-sovereignty',consistency:'strong'}),key='autonomy/v1/status';
    let entry=await store.getWithMetadata(key,{type:'json'});
    if(!entry||entry.data.nonce!==nonce||entry.data.state!=='dispatched')return;
    if((await store.getWithMetadata('mind/v8/settings',{type:'json'}))?.data.paused){await store.setJSON(key,{...entry.data,state:'paused',last_completed_at:new Date(clock()).toISOString()},{onlyIfMatch:entry.etag});return;}
    const total=Number(entry.data.total_cycles||0),mode='integrated';
    const running={...entry.data,state:'running',mode,started_at:new Date(clock()).toISOString(),lease_expires_at:clock()+120000};
    if(!(await store.setJSON(key,running,{onlyIfMatch:entry.etag})).modified)return;
    entry=await store.getWithMetadata(key,{type:'json'});
    const day=new Date(clock()).toISOString().slice(0,10),quotaKey='autonomy/v1/usage/'+day,limit=Math.max(1,Number(process.env.AUTONOMY_DAILY_CALL_LIMIT||24));
    for(let i=0;i<8;i++){
      const q=await store.getWithMetadata(quotaKey,{type:'json'}),calls=q?.data.calls||0;
      if(calls>=limit){await store.setJSON(key,{...entry.data,state:'daily_limit',last_completed_at:new Date(clock()).toISOString()},{onlyIfMatch:entry.etag});return;}
      const saved=await store.setJSON(quotaKey,{calls:calls+1},{...(q?{onlyIfMatch:q.etag}:{onlyIfNew:true})});if(saved.modified)break;
      if(i===7){await store.setJSON(key,{...entry.data,state:'deferred',blocked:false,defer_reason:'quota_contention',last_completed_at:new Date(clock()).toISOString()},{onlyIfMatch:entry.etag});return;}
    }
    let providerInvoked=false;
    try{
      const handler=createHandler({storeFactory:()=>store,completionProvider:async (messages,options)=>{providerInvoked=true;return (completionProvider||deepSeek)(messages,options);}});
      const response=await handler(new Request('https://autonomous-cycle.invalid/api/living/tick',{method:'POST',headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({request_id:'auto-'+nonce})}));
      const result=await response.json();entry=await store.getWithMetadata(key,{type:'json'});
      const deferred=result.deferred||result.queued||(!providerInvoked&&[409,429].includes(response.status)),completed=response.ok&&typeof result.reply==='string';
      await store.setJSON(key,{...running,state:deferred?'deferred':completed?'completed':'failed',blocked:false,consecutive_failures:completed?0:deferred?(running.consecutive_failures||0):(running.consecutive_failures||0)+1,next_retry_at:!completed&&!deferred?new Date(clock()+Math.min(3600000,900000*2**Math.min(2,running.consecutive_failures||0))).toISOString():null,last_completed_at:new Date(clock()).toISOString(),total_cycles:total+(completed?1:0),last_result:completed?{mode,state_version:result.state_version,reply:result.reply}:null,defer_reason:deferred?(result.reason||result.status||result.error):null,last_error:response.ok?null:(result.error||`HTTP ${response.status}`)},{onlyIfMatch:entry.etag});
    }catch(error){entry=await store.getWithMetadata(key,{type:'json'});await store.setJSON(key,{...running,state:'outcome_unknown',blocked:true,last_error:error.message},{onlyIfMatch:entry.etag});}
    finally{if(!providerInvoked)for(let i=0;i<8;i++){const q=await store.getWithMetadata(quotaKey,{type:'json'});if(!q)break;if((await store.setJSON(quotaKey,{...q.data,calls:Math.max(0,q.data.calls-1)},{onlyIfMatch:q.etag})).modified)break;}}
  };
}
export default autonomyWorker();
export const config={background:true};
