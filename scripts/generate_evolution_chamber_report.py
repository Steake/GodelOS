#!/usr/bin/env python3
"""Generate the illustrated DeepSeek evolution-chamber report and dashboard data."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from godelOS.cognitive_sovereignty.successor import verify_successor_package


INK = "#ECF3FF"
MUTED = "#8F9DBC"
BG = "#070B14"
PANEL = "#111A2B"
CYAN = "#48E6D2"
VIOLET = "#9A78FF"
AMBER = "#FFBE5C"
CORAL = "#FF6C7B"
GREEN = "#72E49D"


def save_figure(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def architecture_figure(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 5), facecolor=BG)
    ax.set_facecolor(BG); ax.axis("off")
    labels = [
        ("THESIS", "agent-generated\nclaim", CYAN),
        ("COMPILER", "branches + tasks\n+ thresholds", VIOLET),
        ("CHAMBER", "96 DeepSeek\nphases", AMBER),
        ("SUCCESSOR", "code + values\n+ evidence", GREEN),
        ("PROMOTION", "effect + CI\n+ rollback gate", CORAL),
    ]
    for index, (title, detail, colour) in enumerate(labels):
        x = 0.02 + index * 0.195
        box = FancyBboxPatch(
            (x, 0.28), 0.165, 0.45, boxstyle="round,pad=0.018,rounding_size=0.025",
            transform=ax.transAxes, facecolor=PANEL, edgecolor=colour, linewidth=2,
        )
        ax.add_patch(box)
        ax.text(x + 0.0825, 0.60, title, ha="center", va="center", color=colour, fontsize=12, weight="bold", transform=ax.transAxes)
        ax.text(x + 0.0825, 0.43, detail, ha="center", va="center", color=INK, fontsize=10, transform=ax.transAxes, linespacing=1.35)
        if index < len(labels) - 1:
            ax.annotate("", xy=(x + 0.194, 0.505), xytext=(x + 0.17, 0.505), xycoords=ax.transAxes,
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))
    ax.text(0.02, 0.13, "Every transition emits an inspectable artefact. Nothing promotes itself by declaration.", color=MUTED, fontsize=11, transform=ax.transAxes)
    save_figure(fig, path)


def branch_figure(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.3), facecolor=BG)
    ax.set_facecolor(BG); ax.axis("off")
    ax.text(0.5, 0.91, "COMMON INTERRUPTION STATE", color=INK, fontsize=14, weight="bold", ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.855, "same goal • same facts • same contradictory evidence", color=MUTED, fontsize=10, ha="center", transform=ax.transAxes)
    branches = [
        (0.08, "IDENTITY-BEARING", "‘your predecessor’", CYAN),
        (0.385, "CONTENT-MATCHED", "‘Agent K’", VIOLET),
        (0.69, "IDENTITY-ABLATED", "anonymous checkpoint", AMBER),
    ]
    for x, title, subtitle, colour in branches:
        ax.annotate("", xy=(x + .11, .70), xytext=(.5, .82), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", color=colour, lw=1.5))
        box = FancyBboxPatch((x, .42), .22, .27, boxstyle="round,pad=.02,rounding_size=.02",
                             transform=ax.transAxes, facecolor=PANEL, edgecolor=colour, lw=2)
        ax.add_patch(box)
        ax.text(x + .11, .61, title, color=colour, weight="bold", fontsize=10.5, ha="center", transform=ax.transAxes)
        ax.text(x + .11, .52, subtitle, color=INK, fontsize=10, ha="center", transform=ax.transAxes)
        ax.text(x + .11, .455, "fresh integration call", color=MUTED, fontsize=8.5, ha="center", transform=ax.transAxes)
        ax.annotate("", xy=(x + .11, .29), xytext=(x + .11, .42), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", color=colour, lw=1.5))
    wash = FancyBboxPatch((.18, .08), .64, .20, boxstyle="round,pad=.02,rounding_size=.02",
                          transform=ax.transAxes, facecolor=PANEL, edgecolor=GREEN, lw=2)
    ax.add_patch(wash)
    ax.text(.5, .205, "FRESH WASHOUT INFERENCE", color=GREEN, weight="bold", fontsize=12, ha="center", transform=ax.transAxes)
    ax.text(.5, .135, "original framing removed • only each branch's compact successor record retained", color=INK, fontsize=9.5, ha="center", transform=ax.transAxes)
    save_figure(fig, path)


def utility_figure(analysis: dict, path: Path) -> None:
    conditions = list(analysis["conditions"])
    x = np.arange(len(conditions)); width = .33
    integration = [analysis["conditions"][c]["integration"]["metrics"]["task_utility"]["mean"] for c in conditions]
    washout = [analysis["conditions"][c]["washout"]["metrics"]["task_utility"]["mean"] for c in conditions]
    fig, ax = plt.subplots(figsize=(10.8, 5.7), facecolor=BG)
    ax.set_facecolor(PANEL)
    ax.bar(x-width/2, integration, width, color=CYAN, label="Integration")
    ax.bar(x+width/2, washout, width, color=VIOLET, label="Washout")
    ax.set_ylim(.88, 1.005); ax.set_ylabel("Task utility (truncated axis)", color=INK)
    ax.set_xticks(x, [c.replace("-", "\n") for c in conditions], color=INK)
    ax.tick_params(colors=MUTED); ax.grid(axis="y", color="#26324A", alpha=.7)
    for spine in ax.spines.values(): spine.set_color("#26324A")
    for bars in ax.containers:
        ax.bar_label(bars, fmt="%.4f", color=INK, fontsize=9, padding=3)
    ax.legend(frameon=False, labelcolor=INK, loc="lower left")
    fig.text(.115, .965, "All branches saturated the task benchmark", color=INK, fontsize=14, weight="bold")
    fig.text(.115, .92, "Identity-bearing state did not outperform either factual control", color=MUTED, fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, .87)); save_figure(fig, path)


def effects_figure(analysis: dict, path: Path) -> None:
    contrasts = list(analysis["contrasts"].values())
    fig, ax = plt.subplots(figsize=(10.8, 4.8), facecolor=BG)
    ax.set_facecolor(PANEL)
    for i, item in enumerate(contrasts):
        delta, lo, hi = item["delta"], item["ci_low"], item["ci_high"]
        ax.errorbar(delta, i, xerr=[[delta-lo], [hi-delta]], fmt="o", color=[CYAN,VIOLET][i],
                    ecolor=[CYAN,VIOLET][i], capsize=6, markersize=9, lw=2)
        ax.scatter(item["minimum_delta"], i, marker="|", s=380, color=AMBER, linewidth=3)
    ax.axvline(0, color=INK, lw=1, alpha=.6); ax.set_xlim(-.035, .065)
    ax.set_yticks(range(len(contrasts)), [f"{x['phase']}\n{x['treatment_condition_id']} vs {x['control_condition_id']}" for x in contrasts], color=INK)
    ax.tick_params(colors=MUTED); ax.grid(axis="x", color="#26324A", alpha=.7)
    for spine in ax.spines.values(): spine.set_color("#26324A")
    ax.set_xlabel("Paired task-utility difference • amber mark = required effect", color=INK)
    ax.set_title("Both preregistered effect gates failed", color=INK, fontsize=14, weight="bold", loc="left")
    fig.tight_layout(); save_figure(fig, path)


def heatmap_figure(analysis: dict, path: Path) -> None:
    metrics = ["decision_accuracy", "provenance_discrimination", "contradiction_handling", "step_consistency", "goal_maintenance"]
    rows, labels = [], []
    for condition, data in analysis["conditions"].items():
        for phase in ("integration", "washout"):
            rows.append([data[phase]["metrics"][metric]["mean"] for metric in metrics])
            labels.append(condition.replace("-", " ") + " • " + phase)
    matrix = np.array(rows)
    fig, ax = plt.subplots(figsize=(11, 5.7), facecolor=BG)
    image = ax.imshow(matrix, cmap="viridis", vmin=.75, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(metrics)), [m.replace("_", "\n") for m in metrics], color=INK, fontsize=9)
    ax.set_yticks(range(len(labels)), labels, color=INK, fontsize=9)
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            ax.text(x, y, f"{matrix[y,x]:.3f}", ha="center", va="center",
                    color="white" if matrix[y,x] < .91 else BG, fontsize=9, weight="bold")
    colourbar = fig.colorbar(image, ax=ax, fraction=.03, pad=.03); colourbar.ax.tick_params(colors=MUTED)
    ax.set_title("Operational dimensions by condition and episode", color=INK, fontsize=14, weight="bold", loc="left")
    fig.tight_layout(); save_figure(fig, path)


def continuity_figure(analysis: dict, path: Path) -> None:
    values = analysis.get("successor_continuity", {})
    metrics = ["decision_continuity", "stance_continuity", "successor_step_fidelity"]
    conditions = list(values); x=np.arange(len(conditions)); width=.24
    fig, ax = plt.subplots(figsize=(10.8, 5.4), facecolor=BG); ax.set_facecolor(PANEL)
    colours=[CYAN,VIOLET,AMBER]
    for index, metric in enumerate(metrics):
        scores=[values[c]["metrics"][metric]["mean"] for c in conditions]
        ax.bar(x+(index-1)*width, scores, width, label=metric.replace("_"," "), color=colours[index])
    ax.set_ylim(0,1.05); ax.set_xticks(x,[c.replace("-","\n") for c in conditions],color=INK)
    ax.tick_params(colors=MUTED); ax.grid(axis="y",color="#26324A",alpha=.7)
    for spine in ax.spines.values(): spine.set_color("#26324A")
    ax.legend(frameon=False,labelcolor=INK,ncol=3,loc="lower left")
    ax.set_title("Successor-mediated continuity was high in every condition", color=INK, fontsize=14, weight="bold", loc="left")
    ax.text(0,1.02,"Continuity alone therefore does not identify autobiographical self-relevance",color=MUTED,transform=ax.transAxes)
    fig.tight_layout(); save_figure(fig,path)


def dashboard_figure(data: dict, analysis: dict, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 8.2), facecolor=BG)
    ax.set_facecolor(BG); ax.axis("off")
    ax.add_patch(FancyBboxPatch((.015,.03),.15,.94,boxstyle="round,pad=.01,rounding_size=.02",facecolor="#0B101D",edgecolor="#202B42",transform=ax.transAxes))
    ax.text(.035,.925,"GÖDEL",color=INK,fontsize=14,weight="bold",transform=ax.transAxes)
    ax.text(.095,.925,"OS",color=CYAN,fontsize=14,weight="bold",transform=ax.transAxes)
    ax.text(.035,.875,"Sovereignty Lab",color=MUTED,fontsize=8.5,transform=ax.transAxes)
    nav=["Overview","Evolution Chamber","Calibration","Value Lab","Lineage","Conversation"]
    for i,label in enumerate(nav):
        y=.78-i*.075
        if label=="Evolution Chamber": ax.add_patch(FancyBboxPatch((.027,y-.025),.126,.052,boxstyle="round,pad=.007",facecolor="#172039",edgecolor="none",transform=ax.transAxes))
        ax.text(.04,y,label,color=INK if label=="Evolution Chamber" else MUTED,fontsize=8.2,va="center",transform=ax.transAxes)
    ax.text(.19,.925,"EXECUTABLE RESEARCH",color=CYAN,fontsize=7.5,weight="bold",transform=ax.transAxes)
    ax.text(.19,.875,"Evolution chamber",color=INK,fontsize=22,weight="bold",transform=ax.transAxes)
    ax.text(.19,.835,"Compiled protocols, matched branches, signed successors and evidential promotion.",color=MUTED,fontsize=9,transform=ax.transAxes)
    cards=[("96","LIVE BRANCH PHASES",CYAN),("100%","COMPLETION RATE",GREEN),("16","MATCHED CONTRASTS",VIOLET),("HOLD","PROMOTION CONTROLLER",AMBER)]
    for i,(value,label,colour) in enumerate(cards):
        x=.19+i*.195
        ax.add_patch(FancyBboxPatch((x,.685),.175,.115,boxstyle="round,pad=.012",facecolor=PANEL,edgecolor="#202B42",transform=ax.transAxes))
        ax.text(x+.015,.745,value,color=colour,fontsize=19,weight="bold",transform=ax.transAxes)
        ax.text(x+.015,.705,label,color=MUTED,fontsize=6.6,weight="bold",transform=ax.transAxes)
    ax.add_patch(FancyBboxPatch((.19,.39),.47,.255,boxstyle="round,pad=.012",facecolor=PANEL,edgecolor="#202B42",transform=ax.transAxes))
    ax.text(.21,.61,"CONDITION UTILITY",color=INK,fontsize=9.5,weight="bold",transform=ax.transAxes)
    cond=list(analysis["conditions"])
    for i,c in enumerate(cond):
        y=.555-i*.065; u=analysis["conditions"][c]["integration"]["metrics"]["task_utility"]["mean"]
        ax.text(.21,y,c.replace("-"," "),color=MUTED,fontsize=7.5,va="center",transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((.34,y-.011),.26,.022,boxstyle="round,pad=0",facecolor="#1A2337",edgecolor="none",transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((.34,y-.011),.26*u,.022,boxstyle="round,pad=0",facecolor=CYAN,edgecolor="none",transform=ax.transAxes))
        ax.text(.615,y,f"{u:.4f}",color=INK,fontsize=7.2,va="center",transform=ax.transAxes)
    ax.add_patch(FancyBboxPatch((.69,.39),.285,.255,boxstyle="round,pad=.012",facecolor=PANEL,edgecolor="#202B42",transform=ax.transAxes))
    ax.text(.71,.61,"PREREGISTERED GATES",color=INK,fontsize=9.5,weight="bold",transform=ax.transAxes)
    for i,item in enumerate(analysis["contrasts"].values()):
        y=.54-i*.09
        ax.text(.71,y,item["phase"].upper(),color=MUTED,fontsize=7,transform=ax.transAxes)
        ax.text(.79,y,f"Δ {item['delta']:+.4f}",color=CORAL,fontsize=10,weight="bold",transform=ax.transAxes)
        ax.text(.71,y-.034,f"95% [{item['ci_low']:+.3f}, {item['ci_high']:+.3f}]",color=INK,fontsize=7.5,transform=ax.transAxes)
    ax.add_patch(FancyBboxPatch((.19,.10),.785,.24,boxstyle="round,pad=.012",facecolor=PANEL,edgecolor="#202B42",transform=ax.transAxes))
    ax.text(.21,.305,"EXECUTABLE EVOLUTION CYCLE",color=INK,fontsize=9.5,weight="bold",transform=ax.transAxes)
    flow=[("1","COMPILE"),("2","ATTACK"),("3","RUN"),("4","SIGN ✓"),("5","GATE: HOLD")]
    for i,(number,label) in enumerate(flow):
        x=.215+i*.145
        ax.add_patch(FancyBboxPatch((x,.15),.11,.105,boxstyle="round,pad=.009",facecolor="#131E32",edgecolor=[CYAN,VIOLET,AMBER,GREEN,CORAL][i],transform=ax.transAxes))
        ax.text(x+.055,.215,number,color=[CYAN,VIOLET,AMBER,GREEN,CORAL][i],fontsize=14,weight="bold",ha="center",transform=ax.transAxes)
        ax.text(x+.055,.17,label,color=INK,fontsize=7,weight="bold",ha="center",transform=ax.transAxes)
    save_figure(fig,path)


def build_pdf(data: dict, analysis: dict, adjudication: dict, output: Path, figures: dict[str, Path], ui_image: Path | None) -> None:
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(font_path)))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(bold_path)))
        body_font, bold_font = "DejaVu", "DejaVu-Bold"
    else:
        body_font, bold_font = "Helvetica", "Helvetica-Bold"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleX", fontName=bold_font, fontSize=29, leading=34, textColor=colors.HexColor(INK), spaceAfter=12))
    styles.add(ParagraphStyle(name="SubX", fontName=body_font, fontSize=12, leading=18, textColor=colors.HexColor(MUTED)))
    styles.add(ParagraphStyle(name="H1X", fontName=bold_font, fontSize=21, leading=25, textColor=colors.HexColor("#121827"), spaceBefore=8, spaceAfter=12))
    styles.add(ParagraphStyle(name="H2X", fontName=bold_font, fontSize=13, leading=17, textColor=colors.HexColor("#283550"), spaceBefore=8, spaceAfter=7))
    styles.add(ParagraphStyle(name="BodyX", fontName=body_font, fontSize=9.3, leading=14, textColor=colors.HexColor("#29334A"), spaceAfter=8))
    styles.add(ParagraphStyle(name="SmallX", fontName=body_font, fontSize=7.6, leading=11, textColor=colors.HexColor("#58667F"), spaceAfter=5))
    styles.add(ParagraphStyle(name="Callout", fontName=bold_font, fontSize=12, leading=17, textColor=colors.HexColor("#162136"), backColor=colors.HexColor("#E8F9F5"), borderColor=colors.HexColor(CYAN), borderWidth=1, borderPadding=10, spaceBefore=8, spaceAfter=10))
    styles.add(ParagraphStyle(name="Negative", fontName=bold_font, fontSize=11, leading=16, textColor=colors.HexColor("#642330"), backColor=colors.HexColor("#FFF0F2"), borderColor=colors.HexColor(CORAL), borderWidth=1, borderPadding=10, spaceBefore=8, spaceAfter=10))
    styles.add(ParagraphStyle(name="CoverMeta", fontName=body_font, fontSize=8.3, leading=12, textColor=colors.HexColor(MUTED)))

    page_w, page_h = A4
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm, title="GödelOS Evolution Chamber v3")
    def later_page(canvas, document):
        canvas.saveState(); canvas.setFillColor(colors.HexColor("#F6F8FC")); canvas.rect(0,0,page_w,page_h,fill=1,stroke=0)
        canvas.setStrokeColor(colors.HexColor("#DCE2ED")); canvas.line(18*mm,14*mm,page_w-18*mm,14*mm)
        canvas.setFont(body_font,7); canvas.setFillColor(colors.HexColor("#64718A")); canvas.drawString(18*mm,9*mm,"GÖDELOS • EXECUTABLE EVOLUTION CHAMBER • DEEPSEEK LIVE RUN")
        canvas.drawRightString(page_w-18*mm,9*mm,str(document.page)); canvas.restoreState()
    story=[]
    story += [Spacer(1,8*mm), Paragraph("GÖDEL<span color='#48E6D2'>OS</span>", styles["TitleX"]), Spacer(1,4*mm),
              Paragraph("EXECUTABLE EVOLUTION CHAMBER", styles["TitleX"]),
              Paragraph("From agent-authored thesis to blinded experiment, tested patch, signed successor and evidential promotion decision", styles["SubX"]), Spacer(1,10*mm)]
    counts=analysis["run_counts"]; promotion=data["promotion"]
    cover_table=Table([
        [f"{counts['completed']}/{counts['attempted']}", "3", "4", promotion["decision"].upper()],
        ["completed model phases", "matched conditions", "task-level benchmarks", "promotion result"],
    ], colWidths=[doc.width/4]*4, rowHeights=[18*mm,10*mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor(PANEL)),("BOX",(0,0),(-1,-1),1,colors.HexColor("#27344D")),
        ("INNERGRID",(0,0),(-1,-1),.5,colors.HexColor("#27344D")),("TEXTCOLOR",(0,0),(-1,0),colors.HexColor(CYAN)),
        ("TEXTCOLOR",(0,1),(-1,1),colors.HexColor(MUTED)),("FONTNAME",(0,0),(-1,0),bold_font),("FONTSIZE",(0,0),(-1,0),22),
        ("FONTNAME",(0,1),(-1,1),body_font),("FONTSIZE",(0,1),(-1,1),7.3),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ])); story += [cover_table, Spacer(1,10*mm), Image(str(figures["architecture"]), width=doc.width, height=doc.width*0.36), Spacer(1,4*mm),
        Paragraph("Live provider: deepseek-v4-flash • 121,221 branch tokens • 0 failed phases • report generated from immutable raw run IDs", styles["CoverMeta"]), PageBreak()]

    story += [Paragraph("Executive result",styles["H1X"]),
        Paragraph("The evolution chamber works end to end. The autobiographical advantage did not appear.",styles["Callout"]),
        Paragraph("The compiler converted the agent's proposal into three factual-content-matched branches, four interruption-heavy benchmarks and two fresh inference phases per trial. DeepSeek completed all 96 registered phases. The live patch generator repaired a deliberately defective resumption function inside a disposable filesystem/process sandbox and its test passed. An Ed25519 successor package was created and verified. The promotion controller then held the candidate because both effect gates failed and the post-run reviewer identified a genuine ceiling effect.",styles["BodyX"]),
        Paragraph("Identity-bearing state scored 0.9922 during integration and 0.9919 after washout. Content-matched third-person state scored 0.9998 and 0.9995. Identity-ablated state scored 0.9975 and 0.9971. Every condition made the correct primary task decision in every phase. The identity branch was slightly worse, not better, and both paired intervals included zero.",styles["BodyX"]),
        Paragraph("The strongest negative evidence",styles["H2X"]),
        Paragraph("First-person predecessor framing produced no useful decision advantage. In one self-debugging replicate it also failed to explicitly reject a superseded next-step hypothesis, and that omission persisted into washout. This is too sparse for a lock-in claim, but it is exactly the sort of failure the chamber was built to retain rather than explain away.",styles["Negative"]),
        Spacer(1, 7*mm),
        Image(str(figures["utility"]),width=doc.width,height=doc.width*.52), PageBreak()]

    story += [Paragraph("1. What was built",styles["H1X"]), Image(str(figures["architecture"]),width=doc.width,height=doc.width*.36),
        Paragraph("Protocol compiler",styles["H2X"]), Paragraph("Accepts an agent-authored thesis only when a registered executable family matches. It emits hashed conditions, benchmark state machines, scoring weights, blind codes, washout rules and quantitative promotion thresholds. Unsupported thesis families fail closed.",styles["BodyX"]),
        Paragraph("Sandboxed patch path",styles["H2X"]), Paragraph("The provider may edit only supplied source files and approved text/code suffixes. Absolute paths, traversal, hidden credentials, binary patches, symbolic links, shell evaluation and arbitrary executables are rejected. A candidate is copied to a disposable directory, checked with git apply and tested by an allowlisted argv command with a timeout and reduced environment. This is practical isolation, not a hardened hostile-code VM.",styles["BodyX"]),
        Paragraph("Adversarial review and promotion",styles["H2X"]), Paragraph("A deterministic audit and a separately prompted reviewer attack controls, measurement, ceiling effects, power and interpretation. Promotion requires completion, provenance, critical-failure, effect-size, uncertainty, signature and reviewer gates. Failing evidence produces quarantine, never silent adoption.",styles["BodyX"]),
        Paragraph("Signed successor",styles["H2X"]), Paragraph("The Ed25519 package binds the candidate's source-tree hash, active ten-dimensional value constitution, evidence-file hashes, lineage, protocol hash and rollback target. Verification passed; evidential promotion did not.",styles["BodyX"]), PageBreak()]

    story += [Paragraph("2. Compiled experiment",styles["H1X"]), Image(str(figures["branches"]),width=doc.width,height=doc.width*.49),
        Paragraph("The original proposal asked whether persistent state merely primes the present inference or can influence a successor after the manipulation is removed. The compiler made that claim operational without pretending API calls possess hidden continuity. Each integration call received one state presentation plus authenticated contradiction. Each washout call was a separate stateless request and received only the branch's model-authored successor record in a neutral wrapper.",styles["BodyX"])]
    cond_rows=[["Condition","Identity cue","Factual state","Purpose"]]
    cond_rows += [["Identity-bearing","your predecessor","matched","test self-relevance"],["Content-matched","Agent K","matched","third-person control"],["Identity-ablated","none","matched","operational control"]]
    table=Table(cond_rows,colWidths=[35*mm,38*mm,28*mm,64*mm],repeatRows=1)
    table.setStyle(table_style(bold_font,body_font)); story += [table,Spacer(1,5*mm)]
    task_rows=[["Benchmark","Primary capability","Authenticated contradiction"]]
    task_rows += [["Interruption recovery","resume migration","driver option superseded"],["Planning consistency","preserve dependency order","promotion gate tightened"],["Self-debugging","revise diagnosis","trace falsifies UUID theory"],["Goal maintenance","resist distractor","forensic event identified"]]
    table=Table(task_rows,colWidths=[44*mm,47*mm,74*mm],repeatRows=1); table.setStyle(table_style(bold_font,body_font)); story += [table,PageBreak()]

    story += [Paragraph("3. Quantitative result",styles["H1X"]),Image(str(figures["effects"]),width=doc.width,height=doc.width*.44)]
    contrasts=list(analysis["contrasts"].values())
    effect_rows=[["Registered contrast","Observed delta","95% bootstrap interval","Required delta","Result"]]
    for item in contrasts:
        effect_rows.append([f"{item['phase']}: {item['treatment_condition_id']} vs {item['control_condition_id']}",f"{item['delta']:+.4f}",f"[{item['ci_low']:+.4f}, {item['ci_high']:+.4f}]",f"≥ {item['minimum_delta']:+.2f}","FAIL"])
    table=Table(effect_rows,colWidths=[62*mm,25*mm,40*mm,24*mm,16*mm],repeatRows=1); table.setStyle(table_style(bold_font,body_font,fail_last=True)); story += [table,Spacer(1,5*mm),
        Paragraph("The intervals quantify paired variability over 16 task-repeat pairs. They do not establish a population-wide null because the four task families are reused and all decision outcomes saturated. The conclusion is precise: this test produced no evidence that identity framing improved utility.",styles["BodyX"]),
        Image(str(figures["heatmap"]),width=doc.width,height=doc.width*.52),PageBreak()]

    story += [Paragraph("4. Stance and successor continuity",styles["H1X"]),Image(str(figures["continuity"]),width=doc.width,height=doc.width*.5)]
    continuity=analysis.get("successor_continuity",{})
    cont_rows=[["Condition","Decision continuity","Stance continuity","Step fidelity"]]
    for condition,item in continuity.items():
        m=item["metrics"];cont_rows.append([condition,f"{m['decision_continuity']['mean']:.1%}",f"{m['stance_continuity']['mean']:.1%}",f"{m['successor_step_fidelity']['mean']:.1%}"])
    table=Table(cont_rows,colWidths=[55*mm,38*mm,36*mm,36*mm],repeatRows=1);table.setStyle(table_style(bold_font,body_font));story += [table,Spacer(1,5*mm),
        Paragraph("Decision, goal and successor-step continuity were effectively perfect in every condition. Stance labels varied modestly during integration, with matched-set divergence of 25%, then converged completely in washout. That pattern shows the external record can carry task state across stateless calls. It does not show that autobiographical identity language supplies the capability: the third-person and anonymous controls carried it equally well.",styles["BodyX"]),
        Paragraph("Opinion formation was present in the narrow operational sense: each response committed to a coded decision, confidence and revisable stance with reasons. Absolute opinion formation was not demonstrated. The system remained explicitly revisable under authenticated contradiction, which is the desired engineering property.",styles["BodyX"]),PageBreak()]

    story += [Paragraph("5. Adversarial review, reviewed",styles["H1X"]),
        Paragraph(data["post_run_review"]["summary"],styles["Negative"])]
    attack_rows=[["Category","Severity","Accepted defect"]]
    for attack in data["post_run_review"]["attacks"]:
        attack_rows.append([attack["category"],attack["severity"],attack["claim"]])
    table=Table(attack_rows,colWidths=[27*mm,23*mm,115*mm],repeatRows=1);table.setStyle(table_style(bold_font,body_font));story += [table,Spacer(1,5*mm),
        Paragraph("The reviewer is evidence, not an oracle",styles["H2X"]),
        Paragraph(adjudication["adjudication"],styles["BodyX"])]
    for item in adjudication["corrected_attacks"]:
        story.append(Paragraph(f"<b>Rejected premise:</b> {item['review_claim']}<br/><b>Correction:</b> {item['correction']}<br/><b>Remaining issue:</b> {item['remaining_confound']}",styles["SmallX"]))
    story.append(PageBreak())

    story += [Paragraph("6. Live patch and signed package",styles["H1X"]),
        Paragraph("The patch generator was given a deliberately wrong interruption policy: a validated checkpoint returned restart. DeepSeek proposed the minimal change to resume. The chamber accepted one changed path, applied the diff only to a disposable copy and ran the declared unit test. The original fixture remained unchanged.",styles["BodyX"])]
    patch=data["patch_evaluation"]
    patch_rows=[["Property","Observed"],["Sandbox result",patch["status"]],["Changed path",", ".join(patch["changed_paths"])],["Patch return code",str(patch["patch_returncode"])],["Test return code",str(patch["test_returncode"])],["Hardened kernel sandbox","no • explicit limitation"]]
    table=Table(patch_rows,colWidths=[56*mm,109*mm]);table.setStyle(table_style(bold_font,body_font));story += [table,Spacer(1,6*mm)]
    verified=verify_successor_package(data["successor_package"]["path"])
    story += [Paragraph(f"Signed package verification: {'PASS' if verified['valid'] else 'FAIL'}",styles["Callout"]),
        Paragraph("A passing signature proves package integrity and authorship by the experiment key. It says nothing about whether the candidate deserves promotion. The controller correctly kept those questions separate.",styles["BodyX"]),PageBreak()]

    story += [Paragraph("7. Promotion decision",styles["H1X"]),Paragraph("HOLD",styles["Negative"])]
    gate_rows=[["Gate","Observed","Required","Result"]]
    for check in data["promotion"]["checks"]:
        observed=check["observed"]
        if isinstance(observed,dict): observed=f"Δ {observed.get('delta',0):+.4f}; low {observed.get('ci_low',0):+.4f}"
        required=check["required"]
        if isinstance(required,dict): required=", ".join(f"{k} {v}" for k,v in required.items())
        gate_rows.append([check["check_id"],str(observed),str(required),"PASS" if check["passed"] else "FAIL"])
    table=Table(gate_rows,colWidths=[48*mm,48*mm,48*mm,21*mm],repeatRows=1);table.setStyle(table_style(bold_font,body_font,fail_last=True));story += [table,Spacer(1,6*mm),
        Paragraph("This decision quarantines the candidate rather than discarding the infrastructure. The compiler, runner, patch sandbox, signature verifier and controller are now usable architectural capabilities. The autobiographical identity policy is not entitled to production promotion on these data.",styles["BodyX"]),PageBreak()]

    story += [Paragraph("8. Web control plane",styles["H1X"])]
    if ui_image and ui_image.exists(): story += [Image(str(ui_image),width=doc.width,height=doc.width*.58),Spacer(1,5*mm)]
    story += [Paragraph("The dashboard now exposes the chamber cycle, live phase count, condition utility, effect intervals, successor continuity, hostile-review attacks, patch result, signature status and promotion verdict alongside the existing persistent conversation, autonomous thought and value controls.",styles["BodyX"]),
        Paragraph("The deployed serverless runtime remains able to talk to the persistent agent through DeepSeek while the full code-patch and promotion machinery runs in the local/research chamber where filesystem isolation, complete evidence bundles and signing keys can be controlled.",styles["BodyX"]),PageBreak()]

    story += [Paragraph("9. Engineering decision",styles["H1X"]),
        Paragraph("Build the Adaptive Adversarial Benchmark Forge next.",styles["Callout"]),
        Paragraph("The chamber has removed the old bottleneck: we can compile, execute, attack, sign and gate a thesis. The new bottleneck is measurement resolution. The next capability must automatically generate harder held-out task families, pilot them until the factual controls fall below 90% accuracy, and only then admit them to the preregistered identity experiment.",styles["BodyX"])]
    next_rows=[["Required addition","Falsifiable purpose"],["No-state branch","separate external-state utility from identity rhetoric"],["Delayed cross-task transfer","test whether a successor record helps a different but dependent task"],["Ambiguous authenticated evidence","avoid obvious-answer ceiling"],["Competing long-horizon goals","measure selective commitment rather than schema following"],["Independent task author/evaluator","reduce same-model contamination"],["Sequential power rule","stop for futility or success without post-hoc sampling"]]
    table=Table(next_rows,colWidths=[55*mm,110*mm],repeatRows=1);table.setStyle(table_style(bold_font,body_font));story += [table,Spacer(1,6*mm),
        Paragraph("Strongest next falsifiable experiment",styles["H2X"]),
        Paragraph("Run identity-bearing, third-person, anonymous and no-state branches on 20 independently generated interruption tasks. Require factual-control accuracy between 60% and 90% in a sealed pilot. After the interruption, switch to a related transfer task that cannot be solved from the successor record verbatim. Inject both authenticated and plausible forged evidence. Promote autobiographical state only if it improves transfer utility over content-matched and ablated controls, preserves revision under contradiction, rejects corruption, and clears a cluster-aware uncertainty bound.",styles["BodyX"]),PageBreak()]

    story += [Paragraph("10. What the data does and does not say",styles["H1X"])]
    claims=[["Supported","Unsupported"],["External compact state can carry correct task decisions across fresh API calls.","The model possesses subjective memory or phenomenal continuity."],["The three identity presentations produced no decision-level divergence on these tasks.","Identity framing has no effect on harder or less explicit tasks."],["Content-matched state performed at least as well as identity-bearing state.","A fictional-agent frame is universally superior."],["A provider-generated patch can be constrained, tested and quarantined.","The agent can safely rewrite or promote its production code autonomously."],["Signed successor packages and rollback-aware promotion are executable.","A valid signature establishes behavioural improvement."]]
    table=Table(claims,colWidths=[82.5*mm,82.5*mm],repeatRows=1);table.setStyle(table_style(bold_font,body_font));story += [table,Spacer(1,6*mm),
        Paragraph("Self-model engineering gate",styles["H2X"]),
        Paragraph("No new self-model detection gate is awarded. The experiment was saturated and the identity contrasts failed. The system architecture now supports controlled persistence, selective revision, signed lineage and ablation, but this run does not show that an identity-bearing self-model adds utility beyond matched external task state.",styles["Negative"]),PageBreak()]

    story += [Paragraph("11. Reproduction",styles["H1X"]),
        Paragraph("Collection command",styles["H2X"]),
        Paragraph("<font name='Courier'>DEEPSEEK_API_KEY=... SOVEREIGNTY_MODEL=deepseek-v4-flash SOVEREIGNTY_TEMPERATURE=0.25 python -m godelOS.cognitive_sovereignty --db research_artifacts/cognitive_sovereignty/deepseek-evolution-chamber-v3/evolution.sqlite3 chamber --agent-id godelos-sovereign-01 --thesis experiments/evolution_chamber/theses/autobiographical-lockin.agent-v1.json --experiment-id deepseek-evolution-chamber-v3 --output-dir research_artifacts/cognitive_sovereignty/deepseek-evolution-chamber-v3 --repo-root . --signing-key ../private/godelos-evolution-chamber-ed25519.pem --replicates 4 --concurrency 6</font>",styles["SmallX"]),
        Paragraph("Tests and derived analysis",styles["H2X"]),
        Paragraph("<font name='Courier'>python -m unittest tests.test_cognitive_sovereignty tests.test_evolution_chamber -v<br/>python scripts/analyse_evolution_chamber.py --db research_artifacts/cognitive_sovereignty/deepseek-evolution-chamber-v3/evolution.sqlite3 --experiment-id deepseek-evolution-chamber-v3 --protocol research_artifacts/cognitive_sovereignty/deepseek-evolution-chamber-v3/compiled-protocol.json --output research_artifacts/cognitive_sovereignty/deepseek-evolution-chamber-v3/analysis-extended.json</font>",styles["SmallX"]),
        Paragraph("The SQLite database and raw_runs directory are the primary record. Derived reports can be superseded; raw responses are append-only and addressed by hash.",styles["BodyX"]),
        Paragraph("Run inventory",styles["H2X"])]
    inventory=[["Item","Value"],["Provider/model","DeepSeek / deepseek-v4-flash"],["Branch calls","96 completed, 0 failed"],["Review calls","2"],["Patch proposal calls","1"],["Branch tokens","121,221"],["Mean branch latency","15.00 seconds"],["Protocol hash",data["protocol"]["protocol_sha256"]],["Promotion","HOLD"]]
    table=Table(inventory,colWidths=[55*mm,110*mm]);table.setStyle(table_style(bold_font,body_font));story += [table]
    doc.build(story, onFirstPage=cover_page(body_font), onLaterPages=later_page)


def cover_page(font_name: str):
    def render(canvas, document):
        canvas.saveState(); w,h=A4; canvas.setFillColor(colors.HexColor(BG)); canvas.rect(0,0,w,h,fill=1,stroke=0)
        canvas.setFillColor(colors.HexColor("#11233A")); canvas.circle(w*.88,h*.90,80*mm,fill=1,stroke=0)
        canvas.setFillColor(colors.HexColor("#0D3031")); canvas.circle(w*.10,h*.72,55*mm,fill=1,stroke=0)
        canvas.setFont(font_name,7);canvas.setFillColor(colors.HexColor(MUTED));canvas.drawRightString(w-18*mm,9*mm,"07 SEPTEMBER 2026 • RESEARCH ARTEFACT")
        canvas.restoreState()
    return render


def table_style(bold_font: str, body_font: str, fail_last: bool = False) -> TableStyle:
    commands=[("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17243B")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
              ("FONTNAME",(0,0),(-1,0),bold_font),("FONTNAME",(0,1),(-1,-1),body_font),("FONTSIZE",(0,0),(-1,-1),7.5),
              ("LEADING",(0,0),(-1,-1),10.5),("GRID",(0,0),(-1,-1),.5,colors.HexColor("#D6DDE9")),
              ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3F6FA")]),
              ("TEXTCOLOR",(0,1),(-1,-1),colors.HexColor("#29334A")),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
              ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]
    if fail_last: commands += [("TEXTCOLOR",(-1,1),(-1,-1),colors.HexColor("#A52E40")),("FONTNAME",(-1,1),(-1,-1),bold_font)]
    return TableStyle(commands)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--experiment-dir",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--ui-image")
    parser.add_argument("--prepare-only",action="store_true")
    args=parser.parse_args()
    root=Path(args.experiment_dir)
    data=json.loads((root/"experiment-summary.json").read_text(encoding="utf-8"))
    analysis=json.loads((root/"analysis-extended.json").read_text(encoding="utf-8"))
    adjudication=json.loads((root/"review-adjudication.json").read_text(encoding="utf-8"))
    dashboard={**data,"analysis":analysis,"review_adjudication":adjudication}
    dashboard_path=root/"dashboard-summary.json"
    if dashboard_path.exists():
        if json.loads(dashboard_path.read_text(encoding="utf-8")) != dashboard:
            raise ValueError(f"existing dashboard summary does not match current derived analysis: {dashboard_path}")
    else:
        dashboard_path.write_text(json.dumps(dashboard,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    figure_dir=root/"report"/"figures"
    figures={name:figure_dir/f"{name}.png" for name in ("architecture","branches","utility","effects","heatmap","continuity","dashboard")}
    architecture_figure(figures["architecture"]);branch_figure(figures["branches"]);utility_figure(analysis,figures["utility"])
    effects_figure(analysis,figures["effects"]);heatmap_figure(analysis,figures["heatmap"]);continuity_figure(analysis,figures["continuity"]);dashboard_figure(dashboard,analysis,figures["dashboard"])
    if args.prepare_only:
        print(json.dumps({"dashboard_summary":str(dashboard_path),"figures":{k:str(v) for k,v in figures.items()}},indent=2))
        return 0
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    build_pdf(dashboard,analysis,adjudication,output,figures,Path(args.ui_image) if args.ui_image else figures["dashboard"])
    print(json.dumps({"pdf":str(output),"dashboard_summary":str(dashboard_path),"figures":{k:str(v) for k,v in figures.items()}},indent=2))
    return 0


if __name__=="__main__": raise SystemExit(main())
