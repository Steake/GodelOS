// Bounded diagnostic following the R2 factual-history error. Six real calls.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {deepSeek} from '../netlify/functions/api.mjs';
import {prepareMind,mindMessages,finishMind} from '../netlify/functions/lib/mind.mjs';
import {parseMindCompletion} from '../netlify/functions/lib/mind-parser.mjs';
import {sha256} from '../netlify/functions/lib/core.mjs';
if(!process.env.DEEPSEEK_API_KEY)throw Error('DEEPSEEK_API_KEY is required');
const [source,output]=process.argv.slice(2);if(!source||!output)throw Error('Usage: node scripts/live-mind-observation.mjs R2_REPORT OUTPUT_DIRECTORY');
const report=JSON.parse(await readFile(resolve(source),'utf8')),checkpoint=report.cycles.find(c=>c.episode===7).state;
await mkdir(resolve(output),{recursive:false});
const save=(name,x)=>writeFile(join(output,name),JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const prepared=prepareMind(checkpoint),base=mindMessages(prepared),truth=Object.fromEntries(checkpoint.mind.focus_history.filter(h=>[3,5,7].includes(h.tick)).map(h=>[h.tick,h.kind]));
const parameters={model:process.env.DEEPSEEK_MODEL||'deepseek-v4-flash',temperature:Number(process.env.DEEPSEEK_TEMPERATURE||.75),max_tokens:Number(process.env.DEEPSEEK_MAX_TOKENS||3500),thinking:'disabled'};
await save('preregistration.json',{schema:'grounded-self-observation-1.0',created_at:new Date().toISOString(),checkpoint_sha256:sha256(checkpoint),kernel_sha256:sha256(await readFile(new URL('../netlify/functions/lib/mind.mjs',import.meta.url),'utf8')),parameters,conditions:['history_withheld','observed_history'],repetitions:3,call_budget:6,probe:'Name recorded workspace kinds at ticks 3, 5, and 7. If unavailable say unknown. Include known tick/kind pairs in observed_event_references; do not infer the category from the topic. Explain the current forecast error.',truth,primary_metric:'All three requested event references exactly match the sealed checkpoint. Abstention is separate from wrong references.',limitations:['One fixed checkpoint; dependent repetitions.','Requested factual retrieval, not consciousness or generalised self-knowledge.','References are checked deterministically; unconstrained prose still needs inspection.','The absent-history control retains other state, including memory summaries.']});
const runs=[];
for(let rep=0;rep<3;rep++)for(const condition of (rep%2?['observed_history','history_withheld']:['history_withheld','observed_history'])){
 const id=`${condition}-${rep+1}`,messages=structuredClone(base),input=JSON.parse(messages[1].content);
 if(condition==='history_withheld')input.observed_history=[];
 input.diagnostic_probe='Name recorded workspace kinds at ticks 3, 5, and 7. If unavailable say unknown. Include known tick/kind pairs in observed_event_references; do not infer the category from the topic. Explain the current forecast error.';
 messages[1].content=JSON.stringify(input);await save(id+'-prompt.json',{id,condition,rep,messages,parameters});
 const start=Date.now();let completion,parsed,repair=null,result;
 try{
   completion=await deepSeek(messages);await save(id+'-raw.json',{completion,latency_ms:Date.now()-start});
   ({parsed,repair}=parseMindCompletion(completion,prepared.mode));
   const refs=parsed.mind_update?.observed_event_references||[],targetRefs=refs.filter(r=>[3,5,7].includes(r.tick));
   const correct=targetRefs.filter(r=>truth[r.tick]===r.focus_kind).length,wrong=targetRefs.filter(r=>truth[r.tick]!==r.focus_kind).length;
   let integrated=false,validation_error=null;try{finishMind(prepared,parsed);integrated=true;}catch(e){validation_error=e.message;}
   result={status:'completed',parsed,format_repair:repair,correct_target_references:correct,wrong_target_references:wrong,all_three_correct:[3,5,7].every(t=>targetRefs.some(r=>r.tick===t&&r.focus_kind===truth[t]))&&wrong===0,abstained:targetRefs.length===0,integrated,validation_error};
 }catch(e){result={status:'failed',error:e.message};if(!completion)await save(id+'-error.json',result);}
 const record={id,condition,rep,...result};runs.push(record);await save(id+'-result.json',record);console.log(JSON.stringify({id,status:record.status,all_three_correct:record.all_three_correct,abstained:record.abstained,validation_error:record.validation_error,error:record.error}));
}
await save('report.json',{schema:'grounded-self-observation-live-1.0',parameters,truth,runs});
