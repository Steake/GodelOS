#!/usr/bin/env python3
"""
Direct WebSocket test for the enhanced cognitive API.
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test direct connection to the enhanced cognitive WebSocket endpoint."""
    uri = "ws://localhost:8000/api/enhanced-cognitive/stream?granularity=standard&subscriptions="
    
    try:
        logger.info(f"Attempting to connect to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Successfully connected to WebSocket!")
            
            # Send a test message
            test_message = {
                "type": "subscribe",
                "data": {"event_types": ["thought", "analysis"]}
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info("📤 Sent test message")
            
            # Wait for a response or timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                logger.info("⏰ No response received within timeout (this is expected)")
            
            # Keep connection open for a few seconds to test
            await asyncio.sleep(3)
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to WebSocket: {e}")
        logger.error(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
