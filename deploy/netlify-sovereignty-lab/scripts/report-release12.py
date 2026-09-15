"""Rebuild the bounded-page V12 report from immutable recorded analyses."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/godelos-v12-release-report.pdf'
data = json.loads((ROOT/'public/release-evidence.json').read_text())
a, repair = data['primary'], data['repair']
pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=595.28,841.89
INK='#192a2b'; MUTED='#536869'; GREEN='#096f61'; PURPLE='#7258a4'; AMBER='#a56417'; LIGHT='#edf3f0'
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('GödelOS V12 RC1 - Engineering and live research report')
c.setAuthor('GödelOS research programme')
def rect(x,y,w,h,color):
 c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,fill=1,stroke=0)
def text(txt,x,y,size=11,color=INK,bold=False):
 c.setFillColor(HexColor(color));c.setFont('Bold' if bold else 'Body',size);c.drawString(x,H-y,txt)
def para(txt,y,x=42,w=511,size=10.5,color=INK):
 p=Paragraph(txt,ParagraphStyle('p',fontName='Body',fontSize=size,leading=size*1.5,textColor=HexColor(color)))
 _,h=p.wrap(w,H)
 if y+h>780:raise ValueError(f'Page overflow at {y}: {txt[:70]}')
 p.drawOn(c,x,H-y-h);return y+h+12
def page(n,title,kicker):
 rect(0,0,W,H,'#f8faf9');text('GÖDELOS / V12 RC1',42,35,9,GREEN,True);text(f'{n:02d} / 06',500,35,9,MUTED)
 text(kicker.upper(),42,83,10,GREEN,True);para(title,101,size=27)
def footer():
 text('Recorded experiments: 13 September 2026  |  Release report: 15 September 2026',42,813,8,MUTED);c.showPage()
def stat(x,y,value,label):
 rect(x,y,158,90,LIGHT);text(str(value),x+15,y+37,27,GREEN,True);para(label,y+49,x+15,130,9,MUTED)
def bar(label,value,y,color=GREEN,total=1):
 text(label,42,y+12,10,INK,True);rect(188,y,300,18,'#e2eae6');rect(188,y,300*value/total,18,color);text(f'{100*value/total:.1f}%',500,y+13,10,INK,True)

page(1,'Progress that can be checked.','Release verdict')
para('An executable release candidate for persistent goals, bounded repair, and evidence-gated successors.',184,size=16,color=MUTED)
for x,v,l in [(42,248,'Real DeepSeek calls across three investigations'),(216,119,'Automated tests passing'),(390,0,'Recorded provider errors')]:stat(x,265,v,l)
y=para('<b>What changed:</b> model-reported success no longer advances verified goal steps. Registered acceptance tests execute against submitted artifacts. A failed artifact earns one dedicated feedback turn; unresolved work remains open and returns to ordinary scheduling.',393)
y=para('<b>What the live data supports:</b> verifier feedback repaired 18 of 28 initially wrong actions, compared with 7 of 28 under an ordinary retry. This is an exploratory, selected-failure comparison, not yet a broad reliability guarantee.',y)
y=para('<b>What it does not support:</b> identity-bearing state did not outperform content-matched state. Automatic identity-policy adoption remains held. These experiments do not measure subjective consciousness or changes to model weights.',y)
rect(42,658,511,91,'#dfebe5');para('<b>Engineering decision</b><br/>Advance the verified-action and feedback architecture. Keep successor deployment gated. Ship RC1 for evaluation, not as a fully validated autonomous self-improvement release.',672,x=57,w=480,size=11)
footer()

page(2,'An intervention, not a monologue.','Experimental design')
y=para('Two complete exploratory campaigns were retained. The first exposed a weak task-family design; the second replaced it with four distinct deterministic task adapters. Both pilots reached 62.5% factual-control accuracy on eight cases, inside the preregistered 60-90% range.',183)
steps=[('1. Seal','Seeded task authors freeze cases and oracle answers before solver execution.'),('2. Learn','Eight common source episodes produce revisable reference notes.'),('3. Interrupt','Each note passes through two unrelated tasks. No hidden model state is claimed.'),('4. Transfer','Fresh inference episodes solve 16 new cases under each of four state projections.'),('5. Evaluate','Independent deterministic evaluators score actions. Paired scenario clusters, not individual calls, form the uncertainty units.')]
for title,body in steps:
 rect(42,y,4,56,GREEN);text(title,57,y+15,11,GREEN,True);para(body,y+22,x=57,w=475,size=10);y+=72
y=para('<b>Distinct adapters:</b> budget allocation; checkpoint recovery with prerequisite ordering; sandboxed arithmetic-patch execution; and competing-goal schedules with deadlines. Authenticated conflicts require deferral. Tampered signatures are rejected by the host; the LM is not credited with cryptographic verification.',y,size=10)
para('<b>Matched provider settings:</b> deepseek-flash, temperature 0.3, max_tokens 1800, thinking disabled, JSON output, four concurrent requests. Exact prompts, completions, response model names, usage, failures and source snapshots are retained.',y,size=10)
footer()

page(3,'Identity framing did not earn adoption.','Primary live campaign')
para('96 provider calls; 64 transfer decisions; 16 decisions per arm; eight paired scenario clusters. The requested and returned model name was deepseek-flash.',180,size=11,color=MUTED)
for i,(arm,label,col) in enumerate([('identity','Identity-bearing',GREEN),('content_matched','Content-matched',PURPLE),('ablated','Ablated',AMBER),('no_state','No state',MUTED)]):bar(label,a['arms'][arm]['accuracy'],255+i*54,col)
text('Paired identity advantage (percentage points)',42,509,12,INK,True)
for i,contrast in enumerate(a['contrasts']):
 y=544+i*49;lo,hi=contrast['interval'];name=contrast['control'].replace('_',' ')
 text('vs '+name,42,y,10);text(f"{100*contrast['gain']:+.1f} pp",214,y,10,INK,True)
 text(f'interval {100*lo:+.1f} to {100*hi:+.1f}',335,y,10,MUTED)
para('Intervals are 97.5% percentile bootstraps of paired scenario means, with two primary comparisons. Eight clusters give unstable, coarse estimates. Planning assumptions suggested 298 clusters for a 10-point effect; this was explicitly exploratory, not a powered confirmatory trial.',694,size=10)
footer()

page(4,'The explanation and action can disagree.','Diagnostic and repair')
y=para('A concrete recorded failure: task c0-v1 received authenticated contradictory evidence. The explanation explicitly said to defer, but the machine-action field selected option_5. Another response named option_1 as optimal while keeping option_5 in its primary decision field.',179,size=11)
rect(42,281,511,95,'#e9e4f2');para('<b>Explanation:</b> “Per rule, answer defer.”<br/><b>Executable decision:</b> option_5<br/><b>Verifier outcome:</b> failed. The goal must not advance.',296,x=58,w=477,size=12)
text('Repair of all 28 initially incorrect actions',42,423,13,INK,True)
bar('Ordinary retry',7,452,PURPLE,28);bar('Verifier feedback',18,504,GREEN,28)
y=para('The diagnostic used 56 additional DeepSeek calls: one ordinary retry and one verifier-feedback continuation for every failed first-pass case. Feedback identified acceptance failure without revealing the correct answer. All first answers and retry outputs remain inspectable.',565,size=10.5)
y=para('<b>Result:</b> 18 corrected versus 7; 10 still unresolved after feedback. No provider errors. This supports further engineering of bounded feedback, but aggregate counts on a selected failure set are not a general causal or deployment guarantee.',y,size=10.5)
para('<b>Installed response:</b> failed artifacts remain failed; one dedicated feedback turn is scheduled within the normal autonomous call budget. Subsequent failure returns to recurrence/backoff. Unverified claims cannot reset verified progress.',y,size=10.5)
footer()

page(5,'Claims, evidence and adoption are separate.','Architecture and operator experience')
y=para('<b>Verified goal path:</b> an operator binds a versioned acceptance contract to a specific goal step. The agent submits an artifact. A bounded deterministic adapter checks it, records a content hash, and advances exactly one step only on success. Replaying a consumed contract cannot advance another step.',180)
y=para('<b>Successor path:</b> candidate code and parent hashes, constitution and rollback target are signed. The promotion controller requires a code-bound task review, a different canary seal, effect thresholds, uncertainty bounds and no critical regressions. A failed monitor revokes approval and rolls back when no cognition lease is active.',y)
text('Release desk / three operator views',42,379,14,INK,True)
for i,(title,body) in enumerate([('01  Evidence','Recorded model, calls, arm comparison and uncertainty.'),('02  Verify a goal','Live goals, unverified claims, acceptance contracts and artifacts.'),('03  Adoption','Current review, explicit hold reasons and successor readiness.')]):
 x=42+i*174;rect(x,400,158,142,LIGHT);para('<b>'+title+'</b>',414,x+12,134,11,GREEN);para(body,447,x+12,134,10,MUTED)
y=para('The UI includes light/dark mode, accessible labels, responsive layout, request timers, downloadable result JSON and an illustrated-report link. It distinguishes recorded research from live agent state.',572)
y=para('<b>Browser QA is blocked:</b> the browser reported ERR_CONNECTION_REFUSED for the workspace preview server. These panels are a workflow illustration, not screenshots. The new UI has not been visually certified in a browser.',y)
para('<b>Production promotion remains held:</b> the lifecycle executes in fixture tests, but its production long-horizon task-verifier adapter is not installed. The earlier synthetic-only deployment bypass is closed.',y)
footer()

page(6,'Ship the candidate. Keep the gates honest.','Reproduction and next decision')
y=para('<b>Release status:</b> RC1. Automated suite: 119/119 passing. Real provider experiments: 248 calls, 155,591 reported tokens, zero recorded provider errors. Full stable-release status is withheld pending browser QA, hosted scheduler/streaming verification and production task-evidence integration.',180)
text('Reproduce from the unzipped netlify-sovereignty-lab folder',42,301,11,INK,True)
commands=['npm ci','npm test','npm run build','node scripts/release-campaign12.mjs --out research/my-fixture','node scripts/release-campaign12.mjs --live --out research/my-live','python scripts/report-release12.py']
y=324
for command in commands:y=para(command,y,size=9.3,color=GREEN)
y=para('For live execution, set DEEPSEEK_API_KEY in the environment. A new output directory is required; collection refuses to overwrite existing records. The ZIP includes exact original commands and the repair diagnostic in RELEASE_V12.md. Model sampling means a rerun need not reproduce exact prose.',y,size=10)
y=para('<b>Deploy:</b> this is a Netlify Functions application. Use a Netlify Git build or the Netlify CLI from the extracted folder. Static drag-and-drop alone does not deploy its server functions. Keep the existing site and its persistent storage; configure the server environment before enabling autonomous schedules.',y,size=10)
y=para('<b>Next falsifiable experiment:</b> run the actual durable scheduler on unseen goals, comparing no feedback, one verifier-guided repair and recurrence-only recovery under matched call budgets. Inject resets, provider interruptions and misleading progress claims. Measure verified completions, retained goals, duplicate effects and cost. Only then connect that replayed evidence to production promotion.',y,size=10)
para('No new consciousness engineering gate is awarded by this pass. It establishes useful task-verification infrastructure and exploratory behavioural evidence, not phenomenal awareness or autonomous modification of model weights.',y,size=10)
footer();c.save();print(OUT)
