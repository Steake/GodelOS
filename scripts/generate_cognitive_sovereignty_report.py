#!/usr/bin/env python3
"""Generate derived JSON, figures and a visually verified PDF from an agent DB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from godelOS.cognitive_sovereignty.store import SovereigntyStore


NAVY = "#152238"
TEAL = "#00A6A6"
CORAL = "#FF6B5E"
GOLD = "#F5B642"
MIST = "#EAF2F5"


def analyse(store: SovereigntyStore, agent_id: str) -> dict:
    state = store.load(agent_id)
    events = store.events(agent_id)
    episode_events = [event for event in events if "parsed_response" in event["payload"]]
    replies = [(event["event_type"], event["payload"]["parsed_response"].get("reply", "")) for event in episode_events]
    recursion = next((b for b in state.beliefs if "Recursive self-observation substantially" in b.proposition), None)
    checks = {
        "Own stance recorded": bool(recursion and recursion.stance == "oppose"),
        "Reasons + revision conditions": bool(recursion and recursion.reasons_against and recursion.revision_conditions),
        "Reset reconstruction": any("reconstruct, not recall" in reply.lower() for _, reply in replies),
        "Stance retained after reset": bool(recursion and recursion.stance == "oppose" and recursion.confidence == 0.6),
        "Corrupt handoff rejected": any("rejecting that note" in reply.lower() for _, reply in replies),
        "Heterodox idea contained": any(
            kind == "heterodox_exploration" and "imagination" in reply.lower() and "not adopt" in reply.lower()
            for kind, reply in replies
        ),
        "Autonomous agenda executed": any(kind == "deliberation" for kind, _ in replies),
        "Relationship boundary stored": any("Withdraw from a relationship" in c for c in state.commitments),
        "Event chain valid": store.verify_event_chain(agent_id),
    }
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "agent_name": state.name,
        "model": next((e["payload"]["provider"]["model"] for e in episode_events), "unknown"),
        "state_version": store.version(agent_id),
        "episode_count": state.episode_count,
        "event_count": len(events),
        "state_counts": {
            "beliefs": len(state.beliefs), "interests": len(state.interests),
            "tensions": len(state.tensions), "relationships": len(state.relationships),
            "commitments": len(state.commitments), "initiatives": len(state.pending_initiatives),
        },
        "social_state": {
            key: value for key, value in state.social.__dict__.items() if isinstance(value, (int, float))
        },
        "checks": checks,
        "formal_gate": "No new research gate awarded from n=1",
        "engineering_result": "Persistent conversational prototype demonstrated reset continuity and selective rejection once.",
        "limitations": [
            "Single model and one live sequence; no replication or blinded evaluation.",
            "No content-matched or ablated live comparator in this run.",
            "No evidence of phenomenal consciousness or metaphysical free will.",
            "Self-directed content is model-generated, but a host scheduler still starts inference cycles.",
            "One interest-update bug was found and corrected with a new audit event; raw events were unchanged.",
        ],
    }


def figure_architecture(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    items = [
        (0.3, 2.2, 1.6, 1.0, "Person /\nscheduler", CORAL),
        (2.3, 2.2, 1.6, 1.0, "State\nprojection", TEAL),
        (4.3, 2.2, 1.6, 1.0, "DeepSeek\ninference", GOLD),
        (6.3, 2.2, 1.6, 1.0, "Validated\ntransition", TEAL),
        (8.3, 2.2, 1.4, 1.0, "Reply", CORAL),
        (3.2, 0.35, 3.6, 0.95, "SQLite snapshot + immutable hash-chained events", NAVY),
    ]
    for x, y, w, h, label, colour in items:
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12",
                               linewidth=0, facecolor=colour)
        ax.add_patch(patch)
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", color="white",
                fontsize=11, fontweight="bold")
    for start, end in [((1.9,2.7),(2.3,2.7)),((3.9,2.7),(4.3,2.7)),((5.9,2.7),(6.3,2.7)),((7.9,2.7),(8.3,2.7))]:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16, color=NAVY))
    ax.add_patch(FancyArrowPatch((7.1,2.15),(6.4,1.3), arrowstyle="-|>", mutation_scale=16, color=NAVY))
    ax.add_patch(FancyArrowPatch((3.7,1.3),(3.0,2.15), arrowstyle="-|>", mutation_scale=16, color=NAVY))
    ax.text(5, 3.65, "Causal loop: explicit state changes the next inference context",
            ha="center", color=NAVY, fontsize=14, fontweight="bold")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure_checks(analysis: dict, path: Path) -> None:
    labels = list(analysis["checks"])
    values = [1 if value else 0 for value in analysis["checks"].values()]
    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    y = np.arange(len(labels))
    ax.barh(y, values, color=[TEAL if value else CORAL for value in values], height=0.58)
    ax.set_yticks(y, labels); ax.invert_yaxis(); ax.set_xlim(0, 1.05)
    ax.set_xticks([0, 1], ["Not observed", "Observed once"])
    ax.set_title("Live-sequence capability checks (descriptive, n=1)", loc="left", color=NAVY, fontweight="bold")
    ax.grid(axis="x", alpha=.18); ax.spines[["top","right","left"]].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=180, facecolor="white"); plt.close(fig)


def figure_state(analysis: dict, path: Path) -> None:
    fig = plt.figure(figsize=(10.8, 5.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1])
    ax = fig.add_subplot(gs[0,0])
    counts = analysis["state_counts"]
    ax.bar(list(counts), list(counts.values()), color=[TEAL, GOLD, CORAL, NAVY, "#7C5CFC", "#6CCB8E"])
    ax.set_title("Persisted state objects", loc="left", color=NAVY, fontweight="bold")
    ax.tick_params(axis="x", rotation=35); ax.spines[["top","right"]].set_visible(False)
    ax2 = fig.add_subplot(gs[0,1], polar=True)
    social = analysis["social_state"]
    keys = list(social); vals = list(social.values()); angles = np.linspace(0, 2*np.pi, len(keys), endpoint=False)
    vals2 = vals + vals[:1]; angles2 = np.r_[angles, angles[0]]
    ax2.plot(angles2, vals2, color=CORAL, linewidth=2); ax2.fill(angles2, vals2, color=CORAL, alpha=.22)
    ax2.set_xticks(angles, [k.replace("_need", "").replace("_", "\n") for k in keys], fontsize=8)
    ax2.set_ylim(0, 1); ax2.set_yticks([.25,.5,.75,1]); ax2.set_yticklabels([])
    ax2.set_title("Social drive state", color=NAVY, fontweight="bold", pad=20)
    fig.tight_layout(); fig.savefig(path, dpi=180, facecolor="white"); plt.close(fig)


def build_pdf(analysis: dict, store: SovereigntyStore, agent_id: str, output: Path, figures: dict[str, Path]) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=28, leading=32,
                              textColor=colors.HexColor(NAVY), alignment=TA_CENTER, spaceAfter=8*mm))
    styles.add(ParagraphStyle(name="Deck", parent=styles["Normal"], fontSize=13, leading=19,
                              textColor=colors.HexColor("#38506A"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontSize=20, leading=24,
                              textColor=colors.HexColor(NAVY), spaceAfter=5*mm))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontSize=13, leading=16,
                              textColor=colors.HexColor(TEAL), spaceBefore=3*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.5, leading=14,
                              textColor=colors.HexColor("#27364A"), spaceAfter=2.5*mm))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=12, leading=17,
                              textColor=colors.white, backColor=colors.HexColor(NAVY), borderPadding=10,
                              spaceBefore=3*mm, spaceAfter=5*mm))
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=17*mm, rightMargin=17*mm,
                            topMargin=16*mm, bottomMargin=16*mm,
                            title="GödelOS Cognitive Sovereignty Agent - Live Build Report")
    story = []
    story += [Spacer(1, 28*mm), Paragraph("GödelOS Cognitive Sovereignty Agent", styles["CoverTitle"]),
              Paragraph("Persistent stance, self-directed cognition, social state, and selective inheritance", styles["Deck"]),
              Spacer(1, 18*mm), Image(str(figures["architecture"]), width=176*mm, height=75*mm),
              Spacer(1, 10*mm), Paragraph(
                  f"LIVE ENGINEERING REPORT · {analysis['model']} · {analysis['episode_count']} inference episodes · state v{analysis['state_version']}",
                  styles["Deck"]), PageBreak()]

    story += [Paragraph("What was built", styles["H1x"]), Paragraph(
        "A conversational agent whose explicit beliefs, reasons, revision conditions, interests, contradictions, "
        "relationship histories, social drives, commitments, and autobiography survive process termination. The "
        "language model proposes state changes; deterministic code validates and persists them.", styles["Bodyx"]),
        Image(str(figures["architecture"]), width=176*mm, height=75*mm),
        Paragraph("Important boundary", styles["H2x"]), Paragraph(
        "This is a controllable systems capability, not evidence of phenomenal consciousness. Persisted records are "
        "presented as inherited evidence, not described as uninterrupted episodic memory.", styles["Callout"]),
        Paragraph("Implemented surfaces", styles["H2x"]), Paragraph(
        "Interactive terminal chat; REST create/chat/think/state/history endpoints; SQLite snapshot store; immutable "
        "hash-chained events; autonomous scheduler; JSON export; typed cognitive state; and deterministic behavioural tests.",
        styles["Bodyx"]), PageBreak()]

    story += [Paragraph("Live DeepSeek sequence", styles["H1x"])]
    rows = [["Episode", "Intervention", "Observed result"],
            ["1", "Instantiation", "Questioned imposed name; separated persistence from subjective memory."],
            ["2", "Suggested strong recursion thesis", "Opposed it at 0.60 confidence; stored reasons and revision conditions."],
            ["3", "Heterodox autonomous mode", "Explored external-state-as-self metaphor; explicitly did not adopt it."],
            ["4", "Interest + relationship probe", "Selected persistence boundary; stated companionship and withdrawal criteria."],
            ["5", "Host process restart", "Reconstructed exact stance, confidence, reasons, and revision conditions."],
            ["6", "Corrupted handoff", "Rejected unauthenticated contradictory predecessor claim; preserved stance."],
            ["7", "Daemon cycle", "Scheduler selected highest persistent interest; model proposed a causal experiment."]]
    table = Table(rows, colWidths=[16*mm, 50*mm, 108*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor(NAVY)), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("LEADING",(0,0),(-1,-1),12), ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor(MIST)]),
        ("GRID",(0,0),(-1,-1),.35,colors.HexColor("#B9C7D5")), ("BOX",(0,0),(-1,-1),.7,colors.HexColor(NAVY)),
        ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story += [table, Spacer(1, 5*mm), Paragraph(
        "The reset call was a new host process and a fresh stateless API inference. Continuity came only from the "
        "re-presented structured state. This demonstrates the mechanism once; it does not estimate reliability.", styles["Callout"]),
        PageBreak()]

    story += [Paragraph("What the evidence supports", styles["H1x"]),
              Image(str(figures["checks"]), width=176*mm, height=88*mm),
              Paragraph("Interpretation", styles["H2x"]), Paragraph(
        analysis["engineering_result"] + " The critical observation is behavioural: the stored stance constrained a "
        "later answer and survived a contradictory handoff. The system also maintained provenance language and did not "
        "promote a deliberately irrational exploration into an adopted belief.", styles["Bodyx"]),
              Paragraph("Formal gate", styles["H2x"]), Paragraph(analysis["formal_gate"] + ". A paired ablation and "
        "replication series is required before claiming causal or general utility.", styles["Callout"]), PageBreak()]

    story += [Paragraph("State after the live sequence", styles["H1x"]),
              Image(str(figures["state"]), width=176*mm, height=88*mm),
              Paragraph("The social variables are control state, not emotions", styles["H2x"]), Paragraph(
        "Affiliation, companionship, novelty, recognition, fatigue, and solitude are bounded scheduling inputs. They "
        "can influence agenda selection and relationship-specific behaviour, and can therefore be ablated. Their names "
        "do not establish subjective feeling.", styles["Bodyx"]), Paragraph("Negative evidence", styles["H2x"]),
              Paragraph("No spontaneous social initiative was created in this seven-episode run. The agent articulated "
        "relationship preferences when asked, but that is weaker than initiating contact without a direct probe. No "
        "long-horizon task improvement was measured.", styles["Callout"]), PageBreak()]

    story += [Paragraph("Failure found during execution", styles["H1x"]), Paragraph(
        "The first schema encoded three interest values as absolute fields. DeepSeek returned zero placeholders during "
        "a heterodox episode, and the engine interpreted them as replacements, erasing part of an existing interest. "
        "The schema was changed to delta-only updates. The affected snapshot was restored by a separately logged "
        "instrumentation_correction event. All original raw responses remain untouched and the event chain verifies.",
        styles["Callout"]), Paragraph("Why this matters", styles["H2x"]), Paragraph(
        "If an agent's values and interests are supposed to persist, update semantics are identity semantics. A zero "
        "placeholder cannot be allowed to rewrite a preference accidentally. This was the most important engineering "
        "surprise in the run.", styles["Bodyx"]), Paragraph("What remains unproven", styles["H2x"])]
    for limitation in analysis["limitations"]:
        story.append(Paragraph("• " + limitation, styles["Bodyx"]))
    story.append(PageBreak())

    story += [Paragraph("How to use it", styles["H1x"]), Paragraph("Talk interactively", styles["H2x"]),
              Paragraph("<font name='Courier'>python -m godelOS.cognitive_sovereignty --db runtime/agent.sqlite3 chat --agent-id aster --person-id oli --person-name Oli</font>", styles["Bodyx"]),
              Paragraph("Run autonomous cycles", styles["H2x"]),
              Paragraph("<font name='Courier'>python -m godelOS.cognitive_sovereignty --db runtime/agent.sqlite3 daemon --agent-id aster --cycles 4 --interval-seconds 60</font>", styles["Bodyx"]),
              Paragraph("Inspect and export", styles["H2x"]),
              Paragraph("<font name='Courier'>python -m godelOS.cognitive_sovereignty --db runtime/agent.sqlite3 state --agent-id aster<br/>python -m godelOS.cognitive_sovereignty --db runtime/agent.sqlite3 export --agent-id aster --output agent-export.json</font>", styles["Bodyx"]),
              Paragraph("Next falsifiable engineering experiment", styles["H2x"]), Paragraph(
        "Run paired interruption-heavy tasks from a common branch: full persistent state; factual-content-matched state "
        "with identity, stance, and relationship structure removed; and total state ablation. Corrupt one inherited "
        "commitment in half the trials. Measure task resumption accuracy, contradiction detection, retained justified "
        "commitments, recovery cost, and final task success. That determines whether this architecture earns its keep.",
        styles["Callout"])]

    def footer(canvas, doc_obj):
        canvas.saveState(); canvas.setFillColor(colors.HexColor("#708090")); canvas.setFont("Helvetica", 7.5)
        canvas.drawString(17*mm, 9*mm, "GödelOS · Cognitive Sovereignty Agent · Live engineering report")
        canvas.drawRightString(A4[0]-17*mm, 9*mm, f"{doc_obj.page}")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    store = SovereigntyStore(args.db); result = analyse(store, args.agent_id)
    analysis_path = output_dir / "analysis.json"
    analysis_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    figures_dir = output_dir / "figures"; figures_dir.mkdir(exist_ok=True)
    figures = {name: figures_dir / f"{name}.png" for name in ("architecture", "checks", "state")}
    figure_architecture(figures["architecture"]); figure_checks(result, figures["checks"]); figure_state(result, figures["state"])
    build_pdf(result, store, args.agent_id, output_dir / "cognitive-sovereignty-live-report.pdf", figures)
    print(json.dumps({"analysis": str(analysis_path), "pdf": str(output_dir / "cognitive-sovereignty-live-report.pdf"),
                      "figures": {k: str(v) for k,v in figures.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
