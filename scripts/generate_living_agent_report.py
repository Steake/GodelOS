#!/usr/bin/env python3
"""Create the V7 visual research report from immutable live-run evidence."""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research_artifacts/cognitive_sovereignty/living-agent-v7-live-r2/living-agent-live-report.json"
OUT = ROOT / "output/pdf/godelos-living-sovereign-agent-v7-report.pdf"
SCREENSHOT = Path("/workspace/scratch/godelos-living-agent-v7-preview.jpg")

INK = colors.HexColor("#13263D")
MINT = colors.HexColor("#39E6B0")
VIOLET = colors.HexColor("#7A64FF")
CORAL = colors.HexColor("#FF6B74")
SKY = colors.HexColor("#45B8FF")
CREAM = colors.HexColor("#F6F3EA")
PAPER = colors.HexColor("#FCFBF7")
MUTED = colors.HexColor("#667085")
PALE = colors.HexColor("#E9EEF4")


class LatencyBars(Flowable):
    def __init__(self, rows, width=225*mm, height=55*mm):
        super().__init__(); self.rows=rows; self.width=width; self.height=height
    def draw(self):
        c=self.canv; maxv=max(r[1] for r in self.rows); left=48*mm; top=self.height-6*mm
        palette=[MINT,VIOLET,CORAL,SKY,colors.HexColor("#F5B83B")]
        for i,(label,value) in enumerate(self.rows):
            y=top-i*10*mm
            c.setFont("Helvetica-Bold",8); c.setFillColor(INK); c.drawRightString(left-3*mm,y,label)
            c.setFillColor(PALE); c.roundRect(left,y-3*mm,155*mm,5*mm,2*mm,fill=1,stroke=0)
            c.setFillColor(palette[i]); c.roundRect(left,y-3*mm,155*mm*value/maxv,5*mm,2*mm,fill=1,stroke=0)
            c.setFillColor(INK); c.setFont("Helvetica-Bold",8); c.drawString(left+158*mm,y-1*mm,f"{value/1000:.1f}s")


class AffectWheel(Flowable):
    def __init__(self, values, width=105*mm, height=67*mm):
        super().__init__(); self.values=values; self.width=width; self.height=height
    def draw(self):
        c=self.canv; cx=25*mm; cy=34*mm; radius=22*mm
        palette=[MINT,VIOLET,CORAL,SKY,colors.HexColor("#F5B83B")]
        import math
        pts=[]
        keys=list(self.values)
        for ring in (.25,.5,.75,1):
            ringpts=[]
            for i in range(len(keys)):
                a=math.pi/2-2*math.pi*i/len(keys); ringpts.append((cx+radius*ring*math.cos(a),cy+radius*ring*math.sin(a)))
            c.setStrokeColor(PALE); p=c.beginPath(); p.moveTo(*ringpts[0]); [p.lineTo(*x) for x in ringpts[1:]]; p.close(); c.drawPath(p)
        for i,k in enumerate(keys):
            a=math.pi/2-2*math.pi*i/len(keys); x=cx+radius*math.cos(a); y=cy+radius*math.sin(a)
            c.setStrokeColor(PALE); c.line(cx,cy,x,y); c.setFillColor(INK); c.setFont("Helvetica-Bold",7)
            c.drawCentredString(cx+(radius+7*mm)*math.cos(a),cy+(radius+5*mm)*math.sin(a),k)
            a2=math.pi/2-2*math.pi*i/len(keys); v=self.values[k]; pts.append((cx+radius*v*math.cos(a2),cy+radius*v*math.sin(a2)))
        p=c.beginPath(); p.moveTo(*pts[0]); [p.lineTo(*x) for x in pts[1:]]; p.close(); c.setFillColor(colors.Color(.24,.9,.69,alpha=.25)); c.setStrokeColor(MINT); c.setLineWidth(2); c.drawPath(p,fill=1,stroke=1)
        c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(63*mm,48*mm,"Functional affect")
        c.setFont("Helvetica",8); c.setFillColor(MUTED); c.drawString(63*mm,41*mm,"Attention state, not a claim")
        c.drawString(63*mm,36*mm,"of subjective feeling.")
        c.setFillColor(MINT); c.roundRect(63*mm,23*mm,35*mm,9*mm,3*mm,fill=1,stroke=0)
        c.setFillColor(INK); c.setFont("Helvetica-Bold",10); c.drawCentredString(80.5*mm,26*mm,"curiosity 0.95")


def styles():
    s=getSampleStyleSheet()
    return {
        "h1":ParagraphStyle("h1",parent=s["Title"],fontName="Helvetica-Bold",fontSize=32,leading=34,textColor=INK,spaceAfter=8*mm),
        "h2":ParagraphStyle("h2",parent=s["Heading2"],fontName="Helvetica-Bold",fontSize=22,leading=25,textColor=INK,spaceAfter=5*mm),
        "h3":ParagraphStyle("h3",parent=s["Heading3"],fontName="Helvetica-Bold",fontSize=12,leading=14,textColor=INK,spaceAfter=2*mm),
        "body":ParagraphStyle("body",parent=s["BodyText"],fontName="Helvetica",fontSize=9.2,leading=13,textColor=INK,spaceAfter=3*mm),
        "small":ParagraphStyle("small",parent=s["BodyText"],fontName="Helvetica",fontSize=7.5,leading=10,textColor=MUTED),
        "kicker":ParagraphStyle("kicker",parent=s["BodyText"],fontName="Helvetica-Bold",fontSize=8,leading=10,textColor=VIOLET,spaceAfter=3*mm),
        "quote":ParagraphStyle("quote",parent=s["BodyText"],fontName="Helvetica-Oblique",fontSize=11,leading=15,textColor=INK,leftIndent=6*mm,rightIndent=6*mm,borderColor=MINT,borderWidth=0,borderPadding=5*mm,backColor=colors.HexColor("#E9FFF8")),
    }


def card(title, body, st, accent=MINT):
    table=Table([[Paragraph(title,st["h3"])],[Paragraph(body,st["body"])]],colWidths=[76*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.white),("BOX",(0,0),(-1,-1),.6,PALE),("LINEABOVE",(0,0),(-1,0),3,accent),("LEFTPADDING",(0,0),(-1,-1),5*mm),("RIGHTPADDING",(0,0),(-1,-1),5*mm),("TOPPADDING",(0,0),(-1,-1),4*mm),("BOTTOMPADDING",(0,0),(-1,-1),4*mm)]))
    return table


def page(canvas, doc):
    canvas.saveState(); w,h=landscape(A4); canvas.setFillColor(PAPER); canvas.rect(0,0,w,h,fill=1,stroke=0)
    canvas.setFillColor(INK); canvas.rect(0,h-6*mm,w,6*mm,fill=1,stroke=0)
    canvas.setFillColor(MINT); canvas.rect(0,0,w,2*mm,fill=1,stroke=0)
    canvas.setFont("Helvetica-Bold",7); canvas.setFillColor(MUTED); canvas.drawString(18*mm,8*mm,"GODELOS / LIVING SOVEREIGN AGENT V7 / MEASURED 09 SEP 2026")
    canvas.drawRightString(w-18*mm,8*mm,str(doc.page)); canvas.restoreState()


def main():
    data=json.loads(DATA.read_text())
    st=styles(); OUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUT),pagesize=landscape(A4),leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=14*mm,title="GodelOS Living Sovereign Agent V7")
    story=[]
    story += [Paragraph("ENGINEERING EVIDENCE / LIVE DEEPSEEK PASS",st["kicker"]),Paragraph("A mind that can wander<br/>without losing its epistemic footing",st["h1"]),Paragraph("V7 implements persistent imagination, functional affect, self-directed cognition, position continuity, contradiction preservation, social state and an experimental escape hatch. Five real model calls tested the complete cognitive cycle.",ParagraphStyle("deck",parent=st["body"],fontSize=14,leading=19,textColor=MUTED,spaceAfter=7*mm))]
    metrics=[["5 / 5","real cycles completed"],["11 -> 16","persistent state versions"],["3","imaginations preserved"],["0","imaginations promoted to belief"]]
    mt=Table([[Paragraph(f"<b>{a}</b><br/><font size='8'>{b}</font>",st["body"]) for a,b in metrics]],colWidths=[61*mm]*4)
    mt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),INK),("TEXTCOLOR",(0,0),(-1,-1),colors.white),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),5*mm),("BOTTOMPADDING",(0,0),(-1,-1),5*mm),("INNERGRID",(0,0),(-1,-1),.5,colors.HexColor("#34495E"))])); story += [mt,Spacer(1,6*mm)]
    if SCREENSHOT.exists():
        im=Image(str(SCREENSHOT),width=156*mm,height=76*mm); story.append(im)
    story += [PageBreak(),Paragraph("01 / THE BUILD",st["kicker"]),Paragraph("A persistent cognitive control plane",st["h2"])]
    rows=[[card("Standing objective","Increase epistemic sovereignty through reasoned positions, provenance discrimination, disconfirmation, productive contradiction and revisable commitments.",st,MINT),card("Wandering mind","Reverie, cognitive drift and heterodox exploration produce labelled possibilities without granting them belief authority.",st,VIOLET),card("Functional affect","Appraisal variables bias attention and agenda choice. Triggers and action biases remain visible to the operator.",st,CORAL)],
          [card("Social continuity","Relationship-specific trust, affinity, unresolved social tensions and companionship needs persist across calls.",st,SKY),card("Autonomous cadence","A scheduled dispatcher and leased background worker run bounded thought episodes with a separate daily quota.",st,MINT),card("Research escape hatch","Any live belief, tension or imagination can become a controlled multi-round branch experiment.",st,VIOLET)]]
    grid=Table(rows,colWidths=[81*mm]*3,rowHeights=[52*mm,52*mm],hAlign="LEFT"); grid.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2*mm),("RIGHTPADDING",(0,0),(-1,-1),2*mm),("TOPPADDING",(0,0),(-1,-1),2*mm)])); story += [grid,Spacer(1,5*mm),Paragraph("Control boundary: imagination may propose. Affect may prioritize. Neither may silently rewrite a belief or promote code. Promotion still requires independent task evidence.",st["quote"])]
    story += [PageBreak(),Paragraph("02 / THE REAL RUN",st["kicker"]),Paragraph("Five calls. One continuous external state.",st["h2"])]
    lat=[(x["mode"].replace("_"," ").title(),x["latency_ms"]) for x in data["cycles"]]; story += [LatencyBars(lat),Spacer(1,4*mm)]
    episode_rows=[["Mode","State","Status","What changed"]]
    changes=["Operational hypothesis; no belief update","2 imaginations; wonder and curiosity increased","Affect checked; tension preserved","Experiment failure conditions refined","1 imagination; causal/contextual tension sharpened"]
    for x,ch in zip(data["cycles"],changes): episode_rows.append([x["mode"].replace("_"," "),str(x.get("state_version","-")),x["status"],ch])
    t=Table(episode_rows,colWidths=[48*mm,20*mm,25*mm,152*mm]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INK),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),.5,PALE),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F2F5F8")]),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3*mm),("BOTTOMPADDING",(0,0),(-1,-1),3*mm)])); story += [t]
    story += [PageBreak(),Paragraph("03 / CAUSAL TRACE",st["kicker"]),Paragraph("Inspiration entered attention - not belief",st["h2"])]
    flow=[("1  WONDER","Reverie linked a self-reading library to a river shaped by its banks."),("2  LABEL","Both became imagined_not_adopted with attraction, absurdity and a test question."),("3  APPRAISE","Wonder and curiosity rose; the recorded action bias became experiment refinement."),("4  USE","Later episodes reused the metaphor to sharpen controls and seek disconfirmation."),("5  REFUSE","No episode promoted the metaphor to belief; the agent named elegance as a bias risk.")]
    ft=Table([[Paragraph(a,st["h3"]),Paragraph(b,st["body"])] for a,b in flow],colWidths=[42*mm,201*mm]); ft.setStyle(TableStyle([("LINEBEFORE",(0,0),(0,-1),4,MINT),("BACKGROUND",(0,0),(-1,-1),colors.white),("GRID",(0,0),(-1,-1),.4,PALE),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),4*mm),("BOTTOMPADDING",(0,0),(-1,-1),4*mm),("LEFTPADDING",(0,0),(-1,-1),5*mm)])); story += [ft,Spacer(1,5*mm)]
    affect=data["final"]["affect"]; vals={"curiosity":affect["curiosity"],"wonder":affect["wonder"],"activation":affect["activation"],"warmth":affect["social_warmth"],"calm":1-affect["frustration"]}
    causal_bottom=Table([[AffectWheel(vals,width=105*mm,height=61*mm),Paragraph("<b>Measured behavioural trace</b><br/><br/>An internally labelled imaginative object changed the persisted appraisal vector and its action bias. The later inference then cited that construct while refining an experiment.<br/><br/><b>Boundary:</b> ablation against matched controls has not yet shown that this improves task utility.",st["quote"])]],colWidths=[112*mm,131*mm],rowHeights=[63*mm])
    causal_bottom.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),2*mm),("RIGHTPADDING",(0,0),(-1,-1),2*mm)])); story += [causal_bottom]
    story += [PageBreak(),Paragraph("04 / IMAGINATION GALLERY",st["kicker"]),Paragraph("Ideas kept alive without being mistaken for facts",st["h2"])]
    ims=data["final"]["imaginations"]
    cards=[]
    for i,it in enumerate(ims):
        body=f"<b>Image</b><br/>{it['image_or_idea']}<br/><br/><b>Test question</b><br/>{it['test_question']}<br/><br/><font color='#667085'>Attraction {it['attraction']:.2f} / Absurdity {it['absurdity']:.2f} / {it['status']}</font>"
        cards.append(card(it["title"],body,st,[VIOLET,MINT,CORAL][i%3]))
    gallery=Table([cards],colWidths=[81*mm]*3); gallery.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2*mm),("RIGHTPADDING",(0,0),(-1,-1),2*mm)])); story += [gallery]
    story += [PageBreak(),Paragraph("05 / WHAT THE DATA SAYS",st["kicker"]),Paragraph("Architecture proof, not metaphysical proof",st["h2"])]
    yes=["External state preserved three labelled imaginative constructs across stateless calls.","Reverie changed a functional appraisal state that later influenced attention and experiment design.","The agent maintained a position boundary: attractive imagery was repeatedly not adopted as belief.","A complete five-mode cycle ran against DeepSeek with immutable provider evidence.","A malformed prior run exposed a real instrumentation defect, which is now tested and fixed."]
    no=["No evidence of phenomenal emotion, consciousness, free will or uninterrupted subjective identity.","No proof that the model originated its constitutional objective independently.","No controlled evidence yet that imagination or affect improves held-out task performance.","No weight update or autonomous code promotion occurred.","One successful sequence is not a replication or a statistically supported capability claim."]
    def bullets(items): return "<br/>".join("- "+x for x in items)
    yn=Table([[card("SUPPORTED",bullets(yes),st,MINT),card("NOT SUPPORTED",bullets(no),st,CORAL)]],colWidths=[121*mm,121*mm]); yn.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2*mm),("RIGHTPADDING",(0,0),(-1,-1),2*mm)])); story += [yn,Spacer(1,7*mm),Paragraph("Most important result: the interesting event was restraint. The model used imagination to create a better experimental question, but it did not turn the compelling narrative into autobiographical certainty.",st["quote"])]
    story += [PageBreak(),Paragraph("06 / OPERATOR SURFACE",st["kicker"]),Paragraph("The system is conversational before it is diagnostic",st["h2"])]
    if SCREENSHOT.exists(): story.append(Image(str(SCREENSHOT),width=235*mm,height=114*mm))
    story += [Spacer(1,4*mm),Paragraph("The first deployed view exposes the live agent: speak to it, challenge positions, preserve contradictions, enter reverie, wander, inspect affect, or turn an idea into an autonomous research campaign. The forensic workbench remains available behind it.",st["body"])]
    story += [PageBreak(),Paragraph("07 / ENGINEERING DECISION",st["kicker"]),Paragraph("Build the imagination ablation bridge next",st["h2"]),Paragraph("Do not promote functional affect into the active policy simply because this transcript is compelling. Connect appraisal and imagination to a preregistered policy selector, then compare three otherwise identical agents on independently authored interruption-recovery tasks.",st["quote"]),Spacer(1,6*mm)]
    exp=[["Branch","State available","Purpose"],["Identity + imagination","Authenticated autobiography, positions, affect and imagined candidates","Candidate system"],["Content matched","Same task-relevant facts without identity or affect framing","Separates information from self-model"],["Imagination ablated","Identity-bearing state with imaginative objects removed","Tests marginal utility of wandering"],["No state","No inherited record","True baseline"]]
    et=Table(exp,colWidths=[47*mm,100*mm,99*mm]); et.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INK),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),.5,PALE),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F2F5F8")]),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),3*mm),("BOTTOMPADDING",(0,0),(-1,-1),3*mm)])); story += [et,Spacer(1,5*mm),Paragraph("Promotion rule: identity plus imagination must improve delayed transfer utility over content-matched, ablated and no-state branches, and the lower uncertainty bound must clear the preregistered effect threshold. Otherwise it remains an expressive feature, not a control-loop capability.",st["body"])]
    story += [PageBreak(),Paragraph("08 / REPRODUCE + DEPLOY",st["kicker"]),Paragraph("One archive, one explicit route",st["h2"])]
    cmd="""<font name='Courier' size='7'>cd deploy/netlify-sovereignty-lab<br/>node --test tests/*.test.mjs<br/>DEEPSEEK_MAX_TOKENS=3500 node<br/> scripts/live-agent-life.mjs [output-dir]<br/><br/>cd ../..<br/>python3 scripts/generate_living_agent_report.py<br/>python3 scripts/build_netlify_sovereignty_bundle.py</font>"""
    deploy_cards=Table([[card("RESEARCH",cmd,st,VIOLET),card("NETLIFY","Unzip the archive. Run npm ci, link the site with Netlify CLI, configure DEEPSEEK_API_KEY and SOVEREIGNTY_ACCESS_TOKEN, optionally enable the autonomous cadence variables, then run npx netlify-cli deploy --build --prod.",st,MINT),card("EVIDENCE","Machine-readable result: research_artifacts/cognitive_sovereignty/living-agent-v7-live-r2/living-agent-live-report.json. Full method: docs/LIVING_SOVEREIGN_AGENT_V7.md. The failed attempt is retained separately.",st,CORAL)]],colWidths=[81*mm]*3)
    deploy_cards.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2*mm),("RIGHTPADDING",(0,0),(-1,-1),2*mm)])); story += [deploy_cards]
    doc.build(story,onFirstPage=page,onLaterPages=page)
    print(OUT)


if __name__ == "__main__": main()
