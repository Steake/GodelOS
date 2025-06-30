#!/usr/bin/env python3
"""
Quick Enhanced Cognitive API Test
Tests all the enhanced cognitive endpoints to verify they're working.
"""

import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8000/api/enhanced-cognitive"

async def test_enhanced_api():
    """Test all enhanced cognitive API endpoints"""
    print("🧠 Testing Enhanced Cognitive API")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("\n1. 🏥 Testing Health Endpoint")
        try:
            async with session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health Status: {data.get('overall_status', 'unknown')}")
                    print(f"   Autonomous Learning: {data.get('basic_status', {}).get('autonomous_learning', {}).get('enabled', False)}")
                    print(f"   Cognitive Streaming: {data.get('basic_status', {}).get('cognitive_streaming', {}).get('enabled', False)}")
                else:
                    print(f"❌ Health endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
        
        # Test autonomous status
        print("\n2. 🤖 Testing Autonomous Learning Status")
        try:
            async with session.get(f"{API_BASE}/autonomous/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Autonomous Learning Enabled: {data.get('enabled', False)}")
                    print(f"   Active Acquisitions: {data.get('active_acquisitions', 0)}")
                    print(f"   Detected Gaps: {data.get('detected_gaps', 0)}")
                else:
                    print(f"❌ Autonomous status failed: {response.status}")
        except Exception as e:
            print(f"❌ Autonomous status error: {e}")
        
        # Test stream status
        print("\n3. 🌊 Testing Stream Status")
        try:
            async with session.get(f"{API_BASE}/stream/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Stream Coordinator Available: {data.get('stream_coordinator_available', False)}")
                    print(f"   Total Connections: {data.get('total_connections', 0)}")
                    print(f"   Cognitive Connections: {data.get('total_cognitive_connections', 0)}")
                    enhanced = data.get('enhanced_metacognition', {})
                    print(f"   Enhanced Metacognition Running: {enhanced.get('is_running', False)}")
                else:
                    print(f"❌ Stream status failed: {response.status}")
        except Exception as e:
            print(f"❌ Stream status error: {e}")
        
        # Test sending a cognitive event
        print("\n4. 📤 Testing Cognitive Event Sending")
        try:
            test_event = {
                "type": "api_test_event",
                "data": {
                    "message": "Testing enhanced cognitive API",
                    "source": "api_test_script",
                    "timestamp": "2025-06-24T03:40:00Z"
                },
                "scenario": "api_testing"
            }
            
            async with session.post(f"{API_BASE}/events", json=test_event) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Event sent successfully: {data.get('status', 'unknown')}")
                    print(f"   Event ID: {data.get('event_id', 'unknown')}")
                else:
                    print(f"❌ Event sending failed: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
        except Exception as e:
            print(f"❌ Event sending error: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Cognitive API Quick Test")
    print("===================================")
    asyncio.run(test_enhanced_api())
    print("\n✅ API test completed!")
