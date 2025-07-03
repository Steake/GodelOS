#!/usr/bin/env python3
"""Test the enhanced metacognition manager creation."""

from backend.metacognition_modules.enhanced_metacognition_manager import EnhancedMetacognitionManager
from backend.websocket_manager import WebSocketManager
from backend.config_manager import get_config

def test_manager_creation():
    """Test creating the enhanced manager."""
    try:
        print("Testing enhanced manager creation...")
        
        ws_manager = WebSocketManager()
        print("✅ WebSocket manager created")
        
        config = get_config()
        print("✅ Config loaded")
        
        manager = EnhancedMetacognitionManager(
            websocket_manager=ws_manager,
            config=config
        )
        print("✅ Enhanced manager created")
        
        print(f"has is_initialized: {hasattr(manager, 'is_initialized')}")
        print(f"is_initialized value: {manager.is_initialized}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_manager_creation()
    if success:
        print("🎉 Manager creation test passed!")
    else:
        print("❌ Manager creation test failed!")
