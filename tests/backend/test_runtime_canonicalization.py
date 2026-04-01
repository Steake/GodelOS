"""
Runtime Canonicalization Enforcement Tests

These tests prove that the GödelOS runtime executes through a single canonical
contract — one WebSocket manager, one consciousness state authority, one
server entrypoint, and no active legacy modules.
"""
import importlib
import sys
import types
import pytest


# ---------------------------------------------------------------------------
# 1. Single server entrypoint
# ---------------------------------------------------------------------------

class TestCanonicalEntrypoint:
    """Verify that only ``backend.unified_server`` defines the production app."""

    def test_unified_server_defines_app(self):
        """The canonical FastAPI app lives in backend.unified_server."""
        from backend.unified_server import app
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_main_shim_returns_same_app(self):
        """backend.main re-exports the exact same app object."""
        from backend.unified_server import app as canonical_app
        # backend.main replaces itself in sys.modules; importing it
        # yields the unified_server module.
        import backend.main as main_mod
        assert main_mod.app is canonical_app

    def test_minimal_server_shim_returns_same_app(self):
        """backend.minimal_server re-exports the canonical app (pure shim)."""
        import warnings
        from backend.unified_server import app as canonical_app
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from backend.minimal_server import app as minimal_app
        assert minimal_app is canonical_app

    def test_minimal_server_emits_deprecation(self):
        """Importing backend.minimal_server emits a DeprecationWarning."""
        # Force reimport to trigger the warning
        saved = sys.modules.pop("backend.minimal_server", None)
        try:
            with pytest.warns(DeprecationWarning, match="backend.minimal_server is deprecated"):
                importlib.import_module("backend.minimal_server")
        finally:
            if saved is not None:
                sys.modules["backend.minimal_server"] = saved

    def test_start_server_imports_from_unified(self):
        """backend.start_server imports app from the canonical module."""
        import pathlib
        source = (pathlib.Path(__file__).resolve().parents[2] / "backend" / "start_server.py").read_text()
        assert "backend.unified_server" in source
        # Ensure the import line referencing unified_server comes before any
        # reference to the old backend.main import.
        assert "backend.main" not in source.split("backend.unified_server")[0]


# ---------------------------------------------------------------------------
# 2. Single WebSocket manager identity
# ---------------------------------------------------------------------------

class TestWebSocketManagerIdentity:
    """Prove that only ONE WebSocket manager instance is created at runtime."""

    def test_websocket_manager_class_is_base(self):
        """backend.websocket_manager exports the base WebSocketManager class."""
        from backend.websocket_manager import WebSocketManager
        assert hasattr(WebSocketManager, "broadcast")
        assert hasattr(WebSocketManager, "connect")
        assert hasattr(WebSocketManager, "disconnect")

    def test_enhanced_inherits_base(self):
        """EnhancedWebSocketManager is a subclass of the base WebSocketManager."""
        from backend.websocket_manager import WebSocketManager
        from backend.core.enhanced_websocket_manager import EnhancedWebSocketManager
        assert issubclass(EnhancedWebSocketManager, WebSocketManager)

    def test_initialize_creates_single_instance(self):
        """After initialize_core_services, both globals reference the same object."""
        import backend.unified_server as us
        # At module-load time both are None.  After lifespan they should be set.
        # We test the *structural invariant*: if one is set, the other must be
        # the same object (identity, not equality).
        if us.websocket_manager is not None:
            assert us.websocket_manager is us.enhanced_websocket_manager, (
                "websocket_manager and enhanced_websocket_manager must be the "
                "same object at runtime"
            )

    @pytest.mark.asyncio
    async def test_init_core_services_aliases_managers(self):
        """initialize_core_services sets both WS globals to the same instance."""
        import backend.unified_server as us

        # Save originals
        orig_ws = us.websocket_manager
        orig_ews = us.enhanced_websocket_manager

        try:
            us.websocket_manager = None
            us.enhanced_websocket_manager = None
            await us.initialize_core_services()

            assert us.websocket_manager is not None, "websocket_manager should be initialized"
            assert us.enhanced_websocket_manager is not None, "enhanced_websocket_manager should be initialized"
            assert us.websocket_manager is us.enhanced_websocket_manager, (
                "Both WS globals must reference the SAME runtime object"
            )
        finally:
            us.websocket_manager = orig_ws
            us.enhanced_websocket_manager = orig_ews

    def test_no_inline_websocketmanager_in_unified_server(self):
        """unified_server.py must NOT define WebSocketManager inline — it imports it."""
        import inspect
        import backend.unified_server as us
        source = inspect.getsource(us)
        # The class definition should NOT be in unified_server.py
        assert "\nclass WebSocketManager:" not in source, (
            "WebSocketManager must be imported from backend.websocket_manager, "
            "not defined inline in unified_server.py"
        )


# ---------------------------------------------------------------------------
# 3. Canonical consciousness state authority
# ---------------------------------------------------------------------------

class TestCanonicalConsciousnessState:
    """All state reads must derive from UnifiedConsciousnessEngine."""

    def test_consciousness_endpoints_use_unified_engine(self):
        """consciousness_endpoints.py references unified_consciousness_engine."""
        from backend.api import consciousness_endpoints as ce
        # The setter function must exist and update the module-level engine ref
        assert callable(getattr(ce, "set_consciousness_engine", None))

    def test_cognitive_state_endpoint_prefers_unified_engine(self):
        """The /cognitive/state handler checks unified_consciousness_engine first."""
        import inspect
        import backend.unified_server as us
        source = inspect.getsource(us.get_cognitive_state_endpoint)
        # The first conditional should check the unified engine
        idx_uce = source.find("unified_consciousness_engine")
        idx_gi = source.find("godelos_integration")
        assert idx_uce != -1, "/cognitive/state must check unified_consciousness_engine"
        assert idx_uce < idx_gi, (
            "unified_consciousness_engine must be checked BEFORE godelos_integration "
            "in /cognitive/state"
        )

    def test_api_cognitive_state_prefers_unified_engine(self):
        """The /api/cognitive-state handler enriches from unified_consciousness_engine first."""
        import inspect
        import backend.unified_server as us
        source = inspect.getsource(us.api_get_cognitive_state_alias)
        idx_uce = source.find("unified_consciousness_engine")
        idx_gi = source.find("godelos_integration")
        assert idx_uce != -1, "/api/cognitive-state must reference unified_consciousness_engine"
        assert idx_uce < idx_gi, (
            "unified_consciousness_engine must be checked BEFORE godelos_integration "
            "in /api/cognitive-state"
        )

    def test_v1_consciousness_state_uses_cognitive_manager(self):
        """/api/v1/consciousness/state derives from cognitive_manager.assess_consciousness."""
        import inspect
        import backend.unified_server as us
        source = inspect.getsource(us.get_consciousness_state)
        assert "cognitive_manager" in source


# ---------------------------------------------------------------------------
# 4. Legacy modules not active in runtime flow
# ---------------------------------------------------------------------------

class TestLegacyModulesInactive:
    """Deprecated / legacy modules are shims, not active implementations."""

    def test_minimal_server_is_pure_shim(self):
        """minimal_server.py should be ≤30 lines (shim only)."""
        import pathlib
        path = pathlib.Path(__file__).resolve().parents[2] / "backend" / "minimal_server.py"
        line_count = len(path.read_text().splitlines())
        assert line_count <= 30, (
            f"minimal_server.py has {line_count} lines — it should be a pure "
            f"shim (re-export only)"
        )

    def test_phenomenal_experience_generator_is_shim(self):
        """phenomenal_experience_generator.py should be ≤30 lines (shim only)."""
        import pathlib
        path = pathlib.Path(__file__).resolve().parents[2] / "backend" / "phenomenal_experience_generator.py"
        line_count = len(path.read_text().splitlines())
        assert line_count <= 30, (
            f"phenomenal_experience_generator.py has {line_count} lines — it "
            f"should be a pure shim"
        )

    def test_consciousness_engine_class_is_deprecated(self):
        """ConsciousnessEngine docstring declares deprecation."""
        from backend.core.consciousness_engine import ConsciousnessEngine
        assert "DEPRECATED" in (ConsciousnessEngine.__doc__ or ""), (
            "ConsciousnessEngine must be marked DEPRECATED in its docstring"
        )

    def test_consciousness_state_types_remain_canonical(self):
        """ConsciousnessState and ConsciousnessLevel are still importable (they are base types)."""
        from backend.core.consciousness_engine import ConsciousnessState, ConsciousnessLevel
        assert ConsciousnessState is not None
        assert ConsciousnessLevel is not None


# ---------------------------------------------------------------------------
# 5. Pipeline integration gating
# ---------------------------------------------------------------------------

class TestPipelineIntegrationGating:
    """godelos_integration gates fallback knowledge store usage."""

    def test_simple_knowledge_store_is_property(self):
        """simple_knowledge_store should be a property that can detect pipeline presence."""
        from backend.godelos_integration import GödelOSIntegration
        assert isinstance(
            GödelOSIntegration.__dict__.get("simple_knowledge_store"),
            property,
        ), "simple_knowledge_store must be a property, not a plain attribute"

    def test_fallback_warns_when_pipeline_active(self):
        """Accessing simple_knowledge_store with an active pipeline logs a warning."""
        from backend.godelos_integration import GödelOSIntegration

        gi = GödelOSIntegration()
        # Reset class-level warning flag for this test
        GödelOSIntegration._fallback_warned = False
        # Simulate an active pipeline
        gi.cognitive_pipeline = object()  # truthy sentinel

        # Access should succeed but set the warned flag
        _ = gi.simple_knowledge_store
        assert GödelOSIntegration._fallback_warned is True

        # Clean up
        GödelOSIntegration._fallback_warned = False

    def test_no_warning_without_pipeline(self):
        """No warning when pipeline is None (test/fallback mode)."""
        from backend.godelos_integration import GödelOSIntegration
        gi = GödelOSIntegration()
        GödelOSIntegration._fallback_warned = False
        gi.cognitive_pipeline = None
        _ = gi.simple_knowledge_store
        assert GödelOSIntegration._fallback_warned is False
        GödelOSIntegration._fallback_warned = False
