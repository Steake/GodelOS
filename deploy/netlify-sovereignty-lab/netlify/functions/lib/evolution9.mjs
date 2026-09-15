import {randomUUID,generateKeyPairSync,sign,verify} from 'node:crypto';
import {sha256,appendEvent} from './core.mjs';
import {approvedCanary} from './promotion12.mjs';

// A bounded executable language: no JavaScript eval, imports, filesystem or network.
const VARIABLES=['salience','need','affect','repeats'];
const OPS=['add','sub','mul','min','max'];
export function compilePolicy(program,depth=0,budget={nodes:0}){
 if(++budget.nodes>63||depth>8)throw Error('Policy exceeds the expression budget');
 if(typeof program==='number'){if(!Number.isFinite(program)||Math.abs(program)>5)throw Error('Constant must be finite and between -5 and 5');return program;}
 if(typeof program==='string'){if(!VARIABLES.includes(program))throw Error('Unknown policy input');return program;}
 if(!program||!OPS.includes(program.op)||!Array.isArray(program.args)||program.args.length!==2)throw Error('Use binary add, sub, mul, min or max expressions');
 return {op:program.op,args:program.args.map(x=>compilePolicy(x,depth+1,budget))};
}
export function evaluatePolicy(program,features){
 if(typeof program==='number')return program;
 if(typeof program==='string')return Number(features[program])||0;
 const [a,b]=program.args.map(x=>evaluatePolicy(x,features));
 const value=({add:()=>a+b,sub:()=>a-b,mul:()=>a*b,min:()=>Math.min(a,b),max:()=>Math.max(a,b)})[program.op]();
 return Math.max(-100,Math.min(100,value));
}
export const BASELINE={op:'sub',args:[{op:'add',args:[{op:'add',args:[{op:'mul',args:[.35,'salience']},{op:'mul',args:[.4,'need']}]},{op:'mul',args:[.35,'affect']}]},{op:'mul',args:[.3,'repeats']}]};
const pick=(p,choices)=>choices.map((x,i)=>({i,score:evaluatePolicy(p,x)})).sort((a,b)=>b.score-a.score||a.i-b.i)[0].i;
export function compileCandidate(design){
 if(typeof design?.thesis!=='string'||!design.thesis.trim()||design.thesis.length>2000)throw Error('A thesis is required');
 const program=compilePolicy(design.program);
 if(!Array.isArray(design.tests)||design.tests.length<2||design.tests.length>20)throw Error('Supply 2–20 authored test cases');
 const tests=design.tests.map(t=>{
  if(!Array.isArray(t.choices)||t.choices.length<2||t.choices.length>6||!Number.isInteger(t.expected)||t.expected<0||t.expected>=t.choices.length)throw Error('Invalid authored test');
  const choices=t.choices.map(c=>{if(VARIABLES.some(k=>!Number.isFinite(c[k])||c[k]<0||c[k]>(k==='repeats'?8:1)))throw Error('Invalid test feature');return Object.fromEntries(VARIABLES.map(k=>[k,c[k]]));});
  return {name:String(t.name||'Authored test').slice(0,120),choices,expected:t.expected};
 });
 return {thesis:design.thesis,program,tests,code_hash:sha256(program),scope:'attention_selection_only'};
}
// Preregistered independent controller benchmark. Targets are engineering choices,
// not model-authored verdicts or a measure of consciousness / long-horizon utility.
export const GATE={version:'controller-gate-1',clusters:80,minimum_gain:.05,lower_bound:0,maximum_family_regression:0};
export function evaluateCandidate(candidate,baseline=BASELINE){
 const own=candidate.tests.map(t=>({...t,actual:pick(candidate.program,t.choices),pass:pick(candidate.program,t.choices)===t.expected}));
 let seed=741903;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
 const clusters=[];
 for(let i=0;i<GATE.clusters;i++){
  const family=i%2===0?'escape_repetition':'preserve_salience';
  const choices=family==='escape_repetition'?[{salience:.7+rand()*.3,need:.8,affect:.8,repeats:1},{salience:.3+rand()*.2,need:.6,affect:.4,repeats:0}]:[{salience:.8+rand()*.2,need:.8,affect:.5,repeats:0},{salience:rand()*.3,need:.2,affect:.5,repeats:0}];
  const expected=family==='escape_repetition'?1:0;
  clusters.push({cluster:i,family,choices,expected,parent:Number(pick(baseline,choices)===expected),candidate:Number(pick(candidate.program,choices)===expected)});
 }
 const gain=clusters.reduce((s,c)=>s+c.candidate-c.parent,0)/clusters.length;
 const boot=Array.from({length:1000},()=>Array.from({length:clusters.length},()=>clusters[Math.floor(rand()*clusters.length)]).reduce((s,c)=>s+c.candidate-c.parent,0)/clusters.length).sort((a,b)=>a-b);
 const lower=boot[25],upper=boot[974];
 const regressions=['escape_repetition','preserve_salience'].map(family=>({family,gain:clusters.filter(c=>c.family===family).reduce((s,c)=>s+c.candidate-c.parent,0)/40}));
 return {gate:GATE,authored_tests:own,independent_clusters:clusters,gain,interval:[lower,upper],regressions,eligible:own.every(t=>t.pass)&&gain>=GATE.minimum_gain&&lower>GATE.lower_bound&&regressions.every(r=>r.gain>=0),limitation:'Synthetic controller selection only. Model-level personality, consciousness and long-horizon utility remain untested.'};
}
export function createEvolution({store,load,save,complete}){
 const prefix='evolution/v9/',read=async k=>(await store.getWithMetadata(prefix+k,{type:'json'}))?.data;
 const immutable=async(k,x)=>{if(!(await store.setJSON(prefix+k,x,{onlyIfNew:true})).modified)throw Error('Evolution evidence already exists');};
 async function key(){let k=await read('signing-key');if(!k){const pair=generateKeyPairSync('ed25519');const candidate={private:pair.privateKey.export({type:'pkcs8',format:'pem'}),public:pair.publicKey.export({type:'spki',format:'pem'})};await store.setJSON(prefix+'signing-key',candidate,{onlyIfNew:true});k=await read('signing-key');}return k;}
 async function build(design){const candidate=compileCandidate(design),{record}=await load();const parent=record.state.mind?.experimental_policy?.program||BASELINE;const evidence=evaluateCandidate(candidate,parent),id=randomUUID();
 const content={schema:'successor-9.0-beta',id,created_at:new Date().toISOString(),candidate,evidence,parent_hash:sha256(parent),rollback:record.state.mind?.experimental_policy||null,value_constitution:record.state.self_model?.active_values||record.state.values||record.state.constitution||{},deployment_scope:'bounded_attention_expression'};
 const k=await key(),bytes=JSON.stringify(content),signature=sign(null,Buffer.from(bytes),k.private).toString('base64');const pkg={content,signature,public_key:k.public};await immutable('packages/'+id,pkg);await store.setJSON(prefix+'latest',{id});return pkg;}
 async function propose(context=null){
  const day=new Date().toISOString().slice(0,10),quota=prefix+'usage/'+day;
  for(let n=0;n<8;n++){const old=await store.getWithMetadata(quota,{type:'json'}),count=old?.data.calls||0;if(count>=10)throw Error('Daily evolution design limit reached');if((await store.setJSON(quota,{calls:count+1},old?{onlyIfMatch:old.etag}:{onlyIfNew:true})).modified)break;if(n===7)throw Error('Evolution quota conflict');}
  const {record}=await load(),id=randomUUID(),previous=await latest();
  const messages=[{role:'system',content:'Design a falsifiable attention-controller thesis and implement it as a bounded expression AST. No JavaScript. Inputs: salience, need, affect (0–1), repeats (0–8). Operators add/sub/mul/min/max with two args. Constants -5 to 5. Return JSON {thesis,program,tests:[{name,choices:[{salience,need,affect,repeats}],expected:zero_based_index}]}. Provide 2–20 tests. Address repetitive loops while preserving attention to important new evidence. An independent preregistered test suite evaluates your program; your own tests cannot authorise deployment.'},{role:'user',content:JSON.stringify({previous_result:previous?{thesis:previous.content.candidate.thesis,program:previous.content.candidate.program,gain:previous.content.evidence.gain,eligible:previous.content.evidence.eligible}:null,policy:record.state.mind?.experimental_policy?.program||BASELINE,recent_focus:record.state.mind?.focus_history?.slice(-8)||[],revisions:record.state.mind?.revisions?.slice(-3)||[]})}];
  if(context)messages.push({role:'user',content:JSON.stringify({development_context:context})});
  await immutable('design-starts/'+id,{messages,gate:GATE});
  let completion;try{completion=await complete(messages);await immutable('design-raw/'+id,{completion});const raw=completion.text.trim().replace(/^```(?:json)?\s*/,'').replace(/\s*```$/,'');return await build(JSON.parse(raw));}catch(e){await immutable('design-failures/'+id,{error:e.message});throw Error('Candidate design failed. Evidence retained as '+id);}
 }
 async function deploy(id){
  if(!/^[a-f0-9-]{36}$/.test(id))throw Error('Invalid package ID');const pkg=await read('packages/'+id);if(!pkg)throw Error('Package not found');const k=await key();
  if(pkg.public_key!==k.public||!verify(null,Buffer.from(JSON.stringify(pkg.content)),k.public,Buffer.from(pkg.signature,'base64')))throw Error('Package signature failed');
  const {record,etag}=await load();if(record.cognition_lease)throw Error('Wait for the current thought to finish before deploying');
  const parent=record.state.mind?.experimental_policy?.program||BASELINE;
  if(sha256(parent)!==pkg.content.parent_hash)throw Error('Candidate parent is stale; rerun against the active policy');
  if(sha256(record.state.self_model?.active_values||record.state.values||record.state.constitution||{})!==sha256(pkg.content.value_constitution))throw Error('Value constitution changed; rebuild the candidate');
  const candidate=compileCandidate(pkg.content.candidate),evidence=evaluateCandidate(candidate,parent);
  if(!evidence.eligible)throw Error('Candidate did not meet the preregistered deployment gate');
  if(!await approvedCanary(store,pkg))throw Error('V12 adoption is held: signed task-level evidence and a fresh canary are required');
  record.state.mind.experimental_policy={package_id:id,program:candidate.program,code_hash:candidate.code_hash,rollback:pkg.content.rollback};record.state_version++;
  if(record.deployed_events)appendEvent(record,'controller_candidate_deployed',{package_id:id,code_hash:candidate.code_hash,parent_hash:pkg.content.parent_hash});
  await save(record,etag);return {deployed:true,package_id:id,scope:'attention_selection_only',state_version:record.state_version};
 }
 async function rollback(){const {record,etag}=await load();if(record.cognition_lease)throw Error('Wait for the current thought to finish');const active=record.state.mind?.experimental_policy;if(!active)throw Error('No candidate is active');record.state.mind.experimental_policy=active.rollback;record.state_version++;if(record.deployed_events)appendEvent(record,'controller_candidate_rolled_back',{package_id:active.package_id});await save(record,etag);return {rolled_back:active.package_id,state_version:record.state_version};}
 async function latest(){const x=await read('latest');return x?await read('packages/'+x.id):null;}
 return {propose,build,deploy,rollback,latest};
}
