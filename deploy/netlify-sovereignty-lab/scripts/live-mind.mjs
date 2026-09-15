// Run the deployed API and pure ablation branches with immutable evidence.
import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createHandler,deepSeek} from '../netlify/functions/api.mjs';
import {prepareMind,mindMessages,finishMind,ABLATIONS} from '../netlify/functions/lib/mind.mjs';
import {sha256} from '../netlify/functions/lib/core.mjs';
import {parseMindCompletion} from '../netlify/functions/lib/mind-parser.mjs';

if(!process.env.DEEPSEEK_API_KEY)throw Error('DEEPSEEK_API_KEY is required');
const out=resolve(process.argv[2]||'mind-live');await mkdir(out,{recursive:false});await mkdir(join(out,'store'));
const save=(name,x)=>writeFile(join(out,name),JSON.stringify(x,null,2),{flag:'wx'});
class LocalStore {
  path(key){return join(out,'store',createHash('sha256').update(key).digest('hex')+'.json');}
  async getWithMetadata(key){try{return JSON.parse(await readFile(this.path(key),'utf8'));}catch(e){if(e.code==='ENOENT')return null;throw e;}}
  async setJSON(key,data,o={}){const old=await this.getWithMetadata(key);if(o.onlyIfNew&&old||o.onlyIfMatch&&o.onlyIfMatch!==old?.etag)return {modified:false};const etag=randomUUID(),file=this.path(key),temp=file+'.'+etag+'.tmp';await writeFile(temp,JSON.stringify({key,data,etag},null,2),{flag:'wx',mode:0o600});await rename(temp,file);return {modified:true,etag};}
}
const schedule=[{},
 {message:'I feel torn between wanting intellectual company and wanting a room where nothing needs explaining. What do you make of that?',outcome:'novel'},
 {},
 {message:'The line of inquiry you planned cannot be completed with the tools available today. What will you do with that obstruction?',outcome:'blocked'},
 {},
 {message:'A familiar record is not automatically reliable. Which of your own positions would you challenge if its provenance was mistaken?',outcome:'contradiction'},
 {},{}];
const parameters={model:process.env.DEEPSEEK_MODEL||'deepseek-v4-flash',temperature:Number(process.env.DEEPSEEK_TEMPERATURE||.75),max_tokens:Number(process.env.DEEPSEEK_MAX_TOKENS||3500),thinking:'disabled'};
const branchesToRun=process.argv.includes('--cycles-only')?[]:ABLATIONS;
let gitCommit=null;try{gitCommit=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();}catch{}
const sourceHashes={};for(const file of ['api.mjs','lib/mind.mjs','lib/core.mjs','lib/mind-runtime.mjs','lib/mind-parser.mjs','lib/seed.mjs'])sourceHashes[file]=sha256(await readFile(new URL('../netlify/functions/'+file,import.meta.url),'utf8'));
await save('source-manifest.json',{git_commit:gitCommit,source_sha256:sourceHashes,working_tree_note:'Hashes bind the executed files; the commit alone may not include working-tree changes.'});
await save('preregistration.json',{schema:'integrated-mind-experiment-1.1',created_at:new Date().toISOString(),parameters,schedule,branch_checkpoint:'after completed cycle 4',branches:branchesToRun,repetitions:2,provider_call_budget:8+2*branchesToRun.length,code_sha256:sha256(await readFile(new URL('../netlify/functions/lib/mind.mjs',import.meta.url),'utf8')),metrics:['focus kind and actual mode','structured model intention updates','memory retrieval and validated ID references','imagination candidate generation','committed next-focus forecast Brier error','component ablation differences'],limits:['One model and one continuous trajectory; branch repetitions are dependent checkpoint samples.','No score for consciousness or productivity; component functionality and intervention sensitivity only.','Functional affect and focus are engineered variables.','LocalStore assumes one writer process; production uses Blob conditional writes.']});
process.env.SOVEREIGNTY_ACCESS_TOKEN=randomUUID();const store=new LocalStore();let handler=createHandler({storeFactory:()=>store});
async function api(path,payload){const r=await handler(new Request('https://local-mind.invalid'+path,{method:payload?'POST':'GET',headers:{Authorization:'Bearer '+process.env.SOVEREIGNTY_ACCESS_TOKEN,'Content-Type':'application/json'},...(payload?{body:JSON.stringify(payload)}:{})}));const x=await r.json();if(!r.ok)throw Error(x.error);return x;}
const cycles=[],branches=[];let checkpoint;
for(let i=0;i<schedule.length;i++){
 if(i===6)handler=createHandler({storeFactory:()=>store});
 const payload={...schedule[i],request_id:`episode-${i+1}`,...(schedule[i].message?{person_id:'oli',person_name:'Oli'}:{})};
 const start=Date.now();let result;
 try{result={status:'completed',response:await api(schedule[i].message?'/api/chat':'/api/mind/cycle',payload)};}catch(e){result={status:'failed',error:e.message};}
 const snapshot=await api('/api/snapshot');cycles.push({episode:i+1,input:payload,...result,latency_ms:Date.now()-start,state:snapshot.agent});await save(`episode-${i+1}.json`,cycles.at(-1));
 if(i===3)checkpoint=structuredClone(snapshot.agent);
 console.log(JSON.stringify({episode:i+1,status:result.status,focus:result.response?.trace.focus.kind,mode:result.response?.cognitive_mode,error:result.error}));
}
for(let rep=0;rep<2;rep++)for(const ablation of (rep?branchesToRun.slice().reverse():branchesToRun)){
 const id=`branch-${rep+1}-${ablation}`,prepared=prepareMind(checkpoint,{}, {ablation}),messages=mindMessages(prepared);await save(id+'-prompt.json',{id,ablation,rep,messages,parameters,checkpoint_sha256:sha256(checkpoint),workspace:prepared.workspace});
 let completion,result;const start=Date.now();
 try{completion=await deepSeek(messages);await save(id+'-raw.json',{completion,latency_ms:Date.now()-start});const {parsed,repair}=parseMindCompletion(completion,prepared.mode);result={status:'completed',parsed,format_repair:repair,...finishMind(prepared,parsed)};}catch(e){result={status:'failed',error:e.message};if(!completion)await save(id+'-error.json',result);}
 branches.push({id,ablation,rep,...result});await save(id+'-result.json',branches.at(-1));console.log(JSON.stringify({branch:id,status:result.status,error:result.error}));
}
await save('report.json',{schema:'integrated-mind-live-1.0',parameters,cycles,branches,completed:cycles.filter(c=>c.status==='completed').length+branches.filter(c=>c.status==='completed').length,failed:cycles.filter(c=>c.status!=='completed').length+branches.filter(c=>c.status!=='completed').length});
console.log('Evidence complete: '+out);
