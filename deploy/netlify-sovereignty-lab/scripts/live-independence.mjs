// Actual authenticated API + local durable adapter; Netlify scheduling is tested separately.
import {mkdir,readFile,writeFile,rename,open,unlink} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {createHandler} from '../netlify/functions/api.mjs';

const output=resolve(process.argv[2]||'independence-live');
const rounds=Number(process.argv[3]||2),cases=Number(process.argv[4]||1);
const mode=process.argv.includes('--synthetic')?'synthetic':'live';
if(mode==='live'&&!process.env.DEEPSEEK_API_KEY)throw new Error('Set DEEPSEEK_API_KEY before starting a live campaign.');
await mkdir(output,{recursive:true});
await mkdir(join(output,'store'),{recursive:true});
// No parallel writers. A crashed runner leaves a lock requiring operator inspection.
const lockPath=join(output,'runner.lock');
const lock=await open(lockPath,'wx',0o600);
await lock.writeFile(JSON.stringify({pid:process.pid,created_at:new Date().toISOString()}));
class FileStore {
  path(key){return join(output,'store',createHash('sha256').update(key).digest('hex')+'.json');}
  async getWithMetadata(key){try{return JSON.parse(await readFile(this.path(key),'utf8'));}catch(e){if(e.code==='ENOENT')return null;throw e;}}
  async setJSON(key,data,options={}){
    const old=await this.getWithMetadata(key);
    if(options.onlyIfNew&&old||options.onlyIfMatch&&old?.etag!==options.onlyIfMatch)return {modified:false};
    const etag=randomUUID(),file=this.path(key),temp=file+'.'+etag+'.tmp';
    await writeFile(temp,JSON.stringify({key,data,etag},null,2),{mode:0o600,flag:'wx'});
    await rename(temp,file);return {modified:true,etag};
  }
}
process.env.SOVEREIGNTY_ACCESS_TOKEN=randomUUID();
const handler=createHandler({storeFactory:()=>new FileStore()});
async function api(path='',method='GET',payload){
  const response=await handler(new Request('https://local-verification.invalid/api/independence'+path,{method,headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},...(payload?{body:JSON.stringify(payload)}:{})}));
  const value=await response.json();if(!response.ok)throw new Error(JSON.stringify(value));return value;
}
try {
  let manifest;
  try{manifest=JSON.parse(await readFile(join(output,'manifest.json'),'utf8'));}
  catch(e){if(e.code!=='ENOENT')throw e;manifest={request_id:randomUUID(),rounds,cases,mode,created_at:new Date().toISOString()};await writeFile(join(output,'manifest.json'),JSON.stringify(manifest,null,2),{flag:'wx'});}
  if(manifest.rounds!==rounds||manifest.cases!==cases||manifest.mode!==mode)throw new Error('Output directory belongs to a different configuration. Use a new directory.');
  let c=await api('','POST',{request_id:manifest.request_id,rounds,cases,mode});
  console.log(JSON.stringify({event:'campaign',id:c.id,budget:c.budget,mode}));
  while(!['completed','failed','stopped','paused'].includes(c.status)){
    c=await api('/'+c.id+'/advance','POST',{expected_revision:c.revision});
    console.log(JSON.stringify({event:'step',revision:c.revision,status:c.status,stage:c.stage,round:c.round,last:c.results.at(-1)?.role,error:c.results.at(-1)?.error||null}));
  }
  const exported=await api('/'+c.id+'/export');
  // Raw objects are write-once. Exports and summary are derived, reproducible views.
  await writeFile(join(output,'campaign-export.json'),JSON.stringify(exported,null,2));
  const summary={release:c.release,campaign_id:c.id,status:c.status,mode,rounds_completed:c.round,
    provider_attempts:c.results.filter(r=>r.provider_call_attempted).length,
    models:[...new Set(c.results.map(r=>r.completion?.model).filter(Boolean))],analysis:c.analysis,
    validation_scope:'actual API handler and local durable adapter; published Netlify worker not exercised'};
  await writeFile(join(output,'summary.json'),JSON.stringify(summary,null,2));
  console.log(JSON.stringify({event:'finished',status:c.status,calls:summary.provider_attempts}));
  if(c.status==='failed')process.exitCode=1;
}finally{await lock.close();await unlink(lockPath);}
