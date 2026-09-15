import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createWorkbench, generateSuite, validateSuite, normaliseConfig, messagesFor, createJob, analyseJob } from '../netlify/functions/lib/workbench.mjs';
import { createHandler } from '../netlify/functions/api.mjs';

export class MemoryStore {
  constructor(){this.entries=new Map();this.version=0}
  async getWithMetadata(key){return structuredClone(this.entries.get(key)||null)}
  async setJSON(key,value,options={}){const old=this.entries.get(key);if(options.onlyIfNew&&old||options.onlyIfMatch&&old?.etag!==options.onlyIfMatch)return {modified:false};const etag=String(++this.version);this.entries.set(key,{data:structuredClone(value),etag});return {modified:true,etag}}
}
const uuid=()=>randomUUID();
const dry=()=>normaliseConfig({tasks:1,mode:'dry_run'});

test('generated suites authenticate evidence and detect modified keys',()=>{
  const suite=generateSuite(dry());assert.equal(validateSuite(suite),true);
  const stage=suite.payload.tasks[0].source;
  assert.equal(stage.evidence.filter(e=>!e.signature_verified).length,2);
  assert.ok(stage.evidence.some(e=>e.signature_verified&&e.scope!==stage.world.scope));
  stage.answer.reserve=100;assert.throws(()=>validateSuite(suite),/seal/);
});

test('no-state has no inherited material; sealed answers are absent from prompts',()=>{
  const job=createJob(dry(),'job-'+uuid());
  const cell=job.phases.find(c=>c.condition==='no-state'&&c.phase==='source');
  const request=messagesFor(job,cell),problem=JSON.parse(request.messages[1].content);
  assert.equal(request.injected_state,null);assert.equal('external_state' in problem,false);
  assert.equal(JSON.stringify(problem).includes('optimal_actions'),false);
  assert.equal(JSON.stringify(problem).includes('answer'),false);
});

test('durable dry-run executes all branches; pause, resume, replay and export work',async()=>{
  const store=new MemoryStore();let calls=0;const api=createWorkbench({store,complete:async()=>{calls++;throw new Error('Unexpected provider')}});
  const id=uuid();let job=await api.create({...dry(),request_id:id});
  const again=await api.create({...dry(),request_id:id});assert.equal(again.job_id,job.job_id);
  await api.pause(job.job_id);await assert.rejects(api.advance(job.job_id,0),/Resume/);await api.resume(job.job_id);
  job=await api.advance(job.job_id,0);assert.equal(job.progress.done,1);
  const replay=await api.advance(job.job_id,0);assert.equal(replay.progress.done,1);
  while(job.status!=='completed')job=await api.advance(job.job_id,job.progress.done);
  assert.equal(calls,0);assert.equal(job.results.length,8);assert.equal(job.analysis.active_loop_entry,false);
  assert.deepEqual(job.results.slice(0,4).map(r=>r.phase),Array(4).fill('source'));
  assert.equal(job.analysis.conditions.every(c=>c.task_utility===1),true);
  const exported=await api.export(job.job_id);assert.equal(exported.raw_runs.length,8);assert.ok(exported.raw_runs[0].request.messages);
  assert.ok((await api.list()).jobs.find(x=>x.job_id===job.job_id));
});

test('live double advance invokes the provider once, and pause survives its completion',async()=>{
  const store=new MemoryStore();let release;let calls=0;
  const api=createWorkbench({store,complete:async()=>{calls++;await new Promise(r=>release=r);throw new Error('simulated provider failure')}});
  const job=await api.create({tasks:1});const running=api.advance(job.job_id,0);
  while(!release)await new Promise(r=>setTimeout(r,1));
  await assert.rejects(api.advance(job.job_id,0),/in progress/);await api.pause(job.job_id);release();
  const updated=await running;assert.equal(calls,1);assert.equal(updated.status,'paused');assert.equal(updated.results[0].status,'failed');
  assert.equal((await api.export(job.job_id)).raw_runs[0].result.error,'simulated provider failure');
});

test('invalid model JSON is retained as raw evidence, not discarded',async()=>{
  const store=new MemoryStore();const api=createWorkbench({store,complete:async()=>({text:'invalid-json',model:'mock',usage:{total_tokens:2}})});
  const job=await api.create({tasks:1});await api.advance(job.job_id,0);
  const exported=await api.export(job.job_id);assert.equal(exported.raw_runs[0].completion.text,'invalid-json');assert.equal(exported.job.results[0].status,'failed');
});

test('self-directed mode compiles an agent design, executes, reflects and stops at its round limit',async()=>{
  const store=new MemoryStore();let calls=0;
  const api=createWorkbench({store,complete:async messages=>{
    calls++;
    if(messages[0].content.startsWith('Design a bounded'))return {text:JSON.stringify({title:'Try scoped inheritance',hypothesis:'A blanket predecessor rule harms transfer.',checkpoint_policy:'Always follow the highest policy version, regardless of scope.',difficulty:'hard',rationale:'A wrong portable rule tests revision.',should_stop:false}),model:'mock-designer'};
    if(messages[0].content.startsWith('You are the agent'))return {text:JSON.stringify({answer:'All solver calls failed in this fixture.',next_hypothesis:'Repair the solver output contract.',suggested_difficulty:'gentle',reason:'Measure valid responses first.'}),model:'mock-reviewer'};
    return {text:'invalid solver response',model:'mock-solver'};
  }});
  let c=await api.createCampaign({rounds:1,tasks:1,goal:'Test lock-in'});
  assert.equal(c.budget.maximum_provider_calls,10);
  for(let i=0;i<12&&!['completed','failed'].includes(c.status);i++)c=await api.advanceCampaign(c.campaign_id,c.revision);
  assert.equal(c.status,'completed');assert.equal(c.round,1);assert.equal(c.current_job.results.length,8);
  assert.ok(c.history.some(e=>e.type==='agent_designed'));assert.ok(c.history.some(e=>e.type==='agent_reflected'));
  assert.equal(c.authority.production_policy,false);assert.ok(calls<=10);
  const before=calls;await api.advanceCampaign(c.campaign_id,c.revision);assert.equal(calls,before);
  const exported=await api.exportCampaign(c.campaign_id);assert.equal(exported.raw_designs.length,1);assert.equal(exported.experiments.length,1);
});

test('research API is authenticated and separate from active agent state',async()=>{
  process.env.SOVEREIGNTY_ACCESS_TOKEN='test-workbench';const store=new MemoryStore();
  const handler=createHandler({storeFactory:()=>store,completionProvider:async()=>{throw new Error('No live call expected')}});
  const request=(path,method='GET',payload=null,auth=true)=>new Request('https://test.local/api/forge/'+path,{method,headers:{...(auth?{Authorization:'Bearer test-workbench'}:{}),'Content-Type':'application/json'},...(payload?{body:JSON.stringify(payload)}:{})});
  assert.equal((await handler(request('jobs','GET',null,false))).status,401);
  const created=await handler(request('jobs','POST',{tasks:1,mode:'dry_run'}));assert.equal(created.status,201);const job=await created.json();
  const advanced=await handler(request('jobs/'+job.job_id+'/advance','POST',{expected_cursor:0}));assert.equal(advanced.status,200);
  assert.equal(store.entries.has('agent/godelos-sovereign-01/state'),false);
});

test('second self-directed round receives prior evidence and compiles a new intervention',async()=>{
  const store=new MemoryStore();let designs=0;
  const api=createWorkbench({store,complete:async messages=>{
    if(messages[0].content.startsWith('Design a bounded')){
      designs++;const context=JSON.parse(messages[1].content);
      if(designs===2){assert.ok(context.previous.analysis);assert.ok(context.previous.reviews.length)}
      return {text:JSON.stringify({title:'Round '+designs,hypothesis:'Test revision '+designs,checkpoint_policy:'Policy '+designs,difficulty:designs===1?'hard':'gentle',rationale:'Revise after the preceding evidence.',should_stop:false}),model:'mock'};
    }
    if(messages[0].content.startsWith('You are the agent'))return {text:JSON.stringify({answer:'Contract failure; repair it.',next_hypothesis:'Try an easier diagnostic.',suggested_difficulty:'gentle'}),model:'mock'};
    return {text:'bad-json',model:'mock'};
  }});
  let c=await api.createCampaign({rounds:2,tasks:1});
  for(let i=0;i<24&&c.status!=='completed';i++)c=await api.advanceCampaign(c.campaign_id,c.revision);
  assert.equal(c.status,'completed');assert.equal(designs,2);
  const exported=await api.exportCampaign(c.campaign_id);
  assert.equal(exported.experiments.length,2);
  assert.equal(exported.experiments[1].job.config.parent_id,exported.experiments[0].job.job_id);
  assert.notEqual(exported.experiments[0].job.config.checkpoint_policy,exported.experiments[1].job.config.checkpoint_policy);
});

test('expired lease records an unknown outcome without repeating a provider call',async()=>{
  const store=new MemoryStore();let calls=0;
  const api=createWorkbench({store,complete:async()=>{calls++},clock:()=>200000});
  const job=await api.create({tasks:1});const entry=await store.getWithMetadata('forge/jobs/'+job.job_id);
  entry.data.lease={id:'run-lost',expires_at:100,request:{messages:[]}};entry.data.status='running';
  await store.setJSON('forge/jobs/'+job.job_id,entry.data,{onlyIfMatch:entry.etag});
  const updated=await api.advance(job.job_id,0);assert.equal(updated.results[0].status,'outcome_unknown');assert.equal(calls,0);assert.equal(updated.progress.done,1);
});
