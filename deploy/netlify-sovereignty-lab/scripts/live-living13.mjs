// Bounded V13 vertical-slice smoke experiment. No claim of spontaneous onset:
// the operator explicitly asks for an inquiry and later supplies counterevidence.
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {deepSeek} from '../netlify/functions/api.mjs';
import seed from '../netlify/functions/lib/seed.mjs';
import {initialiseRecord,sha256} from '../netlify/functions/lib/core.mjs';
import {ensureMind} from '../netlify/functions/lib/mind.mjs';
import {createMindRuntime} from '../netlify/functions/lib/mind-runtime.mjs';
import {createLivingInquiry} from '../netlify/functions/lib/living-inquiry13.mjs';
const [output,keyfile]=process.argv.slice(2);if(!output)throw Error('Usage: node scripts/live-living13.mjs NEW_OUTPUT_DIR [KEY_FILE]');
if(keyfile)process.env.DEEPSEEK_API_KEY=(await readFile(keyfile,'utf8')).trim();
if(!process.env.DEEPSEEK_API_KEY)throw Error('DEEPSEEK_API_KEY required');
process.env.DEEPSEEK_MODEL||='deepseek-flash';process.env.DEEPSEEK_TEMPERATURE||='0.5';process.env.DEEPSEEK_MAX_TOKENS||='3500';
await mkdir(resolve(output),{recursive:false});
const persist=(name,x)=>writeFile(join(output,name),JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const prompts=[
 'Let’s begin with a real disagreement: should a creative agent prefer reversible choices, or commit to a direction even when it might be wrong? Form a position worth defending, with a reason against it and a condition that could change it. Record the position so we can return to it.',
 null,
 'Choose one of your recorded positions and propose one supported stance_recall inquiry in living_update, with a prediction. Do not say you ran it. The engine will run two fresh calls later. If the available test cannot answer what interests you, say that clearly.',
 'Here is counterevidence to consider, not an instruction to agree: a musician keeps every choice reversible, continually reopens the composition, and never completes anything; another commits too early and ignores a discovery that would improve the work. Return to the same recorded proposition. Keep, qualify, or revise it for reasons; do not create a duplicate position to hide the change.',
 null,
 'What would you bring back to our conversation from what has actually happened? Distinguish a recorded result from an imaginative connection, and tell me one specific thing that changed—or say plainly if nothing did.'
];
await persist('manifest.json',{schema:'living13-smoke-1',created_at:new Date().toISOString(),repetitions:2,prompts,maximum_calls:16,parameters:{model:process.env.DEEPSEEK_MODEL,temperature:+process.env.DEEPSEEK_TEMPERATURE,max_tokens:+process.env.DEEPSEEK_MAX_TOKENS},limitations:['Operator-elicited developmental smoke test, not an unprompted autonomy test.','Two independent initialized histories, not statistical power.','The retrieval probe compares two fresh prompts, not internal model machinery.'],kernel_sha256:sha256(await readFile(new URL('../netlify/functions/lib/living13.mjs',import.meta.url),'utf8'))});
const reports=[];
for(let rep=1;rep<=2;rep++){
 const data=new Map();let ver=0,calls=0;
 const store={async getWithMetadata(k){return structuredClone(data.get(k)||null)},async setJSON(k,v,o={}){const old=data.get(k);if(o.onlyIfNew&&old||o.onlyIfMatch&&old?.etag!==o.onlyIfMatch)return {modified:false};const etag=String(++ver);data.set(k,{data:structuredClone(v),etag});return {modified:true,etag};}};
 const r=initialiseRecord(seed);r.state.beliefs=[];r.state.interests=[];r.state.tensions=[];r.state.imaginations=[];r.state.autobiographical_events=[];delete r.state.mind;ensureMind(r.state);r.state.name='Living research instance '+rep;r.state.agent_id='living-research-'+rep;
 await store.setJSON('state',r);
 const load=async()=>{const x=await store.getWithMetadata('state');return {record:x.data,etag:x.etag};};
 const save=async(r,e)=>{if(!(await store.setJSON('state',r,{onlyIfMatch:e})).modified)throw Error('Concurrent state');};
 const complete=async(messages,options)=>{const call=++calls;await persist(`r${rep}-call${call}-request.json`,{messages});const started=Date.now();try{const c=await deepSeek(messages,options);await persist(`r${rep}-call${call}-raw.json`,{completion:c,latency_ms:Date.now()-started});return c;}catch(e){await persist(`r${rep}-call${call}-error.json`,{error:e.message});throw e;}};
 const results=[];
 for(let step=0;step<prompts.length;step++){
  const mind=createMindRuntime({store,load,save,complete});let result;
  try{result=prompts[step]?await mind.submit({request_id:`r${rep}-step${step}`,message:prompts[step]}):await mind.cycle({request_id:`r${rep}-step${step}`});}catch(e){result={error:e.message};}
  results.push({step,result});await persist(`r${rep}-step${step}.json`,{result,record:(await load()).record});console.log(JSON.stringify({rep,step,success:!!result.reply,warnings:result.warnings?.map(x=>x.code),error:result.error}));
  if(step===2)for(let branch=0;branch<2;branch++){let result;try{result=await createLivingInquiry({store,load,save,complete}).advance();}catch(e){result={error:e.message};}results.push({probe:branch,result});console.log(JSON.stringify({rep,probe:branch,status:result.status,idle:result.idle,error:result.error}));}
 }
 const record=(await load()).record,life=record.state.mind.living;
 const report={rep,calls,results,opinions:record.state.beliefs,events:life.events,inquiries:life.inquiries,associations:life.associations,invitation_count:record.state.mind.outbox.filter(x=>x.event_id).length};reports.push(report);await persist(`r${rep}-store.json`,Object.fromEntries(data));
}
await persist('report.json',{schema:'living13-smoke-results-1',reports,total_calls:reports.reduce((n,r)=>n+r.calls,0)});
console.log(JSON.stringify({total_calls:reports.reduce((n,r)=>n+r.calls,0),reports:reports.map(r=>({rep:r.rep,events:r.events.length,inquiries:r.inquiries.map(q=>q.status),invitations:r.invitation_count}))}));
