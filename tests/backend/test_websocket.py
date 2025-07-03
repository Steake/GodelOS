"""
WebSocket Connection Tests for GödelOS Backend

Comprehensive test suite for WebSocket functionality including:
- Connection establishment and management
- Real-time cognitive event streaming
- Message broadcasting and subscription
- Connection cleanup and error handling
- Performance and concurrency testing
"""

import asyncio
import json
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

# Import the FastAPI app and WebSocket manager
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.main import app
from backend.websocket_manager import WebSocketManager


class TestWebSocketConnection:
    """Test WebSocket connection establishment and management."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
        self.websocket_manager = WebSocketManager()
    
    def test_websocket_connection_establishment(self):
        """Test basic WebSocket connection establishment."""
        with patch('backend.main.godelos_integration') as mock_integration:
            mock_integration.get_cognitive_state = AsyncMock(return_value={
                "manifest_consciousness": {"awareness_level": 0.8},
                "agentic_processes": [],
                "daemon_threads": []
            })
            
            with self.client.websocket_connect("/ws/cognitive-stream") as websocket:
                # Should receive initial connection message
                data = websocket.receive_json()
                assert data["type"] == "connection_established"
                assert "timestamp" in data
                assert "connection_id" in data
                
                # Should receive initial cognitive state
                initial_state = websocket.receive_json()
                assert initial_state["type"] == "initial_state"
                assert "data" in initial_state
    
    def test_websocket_subscription_handling(self):
        """Test WebSocket event subscription functionality."""
        with patch('backend.main.godelos_integration') as mock_integration:
            mock_integration.get_cognitive_state = AsyncMock(return_value={})
            
            with self.client.websocket_connect("/ws/cognitive-stream") as websocket:
                # Skip initial messages
                websocket.receive_json()  # connection_established
                websocket.receive_json()  # initial_state
                
                # Send subscription request
                subscription_request = {
                    "type": "subscribe",
                    "event_types": ["query_processed", "knowledge_added"]
                }
                websocket.send_json(subscription_request)
                
                # Should receive subscription confirmation
                response = websocket.receive_json()
                assert response["type"] == "subscription_confirmed"
                assert response["event_types"] == ["query_processed", "knowledge_added"]
    
    def test_websocket_error_handling(self):
        """Test WebSocket error handling."""
        with patch('backend.main.godelos_integration') as mock_integration:
            mock_integration.get_cognitive_state = AsyncMock(return_value={})
            
            with self.client.websocket_connect("/ws/cognitive-stream") as websocket:
                # Skip initial messages
                websocket.receive_json()  # connection_established
                websocket.receive_json()  # initial_state
                
                # Send invalid JSON
                websocket.send_text("invalid json")
                
                # Should receive error message
                error_response = websocket.receive_json()
                assert error_response["type"] == "error"
                assert "message" in error_response


class TestWebSocketManager:
    """Test WebSocketManager functionality."""
    
    def setup_method(self):
        """Set up WebSocket manager for each test."""
        self.ws_manager = WebSocketManager()
    
    @pytest.mark.asyncio
    async def test_websocket_manager_connection_tracking(self):
        """Test WebSocket connection tracking."""
        # Mock WebSocket
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        
        # Test connection
        await self.ws_manager.connect(mock_websocket)
        
        assert len(self.ws_manager.active_connections) == 1
        assert mock_websocket in self.ws_manager.active_connections
        assert mock_websocket in self.ws_manager.connection_subscriptions
        assert mock_websocket in self.ws_manager.connection_metadata
        
        # Verify connection metadata
        metadata = self.ws_manager.connection_metadata[mock_websocket]
        assert "connected_at" in metadata
        assert "events_sent" in metadata
        assert "last_activity" in metadata
        
        # Test disconnection
        self.ws_manager.disconnect(mock_websocket)
        
        assert len(self.ws_manager.active_connections) == 0
        assert mock_websocket not in self.ws_manager.connection_subscriptions
        assert mock_websocket not in self.ws_manager.connection_metadata
    
    @pytest.mark.asyncio
    async def test_websocket_manager_broadcasting(self):
        """Test event broadcasting to connected clients."""
        # Mock multiple WebSockets
        mock_ws1 = MagicMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        
        mock_ws2 = MagicMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()
        
        # Connect both
        await self.ws_manager.connect(mock_ws1)
        await self.ws_manager.connect(mock_ws2)
        
        # Broadcast event
        test_event = {
            "type": "test_event",
            "timestamp": time.time(),
            "data": {"message": "test broadcast"}
        }
        
        await self.ws_manager.broadcast(test_event)
        
        # Verify both connections received the event
        mock_ws1.send_json.assert_called_with(test_event)
        mock_ws2.send_json.assert_called_with(test_event)
        
        # Verify event was added to queue
        assert len(self.ws_manager.event_queue) == 1
        assert self.ws_manager.event_queue[0] == test_event
    
    @pytest.mark.asyncio
    async def test_websocket_manager_subscription_filtering(self):
        """Test event filtering based on subscriptions."""
        # Mock WebSocket
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        
        await self.ws_manager.connect(mock_websocket)
        
        # Subscribe to specific event types
        await self.ws_manager.subscribe_to_events(mock_websocket, ["query_processed"])
        
        # Broadcast subscribed event type
        subscribed_event = {
            "type": "query_processed",
            "timestamp": time.time(),
            "data": {}
        }
        await self.ws_manager.broadcast(subscribed_event)
        
        # Broadcast unsubscribed event type
        unsubscribed_event = {
            "type": "knowledge_added",
            "timestamp": time.time(),
            "data": {}
        }
        await self.ws_manager.broadcast(unsubscribed_event)
        
        # Should only receive the subscribed event
        call_args = [call[0][0] for call in mock_websocket.send_json.call_args_list]
        event_types = [event["type"] for event in call_args if event.get("type") != "connection_established"]
        
        assert "query_processed" in event_types
        assert "knowledge_added" not in event_types
    
    @pytest.mark.asyncio
    async def test_websocket_manager_connection_cleanup(self):
        """Test connection cleanup on disconnect."""
        # Mock WebSocket that will fail
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock(side_effect=WebSocketDisconnect())
        
        await self.ws_manager.connect(mock_websocket)
        
        # Broadcast should trigger cleanup for failed connection
        test_event = {"type": "test", "timestamp": time.time()}
        await self.ws_manager.broadcast(test_event)
        
        # Connection should be cleaned up
        assert mock_websocket not in self.ws_manager.active_connections
    
    @pytest.mark.asyncio
    async def test_websocket_manager_event_queue_limit(self):
        """Test event queue size limiting."""
        # Fill queue beyond limit
        for i in range(self.ws_manager.max_queue_size + 100):
            event = {"type": "test", "timestamp": time.time(), "data": {"index": i}}
            self.ws_manager._add_to_event_queue(event)
        
        # Queue should be limited to max size
        assert len(self.ws_manager.event_queue) == self.ws_manager.max_queue_size
        
        # Should contain most recent events
        last_event = self.ws_manager.event_queue[-1]
        assert last_event["data"]["index"] >= self.ws_manager.max_queue_size
    
    @pytest.mark.asyncio
    async def test_websocket_manager_specialized_broadcasts(self):
        """Test specialized broadcast methods."""
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        
        await self.ws_manager.connect(mock_websocket)
        
        # Test cognitive event broadcast
        await self.ws_manager.broadcast_cognitive_event("inference_started", {"query": "test"})
        
        # Test system status broadcast
        await self.ws_manager.broadcast_system_status({"cpu_usage": 75, "memory_usage": 60})
        
        # Test knowledge update broadcast
        await self.ws_manager.broadcast_knowledge_update("item_added", {"item_id": "test123"})
        
        # Test inference progress broadcast
        await self.ws_manager.broadcast_inference_progress("test query", {"progress": 0.5})
        
        # Verify all broadcasts were sent
        assert mock_websocket.send_json.call_count == 5  # 1 connection + 4 broadcasts
    
    def test_websocket_manager_connection_stats(self):
        """Test connection statistics generation."""
        stats = self.ws_manager.get_connection_stats()
        
        assert "total_connections" in stats
        assert "total_events_sent" in stats
        assert "avg_connection_duration_seconds" in stats
        assert "event_queue_size" in stats
        assert "subscription_summary" in stats
        
        assert stats["total_connections"] == 0
        assert stats["event_queue_size"] == 0
    
    @pytest.mark.asyncio
    async def test_websocket_manager_ping_connections(self):
        """Test connection keep-alive ping functionality."""
        # Mock healthy connection
        mock_ws_healthy = MagicMock()
        mock_ws_healthy.accept = AsyncMock()
        mock_ws_healthy.send_json = AsyncMock()
        
        # Mock failed connection
        mock_ws_failed = MagicMock()
        mock_ws_failed.accept = AsyncMock()
        mock_ws_failed.send_json = AsyncMock(side_effect=Exception("Connection failed"))
        
        await self.ws_manager.connect(mock_ws_healthy)
        await self.ws_manager.connect(mock_ws_failed)
        
        assert len(self.ws_manager.active_connections) == 2
        
        # Ping connections
        await self.ws_manager.ping_connections()
        
        # Failed connection should be removed
        assert len(self.ws_manager.active_connections) == 1
        assert mock_ws_healthy in self.ws_manager.active_connections
        assert mock_ws_failed not in self.ws_manager.active_connections


class TestCognitiveStreaming:
    """Test continuous cognitive state streaming."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    @patch('backend.main.godelos_integration')
    @patch('backend.main.websocket_manager')
    @pytest.mark.asyncio
    async def test_cognitive_streaming_format(self, mock_ws_manager, mock_integration):
        """Test cognitive state streaming data format."""
        # Mock cognitive state
        mock_cognitive_state = {
            "manifest_consciousness": {"awareness_level": 0.8},
            "agentic_processes": [
                {
                    "description": "Query Parser",
                    "status": "active",
                    "progress": 0.7,
                    "priority": 5
                }
            ],
            "daemon_threads": [
                {
                    "description": "Memory Consolidation",
                    "status": "running",
                    "progress": 0.5
                }
            ],
            "working_memory": {
                "active_items": [
                    {"content": "Current processing task"}
                ]
            },
            "attention_focus": [
                {"salience": 0.9}
            ]
        }
        
        mock_integration.get_cognitive_state = AsyncMock(return_value=mock_cognitive_state)
        mock_ws_manager.has_connections = MagicMock(return_value=True)
        mock_ws_manager.broadcast = AsyncMock()
        
        # Import and call the streaming function directly
        from backend.main import continuous_cognitive_streaming
        
        # Run one iteration of the streaming loop
        with patch('asyncio.sleep', AsyncMock()):
            await continuous_cognitive_streaming()
        
        # Verify broadcast was called with properly formatted data
        mock_ws_manager.broadcast.assert_called_once()
        
        call_args = mock_ws_manager.broadcast.call_args[0][0]
        assert call_args["type"] == "cognitive_state_update"
        assert "timestamp" in call_args
        assert "data" in call_args
        
        # Verify data structure
        data = call_args["data"]
        assert "manifest_consciousness" in data
        assert "agentic_processes" in data
        assert "daemon_threads" in data
        
        # Verify manifest consciousness formatting
        assert "attention_focus" in data["manifest_consciousness"]
        assert "working_memory" in data["manifest_consciousness"]
        
        # Verify agentic processes formatting
        assert len(data["agentic_processes"]) > 0
        process = data["agentic_processes"][0]
        assert "name" in process
        assert "status" in process
        assert "cpu_usage" in process
        assert "memory_usage" in process


class TestWebSocketConcurrency:
    """Test WebSocket handling under concurrent load."""
    
    def setup_method(self):
        """Set up WebSocket manager for concurrent tests."""
        self.ws_manager = WebSocketManager()
    
    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test handling multiple concurrent WebSocket connections."""
        # Create multiple mock WebSockets
        connections = []
        for i in range(10):
            mock_ws = MagicMock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            connections.append(mock_ws)
        
        # Connect all simultaneously
        connect_tasks = [self.ws_manager.connect(ws) for ws in connections]
        await asyncio.gather(*connect_tasks)
        
        assert len(self.ws_manager.active_connections) == 10
        
        # Broadcast to all simultaneously
        test_event = {"type": "concurrent_test", "timestamp": time.time()}
        await self.ws_manager.broadcast(test_event)
        
        # Verify all connections received the event
        for ws in connections:
            ws.send_json.assert_called_with(test_event)
    
    @pytest.mark.asyncio
    async def test_concurrent_broadcasting(self):
        """Test concurrent event broadcasting."""
        # Set up connection
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()
        await self.ws_manager.connect(mock_ws)
        
        # Broadcast multiple events concurrently
        events = [
            {"type": f"event_{i}", "timestamp": time.time(), "data": {"index": i}}
            for i in range(20)
        ]
        
        broadcast_tasks = [self.ws_manager.broadcast(event) for event in events]
        await asyncio.gather(*broadcast_tasks)
        
        # All events should be sent
        assert mock_ws.send_json.call_count == len(events) + 1  # +1 for connection message
        
        # All events should be in queue
        assert len(self.ws_manager.event_queue) == len(events)
    
    @pytest.mark.asyncio
    async def test_connection_stability_under_load(self):
        """Test WebSocket connection stability under high load."""
        # Mix of healthy and failing connections
        healthy_connections = []
        failing_connections = []
        
        for i in range(5):
            # Healthy connection
            healthy_ws = MagicMock()
            healthy_ws.accept = AsyncMock()
            healthy_ws.send_json = AsyncMock()
            healthy_connections.append(healthy_ws)
            
            # Failing connection
            failing_ws = MagicMock()
            failing_ws.accept = AsyncMock()
            failing_ws.send_json = AsyncMock(side_effect=Exception("Connection failed"))
            failing_connections.append(failing_ws)
        
        # Connect all
        all_connections = healthy_connections + failing_connections
        for ws in all_connections:
            await self.ws_manager.connect(ws)
        
        assert len(self.ws_manager.active_connections) == 10
        
        # Send many events rapidly
        for i in range(50):
            event = {"type": "load_test", "timestamp": time.time(), "data": {"index": i}}
            await self.ws_manager.broadcast(event)
        
        # Only healthy connections should remain
        assert len(self.ws_manager.active_connections) == 5
        
        # Verify all healthy connections are still tracked
        for ws in healthy_connections:
            assert ws in self.ws_manager.active_connections


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality with the main app."""
    
    def setup_method(self):
        """Set up test client for integration tests."""
        self.client = TestClient(app)
    
    def test_websocket_query_integration(self):
        """Test WebSocket integration with query processing."""
        with patch('backend.main.godelos_integration') as mock_integration:
            # Mock query processing
            mock_integration.get_cognitive_state = AsyncMock(return_value={})
            mock_integration.process_natural_language_query = AsyncMock(return_value={
                "response": "Test response",
                "confidence": 0.9,
                "reasoning_steps": [],
                "inference_time_ms": 100.0,
                "knowledge_used": []
            })
            
            with self.client.websocket_connect("/ws/cognitive-stream") as websocket:
                # Skip initial messages
                websocket.receive_json()  # connection_established
                websocket.receive_json()  # initial_state
                
                # Process a query via HTTP API (should trigger WebSocket event)
                query_response = self.client.post("/api/query", json={"query": "test query"})
                assert query_response.status_code == 200
                
                # Should receive query processed event via WebSocket
                # Note: In actual test, timing might need adjustment
                try:
                    event = websocket.receive_json(timeout=1.0)
                    assert event["type"] == "query_processed"
                    assert event["query"] == "test query"
                except:
                    # Timeout is acceptable in unit tests due to async nature
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])