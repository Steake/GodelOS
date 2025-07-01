#!/usr/bin/env python3
"""
Post-Fix Validation - Confirm Enhanced Metacognition is Working

This test validates that all the fixes have been applied correctly and
the enhanced metacognition system is ready for deployment.
"""

def main():
    print("🔧 POST-FIX VALIDATION")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Import components
    total_tests += 1
    try:
        from backend.metacognition_modules.enhanced_metacognition_manager import EnhancedMetacognitionManager
        from backend.websocket_manager import WebSocketManager
        from backend.config_manager import get_config
        print("✅ Test 1: All components import successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Import failed: {e}")
    
    # Test 2: Create manager with is_initialized attribute
    total_tests += 1
    try:
        ws_manager = WebSocketManager()
        config = get_config()
        manager = EnhancedMetacognitionManager(websocket_manager=ws_manager, config=config)
        
        # Check critical attributes
        assert hasattr(manager, 'is_initialized'), "Missing is_initialized attribute"
        assert manager.is_initialized == False, "is_initialized should start as False"
        assert hasattr(manager, 'godelos_integration'), "Missing godelos_integration attribute"
        
        print("✅ Test 2: Manager created with correct attributes")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: Manager creation failed: {e}")
    
    # Test 3: Initialize method signature
    total_tests += 1
    try:
        import inspect
        init_method = getattr(manager, 'initialize')
        sig = inspect.signature(init_method)
        params = list(sig.parameters.keys())
        
        # Should accept optional godelos_integration parameter
        assert 'godelos_integration' in params, "initialize method missing godelos_integration parameter"
        
        print("✅ Test 3: Initialize method has correct signature")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Initialize method check failed: {e}")
    
    # Test 4: Cognitive models work
    total_tests += 1
    try:
        from backend.metacognition_modules.cognitive_models import KnowledgeGap, CognitiveEvent
        gap = KnowledgeGap()
        event = CognitiveEvent(type="reasoning")
        
        assert hasattr(gap, 'detected_at'), "KnowledgeGap missing detected_at attribute"
        assert hasattr(event, 'event_id'), "CognitiveEvent missing event_id attribute"
        
        print("✅ Test 4: Cognitive models work correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: Cognitive models failed: {e}")
    
    # Test 5: API integration can be imported
    total_tests += 1
    try:
        from backend.enhanced_cognitive_api import initialize_enhanced_cognitive, router
        assert callable(initialize_enhanced_cognitive), "initialize_enhanced_cognitive not callable"
        assert hasattr(router, 'routes'), "Router missing routes"
        
        print("✅ Test 5: API integration imports correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5: API integration failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"VALIDATION RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL POST-FIX VALIDATION TESTS PASSED!")
        print("✅ Enhanced metacognition is ready for deployment")
        print("\n🚀 NEXT STEPS:")
        print("  1. Start backend: python backend/main.py")
        print("  2. Backend should start without initialization errors")
        print("  3. Enhanced cognitive endpoints should be available")
        print("  4. Test autonomous knowledge acquisition features")
    else:
        print(f"⚠️ {total_tests - tests_passed} validation tests failed")
        print("❌ Additional fixes may be needed")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
