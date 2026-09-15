import {getStore} from '@netlify/blobs';
import {DEVELOPMENT_KEY} from './lib/development12.mjs';

export function developmentScheduler({storeFactory=getStore,send=fetch}={}){
 return async()=>{
  if(!process.env.DEEPSEEK_API_KEY||!process.env.SOVEREIGNTY_ACCESS_TOKEN||!process.env.URL)return;
  const store=storeFactory({name:'godelos-sovereignty',consistency:'strong'});
  const s=(await store.getWithMetadata(DEVELOPMENT_KEY,{type:'json'}))?.data;
  if(!s||(!s.active&&s.phase!=='designing'))return;
  if((await store.getWithMetadata('mind/v8/settings',{type:'json'}))?.data.paused)return;
  // An uncertain dispatch is safe to retry: the worker reserves before calling the LM.
  try{await send(new URL('/.netlify/functions/development-worker-background',process.env.URL),{
   method:'POST',headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({run_id:s.id,expected_round:s.round}),signal:AbortSignal.timeout(10000)});
  }catch{/* The next scheduled delivery reconciles the durable cursor. */}
 };
}
export default developmentScheduler();
export const config={schedule:'*/15 * * * *'};
