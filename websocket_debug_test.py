#!/usr/bin/env python3
"""
WebSocket Debug Tool - Test cognitive streaming connection
"""

import asyncio
import json
import logging
import websockets
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cognitive_websocket():
    """Test the cognitive WebSocket connection"""
    uri = "ws://localhost:8000/api/enhanced-cognitive/stream"
    
    try:
        logger.info(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected to cognitive stream!")
            
            # Send a ping message
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            logger.info(f"📤 Sent ping: {ping_msg}")
            
            # Listen for messages for 30 seconds
            start_time = time.time()
            timeout = 30
            
            logger.info(f"🎧 Listening for messages for {timeout} seconds...")
            
            while time.time() - start_time < timeout:
                try:
                    # Wait for message with 5 second timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    
                    try:
                        data = json.loads(message)
                        logger.info(f"📥 Received: {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError:
                        logger.info(f"📥 Received raw: {message}")
                        
                except asyncio.TimeoutError:
                    logger.info("⏰ No message received in 5 seconds, continuing to listen...")
                    continue
                except websockets.exceptions.ConnectionClosedError as e:
                    logger.error(f"🔌 Connection closed: {e}")
                    break
                    
            logger.info("⏰ Finished listening")
                    
    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"❌ Connection failed with status {e.status_code}")
        logger.error(f"   Headers: {e.response_headers}")
    except ConnectionRefusedError:
        logger.error("❌ Connection refused - is the backend running?")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def test_stream_status():
    """Test the stream status endpoint"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/api/enhanced-cognitive/stream/status') as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Stream status: {json.dumps(data, indent=2)}")
                else:
                    logger.error(f"❌ Status endpoint failed: {response.status}")
                    text = await response.text()
                    logger.error(f"   Response: {text}")
    except Exception as e:
        logger.error(f"❌ Failed to check stream status: {e}")

async def main():
    """Main test function"""
    logger.info("🚀 Starting WebSocket debug test...")
    
    # Test status endpoint first
    logger.info("📊 Testing stream status endpoint...")
    await test_stream_status()
    
    # Test WebSocket connection
    logger.info("🔌 Testing WebSocket connection...")
    await test_cognitive_websocket()
    
    logger.info("✅ Debug test completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Interrupted by user")
