#!/usr/bin/env python3
"""
WebSocket listener to verify event broadcasting.
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def listen_for_events():
    """Keep WebSocket connection open and listen for events."""
    uri = "ws://localhost:8000/api/enhanced-cognitive/stream?granularity=standard&subscriptions="
    
    try:
        logger.info(f"Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected! Listening for events...")
            logger.info("💡 Run 'python3 send_test_event.py' in another terminal to send test events")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get('type', 'unknown')
                    timestamp = data.get('timestamp', 'N/A')
                    
                    if event_type == 'THOUGHT':
                        logger.info(f"🧠 THOUGHT EVENT: {data.get('data', {}).get('content', 'No content')}")
                    else:
                        logger.info(f"📡 {event_type}: {timestamp}")
                    
                except json.JSONDecodeError:
                    logger.info(f"📥 Raw message: {message}")
                    
    except Exception as e:
        logger.error(f"❌ Connection error: {e}")

if __name__ == "__main__":
    logger.info("🎧 Starting event listener...")
    logger.info("Press Ctrl+C to stop")
    try:
        asyncio.run(listen_for_events())
    except KeyboardInterrupt:
        logger.info("👋 Stopping listener...")
