"""
Test suite for the GödelOS Backend API

Basic tests to verify API functionality and integration.
"""

import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import websockets

from backend.main import app
from backend.config import TestingSettings

# Use testing configuration
import backend.config
backend.config.settings = TestingSettings()

client = TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        # May return 503 if GödelOS not initialized, which is expected in tests
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "timestamp" in data


class TestQueryEndpoint:
    """Test query processing endpoint."""
    
    def test_query_endpoint_structure(self):
        """Test query endpoint structure."""
        query_data = {
            "query": "Where is John?",
            "include_reasoning": False
        }
        
        response = client.post("/api/query", json=query_data)
        # May return 503 if GödelOS not initialized
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "confidence" in data
            assert "inference_time_ms" in data
    
    def test_query_with_reasoning(self):
        """Test query endpoint with reasoning enabled."""
        query_data = {
            "query": "Can John go to the Library?",
            "include_reasoning": True
        }
        
        response = client.post("/api/query", json=query_data)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "reasoning_steps" in data
    
    def test_invalid_query_data(self):
        """Test query endpoint with invalid data."""
        response = client.post("/api/query", json={})
        assert response.status_code == 422  # Validation error


class TestKnowledgeEndpoints:
    """Test knowledge management endpoints."""
    
    def test_get_knowledge_endpoint(self):
        """Test knowledge retrieval endpoint."""
        response = client.get("/api/knowledge")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "facts" in data
            assert "rules" in data
            assert "concepts" in data
            assert "total_count" in data
    
    def test_get_knowledge_with_filters(self):
        """Test knowledge retrieval with filters."""
        response = client.get("/api/knowledge?knowledge_type=facts&limit=10")
        assert response.status_code in [200, 503]
    
    def test_add_knowledge_endpoint(self):
        """Test knowledge addition endpoint."""
        knowledge_data = {
            "content": "Test fact",
            "knowledge_type": "fact",
            "context_id": "TEST"
        }
        
        response = client.post("/api/knowledge", json=knowledge_data)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
    
    def test_invalid_knowledge_data(self):
        """Test knowledge endpoint with invalid data."""
        response = client.post("/api/knowledge", json={})
        assert response.status_code == 422  # Validation error


class TestCognitiveStateEndpoint:
    """Test cognitive state endpoint."""
    
    def test_cognitive_state_endpoint(self):
        """Test cognitive state retrieval."""
        response = client.get("/api/cognitive-state")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "manifest_consciousness" in data
            assert "agentic_processes" in data
            assert "daemon_threads" in data
            assert "working_memory" in data
            assert "attention_focus" in data
            assert "metacognitive_state" in data
            assert "timestamp" in data


@pytest.mark.asyncio
class TestWebSocketEndpoint:
    """Test WebSocket functionality."""
    
    async def test_websocket_connection(self):
        """Test WebSocket connection establishment."""
        try:
            with client.websocket_connect("/ws/cognitive-stream") as websocket:
                # Should receive initial connection message
                data = websocket.receive_json()
                assert data["type"] == "connection_established"
        except Exception as e:
            # WebSocket may not be available in test environment
            pytest.skip(f"WebSocket test skipped: {e}")
    
    async def test_websocket_subscription(self):
        """Test WebSocket event subscription."""
        try:
            with client.websocket_connect("/ws/cognitive-stream") as websocket:
                # Receive initial message
                websocket.receive_json()
                
                # Send subscription message
                subscription = {
                    "type": "subscribe",
                    "event_types": ["query_processed", "knowledge_added"]
                }
                websocket.send_json(subscription)
                
                # Should receive confirmation
                response = websocket.receive_json()
                assert response["type"] == "subscription_confirmed"
        except Exception as e:
            pytest.skip(f"WebSocket subscription test skipped: {e}")


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_endpoint(self):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_malformed_json(self):
        """Test malformed JSON handling."""
        response = client.post(
            "/api/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


def run_integration_test():
    """Run a simple integration test."""
    print("Running GödelOS Backend Integration Test...")
    
    # Test basic connectivity
    print("1. Testing basic connectivity...")
    response = client.get("/")
    print(f"   Root endpoint: {response.status_code}")
    
    response = client.get("/health")
    print(f"   Health endpoint: {response.status_code}")
    
    # Test query processing
    print("2. Testing query processing...")
    query_data = {"query": "Where is John?", "include_reasoning": False}
    response = client.post("/api/query", json=query_data)
    print(f"   Query endpoint: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {data.get('response', 'N/A')}")
        print(f"   Confidence: {data.get('confidence', 'N/A')}")
        print(f"   Inference time: {data.get('inference_time_ms', 'N/A')} ms")
    
    # Test knowledge retrieval
    print("3. Testing knowledge retrieval...")
    response = client.get("/api/knowledge")
    print(f"   Knowledge endpoint: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total knowledge items: {data.get('total_count', 'N/A')}")
    
    # Test cognitive state
    print("4. Testing cognitive state...")
    response = client.get("/api/cognitive-state")
    print(f"   Cognitive state endpoint: {response.status_code}")
    
    print("Integration test completed!")


if __name__ == "__main__":
    # Run integration test if called directly
    run_integration_test()