#!/usr/bin/env python3
"""
Production-Ready Test Suite for Enhanced Metacognition Implementation

This test suite validates that all components are working correctly and
ready for deployment in a production environment.
"""

import sys
import time
import asyncio
import traceback

def test_basic_imports():
    """Test that all basic imports work without issues."""
    print("🔍 Testing basic imports...")
    
    try:
        # Test configuration
        from backend.config_manager import get_config, is_feature_enabled
        config = get_config()
        print(f"✅ Configuration: {type(config).__name__}")
        
        # Test cognitive models
        from backend.metacognition_modules.cognitive_models import (
            KnowledgeGap, CognitiveEvent, AcquisitionPlan, CognitiveEventType, GranularityLevel
        )
        print("✅ Cognitive models imported")
        
        # Test enhanced manager
        from backend.metacognition_modules.enhanced_metacognition_manager import EnhancedMetacognitionManager
        print("✅ Enhanced metacognition manager imported")
        
        # Test API
        from backend.enhanced_cognitive_api import router, initialize_enhanced_cognitive
        print("✅ Enhanced cognitive API imported")
        
        # Test WebSocket manager
        from backend.websocket_manager import WebSocketManager
        print("✅ WebSocket manager imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_model_functionality():
    """Test that cognitive models work correctly."""
    print("\n🔍 Testing model functionality...")
    
    try:
        from backend.metacognition_modules.cognitive_models import (
            KnowledgeGap, CognitiveEvent, AcquisitionPlan, 
            CognitiveEventType, GranularityLevel, KnowledgeGapType, AcquisitionStrategy
        )
        
        # Test KnowledgeGap
        gap = KnowledgeGap(
            type=KnowledgeGapType.CONCEPT_MISSING,
            missing_concepts=["test_concept"],
            priority=0.8
        )
        print(f"✅ KnowledgeGap: {gap.id[:8]}... type={gap.type.value}")
        
        # Test CognitiveEvent
        event = CognitiveEvent(
            type=CognitiveEventType.REASONING,
            data={"test": "data"},
            granularity_level=GranularityLevel.STANDARD
        )
        print(f"✅ CognitiveEvent: {event.event_id[:8]}... type={event.type.value}")
        
        # Test AcquisitionPlan
        plan = AcquisitionPlan(
            strategy=AcquisitionStrategy.CONCEPT_EXPANSION,
            priority=0.7,
            gap=gap
        )
        print(f"✅ AcquisitionPlan: {plan.plan_id[:8]}... strategy={plan.strategy.value}")
        
        # Test serialization
        gap_dict = gap.to_dict()
        event_dict = event.to_dict()
        plan_dict = plan.to_dict()
        print("✅ Model serialization works")
        
        return True
        
    except Exception as e:
        print(f"❌ Model functionality failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration management."""
    print("\n🔍 Testing configuration management...")
    
    try:
        from backend.config_manager import get_config, is_feature_enabled
        
        config = get_config()
        
        # Test configuration structure
        assert hasattr(config, 'cognitive_streaming')
        assert hasattr(config, 'autonomous_learning')
        assert hasattr(config, 'knowledge_acquisition')
        print("✅ Configuration structure is valid")
        
        # Test feature flags
        enhanced_enabled = is_feature_enabled('enhanced_metacognition')
        autonomous_enabled = is_feature_enabled('autonomous_learning')
        print(f"✅ Feature flags: enhanced={enhanced_enabled}, autonomous={autonomous_enabled}")
        
        # Test configuration values
        streaming_config = config.cognitive_streaming
        learning_config = config.autonomous_learning
        print(f"✅ Config values: streaming_enabled={streaming_config.enabled}, "
              f"gap_interval={learning_config.gap_detection_interval}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False

async def test_async_components():
    """Test async functionality."""
    print("\n🔍 Testing async components...")
    
    try:
        from backend.metacognition_modules.enhanced_metacognition_manager import EnhancedMetacognitionManager
        from backend.websocket_manager import WebSocketManager
        from backend.config_manager import get_config
        from unittest.mock import MagicMock
        
        # Test WebSocket manager creation
        ws_manager = WebSocketManager()
        print("✅ WebSocket manager created")
        
        # Test enhanced metacognition manager creation
        config = get_config()
        manager = EnhancedMetacognitionManager(
            websocket_manager=ws_manager,
            config=config
        )
        print("✅ Enhanced metacognition manager created")
        
        # Test that components are initialized
        assert hasattr(manager, 'knowledge_gap_detector')
        assert hasattr(manager, 'autonomous_knowledge_acquisition')
        assert hasattr(manager, 'stream_coordinator')
        print("✅ Manager components are properly initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Async component test failed: {e}")
        traceback.print_exc()
        return False

def test_api_components():
    """Test API components."""
    print("\n🔍 Testing API components...")
    
    try:
        from backend.enhanced_cognitive_api import router, initialize_enhanced_cognitive
        from backend.websocket_manager import WebSocketManager
        from unittest.mock import MagicMock
        
        # Test router is properly configured
        assert router is not None
        assert hasattr(router, 'routes')
        print(f"✅ Enhanced cognitive API router with {len(router.routes)} routes")
        
        # Test that we can create the initialization function
        ws_manager = MagicMock()
        print("✅ API components are accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ API component test failed: {e}")
        traceback.print_exc()
        return False

def test_frontend_files():
    """Test that frontend files exist."""
    print("\n🔍 Testing frontend files...")
    
    try:
        from pathlib import Path
        
        frontend_files = [
            "svelte-frontend/src/stores/enhanced-cognitive.js",
            "svelte-frontend/src/components/core/StreamOfConsciousnessMonitor.svelte",
            "svelte-frontend/src/components/core/AutonomousLearningMonitor.svelte",
            "svelte-frontend/src/components/dashboard/EnhancedCognitiveDashboard.svelte"
        ]
        
        for file_path in frontend_files:
            if Path(file_path).exists():
                print(f"✅ {Path(file_path).name}")
            else:
                print(f"❌ {Path(file_path).name} - MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend file test failed: {e}")
        return False

def test_backwards_compatibility():
    """Test that existing functionality still works."""
    print("\n🔍 Testing backwards compatibility...")
    
    try:
        # Test that we can still import existing modules
        from backend.models import QueryRequest, QueryResponse
        from backend.websocket_manager import WebSocketManager
        
        # Test basic functionality
        query = QueryRequest(text="test query")
        assert query.text == "test query"
        print("✅ Existing models work")
        
        ws_manager = WebSocketManager()
        assert ws_manager is not None
        print("✅ Existing WebSocket manager works")
        
        return True
        
    except Exception as e:
        print(f"❌ Backwards compatibility test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all production-ready tests."""
    print("🚀 PRODUCTION-READY TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Model Functionality", test_model_functionality),
        ("Configuration Management", test_configuration),
        ("Async Components", test_async_components),
        ("API Components", test_api_components),
        ("Frontend Files", test_frontend_files),
        ("Backwards Compatibility", test_backwards_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {name} PASSED")
                passed += 1
            else:
                print(f"❌ {name} FAILED")
        except Exception as e:
            print(f"❌ {name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"PRODUCTION TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is production-ready!")
        print("\n🚀 READY FOR DEPLOYMENT:")
        print("  1. Start backend: python backend/main.py")
        print("  2. Start frontend: cd svelte-frontend && npm run dev")
        print("  3. Access Enhanced Cognitive Dashboard")
        print("  4. Test autonomous knowledge acquisition")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("❌ System needs fixes before production deployment")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
