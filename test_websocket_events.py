#!/usr/bin/env python3
"""
Test WebSocket cognitive stream connection
"""

import asyncio
import websockets
import json
import aiohttp

async def test_websocket_and_events():
    """Test both WebSocket connection and event sending"""
    
    print("🔌 Testing WebSocket connection...")
    
    # Test WebSocket connection
    try:
        async with websockets.connect("ws://localhost:8000/api/enhanced-cognitive/stream?granularity=detailed") as websocket:
            print("✅ WebSocket connected successfully")
            
            # Send a test event via HTTP API
            print("📡 Sending test event via API...")
            async with aiohttp.ClientSession() as session:
                test_event = {
                    "type": "test_websocket_event",
                    "data": {
                        "message": "Testing WebSocket delivery",
                        "test_id": "ws_test_001"
                    }
                }
                
                async with session.post(
                    "http://localhost:8000/api/enhanced-cognitive/events",
                    json=test_event
                ) as response:
                    if response.status == 200:
                        print("✅ Event sent via API successfully")
                    else:
                        print(f"❌ Failed to send event: {response.status}")
            
            # Wait for WebSocket message
            print("👂 Listening for WebSocket messages...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                print(f"📨 Received WebSocket message: {data.get('type', 'unknown')}")
                print(f"📄 Message content: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⏰ No WebSocket message received within 10 seconds")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_and_events())
