#!/usr/bin/env python3
"""
WebSocket Client Test for Enhanced Cognitive Streaming

This script tests the WebSocket connection to the enhanced cognitive streaming endpoint
and displays real-time cognitive events.
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cognitive_websocket():
    """Test the cognitive WebSocket streaming."""
    
    uri = "ws://localhost:8000/api/enhanced-cognitive/stream"
    params = "?granularity=standard&subscriptions=reasoning,knowledge_gap,reflection"
    full_uri = uri + params
    
    print(f"🔌 Connecting to cognitive stream: {full_uri}")
    
    try:
        async with websockets.connect(full_uri) as websocket:
            print("✅ Connected to cognitive stream!")
            
            # Send a configuration message
            config_message = {
                "type": "configure",
                "config": {
                    "granularity": "detailed",
                    "subscriptions": ["reasoning", "knowledge_gap", "reflection", "acquisition"]
                }
            }
            
            await websocket.send(json.dumps(config_message))
            print("📡 Sent configuration message")
            
            # Send a ping
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("🏓 Sent ping message")
            
            # Listen for messages
            print("\n👂 Listening for cognitive events...")
            print("-" * 50)
            
            message_count = 0
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    event_type = data.get("type", "unknown")
                    
                    print(f"[{timestamp}] 📨 Event #{message_count}: {event_type}")
                    
                    if event_type == "cognitive_stream_connected":
                        print(f"   🔗 Connected with client ID: {data.get('client_id')}")
                        print(f"   ⚙️  Granularity: {data.get('granularity')}")
                        print(f"   📋 Subscriptions: {data.get('subscriptions', [])}")
                    
                    elif event_type == "pong":
                        print(f"   🏓 Pong received")
                    
                    elif event_type == "cognitive_event":
                        event_data = data.get("data", {})
                        print(f"   🧠 Cognitive Event: {event_data.get('type', 'unknown')}")
                        print(f"   📊 Data: {json.dumps(event_data.get('data', {}), indent=6)}")
                    
                    elif event_type == "cognitive_stream_configured":
                        print(f"   ⚙️  Stream reconfigured")
                        print(f"   📊 New granularity: {data.get('granularity')}")
                        print(f"   📋 New subscriptions: {data.get('subscriptions', [])}")
                    
                    else:
                        print(f"   📄 Raw data: {json.dumps(data, indent=6)}")
                    
                    print("-" * 50)
                    
                    # Limit to 20 messages for demo
                    if message_count >= 20:
                        print(f"📊 Received {message_count} messages. Demo complete!")
                        break
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("🔌 WebSocket connection closed")
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the backend running on localhost:8000?")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

async def main():
    """Main test function."""
    print("🧠 Enhanced Cognitive WebSocket Stream Test")
    print("=" * 50)
    
    # Test the connection
    await test_cognitive_websocket()
    
    print("\n✅ WebSocket test completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
