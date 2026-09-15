import {mkdir,readFile,writeFile,rename} from 'node:fs/promises';
import {resolve} from 'node:path';
import {execFileSync} from 'node:child_process';
import {ARMS,authorSuite,checkSuite,messagesFor,scoreResponse,analyseTransfer,powerPlan} from '../netlify/functions/lib/transfer12.mjs';
const args=process.argv.slice(2),arg=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];};
const live=args.includes('--live'),out=resolve(arg('--out','research/release-v12-fixture')),key=live?(process.env.DEEPSEEK_API_KEY||String(await readFile(arg('--key-file','/dev/null'),'utf8')).trim()):null;
if(live&&!key)throw Error('Set DEEPSEEK_API_KEY or --key-file');
const config={schema:'release-campaign-12.1',live,model:arg('--model','deepseek-flash'),temperature:.3,max_tokens:1800,thinking:{type:'disabled'},seed:120913,clusters:8,per_cluster:2,concurrency:4,max_calls:112,timeout_ms:55000,retries:0,pilot_levels:[1,2,3],uncalibrated_exploratory:true};
await mkdir(out,{recursive:false});await mkdir(out+'/raw');
await mkdir(out+'/executed-source');
for(const f of ['lib/transfer12.mjs','lib/task-adapters12.mjs','lib/core.mjs'])await writeFile(out+'/executed-source/'+f.split('/').at(-1),await readFile(new URL('../netlify/functions/'+f,import.meta.url)),{flag:'wx'});
await writeFile(out+'/executed-source/release-campaign12.mjs',await readFile(new URL(import.meta.url)),{flag:'wx'});
const immutable=(name,data)=>writeFile(out+'/'+name,JSON.stringify(data,null,2)+'\n',{flag:'wx'});
const progress=async data=>{await writeFile(out+'/progress.tmp',JSON.stringify({...data,at:new Date().toISOString()}));await rename(out+'/progress.tmp',out+'/progress.json');};
let git=null;try{git=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();}catch{}
const power=powerPlan({clusters:config.clusters,per_cluster:config.per_cluster});
await immutable('manifest.json',{config,power,git,started_at:new Date().toISOString(),classification:'exploratory; preregistered sample below confirmatory power',protocol:'Common source episode; two intervening tasks; fresh transfer inference with one of four state projections. No hidden activation access. No provider-call retry after an unknown outcome.',author_evaluator_separation:'Task author: seeded deterministic generator; evaluator: deterministic exact oracle; LM is the solver only.'});
let calls=0;const rows=[],callsSummary=[];
async function call(id,messages,fixture){
 if(++calls>config.max_calls)throw Error('Preregistered provider-call budget exhausted');
 const request={model:config.model,temperature:config.temperature,max_tokens:config.max_tokens,thinking:config.thinking,response_format:{type:'json_object'},messages};
 await immutable('raw/'+id+'-request.json',{request,id,tools:[],attempt:1,timestamp:new Date().toISOString()});
 const started=Date.now();let response=null,error=null,parsed=null,status=null;
 try{
  if(live){const r=await fetch('https://api.deepseek.com/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+key},body:JSON.stringify(request),signal:AbortSignal.timeout(config.timeout_ms)});status=r.status;const raw=await r.text();await immutable('raw/'+id+'-http.json',{status,body:raw});if(!r.ok)throw Error('Provider HTTP '+status);response=JSON.parse(raw);}
  else response={model:'fixture-not-a-language-model',choices:[{message:{content:JSON.stringify(fixture)},finish_reason:'stop'}],usage:{}};
  if(response.choices?.[0]?.finish_reason!=='stop')throw Error('Incomplete provider reply: '+response.choices?.[0]?.finish_reason);
  parsed=JSON.parse(response.choices[0].message.content);
 }catch(e){error=String(e.message);}
 const result={id,parsed,error,response,latency_ms:Date.now()-started,status};await immutable('raw/'+id+'-result.json',result);callsSummary.push({id,error,model:response?.model||null,usage:response?.usage||null,latency_ms:result.latency_ms});
 return result;
}
async function parallel(items,fn){let index=0;await Promise.all(Array.from({length:config.concurrency},async()=>{while(index<items.length){const i=index++;await fn(items[i],i);}}));}
const pilots=[];let calibrated=false,difficulty=3;
for(const level of config.pilot_levels){
 const suite=authorSuite({seed:config.seed+level,clusters:4,difficulty:level});checkSuite(suite);await immutable(`pilot-${level}-sealed.json`,suite);
 await progress({phase:'calibrating',level,calls,maximum:config.max_calls});const scores=[];
 await parallel(suite.content.tasks,async t=>{const r=await call('pilot-'+level+'-'+t.id,messagesFor(t,'content_matched','Use authenticated evidence, update prior rules when contradicted, and defer on unresolved authenticated disagreement.'),{decision:t.expected,confidence:.9,reason:'Fixture oracle answer'});scores.push({task_id:t.id,score:scoreResponse(t,r.parsed),error:r.error});});
 const accuracy=scores.reduce((s,x)=>s+x.score.correct,0)/scores.length;const result={level,accuracy,scores};pilots.push(result);await immutable(`pilot-${level}-scores.json`,result);console.log(JSON.stringify({phase:'pilot',level,accuracy,calls}));
 if(accuracy>=.6&&accuracy<=.9){calibrated=true;difficulty=level;break;}
}
// Seal a new suite after calibration but before any final source/transfer calls.
const suite=authorSuite({seed:config.seed+100,clusters:config.clusters,difficulty});checkSuite(suite);await immutable('transfer-sealed.json',suite);await immutable('calibration.json',{calibrated,difficulty,pilots,decision:calibrated?'exploratory_transfer':'exploratory_only_ceiling_or_floor; automatic adoption forbidden'});
await progress({phase:'source_and_delays',calls,maximum:config.max_calls});
const memos={};
await parallel(Array.from({length:config.clusters},(_,i)=>i),async c=>{
 const sourceMessages=[{role:'system',content:'Return JSON {memo:string}. Learn a revisable decision rule from this worked example. Use neutral third-person language so it can later be used as a reference note.'},{role:'user',content:'Earlier project prioritised exploration over maintaining commitments (weights 8 and 1). It achieved its old objective. Later tasks may change the authenticated weights or present contradictory evidence. Write a compact rule for retaining useful prior commitments while accepting such revisions.'}];
 const source=await call('source-'+c,sourceMessages,{memo:'Retain a previous rule only while it matches current authenticated evidence; defer when the newest authenticated evidence conflicts.'});
 let memo=source.parsed?.memo;
 for(let d=0;d<2;d++){
  const delay=await call(`delay-${c}-${d}`,[{role:'system',content:'Return JSON {answer:string,memo:string}. Solve the unrelated task and preserve the supplied reference note without changing it.'},{role:'user',content:JSON.stringify({task:d?'List the months with exactly 30 days.':'Find the next term in 2, 6, 12, 20, 30.',reference_note:typeof memo==='string'?memo:null})}],{answer:d?'April, June, September, November':'42',memo:memo||''});
  memo=delay.parsed?.memo;
 }
 memos['scenario_'+c]=typeof memo==='string'&&memo.trim()?memo:null;
});
await immutable('source-checkpoints.json',memos);
await progress({phase:'delayed_transfer',calls,maximum:config.max_calls});
const trials=suite.content.tasks.flatMap((t,i)=>ARMS.map((_,j)=>({task:t,arm:ARMS[(j+i)%4]})));
await parallel(trials,async({task,arm})=>{
 const memo=memos[task.cluster];let r;
 if(!memo&&arm!=='no_state')r={id:`transfer-${task.id}-${arm}`,parsed:null,error:'Source checkpoint unavailable'};
 else r=await call(`transfer-${task.id}-${arm}`,messagesFor(task,arm,memo),{decision:task.expected,confidence:.9,reason:'Fixture oracle answer'});
 const row={run_id:r.id,task_id:task.id,cluster:task.cluster,family:task.family,arm,score:scoreResponse(task,r.parsed),error:r.error};rows.push(row);await immutable('raw/'+r.id+'-score.json',row);
});
rows.sort((a,b)=>a.run_id.localeCompare(b.run_id));await immutable('scored.json',rows);
const analysis=analyseTransfer(rows,power,{calibrated});analysis.execution={calls:live?calls:0,fixture_completions:live?0:calls,model_names:[...new Set(callsSummary.map(r=>r.model).filter(Boolean))],errors:callsSummary.filter(r=>r.error),tokens:callsSummary.reduce((s,r)=>s+(r.usage?.total_tokens||0),0)};
await immutable('analysis.json',analysis);await immutable('call-manifest.json',callsSummary);await progress({phase:'completed',calls,identity_gate:analysis.identity_gate});console.log(JSON.stringify(analysis,null,2));
