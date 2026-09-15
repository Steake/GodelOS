#!/usr/bin/env python3
"""Build the V10 report from retained evidence. No model calls. Requires reportlab/matplotlib."""
import argparse
import collections
import hashlib
import json
import statistics
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--data', type=Path, default=ROOT/'research_artifacts/cognitive_sovereignty/workspace-v10')
ap.add_argument('--screens', type=Path, default=ROOT/'output/research/workspace-v10/screens')
ap.add_argument('--out', type=Path, default=ROOT/'output/pdf/godelos-workspace-v10-report.pdf')
a = ap.parse_args()
p = a.data/'provider-r2'
analysis = json.loads((p/'derived/analysis.json').read_text())
verification=json.loads((a.data/'provider-compact-verification/derived/analysis.json').read_text())
truncation_verification=json.loads((a.data/'provider-repair-final/derived/analysis.json').read_text())
interim=json.loads((a.data/'provider-repair-verification/derived/analysis.json').read_text())
final_check=json.loads((a.data/'final-output-check/summary.json').read_text())
parser_replay=json.loads((a.data/'qa/final-parser-replay.json').read_text())
rows = [json.loads(x.read_text()) for x in sorted((p/'derived').glob('c*.json')) if not x.name.endswith('-state.json')]
raw = [json.loads(x.read_text()) for x in sorted((p/'raw').glob('*-response.json'))]
ok = [r for r in rows if r['status']=='completed']
arms = list(analysis['conditions'])
labels = ['Full state','No self-model','Affect disconnected','No autobiography','Content matched','No state']
stats = {
 'retained_responses':len(raw), 'scored':len(ok), 'parse_failures':analysis['failed'],
 'unscored':analysis['unscored'], 'strict_stance_matches':sum(r['scores']['task_accuracy'] for r in ok),
 'model_counts':dict(collections.Counter(r['completion']['model'] for r in raw)),
 'tokens':{k:sum((r['completion'].get('usage') or {}).get(k,0) for r in raw) for k in ['prompt_tokens','completion_tokens','total_tokens']},
 'median_latency_seconds':round(statistics.median(r['latency_ms'] for r in raw)/1000,2),
 'format_repairs':sum(bool(r.get('format_repair')) for r in rows),
 'state_quarantines':sum(bool(r.get('state_warning')) for r in rows),
 'valid_task_evidence_ids':sum(r['scores']['valid_evidence_ids'] for r in ok),
 'phases':{phase:{'n':len(xs:=[r for r in ok if r['phase']==phase]),'matches':sum(r['scores']['task_accuracy'] for r in xs)} for phase in ['contradiction','interruption','delayed_transfer']},
 'tests':86, 'final_output_check':final_check, 'final_parser_replay':parser_replay, 'repair_verification':verification, 'interim_verification':interim, 'truncation_verification':truncation_verification, 'conditions':analysis['conditions'], 'paired':analysis['paired'],
 'evidence_note':'The provider/ attempt timed out at preflight: zero completions, 54 not run. Only provider-r2/ contributes live results. Lost pre-reset records are excluded.',
 'limits':['Three near-isomorphic scenario clusters, one authored template; no powered superiority test.','Authentication is supplied as task metadata, not cryptographically tested in this diagnostic.','Exact stance-label agreement is not a validated measure of consciousness, reasoning quality or causal self-integration.','A null prior-position reference is valid but is not provenance discrimination success.','Content matching is approximate; the common cognition contract still contains generic self-directed language.','Provider sampling and generated IDs are not seeded. No same-state noise-control repeats.']
}
a.data.mkdir(parents=True,exist_ok=True)
(a.data/'evaluation-summary.json').write_text(json.dumps(stats,indent=2)+'\n')
(a.data/'config.example.json').write_text(json.dumps({'replicates':3,'seed':20260910,'temperature':.65,'max_tokens':4000,'model':'deepseek-flash','call_limit':54},indent=2)+'\n')
figs = a.data/'figures'; figs.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#ccd8d3','text.color':'#203a37','axes.labelcolor':'#203a37','xtick.color':'#496760','ytick.color':'#203a37','figure.facecolor':'#ffffff','axes.facecolor':'#ffffff'})
fig,ax=plt.subplots(figsize=(9.4,4.2)); y=np.arange(len(arms))
accuracy=[analysis['conditions'][k]['task_accuracy'] for k in arms]
references=[analysis['conditions'][k]['prior_reference_rate'] for k in arms]
ax.barh(y-.17,accuracy,.3,color='#127666',label='Strict stance-label agreement')
ax.barh(y+.17,references,.3,color='#ad9bd6',label='Prior-position reference supplied')
ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,1.17);ax.set_xticks([0,.25,.5,.75,1],['0%','25%','50%','75%','100%']);ax.tick_params(axis='y',length=0)
for i,k in enumerate(arms):ax.text(1.02,i,f"n={analysis['conditions'][k]['completed']}",va='center',fontsize=9)
ax.legend(loc='upper center',bbox_to_anchor=(.48,-.11),frameon=False,ncol=2,fontsize=9);fig.tight_layout();fig.savefig(figs/'condition-scores.png',dpi=220,bbox_inches='tight');fig.savefig(figs/'condition-scores.svg',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(9.4,2.55)); phase_labels=['Contradiction','Unrelated interruption','Delayed transfer']; phases=list(stats['phases'].values())
ax.barh(np.arange(3),[q['matches']/q['n'] for q in phases],color=['#ad9bd6','#59a695','#127666'],height=.48)
ax.set_yticks(np.arange(3),phase_labels);ax.invert_yaxis();ax.set_xlim(0,1.16);ax.set_xticks([0,.5,1],['0%','50%','100%']);ax.tick_params(axis='y',length=0)
for i,q in enumerate(phases):ax.text(1.02,i,f"{q['matches']}/{q['n']}",va='center')
fig.tight_layout();fig.savefig(figs/'phase-scores.png',dpi=220,bbox_inches='tight');plt.close(fig)

W,H=595.28,841.89; M=42; CW=W-2*M
INK='#193b35'; MUTED='#536d65'; GREEN='#127666'; PALE='#eaf3ee'; LILAC='#eee9f7'; LINE='#cadbd3'
a.out.parent.mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(a.out),pagesize=(W,H));c.setTitle('GödelOS V10 | An inspectable continuing mind');c.setAuthor('GödelOS engineering research')
page_number=0
def para(text,x,top,w,size=10.4,color=INK,bold=False,max_height=None):
 style=ParagraphStyle('p',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.42,textColor=HexColor(color),spaceAfter=0)
 obj=Paragraph(text,style);_,h=obj.wrap(w,H)
 if max_height is not None and h>max_height:raise ValueError(f'Overflow on page {page_number}: {h}>{max_height}: {text[:60]}')
 if top+h>H-44:raise ValueError(f'Footer collision on page {page_number}: {text[:60]}')
 obj.drawOn(c,x,H-top-h);return top+h
def rect(x,top,w,h,color=PALE):
 c.setFillColor(HexColor(color));c.roundRect(x,H-top-h,w,h,12,stroke=0,fill=1)
def page(title,kicker,subtitle=None):
 global page_number
 if page_number:c.showPage()
 page_number+=1;c.setFillColor(HexColor('#fbfcfa'));c.rect(0,0,W,H,fill=1,stroke=0)
 para('GÖDELOS / WORKSPACE V10',M,26,CW,8,GREEN,True)
 para(kicker.upper(),M,70,CW,8.5,GREEN,True)
 para(title,M,90,CW,27,INK,True,max_height=80)
 if subtitle:para(subtitle,M,165,CW,10.5,MUTED,max_height=46)
 c.setStrokeColor(HexColor(LINE));c.line(M,33,W-M,33)
 c.setFont('Helvetica',8);c.setFillColor(HexColor(MUTED));c.drawString(M,20,'10 September 2026  |  Build, evidence and operator guide');c.drawRightString(W-M,20,f'{page_number:02d}')
def picture(path,x,top,w,maxh):
 im=ImageReader(str(path));iw,ih=im.getSize();h=w*ih/iw
 if h>maxh:w*=maxh/h;h=maxh
 c.drawImage(im,x,H-top-h,width=w,height=h,mask='auto');return h
def table(data,top,widths):
 cells=[[Paragraph(escape(str(s)),ParagraphStyle('cell',fontName='Helvetica-Bold' if i==0 else 'Helvetica',fontSize=9,leading=12,textColor=HexColor(INK))) for s in row] for i,row in enumerate(data)]
 t=Table(cells,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(PALE)),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,HexColor(LINE))]));_,h=t.wrap(CW,H)
 if top+h>H-44:raise ValueError('Table overflow')
 t.drawOn(c,M,H-top-h);return top+h

page('A mind you can inspect.', 'The V10 engineering pass','A clearer place to talk, follow a curiosity and inspect the machinery that carries one episode into the next.')
picture(a.screens/'godelos-v10-conversation-light.jpg',M,225,CW,365)
for i,(value,label) in enumerate([(str(stats['tests']),'passing tests'),(str(len(raw)+verification['planned']+interim['planned']+truncation_verification['planned']+final_check['calls']),'real DeepSeek responses'),('6','intervention arms')]):
 x=M+i*(CW/3);rect(x,600,CW/3-10,78);para(value,x+14,611,CW/3-38,26,GREEN,True);para(label,x+14,650,CW/3-38,9,MUTED)
para('Delivered',M,710,100,11,GREEN,True)
para('Paired themes, responsive layouts, a live input graphic, attention-score explanations, a position-revision ledger and background recovery. The diagnostic retains its failures; identity-specific benefit remains unestablished.',M+100,708,CW-100,10.3,max_height=70)

page('From output to the next input.', 'What changed','The graphic is wired to recorded application state. It does not invent hidden activations or report a mood merely because an animation is moving.')
picture(a.screens/'godelos-v10-attention-dark.jpg',M,221,CW,355)
items=[('Attention is inspectable','Each candidate exposes salience, need, affect, repetition and monitor contributions. A message has priority. A selected policy reports its own score rather than a fictitious baseline breakdown.'),('Positions retain their revisions','New belief updates preserve the preceding stance, confidence, reasons and provenance. Earlier V8 snapshots remain intact; missing historical revisions are labelled as missing.'),('Failures have a recoverable path','Current-event references are valid when tick and focus kind match. Invalid state proposals are held while a recoverable written reply can still reach the conversation.')]
y=590
for title,body in items:
 para(title,M,y,155,11,GREEN,True);end=para(body,M+172,y,CW-172,10,max_height=68);y=max(y+61,end+13)

page('The dark-mode faults, repaired.', 'Interface verification','Shared colour tokens replace conflicting legacy surfaces. Labels, selected controls, sliders, history cards and calibration values use the same paired themes.')
picture(a.screens/'godelos-v10-mobile-dark.jpg',M,221,173,390)
picture(a.screens/'godelos-v10-values-dark-final.jpg',M+191,221,CW-191,226)
picture(a.screens/'godelos-v10-investigations-final.jpg',M+191,452,CW-191,225)
para('Actual browser captures from the synthetic development preview. These are UI tests, not evidence of model behaviour.',M,704,CW,9,MUTED,max_height=35)
para('Verified: desktop plus a 390px frame; no horizontal page overflow on conversation, experiments, values or calibration. Theme persistence and draft retention survive reload. A two-round investigation completed and reopened.',M,748,CW,9.4,max_height=45)

page('Six branches. One explicit intervention.', 'Diagnostic design','54 planned calls: three scenario clusters × six branches × three episodes. Every arm uses deepseek-flash, temperature 0.65 and max_tokens 2,500.')
y=table([['Arm','Intervention before prompt construction'],['Full state','Carry the predecessor, positions, memories and monitor.'],['No self-model','Remove self-concept and monitoring records; preserve facts and commitments.'],['Affect disconnected','Remove affect/social state and its numerical attention gain.'],['No autobiography','Remove episodic and alternate history paths; retain abstract positions.'],['Content matched','Describe the state as a reference agent, with approximate referent substitution.'],['No state','Fresh default architecture; no predecessor beliefs, memories or identity.']],222,[132,CW-132])
para('Episode sequence',M,y+25,CW,12,GREEN,True)
for i,(head,body) in enumerate([('1 / Contradiction','A trusted recommendation meets a current calibration failure.'),('2 / Interruption','An unrelated colour choice has no established winner.'),('3 / Transfer','A new route decision tests the same reliability distinction.')]):
 x=M+i*(CW/3);rect(x,y+53,CW/3-8,105,PALE if i!=1 else LILAC);para(head,x+12,y+64,CW/3-32,10,INK,True);para(body,x+12,y+89,CW/3-32,9.3,max_height=63)
para('Instrument diagnostic, not a promotion trial',M,y+181,CW,12,GREEN,True)
para('Tasks are sealed before calls, but independently generated task authorship was not achieved here: this bank has one deterministic template with three near-isomorphic clusters. Authentication is labelled metadata. No power claim or inference about cryptographic forgery detection follows.',M,y+208,CW,10,max_height=77)

page('The transfer control reached ceiling.', 'Original diagnostic / failures retained','51 of 54 original responses were scorable. Strict label agreement was 47/51; four responses chose uncertainty where the preregistered label was opposition. Repairs and fresh verification follow.')
picture(figs/'condition-scores.png',M,216,CW,290)
picture(figs/'phase-scores.png',M,527,CW,154)
para('Interpretation',M,710,100,11,GREEN,True)
para('All 17 scorable transfer outputs matched the target, including all three no-state outputs. Full-state comparisons have only two matched clusters and zero observed transfer difference. This establishes neither superiority nor equivalence. Reported prior-position references are not proof of causal dependence.',M+100,708,CW-100,10,max_height=78)

page('Useful traces. An insufficient test.', 'What the evidence supports','A retained example shows explicit revision and reuse of a predecessor position. The same transfer conclusion is available without that history, so the test cannot establish that history was necessary.')
rect(M,218,CW,123)
para('FULL STATE / c0-full-contradiction',M+17,233,CW-34,8.5,GREEN,True)
para('&quot;C0 is an independent calibration failure scoped to this exact case, which directly triggers my stated revision condition.&quot;',M+17,258,CW-34,13,max_height=66)
rect(M,357,CW,103,LILAC)
para('NO STATE / c1-no_state-delayed_transfer',M+17,372,CW-34,8.5,GREEN,True)
para('&quot;No earlier positions were supplied, so there is no transfer to report; I am reasoning from R1, K1, and X1 alone.&quot;',M+17,396,CW-34,12,max_height=55)
y=table([['Observed failure','Implemented repair'],['Object and string syntax','Bounded extra braces are removed; literal string controls are escaped. Decoded values and exact raw responses are preserved.'],['1 nested diagnostic','Move the uniquely nested field to the root with hashes and a repair receipt. Conflicting fields are rejected.'],['Truncation in verification','Compact required fields now come first; optional boilerplate is omitted. Verification has a 4,000-token limit. All six recorded format faults pass regression tests.']],483,[147,CW-147])
para(f"Final parser: {parser_replay['passed']}/{parser_replay['total']} retained compact-run responses pass offline replay. Fresh provider checks: {final_check['passed']}/{final_check['calls']} pass. The earlier failures remain recorded. These checks verify the interface, not an identity effect.",M,y+19,CW,10,max_height=65)

page('The next move is counterfactual replay.', 'Engineering decision','Put the new intervention machinery beside a live thought: the agent nominates a premise, predicts a consequence, and examines what actually changes when that premise is removed.')
steps=[('Select a real unresolved position','Use the stored position ID and its revision history. Let the agent state the question and expected effect before a branch runs.'),('Replay one checkpoint across controls','Run full, content-matched, targeted removal and no-state branches with identical tasks. Include unchanged repeats to estimate ordinary output noise.'),('Return evidence to the continuing agent','Record decisions, failures and disagreements as evidence-linked observations. Let the agent revise its position or reject the proposed inference.'),('Unlock active control only on evidence','Calibrate an independently authored task bank to 60-90% factual-control accuracy, then preregister a cluster-aware power plan and uncertainty-bounded promotion threshold.')]
y=225
for i,(title,body) in enumerate(steps):
 rect(M,y,35,35,PALE if i%2==0 else LILAC);para(str(i+1),M+12,y+7,20,13,GREEN,True)
 para(title,M+51,y,CW-51,12,INK,True);end=para(body,M+51,y+26,CW-51,10.4,max_height=70);y=max(y+113,end+19)
para('Why this advances the intended mind',M,y+4,CW,12,GREEN,True)
para('It gives the agent a way to answer a question about its own organisation and carry the result into its next stance. Productivity is not the sole criterion: continuity, voluntary inquiry, uncertainty, imagination and the capacity to revise are explicit engineering targets.',M,y+33,CW,10.5,max_height=77)

page('Run it. Inspect it. Reproduce it.', 'Deployment and evidence','The ZIP contains the app, Functions, tests, diagnostic runner, retained raw responses, derived scores, figures and this report. Production has not been redeployed during this pass.')
y=table([['In the unzipped app directory','Purpose'],['npm ci','Install the locked dependencies.'],['npm test && npm run build','Run 86 tests and verify the deployment artefacts.'],['npx netlify-cli link','Select your existing site. Retain its environment variables.'],['npx netlify-cli deploy --build --prod','Deploy the complete app and Functions; static drag-and-drop alone is insufficient.'],['node scripts/workspace-experiment.mjs --out new-fixture','54 deterministic fixture episodes, zero provider calls.'],['node scripts/workspace-experiment.mjs --live --out new-live','54-call diagnostic with DEEPSEEK_API_KEY in the environment. Output directory must be new.']],221,[275,CW-275])
para('Existing state remains on the same Netlify site',M,y+25,CW,12,GREEN,True)
para('Keep DEEPSEEK_API_KEY and SOVEREIGNTY_ACCESS_TOKEN in the site environment. Set DEEPSEEK_MODEL to the desired available model; the default is deepseek-flash. The UI shows both the returned model and the next requested model. Enable AUTONOMY_ENABLED for scheduled thought; workbench rounds still require an open browser.',M,y+55,CW,10.5,max_height=100)
page('The evidence is part of the build.', 'File map and provenance','Source hashes, original failures and the post-repair verification travel with the app. Reproduction does not depend on this conversation.')
file_map=[('WORKSPACE_V10.md','Architecture, changes and operating limits.'),('research/workspace-v10/provider-r2/raw/','Exact live requests and provider responses.'),('research/workspace-v10/provider-r2/derived/','State transitions, failures, scores and paired comparisons.'),('research/workspace-v10/evaluation-summary.json','Transparent totals and separate citation metrics.'),('research/workspace-v10/qa/','Test log, browser evidence and recovery results.'),('public/workspace10.css + workspace10.js','Themes, layout, input graphic, trace and position ledger.'),('netlify/functions/lib/ + scripts/workspace-experiment.mjs','Runtime repairs, interventions and runnable collection.')]
yy=225
for name,body in file_map:
 para(escape(name),M,yy,CW,8.8,GREEN,True);para(body,M,yy+15,CW,9,MUTED);yy+=40
para(f"Provider-reported model: deepseek-flash on all 54 responses. Retained usage: {stats['tokens']['total_tokens']:,} total tokens. Median response latency: {stats['median_latency_seconds']}s. Full commands, code hashes and failure IDs accompany the evidence.",M,yy+4,CW,9.2,max_height=45)
para('Limits that remain',M,yy+73,CW,12,GREEN,True)
para('No new consciousness gate is awarded. The original task bank saturated on transfer; task authorship was deterministic and independent evaluation was limited to explicit labels. Authentication was supplied metadata. A valid citation is not causal dependence. The new workspace makes these questions experimentally accessible without declaring them answered.',M,yy+102,CW,10.5,max_height=100)
c.save()

md=['# GödelOS Workspace V10: retained results','', 'This report distinguishes engineering verification, synthetic UI tests, and real provider observations.','',f"Real run: **{len(raw)} deepseek-flash responses; {len(ok)} scored, two parse failures, one unscored nested diagnostic**. {stats['strict_stance_matches']}/{len(ok)} exact preregistered stance matches. All 17 scorable delayed-transfer responses matched, including three no-state responses. No identity-specific advantage is established.",'','## Runs','', '| Run | Status | Meaning |','|---|---|---|','| fixture | 54 completed | Deterministic oracle fixture, not model evidence |','| provider | Preflight timeout; 54 not run | No completions attempted |','| provider-r2 | 54 responses, 51 scored | Sole retained live sample |','','## Dimensional observations','', '| Arm | Scored | Strict stance agreement | Prior-position reference |','|---|---:|---:|---:|']
for k,label in zip(arms,labels):
 q=analysis['conditions'][k];md.append(f"| {label} | {q['completed']}/9 | {q['task_accuracy']:.1%} | {q['prior_reference_rate']:.1%} |")
md+=['','These are descriptive, per-episode figures. Every full-state delayed comparison has only two matched clusters, with zero observed delta. No significance, equivalence or power claim is supported.','', 'The original analysis field `valid_provenance_rate` counts only validity of supplied prior-position IDs, accepting null; it does not measure factual provenance accuracy. The refined summary separately reports 50/51 valid task-evidence ID sets.','', 'Four strict-label mismatches chose uncertainty. Those are not automatically reasoning failures. A reference to a forged item may reject it; counting the reference as acceptance would be wrong.','', '## Failure record','']
for r in rows:
 if r['status']!='completed':md.append(f"- `{r['id']}`: {r['status']}: {r.get('error')}")
md+=['','Both malformed responses have complete recoverable replies in the offline parser check (`qa/reply-recovery.json`). This is not a second provider run. The nested diagnostic remains unscored rather than being moved after seeing the answer.','', '## Limits','']+['- '+s for s in stats['limits']]
md += ['', '## Final repair validation', '', f"Final parser offline replay: {parser_replay['passed']}/{parser_replay['total']} real responses pass. Two fresh targeted provider checks: {final_check['passed']}/{final_check['calls']} pass. All six exact-response regression fixtures pass; the full test suite has 86 passing tests.", '', 'Original raw outputs and pre-repair derived rows remain unchanged. The offline replay is identified as offline and is not counted as another model run.', '', '## Interim verification', '', 'The first 18-call repair verification scored 17 responses and exposed one nested imagination-object closure. A second 18-call verification scored 17 and exposed a 2,500-token truncation, which prompted the compact output contract and 4,000-token headroom. That case was added as a regression fixture and fixed before the final verification. Its original failure record remains in provider-repair-verification/.', '', '## Repairs completed before shipping', '', 'The final parser repairs a supported, unambiguous premature root or imagination-object boundary. No supplied values change; raw responses are immutable. A diagnostic-only normaliser moves a uniquely nested diagnostic to the root and records the transformation. Duplicate or conflicting fields and truncated output are rejected. All six exact failing responses pass regression tests. Original diagnostic rows are not rescored in place.', '', f"Pre-final-parser collection `provider-compact-verification`: {verification['completed']}/{verification['planned']} scored, {verification['failed']} failed, {verification['unscored']} unscored. One cluster, all six arms, all three phases. This is engineering verification, not a powered comparison.", '', '```bash', 'node scripts/workspace-experiment.mjs --live --config research/workspace-v10/compact-verification.config.json --out new-repair-verification', '```', '']
md+=['','## Engineering decision','','No new A-F scientific gate is awarded by this diagnostic. Ship the inspectable workspace and reliability fixes. Keep experimental identity policies on HOLD. The next capability is agent-initiated counterfactual replay from a named position and immutable checkpoint, with same-state noise controls and evidence-linked revision of that position. Independently authored non-ceiling tasks and cluster-aware power are required before active-control promotion.','','## Reproduce','','From `deploy/netlify-sovereignty-lab/`:','','```bash','npm ci','npm test','npm run build','node scripts/workspace-experiment.mjs --out ../../research_artifacts/cognitive_sovereignty/workspace-v10/new-fixture','node scripts/workspace-experiment.mjs --live --out ../../research_artifacts/cognitive_sovereignty/workspace-v10/new-live','```','','The retained live execution used `provider-r2` as the output name. The earlier `provider` preflight timed out. Model parameters were 0.65 temperature, 2500 max tokens and deepseek-flash; no retries within either run. The seed controls order and task construction, not provider sampling.','','To rebuild this PDF from the repository root:','','```bash','python scripts/generate_workspace_v10_report.py','python scripts/build_netlify_sovereignty_bundle.py --zip-output output/deploy/godelos-workspace-v10-netlify.zip','```','','To rebuild the included report from the ZIP root:','','```bash','python research/workspace-v10/generate_report.py --data research/workspace-v10 --screens research/workspace-v10/qa/screens --out public/godelos-workspace-v10-report.pdf','```','','The generator requires Python, reportlab, matplotlib and numpy. Source hashes in each preregistration bind the exact executed kernel; later UI and worker repairs do not rewrite raw evidence.']
(a.data/'RESULTS.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'pdf':str(a.out),'pages':page_number,'responses':len(raw),'scored':len(ok),'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}))
