#!/usr/bin/env python3
"""Simple test for manager attributes"""

from backend.metacognition_modules.enhanced_metacognition_manager import EnhancedMetacognitionManager
from backend.websocket_manager import WebSocketManager
from backend.config_manager import get_config

print('Testing manager creation...')
ws_manager = WebSocketManager()
config = get_config()
manager = EnhancedMetacognitionManager(websocket_manager=ws_manager, config=config)

print(f'✅ has is_initialized: {hasattr(manager, "is_initialized")}')
print(f'✅ is_initialized value: {manager.is_initialized}')
print(f'✅ has godelos_integration: {hasattr(manager, "godelos_integration")}')
print(f'✅ godelos_integration value: {manager.godelos_integration}')
print('🎉 Manager creation successful!')
