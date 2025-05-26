"""
WebSocket Manager for GödelOS API

Manages WebSocket connections and broadcasts real-time cognitive events
to connected clients.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and event broadcasting."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: List[WebSocket] = []
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.event_queue: List[Dict[str, Any]] = []
        self.max_queue_size = 1000
        self.broadcast_lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.connection_subscriptions[websocket] = set()
            self.connection_metadata[websocket] = {
                "connected_at": time.time(),
                "events_sent": 0,
                "last_activity": time.time()
            }
            
            logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
            
            # Send welcome message
            await self._send_to_connection(websocket, {
                "type": "connection_established",
                "timestamp": time.time(),
                "message": "Connected to GödelOS cognitive stream",
                "connection_id": id(websocket)
            })
            
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            await self._cleanup_connection(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            if websocket in self.connection_subscriptions:
                del self.connection_subscriptions[websocket]
            
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def _cleanup_connection(self, websocket: WebSocket):
        """Clean up a failed connection."""
        try:
            await websocket.close()
        except:
            pass
        finally:
            self.disconnect(websocket)
    
    async def subscribe_to_events(self, websocket: WebSocket, event_types: List[str]):
        """Subscribe a connection to specific event types."""
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket].update(event_types)
            logger.info(f"WebSocket subscribed to events: {event_types}")
    
    async def unsubscribe_from_events(self, websocket: WebSocket, event_types: List[str]):
        """Unsubscribe a connection from specific event types."""
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket].difference_update(event_types)
            logger.info(f"WebSocket unsubscribed from events: {event_types}")
    
    def has_connections(self) -> bool:
        """Check if there are any active connections."""
        return len(self.active_connections) > 0
    
    async def broadcast(self, event: Dict[str, Any]):
        """Broadcast an event to all connected clients."""
        if not self.active_connections:
            return
        
        async with self.broadcast_lock:
            # Add event to queue for new connections
            self._add_to_event_queue(event)
            
            # Send to all active connections
            disconnected_connections = []
            
            for websocket in self.active_connections:
                try:
                    # Check if connection is subscribed to this event type
                    if self._should_send_event(websocket, event):
                        await self._send_to_connection(websocket, event)
                        
                        # Update connection metadata
                        if websocket in self.connection_metadata:
                            self.connection_metadata[websocket]["events_sent"] += 1
                            self.connection_metadata[websocket]["last_activity"] = time.time()
                
                except WebSocketDisconnect:
                    disconnected_connections.append(websocket)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected_connections.append(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                self.disconnect(websocket)
    
    def _should_send_event(self, websocket: WebSocket, event: Dict[str, Any]) -> bool:
        """Determine if an event should be sent to a specific connection."""
        # If no subscriptions, send all events
        if websocket not in self.connection_subscriptions:
            return True
        
        subscriptions = self.connection_subscriptions[websocket]
        if not subscriptions:
            return True
        
        event_type = event.get("type", "")
        return event_type in subscriptions or "all" in subscriptions
    
    async def _send_to_connection(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send data to a specific WebSocket connection."""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send data to WebSocket: {e}")
            raise
    
    def _add_to_event_queue(self, event: Dict[str, Any]):
        """Add event to the queue for replay to new connections."""
        self.event_queue.append(event)
        
        # Maintain queue size limit
        if len(self.event_queue) > self.max_queue_size:
            self.event_queue = self.event_queue[-self.max_queue_size:]
    
    async def send_recent_events(self, websocket: WebSocket, count: int = 10):
        """Send recent events to a newly connected client."""
        try:
            recent_events = self.event_queue[-count:] if self.event_queue else []
            
            if recent_events:
                await self._send_to_connection(websocket, {
                    "type": "recent_events",
                    "timestamp": time.time(),
                    "events": recent_events,
                    "count": len(recent_events)
                })
                
        except Exception as e:
            logger.error(f"Error sending recent events: {e}")
    
    async def broadcast_cognitive_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast a cognitive event with proper formatting."""
        cognitive_event = {
            "type": "cognitive_event",
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data,
            "source": "godelos_system"
        }
        
        await self.broadcast(cognitive_event)
    
    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status update."""
        status_event = {
            "type": "system_status",
            "timestamp": time.time(),
            "data": status,
            "source": "godelos_system"
        }
        
        await self.broadcast(status_event)
    
    async def broadcast_knowledge_update(self, update_type: str, knowledge_data: Dict[str, Any]):
        """Broadcast knowledge base update."""
        knowledge_event = {
            "type": "knowledge_update",
            "timestamp": time.time(),
            "update_type": update_type,
            "data": knowledge_data,
            "source": "godelos_system"
        }
        
        await self.broadcast(knowledge_event)
    
    async def broadcast_inference_progress(self, query: str, progress_data: Dict[str, Any]):
        """Broadcast inference progress update."""
        inference_event = {
            "type": "inference_progress",
            "timestamp": time.time(),
            "query": query,
            "data": progress_data,
            "source": "godelos_inference_engine"
        }
        
        await self.broadcast(inference_event)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections."""
        total_connections = len(self.active_connections)
        total_events_sent = sum(
            metadata.get("events_sent", 0) 
            for metadata in self.connection_metadata.values()
        )
        
        # Calculate average connection duration
        current_time = time.time()
        connection_durations = [
            current_time - metadata.get("connected_at", current_time)
            for metadata in self.connection_metadata.values()
        ]
        avg_duration = sum(connection_durations) / len(connection_durations) if connection_durations else 0
        
        return {
            "total_connections": total_connections,
            "total_events_sent": total_events_sent,
            "avg_connection_duration_seconds": avg_duration,
            "event_queue_size": len(self.event_queue),
            "subscription_summary": self._get_subscription_summary()
        }
    
    def _get_subscription_summary(self) -> Dict[str, int]:
        """Get summary of event subscriptions."""
        subscription_counts = {}
        
        for subscriptions in self.connection_subscriptions.values():
            for event_type in subscriptions:
                subscription_counts[event_type] = subscription_counts.get(event_type, 0) + 1
        
        return subscription_counts
    
    async def ping_connections(self):
        """Send ping to all connections to keep them alive."""
        if not self.active_connections:
            return
        
        ping_event = {
            "type": "ping",
            "timestamp": time.time(),
            "message": "keepalive"
        }
        
        disconnected_connections = []
        
        for websocket in self.active_connections:
            try:
                await self._send_to_connection(websocket, ping_event)
            except Exception as e:
                logger.warning(f"Connection failed ping test: {e}")
                disconnected_connections.append(websocket)
        
        # Clean up failed connections
        for websocket in disconnected_connections:
            self.disconnect(websocket)
    
    async def start_keepalive_task(self):
        """Start a background task to keep connections alive."""
        async def keepalive_loop():
            while True:
                try:
                    await asyncio.sleep(30)  # Ping every 30 seconds
                    await self.ping_connections()
                except Exception as e:
                    logger.error(f"Keepalive task error: {e}")
        
        asyncio.create_task(keepalive_loop())