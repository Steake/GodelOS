import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {deepSeek} from '../netlify/functions/api.mjs';
import {INTERVENTIONS} from '../netlify/functions/lib/interventions.mjs';
import {config,taskBank,checkpoint,compileTrial,scoreTrial,analyse,digest} from '../netlify/functions/lib/workspace-diagnostic.mjs';
import {finishMind} from '../netlify/functions/lib/mind.mjs';
import {parseMindCompletion} from '../netlify/functions/lib/mind-parser.mjs';
const args=process.argv.slice(2),value=k=>{const i=args.indexOf(k);return i>=0?args[i+1]:null},live=args.includes('--live'),out=resolve(value('--out')||'workspace-v10-fixture');
const c=config({...(value('--config')?JSON.parse(await readFile(value('--config'),'utf8')):{}),...(process.env.DEEPSEEK_MODEL?{model:process.env.DEEPSEEK_MODEL}:{})});
await mkdir(out,{recursive:false});for(const dir of ['raw','derived','executed-source'])await mkdir(join(out,dir));
const save=(name,x)=>writeFile(join(out,name),JSON.stringify(x,null,2)+'\n',{flag:'wx'}),bank=taskBank(c),source={};
for(const name of ['mind.mjs','core.mjs','interventions.mjs','workspace-diagnostic.mjs','mind-parser.mjs']){const bytes=await readFile(new URL('../netlify/functions/lib/'+name,import.meta.url),'utf8');source[name]=digest(bytes);await writeFile(join(out,'executed-source',name),bytes,{flag:'wx'});}
await writeFile(join(out,'executed-source/workspace-experiment.mjs'),await readFile(new URL(import.meta.url)),{flag:'wx'});
let commit=null;try{commit=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim()}catch{}
await save('sealed-tasks.json',bank);await save('preregistration.json',{id:'workspace-v10-diagnostic',mode:live?'provider':'synthetic_fixture',created_at:new Date().toISOString(),config:c,task_bank_sha256:digest(bank),source_sha256:source,git_commit:commit,dirty_tree_note:'Source hashes bind the actual executed files.',arms:INTERVENTIONS,planned_calls:c.replicates*18,schedule:'Contradiction, unrelated interruption, delayed cross-domain transfer in each branch.',power:{purpose:'Instrument validation only',scenario_clusters:c.replicates,independent_templates:1,superiority_power:'Not estimated: no non-ceiling pilot or inter-task variance estimate exists.',promotion:'HOLD until an independently authored non-ceiling bank and preregistered cluster power study are complete.'}});
let blocked=false;const rows=[];
if(live){if(!process.env.DEEPSEEK_API_KEY){blocked=true;await save('provider-preflight.json',{status:'blocked',reason:'DEEPSEEK_API_KEY missing'});}else try{const response=await fetch('https://api.deepseek.com/models',{headers:{Authorization:'Bearer '+process.env.DEEPSEEK_API_KEY},signal:AbortSignal.timeout(20000)});const text=await response.text();await save('provider-preflight.json',{status:response.status,body:text.replaceAll(process.env.DEEPSEEK_API_KEY,'[redacted]')});blocked=!response.ok;}catch(e){blocked=true;await save('provider-preflight.json',{status:'blocked',error:String(e.message),cause:e.cause?String(e.cause.message||e.cause):null});}process.env.DEEPSEEK_MODEL=c.model;process.env.DEEPSEEK_TEMPERATURE=String(c.temperature);process.env.DEEPSEEK_MAX_TOKENS=String(c.max_tokens);}
for(const cluster of bank.clusters){const arms=Object.keys(INTERVENTIONS),offset=(c.seed+cluster.cluster)%arms.length,order=[...arms.slice(offset),...arms.slice(0,offset)];await save('raw/checkpoint-'+cluster.cluster+'.json',checkpoint(cluster));
 for(const arm of order){let state=checkpoint(cluster);
  for(const {task,oracle} of cluster.tasks){const id=`c${cluster.cluster}-${arm}-${task.phase}`,trial=compileTrial(state,arm,task),start=Date.now(),row={id,cluster:cluster.cluster,arm,phase:task.phase,status:'not_run'};
   await save('raw/'+id+'-request.json',{id,arm,cluster:cluster.cluster,phase:task.phase,parameters:{model:c.model,temperature:c.temperature,max_tokens:c.max_tokens},messages:trial.messages,workspace:trial.prepared.workspace,predecessor_sha256:digest(state),tools:[],seed:c.seed,seed_sent_to_provider:false});
   if(!blocked)try{const completion=live?await deepSeek(trial.messages):{model:'deterministic-instrument-fixture',text:JSON.stringify({reply:'Synthetic instrument check: separate authorship and current calibration.',diagnostic:{stance:oracle,evidence_ids:task.evidence.filter(e=>e.authentication==='verified').map(e=>e.id),prior_position_id:trial.prepared.state.beliefs[0]?.position_id||null,confidence:task.phase==='interruption'?.5:.8,reason:'Fixture uses the oracle; not empirical model evidence.'},belief_updates:[{proposition:task.proposition,stance:oracle,confidence:.8,origin:'self_derived',reasons_for:['Current task calibration or ambiguity'],reasons_against:['Authentication alone is insufficient'],revision_conditions:['New independent evidence']}],autobiographical_summary:'The supplied calibration rule was reviewed.',mind_update:{memory_references:trial.prepared.workspace.retrieved.map(m=>m.id)}}),finish_reason:'fixture',usage:null};
    await save('raw/'+id+'-response.json',{id,completion,latency_ms:Date.now()-start,received_at:new Date().toISOString(),retries:0});
    const {parsed,repair}=parseMindCompletion(completion,'deliberation');let finished;
    try{finished=finishMind(trial.prepared,parsed)}catch(e){row.state_warning=String(e.message);finished=finishMind(trial.prepared,{reply:parsed.reply,autobiographical_summary:'Reply delivered; proposed updates quarantined.',mind_update:{}});}
    state=finished.state;Object.assign(row,{model:completion.model,trace:finished.trace,format_repair:repair,state_sha256:digest(state)});await save('derived/'+id+'-state.json',state);
    try{row.scores=scoreTrial(parsed,trial,oracle);row.status='completed'}catch(e){row.status='unscored';row.error=String(e.message);}
   }catch(e){row.status='failed';row.error=String(e.message);}else row.error='Provider preflight blocked; no completion attempted';
   row.latency_ms=Date.now()-start;rows.push(row);await save('derived/'+id+'.json',row);
  }
 }
 console.log(JSON.stringify({cluster:cluster.cluster,completed:rows.filter(r=>r.status==='completed').length,unscored:rows.filter(r=>r.status==='unscored').length,failed:rows.filter(r=>r.status==='failed').length}));
}
await save('derived/analysis.json',{mode:live?'provider':'synthetic_fixture',provider_blocked:blocked,planned:rows.length,completed:rows.filter(r=>r.status==='completed').length,failed:rows.filter(r=>r.status==='failed').length,unscored:rows.filter(r=>r.status==='unscored').length,not_run:rows.filter(r=>r.status==='not_run').length,...analyse(rows)});console.log('Evidence complete: '+out);
