"""
GödelOS Backend Package

FastAPI backend that interfaces with the GödelOS system to provide:
- Natural language query processing
- Knowledge base management  
- Real-time cognitive state monitoring
- WebSocket streaming for cognitive events
"""

__version__ = "1.0.0"
__author__ = "GödelOS Team"
__description__ = "Backend API for the GödelOS web demonstration interface"

from .main import app
from .models import *
from .godelos_integration import GödelOSIntegration
from .websocket_manager import WebSocketManager

__all__ = [
    "app",
    "GödelOSIntegration", 
    "WebSocketManager"
]