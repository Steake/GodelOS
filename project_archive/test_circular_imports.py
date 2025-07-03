#!/usr/bin/env python3
"""
Circular Import Dependency Test

Tests that the circular import issue has been resolved.
"""

import sys
import time

def test_imports():
    """Test that all imports work without circular dependencies."""
    print("🔍 Testing circular import resolution...")
    
    try:
        print("1. Testing WebSocket manager import...")
        start_time = time.time()
        from backend.websocket_manager import WebSocketManager
        elapsed = time.time() - start_time
        print(f"✅ WebSocket manager imported in {elapsed:.2f}s")
        
        print("2. Testing cognitive models import...")
        start_time = time.time()
        from backend.metacognition_modules.cognitive_models import KnowledgeGap, CognitiveEvent
        elapsed = time.time() - start_time
        print(f"✅ Cognitive models imported in {elapsed:.2f}s")
        
        print("3. Testing config manager import...")
        start_time = time.time()
        from backend.config_manager import get_config
        elapsed = time.time() - start_time
        print(f"✅ Config manager imported in {elapsed:.2f}s")
        
        print("4. Testing enhanced cognitive API import...")
        start_time = time.time()
        from backend.enhanced_cognitive_api import router
        elapsed = time.time() - start_time
        print(f"✅ Enhanced cognitive API imported in {elapsed:.2f}s")
        
        print("5. Testing model creation...")
        gap = KnowledgeGap()
        event = CognitiveEvent(type="reasoning")
        print(f"✅ Models created: gap={gap.id[:8]}..., event={event.event_id[:8]}...")
        
        print("6. Testing configuration...")
        config = get_config()
        print(f"✅ Configuration loaded: streaming={config.cognitive_streaming.enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test basic integration functionality."""
    print("\n🔍 Testing basic integration...")
    
    try:
        from backend.websocket_manager import WebSocketManager
        from backend.config_manager import get_config
        
        print("1. Creating WebSocket manager...")
        ws_manager = WebSocketManager()
        print("✅ WebSocket manager created")
        
        print("2. Testing configuration access...")
        config = get_config()
        print(f"✅ Configuration accessed: autonomous_learning={config.autonomous_learning.enabled}")
        
        print("3. Testing cognitive models availability...")
        from backend.websocket_manager import COGNITIVE_MODELS_AVAILABLE
        print(f"✅ Cognitive models available: {COGNITIVE_MODELS_AVAILABLE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all circular dependency tests."""
    print("🚀 CIRCULAR IMPORT DEPENDENCY RESOLUTION TEST")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test integration
    if not test_integration():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Circular import dependencies have been resolved")
        print("✅ System is ready for integration testing")
    else:
        print("❌ Some tests failed")
        print("⚠️ Circular import issues may still exist")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
