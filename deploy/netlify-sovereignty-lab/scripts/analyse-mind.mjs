// Recompute descriptive component evidence. Never edits collected run records.
import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {basename,resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

const mean=values=>values.length?values.reduce((a,b)=>a+b,0)/values.length:null;
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function summariseReport(report,results=new Map()){
 if(!Array.isArray(report.cycles)||!Array.isArray(report.branches))throw Error('A live report needs cycles and branches');
 if(new Set(report.cycles.map(c=>c.episode)).size!==report.cycles.length)throw Error('Duplicate episode ID');
 const seenImaginations=new Map(),reentries=[];
 const cycles=report.cycles.map(c=>{
   const trace=c.response?.trace,m=c.state?.mind;
   const previous=trace&&seenImaginations.get(trace.focus.id);
   if(previous)reentries.push({id:trace.focus.id,generated_episode:previous.episode,selected_episode:c.episode,title:previous.title});
   for(const i of c.state?.imaginations||[])if(!seenImaginations.has(i.imagination_id))seenImaginations.set(i.imagination_id,{episode:c.episode,title:i.title});
   const err=trace?.prediction_error;
   return {episode:c.episode,status:c.status,tick:m?.tick,focus:trace?.focus.kind||null,title:trace?.focus.title||null,provenance:trace?.focus.provenance||null,mode:c.response?.cognitive_mode||null,external_contact:!!c.input?.message,retrieved:trace?.retrieved_ids.length||0,cited:trace?.cited_memory_ids.length||0,intention_changes:trace?.intention_changes.length||0,intentions:m?.intentions.length||0,imaginations:c.state?.imaginations?.length||0,revisions:m?.revisions.length||0,drives:m?.drives,affect:c.state?.affect,brier:err?.context==='autonomous'?err.brier:null,forecast_context:err?.context||null,format_repair:results.get(c.input?.request_id)?.format_repair||null,latency_ms:c.latency_ms,error:c.error||null};
 });
 const branches=report.branches.map(b=>({id:b.id,ablation:b.ablation,rep:b.rep,status:b.status,focus:b.trace?.focus.kind||null,title:b.trace?.focus.title||null,mode:b.trace?.mode||null,retrieved:b.trace?.retrieved_ids.length??null,cited:b.trace?.cited_memory_ids.length??null,new_thoughts:b.trace?.new_thought_ids.length??null,intention_changes:b.trace?.intention_changes.length??null,format_repair:b.format_repair||null,error:b.error||null}));
 const contrasts=branches.filter(b=>b.ablation!=='none').map(b=>{
   const control=branches.find(c=>c.rep===b.rep&&c.ablation==='none');
   const comparable=control?.status==='completed'&&b.status==='completed';
   return {branch:b.id,control:control?.id||null,comparable,focus_changed:comparable?control.focus!==b.focus:null,citation_delta:comparable?b.cited-control.cited:null};
 });
 const errors=cycles.filter(c=>c.brier!==null).map(c=>c.brier);
 const all=[...cycles,...branches],last=report.cycles.at(-1)?.state?.mind;
 return {parameters:report.parameters,attempted:all.length,completed:all.filter(c=>c.status==='completed').length,failed:all.filter(c=>c.status!=='completed').length,format_repairs:all.filter(c=>c.format_repair).length,cycles,branches,contrasts,generated_image_reentries:reentries,autonomous_forecast:{n:errors.length,mean_brier:mean(errors),uniform_seven_kind_brier:6/7,lower_is_better:true,independence:'dependent ticks within one trajectory; no confidence interval claimed'},final_intentions:last?.intentions||[],final_revisions:last?.revisions||[],final_social_initiatives:last?.outbox||[],limits:['Bids and selections are designed controller behavior, not discovered neural mechanisms.','Two branch outputs per component share one checkpoint; they are not independent replications of an agent.','Ablations remove named routes only. Memory removal retains beliefs, imagery and intentions; self-model removal retains self-relevant language elsewhere.','Generator is also the author of intention evidence and self-observations. These are reports, not independent verification.','Before/after engineering runs change parsing and forecast handling and use stochastic generation; do not attribute all trajectory differences to the fixes.']};
}

export async function analyseDirectory(dir){
 const bytes=await readFile(join(dir,'report.json')),report=JSON.parse(bytes),results=new Map(),raw=[];
 for(const file of await readdir(join(dir,'store'))){
   if(!file.endsWith('.json'))continue;
   const entry=JSON.parse(await readFile(join(dir,'store',file),'utf8'));
   if(entry.key.startsWith('mind/v8/results/'))results.set(entry.key.split('/').at(-1),entry.data);
   if(entry.key.startsWith('mind/v8/raw/'))raw.push(entry.data.completion);
 }
 for(const b of report.branches){try{raw.push(JSON.parse(await readFile(join(dir,b.id+'-raw.json'),'utf8')).completion);}catch(e){if(e.code!=='ENOENT')throw e;}}
 const tokens=raw.reduce((a,c)=>({prompt:a.prompt+Number(c.usage?.prompt_tokens||0),completion:a.completion+Number(c.usage?.completion_tokens||0),total:a.total+Number(c.usage?.total_tokens||0)}),{prompt:0,completion:0,total:0});
 return {run_id:basename(dir),source_report_sha256:hash(bytes),raw_completions:raw.length,returned_models:[...new Set(raw.map(c=>c.model))],tokens,...summariseReport(report,results)};
}

if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 const [output,...dirs]=process.argv.slice(2);if(!output||!dirs.length)throw Error('Usage: node scripts/analyse-mind.mjs OUTPUT_DIRECTORY RUN_DIRECTORY [RUN_DIRECTORY...]');
 const runs=[];for(const dir of dirs)runs.push(await analyseDirectory(resolve(dir)));
 await mkdir(resolve(output),{recursive:true});
 const analysis={schema:'integrated-mind-analysis-1.0',generated_at:new Date().toISOString(),runs,total_calls:runs.reduce((n,r)=>n+r.attempted,0),total_completed:runs.reduce((n,r)=>n+r.completed,0),total_failed:runs.reduce((n,r)=>n+r.failed,0),interpretation:'Executable recurrent component integration demonstrated. Subjective experience and calibrated self-knowledge are not established.'};
 await writeFile(join(output,'analysis.json'),JSON.stringify(analysis,null,2)+'\n');
 console.log(JSON.stringify({output:resolve(output),runs:runs.map(r=>({run_id:r.run_id,completed:r.completed,failed:r.failed,format_repairs:r.format_repairs,forecast:r.autonomous_forecast,image_reentries:r.generated_image_reentries.length})),total_calls:analysis.total_calls},null,2));
}
