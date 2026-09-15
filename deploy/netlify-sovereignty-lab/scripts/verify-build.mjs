import { readFile, stat } from "node:fs/promises";

const required = [
  "public/release12.html",
  "public/release12.js",
  "public/release12.css",
  "public/release-evidence.json",
  "public/godelos-v12-release-report.pdf",
  "RELEASE_V12.md",
  "netlify/functions/lib/verification12.mjs",
  "netlify/functions/lib/promotion12.mjs",
  "public/index.html",
  "public/workbench.js",
  "public/workbench.css",
  "public/independence.js",
  "public/independence.css",
  "public/living-agent.js",
  "public/living-agent.css",
  "public/mind.js",
  "public/mind.css",
  "public/workspace10.css",
  "public/workspace10.js",
  "public/godelos-workspace-v10-report.pdf",
  "WORKSPACE_V10.md",
  "scripts/workspace-experiment.mjs",
  "netlify/functions/lib/interventions.mjs",
  "netlify/functions/lib/workspace-diagnostic.mjs",
  "netlify/functions/lib/autonomy-control.mjs",
  "netlify/functions/lib/mind.mjs",
  "netlify/functions/lib/mind-runtime.mjs",
  "netlify/functions/lib/mind-parser.mjs",
  "scripts/live-mind.mjs",
  "scripts/analyse-mind.mjs",
  "scripts/live-mind-observation.mjs",
  "public/godelos-integrated-mind-v8-report.pdf",
  "research/integrated-mind-v8/INTEGRATED_MIND_V8.md",
  "netlify/functions/lib/independence.mjs",
  "netlify/functions/independence-worker.mjs",
  "netlify/functions/independence-scheduler.mjs",
  "netlify/functions/autonomy-worker.mjs",
  "netlify/functions/autonomy-scheduler.mjs",
  "scripts/live-agent-life.mjs",
  "public/godelos-living-sovereign-agent-v7-report.pdf",
  "research/living-agent-v7/README.md",
  "research/living-agent-v7/living-agent-live-report.json",
  "netlify/functions/lib/workbench.mjs",
  "public/godelos-successor-forge-live-report.pdf",
  "netlify/functions/api.mjs",
  "netlify/functions/lib/core.mjs",
  "netlify/functions/lib/seed.mjs",
  "netlify.toml",
  "DEPLOYMENT_MANIFEST.json",
];

for (const path of required) {
  const info = await stat(path);
  if (!info.isFile() || info.size === 0) throw new Error(`missing deployment artefact: ${path}`);
}

for (const path of required.filter((item) => !item.endsWith(".pdf"))) {
  const text = await readFile(path, "utf8");
  if (/sk-[A-Za-z0-9_-]{16,}/.test(text)) throw new Error(`possible API key embedded in ${path}`);
}

const index = await readFile("public/index.html", "utf8");
if (!index.includes("Sovereignty Lab") || !index.includes("SOVEREIGNTY_ACCESS_TOKEN")) {
  throw new Error("dashboard authentication/bootstrap UI is incomplete");
}

const api = await readFile("netlify/functions/api.mjs", "utf8");
for (const requirement of ["process.env.DEEPSEEK_API_KEY", "timingSafeEqual", "onlyIfMatch", "consistency: \"strong\""]) {
  if (!api.includes(requirement)) throw new Error(`function security requirement missing: ${requirement}`);
}

const manifest = JSON.parse(await readFile("DEPLOYMENT_MANIFEST.json", "utf8"));
if (manifest.diagnostic_runs !== 120 || manifest.legacy_event_chain_valid !== true) {
  throw new Error("deployment manifest does not identify the verified research seed");
}
if(manifest.integrated_mind?.version!=='13.0.0-alpha.1'||manifest.runtime_build!=='13.0.0-alpha.1')throw new Error('The V13 alpha runtime manifest is missing');
for (const asset of ['/mind.js?v=13.0.0-alpha.1','/workspace10.js?v=13.0.0-alpha.1','/workspace10.css?v=13.0.0-alpha.1','/living13.js?v=13.0.0-alpha.1','/living13.css?v=13.0.0-alpha.1']) {
  if(!index.includes(asset))throw new Error(`The current workspace entrypoint is missing: ${asset}`);
}
const theme = await readFile('public/workspace10.css','utf8');
if(!theme.includes('[data-theme=dark]')||!theme.includes('--panel'))throw new Error('The paired workspace themes are incomplete');
if(!api.includes('/api/mind/stream')||!api.includes('application/x-ndjson'))throw new Error('The live cognition stream is missing');
const mindUi=await readFile('public/mind.js','utf8');
if(!mindUi.includes("streamApi(contact?'chat':'cycle'")||!theme.includes('.studio-live'))throw new Error('The streaming interface is incomplete');

console.log("Netlify deployment bundle verified.");
