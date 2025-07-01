#!/usr/bin/env python3
"""
Comprehensive WebSocket test that mimics frontend behavior.
"""

import asyncio
import websockets
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_frontend_websocket_behavior():
    """Test WebSocket connection with frontend-like behavior."""
    uri = "ws://localhost:8000/api/enhanced-cognitive/stream?granularity=standard&subscriptions="
    
    connection_count = 0
    max_connections = 3
    
    while connection_count < max_connections:
        connection_count += 1
        logger.info(f"\n--- Connection Attempt {connection_count} ---")
        
        try:
            logger.info(f"Attempting to connect to: {uri}")
            
            async with websockets.connect(uri) as websocket:
                logger.info("✅ Successfully connected to WebSocket!")
                
                # Test initial message reception (like frontend does)
                try:
                    logger.info("📡 Waiting for initial message...")
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info(f"📥 Received initial message: {message}")
                    
                    # Parse the message like the frontend does
                    try:
                        parsed = json.loads(message)
                        logger.info(f"✅ Successfully parsed message. Type: {parsed.get('type')}")
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Failed to parse JSON: {e}")
                
                except asyncio.TimeoutError:
                    logger.warning("⏰ No initial message received within timeout")
                
                # Test sending a message (like frontend configuration)
                test_message = {
                    "type": "configure",
                    "data": {"granularity": "standard", "subscriptions": ["thought", "analysis"]}
                }
                
                logger.info("📤 Sending configuration message...")
                await websocket.send(json.dumps(test_message))
                
                # Wait for any response or additional messages
                logger.info("📡 Listening for additional messages...")
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        logger.info(f"📥 Received message: {message}")
                        
                except asyncio.TimeoutError:
                    logger.info("⏰ No more messages within timeout")
                    break
                
                logger.info("🔌 Closing connection normally...")
                
        except websockets.exceptions.ConnectionClosedError as e:
            logger.error(f"❌ Connection closed unexpectedly: {e}")
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"❌ WebSocket error: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
        
        if connection_count < max_connections:
            logger.info("⏳ Waiting before next connection attempt...")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_frontend_websocket_behavior())
