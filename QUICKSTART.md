# 🚀 GödelOS Quickstart Guide

GödelOS is an advanced cognitive architecture and tractable self-optimizing operating system implementing the theoretical principles of the **Gödel Machine**, **Proof-Carrying Code (PCC)**, and **Unified Emergent Consciousness**.

---

## ⚡ 1-Command Fast Start

Run the unified bootstrap and verification script:

```bash
chmod +x quickstart.sh
./quickstart.sh
```

This will automatically:
1. Verify system dependencies (Python 3.12+, Node.js 20+).
2. Validate Python syntax across all core modules.
3. Build the Svelte frontend production bundle.
4. Execute the formal verification, adversarial, and TCB test suites (27 tests).
5. Optionally start the unified server and web interface.

---

## 🛠️ Manual Step-by-Step Setup

### Prerequisites
- **Python**: 3.12+
- **Node.js**: 20+ (with `npm`)
- **Memory**: Minimum 4 GB RAM recommended

### 1. Python Environment Setup
```bash
# Clone the repository
git clone https://github.com/Steake/GodelOS.git
cd GodelOS

# Install dependencies
python3 -m pip install -r requirements.txt --break-system-packages
```

### 2. Frontend Build
```bash
cd svelte-frontend
npm install
npm run build
cd ..
```

### 3. Run the Formal Test Suite
Verify that all formal verification kernels, decidable fragment checkers, and adversarial wireheading defenses pass:

```bash
pytest tests/test_godel_machine.py \
       tests/test_godel_tcb_adversarial.py \
       tests/test_godel_tcb_formal_rigor.py \
       tests/test_formal_verification.py -v
```

Expected output: `27 passed in ~1.1s`.

### 4. Start the Services

#### Start the Unified Backend API:
```bash
python3 -m uvicorn backend.unified_server:app --host 0.0.0.0 --port 8000
```

The REST API will be available at `http://localhost:8000`.  
Interactive OpenAPI documentation is at `http://localhost:8000/docs`.

#### Start the Svelte Web Interface:
In a separate terminal:
```bash
cd svelte-frontend
npm run dev -- --host 0.0.0.0 --port 3000
```
Open `http://localhost:3000` in your web browser.

---

## 🖥️ System Interface Overview

When you access the web interface, the following views are available:

### 1. 🌐 Holistic Constellation Dashboard (Default View)
- **Pipeline Topology**: Interactive map tracing data from Ingestion &rarr; Knowledge Graph &rarr; Consciousness &rarr; Symbolic Provers &rarr; Gödel Machine.
- **Stage Inspection**: Click any stage to open deep-dive telemetry drawers.
- **Vital Metrics**: Live system health score, active subsystems count, and TCB security status.

### 2. 🤖 Gödel Machine & TCB Playground
- **Active Self-Model Parameters**: Live display of mutable heuristics, recursion limits, and learning rates.
- **TCB Invariants**: Exact rational arithmetic bounds ($\lambda = 1/20, \beta = 1/2$), Presburger QF-LIA recursion caps, and Lyapunov dissipation checks.
- **Interactive Mutation Sandbox**: Propose candidate rewrites, set conservative bounds, test automatic transactional rollback on simulated runtime crashes, and verify wireheading rejections.
- **Audit Trail**: Full chronological history of certified parameter mutations.

### 3. ⚖️ Symbolic Reasoning Studio
- **First-Order Resolution Refutation**: First-order logic theorem proving with CNF transformation and unification.
- **Modal Tableau Prover**: Modal logics K, T, S4, and S5 for evaluating necessity ($\Box$) and possibility ($\Diamond$).
- **Analogical Reasoning**: Structure-mapping across semantic schemas.

### 4. 🧠 Unified Consciousness & Metacognition
- Real-time monitoring of **Unity of Experience**, **Narrative Coherence**, and **Subjective Presence**.
- Autonomous knowledge acquisition and epistemic gap detection.

---

## 📡 Essential REST API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/v1/godel-machine/status` | `GET` | Surfaces active parameters, TCB weights, and proposer search performance. |
| `/api/v1/godel-machine/verify-and-rewrite` | `POST` | Submits candidate mutation for TCB proof verification and atomic hot-swap. |
| `/api/system/subsystems` | `GET` | Health and activation status across all 23 cognitive subsystems. |
| `/api/v1/consciousness/state` | `GET` | Real-time phenomenal experience qualia and narrative coherence metrics. |
| `/api/knowledge/graph/stats` | `GET` | Long-term knowledge graph node, edge, and ontology consistency stats. |
| `/api/import/jobs` | `GET` | Active document, Wikipedia, and ArXiv ingestion jobs. |

---

## 🧪 Testing Reference

| Test Suite | Purpose | Command |
| :--- | :--- | :--- |
| **Gödel Machine Unit** | Base optimizer, contract checks | `pytest tests/test_godel_machine.py` |
| **TCB Adversarial** | Wireheading, cyclical proofs, overflow, rollback | `pytest tests/test_godel_tcb_adversarial.py` |
| **Formal Rigor** | Rational arithmetic, differential testing, process isolation | `pytest tests/test_godel_tcb_formal_rigor.py` |
| **Formal Verification** | First-order resolution refutation, error contraction | `pytest tests/test_formal_verification.py` |
| **All Formal Suites** | Complete formal system verification | `pytest tests/test_godel* tests/test_formal*` |
