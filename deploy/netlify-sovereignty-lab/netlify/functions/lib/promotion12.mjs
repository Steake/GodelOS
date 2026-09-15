import {generateKeyPairSync,sign,verify,randomUUID} from 'node:crypto';
import {sha256,appendEvent} from './core.mjs';
export const PROMOTION_PREFIX='promotion/v12/';
export const PROMOTION_GATE={schema:'promotion-gate-12.1',minimum_gain:.1,minimum_clusters:48,lower_bound:0,maximum_regression:0};
export function judgeEvidence(e,codeHash,parentHash){
 const reasons=[];
 if(e?.code_hash!==codeHash||e?.parent_hash!==parentHash)reasons.push('Evidence is not bound to this candidate and parent');
 if(e?.provenance!=='replayed_task_verifier'||!e?.seal_hash)reasons.push('Independent sealed task verification is missing');
 if(e?.scope!=='long_horizon_task_utility')reasons.push('Synthetic attention scores do not establish task utility');
 if(!Number.isInteger(e?.clusters)||e.clusters<PROMOTION_GATE.minimum_clusters||!e?.power_adequate)reasons.push('Cluster-aware sample requirement is unmet');
 if(!Number.isFinite(e?.gain)||e.gain<PROMOTION_GATE.minimum_gain||!Array.isArray(e?.interval)||e.interval.length!==2||!e.interval.every(Number.isFinite)||e.interval[0]<=0||e.interval[1]<e.interval[0])reasons.push('Preregistered effect or uncertainty threshold is unmet');
 if(!Array.isArray(e?.family_gains)||!e.family_gains.length||e.family_gains.some(x=>!Number.isFinite(x)||x<0)||e?.critical_failures!==0)reasons.push('Regression or incomplete family evidence');
 return {eligible:!reasons.length,reasons,gate:PROMOTION_GATE};
}
export async function approvedCanary(store,pkg){
 const get=async k=>(await store.getWithMetadata(PROMOTION_PREFIX+k,{type:'json'}))?.data;
 const key=await get('signing-key'),approval=await get('approvals/'+pkg.content.id);
 if(await get('revoked/'+pkg.content.id))return false;
 if(!key||!approval||approval.public_key!==key.public||!verify(null,Buffer.from(JSON.stringify(approval.content)),key.public,Buffer.from(approval.signature||'','base64')))return false;
 const c=approval.content;return c.package_hash===sha256(pkg.content)&&c.code_hash===pkg.content.candidate.code_hash&&c.parent_hash===pkg.content.parent_hash&&c.phase==='canary_passed';
}

// The evaluator is a server-owned adapter, never a request-supplied pass flag.
// No production long-horizon adapter exists yet: absence is an explicit HOLD.
export function createPromotion({store,load,save,evaluate=null,clock=()=>Date.now()}){
 const get=async k=>(await store.getWithMetadata(PROMOTION_PREFIX+k,{type:'json'}))?.data;
 const immutable=async(k,x)=>{if(!(await store.setJSON(PROMOTION_PREFIX+k,x,{onlyIfNew:true})).modified)throw Error('Promotion evidence is immutable');};
 async function signed(content){
  let k=await get('signing-key');if(!k){const p=generateKeyPairSync('ed25519');await store.setJSON(PROMOTION_PREFIX+'signing-key',{private:p.privateKey.export({format:'pem',type:'pkcs8'}),public:p.publicKey.export({format:'pem',type:'spki'})},{onlyIfNew:true});k=await get('signing-key');}
  return {content,signature:sign(null,Buffer.from(JSON.stringify(content)),k.private).toString('base64'),public_key:k.public};
 }
 async function candidate(id){
  if(!/^[a-f0-9-]{36}$/.test(id))throw Error('Invalid package ID');
  const pkg=(await store.getWithMetadata('evolution/v9/packages/'+id,{type:'json'}))?.data,key=(await store.getWithMetadata('evolution/v9/signing-key',{type:'json'}))?.data;
  if(!pkg||!key||pkg.public_key!==key.public||!verify(null,Buffer.from(JSON.stringify(pkg.content)),key.public,Buffer.from(pkg.signature,'base64')))throw Error('Successor signature failed');
  return pkg;
 }
 async function review(id){
  const pkg=await candidate(id);
  const evidence=evaluate?await evaluate({phase:'review',package:pkg}):null;
  const judgment=judgeEvidence(evidence,pkg.content.candidate.code_hash,pkg.content.parent_hash);
  const result={id:randomUUID(),package_id:id,phase:judgment.eligible?'ready_for_shadow_canary':'held',judgment,evidence,at:clock()};await immutable('reviews/'+result.id,result);await store.setJSON(PROMOTION_PREFIX+'latest-review',result);return result;
 }
 async function canary(id){
  const pkg=await candidate(id),reviewed=await review(id);if(!reviewed.judgment.eligible)return reviewed;
  const evidence=await evaluate({phase:'canary',package:pkg});
  const judgment=judgeEvidence(evidence,pkg.content.candidate.code_hash,pkg.content.parent_hash);
  if(evidence?.seal_hash===reviewed.evidence.seal_hash){judgment.eligible=false;judgment.reasons.push('Canary reused the review holdout');}
  if(!judgment.eligible){const result={package_id:id,phase:'canary_failed',judgment,evidence};await immutable('canary-failures/'+randomUUID(),result);return result;}
  const approval=await signed({schema:'signed-canary-12.1',package_id:id,phase:'canary_passed',package_hash:sha256(pkg.content),code_hash:pkg.content.candidate.code_hash,parent_hash:pkg.content.parent_hash,value_constitution:pkg.content.value_constitution,rollback_target:pkg.content.rollback,evidence_bundle:{review:reviewed,evidence},at:clock()});
  await immutable('approvals/'+id,approval);return {phase:'canary_passed',approval};
 }
 async function monitor(){
  const {record,etag}=await load(),active=record.state.mind?.experimental_policy;if(!active)return {phase:'no_active_successor'};
  const pkg=await candidate(active.package_id),evidence=evaluate?await evaluate({phase:'monitor',package:pkg}):null;
  if(!evidence)return {phase:'monitor_unavailable',reason:'No task-verifier monitoring adapter is installed'};
  const judgment=judgeEvidence(evidence,pkg.content.candidate.code_hash,pkg.content.parent_hash);
  await immutable('monitor/'+randomUUID(),{package_id:active.package_id,evidence,judgment});
  if(judgment.eligible)return {phase:'healthy'};
  await store.setJSON(PROMOTION_PREFIX+'revoked/'+active.package_id,{at:clock(),judgment},{onlyIfNew:true});
  if(record.cognition_lease)return {phase:'rollback_waiting_for_episode',judgment};
  record.state.mind.experimental_policy=active.rollback||null;record.state_version++;
  if(record.deployed_events)appendEvent(record,'successor_regression_rollback',{package_id:active.package_id,judgment});
  await save(record,etag);return {phase:'rolled_back',package_id:active.package_id,judgment};
 }
 async function status(){return {gate:PROMOTION_GATE,adapter_installed:!!evaluate,latest_review:await get('latest-review'),deployment_requirement:'Signed fresh task-level review and separate canary; legacy synthetic gate alone cannot deploy'};}
 return {review,canary,monitor,status};
}
