"""
Canonical WebSocket Manager for GödelOS.

This is the single base WebSocket manager implementation used throughout the
system.  ``EnhancedWebSocketManager`` (in ``backend.core.enhanced_websocket_manager``)
extends this class with consciousness-streaming capabilities and is the
recommended runtime manager.

All WebSocket traffic in the GödelOS backend MUST be routed through one of
these two classes — no inline or ad-hoc managers.
"""

import json
import logging
import time
from typing import Dict, List, Union

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Base WebSocket connection manager.

    Provides fundamental connect / disconnect / broadcast primitives.
    For consciousness-aware streaming, use ``EnhancedWebSocketManager``.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: Union[str, dict]):
        if isinstance(message, dict):
            message = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection closed or broken — silently skip.
                # Disconnected clients are cleaned up in disconnect().
                pass

    async def broadcast_cognitive_update(self, event: dict):
        """Broadcast cognitive update event to all connected clients."""
        try:
            inner_event = event
            if isinstance(event, dict) and event.get("type") == "cognitive_event" and isinstance(event.get("data"), dict):
                inner_event = event.get("data")
            message = {
                "type": "cognitive_event",
                "timestamp": inner_event.get("timestamp", ""),
                "data": inner_event
            }
        except Exception:
            message = {
                "type": "cognitive_event",
                "timestamp": event.get("timestamp", ""),
                "data": event
            }
        await self.broadcast(message)

    async def broadcast_consciousness_update(self, consciousness_data: dict):
        """Broadcast consciousness update to all connected clients."""
        try:
            message = {
                "type": "consciousness_update",
                "timestamp": consciousness_data.get("timestamp", time.time()),
                "data": consciousness_data
            }
            await self.broadcast(message)
        except Exception as e:
            logger.error(f"Error broadcasting consciousness update: {e}")

    def has_connections(self) -> bool:
        return len(self.active_connections) > 0

    async def get_stats(self) -> Dict:
        """Return basic connection statistics."""
        return {
            "active_connections": len(self.active_connections),
        }


__all__ = ["WebSocketManager"]
