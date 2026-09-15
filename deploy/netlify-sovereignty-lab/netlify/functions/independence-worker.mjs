import { getStore } from '@netlify/blobs';
import { authorised, deepSeek } from './api.mjs';
import { createIndependence, RELEASE } from './lib/independence.mjs';

// One cursor per invocation. Host retries carry the same revision and cannot repeat a committed call.
export function workerHandler({storeFactory=getStore,complete=deepSeek}={}) {
  return async request => {
    if(!authorised(request))return new Response('Unauthorized',{status:401});
    const {id,revision}=await request.json();
    const store=storeFactory({name:'godelos-sovereignty',consistency:'strong'});
    try {
      const c=await createIndependence({store,complete}).advance(id,revision);
      await store.setJSON('independence/v6/worker',{release:RELEASE,last_step_at:new Date().toISOString(),campaign_id:id,status:c.status,revision:c.revision});
    }catch(e){
      await store.setJSON('independence/v6/worker',{release:RELEASE,last_step_at:new Date().toISOString(),campaign_id:id,status:'error',error:e.message});
      // Do not throw a provider failure into Netlify's automatic retry path.
    }
  };
}
export default workerHandler();
export const config={background:true};
