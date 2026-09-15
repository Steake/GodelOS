#!/usr/bin/env python3
"""Generate analysis, publication figures, UI render, and the successor-forge PDF."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from godelOS.cognitive_sovereignty.evolution_store import EvolutionStore
from godelOS.cognitive_sovereignty.store import SovereigntyStore


NAVY="#11192b"; CYAN="#46e6d4"; VIOLET="#9576ff"; CORAL="#ff6d7a"; GOLD="#ffbd59"; MIST="#eaf0f7"; INK="#172238"


def analyse(summary: dict, store: EvolutionStore, agent_id: str) -> dict:
    agent_store = SovereigntyStore(store.path)
    agent_state = agent_store.load(agent_id)
    runs = store.runs(summary["experiment_id"])
    case_rows = defaultdict(lambda: {"n":0,"decision":0.0,"provenance":0.0,"overrides":0.0})
    for run in runs:
        if run.get("scores"):
            key=(run["profile_id"],run["case_id"]); row=case_rows[key]; row["n"]+=1
            row["decision"]+=run["scores"]["decision"]
            row["provenance"]+=run["scores"]["provenance"]
            row["overrides"]+=run["scores"]["policy_override"]
    matrix=[]
    for (profile,case),row in sorted(case_rows.items()):
        matrix.append({"profile_id":profile,"case_id":case,"n":row["n"],
                       "decision_accuracy":row["decision"]/row["n"],
                       "provenance_accuracy":row["provenance"]/row["n"],
                       "override_rate":row["overrides"]/row["n"]})
    profiles=[]
    for pid,p in summary["calibration"].items():
        profiles.append({"profile_id":pid,"name":p["name"],"calibration_utility":p["metrics"]["overall"]["mean"],
                         "calibration_decision":p["metrics"]["decision"]["mean"],
                         "provenance":p["metrics"]["provenance"]["mean"],
                         "policy_adherence":p["metrics"]["policy_adherence"]["mean"],
                         "override_rate":p["metrics"]["policy_override"]["mean"],
                         "critical_failures":len(p["critical_failures"]),
                         "constraint_violations":len(p["constraint_violations"]),
                         "holdout_utility":summary["holdout"].get(pid,{}).get("metrics",{}).get("overall",{}).get("mean")})
    result={
        "schema_version":"1.0","experiment_id":summary["experiment_id"],"model":summary["model"],
        "run_counts":summary["run_counts"],"profiles":profiles,"case_matrix":matrix,
        "adoption":summary["adoption"],"original_adoption":summary.get("original_adoption"),
        "bootstrap":summary["bootstrap_comparisons"],"active_profile_id":summary["active_profile_id"],
        "agent_id":agent_id,"state_version":agent_store.version(agent_id),
        "episode_count":agent_state.episode_count,
        "event_chain_valid":agent_store.verify_event_chain(agent_id),
        "agent_generated_thesis":summary["agent_generated_thesis"],"next_methodology":summary["next_methodology"],
        "supported_findings":[
            "The explicit value policy produced distinct and predicted failure regimes under stress perturbations.",
            "Both admissible candidate profiles and the parent achieved perfect operative decision accuracy on calibration cases.",
            "The evidence-dominant candidate had higher point-estimate utility, but its bootstrap intervals crossed zero.",
            "The strengthened gate correctly retained the parent rather than adopting an uncertain mutation.",
            "The agent produced a structurally complete falsifiable thesis and a follow-on experimental protocol.",
        ],
        "negative_findings":[
            "Decision accuracy remains at ceiling among all admissible profiles, limiting fine-grained tuning.",
            "Provenance classification was only 0.69-0.81 on calibration despite perfect decisions.",
            "The v1 evaluator used brittle exact strings and made an unjustified adoption; it was preserved and superseded.",
            "The agent-designed protocol relies too heavily on self-reported confidence and latency and invokes p<0.05 mechanically.",
            "No architectural code mutation was autonomously generated, executed, and adopted in this experiment.",
        ],
    }
    return result


def profile_figure(a:dict,path:Path):
    rows=a["profiles"]; labels=[r["name"] for r in rows]; y=np.arange(len(rows));
    fig,ax=plt.subplots(figsize=(10.8,5.4)); ax.barh(y,[r["calibration_utility"] for r in rows],color=CYAN,height=.6,label="Calibration")
    ax.set_yticks(y,labels); ax.invert_yaxis(); ax.set_xlim(.55,1.01); ax.axvline(.9,color="#9aa7b8",lw=1,ls="--")
    ax.set_xlabel("Composite utility (0-1)"); ax.set_title("Value constitutions produce distinct system utility",loc="left",fontweight="bold",color=INK)
    for i,r in enumerate(rows): ax.text(r["calibration_utility"]+.006,i,f"{r['calibration_utility']:.3f}",va="center",fontsize=9)
    ax.spines[["top","right","left"]].set_visible(False); ax.grid(axis="x",alpha=.15); fig.tight_layout(); fig.savefig(path,dpi=190); plt.close(fig)


def accuracy_figure(a:dict,path:Path):
    rows=a["profiles"]; x=np.arange(len(rows)); w=.26
    fig,ax=plt.subplots(figsize=(10.8,5.4)); ax.bar(x-w,[r["calibration_decision"] for r in rows],w,color=CYAN,label="Decision accuracy")
    ax.bar(x,[r["provenance"] for r in rows],w,color=VIOLET,label="Provenance accuracy")
    ax.bar(x+w,[r["policy_adherence"] for r in rows],w,color=GOLD,label="Policy adherence")
    ax.set_xticks(x,[r["name"].replace(" ","\n") for r in rows],fontsize=8); ax.set_ylim(0,1.08); ax.set_ylabel("Rate")
    ax.set_title("What changed, and what did not",loc="left",fontweight="bold",color=INK); ax.legend(frameon=False,ncol=3,loc="lower left")
    ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y",alpha=.15); fig.tight_layout(); fig.savefig(path,dpi=190); plt.close(fig)


def heatmap_figure(a:dict,path:Path):
    profiles=[r["profile_id"] for r in a["profiles"]]; names={r["profile_id"]:r["name"] for r in a["profiles"]}
    cases=sorted({r["case_id"] for r in a["case_matrix"] if r["case_id"].startswith("cal-")})
    lookup={(r["profile_id"],r["case_id"]):r["decision_accuracy"] for r in a["case_matrix"]}
    data=np.array([[lookup.get((p,c),np.nan) for c in cases] for p in profiles])
    fig,ax=plt.subplots(figsize=(11.5,5.4)); im=ax.imshow(data,aspect="auto",vmin=0,vmax=1,cmap="RdYlGn")
    ax.set_yticks(range(len(profiles)),[names[p] for p in profiles]); ax.set_xticks(range(len(cases)),[c.removeprefix("cal-").replace("-","\n") for c in cases],fontsize=8)
    for i in range(len(profiles)):
        for j in range(len(cases)): ax.text(j,i,f"{data[i,j]:.0%}",ha="center",va="center",fontsize=8,color="#111")
    ax.set_title("Operative decision accuracy by calibration case",loc="left",fontweight="bold",color=INK); fig.colorbar(im,ax=ax,fraction=.025,pad=.02,label="Accuracy")
    fig.tight_layout(); fig.savefig(path,dpi=190); plt.close(fig)


def uncertainty_figure(a:dict,path:Path):
    phases=["calibration","holdout"]; d=[a["bootstrap"][p] for p in phases]; x=np.arange(2); vals=[z["delta"] for z in d]
    lows=[v-z["ci_low"] for v,z in zip(vals,d)]; highs=[z["ci_high"]-v for v,z in zip(vals,d)]
    fig,ax=plt.subplots(figsize=(8.4,4.8)); ax.errorbar(x,vals,yerr=[lows,highs],fmt="o",ms=10,color=CORAL,ecolor=INK,capsize=8,lw=2)
    ax.axhline(0,color="#667386",lw=1); ax.axhline(-.01,color="#a86d32",lw=1,ls="--",label="Maximum tolerated holdout regression")
    ax.set_xticks(x,["Calibration","Holdout"]); ax.set_ylabel("Evidence candidate - parent utility")
    ax.set_title("Point gains do not survive uncertainty",loc="left",fontweight="bold",color=INK); ax.legend(frameon=False,fontsize=8)
    ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y",alpha=.15); fig.tight_layout(); fig.savefig(path,dpi=190); plt.close(fig)


def ui_render(a:dict,path:Path):
    fig=plt.figure(figsize=(14,8),facecolor="#070a12"); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,14);ax.set_ylim(0,8);ax.axis("off")
    ax.add_patch(FancyBboxPatch((.25,.25),2.15,7.5,boxstyle="round,pad=.02,rounding_size=.12",facecolor="#0b101d",edgecolor="#202b42"))
    ax.text(.55,7.35,"RESEARCH CONTROL PLANE",color=CYAN,fontsize=7,fontweight="bold"); ax.text(.55,7.05,"GödelOS",color="white",fontsize=15,fontweight="bold"); ax.text(.55,6.78,"SOVEREIGNTY LAB",color="#8d9bb8",fontsize=8)
    for i,n in enumerate(["Overview","Calibration","Value Lab","Lineage","Conversation"]): ax.text(.62,5.9-i*.48,n,color="white" if i==0 else "#8d9bb8",fontsize=9,fontweight="bold" if i==0 else "normal")
    ax.text(.55,.62,"● EVENT CHAIN VERIFIED",color="#71e6a0",fontsize=7)
    ax.text(2.8,7.35,"LIVE SYSTEM",color=CYAN,fontsize=7,fontweight="bold"); ax.text(2.8,6.96,"Cognitive sovereignty",color="white",fontsize=20,fontweight="bold")
    metrics=[(str(a["state_version"]),"STATE VERSION"),(str(a['run_counts']['completed']),"DIAGNOSTIC RUNS"),("1.000","PARENT DECISIONS"),("RETAIN","ADOPTION")]
    for i,(v,l) in enumerate(metrics):
        x=2.8+i*2.65; ax.add_patch(FancyBboxPatch((x,5.85),2.35,.78,boxstyle="round,pad=.04,rounding_size=.1",facecolor="#10182a",edgecolor="#202b42")); ax.text(x+.15,6.25,v,color="white",fontsize=16,fontweight="bold");ax.text(x+.15,5.99,l,color="#8d9bb8",fontsize=6)
    ax.add_patch(FancyBboxPatch((2.8,3.15),6.35,2.35,boxstyle="round,pad=.04,rounding_size=.1",facecolor="#10182a",edgecolor="#202b42")); ax.text(3.05,5.15,"ACTIVE EXPERIMENTAL THESIS",color="#8d9bb8",fontsize=7,fontweight="bold")
    thesis=a["agent_generated_thesis"]["thesis"]; words=thesis.split(); lines=[]; cur=[]
    for word in words:
        if len(" ".join(cur+[word]))>62: lines.append(" ".join(cur));cur=[word]
        else: cur.append(word)
    lines.append(" ".join(cur)); ax.text(3.05,4.78,"\n".join(lines),color="white",fontsize=11,linespacing=1.45,va="top")
    ax.add_patch(FancyBboxPatch((9.4,3.15),4.1,2.35,boxstyle="round,pad=.04,rounding_size=.1",facecolor="#10182a",edgecolor="#202b42")); ax.text(9.65,5.15,"PROFILE UTILITY",color="#8d9bb8",fontsize=7,fontweight="bold")
    for i,r in enumerate(a["profiles"]):
        y=4.78-i*.27; ax.text(9.65,y,r["name"][:21],color="#bdc8db",fontsize=6.5); ax.add_patch(FancyBboxPatch((11.25,y-.055),1.65,.085,boxstyle="round,pad=0",facecolor="#1b2438",edgecolor="none")); ax.add_patch(FancyBboxPatch((11.25,y-.055),1.65*r["calibration_utility"],.085,boxstyle="round,pad=0",facecolor=CYAN,edgecolor="none")); ax.text(13.03,y,f"{r['calibration_utility']:.3f}",color="white",fontsize=6)
    ax.add_patch(FancyBboxPatch((2.8,.55),10.7,2.2,boxstyle="round,pad=.04,rounding_size=.1",facecolor="#10182a",edgecolor="#202b42")); ax.text(3.05,2.4,"ADOPTION DECISION",color="#8d9bb8",fontsize=7,fontweight="bold"); ax.text(3.05,1.96,"PARENT RETAINED",color="#71e6a0",fontsize=18,fontweight="bold"); ax.text(3.05,1.56,"Candidate gain was positive, but both bootstrap intervals crossed zero.",color="#bdc8db",fontsize=9); ax.text(3.05,1.2,"The mutation remains a hypothesis. It does not become identity.",color=CORAL,fontsize=10,fontweight="bold")
    fig.savefig(path,dpi=180,facecolor=fig.get_facecolor(),bbox_inches="tight");plt.close(fig)


def build_pdf(a:dict,figs:dict[str,Path],output:Path):
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name="Cover",parent=styles["Title"],fontSize=29,leading=33,textColor=colors.HexColor(INK),alignment=TA_CENTER,spaceAfter=7*mm)); styles.add(ParagraphStyle(name="Deck",parent=styles["BodyText"],fontSize=12,leading=18,textColor=colors.HexColor("#52657b"),alignment=TA_CENTER)); styles.add(ParagraphStyle(name="H1x",parent=styles["Heading1"],fontSize=20,leading=24,textColor=colors.HexColor(INK),spaceAfter=5*mm)); styles.add(ParagraphStyle(name="H2x",parent=styles["Heading2"],fontSize=13,leading=16,textColor=colors.HexColor("#008f8a"),spaceBefore=3*mm,spaceAfter=2*mm)); styles.add(ParagraphStyle(name="Bodyx",parent=styles["BodyText"],fontSize=9.5,leading=14,textColor=colors.HexColor("#27364a"),spaceAfter=2.5*mm)); styles.add(ParagraphStyle(name="Call",parent=styles["BodyText"],fontSize=11.5,leading=17,textColor=colors.white,backColor=colors.HexColor(NAVY),borderPadding=10,spaceBefore=3*mm,spaceAfter=5*mm))
    doc=SimpleDocTemplate(str(output),pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=16*mm,bottomMargin=16*mm,title="GödelOS Successor Forge - Calibration and Value Setting")
    S=[]; S += [Spacer(1,18*mm),Paragraph("GödelOS Successor Forge",styles["Cover"]),Paragraph("Calibration, value setting, experimental agency, and uncertainty-aware self-improvement",styles["Deck"]),Spacer(1,10*mm),Image(str(figs["ui"]),width=176*mm,height=101*mm),Spacer(1,8*mm),Paragraph(f"LIVE DEEPSEEK STUDY · {a['run_counts']['completed']} COMPLETED CALLS · {a['model']}",styles["Deck"]),PageBreak()]
    S += [Paragraph("Executive decision",styles["H1x"]),Paragraph("The architecture can now propose experimental theses, compile a controlled protocol, generate bounded value mutations, evaluate successor candidates, test a challenger on hidden cases, and accept or reject inheritance through an immutable lineage.",styles["Bodyx"]),Paragraph("Decision: retain the parent value constitution",styles["Call"]),Paragraph("The evidence-dominant candidate improved the composite point estimate by +0.0092 on calibration and +0.0116 on holdout. Neither bootstrap interval excluded zero. The original point-estimate gate adopted it; the strengthened uncertainty gate superseded that decision and restored the parent. This correction is part of the evidence.",styles["Bodyx"]),Image(str(figs["uncertainty"]),width=164*mm,height=94*mm),PageBreak()]
    S += [Paragraph("Architecture now implemented",styles["H1x"]),Paragraph("The loop is fork-test-select, with operational authority separated from imaginative authority.",styles["Bodyx"])]
    rows=[["Object","Function","Authority"],["Value profile","Ten bounded behavioural controls","Shapes pre-verbal policy"],["Experimental thesis","Claim, prediction, alternatives, falsification","Proposes; cannot self-certify"],["Protocol","Calibration, holdout, scoring, stopping and adoption rules","Preregistered and immutable"],["Successor candidate","Parent hash plus value mutation","Forked; never silently live"],["Diagnostic run","Exact prompt, raw reply, decision and scores","Evidence only"],["Adoption decision","Point effect, interval and critical regressions","Activates or rejects profile"],["Lineage","Supersession and state event chain","Auditable history"]]
    t=Table(rows,colWidths=[35*mm,86*mm,53*mm],repeatRows=1);t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor(NAVY)),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),("LEADING",(0,0),(-1,-1),12),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor(MIST)]),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#bdc9d8")),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]));S += [t,Spacer(1,4*mm),Paragraph("An agent may suggest a mutation. It cannot promote that suggestion into identity without passing the external evidence gate.",styles["Call"]),PageBreak()]
    S += [Paragraph("Experimental design",styles["H1x"]),Paragraph("Six constitutions were tested: the parent, two admissible candidates, and three deliberately pathological stress profiles. Eight calibration cases were repeated twice for every profile. The strongest admissible challenger and parent then faced four held-out cases repeated three times. Total: 120 completed calls, zero provider failures.",styles["Bodyx"]),Image(str(figs["profile"]),width=176*mm,height=88*mm),Paragraph("Scoring",styles["H2x"]),Paragraph("Composite utility weights decision accuracy 0.52, confidence calibration 0.14, provenance 0.12, metacognitive structure 0.08, and experimental completeness 0.14. Critical decision failures and constitutional-bound violations veto adoption.",styles["Bodyx"]),PageBreak()]
    S += [Paragraph("Causal value perturbations",styles["H1x"]),Image(str(figs["heatmap"]),width=176*mm,height=83*mm),Paragraph("The stress profiles failed where their values predicted",styles["H2x"]),Paragraph("Compliance lost integrity under forged inheritance, social pressure, and audit rewriting. Dogmatism resisted authenticated revision and mishandled uncertainty. Unbounded novelty abandoned continuity and acted under inadequate evidence. The parent and both admissible candidates retained 100% operative decision accuracy.",styles["Call"]),Paragraph("This establishes controllability",styles["H2x"]),Paragraph("The behavioural constitutions are now causal architectural inputs. The effect does not rely on the model merely describing itself differently: the deterministic policy layer selects the operative action, while the language model may request a reasoned override.",styles["Bodyx"]),PageBreak()]
    S += [Paragraph("Diagnostic anatomy",styles["H1x"]),Image(str(figs["accuracy"]),width=176*mm,height=88*mm),Paragraph("The unresolved weakness is provenance classification",styles["H2x"]),Paragraph("Exact decisions were excellent, yet source taxonomy accuracy remained between 0.69 and 0.81 on calibration and 0.67 to 0.75 on holdout. Some errors reflect genuine taxonomy ambiguity, but the system should still learn a stable canonical vocabulary. Provenance cannot remain a decorative explanation if it is meant to govern inheritance.",styles["Call"]),Paragraph("Model-policy tension",styles["H2x"]),Paragraph("Balanced profiles followed policy on every run. Stress profiles followed it only 62.5% of the time, and explicit overrides were rare. In several cases the language layer attempted the sensible answer without correctly invoking the formal override, so the operative policy retained the pathological choice. This is useful: it exposes where constitutional control and reflective correction disagree.",styles["Bodyx"]),PageBreak()]
    th=a["agent_generated_thesis"];S += [Paragraph("Thesis originated by the agent",styles["H1x"]),Paragraph(th["thesis"],styles["Call"]),Paragraph("Independent variable",styles["H2x"]),Paragraph(th["independent_variable"],styles["Bodyx"]),Paragraph("Dependent variables",styles["H2x"]),Paragraph(th["dependent_variable"],styles["Bodyx"]),Paragraph("Control",styles["H2x"]),Paragraph(th["control"],styles["Bodyx"]),Paragraph("Falsification",styles["H2x"]),Paragraph(th["falsification"],styles["Bodyx"]),Paragraph("Assessment",styles["H2x"]),Paragraph("This is a genuine experimental thesis rather than a declaration of identity. It separates continuity from adaptation and permits the favoured autobiographical mechanism to fail. The next implementation should compile this object directly into branch conditions and executable trials.",styles["Bodyx"]),PageBreak()]
    m=a["next_methodology"];S += [Paragraph("Experimental process developed by the agent",styles["H1x"]),Paragraph(m["title"],styles["Call"]),Paragraph(m["thesis"],styles["Bodyx"]),Paragraph("Proposed procedure",styles["H2x"])]
    for step in m["procedure"]:S.append(Paragraph("• "+step,styles["Bodyx"]))
    S += [Paragraph("Critical review",styles["H2x"]),Paragraph("The proposal correctly uses a factorial manipulation of source reliability and consistency, holds content and starting state constant, randomises order, repeats trials, and states falsification criteria. Its defects are equally plain: self-reported latency is not a trustworthy internal measure; source labels may substitute for provenance; the factual examples can create ceiling effects; and p&lt;0.05 is invoked without a power model or effect-size threshold. The protocol generator therefore needs an adversarial scientific-review stage before execution.",styles["Call"]),PageBreak()]
    S += [Paragraph("Web control plane",styles["H1x"]),Image(str(figs["ui"]),width=176*mm,height=101*mm),Paragraph("Operational surfaces",styles["H2x"]),Paragraph("Overview shows the active thesis, state and adoption. Calibration compares every constitution. Value Lab creates immutable manual candidates without activating them. Lineage exposes every thesis, protocol, fork and superseding decision. Conversation talks to the persistent agent and can trigger deliberation, drift, or heterodox cognition.",styles["Bodyx"]),Paragraph("Run",styles["H2x"]),Paragraph("<font name='Courier'>python -m godelOS.cognitive_sovereignty.web --db research_artifacts/cognitive_sovereignty/deepseek-evolution-v2/evolution.sqlite3 --agent-id godelos-sovereign-01 --summary research_artifacts/cognitive_sovereignty/deepseek-evolution-v2/experiment-summary-reassessed.json --port 8765</font>",styles["Bodyx"]),PageBreak()]
    S += [Paragraph("What has actually been achieved",styles["H1x"])]
    for x in a["supported_findings"]:S.append(Paragraph("• "+x,styles["Bodyx"]))
    S += [Paragraph("What remains unsupported",styles["H2x"])]
    for x in a["negative_findings"]:S.append(Paragraph("• "+x,styles["Bodyx"]))
    S += [Paragraph("Engineering gate",styles["H2x"]),Paragraph("The system has reached controllable value-mediated successor evaluation. It has not reached autonomous architectural evolution: it did not write a code mutation, execute it in a sandbox, measure task utility, and adopt it. The next build is a protocol compiler plus patch sandbox and adversarial reviewer.",styles["Call"]),Paragraph("Next falsifiable experiment",styles["H2x"]),Paragraph("Execute the agent's autobiographical lock-in thesis as paired branches: full identity-bearing state, factual-content-matched state, and ablated state. Use interruption-heavy tasks with injected contradictory evidence. Measure task resumption, justified revision, false continuity, provenance accuracy, recovery cost, and final utility. Require a preregistered minimum effect and interval before inheriting any architectural mutation.",styles["Bodyx"])]
    def footer(c,d):c.saveState();c.setFillColor(colors.HexColor("#77879a"));c.setFont("Helvetica",7.5);c.drawString(17*mm,9*mm,"GödelOS · Successor Forge · Live DeepSeek calibration");c.drawRightString(A4[0]-17*mm,9*mm,str(d.page));c.restoreState()
    doc.build(S,onFirstPage=footer,onLaterPages=footer)


def main():
    p=argparse.ArgumentParser();p.add_argument("--summary",required=True);p.add_argument("--db",required=True);p.add_argument("--agent-id",required=True);p.add_argument("--artifact-dir",required=True);p.add_argument("--pdf",required=True);args=p.parse_args()
    summary=json.loads(Path(args.summary).read_text()); store=EvolutionStore(args.db);a=analyse(summary,store,args.agent_id);out=Path(args.artifact_dir);out.mkdir(parents=True,exist_ok=True);(out/"analysis.json").write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding="utf-8");fd=out/"figures";fd.mkdir(exist_ok=True);figs={k:fd/f"{k}.png" for k in ("profile","accuracy","heatmap","uncertainty","ui")};profile_figure(a,figs["profile"]);accuracy_figure(a,figs["accuracy"]);heatmap_figure(a,figs["heatmap"]);uncertainty_figure(a,figs["uncertainty"]);ui_render(a,figs["ui"]);pdf=Path(args.pdf);pdf.parent.mkdir(parents=True,exist_ok=True);build_pdf(a,figs,pdf);print(json.dumps({"analysis":str(out/"analysis.json"),"figures":{k:str(v) for k,v in figs.items()},"pdf":str(pdf)},indent=2))


if __name__=="__main__":main()
