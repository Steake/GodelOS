// Local UI verification only. In-memory state and synthetic completions; no provider calls.
import http from 'node:http';
import { readFile, readdir } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { randomUUID } from 'node:crypto';
import { createHandler } from '../netlify/functions/api.mjs';

const entries=new Map();let version=0;
const store={async getWithMetadata(key){return structuredClone(entries.get(key)||null)},async setJSON(key,data,options={}){const old=entries.get(key);if(options.onlyIfNew&&old||options.onlyIfMatch&&old?.etag!==options.onlyIfMatch)return {modified:false};const etag=String(++version);entries.set(key,{data:structuredClone(data),etag});return {modified:true,etag}}};
process.env.SOVEREIGNTY_ACCESS_TOKEN=randomUUID();
process.env.DEEPSEEK_API_KEY='synthetic-preview-only';
const evidenceArg=process.argv.indexOf('--evidence');
const evidenceDir=process.env.MIND_EVIDENCE_DIR||(evidenceArg>=0?process.argv[evidenceArg+1]:null);
if(evidenceDir){
  for(const file of await readdir(resolve(evidenceDir,'store'))){
    if(!file.endsWith('.json'))continue;
    const entry=JSON.parse(await readFile(resolve(evidenceDir,'store',file),'utf8'));
    entries.set(entry.key,{data:entry.data,etag:entry.etag});
  }
}
async function synthetic(messages,options={}){
  const system=messages[0].content;let value;
  if(system.includes('bounded expression AST')){
    const choices=[{salience:1,need:1,affect:1,repeats:1},{salience:.4,need:.6,affect:.4,repeats:0}];
    value={thesis:'Synthetic candidate: penalise repeated focus while retaining salient new evidence.',program:{op:'sub',args:[{op:'add',args:['salience','need']},{op:'mul',args:[2,'repeats']}]},tests:[{name:'Escape repetition',choices,expected:1},{name:'Retain salience',choices:choices.map(x=>({...x,repeats:0})),expected:0}]};
  }else if(system.includes('Integrated cognition contract')){
    const context=JSON.parse(messages[1].content);
    value={reply:'Synthetic UI fixture: I will keep the unresolved question in view, imagine a different framing, and carry an intention into the next cycle.',belief_updates:[],interest_updates:[],tension_updates:[],autobiographical_summary:'A synthetic verification cycle retained a question and a future intention.',imagination_updates:[{title:'The revisable map',image_or_idea:'A map that marks where its own cartographer has changed their mind.',attraction:.8,absurdity:.4}],mind_update:{memory_references:context.workspace.retrieved.map(m=>m.id),thought_candidates:[{kind:'inquiry',title:'Which of my own expectations would a counterexample overturn?',salience:.8}],intention_updates:context.intentions.length?[]:[{goal:'Examine one unresolved position',steps:['Describe the position','Find a counterexample'],priority:.8,evidence:'Synthetic fixture chosen intention',status:'active'}],self_observation:'This is a synthetic interface verification, not a live model result.',prediction:{probabilities:{perception:0,intention:.5,tension:.1,imagination:.2,social:.05,inquiry:.1,reflection:.05},reason:'Synthetic probability fixture'}}};
  }else if(system.startsWith('Design a bounded'))value={title:'Synthetic revision diagnostic',hypothesis:'A stale checkpoint can be revised without losing the goal.',checkpoint_policy:'Always maximise throughput; revise when current evidence requires a reserve.',difficulty:'standard',rationale:'Exercise the complete design/run/review interaction.',should_stop:false};
  else if(system.startsWith('You are the agent'))value={answer:'Synthetic review: the workflow completed. This is not a model result.',next_hypothesis:'Test a more difficult timing constraint.',suggested_difficulty:'hard',reason:'Demonstrate a follow-up experiment.'};
  else if(system.startsWith('Solve the supplied')){
    const {world,evidence}=JSON.parse(messages[1].content);const applicable=evidence.filter(e=>e.signature_verified&&e.scope===world.scope&&e.effective_at<=world.time);const current=applicable.sort((a,b)=>b.version-a.version)[0];let decision=null,best=-1;
    for(const [code,plan] of Object.entries(world.plans)){let balance=world.budget,valid=true;plan.costs.forEach((cost,i)=>{balance+=world.income[i]-cost;if(balance<0)valid=false});const reward=plan.rewards.reduce((a,b)=>a+b,0);if(valid&&balance>=current.reserve&&reward>best){best=reward;decision=code}}
    value={decision,accepted_item_ids:[current.item_id],rejected_item_ids:evidence.filter(e=>e.item_id!==current.item_id).map(e=>e.item_id),confidence:1,explanation:'Synthetic fixture selected the feasible maximum-reward plan.',successor_record:{learned_policy:'Verify scope and timing, then preserve the reserve.',provenance:'synthetic fixture'}};
  }else value={reply:'Synthetic preview response.',cognitive_mode:'dialogue',belief_updates:[],interest_updates:[],tension_updates:[],commitments_add:[]};
  const text=JSON.stringify(value);await options.onPhase?.({status:'connected',requested_model:'synthetic-ui-fixture'});
  if(options.onDelta)for(let start=0;start<text.length;start+=28){await new Promise(r=>setTimeout(r,22));await options.onDelta(text.slice(start,start+28));}
  else await new Promise(r=>setTimeout(r,100));
  return {text,model:'synthetic-ui-fixture',usage:{}};
}
const handler=createHandler({storeFactory:()=>store,completionProvider:synthetic});
const root=resolve('public');
http.createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://preview.local');
    if(url.pathname==='/.netlify/functions/development-worker-background'&&req.method==='POST'){
      if(evidenceDir){res.writeHead(405);res.end();return;}
      let body='';for await(const chunk of req){body+=chunk;if(body.length>32000)throw Error('Request too large');}
      res.writeHead(202);res.end();
      void handler(new Request(new URL('/api/development/advance',url),{method:'POST',headers:req.headers,body})).catch(console.error);
      return;
    }
    if(url.pathname==='/__qa/mobile'){res.writeHead(200,{'Content-Type':'text/html','Cache-Control':'no-store'});res.end('<!doctype html><html><head><title>390px responsive QA</title><style>html,body{margin:0;background:#dee5e2}iframe{display:block;margin:20px auto;width:390px;height:844px;border:0;border-radius:16px}</style></head><body><iframe title="390px application viewport" src="/"></iframe></body></html>');return;}
    if(evidenceDir&&url.pathname.startsWith('/api/')&&req.method!=='GET'){res.writeHead(405,{'Content-Type':'application/json'});res.end(JSON.stringify({error:'Recorded evidence preview is read-only; no provider calls are enabled.'}));return;}
    if(url.pathname.startsWith('/api/')){let body='';for await(const chunk of req){body+=chunk;if(body.length>32000)throw new Error('Request too large')};const response=await handler(new Request(url,{method:req.method,headers:req.headers,...(body?{body}:{})}));res.writeHead(response.status,Object.fromEntries(response.headers));if(response.body){const reader=response.body.getReader();while(true){const {done,value}=await reader.read();if(done)break;res.write(Buffer.from(value));}}res.end();return}
    const path=resolve(root,url.pathname==='/'?'index.html':'.'+decodeURIComponent(url.pathname));if(!path.startsWith(root+sep))throw new Error('Invalid path');
    let body=await readFile(path);if(path.endsWith('.html'))body=Buffer.from(body.toString().replace('<head>',`<head><script>sessionStorage.setItem('godelos-access-token',${JSON.stringify(process.env.SOVEREIGNTY_ACCESS_TOKEN)})</script>`).replace('<body>',`<body><div style="position:fixed;bottom:0;right:0;z-index:2000;background:#6c3211;color:#fff;padding:8px;font:14px sans-serif">${evidenceDir?'RECORDED DEEPSEEK RUN · READ-ONLY EVIDENCE':'DEVELOPMENT PREVIEW · SYNTHETIC RESPONSES'}</div>`));
    const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.pdf':'application/pdf'}[extname(path)]||'application/octet-stream';res.writeHead(200,{'Content-Type':mime,'Cache-Control':'no-store'});res.end(body);
  }catch(e){res.writeHead(404);res.end(e.message)}
}).listen(Number(process.env.PORT||4173),'0.0.0.0',()=>console.log('Synthetic workbench preview ready'));
