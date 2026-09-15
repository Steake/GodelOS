/* V8.2 operator navigation. Reuses the existing authenticated actions and state. */
window.renderModelStatus = function(snapshot) {
  const node=document.getElementById('modelLabel');if(!node)return;
  const status=snapshot.model_status;
  node.replaceChildren();
  for(const text of [status?.last_response?.model ? 'Last response: '+status.last_response.model : 'No live response model recorded', 'Next request: '+(status?.configured||'Unavailable')]) {
    const line=document.createElement('div');line.textContent=text;node.append(line);
  }
  const quick=document.getElementById('modelQuick');if(quick)quick.textContent=status?.last_response?.model||'Model details';
  node.title='Provider-reported model of the last recorded completion; separately, the configured model requested for the next call.';
};
window.addEventListener('DOMContentLoaded',()=>{
 const $=id=>document.getElementById(id), make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
 const nav=$('nav'), mind=$('mind'), legacy=[...nav.querySelectorAll('button')];
 const originalMind=legacy.find(n=>n.textContent==='Your agent');
 const originalResearch=legacy.find(n=>n.textContent==='Experiment workbench');
 const side=document.querySelector('.side');
 const brand=document.querySelector('.brand');brand.textContent='G';brand.title='GödelOS';
 const rail=make('div','md-rail');
 const icons={Conversation:'<path d="M5 5h14v10H9l-4 4z"/>',Activity:'<path d="M3 12h4l3-7 4 14 3-7h4"/>',Experiments:'<path d="M9 3h6M10 3v7l-6 9q0 2 2 2h12q2 0 2-2l-6-9V3M7 15h10"/>',Archive:'<rect x="4" y="4" width="16" height="5" rx="1"/><path d="M6 9v11h12V9M10 13h4"/>',Settings:'<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3"/><circle cx="15" cy="17" r="3"/>'};
 const destinations={};
 for(const label of Object.keys(icons)){
  const b=make('button','md-destination');b.type='button';b.setAttribute('aria-label',label);
  b.innerHTML='<span class="md-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icons[label]+'</svg></span><span>'+label+'</span>';
  rail.append(b);destinations[label]=b;
 }
 nav.prepend(rail);
 const cabinet=make('section','view md-cabinet');cabinet.id='operatorArchive';
 cabinet.innerHTML='<h2>Research archive</h2><p>Previous experiments, specialist tools and the evidence behind the agent’s development.</p><div class="md-archive-grid"></div>';
 const settings=make('section','view md-cabinet');settings.id='operatorSettings';
 settings.innerHTML='<h2>Agent settings</h2><p>Review the current model, inspect continuity and edit the agent’s value profile.</p><div class="md-settings-model"><h3>Model connection</h3></div><div class="md-settings-tools"></div>';
 document.querySelector('main').append(cabinet,settings);
 settings.querySelector('.md-settings-model').append($('modelLabel'));
 const integrity=document.querySelector('.chain');if(integrity)settings.querySelector('.md-settings-model').append(integrity);
 const report=document.querySelector('.report-link');if(report){const tile=make('div','md-tool');report.textContent='V8 research report';tile.append(report,make('p',null,'Read the earlier experiment, results and limitations.'));cabinet.querySelector('.md-archive-grid').append(tile);}
 const originalHost=make('div','md-legacy-nav');nav.append(originalHost);
 const toolHelp={'Overview':'Summary of earlier calibration and adoption decisions.','Evolution Chamber':'Inspect branch experiments and promotion gates.','Calibration':'Compare value profiles against recorded diagnostics.','Lineage':'Trace predecessor and successor decisions.','Living agent':'Earlier exploration interface and its recorded state.','Independence chamber':'Inspect the sovereignty research programme.','Conversation':'Earlier conversation interface.','Value Lab':'Edit the values that guide the agent’s decisions.','Benchmark Forge':'Calibrate task difficulty and compare transfer branches.'};
 const addTool=b=>{
   if(b===originalMind||b===originalResearch){originalHost.append(b);return;}
   const tile=make('div','md-tool');const label=b.textContent;
   tile.append(b,make('p',null,toolHelp[label]||'Open this specialist research instrument.'));
   (label==='Value Lab'?settings.querySelector('.md-settings-tools'):cabinet.querySelector('.md-archive-grid')).append(tile);
 };
 legacy.forEach(addTool);
 // Some retained tools register after their initial data request finishes.
 new MutationObserver(records=>{for(const rec of records)for(const n of rec.addedNodes)if(n.nodeType===1&&n.tagName==='BUTTON')addTool(n);}).observe(nav,{childList:true});
 const savedTheme=localStorage.getItem('godelos-theme'); const initialTheme=savedTheme||(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'); document.body.dataset.theme=initialTheme; const top=document.querySelector('.top');top.classList.add('md-appbar');const releaseLink=make('a','md-theme-toggle','Release desk ↗');releaseLink.href='/release12.html';top.append(releaseLink); const themeToggle=make('button','md-theme-toggle',initialTheme==='dark'?'Light mode':'Dark mode');themeToggle.type='button';themeToggle.setAttribute('aria-pressed',initialTheme==='dark');themeToggle.onclick=()=>{const dark=document.body.dataset.theme!=='dark';document.body.dataset.theme=dark?'dark':'light';localStorage.setItem('godelos-theme',document.body.dataset.theme);themeToggle.textContent=dark?'Light mode':'Dark mode';themeToggle.setAttribute('aria-pressed',String(dark));};
 const purpose=make('span','md-build','V9 beta');const modelQuick=make('button','md-model-quick','Model details');modelQuick.id='modelQuick';modelQuick.type='button';modelQuick.onclick=()=>select('Settings');top.append(modelQuick,themeToggle,purpose);
 const chat=mind.querySelector('.mind-conversation');
 chat.querySelector('h3').textContent='Conversation';
 const intro=make('div','md-chat-intro');intro.innerHTML='<span class="md-overline">A MIND IN DEVELOPMENT</span><h2>Something worth thinking about.</h2><p>Talk to Sovereign-01. Challenge a belief, follow a curiosity, or pick up an earlier thread.</p>';
 chat.prepend(intro);
 const suggestions=make('div','md-suggestions');
 for(const [label,text] of [['What’s on your mind?','What are you interested in exploring, and why?'],['Challenge a belief','Choose one of your held positions. What evidence would make you revise it?'],['What has changed?','What has changed in your recorded state since our previous conversation?']]){
 const b=make('button',null,label);b.type='button';b.onclick=()=>{$('mindMessage').value=text;$('mindMessage').focus();};suggestions.append(b);}
 $('mindChat').before(suggestions);
 $('mindMessage').placeholder='Message Sovereign-01…';$('mindMessage').rows=2;
 const send=$('mindChat').querySelector('button');send.textContent='Send';send.id='mindSend';send.type='button';send.onclick=()=>$('mindChat').requestSubmit();
 $('mindChat').append(make('p','md-composer-note','Messages join the agent’s continuing memory. Shift + Enter for a new line.'));
 $('mindMessage').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('mindChat').requestSubmit();}});
 const activity=make('div','md-activity');
 activity.innerHTML='<div class="md-section-heading"><span class="md-overline">OBSERVE & EXPLORE</span><h2>Follow its attention.</h2><p>Run a thought cycle to see what the agent chooses next, then inspect what changed.</p></div>';
 activity.append(mind.querySelector('.mind-top'),mind.querySelector('.mind-toolbar'));
 const stateGrid=make('div','md-state-grid');
 for(const card of [...mind.querySelector('.mind-grid').children])if(card!==chat)stateGrid.append(card);
 activity.append(stateGrid,mind.querySelector('.mind-guide'));
 mind.append(activity);
 const status=make('div','md-chat-status');status.setAttribute('role','status');chat.querySelector('.md-chat-intro').after(status);
 const statusObserver=new MutationObserver(()=>{status.textContent=$('mindStatus').textContent;});statusObserver.observe($('mindStatus'),{childList:true,characterData:true,subtree:true});status.textContent=$('mindStatus').textContent;
 function select(label){
  if(label==='Conversation'||label==='Activity'){
   originalMind.click();mind.dataset.pane=label.toLowerCase();
   $('viewTitle').textContent=label==='Conversation'?'Sovereign-01':'Activity';
   $('viewSub').textContent=label==='Conversation'?'Persistent agent':'Attention, memory and self-directed thought';
  }else if(label==='Experiments'){
   originalResearch.click();$('viewTitle').textContent='Experiments';$('viewSub').textContent='Ask a question. Compare branches. Examine the evidence.';
  }else{
   document.querySelectorAll('.view').forEach(n=>n.classList.remove('active'));
   (label==='Archive'?cabinet:settings).classList.add('active');$('viewTitle').textContent=label;$('viewSub').textContent=label==='Archive'?'Evidence and specialist instruments':'Configuration and values';
  }
  Object.entries(destinations).forEach(([k,b])=>{b.classList.toggle('selected',k===label);b.setAttribute('aria-current',k===label?'page':'false');});
 }
 Object.entries(destinations).forEach(([label,b])=>b.onclick=()=>select(label));
 // Transform the existing executable form instead of introducing a second research engine.
 const evolution=make('details','mind-guide md-evolution');
 evolution.innerHTML='<summary>V12 RC1 · Development chamber</summary><p>Can the agent escape repetitive thinking without losing important recurring goals? It designs executable attention policies, tests them, and carries the review into its next attempt.</p><div class="actions"><button id="evoRounds" class="action">Start 3 background rounds</button><button id="evoStop" class="action secondary">Pause development</button><button id="devRefresh" class="action secondary">Refresh progress</button></div><p>Rounds continue with this page closed, on the 15-minute server schedule. Changes stay in shadow mode: the current benchmark is not sufficient evidence for automatic adoption. The global thinking pause also pauses development.</p><p id="devStatus" role="status" aria-live="polite">Loading development state…</p><progress id="devProgress" max="3" value="0" aria-label="Development rounds completed"></progress><ol id="devHistory"></ol><details><summary>Manual controller tools</summary><div class="actions"><button id="evoDesign" class="action secondary">Design one candidate</button><button id="evoDeploy" class="action secondary" disabled>Deploy to attention only</button><button id="evoRollback" class="action secondary">Roll back controller</button></div><p>Adoption requires a signed task-level review and separate canary. The old synthetic gate cannot bypass this requirement.</p><p id="evoStatus" role="status">No candidate loaded.</p><pre id="evoResult" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>';
 $('workbench').prepend(evolution);
 const devResume=make('button','action secondary','Resume development');devResume.type='button';devResume.disabled=true;$('evoStop').after(devResume);
 let evoCandidate=null,evoBusy=false;
 const evoCall=async(action,data)=>{const response=await apiFetch('/api/evolution/'+action,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const result=await response.json();if(!response.ok)throw Error(result.error||'Evolution request failed');return result;};
 const evoShow=pkg=>{if(!pkg)return;evoCandidate=pkg;const c=pkg.content,e=c.evidence;$('evoResult').textContent=c.candidate.thesis+'\n\nController selection gain: '+(100*e.gain).toFixed(1)+' percentage points\n95% bootstrap interval: '+e.interval.map(x=>(100*x).toFixed(1)).join(' to ')+'\nAuthored tests passed: '+e.authored_tests.filter(x=>x.pass).length+'/'+e.authored_tests.length+'\nGate: '+(e.eligible?'ELIGIBLE':'HOLD')+'\nCode hash: '+c.candidate.code_hash+'\n\n'+e.limitation;$('evoDeploy').disabled=true;$('evoDeploy').title='Review adoption readiness in the Release desk';};
 async function evolve(){if(evoBusy)return;evoBusy=true;$('evoDesign').disabled=true;try{$('evoStatus').textContent='Designing and testing one candidate…';evoShow(await evoCall('propose',{}));$('evoStatus').textContent='Candidate tested; inspect the evidence below.';}catch(e){$('evoStatus').textContent=e.message;}finally{evoBusy=false;$('evoDesign').disabled=false;}}
 $('evoDesign').onclick=()=>evolve(1);
 const devCall=async(action,data)=>{const r=await apiFetch('/api/development/'+action,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const x=await r.json();if(!r.ok)throw Error(x.error||'Development request failed');return x;};
 const devShow=s=>{
  $('devStatus').textContent=!s?'No development run yet.':`${s.phase==='designing'?'Designing and testing':s.phase==='completed'?'Completed':s.active?'Waiting for the next server tick':'Paused'} · ${s.round} / ${s.rounds} rounds · shadow mode`;
  $('devProgress').max=s?.rounds||3;$('devProgress').value=s?.round||0;
  $('evoRounds').disabled=!!s&&(s.active||s.phase==='designing');$('evoStop').disabled=!s?.active;
  devResume.disabled=!s||s.active||s.round>=s.rounds;
  $('devHistory').replaceChildren();
  for(const h of s?.history||[]){const li=make('li');li.style.overflowWrap='anywhere';li.textContent=`Round ${h.round}: ${h.thesis||h.error||h.outcome}`;
   if(h.review){li.append(make('p',null,`Synthetic gain: ${(100*h.gain).toFixed(1)} points. Decision: shadow only.`));const d=make('details');d.append(make('summary',null,'Why was adoption withheld?'));for(const f of h.review.findings)d.append(make('p',null,f.detail));li.append(d);} $('devHistory').append(li);}
 };
 const devRefresh=()=>devCall('status').then(devShow).catch(e=>$('devStatus').textContent=e.message);
 $('devRefresh').onclick=devRefresh;
 $('evoRounds').onclick=async()=>{ $('evoRounds').disabled=true;try{const s=await devCall('start',{rounds:3});devShow(s);$('devStatus').textContent='Run saved. Starting the first background round…';const r=await apiFetch('/.netlify/functions/development-worker-background',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id:s.id,expected_round:s.round})});if(!r.ok)throw Error('Immediate start was not acknowledged; the saved run will be picked up by the server schedule.');await devRefresh();}catch(e){$('devStatus').textContent=e.message;}};
 $('evoStop').onclick=async()=>{try{devShow(await devCall('pause',{}));}catch(e){$('devStatus').textContent=e.message;}};
 devResume.onclick=async()=>{try{devShow(await devCall('resume',{}));}catch(e){$('devStatus').textContent=e.message;}};
 devRefresh();setInterval(()=>{if(!document.hidden&&evolution.open)devRefresh();},5000);
 $('evoDeploy').onclick=async()=>{try{await evoCall('deploy',{id:evoCandidate.content.id});$('evoStatus').textContent='Candidate deployed to attention selection.';$('evoDeploy').disabled=true;}catch(e){$('evoStatus').textContent=e.message;}};
 $('evoRollback').onclick=async()=>{try{await evoCall('rollback',{});$('evoStatus').textContent='Previous controller restored.';}catch(e){$('evoStatus').textContent=e.message;}};
 evolution.addEventListener('toggle',()=>{if(evolution.open&&!evoCandidate)evoCall('latest').then(evoShow).catch(e=>$('evoStatus').textContent=e.message);});
 const wb=$('workbench');wb.querySelector('.wb-intro h2').textContent='What do you want to find out?';
 wb.querySelector('.wb-intro p').textContent='The agent designs a test, runs controlled branches, and critiques its result.';
 wb.querySelector('.wb-kicker').textContent='SELF-DIRECTED RESEARCH';
 const fields=wb.querySelector('.wb-fields'), options=make('details','md-run-options');options.append(make('summary',null,'Run settings'));fields.before(options);options.append(fields,$('wbManualOptions'));
 $('wbManual').addEventListener('click',()=>options.open=true);
 const runGuide=make('div','md-experiment-steps');runGuide.innerHTML='<div><span>01</span><b>Ask</b><p>Choose a question and a call budget.</p></div><div><span>02</span><b>Compare</b><p>Run matched tasks with different inherited state.</p></div><div><span>03</span><b>Learn</b><p>Read the result and choose the next intervention.</p></div>';
 wb.querySelector('.wb-layout').before(runGuide);
 $('wbEmpty').querySelector('h3').textContent='What changes between the branches?';
 $('wbEmpty').querySelector('p').textContent='The same task is given to four branches. What differs is the state inherited from the predecessor.';
 $('wbEmpty').querySelector('.wb-kicker').textContent='UNDERSTAND THE TEST';
 const formWrap=make('details','md-investigation-config');formWrap.open=true;
 formWrap.append(make('summary',null,'Configure an investigation'));$('wbForm').before(formWrap);formWrap.append($('wbForm'));
 new MutationObserver(()=>{if(!$('wbActive').hidden)formWrap.open=false;}).observe($('wbActive'),{attributes:true,attributeFilter:['hidden']});
 $('wbFork').addEventListener('click',()=>{formWrap.open=true;});
 select('Conversation');
});
