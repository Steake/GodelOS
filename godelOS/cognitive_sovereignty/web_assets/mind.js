/* Integrated cognitive operator surface, backed by the same state as chat. */
(() => {
  const el=(tag,copy,cls)=>{const n=document.createElement(tag);if(copy!==undefined)n.textContent=copy;if(cls)n.className=cls;return n;};
  const $=id=>document.getElementById(id);
  const requestId=()=>typeof crypto.randomUUID==='function'?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
  let current=null,busy=false,runRemaining=0,historyTick=-1,sending=false,lastAttentionHold=0;
  window.godelosPrimaryView='mind';
  const panel=el('section',undefined,'view mind');panel.id='mind';
  panel.innerHTML=`
    <div class="mind-top"><div><span class="mind-kicker">GÖDELOS · V8.1</span><p id="mindCadence">Connect to the persistent agent.</p></div><span id="mindTick" class="mind-chip">Cycle 0</span></div>
    <div class="mind-toolbar"><button id="mindStep" class="mind-primary">Think one cycle</button><label>Explore <select id="mindRounds"><option>3</option><option selected>6</option><option>12</option></select> cycles</label><button id="mindRun">Begin</button><button id="mindPause">Pause autonomous thought</button><span id="mindStatus" role="status"></span></div>
    <div class="mind-alert" id="mindError" role="alert" hidden></div>
    <div class="mind-alert" id="mindRecovery" hidden><p>An earlier cycle expired without a confirmed outcome. Its evidence and call reservation are retained. Recovery allows a new cycle; it does not repeat or invent the missing result.</p><button id="mindRecover">Acknowledge unknown outcome and recover</button></div>
    <div class="mind-grid">
      <section class="mind-card mind-focus"><div class="mind-kicker">CURRENT WORKSPACE</div><h3 id="mindFocus">No integrated cycle yet</h3><p id="mindWhy">The first cycle will select a focus from the agent's recorded interests, intentions and drives.</p><details class="mind-options"><summary>Why this focus?</summary><p class="mind-muted">These are the competing attention scores used by the controller, not confidence in the answer.</p><div id="mindBids"></div></details><div class="mind-caption">Each focus feeds cognition, memory, drive satisfaction and the next attention selection.</div></section>
      <section class="mind-card mind-conversation"><h3>Talk to the agent</h3><div id="mindMessages" aria-live="polite"><p class="mind-muted">Your message enters the same attention and memory loop as autonomous thought.</p></div><form id="mindChat"><label for="mindMessage">Message</label><textarea id="mindMessage" rows="3" placeholder="Ask a question, challenge a position, or suggest something to explore…"></textarea><button class="mind-primary">Send</button></form></section>
      <section class="mind-card"><h3>What pulls its attention</h3><div id="mindDrives"></div><p id="mindAffect" class="mind-muted"></p><div id="mindAffectBars"></div></section>
      <section class="mind-card"><h3>Intentions that persist</h3><div id="mindIntentions"></div></section>
      <section class="mind-card"><h3>Its model of itself</h3><p id="mindSelf"></p><div id="mindForecast"></div><h4>Recorded attention</h4><p id="mindObserved" class="mind-muted"></p></section>
      <section class="mind-card"><h3>Imagination and invitations</h3><div id="mindIdeas"></div><div id="mindInvitations"></div></section>
      <section class="mind-card"><h3>Memory carried forward</h3><div id="mindMemories"></div></section>
      <section class="mind-card"><h3>Proposed self-revisions</h3><div id="mindRevisions"></div><button id="mindEvidence">Download last cycle evidence</button></section>
    </div>`;
  document.querySelector('main').append(panel);
  const grid=panel.querySelector('.mind-grid');
  grid.prepend(panel.querySelector('.mind-conversation'));
  const guide=el('details',undefined,'mind-guide');
  guide.innerHTML='<summary>What are we building and testing?</summary><p>A persistent agent whose memories, interests and intentions can influence its next decision. Conversation and autonomous thought use the same recorded state.</p><ol><li><b>Talk:</b> introduce an idea or challenge a held position.</li><li><b>Explore:</b> run several cycles and see what it chooses to pursue.</li><li><b>Test:</b> compare matched branches with parts of the state removed. A changed answer alone is not enough: look for repeatable differences linked to the intervention.</li></ol><p>Attention and affect scores are controller variables. They show how this architecture operates; they do not measure subjective experience.</p>';
  panel.querySelector('.mind-toolbar').before(guide);
  for(const card of [...grid.children].slice(2)){
    const details=el('details',undefined,'mind-card mind-detail');
    const heading=card.querySelector('h3');details.append(el('summary',heading.textContent));heading.remove();
    while(card.firstChild)details.append(card.firstChild);card.replaceWith(details);
  }

  const nav=el('button','Your agent');$('nav').prepend(nav);
  function open(){document.querySelectorAll('.view,#nav button').forEach(n=>n.classList.remove('active'));panel.classList.add('active');nav.classList.add('active');$('viewTitle').textContent=panel.dataset.pane==='activity'?'Activity':(current?.agent?.name||'Sovereign-01');$('viewEyebrow').textContent='Integrated cognition';$('viewSub').textContent=panel.dataset.pane==='activity'?'Attention, memory and self-directed thought':'Persistent agent';}
  async function api(path,payload){const r=await apiFetch(path,payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}:{});const x=await r.json();if(!r.ok)throw Error(x.error||'Request failed');return x;}
  async function streamApi(kind,payload,onEvent){
    const response=await apiFetch('/api/mind/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,...payload})});
    if(!response.ok){let problem={};try{problem=await response.json();}catch{}throw Error(problem.error||`Request failed (${response.status})`);}
    if(!response.body)throw Error('This browser did not receive a streaming response.');
    const reader=response.body.getReader(),decoder=new TextDecoder();let pending='',result=null,failure=null;
    const consume=line=>{if(!line.trim())return;let event;try{event=JSON.parse(line);}catch{throw Error('The live response stream was malformed.');}onEvent(event);if(event.event==='complete')result=event.result;if(event.event==='error')failure=Error(event.message||'The model call failed.');};
    while(true){const {done,value}=await reader.read();pending+=decoder.decode(value||new Uint8Array(),{stream:!done});const lines=pending.split('\n');pending=lines.pop()||'';for(const line of lines)consume(line);if(done)break;}
    if(pending.trim())consume(pending);if(failure)throw failure;if(!result)throw Error('The live response ended before completion.');return result;
  }
  function replyPrefix(raw){
    const found=/"reply"\s*:\s*"/.exec(raw);if(!found)return '';
    let out='',i=found.index+found[0].length;
    for(;i<raw.length;i++){const c=raw[i];if(c==='"')break;if(c!=='\\'){out+=c;continue;}if(++i>=raw.length)break;const e=raw[i];if(e==='n')out+='\n';else if(e==='r')out+='\r';else if(e==='t')out+='\t';else if(e==='b')out+='\b';else if(e==='f')out+='\f';else if(e==='u'){const code=raw.slice(i+1,i+5);if(!/^[0-9a-f]{4}$/i.test(code))break;out+=String.fromCharCode(parseInt(code,16));i+=4;}else out+=e;}
    return out;
  }
  function bar(label,value,max=1){const row=el('div',undefined,'mind-bar');row.append(el('span',label));const meter=el('meter');meter.min=0;meter.max=max;meter.value=Math.max(0,Number(value)||0);row.append(meter,el('b',(Number(value)||0).toFixed(2)));return row;}
  function cards(id,items,fn,empty){const n=$(id);n.replaceChildren();if(!items?.length)n.append(el('p',empty,'mind-muted'));else items.forEach(item=>n.append(fn(item)));}
  function box(title,copy,meta){const n=el('article',undefined,'mind-item');n.append(el('h4',title),el('p',copy));if(meta)n.append(el('small',meta));return n;}
  function render(s){current=s;const a=s.agent,m=a.mind;if(!m)return;
    window.renderModelStatus?.(s);$('agentName').textContent=a.name;$('agentMeta').textContent=`${a.agent_id} · state v${s.state_version}`;
    $('chainStatus').textContent=s.event_chain_valid?'Event chain verified':'Integrity failure';
    $('systemStatus').textContent=s.event_chain_valid?'STATE · VERIFIED':'FAULT';
    $('mindRecovery').hidden=!(s.cognition_lease&&s.cognition_lease.expires_at<=Date.now());
    $('mindTick').textContent=`Cycle ${m.tick} · State ${s.state_version}`;
    $('mindCadence').textContent=s.autonomy?.enabled?`Scheduled every ${s.autonomy.interval_minutes} minutes, up to ${s.autonomy.daily_limit} background cycles per day. ${s.mind_control?.paused?'Autonomous thought is paused.':'Continues without an open browser.'}`:'Manual mode. Choose one thought cycle or a short exploration. Background thought is not enabled.';
    $('mindPause').textContent=s.mind_control?.paused?'Resume autonomous thought':'Pause autonomous thought';
    const w=m.workspace;
    if(w){$('mindFocus').textContent=w.focus.title;$('mindWhy').textContent=`${w.focus.kind} · ${w.focus.provenance.replaceAll('_',' ')} · ${w.retrieved.length} retrieved memories`;$('mindBids').replaceChildren();[w.focus,...w.competitors].forEach(c=>$('mindBids').append(bar(c.kind,c.score,1.5)));}
    $('mindDrives').replaceChildren();Object.entries(m.drives).forEach(([k,v])=>$('mindDrives').append(bar(k,v)));
    $('mindAffect').textContent=`${a.affect?.label||'appraisal'}: ${a.affect?.trigger||'No recorded trigger'}`;
    $('mindAffectBars').replaceChildren();['curiosity','wonder','frustration','social_warmth'].forEach(k=>$('mindAffectBars').append(bar(k.replaceAll('_',' '),a.affect?.[k])));
    cards('mindIntentions',m.intentions.slice().reverse(),i=>box(i.goal,i.steps[i.step]||'Review recorded outcome',`${i.status} · Step ${Math.min(i.step+1,i.steps.length)}/${i.steps.length} · ${i.history.at(-1)?.reason||i.origin}`),'No intention has been formed yet.');
    $('mindSelf').textContent=m.self_observation?.text||m.self_concept;
    $('mindObserved').textContent=m.focus_history.slice(-8).map(h=>`${h.tick}: ${h.kind}`).join(' · ')||'No events recorded yet.';
    const err=m.prediction_errors.at(-1);$('mindForecast').replaceChildren(el('p',err?(err.brier===null?`Observed ${err.observed} after an external interruption. The autonomous forecast was excluded from calibration.`:`Earlier attention forecast → observed ${err.observed}. Brier error ${err.brier.toFixed(3)} on a 0–2 scale; lower is better. Context: ${err.context}.`):'The first prediction will be compared with the following cycle.','mind-muted'));
    cards('mindIdeas',(a.imaginations||[]).slice(-3).reverse(),i=>box(i.title,i.image_or_idea,'Imagined candidate · '+i.status),'No imagined candidates recorded yet.');
    cards('mindInvitations',m.outbox.slice(-3).reverse(),i=>box('An invitation',i.message,i.reason),'No invitation awaiting you.');
    cards('mindMemories',m.memories.slice(-5).reverse(),i=>box(`Cycle ${i.tick} · ${i.source_kind}`,i.summary,`${i.provenance} · salience ${i.salience.toFixed(2)}`),'The first cycle will consolidate an episode.');
    cards('mindRevisions',m.revisions.slice(-3).reverse(),r=>box(r.change,r.reason,`Proposed test: ${r.test} · ${r.status}`),'No proposed change yet.');
    if(!busy)$('mindStatus').textContent=s.cognition_lease?'A cycle is running.':s.mind_control?.paused?'Paused · conversation available':s.autonomy?.status?.blocked?'Background thought needs attention':'Ready';
    document.dispatchEvent(new CustomEvent('mind:snapshot',{detail:s}));
  }
  async function refresh(){render(await api('/api/snapshot'));const version=JSON.stringify([current.state_version,current.inbox]);if(version!==historyTick){const history=await api('/api/mind/history'),log=$('mindMessages'),oldScroll=log.scrollTop,atEnd=log.scrollHeight-log.clientHeight-oldScroll<70;log.replaceChildren();for(const episode of history.episodes){if(episode.input)message('You',episode.input);message(`Cycle ${episode.tick} · ${episode.mode}`,episode.reply);}if(!history.episodes.length)log.append(el('p','Start with a question. Your message becomes part of the same memory and attention loop as its own exploration.','mind-muted'));for(const pending of (current.inbox||[]).filter(x=>x.status!=='completed')){message('You · '+pending.status.replaceAll('_',' '),pending.message);if(!['queued','running'].includes(pending.status)){const retry=el('button','Return message to draft');retry.type='button';retry.onclick=()=>{if(!$('mindMessage').value){$('mindMessage').value=pending.message;$('mindMessage').dispatchEvent(new Event('input'));$('mindMessage').focus();}};log.lastElementChild.append(retry);}}if(!atEnd)log.scrollTop=oldScroll;historyTick=version;}}
  async function drainInbox(){if(sending||busy)return;if((current?.inbox||[]).some(x=>x.status==='queued')&&!current?.cognition_lease){sending=true;try{await cycle();}finally{sending=false}}}
  function fail(e){$('mindError').hidden=false;$('mindError').textContent=e.message;}
  function message(label,copy){const n=box(label.replaceAll('_',' '),copy);if(label.startsWith('You'))n.classList.add('user-message');$('mindMessages').append(n);$('mindMessages').scrollTop=$('mindMessages').scrollHeight;return n;}
  async function cycle(payload={},contact=false){if(busy)return false;busy=true;$('mindError').hidden=true;$('mindStep').disabled=true;$('mindRun').disabled=true;$('mindStatus').textContent='Securing input';
    const id=payload.request_id||requestId(),bubble=message((current?.agent?.name||'Sovereign-01')+' · live',''),copy=bubble.querySelector('p');bubble.classList.add('streaming-message');let raw='',shown='';
    window.godelosLiveOperation?.begin({request_id:id,kind:contact?'conversation':'thought cycle'});
    try{const r=await streamApi(contact?'chat':'cycle',{...payload,request_id:id},event=>{
      if(event.event==='token'){raw+=event.text||'';const next=replyPrefix(raw);if(next!==shown){shown=next;copy.textContent=shown;window.godelosLiveOperation?.reply(shown);$('mindMessages').scrollTop=$('mindMessages').scrollHeight;}}
      if(event.event==='phase'){window.godelosLiveOperation?.phase(event);const labels={queued:'Queued',reserved:'Input secured',context:'Context assembled',provider:event.status==='connected'?'Model connected':'Contacting model',first_token:'Response streaming',validating:'Validating output',state_ready:event.state_updates_applied?'State update validated':'State update quarantined',committing:'Writing persistent state',committed:'State committed'};$('mindStatus').textContent=labels[event.phase]||'Cognition in progress';}
    });
      if(r.deferred){bubble.remove();runRemaining=0;$('mindStatus').textContent='Exploration paused while you compose a message.';window.godelosLiveOperation?.finish({deferred:true});return false;}
      if(r.queued){copy.textContent='Queued behind the thought already in progress.';bubble.classList.remove('streaming-message');window.godelosLiveOperation?.finish(r);return r;}
      copy.textContent=r.reply;bubble.querySelector('h4').textContent=`Cycle ${r.mind_tick} · ${r.cognitive_mode}`;bubble.classList.remove('streaming-message');window.godelosLiveOperation?.finish(r);await refresh();return r;}
    catch(e){
      $('mindStatus').textContent='Connection interrupted · recovering saved reply';
      for(let attempt=0;attempt<6;attempt++){
        try{const saved=await api('/api/mind/evidence/'+id);
          if(saved.result?.status==='completed'){const r=saved.result.response;copy.textContent=r.reply;bubble.classList.remove('streaming-message');window.godelosLiveOperation?.finish(r);await refresh();return r;}
          if(saved.result)break;
        }catch{/* A temporary network loss may also affect the lookup. */}
        await new Promise(resolve=>setTimeout(resolve,1000*(attempt+1)));
      }
      copy.textContent=shown?shown+'\n\n[Reply interrupted. This partial text is not a completed answer.]':'The attempt stopped before a complete reply. The input remains available to retry.';bubble.classList.remove('streaming-message');bubble.classList.add('stream-failed');window.godelosLiveOperation?.fail(e);fail(e);runRemaining=0;return false;}
    finally{busy=false;$('mindStep').disabled=false;$('mindRun').disabled=false;$('mindStatus').textContent=!$('mindError').hidden?'Cycle failed · your draft is retained':runRemaining?`${runRemaining} cycles remaining`:'Ready';}
  }
  $('mindStep').onclick=()=>cycle();
  $('mindRun').onclick=async()=>{runRemaining=Number($('mindRounds').value);let completed=0,failed=false;while(runRemaining>0){runRemaining--;if(!await cycle()){failed=true;break;}completed++;} $('mindStatus').textContent=failed?`Stopped after ${completed} cycles · inspect the error`:`Exploration stopped · ${completed} cycles completed`;};
  $('mindPause').onclick=async()=>{runRemaining=0;try{await api('/api/mind/control',{paused:!current?.mind_control?.paused});await refresh();}catch(e){fail(e)}};
  $('mindRecover').onclick=async()=>{try{await api('/api/mind/recover',{request_id:current?.cognition_lease?.request_id});await refresh();}catch(e){fail(e)}};
  $('mindMessage').value=sessionStorage.getItem('godelos-draft')||'';
  $('mindMessage').addEventListener('input',()=>{sessionStorage.setItem('godelos-draft',$('mindMessage').value);runRemaining=0;if(Date.now()-lastAttentionHold>10000){lastAttentionHold=Date.now();api('/api/mind/attention',{}).catch(fail);}});
  $('mindChat').onsubmit=async e=>{
    e.preventDefault();const value=$('mindMessage').value.trim();if(!value||sending)return;
    runRemaining=0;sending=true;$('mindError').hidden=true;const id=requestId();
    $('mindMessage').value='';sessionStorage.removeItem('godelos-draft');message('You · sending',value);if($('mindSend'))$('mindSend').disabled=true;
    try{const result=await cycle({request_id:id,message:value,person_id:'oli',person_name:'Oli'},true);if(!result&&(!$('mindMessage').value)){$('mindMessage').value=value;sessionStorage.setItem('godelos-draft',value);}historyTick=-1;$('mindStatus').textContent=result?.queued?'Message queued · it will be answered next':result?.warnings?.length?'Reply delivered · memory update held for inspection':result?'Ready':'Message retained · retry when ready';}
    catch(error){if(!$('mindMessage').value){$('mindMessage').value=value;sessionStorage.setItem('godelos-draft',value);}fail(error);}
    finally{sending=false;if($('mindSend'))$('mindSend').disabled=false;}
  };
  $('mindEvidence').onclick=async()=>{try{const event=(current?.events||[]).slice().reverse().find(e=>e.event_type==='integrated_cycle');if(!event)throw Error('Run a cycle first.');const evidence=await api('/api/mind/evidence/'+event.payload.request_id);const url=URL.createObjectURL(new Blob([JSON.stringify(evidence,null,2)],{type:'application/json'}));const link=el('a');link.href=url;link.download='mind-cycle-'+event.payload.request_id+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){fail(e)}};
  nav.onclick=()=>{open();refresh().catch(fail);};
  window.addEventListener('sovereignty:connected',()=>{open();refresh().catch(fail)});
  document.addEventListener('mind:refresh',()=>refresh().catch(fail));
  open();if(sessionStorage.getItem('godelos-access-token'))refresh().catch(fail);
  setInterval(()=>{if(!busy&&!sending&&panel.classList.contains('active')&&sessionStorage.getItem('godelos-access-token'))refresh().then(drainInbox).catch(fail);},3000);
})();
