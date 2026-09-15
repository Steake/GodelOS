/* A conversation companion, not a second agent or simulated activity feed. */
(()=>{
 const chat=document.querySelector('.mind-conversation');if(!chat)return;
 const release=document.querySelector('a[href="/release12.html"]');if(release){release.href='/release13.html';release.textContent='About V13 ↗';}
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 const panel=el('section','life13');panel.setAttribute('aria-label','Developing threads');
 const head=el('div','life13-heading'),orb=el('span','life13-weather');orb.setAttribute('aria-hidden','true');
 const title=el('div'),name=el('strong',null,'Room to think'),weather=el('p',null,'Connect to see what is developing.');title.append(name,weather);head.append(orb,title);
 const advance=el('button','life13-step','Follow a thought');advance.type='button';head.append(advance);
 const notice=el('p','life13-notice');notice.setAttribute('role','status');
 const invitations=el('div','life13-invitations'),details=el('details','life13-inspect'),summary=el('summary',null,'What is developing?');
 const body=el('div','life13-body');details.append(summary,body);panel.append(head,notice,invitations,details);
 chat.querySelector('.md-chat-intro')?.replaceWith(panel);
 const seedMessage=text=>{const input=document.getElementById('mindMessage');if(input.value.trim()){notice.textContent='Your draft is still there. Send or clear it before picking up this thread.';input.focus();return;}input.value=text;input.dispatchEvent(new Event('input',{bubbles:true}));input.focus();};
 let pending=false,queuedInquiries=0,lastRenderKey='';
 advance.onclick=async()=>{
  if(pending)return;
  if(!queuedInquiries){document.getElementById('mindStep').click();return;}
  pending=true;advance.disabled=true;notice.textContent='Running one fresh-model branch of the queued inquiry. The result will be recorded here; your conversation remains available.';
  try{const r=await apiFetch('/api/living/tick',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request_id:crypto.randomUUID()})}),x=await r.json();if(!r.ok)throw Error(x.error||'The step could not complete.');notice.textContent=x.deferred?'Waiting: '+x.reason.replaceAll('_',' '):x.reply||'Step completed.';document.dispatchEvent(new Event('mind:refresh'));}
  catch(e){notice.textContent=e.message;}finally{pending=false;advance.disabled=false;}
 };
 document.addEventListener('mind:snapshot',({detail:s})=>{
  const agent=s.agent,m=agent?.mind;if(!m)return;const life=m.living||{events:[],inquiries:[]},affect=agent.affect||{};
  queuedInquiries=life.inquiries.filter(q=>['pending','recorded'].includes(q.status)).length;
  name.textContent=agent.name?`${agent.name} · room to think`:'Room to think';
  const qualities=[['curiosity','curious'],['wonder','associative'],['social_warmth','open to company'],['frustration','working through friction']].sort((a,b)=>(affect[b[0]]||0)-(affect[a[0]]||0));
  weather.textContent=`${qualities[0][1]} · ${life.inquiries.filter(q=>['pending','recorded'].includes(q.status)).length} open inquiries · episode ${m.tick||0}`;
  weather.title='Computed appraisal and recorded activity—not a measurement of subjective feeling.';
  orb.style.setProperty('--weather-hue',String(155+Math.round((affect.wonder||0)*90)));
  const renderKey=JSON.stringify([agent.beliefs,life,m.outbox]);if(renderKey===lastRenderKey)return;lastRenderKey=renderKey;
  const expanded=new Set([...body.querySelectorAll('details[open]')].map(n=>n.dataset.position));
  body.replaceChildren();
  const opinions=el('section'),h=el('h3',null,'Positions, not a fixed persona');opinions.append(h);
  const beliefs=(agent.beliefs||[]).filter(b=>b.active!==false).slice(-6);
  if(!beliefs.length)opinions.append(el('p',null,'No positions recorded yet. Start with something you genuinely disagree about.'));
  for(const b of beliefs){const card=el('article','life13-thread'),button=el('button',null,b.proposition);button.type='button';button.onclick=()=>seedMessage(`Let’s revisit your recorded position: ${b.proposition}. What do you think now, and what could change your mind?`);card.append(button,el('p',null,`${b.stance} · ${life.opinions?.[b.position_id]?.revision_count||0} recorded refinements / revisions`));const inspect=el('details'),label=el('summary',null,'Reasons & history');inspect.append(label,el('p',null,'For: '+(b.reasons_for||[]).join(' · ')),el('p',null,'Against: '+(b.reasons_against||[]).join(' · ')));for(const event of (life.events||[]).filter(e=>e.refs?.includes(b.position_id)).slice(-4))inspect.append(el('p',null,`Episode ${event.tick} · ${event.kind.replaceAll('_',' ')}: ${event.title}`));card.append(inspect);opinions.append(card);}
  const stream=el('section');stream.append(el('h3',null,'What happened along the way'));
  for(const e of life.events.slice(-8).reverse()){const c=el('article','life13-event');c.append(el('small',null,`${e.kind.replaceAll('_',' ')} · episode ${e.tick}`),el('p',null,e.title));if(e.kind==='association')c.append(el('p','life13-muted',e.detail.idea),el('small',null,'Imagination, not evidence'));if(e.kind==='experiment_result')c.append(el('p','life13-muted',e.detail.scope));stream.append(c);}
  if(!life.events.length)stream.append(el('p',null,'This timeline fills from actual episodes. Nothing here is pre-scripted.'));
  for(const q of life.inquiries.slice(-4)){const row=el('article','life13-inquiry');row.append(el('strong',null,q.question),el('p',null,`${q.status} · two-branch stance retrieval`));const evidence=el('button',null,'Inspect raw evidence');evidence.type='button';evidence.onclick=async()=>{evidence.disabled=true;try{const r=await apiFetch('/api/living/evidence/'+encodeURIComponent(q.id));const x=await r.json();if(!r.ok)throw Error(x.error);let pre=row.querySelector('pre');if(!pre){pre=el('pre');row.append(pre);}pre.textContent=JSON.stringify(x,null,2);}catch(e){notice.textContent=e.message;}finally{evidence.disabled=false;}};row.append(evidence);stream.append(row);}
  for(const [index,node] of [...opinions.querySelectorAll('details')].entries()){node.dataset.position=beliefs[index].position_id;node.open=expanded.has(node.dataset.position);}
  body.append(opinions,stream);invitations.replaceChildren();
  const invitation=(m.outbox||[]).filter(x=>x.status==='awaiting_operator'&&x.event_id).at(-1);
  if(invitation){const card=el('aside','life13-invitation');card.append(el('small',null,'Something it wanted to bring back'),el('p',null,invitation.message));const reply=el('button',null,'Pick up this thread');reply.type='button';reply.onclick=()=>seedMessage(`You wanted to share: “${invitation.message}” — let’s follow that.`);card.append(reply);invitations.append(card);}
 });
})();
