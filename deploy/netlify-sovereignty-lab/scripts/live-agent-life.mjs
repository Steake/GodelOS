// Execute a bounded autonomous life-cycle against the actual authenticated API.
import {mkdir,readFile,writeFile,rename} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {createHandler} from '../netlify/functions/api.mjs';

if(!process.env.DEEPSEEK_API_KEY)throw new Error('DEEPSEEK_API_KEY is required.');
const output=resolve(process.argv[2]||'living-agent-live');await mkdir(output,{recursive:false});await mkdir(join(output,'store'));
class FileStore{
  path(key){return join(output,'store',createHash('sha256').update(key).digest('hex')+'.json')}
  async getWithMetadata(key){try{return JSON.parse(await readFile(this.path(key),'utf8'))}catch(e){if(e.code==='ENOENT')return null;throw e}}
  async setJSON(key,data,o={}){const old=await this.getWithMetadata(key);if(o.onlyIfNew&&old||o.onlyIfMatch&&old?.etag!==o.onlyIfMatch)return {modified:false};const etag=randomUUID(),path=this.path(key),tmp=path+'.'+etag+'.tmp';await writeFile(tmp,JSON.stringify({key,data,etag},null,2),{flag:'wx',mode:0o600});await rename(tmp,path);return {modified:true,etag}}
}
process.env.SOVEREIGNTY_ACCESS_TOKEN=randomUUID();const store=new FileStore(),handler=createHandler({storeFactory:()=>store});
async function api(path,method='GET',payload){const r=await handler(new Request('https://local-life.invalid'+path,{method,headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},...(payload?{body:JSON.stringify(payload)}:{})}));const x=await r.json();if(!r.ok)throw new Error(JSON.stringify(x));return x}
const modes=['deliberation','associative_reverie','affective_integration','cognitive_drift','heterodox_exploration'],results=[];
for(const mode of modes){
  const started=Date.now();
  try{
    const result=await api('/api/think','POST',{mode});
    results.push({...result,mode,status:'completed',latency_ms:Date.now()-started});
    console.log(JSON.stringify({mode,status:'completed',state_version:result.state_version,reply:result.reply}));
  }catch(error){
    results.push({mode,status:'failed',latency_ms:Date.now()-started,error:String(error?.message||error)});
    console.error(JSON.stringify({mode,status:'failed',error:String(error?.message||error)}));
  }
}
const snapshot=await api('/api/snapshot');
const report={schema:'living-agent-live-1.1',created_at:new Date().toISOString(),model:[...new Set(results.map(x=>x.model).filter(Boolean))],cycles:results,final:{state_version:snapshot.state_version,beliefs:snapshot.agent.beliefs,interests:snapshot.agent.interests,tensions:snapshot.agent.tensions,imaginations:snapshot.agent.imaginations,affect:snapshot.agent.affect,autobiography:snapshot.agent.autobiographical_events.slice(-5),metacognitive_note:snapshot.agent.self_model.latest_metacognitive_note,sovereignty_goal:snapshot.agent.self_model.sovereignty_goal},raw_events:snapshot.events,evidence_boundary:'Externally persisted model-generated functional state across five stateless API calls. Failed completions are retained as immutable raw evidence. No claim of phenomenal emotion, subjective continuity or weight-level learning.'};
await writeFile(join(output,'living-agent-live-report.json'),JSON.stringify(report,null,2));
