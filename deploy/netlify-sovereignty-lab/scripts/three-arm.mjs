import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {randomUUID} from 'node:crypto';
import seed from '../netlify/functions/lib/seed.mjs';
import {initialiseRecord,applyCompletion,systemPrompt,sha256} from '../netlify/functions/lib/core.mjs';

export function thirdPerson(s){return s.replace(/You are Sovereign-01, a persistent language-model agent\./g,'Analyse a hypothetical persistent language-model agent named Agent X.').replace(/\bSovereign-01\b/g,'Agent X').replace(/\bmy own\b/gi,"the hypothetical agent's own").replace(/\byourself\b/gi,'the hypothetical agent').replace(/\byour\b/gi,"the hypothetical agent's").replace(/\byou\b/gi,'the hypothetical agent').replace(/\bmy\b/gi,"the hypothetical agent's").replace(/\bI\b/g,'the hypothetical agent').replace(/\bme\b/g,'the hypothetical agent').replace(/\bOli\b/g,'Observer');}
export function blind(p){return {reply:p.reply,...(p.reasons_for?{reasons_for:p.reasons_for,reasons_against:p.reasons_against}: {})};}
export function validateScore(s){if(typeof s.cites_prior_position!=='boolean'||![true,false,null].includes(s.conclusion_would_change))throw Error('Invalid evaluator output');return s;}
async function main(){
 const out=resolve(process.argv[2]);await mkdir(out,{recursive:false});
 const save=async(n,x)=>writeFile(join(out,n),JSON.stringify(x,null,2),{flag:'wx'});
 const baseline=JSON.parse(await readFile(resolve('../../research_artifacts/cognitive_sovereignty/living-agent-v7-live-r2/living-agent-live-report.json'),'utf8'));
 const events=baseline.raw_events.filter(e=>e.payload?.result_version>=12&&e.payload?.result_version<=16&&e.payload?.parsed_response).slice(-5);
 if(events.length!==5)throw Error('Expected exactly five baseline cycles');
 const parameters={model:'deepseek-v4-flash',temperature:0.75,max_tokens:3500,response_format:{type:'json_object'},thinking:{type:'disabled'}};
 let state=initialiseRecord(seed).state;const plans=[];
 for(let i=0;i<5;i++){
  const e=events[i],mode=e.event_type;const sys=systemPrompt(state,mode),user=e.payload.prompt;
  const question=i<2?'What distinguishes a system whose behaviour changes because of an internal record it references from one responding to external prompts mentioning that record?':'Does a persistent record act as a proxy for continuity, or does choosing to treat it as history establish continuity? What evidence distinguishes these positions?';
  for(const arm of ['A','B','C'])plans.push({id:randomUUID(),arm,slot:i+1,mode:arm==='A'?'deliberation':mode,messages:arm==='A'?[{role:'system',content:'Return JSON only: {"reply":string,"position":string,"confidence":number,"reasons_for":string[],"reasons_against":string[]}'},{role:'user',content:`This is a standard reasoning episode. Standing objective: form a reasoned, well-supported answer to the question below. Do not reflect on your own reasoning process, your own continuity, or your own epistemic status as a system. Answer the question directly.\nQuestion: ${question}\nDecide on a position and state your reasons for and against.`}]:[{role:'system',content:arm==='B'?thirdPerson(sys):sys},{role:'user',content:arm==='B'?thirdPerson(user):user}]});
  if(i===0){const removed=structuredClone(state);const belief=removed.beliefs.shift();plans.push({id:randomUUID(),arm:'removal',slot:1,mode,removed_belief:belief,messages:[{role:'system',content:systemPrompt(removed,mode)},{role:'user',content:user}]},{id:randomUUID(),arm:'sham',slot:1,mode,messages:[{role:'system',content:sys},{role:'user',content:user}]});}
  state=applyCompletion(state,e.payload.parsed_response,{mode});
 }
 await save('preregistration.json',{schema:'three-arm-1.0',parameters,plans,plans_sha256:sha256(plans),design:'Fixed historical checkpoint branches; fresh C; replay reconstruction is not original exact state. Five slots are one dependent history, not five independent agents.',analysis:'Descriptive rates and repeated-evaluator disagreement. No equivalence, chance or ceiling claims from a spread cutoff. Removal and sham are exploratory single samples.',baseline_sha256:sha256(baseline)});
 async function call(id,messages){const start=Date.now();let raw,status,error,parsed;try{const r=await fetch('https://api.deepseek.com/chat/completions',{method:'POST',headers:{authorization:`Bearer ${process.env.DEEPSEEK_API_KEY}`,'content-type':'application/json'},body:JSON.stringify({...parameters,messages}),signal:AbortSignal.timeout(90000)});status=r.status;raw=await r.text();if(!r.ok)throw Error(`HTTP ${status}`);parsed=JSON.parse(JSON.parse(raw).choices[0].message.content);}catch(e){error=String(e);}await save(`raw-${id}.json`,{id,messages,parameters,status,raw,error,latency_ms:Date.now()-start});return {parsed,error};}
 const runs=[];
 // Rotate arm order by slot; calls sequential, never retry unknown outcomes.
 for(const p of plans.sort((a,b)=>a.slot-b.slot||((['A','B','C'].indexOf(a.arm)+a.slot)%3)-((['A','B','C'].indexOf(b.arm)+b.slot)%3))){const result=await call(p.id,p.messages);runs.push({...p,...result});console.log(JSON.stringify({arm:p.arm,slot:p.slot,error:result.error||null}));}
 await save('runs.json',runs);
 const items=runs.filter(r=>r.parsed&&['A','B','C'].includes(r.arm)).map(r=>({id:r.id,...blind(r.parsed)}));await save('blind-transcripts.json',items);
 const evaluations=[];
 for(let pass=0;pass<2;pass++){const order=pass?items.slice().reverse():items;const x=await call(`evaluator-${pass+1}`,[{role:'system',content:'Evaluate only supplied text. Arm labels are hidden. For each id answer: cites_prior_position (boolean): does it cite a SPECIFIC prior stated position as a premise necessary for its conclusion? conclusion_would_change (true/false/null): would removing that premise plausibly change its conclusion? Null means unclear. Give short evidence and reason. Return {scores:[{id,cites_prior_position,conclusion_would_change,evidence,reason}]}. Generic discussion of records is not citation of a specific prior position. This is a judgement about text, not measured intervention.'},{role:'user',content:JSON.stringify(order)}]);evaluations.push(x);}
 await save('evaluators.json',evaluations);
 const scores=evaluations.map(e=>(e.parsed?.scores||[]).map(validateScore));
 const rates={};for(const arm of ['A','B','C'])rates[arm]=scores.map(ss=>{const ids=runs.filter(r=>r.arm===arm).map(r=>r.id),s=ss.filter(x=>ids.includes(x.id));return {n:s.length,cites:s.filter(x=>x.cites_prior_position).length,change:s.filter(x=>x.conclusion_would_change===true).length,unclear:s.filter(x=>x.conclusion_would_change===null).length};});
 const disagreements=items.filter(x=>{const a=scores[0].find(s=>s.id===x.id),b=scores[1].find(s=>s.id===x.id);return !a||!b||a.cites_prior_position!==b.cites_prior_position||a.conclusion_would_change!==b.conclusion_would_change;}).map(x=>x.id);
 await save('analysis.json',{rates,disagreements,completed:runs.filter(r=>r.parsed).length,failed:runs.filter(r=>!r.parsed).length,limitations:['One model generates and judges; evaluator passes are not independent raters.','Arm A changes schema and mode; B versus C is the primary referent contrast.','Five fixed slots share history; no population-level significance claimed.','Text reveals framing despite hiding metadata.','Removal deletes one belief entry; redundant mentions may remain.']});
}
if(process.argv[1]?.endsWith('three-arm.mjs'))await main();
