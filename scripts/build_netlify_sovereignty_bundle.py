#!/usr/bin/env python3
"""Build the curated Netlify deployment seed and authenticated dashboard UI."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from godelOS.cognitive_sovereignty.evolution_store import EvolutionStore
from godelOS.cognitive_sovereignty.store import SovereigntyStore


DEFAULT_BUNDLE = ROOT / "deploy" / "netlify-sovereignty-lab"
DEFAULT_DB = ROOT / "research_artifacts" / "cognitive_sovereignty" / "deepseek-evolution-chamber-v3" / "evolution.sqlite3"
DEFAULT_SUMMARY = ROOT / "research_artifacts" / "cognitive_sovereignty" / "deepseek-evolution-v2" / "experiment-summary-reassessed.json"
DEFAULT_CHAMBER_SUMMARY = DEFAULT_DB.with_name("dashboard-summary.json")
DEFAULT_REPORT = ROOT / "output" / "pdf" / "godelos-integrated-mind-v8-report.pdf"
DEFAULT_ZIP = ROOT / "output" / "deploy" / "godelos-integrated-mind-v8-netlify.zip"
SOURCE_UI = ROOT / "godelOS" / "cognitive_sovereignty" / "web_assets" / "index.html"


def curated_summary(source: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "schema_version", "experiment_id", "model", "run_counts", "profiles",
        "calibration", "holdout", "parent_profile_id", "challenger_profile_id",
        "active_profile_id", "adoption", "original_adoption", "bootstrap_comparisons",
        "agent_generated_thesis", "next_methodology", "preregistered_thesis",
    }
    result = {key: source[key] for key in keep if key in source}
    methodology = result.get("next_methodology")
    if isinstance(methodology, dict):
        result["next_methodology"] = {
            key: value for key, value in methodology.items()
            if key not in {"raw_response", "prompt", "provider"}
        }
    return result


def curated_chamber_summary(source: dict[str, Any]) -> dict[str, Any]:
    """Keep deployable results while excluding raw prompts and reviewer transcripts."""
    protocol = dict(source.get("protocol") or {})
    origin = dict(protocol.get("origin") or {})
    origin.pop("source", None)
    protocol["origin"] = origin
    reviews = {}
    for key in ("pre_run_review", "post_run_review"):
        review = dict(source.get(key) or {})
        reviews[key] = {
            field: review.get(field)
            for field in ("review_id", "reviewer", "verdict", "summary", "attacks", "promotion_blockers")
        }
    return {
        "schema_version": source.get("schema_version"),
        "experiment_id": source.get("experiment_id"),
        "created_at": source.get("created_at"),
        "protocol": protocol,
        "analysis": source.get("analysis"),
        **reviews,
        "patch_evaluation": source.get("patch_evaluation"),
        "successor_package": source.get("successor_package"),
        "promotion": source.get("promotion"),
        "review_adjudication": source.get("review_adjudication"),
    }


def curated_objects(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = {
        "value_profile", "thesis", "protocol", "successor_candidate",
        "adoption_decision", "adoption_reassessment", "agent_generated_thesis",
        "methodology_proposal", "manual_value_candidate",
    }
    result = []
    for item in items:
        if item.get("object_type") not in allowed:
            continue
        payload = dict(item.get("payload") or {})
        for key in ("raw_response", "prompt", "provider"):
            payload.pop(key, None)
        result.append({
            "object_id": item["object_id"],
            "object_type": item["object_type"],
            "payload": payload,
            "created_at": item["created_at"],
        })
    return result


def curated_events(store: SovereigntyStore, agent_id: str) -> list[dict[str, Any]]:
    return [
        {
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "created_at": event["created_at"],
            "previous_hash": event["previous_hash"],
            "event_hash": event["event_hash"],
            "payload": {"result_version": event["payload"].get("result_version")},
        }
        for event in store.events(agent_id)[-30:]
    ]


def deployment_seed(db: Path, summary_path: Path, chamber_summary_path: Path, agent_id: str) -> dict[str, Any]:
    state_store = SovereigntyStore(db)
    state = state_store.load(agent_id).to_mapping()
    events = state_store.events(agent_id)
    return {
        "state": state,
        "state_version": state_store.version(agent_id),
        "legacy_event_chain_valid": state_store.verify_event_chain(agent_id),
        "legacy_head_hash": events[-1]["event_hash"] if events else None,
        "legacy_events": curated_events(state_store, agent_id),
        "evolution_objects": curated_objects(EvolutionStore(db).objects()),
        "experiment": curated_summary(json.loads(summary_path.read_text(encoding="utf-8"))),
        "chamber": curated_chamber_summary(json.loads(chamber_summary_path.read_text(encoding="utf-8"))),
    }


AUTH_CSS = """
    .access-gate{position:fixed;inset:0;z-index:1000;display:grid;place-items:center;padding:20px;background:rgba(3,6,13,.92);backdrop-filter:blur(18px)}
    .access-gate.hidden{display:none}.gate-card{width:min(520px,100%);padding:28px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(145deg,#121a2c,#0b101d);box-shadow:0 30px 100px #000}
    .gate-card h1{font-size:27px;margin:0 0 10px;letter-spacing:-.04em}.gate-card p{color:var(--muted);line-height:1.55;font-size:13px}.gate-card input{width:100%;margin:12px 0 4px;padding:13px;border:1px solid var(--line);border-radius:10px;background:#080d18;color:var(--ink)}
    .gate-error{min-height:20px;color:var(--coral);font-size:11px;margin-top:8px}.report-link{display:block;color:var(--cyan);margin-top:8px;text-decoration:none}
"""

AUTH_HTML = """
<div class="access-gate" id="accessGate">
  <div class="gate-card">
    <div class="eyebrow">Protected research control plane</div>
    <h1>Enter the sovereignty access token</h1>
    <p>The token is configured separately in Netlify and stays in this browser tab. The DeepSeek key never enters the browser.</p>
    <input id="accessToken" type="password" autocomplete="current-password" placeholder="SOVEREIGNTY_ACCESS_TOKEN">
    <div class="actions"><button class="action" id="connectAccess">Connect</button></div>
    <div class="gate-error" id="gateError"></div>
  </div>
</div>
"""

AUTH_JS = """
let accessToken=sessionStorage.getItem('godelos-access-token')||'';
function showGate(message=''){document.getElementById('accessGate').classList.remove('hidden');document.getElementById('gateError').textContent=message;setTimeout(()=>document.getElementById('accessToken').focus(),0)}
function hideGate(){document.getElementById('accessGate').classList.add('hidden')}
async function apiFetch(url,options={}){if(!accessToken){showGate('Enter the access token configured in Netlify.');throw new Error('Access token required')}const operation_id=typeof crypto.randomUUID==='function'?crypto.randomUUID():String(Date.now());document.dispatchEvent(new CustomEvent('godelos:network',{detail:{stage:'begin',operation_id,url,method:options.method||'GET',at:Date.now()}}));const headers={...(options.headers||{}),Authorization:`Bearer ${accessToken}`};try{const response=await fetch(url,{...options,headers});document.dispatchEvent(new CustomEvent('godelos:network',{detail:{stage:'response',operation_id,url,status:response.status,ok:response.ok,at:Date.now()}}));if(response.status===401){sessionStorage.removeItem('godelos-access-token');accessToken='';showGate('That access token was refused.');throw new Error('Access token refused')}return response}catch(error){document.dispatchEvent(new CustomEvent('godelos:network',{detail:{stage:'error',operation_id,url,message:error.message,at:Date.now()}}));throw error}}
"""


def authenticated_ui(source: str) -> str:
    result = source.replace("  </style>", AUTH_CSS + "  </style><link rel=\"stylesheet\" href=\"/workbench.css\">")
    result = result.replace('</body>', '<link rel="stylesheet" href="/independence.css"><link rel="stylesheet" href="/living-agent.css"><link rel="stylesheet" href="/mind.css"><script src="/workbench.js" defer></script><script src="/independence.js" defer></script><script src="/living-agent.js" defer></script><script src="/mind.js" defer></script><link rel="stylesheet" href="/interface.css"><script src="/interface.js" defer></script></body>')
    result=result.replace('</body>','<link rel="stylesheet" href="/workspace10.css?v=13.0.0-alpha.1"><script src="/workspace10.js?v=13.0.0-alpha.1" defer></script><link rel="stylesheet" href="/living13.css?v=13.0.0-alpha.1"><script src="/living13.js?v=13.0.0-alpha.1" defer></script></body>').replace('/mind.js"','/mind.js?v=13.0.0-alpha.1"').replace('/interface.js"','/interface.js?v=13.0.0-alpha.1"')
    result = result.replace("<body>", "<body>" + AUTH_HTML)
    result = result.replace(
        '<div id="modelLabel">Model pending</div>',
        '<div id="modelLabel">Model pending</div><a class="report-link" href="/godelos-integrated-mind-v8-report.pdf" target="_blank" rel="noopener">Open V8 evidence report ↗</a>',
    )
    result = result.replace(
        "let snapshot=null, baseValues={};",
        AUTH_JS + "\nlet snapshot=null, baseValues={};",
    )
    result = result.replace("fetch('/api/", "apiFetch('/api/")
    old_load = "async function load(){try{if(window.__SOVEREIGNTY_SNAPSHOT__){render(window.__SOVEREIGNTY_SNAPSHOT__);return}const r=await apiFetch('/api/snapshot');render(await r.json())}catch(e){$('systemStatus').textContent='OFFLINE';console.error(e)}}"
    new_load = "async function load(){try{const r=await apiFetch('/api/snapshot');const x=await r.json();if(!r.ok)throw new Error(x.error||`HTTP ${r.status}`);render(x);hideGate();window.dispatchEvent(new Event('sovereignty:connected'));return true}catch(e){$('systemStatus').textContent='OFFLINE';if(accessToken)$('gateError').textContent=e.message;console.error(e);return false}}"
    if old_load not in result:
        raise RuntimeError("source dashboard load function changed; update Netlify transformation")
    result = result.replace(old_load, new_load)
    old_tail = "$('message').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('send').click()}};load();"
    new_tail = "$('message').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('send').click()}};$('connectAccess').onclick=async()=>{const candidate=$('accessToken').value.trim();if(!candidate)return;accessToken=candidate;sessionStorage.setItem('godelos-access-token',candidate);$('gateError').textContent='Connecting…';if(!await load()){sessionStorage.removeItem('godelos-access-token')}};$('accessToken').onkeydown=e=>{if(e.key==='Enter')$('connectAccess').click()};if(accessToken)load();else showGate();"
    if old_tail not in result:
        raise RuntimeError("source dashboard boot sequence changed; update Netlify transformation")
    return result.replace(old_tail, new_tail)


def write_manifest(bundle: Path, seed: dict[str, Any]) -> None:
    ignored = {"node_modules", ".netlify", "__pycache__"}
    files = []
    for path in sorted(bundle.rglob("*")):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.name in {"DEPLOYMENT_MANIFEST.json", ".env"} or path.suffix == ".zip":
            continue
        content = path.read_bytes()
        files.append({
            "path": path.relative_to(bundle).as_posix(),
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    manifest = {
        "schema_version": "1.0",
        "bundle": "godelos-sovereignty-lab-netlify",
        "agent_id": seed["state"]["agent_id"],
        "state_version": seed["state_version"],
        "legacy_event_chain_valid": seed["legacy_event_chain_valid"],
        "experiment_id": seed["chamber"]["experiment_id"],
        "model": next(iter(seed["chamber"]["analysis"].get("execution", {}).get("models", {})), seed["experiment"]["model"]),
        "diagnostic_runs": seed["experiment"]["run_counts"]["completed"],
        "chamber_phases": seed["chamber"]["analysis"]["run_counts"]["completed"],
        "workbench": {"version": "5.0", "agent_led_campaigns": True,
                      "engine_sha256": hashlib.sha256((bundle / 'netlify/functions/lib/workbench.mjs').read_bytes()).hexdigest()},
        "runtime_build": "13.0.0-alpha.1",
        "living_v13": {"guide": "LIVING_MIND_V13.md", "analysis": "research/living13-analysis.json", "probe": "stance_recall", "visual_qa": "blocked"},
        "development_v12": {"mode": "shadow_attention_policy", "automatic_promotion": False,
                            "scheduler_minutes": 15, "guide": "DEVELOPMENT_V12.md"},
        "model_scope": "historical_seed",
        "configured_default_model": "deepseek-flash",
        "workspace_v10": {"baseline": "research/workspace-v10/provider-r2/derived/analysis.json",
                          "verification": "research/workspace-v10/provider-compact-verification/derived/analysis.json",
                          "summary": "research/workspace-v10/evaluation-summary.json",
                          "report": "public/godelos-workspace-v10-report.pdf"},
        "integrated_mind": {"version": "13.0.0-alpha.1", "default_view": "mind",
                            "kernel_sha256": hashlib.sha256((bundle / 'netlify/functions/lib/mind.mjs').read_bytes()).hexdigest(),
                            "report": "public/godelos-v13-living-mind-report.pdf"},
        "files": files,
    }
    (bundle / "DEPLOYMENT_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_zip(bundle: Path, output: Path) -> str:
    ignored = {"node_modules", ".netlify", "__pycache__"}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(bundle.rglob("*")):
            if not path.is_file() or any(part in ignored for part in path.parts):
                continue
            if path.name == ".env" or path.suffix == ".zip":
                continue
            archive.write(path, Path(bundle.name) / path.relative_to(bundle))
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--chamber-summary", type=Path, default=DEFAULT_CHAMBER_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--zip-output", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--agent-id", default="godelos-sovereign-01")
    parser.add_argument("--forge-summary", type=Path)
    parser.add_argument("--verified-suite", type=Path)
    args = parser.parse_args()

    public = args.bundle / "public"
    functions = args.bundle / "netlify" / "functions" / "lib"
    public.mkdir(parents=True, exist_ok=True)
    functions.mkdir(parents=True, exist_ok=True)

    seed = deployment_seed(args.db, args.summary, args.chamber_summary, args.agent_id)
    (functions / "seed.mjs").write_text(
        "// Generated by scripts/build_netlify_sovereignty_bundle.py\n"
        f"export default {json.dumps(seed, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    (public / "index.html").write_text(
        authenticated_ui(SOURCE_UI.read_text(encoding="utf-8")), encoding="utf-8"
    )
    shutil.copyfile(args.report, public / "godelos-integrated-mind-v8-report.pdf")
    for name in ('workbench.js', 'workbench.css', 'independence.js', 'independence.css', 'living-agent.js', 'living-agent.css', 'mind.js', 'mind.css', 'interface.js', 'interface.css', 'workspace10.js', 'workspace10.css', 'living13.js', 'living13.css', 'release13.html', 'release12.html', 'release12.js', 'release12.css'):
        shutil.copyfile(ROOT / 'godelOS/cognitive_sovereignty/web_assets' / name, public / name)
    report_v10=ROOT/'output/pdf/godelos-workspace-v10-report.pdf'
    if report_v10.exists():shutil.copyfile(report_v10,public/report_v10.name)
    evidence_v10=ROOT/'research_artifacts/cognitive_sovereignty/workspace-v10'
    if evidence_v10.exists():shutil.copytree(evidence_v10,args.bundle/'research/workspace-v10',dirs_exist_ok=True)
    shutil.copyfile(ROOT/'docs/WORKSPACE_V10.md',args.bundle/'WORKSPACE_V10.md')
    shutil.copyfile(ROOT/'docs/DEVELOPMENT_V12.md',args.bundle/'DEVELOPMENT_V12.md')
    mind_research=args.bundle / 'research' / 'integrated-mind-v8'
    mind_research.mkdir(parents=True, exist_ok=True)
    for name in ('INTEGRATED_MIND_V8.md', 'INTEGRATED_MIND_V8_RESULTS.md'):
        shutil.copyfile(ROOT / 'docs' / name, mind_research / name)
    for run in ('integrated-mind-v8-live', 'integrated-mind-v8-live-r2', 'integrated-mind-v8-analysis', 'integrated-mind-v8-observation'):
        source=ROOT / 'research_artifacts/cognitive_sovereignty' / run
        if source.exists():
            shutil.copytree(source,mind_research / run,dirs_exist_ok=True)
    shutil.copyfile(ROOT / 'scripts/generate_integrated_mind_report.py', mind_research / 'generate_report.py')
    for name in ('godelos-integrated-mind-v8-preview.jpg', 'godelos-integrated-mind-v8-report-view.jpg', 'godelos-integrated-mind-v8-detail.jpg'):
        shutil.copyfile(ROOT / 'output/deploy' / name, mind_research / name)
    shutil.copytree(ROOT / 'output/research/integrated-mind-v8/figures', mind_research / 'figures', dirs_exist_ok=True)
    shutil.copyfile(ROOT / 'output/research/integrated-mind-v8-tests.txt', mind_research / 'tests.txt')
    (mind_research / 'fonts').mkdir(exist_ok=True)
    for name in ('DejaVuSans.ttf','DejaVuSans-Bold.ttf'):
        shutil.copyfile(Path('/usr/share/fonts/truetype/dejavu') / name, mind_research / 'fonts' / name)
    shutil.copyfile('/usr/share/doc/fonts-dejavu-core/copyright', mind_research / 'fonts/LICENSE.txt')
    living_research = args.bundle / "research" / "living-agent-v7"
    living_research.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "docs/LIVING_SOVEREIGN_AGENT_V7.md", living_research / "README.md")
    live_report = ROOT / "research_artifacts/cognitive_sovereignty/living-agent-v7-live-r2/living-agent-live-report.json"
    if live_report.exists():
        shutil.copyfile(live_report, living_research / "living-agent-live-report.json")
    if args.forge_summary:
        shutil.copyfile(args.forge_summary, public / "forge-summary.json")
        shutil.copyfile(ROOT / "godelOS/cognitive_sovereignty/web_assets/forge.js", public / "forge.js")
        # Ship the executable research-side component, not just a results dashboard.
        research = args.bundle / "research"
        research.mkdir(exist_ok=True)
        shutil.copytree(ROOT / "godelOS/cognitive_sovereignty", research / "godelOS/cognitive_sovereignty",
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        (research / "godelOS/__init__.py").write_text("", encoding="utf-8")
        shutil.copyfile(ROOT / "docs/ADAPTIVE_FORGE_V4.md", research / "README.md")
        shutil.copyfile(ROOT / "docs/FORGE_NEXT_BUILD.md", research / "NEXT_BUILD.md")
        shutil.copyfile(ROOT / "docs/SELF_DIRECTED_WORKBENCH_V5.md", research / "WORKBENCH_V5.md")
        live = ROOT / 'research_artifacts/cognitive_sovereignty/workbench-v5-live'
        if live.exists():
            (research / 'workbench-v5-live').mkdir(exist_ok=True)
            for name in ('summary.json', 'campaign-export.json'):
                shutil.copyfile(live / name, research / 'workbench-v5-live' / name)
        preview = Path('/workspace/scratch/godelos-workbench-v5-preview.jpg')
        if preview.exists():
            shutil.copyfile(preview, research / 'workbench-v5-preview.jpg')
        for name in ("test_adaptive_forge.py", "test_evolution_chamber.py", "test_cognitive_sovereignty.py", "test_forge_hardening.py"):
            (research / "tests").mkdir(exist_ok=True)
            shutil.copyfile(ROOT / "tests" / name, research / "tests" / name)
        evidence = research / "results"
        shutil.copytree(args.forge_summary.parent, evidence, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.sqlite3", "*.sqlite3-wal", "*.sqlite3-shm", "*.pem"))
        if args.verified_suite:
            tasks = json.loads((args.verified_suite / "sealed-tasks.json").read_text())["payload"]["tasks"]
            records = json.loads((args.verified_suite / "oracle-records.json").read_text())["records"]
            (public / "forge-verified.json").write_text(json.dumps({"tasks": tasks, "records": records}, indent=2), encoding="utf-8")
            shutil.copytree(args.verified_suite, research / "verified-diagnostic", dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("*.sqlite3", "*.pem"))
    write_manifest(args.bundle, seed)
    zip_hash = write_zip(args.bundle, args.zip_output)
    print(json.dumps({
        "bundle": str(args.bundle),
        "zip": str(args.zip_output),
        "zip_sha256": zip_hash,
        "state_version": seed["state_version"],
        "event_chain_valid": seed["legacy_event_chain_valid"],
        "model": next(iter(seed["chamber"]["analysis"].get("execution", {}).get("models", {})), seed["experiment"]["model"]),
        "diagnostic_runs": seed["experiment"]["run_counts"]["completed"],
        "chamber_phases": seed["chamber"]["analysis"]["run_counts"]["completed"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
