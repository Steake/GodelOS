# GödelOS: Comprehensive UI/UX Audit & Ground-Up Redesign Master Plan

**Document Version:** 1.0.0  
**Status:** Approved Architectural Blueprint (Pre-Implementation)  
**Target Application:** GödelOS v0.3 Core Interface  

---

## 1. Foundational Premises & First Principles

### 1.1 What GödelOS Actually Is
GödelOS is an open, self-reflective, neuro-symbolic cognitive architecture. It is **not** a basic chatbot, nor is it a passive telemetry dashboard. Its distinct value proposition lies in four complementary pillars:

1. **Formal Deductive Rigor (Symbolic Engine)**: Guaranteed sound reasoning through first-order resolution refutation, modal logic tableau checking, constraint logic programming (CLP), and structural analogy mapping.
2. **Empirical Semantic Memory (Knowledge Store)**: Hybrid memory uniting high-dimensional vector embeddings with a structured knowledge graph of typed entities, relations, and fact provenance.
3. **Certified Self-Improvement (Gödel Machine & TCB)**: A self-reflective runtime capable of modifying its own heuristics, execution algorithms, and parameters, guarded by a non-negotiable Trusted Computing Base (TCB) that requires formal proof of utility before applying any mutation.
4. **Metacognitive Continuity (Consciousness Stream)**: Continuous self-monitoring that models attention intensity, informational integration ($\Phi$), prediction surprise, and autonomous goal synthesis.

### 1.2 The Root Cause of Current UI Failure
The current UI fails because it treats the user as an **observer watching simulated telemetry meters**, rather than an **operator conducting interactive cognitive work**:
- **Output-poor**: Queries return synthetic strings about consciousness levels instead of answering questions or presenting formal deductions.
- **Dead ends**: Knowledge graph displays a blank error if no documents are uploaded, with no guidance or sample data.
- **Disconnected systems**: Theorem provers and self-modification sandboxes are buried in nested sub-menus, completely severed from the chat and knowledge base.
- **Silent failure on missing LLM**: Without an LLM connected, the system silently degrades into static template strings without explaining the situation or offering a way to configure a model.

---

## 2. Exhaustive UI Component & Application Layer Audit

| Component & Path | Claimed Feature | Actual Behavior / Failure Mode | Technical Root Cause |
| :--- | :--- | :--- | :--- |
| **`App.svelte`** | System shell & navigation | Spawns 13+ fragmented tabs across 4 categories. Default view (`holistic`) dumps 20+ charts simultaneously with no actionable workflow. | Lack of information hierarchy. Views were created as isolated test pages rather than unified workspaces. |
| **`QueryInterface.svelte`** | Natural language reasoning | Submits query; displays canned narrative: *"I am processing your query while being aware that I am processing it..."* | No LLM provider is connected. Calls `/api/enhanced-cognitive/query` which drops into `_generate_conscious_response` template string generator. |
| **LLM Configuration (Absent)** | Model connectivity | **Completely absent from UI.** Zero ability to enter API keys, select providers, or connect to local Ollama. | Backend expects static environment variables (`OPENAI_API_KEY`) at server boot; frontend has no API or UI to configure models dynamically. |
| **`KnowledgeGraph.svelte`** (3,632 lines) | 2D/3D semantic knowledge visualization | Renders blank dark canvas with *"No knowledge data available"*. Fails to render if no documents imported. | No empty state handling. No "Load Sample Ontology" action. Graph component does not allow creating nodes or edges manually. |
| **`SmartImport.svelte`** | Document ingestion (PDF, URL, Text) | Ingestion jobs queue and process, but results are disconnected from the knowledge graph. Extracted triples are never shown in an editable/inspectable view. | Ingestion WebSocket (`/api/knowledge/import/progress/stream`) updates progress bars but does not trigger reactive graph reload. |
| **`SymbolicReasoningStudio.svelte`** | Theorem proving & modal logic | Hidden in sub-sub-menu. Requires raw formula strings. Output is a raw JSON payload with no visual refutation tree. | Developed as an internal test harness rather than an interactive proof workbench. |
| **`UnifiedConsciousnessDashboard.svelte`** | Emergence & consciousness monitoring | Emits persistent JavaScript errors in console. Reconnects to dead WebSocket endpoints every 3 seconds. | Connects to `/api/consciousness/stream` and `/api/consciousness/emergence` which do not exist. Active backend WebSocket is `/ws/unified-cognitive-stream`. |
| **`HumanInteractionPanel.svelte`** | Direct dialog & interaction metrics | Shows redundant chat box that shares state with QueryInterface, creating race conditions and duplicate logs. | Legacy duplicate of QueryInterface that was never consolidated. |
| **`CapabilityDashboard.svelte`** | Cognitive capability tracking | Static progress bars showing hardcoded percentages (85% Analogical, 65% Integration) with no live evaluation. | Frontend store reads hardcoded initial state; backend has no dynamic capability benchmarking endpoint. |

---

## 3. Backend Readiness & Integration Matrix

To support the ground-up redesign, all frontend actions must map to solid, non-facade backend endpoints:

| Functional Area | Backend Endpoint | Method | Backend Readiness | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **LLM Provider Hub** | `/api/v1/llm/status`<br>`/api/v1/llm/configure` | `GET`<br>`POST` | ⚠️ Missing | **Build Endpoint**: Add dynamic provider configuration router supporting OpenAI, Anthropic, Ollama, and local endpoints. |
| **Interactive Query** | `/api/enhanced-cognitive/query` | `POST` | ✅ Live | **Enhance**: Add flag `use_symbolic_verifier: bool`. When LLM is absent, route to pure symbolic resolution solver. |
| **Consciousness Stream** | `/ws/unified-cognitive-stream` | `WS` | ✅ Live | **Consolidate**: Direct all frontend WebSocket telemetry to this single unified stream. |
| **Knowledge Ingestion** | `/api/knowledge/pipeline/process` | `POST` | ✅ Live | **Bridge**: Return extracted entity/relation summary directly in HTTP response for instant UI confirmation. |
| **Graph Topology** | `/api/knowledge/pipeline/graph` | `GET` | ✅ Live | **Enhance**: Add `/api/knowledge/seed-sample` endpoint to populate initial ontology on first run. |
| **Theorem Proving** | `/api/v1/symbolic/prove` | `POST` | ✅ Live | **Refine**: Return structured step-by-step resolution clauses with unification substitutions for graphical proof tree. |
| **Modal Logic** | `/api/v1/symbolic/modal-check` | `POST` | ✅ Live | ✅ Fully operational (Tableau tree and frame accessibility checks). |
| **Constraint Logic** | `/api/v1/symbolic/clp-solve` | `POST` | ✅ Live | ✅ Fully operational (linear constraints and simplex solver). |
| **Analogical Reasoning**| `/api/v1/symbolic/analogy` | `POST` | ✅ Live | ✅ Fully operational (SME structural mapping engine). |
| **Gödel Machine Status**| `/api/v1/godel-machine/status` | `GET` | ✅ Live | ✅ Fully operational (active parameters, rewrite history). |
| **Gödel Mutation** | `/api/v1/godel-machine/verify-and-rewrite` | `POST` | ✅ Live | ✅ Fully operational (TCB invariant checking, rollback trial). |

---

## 4. The Top-Level LLM Hub Architecture

### 4.1 The Top-Level Status Indicator
In the persistent top navigation bar of GödelOS, an interactive **Model Indicator Pill** is always visible:
- **`[🟢 OpenAI: gpt-4o]`**: API key verified, live neural synthesis active.
- **`[🟡 Ollama: llama3.1 (Local)]`**: Local inference active on `localhost:11434`.
- **`[🔴 Pure Symbolic Mode (Offline)]`**: No LLM connected. Neuro-symbolic features disabled; pure first-order resolution and modal logic reasoning active.

### 4.2 Dynamic Provider Control Drawer
Clicking the Model Indicator opens the **LLM Configuration Drawer**:
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🧠 Cognitive Model & LLM Provider Configuration                        │
├────────────────────────────────────────────────────────────────────────┤
│ Active Provider: [● OpenAI]  [○ Anthropic]  [○ Ollama (Local)]  [○ None]│
│                                                                        │
│ • Base URL:      [http://localhost:11434                    ]          │
│ • API Key:       [sk-proj-••••••••••••••••••••••••••••••••  ]          │
│ • Model Name:    [gpt-4o                                    ]          │
│ • Temperature:   [===|=========] 0.20                                  │
│ • Timeout (sec): [30s          ]                                       │
│                                                                        │
│ [ Test Connection ] ──> ✅ Connected | Latency: 38ms | Models: 12      │
│                                                                        │
│ Offline Fallback Strategy:                                             │
│ ☑ Fall back to Pure Symbolic Resolution Prover when offline             │
│ ☑ Strip conversational pleasantries and return formal proofs only      │
│                                                                        │
│                    [ Save & Activate Runtime Driver ]                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. User Personas & Closed-Loop User Flows

### Flow 1: Neuro-Symbolic Query & Verified Proof Verification
```
User Prompt: "Verify if Socrates is mortal if all humans are mortal and Socrates is human."
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 1. Cognitive Studio Input: Query Dispatched            │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 2. Backend Orchestration                               │
      │    - If LLM Active: Semantic parsing extracts:         │
      │      Premises: ["Human(socrates)", "Human(x) -> Mortal(x)"]│
      │      Goal: "Mortal(socrates)"                        │
      │    - If LLM Offline: Formal Logic Parser parses input  │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 3. Automated Resolution Refutation Engine              │
      │    - Negates goal: ~Mortal(socrates)                   │
      │    - Unifies clauses via MGU: {x/socrates}             │
      │    - Derives empty clause: Box (contradiction found)   │
      │    - Output: Proof valid in 2 steps                    │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 4. Interactive UI Display                              │
      │    - Plain-language verified answer                    │
      │    - Verification Chip: [Formal Proof: 100% Sound]     │
      │    - Expandable Refutation Tree visualizer             │
      │    - One-click [Save Rule to Knowledge Graph]          │
      └────────────────────────────────────────────────────────┘
```

### Flow 2: Document Ingestion to Knowledge Discovery
```
User Action: Drag & drop "neurosymbolic_ai.pdf" or enter URL
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 1. Multi-Stage Ingestion Pipeline (Live Progress Bar)  │
      │    • Parsing & Cleaning Text: 100%                     │
      │    • spaCy Entity Extraction: 38 entities found        │
      │    • Relation Extraction: 54 triples extracted         │
      │    • Embedding Generation: 384-dim MiniLM vectors      │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 2. Extracted Triples Verification Table                │
      │    User reviews extracted knowledge before committing: │
      │    [x] (Deep Learning) ──[lacks]──> (Sound Reasoning)  │
      │    [x] (GödelOS) ──[integrates]──> (Symbolic Logic)    │
      │    [Commit to Graph]                                   │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 3. Immediate Interactive Visualizer                    │
      │    - Graph camera automatically animates to new nodes  │
      │    - Search bar enables querying new entities instantly│
      └────────────────────────────────────────────────────────┘
```

### Flow 3: Gödel Machine Certified Code Rewrite & Rollback
```
User Action: Select parameter "resolution_heuristic" in Gödel Studio
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 1. Proposal Form Formulation                           │
      │    - Parameter: resolution_heuristic                   │
      │    - Current Value: fifo                               │
      │    - Proposed Value: set_of_support_with_unit_pref     │
      │    - Expected Reward Delta: +0.25                      │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 2. TCB Formal Verification & Canary Execution          │
      │    - TCB loads utility axioms & safety invariants      │
      │    - Verifies non-wireheading condition                │
      │    - Runs benchmark proof suite with proposed heuristic│
      │    - Result: 24% faster refutation, 0 invariant breaks │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ 3. Certified Application & Cryptographic Audit Ledger │
      │    - Mutation applied live to active runtime           │
      │    - New snapshot hash generated in ledger             │
      │    - Instant [Rollback Mutation] button available      │
      └────────────────────────────────────────────────────────┘
```

---

## 6. The 4 Unified Studios (Complete UI/UX Specification)

Instead of 13 fragmented tabs, GödelOS will be consolidated into **4 Purpose-Built Studios**:

### Studio 1: Cognitive Studio (`/chat`)
- **Primary Function**: Natural language interaction, verified deductive problem solving, and real-time thought stream inspection.
- **Left Column (Chat Thread, 65% width)**:
  - Rich Markdown, syntax-highlighted code blocks, and LaTeX formulas.
  - Interactive **Proof Cards**: Embedded cards showing verification status, proof steps, and confidence scores.
  - Multi-line input bar with quick switches for `[Formal Verification]`, `[Metacognitive Reflection]`, and `[Search Memory]`.
- **Right Column (Cognitive Inspector, 35% width)**:
  - **Tab 1: Provenance & Logic**: Step-by-step resolution derivation for the active message.
  - **Tab 2: Consciousness Radar**: Real-time chart displaying attention focus, information integration ($\Phi$), and narrative qualia.
  - **Tab 3: Autonomous Goals**: Active self-generated subgoals and cognitive load metrics.

### Studio 2: Knowledge Studio (`/knowledge`)
- **Primary Function**: Ingesting, organizing, inspecting, and querying empirical knowledge.
- **Top Action Bar**:
  - Unified search box with hybrid mode toggles (`Semantic Vector Search` vs `Graph Keyword`).
  - `[+ Import Document / URL]` button opening an inline ingestion panel.
  - `[🌱 Seed Sample Ontology]` button populating classical logic and philosophy of mind concepts for immediate first-time exploration.
- **Main Canvas (70% width)**:
  - High-performance 2D/3D force-directed graph with physics controls, ontology clustering, and edge filtering.
- **Inspector Drawer (30% width)**:
  - Selected concept metadata, connected relationships, confidence metrics, and source citations.
  - Action buttons: `[Query in Chat]`, `[Find Analogies]`, `[Edit Fact]`.

### Studio 3: Formal Reasoning Studio (`/reasoning`)
- **Primary Function**: Rigorous symbolic logic theorem proving and constraint solving.
- **Top Sub-Navigation**: `First-Order Resolution` | `Modal Logic Tableau` | `CLP Constraint Solver` | `Analogical Engine`.
- **Left Panel (Premise & Goal Editor)**:
  - Pre-built theorem presets (*Barber Paradox*, *Socrates Mortality*, *Transitivity of Implication*, *Modal Axiom T*).
  - Formula editor with real-time logic syntax validation.
- **Right Panel (Graphical Proof Tree Canvas)**:
  - Visual refutation tree showing clause resolutions, Most General Unifiers (MGU), and derivation of the empty clause $\Box$.
  - Export options: `[Export LaTeX Proof]`, `[Download JSON Certificate]`.

### Studio 4: Gödel Machine & Core Studio (`/godel`)
- **Primary Function**: Self-modification governance, TCB safety proofs, and emergence telemetry.
- **Section 1: Interactive Self-Rewrite Workbench**:
  - Live parameter mutation form with estimated compute reduction and utility delta calculation.
  - Benchmark sandbox execution before applying mutations.
- **Section 2: TCB Safety Invariant Ledger**:
  - Real-time verification of immutable utility weights and anti-wireheading safety axioms.
- **Section 3: Mutation History & Rollback Table**:
  - Cryptographically ordered record of all executed self-rewrites with instant 1-click snapshot rollback.

---

## 7. Phased Implementation Roadmap

```
Phase 1: Foundation, App Shell & Top-Level LLM Hub
  ├── Clean up App.svelte navigation to 4 Core Studios
  ├── Implement persistent Header with Model Indicator Pill
  ├── Create backend /api/v1/llm/configure and /api/v1/llm/status endpoints
  └── Build LLM Configuration Drawer with latency tester & fallback controls

Phase 2: Cognitive Studio & Chat Interface
  ├── Redesign ChatInterface with Markdown, LaTeX, and Proof Cards
  ├── Build Cognitive Inspector Drawer (Logic, Consciousness Radar, Goals)
  └── Implement pure symbolic fallback mode when LLM is inactive

Phase 3: Knowledge Studio & Graph Integration
  ├── Overhaul KnowledgeGraph with onboarding empty-state & "Seed" action
  ├── Integrate SmartImport directly into the Knowledge Studio drawer
  └── Connect hybrid semantic search and fact editor

Phase 4: Formal Reasoning Studio
  ├── Build visual resolution refutation tree canvas
  ├── Connect Modal Logic Tableau, CLP Solver, and Analogy Engine
  └── Implement pre-built logic presets and proof certificate exporter

Phase 5: Gödel Machine & Self-Modification Studio
  ├── Build interactive mutation workbench with live sandbox trial
  ├── Implement TCB safety invariant audit ledger
  └── Add 1-click snapshot rollback functionality

Phase 6: End-to-End Validation & Polish
  ├── Verify all WebSocket telemetry routes through /ws/unified-cognitive-stream
  ├── Execute end-to-end integration tests across all 4 studios
  └── Validate complete user journeys without dead ends
```
