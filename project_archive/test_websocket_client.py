#!/usr/bin/env python3
"""
Simple WebSocket client to test cognitive event streaming.
"""

import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/api/enhanced-cognitive/stream?granularity=standard&subscriptions="
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔗 Connected to cognitive stream WebSocket")
            
            # Listen for messages for 30 seconds
            timeout = 30
            print(f"📡 Listening for messages for {timeout} seconds...")
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    print(f"📥 Received: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⏰ Timeout reached")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
