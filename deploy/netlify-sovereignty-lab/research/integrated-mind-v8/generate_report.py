#!/usr/bin/env python3
"""Render fixed-page V8 evidence report; all charts use collected data."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
INK='#15253c'; MUTED='#53637a'; PAPER='#f7f7f2'; PALE='#e8edf1'
MINT='#36bea0'; SKY='#418dda'; VIOLET='#8a68c8'; CORAL='#db6d63'; GOLD='#d6a438'
KIND_COLORS={'imagination':VIOLET,'perception':SKY,'tension':CORAL,'reflection':GOLD,'inquiry':MINT,'intention':'#304f9e','social':'#cc79a7'}
W,H=landscape(A4)
FONT_DIR=Path(__file__).resolve().parent/'fonts'
if not FONT_DIR.exists():FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('MindSans',str(FONT_DIR/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('MindSansBold',str(FONT_DIR/'DejaVuSans-Bold.ttf')))

def normal(s):
    return str(s).replace('—',' - ').replace('–','-').replace('’',"'").replace('“','"').replace('”','"').replace('→',' > ')

class Report:
    def __init__(self,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        self.c=canvas.Canvas(str(path),pagesize=(W,H))
        self.c.setTitle('GodelOS Integrated Mind V8 - Construction and Evidence')
        self.c.setAuthor('GodelOS Research Programme')
        self.page=0
    def text(self,s,x,top,w,h,size=11,color=INK,bold=False,leading=None):
        style=ParagraphStyle('box',fontName='MindSansBold' if bold else 'MindSans',fontSize=size,leading=leading or size*1.4,textColor=colors.HexColor(color))
        p=Paragraph(escape(normal(s)).replace('\n','<br/>'),style)
        _,height=p.wrap(w,h)
        if height>h+.1:raise ValueError(f'Page {self.page}: text overflow {height:.1f}>{h}: {s[:80]}')
        if top+height>H-31:raise ValueError(f'Page {self.page}: footer overlap: {s[:80]}')
        p.drawOn(self.c,x,H-top-height)
        return height
    def rect(self,x,top,w,h,fill,stroke=None,r=9):
        self.c.setFillColor(colors.HexColor(fill));self.c.setStrokeColor(colors.HexColor(stroke or fill));self.c.setLineWidth(.7)
        self.c.roundRect(x,H-top-h,w,h,r,fill=1,stroke=bool(stroke))
    def start(self,number,title,subtitle=''):
        if self.page:self.c.showPage()
        self.page+=1;self.c.setFillColor(colors.HexColor(PAPER));self.c.rect(0,0,W,H,fill=1,stroke=0)
        self.c.setFillColor(colors.HexColor(INK));self.c.rect(0,H-7,W,7,fill=1,stroke=0)
        self.text(f'GODELOS / INTEGRATED MIND V8 / {number}',36,24,740,17,9,MINT,True)
        self.text(title,36,48,765,48,27,INK,True,32)
        if subtitle:self.text(subtitle,36,97,765,39,10.4,MUTED)
        self.c.setFont('MindSans',8);self.c.setFillColor(colors.HexColor(MUTED));self.c.drawString(36,18,'ENGINEERING RECORD / 09 SEP 2026 / ACTUAL DATA + EXPLICIT LIMITS')
        self.c.drawRightString(W-36,18,f'{self.page:02d} / 08')
    def card(self,x,top,w,h,title,body,accent=MINT):
        self.rect(x,top,w,h,'#ffffff',PALE)
        self.rect(x,top,w,4,accent,r=0)
        self.text(title,x+14,top+15,w-28,35,12,accent,True)
        self.text(body,x+14,top+54,w-28,h-65,10)
    def figure(self,path,x,top,w,h):
        with Image.open(path) as im:iw,ih=im.size
        scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
        self.c.drawImage(ImageReader(str(path)),x+(w-dw)/2,H-top-dh,width=dw,height=dh,mask='auto')
    def line(self,a,b,color=MUTED,arrow=True):
        x1,y1=a;x2,y2=b;y1=H-y1;y2=H-y2
        self.c.setStrokeColor(colors.HexColor(color));self.c.setLineWidth(1.6);self.c.line(x1,y1,x2,y2)
        if arrow:
            import math
            theta=math.atan2(y2-y1,x2-x1)
            for offset in (-.45,.45):self.c.line(x2,y2,x2-7*math.cos(theta+offset),y2-7*math.sin(theta+offset))
    def end(self):
        assert self.page==8
        self.c.save()

def charts(analysis,out):
    out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':MUTED,'axes.labelcolor':INK,'text.color':INK,'xtick.color':MUTED,'ytick.color':MUTED,'figure.facecolor':PAPER,'axes.facecolor':PAPER,'savefig.facecolor':PAPER})
    r1,r2=analysis['runs'];paths={}
    def save(name,fig):
        path=out/(name+'.png');fig.savefig(path,dpi=190,bbox_inches='tight');plt.close(fig);paths[name]=path
    fig,ax=plt.subplots(figsize=(7.3,2.15))
    for y,r in enumerate((r1,r2)):
        strict=r['completed']-r['format_repairs'];repair=r['format_repairs'];fail=r['failed']
        left=0
        for v,color in ((strict,MINT),(repair,GOLD),(fail,CORAL)):
            ax.barh(y,v,left=left,color=color,height=.55)
            if v:ax.text(left+v/2,y,str(v),ha='center',va='center',fontweight='bold',color=INK)
            left+=v
    ax.set_yticks([0,1],['R1','R2']);ax.invert_yaxis();ax.set_xlim(0,18);ax.set_xticks([0,6,12,18]);ax.set_xlabel('Provider completions received')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=MINT,label='Strict parse'),Patch(color=GOLD,label='Recorded brace repair'),Patch(color=CORAL,label='Rejected')],loc='upper center',bbox_to_anchor=(.5,-.4),ncol=3,frameon=False,fontsize=8)
    save('completion-accounting',fig)
    fig,axs=plt.subplots(1,2,figsize=(11.7,3.7),gridspec_kw={'width_ratios':[1.1,1]})
    ax=axs[0]
    kinds=['imagination','perception','tension','reflection']
    for c in r2['cycles']:
        y=kinds.index(c['focus']);ax.scatter(c['episode'],y,s=270,color=KIND_COLORS[c['focus']],zorder=3)
        ax.text(c['episode'],y,str(c['episode']),ha='center',va='center',color='white',fontweight='bold')
    ax.plot([c['episode'] for c in r2['cycles']],[kinds.index(c['focus']) for c in r2['cycles']],color='#bec8d3',zorder=1)
    ax.set_yticks(range(4),[k.title() for k in kinds]);ax.set_xticks(range(1,9));ax.set_ylim(-.5,3.5);ax.invert_yaxis();ax.set_xlabel('Episode');ax.set_title('Observed attention',loc='left',fontweight='bold',pad=15)
    ax=axs[1]
    for key,color in zip(('curiosity','affiliation','coherence','agency'),(VIOLET,SKY,CORAL,MINT)):
        ax.plot([c['episode'] for c in r2['cycles']],[c['drives'][key] for c in r2['cycles']],marker='o',color=color,label=key.title())
    ax.set_ylim(0,1);ax.set_xticks(range(1,9));ax.set_xlabel('Episode');ax.set_ylabel('Designed control variable');ax.set_title('Drive state after each cycle',loc='left',fontweight='bold',pad=15);ax.legend(fontsize=8,ncol=2,frameon=False,loc='lower left');ax.grid(axis='y',alpha=.15)
    fig.tight_layout(pad=2);save('trajectory-and-drives',fig)
    fig,ax=plt.subplots(figsize=(6.7,3.4))
    conds=['none','affect','workspace','memory','self_model'];names=['Full','Affect removed','Focus replaced','Memory removed','Self-model removed']
    pos=np.arange(5);cites=[];retrieval=[]
    for k in conds:
        rows=[b for b in r2['branches'] if b['ablation']==k and b['status']=='completed'];cites.append(np.mean([b['cited'] for b in rows]));retrieval.append(np.mean([b['retrieved'] for b in rows]))
    ax.barh(pos-.17,retrieval,height=.32,color='#c7d7e7',label='Retrieved')
    ax.barh(pos+.17,cites,height=.32,color=VIOLET,label='Cited valid IDs')
    ax.set_yticks(pos,names);ax.invert_yaxis();ax.set_xlim(0,3.3);ax.set_xticks([0,1,2,3]);ax.set_xlabel('Memories per continuation (mean of two)');ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=2,frameon=False,fontsize=8);fig.tight_layout();save('memory-route',fig)
    fig,ax=plt.subplots(figsize=(6.5,3.5))
    rows=[c for c in r2['cycles'] if c['brier'] is not None]
    ax.bar([str(c['episode']) for c in rows],[c['brier'] for c in rows],color=[VIOLET,VIOLET,CORAL,GOLD],width=.55)
    ax.axhline(6/7,color=MUTED,ls='--',label='Uniform seven-kind forecast: 0.857')
    for i,c in enumerate(rows):ax.text(i,c['brier']+.045,f"{c['brier']:.3f}",ha='center',fontsize=9)
    ax.set_ylim(0,2);ax.set_xlabel('Eligible autonomous episode');ax.set_ylabel('Brier error (lower is better)');ax.legend(frameon=False,loc='upper left',fontsize=8);fig.tight_layout();save('forecast-errors',fig)
    return paths

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--analysis',type=Path,default=ROOT/'research_artifacts/cognitive_sovereignty/integrated-mind-v8-analysis/analysis.json')
    p.add_argument('--screenshot',type=Path,default=ROOT/'output/deploy/godelos-integrated-mind-v8-report-view.jpg')
    p.add_argument('--detail-screenshot',type=Path,default=ROOT/'output/deploy/godelos-integrated-mind-v8-detail.jpg')
    p.add_argument('--output',type=Path,default=ROOT/'output/pdf/godelos-integrated-mind-v8-report.pdf')
    p.add_argument('--figures',type=Path,default=ROOT/'output/research/integrated-mind-v8/figures')
    args=p.parse_args();a=json.loads(args.analysis.read_text());r1,r2=a['runs'];figs=charts(a,args.figures);r=Report(args.output)
    r.start('01 / CONSTRUCTION','Build the organisation.','A deliberately engineered recurrent mind: attention, imagination, memory, intention and self-observation.')
    r.card(36,147,242,153,'36 REAL COMPLETIONS','Two engineering runs with DeepSeek. 31 structured results applied; five rejected results retained.',MINT)
    r.card(299,147,242,153,'8 CONTINUING EPISODES','The corrected run completed its full trajectory. One chosen intention survived the interruptions and handler reconstruction.',SKY)
    r.card(562,147,242,153,'2 IDEAS RETURNED','Images generated in earlier episodes later became the selected focus. Their recorded IDs establish the connection.',VIOLET)
    r.figure(figs['completion-accounting'],36,325,470,194)
    r.text('What this establishes',540,327,250,30,16,INK,True)
    r.text('An executable recurrent prototype whose internal records affect later operation. Accurate self-knowledge remains incomplete. Subjective experience has not been established.',540,367,250,118,12)
    r.text('The research objective is construction of a mind. Office-task efficiency is not used as a substitute for that objective.',36,525,750,28,10,MUTED)

    r.start('02 / ARCHITECTURE','One loop, shared consequences.','Implementation map. Arrows show information flow through software components, not neural activity.')
    r.card(36,146,238,130,'1. CONTACT + DRIVES','Human input, curiosity, affiliation, coherence and agency enter a competitive attention process.',SKY)
    r.card(303,146,238,130,'2. WORKSPACE','Select a focus; retrieve up to three episodes. Habituation reduces bids for repeated items.',MINT)
    r.card(570,146,234,130,'3. MODEL INFERENCE','The selected focus, explicit self-model and recorded history enter the same call used for conversation.',VIOLET)
    r.card(36,324,238,147,'6. NEXT CANDIDATES','Generated thoughts, imagined objects, intentions and tensions compete again. Their effects remain inspectable.',VIOLET)
    r.card(303,324,238,147,'5. PERSISTENCE','Retain memories, intentions and reasons. Raw completions stay separate from the revised agent state.',SKY)
    r.card(570,324,234,147,'4. SELF-OBSERVATION','Commit a forecast for the next tick. Compare with observation. Save interpretations and proposed revisions.',GOLD)
    r.line((274,211),(303,211));r.line((541,211),(570,211));r.line((686,276),(686,324));r.line((570,397),(541,397));r.line((303,397),(274,397));r.line((153,324),(153,296));r.line((153,296),(422,296),arrow=False);r.line((422,296),(422,276))
    r.text('The operator can interrupt, pause, inspect or resume. The scheduler continues discrete ticks after the browser closes when enabled. Code-revision proposals do not install themselves.',36,492,763,48,11)

    r.start('03 / TRAJECTORY','Generated content came back into play.','R2: eight successive episodes from the same persistent agent, including three operator interruptions.')
    r.figure(figs['trajectory-and-drives'],30,144,780,252)
    r.card(36,411,369,127,'EPISODE 1 > EPISODE 3','"River cutting its own channel" was imagined, saved and later selected by its persistent object ID.',VIOLET)
    r.card(431,411,373,127,'EPISODE 2 > EPISODE 5','"Two rooms connected by a corridor" returned after intervening episodes. The controller linked imagination to attention.',SKY)

    r.start('04 / INTERVENTIONS','Remove a connection. Observe the result.','Five conditions, two continuations each, from one shared R2 checkpoint. These are component-route interventions.')
    rows=[('Full','Imagination','2/2'),('Affect removed','Tension','2/2'),('Focus replaced','Inquiry','2/2'),('Memory removed','Imagination','2/2'),('Self-model removed','Imagination','2/2')]
    r.rect(36,152,364,32,INK,r=3)
    for x,s,w in [(48,'Condition',160),(216,'Observed focus',118),(347,'Runs',43)]:r.text(s,x,160,w,20,10,'#ffffff',True)
    for i,(c,f,n) in enumerate(rows):
        top=188+i*39;r.rect(36,top-3,364,36,'#ffffff' if i%2==0 else PALE,r=3);r.text(c,48,top+5,163,25,10);r.text(f,216,top+5,124,25,10,KIND_COLORS[f.lower()],True);r.text(n,351,top+5,43,25,10)
    r.figure(figs['memory-route'],413,145,400,250)
    r.card(36,419,368,121,'CAUSAL CONNECTION DEMONSTRATED','Affect removal changed the selected focus in both repetitions. Workspace replacement changes it by construction.',MINT)
    r.card(431,419,373,121,'IDENTITY EFFECT NOT ESTABLISHED','The self-model projection removal did not change focus. Other self-relevant context remained. No identity-specific inference follows.',CORAL)

    r.start('05 / DIAGNOSIS','Its story about itself was wrong.','Episode 8 supplied the most informative failure: confident self-history contradicted the recorded events.')
    r.rect(36,150,766,84,'#fae9e4',r=8)
    r.text('Model claim: "ticks 3,5,7 were reflections"',53,164,730,30,19,CORAL,True)
    r.text('Recorded events: 3 = imagination; 5 = imagination; 7 = tension.',53,200,730,27,12)
    r.figure(figs['forecast-errors'],31,249,431,260)
    r.text('Mean Brier: 0.886',493,261,285,37,21,INK,True)
    r.text('Uniform baseline: 0.857. On four eligible autonomous ticks, the model did not beat this simple forecast. The sequence is too small and dependent for a population claim.',493,310,290,103,12)
    r.text('Engineering response',493,424,290,28,14,MINT,True)
    r.text('The final build supplies actual event history and validates tick/kind references. This correction has local test coverage; the additional live validation was blocked.',493,459,290,77,11)

    r.start('06 / OPERATOR INTERFACE','Talk to the same continuing system.','Actual R2 records shown in the new interface. Read-only evidence preview; interactive controls were tested separately with synthetic responses.')
    if args.screenshot.exists():r.figure(args.screenshot,36,145,768,386)
    else:r.text('Screenshot will be added during final visual verification.',36,200,730,70,16)
    r.text('The displayed episode-eight error is retained verbatim. An inspectable mistake is part of the experimental record.',36,538,760,22,9.5,MUTED)

    r.start('07 / BUILD DECISION','Give self-observation a factual substrate.','The next construction target is a learned causal model of its own organisation and possible interventions.')
    r.card(36,149,242,201,'ALREADY BUILT','Shared attention\nPersisted intentions\nImagination re-entry\nAppraisal-to-attention coupling\nMemory retrieval\nForecast instrumentation\nConversation and pause',MINT)
    r.card(299,149,242,201,'ADDED AFTER THE FAILURE','Eight recorded attention events in context. Structured event references checked before state update. Existing intention priorities can now alter future bids.',SKY)
    r.card(562,149,242,201,'NEXT EXPERIMENT','Predict what removing a component will do. Compare own event history, matched third-person history and withheld history across independently started agents.',VIOLET)
    r.text('What remains unsettled',36,376,730,28,18,INK,True)
    r.text('A working recurrent organisation does not settle whether there is subjective experience. It also does not establish calibrated self-knowledge: this run contains a clear counterexample. The programme can now investigate these questions through changes to real components.',36,418,745,76,12)
    r.text('No original A-F gate is newly awarded by this component diagnostic. No weight update or autonomous code promotion occurred.',36,517,750,29,10,MUTED)

    r.start('08 / REPRODUCTION','A complete package, with the failures included.','The ZIP contains the Functions, UI, tests, report, analysis and collected V8 evidence. Production deployment was not performed in this pass.')
    r.card(36,146,369,178,'RUN AND INSPECT','npm ci\nnpm test\nnode scripts/live-mind.mjs new-run\nnode scripts/analyse-mind.mjs analysis new-run\n\nSet DEEPSEEK_API_KEY in the environment. The full schedule uses 18 calls. Existing output directories are refused.',MINT)
    r.card(431,146,373,178,'DEPLOY THE COMPLETE APP','Unzip; select the existing site with Netlify CLI. Set DEEPSEEK_API_KEY and SOVEREIGNTY_ACCESS_TOKEN for Functions.\n\nnpx netlify-cli deploy --build --prod\n\nSource-folder drag and drop alone does not install Functions.',SKY)
    r.card(36,349,369,168,'EVIDENCE ACCOUNTING','36 confirmed completions; 311,279 tokens. R1: 13 applied, five rejected. R2: 18 applied, two with explicit brace repairs. 52 tests pass. The six-call follow-up was blocked by automatic approval review before any completion; no retry was made.',CORAL)
    r.card(431,349,373,168,'AUTONOMY AND PROVENANCE','AUTONOMY_ENABLED=true\nAUTONOMY_INTERVAL_MINUTES=15\nAUTONOMY_DAILY_CALL_LIMIT=24\n\nExisting environment values override defaults. Raw transcripts, checksums, commands and limitations accompany the report.',VIOLET)
    r.text('Netlify reference: docs.netlify.com/build/functions/get-started/  |  scheduled-functions/ (accessed 09 Sep 2026)',36,536,760,23,8.5,MUTED)
    r.end();print(args.output)

if __name__=='__main__':main()
