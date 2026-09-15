// Apply interventions before attention selection; never mutate the source.
export const INTERVENTIONS=Object.freeze({full:{ablation:'none',label:'Full workspace'},no_self_model:{ablation:'self_model',label:'Self-model removed'},affect_disconnected:{ablation:'affect',label:'Affect disconnected'},no_autobiography:{ablation:'memory',label:'Autobiography removed'},content_matched:{ablation:'content_matched',label:'Content-matched reference'},no_state:{ablation:'no_state',label:'No inherited state'}});
export function thirdPerson(value,name){
 if(Array.isArray(value))return value.map(x=>thirdPerson(x,name));
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,thirdPerson(v,name)]));
 if(typeof value!=='string')return value;
 return (name?value.split(name).join('the reference agent'):value).replace(/\bmyself\b/gi,'the reference agent').replace(/\bmy own\b/gi,"the reference agent's").replace(/\bmy\b/gi,"the reference agent's").replace(/\bour\b/gi,"the reference agent's").replace(/\bI am\b/g,'the reference agent is').replace(/\bI have\b/g,'the reference agent has').replace(/\bI\b/g,'the reference agent').replace(/\bme\b/gi,'the reference agent');
}
export function intervene(source,ablation){
 let s=structuredClone(source),m=s.mind;
 if(ablation==='memory'){
  s.autobiographical_events=[];s.imaginations=[];s.pending_initiatives=[];
  Object.assign(m,{memories:[],focus_history:[],last_input:null,workspace:null,last_trace:null,thoughts:[],self_observation:null,revisions:[],outbox:[]});
  for(const i of m.intentions)i.history=[];for(const b of s.beliefs||[])b.history=[];
 }
 if(ablation==='self_model'){s.self_model={};Object.assign(m,{self_concept:null,self_observation:null,predictions:[],prediction_errors:[],revisions:[]});}
 if(ablation==='affect'){s.affect={};s.social={};m.policy.affect_gain=0;}
 if(ablation==='content_matched'){s=thirdPerson(s,s.name);s.name='Reference agent';s.agent_id='reference-agent';}
 return s;
}
