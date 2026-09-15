"""Three-page release report; figures derive from retained V13 raw-run analysis."""
import json, sys
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

data=json.loads(Path('research/living13-analysis.json').read_text())
output=Path(sys.argv[1] if len(sys.argv)>1 else 'public/godelos-v13-living-mind-report.pdf')
output.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Sans','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
c=canvas.Canvas(str(output),pagesize=(595,842));c.setTitle('GodelOS V13 - Living Mind alpha')
ink='#183334';teal='#137C6B';mint='#D5EFE3';orange='#ECA15B';muted='#536968'
def box(x,y,w,h,col):
 c.setFillColor(HexColor(col));c.roundRect(x,y,w,h,12,fill=1,stroke=0)
def text(x,y,s,size=11,col=ink,bold=False):
 c.setFillColor(HexColor(col));c.setFont('Bold' if bold else 'Sans',size);c.drawString(x,y,str(s))
def para(x,y,s,w=495,size=10.5,col=ink):
 p=Paragraph(escape(s),ParagraphStyle('p',fontName='Sans',fontSize=size,leading=size*1.5,textColor=HexColor(col)))
 _,h=p.wrap(w,700)
 if y-h<48:raise ValueError('Report text exceeds page: '+s[:60])
 p.drawOn(c,x,y-h);return y-h-14
def page(n,kicker,title):
 c.setFillColor(HexColor('#F5F8F5'));c.rect(0,0,595,842,fill=1,stroke=0)
 text(50,790,kicker,9,teal,True);text(50,745,title,28,ink,True)
 text(50,28,'GODELOS / V13 ALPHA / 15 SEPTEMBER 2026',8,muted);text(530,28,n,9,muted)

page(1,'A MIND IN DEVELOPMENT','Room to think.')
y=para(50,713,'An opinion can now become a continuing thread: something the agent imagines around, tests in a bounded way, qualifies, and brings back to your conversation.',size=13)
labels=[('01','Take a position','Reasons, counterarguments and a condition for revision.'),('02','Let attention wander','Associations refer to real sources and remain marked as imagination.'),('03','Ask, then execute','A proposed retrieval inquiry becomes two fresh model calls.'),('04','Return with a change','The same position can acquire revised confidence and new reasons.')]
for i,(num,title,desc) in enumerate(labels):
 yy=530-i*104;box(50,yy,495,88,'#FFFFFF');box(64,yy+23,42,42,mint)
 text(73,yy+38,num,13,teal,True);text(122,yy+60,title,13,ink,True);para(122,yy+45,desc,400,10)
para(50,200,'The first slice is built on the existing agent: conversation streaming, persistent state, attention, functional affect and relationship machinery remain connected. An inspect layer exposes actual events without turning the conversation into a wall of instruments.',size=11)
para(50,112,'The orb depicts computed appraisal. The timeline depicts stored events. Neither is a measurement of subjective experience.',size=9.5,col=muted)
c.showPage()

page(2,'REAL DEEPSEEK CALLS','The loop ran. So did the faults.')
text(50,697,'32 calls',20,teal,True);text(215,697,'24 replies',20,teal,True);text(390,697,'4 probes',20,teal,True)
para(50,675,f'Model returned: {", ".join(data["models"])}. {data["total_tokens"]:,} reported tokens. Four short histories across two implementation stages. Each probe uses two calls.',size=10)
text(50,602,'Cognition episodes: accepted updates vs quarantined updates',11,ink,True)
for ri,run in enumerate(data['runs']):
 for hi,h in enumerate(run['histories']):
  y=555-(ri*2+hi)*45;text(50,y+4,('Initial' if ri==0 else 'Final')+f' / history {hi+1}',10)
  n=h['episodes'];q=h['quarantined'];good=n-q
  c.setFillColor(HexColor(teal));c.rect(185,y,300*good/n,18,fill=1,stroke=0)
  if q:c.setFillColor(HexColor(orange));c.rect(185+300*good/n,y,300*q/n,18,fill=1,stroke=0)
  text(495,y+3,f'{good} / {q}',10)
para(50,388,'Teal: cognitive updates accepted. Amber: reply delivered, proposed structured updates withheld. All 24 episodes returned a usable reply; three update sets were quarantined. No history was discarded.',size=10)
y=para(50,315,'All four completed inquiries retrieved the frozen stance when a record was supplied and reported uncertainty when it was absent. That behaviour is explicitly instructed by this retrieval test; it is not independent evidence of self-awareness.',size=11)
y=para(50,y,'In the final run, one instance refined the same position: confidence 0.62 to 0.56, plus a counterexample-based reason against. No categorical stance reversal was observed. One subsequent inquiry per history remained pending at the run limit.',size=11)
para(50,y,'These are exploratory engineering smoke runs. The counterevidence and invitation to propose a test came from the operator. No significance claim, spontaneous-development claim or causal identity advantage follows.',size=10,col=muted)
c.showPage()

page(3,'USE IT / INSPECT IT / PUSH IT','What you can do now.')
y=para(50,705,'Open Conversation. Offer a real disagreement. Use Follow a thought, then open What is developing? to inspect the position, associations and inquiry evidence. Challenge the same position later. Pick up an invitation without losing an existing draft.',size=12)
box(50,490,495,100,mint);text(66,564,'The useful result',14,teal,True)
para(66,547,'There is now an executable route from an agent-authored question to a recorded result that enters later cognition. The first supported experiment is narrow, but the route is real.',463,11)
y=para(50,465,'The live run exposed a citation-type error: a real opinion ID appeared in a memory field. The fix retypes known references transparently. It does not legitimise invented references. Truncated and malformed JSON still occurred in the final run; replies survived and invalid updates were retained as evidence.',size=10.5)
y=para(50,y,'The initial run also narrated an intention as completed without verified engine completion. The final build distinguishes the requested question from the fixed compiled retrieval protocol. Broader claims in prose remain an open problem; the evidence view is authoritative for actual state changes.',size=10.5)
y=para(50,y,'Next build: a creative experiment the agent can actually choose and execute. Compare identical creative tasks with identity-bearing, content-matched and absent histories. Return the results without instructing a stance revision, and see whether the agent changes its position for a traceable reason.',size=10.5)
y=para(50,y,'Deployment: extract the ZIP; use Netlify Git or CLI deployment with the existing site and Blob store. Keep the provider key and access token in environment variables. Static Drop alone does not deploy functions. Confirm runtime 13.0.0-alpha.1 at /api/health.',size=10)
para(50,y,'Reproduction: npm ci; npm test; npm run build. Exact live commands, parameters and raw-run locations are in LIVING_MIND_V13.md. Browser visual QA was blocked by ERR_BLOCKED_BY_CLIENT. This report contains no fabricated UI screenshots. No production deployment or Git push was performed.',size=9.5,col=muted)
c.save()
print(output)
