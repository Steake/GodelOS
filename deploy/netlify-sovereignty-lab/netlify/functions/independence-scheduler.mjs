import { getStore } from '@netlify/blobs';
import { createIndependence, RELEASE } from './lib/independence.mjs';

export function schedulerHandler({storeFactory=getStore,send=fetch,clock=()=>Date.now()}={}) {
  return async () => {
    if(!process.env.SOVEREIGNTY_ACCESS_TOKEN||!process.env.DEEPSEEK_API_KEY||!process.env.URL)return;
    const store=storeFactory({name:'godelos-sovereignty',consistency:'strong'});
    const campaigns=await createIndependence({store,complete:()=>{throw new Error('Scheduler cannot call provider')}}).list();
    const next=campaigns.filter(c=>['ready','running'].includes(c.status)&&(!c.lease||c.lease.expires_at<=clock())).sort((a,b)=>a.updated_at.localeCompare(b.updated_at))[0];
    if(!next)return;
    // Reserve the dispatch for this revision; a stale reservation becomes eligible after 3 minutes.
    const k='independence/v6/dispatch/'+next.id,entry=await store.getWithMetadata(k,{type:'json'});
    if(entry?.data.revision===next.revision&&entry.data.expires_at>clock())return;
    const saved=await store.setJSON(k,{revision:next.revision,expires_at:clock()+180000},{...(entry?{onlyIfMatch:entry.etag}:{onlyIfNew:true})});
    if(!saved.modified)return;
    const url=new URL('/.netlify/functions/independence-worker',process.env.URL);
    const response=await send(url,{method:'POST',headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({id:next.id,revision:next.revision}),signal:AbortSignal.timeout(10000)});
    await store.setJSON('independence/v6/dispatch-status',{release:RELEASE,dispatched_at:new Date(clock()).toISOString(),campaign_id:next.id,http_status:response.status});
  };
}
export default schedulerHandler();
export const config={schedule:'* * * * *'};
