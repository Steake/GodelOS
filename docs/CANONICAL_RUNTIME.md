# GödelOS Canonical Runtime Architecture

> **Single source of truth for server startup, WebSocket management,
> consciousness state computation, and cognitive pipeline integration.**
>
> Enforced by `tests/backend/test_runtime_canonicalization.py` (21 tests).

---

## 1. Single Runtime Entrypoint

| Module | Status | Purpose |
|--------|--------|---------|
| `backend/unified_server.py` | **CANONICAL** | The one and only FastAPI application. All startup scripts, CI workflows, and deployment targets must use this module. |
| `backend/main.py` | Compatibility shim | Re-exports `unified_server` into `sys.modules["backend.main"]` so that legacy test imports (`from backend.main import app`) continue to work. Returns the **same** `app` object. |
| `backend/start_server.py` | CLI wrapper | Imports `app` from `backend.unified_server` and wraps it in a `GödelOSServer` class for signal handling. |
| `backend/minimal_server.py` | **DEPRECATED (pure shim)** | 24-line shim that re-exports `unified_server.app`. Emits `DeprecationWarning` on import. Will be removed in a future release. |

### Startup Commands

```bash
# Recommended (both backend + frontend)
./start-godelos.sh --dev

# Backend only
python backend/unified_server.py
# or
uvicorn backend.unified_server:app --reload --port 8000
```

---

## 2. WebSocket Manager

| Class | Module | Status |
|-------|--------|--------|
| `WebSocketManager` | `backend/websocket_manager.py` | Base class — connect/disconnect/broadcast primitives. |
| `EnhancedWebSocketManager` | `backend/core/enhanced_websocket_manager.py` | **CANONICAL runtime manager**. Extends `WebSocketManager` with consciousness streaming, emergence alerts, and recursive-awareness feeds. |

At runtime, **both** `websocket_manager` and `enhanced_websocket_manager` globals
in `unified_server.py` reference the **same** `EnhancedWebSocketManager` instance.
This is verified by `test_init_core_services_aliases_managers`.

### Contract

All outbound WebSocket messages conform to one of these event schemas:

```jsonc
{ "type": "cognitive_event",            "timestamp": ..., "data": {...} }
{ "type": "consciousness_update",       "timestamp": ..., "data": {...} }
{ "type": "consciousness_emergence",    "timestamp": ..., ... }
{ "type": "consciousness_breakthrough", "timestamp": ..., "alert_level": "CRITICAL", ... }
```

---

## 3. Consciousness State

| Component | Module | Status |
|-----------|--------|--------|
| `UnifiedConsciousnessEngine` | `backend/core/unified_consciousness_engine.py` | **CANONICAL** — recursive self-awareness loop, IIT φ, global workspace, phenomenal experience, metacognition. |
| `ConsciousnessEngine` | `backend/core/consciousness_engine.py` | **DEPRECATED class**. The `ConsciousnessState` and `ConsciousnessLevel` data types remain canonical. |
| `ConsciousnessEmergenceDetector` | `backend/core/consciousness_emergence_detector.py` | Active — rolling-window breakthrough scorer. |
| `PhenomenalExperienceGenerator` (core) | `backend/core/phenomenal_experience.py` | **Active** — qualia & subjective-experience simulation used internally by `UnifiedConsciousnessEngine`. |
| `PhenomenalExperienceGenerator` (legacy) | `backend/phenomenal_experience_generator.py` | **DEPRECATED (pure shim)** — 23-line re-export. Emits `DeprecationWarning`. |

### State Read Resolution Order

All consciousness/cognitive-state endpoints follow this priority:

1. **`unified_consciousness_engine`** — authoritative IIT φ, global workspace, recursive awareness
2. **`cognitive_manager.assess_consciousness()`** — assessment backed by `ConsciousnessEngine` + LLM driver
3. **`godelos_integration.get_cognitive_state()`** — pipeline-backed cognitive metrics
4. **Static fallback** — test-only stub (logs warning when served)

Endpoint mapping:
- `/cognitive/state`, `/api/cognitive/state` → resolution order above
- `/api/cognitive-state` → enriches manifest consciousness from `unified_consciousness_engine` first
- `/api/v1/consciousness/state` → `cognitive_manager.assess_consciousness()`
- `/api/consciousness/state` → `unified_consciousness_engine.consciousness_state` (via router)

---

## 4. Cognitive Pipeline Integration

All cognitive processing flows through `godelOS/cognitive_pipeline.py`
(`CognitivePipeline` class).

`backend/godelos_integration.py` wraps the pipeline with graceful degradation.
The `simple_knowledge_store` is a **gated test-only stub**: accessing it when
`CognitivePipeline` is active emits a runtime warning. This is enforced by
`test_fallback_warns_when_pipeline_active`.

---

## 5. Remaining Technical Debt

- [ ] Remove `backend/minimal_server.py` shim once confirmed no external tooling references it.
- [ ] Remove `backend/phenomenal_experience_generator.py` shim once confirmed unused.
- [ ] Merge `ConsciousnessEngine` base types into `unified_consciousness_engine.py` to eliminate import indirection.
- [ ] Contract-test all outbound WebSocket event schemas in CI.
- [ ] Replace mock health scores in `get_system_health_with_labels()` with real service probes.
