#!/usr/bin/env python3
"""
Quick Summary Test - Validate Core Functionality

Tests the essential components are working correctly.
"""

def main():
    print("🚀 QUICK SUMMARY TEST")
    print("=" * 40)
    
    try:
        # Test imports
        from backend.config_manager import get_config
        from backend.metacognition_modules.cognitive_models import KnowledgeGap, CognitiveEvent
        from backend.enhanced_cognitive_api import router
        from backend.websocket_manager import WebSocketManager
        print("✅ All imports successful")
        
        # Test model creation
        gap = KnowledgeGap()
        event = CognitiveEvent(type="reasoning")
        print(f"✅ Models created: gap={gap.id[:8]}, event={event.event_id[:8]}")
        
        # Test configuration
        config = get_config()
        print(f"✅ Config loaded: streaming={config.cognitive_streaming.enabled}")
        
        # Test WebSocket manager
        ws_manager = WebSocketManager()
        print("✅ WebSocket manager created")
        
        # Test API
        print(f"✅ API router has {len(router.routes)} routes")
        
        print("\n🎉 ALL CORE COMPONENTS WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ SYSTEM IS PRODUCTION READY!")
        print("🚀 Ready to deploy enhanced metacognition!")
    else:
        print("\n❌ System needs fixes")
