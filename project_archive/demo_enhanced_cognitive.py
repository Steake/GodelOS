#!/usr/bin/env python3
"""
GödelOS Enhanced Cognitive Features Demo Startup Script

This script demonstrates all enhanced cognitive features:
- Autonomous learning and knowledge gap detection
- Real-time stream of consciousness monitoring
- Enhanced metacognition with cognitive streaming
- WebSocket-based real-time updates
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_enhanced_cognitive_features():
    """Demonstrate all enhanced cognitive features."""
    
    print("🧠 GödelOS Enhanced Cognitive Features Demo")
    print("=" * 50)
    
    # Import and initialize components
    try:
        from backend.enhanced_cognitive_api import initialize_enhanced_cognitive
        from backend.websocket_manager import WebSocketManager
        from backend.godelos_integration import GödelOSIntegration
        from backend.config_manager import get_config, is_feature_enabled
        
        print("✅ Enhanced cognitive modules imported successfully")
        
        # Initialize components
        print("\n🔧 Initializing enhanced cognitive system...")
        
        websocket_manager = WebSocketManager()
        godelos_integration = GödelOSIntegration()
        await godelos_integration.initialize()
        
        # Initialize enhanced cognitive features
        await initialize_enhanced_cognitive(websocket_manager, godelos_integration)
        
        print("✅ Enhanced cognitive system initialized")
        
        # Check configuration
        config = get_config()
        enhanced_enabled = is_feature_enabled('enhanced_metacognition')
        
        print(f"\n📋 Configuration Status:")
        print(f"   - Enhanced Metacognition: {'✅ Enabled' if enhanced_enabled else '❌ Disabled'}")
        print(f"   - WebSocket Manager: {'✅ Active' if websocket_manager else '❌ Inactive'}")
        
        if enhanced_enabled:
            # Get enhanced metacognition manager
            from backend.enhanced_cognitive_api import enhanced_metacognition_manager
            
            if enhanced_metacognition_manager:
                status = await enhanced_metacognition_manager.get_status()
                
                print(f"\n🧠 Enhanced Metacognition Status:")
                print(f"   - System Running: {'✅' if status.get('is_running') else '❌'}")
                print(f"   - Autonomous Learning: {'✅' if status.get('autonomous_learning', {}).get('enabled') else '❌'}")
                print(f"   - Cognitive Streaming: {'✅' if status.get('cognitive_streaming', {}).get('enabled') else '❌'}")
                print(f"   - Active Acquisitions: {status.get('autonomous_learning', {}).get('active_acquisitions', 0)}")
                print(f"   - Detected Gaps: {status.get('autonomous_learning', {}).get('detected_gaps', 0)}")
                print(f"   - Connected Clients: {status.get('cognitive_streaming', {}).get('connected_clients', 0)}")
                print(f"   - Events/Second: {status.get('cognitive_streaming', {}).get('events_per_second', 0)}")
                
                # Demonstrate cognitive processing
                print(f"\n🔍 Demonstrating Enhanced Cognitive Processing...")
                
                # Process a sample query with learning
                test_queries = [
                    "What is consciousness and how does it emerge?",
                    "How does quantum mechanics relate to information theory?",
                    "What are the implications of Gödel's incompleteness theorems for AI?"
                ]
                
                for i, query in enumerate(test_queries, 1):
                    print(f"\n   📝 Test Query {i}: {query}")
                    
                    try:
                        result = await enhanced_metacognition_manager.process_query_with_learning(
                            query=query,
                            context={"demo": True, "test_id": i}
                        )
                        
                        print(f"   ✅ Processing completed with cycle ID: {result.get('cycle_id', 'N/A')}")
                        print(f"   📊 Knowledge gaps detected: {len(result.get('knowledge_gaps', []))}")
                        print(f"   🔄 Autonomous acquisitions triggered: {len(result.get('triggered_acquisitions', []))}")
                        
                        # Brief pause between queries
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        print(f"   ❌ Query processing failed: {e}")
                
                # Show streaming metrics
                print(f"\n📊 Real-time Streaming Metrics:")
                stream_status = await websocket_manager.get_cognitive_stream_status()
                print(f"   - Total Connections: {stream_status.get('total_connections', 0)}")
                print(f"   - Cognitive Connections: {stream_status.get('total_cognitive_connections', 0)}")
                print(f"   - Stream Coordinator Available: {'✅' if stream_status.get('stream_coordinator_available') else '❌'}")
                
                # Generate some test cognitive events
                print(f"\n🎯 Generating Test Cognitive Events...")
                
                try:
                    # Test different types of cognitive events
                    from backend.metacognition_modules.cognitive_models import CognitiveEventType, GranularityLevel
                    
                    test_events = [
                        (CognitiveEventType.REASONING, {"step": "Analyzing conceptual relationships", "confidence": 0.85}),
                        (CognitiveEventType.KNOWLEDGE_GAP, {"concept": "quantum_consciousness_bridge", "priority": 0.7}),
                        (CognitiveEventType.REFLECTION, {"insight": "Integration of multiple knowledge domains", "impact": 0.9})
                    ]
                    
                    for event_type, data in test_events:
                        await enhanced_metacognition_manager._emit_cognitive_event(
                            event_type, data, GranularityLevel.STANDARD
                        )
                        print(f"   ✅ Generated {event_type.value} event")
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    print(f"   ❌ Event generation failed: {e}")
            
            print(f"\n🌟 Demo completed! Enhanced cognitive features are active.")
            print(f"\n📱 Frontend Integration:")
            print(f"   - Open http://localhost:5173 to see the Svelte frontend")
            print(f"   - Navigate to the Enhanced Cognitive Dashboard")
            print(f"   - Monitor real-time cognitive streaming")
            print(f"   - Observe autonomous learning in action")
            
        else:
            print(f"\n❌ Enhanced metacognition is disabled in configuration")
            print(f"   Check backend/config/enhanced_metacognition_config.yaml")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

async def start_backend_server():
    """Start the backend server."""
    print("\n🚀 Starting Backend Server...")
    
    try:
        from backend.start_server import GödelOSServer
        
        server = GödelOSServer(
            host="0.0.0.0",
            port=8000,
            debug=True
        )
        
        # Start the server
        await server.startup()
        
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main demo function."""
    print("🧠 GödelOS Enhanced Cognitive Features Demo")
    print("=" * 50)
    print("This demo will:")
    print("1. Initialize enhanced cognitive system")
    print("2. Demonstrate autonomous learning")
    print("3. Show real-time cognitive streaming")
    print("4. Test knowledge gap detection")
    print("5. Start backend server for frontend integration")
    print("=" * 50)
    
    # Run the demo
    await demo_enhanced_cognitive_features()
    
    # Start backend server
    print(f"\n🚀 Starting backend server for full integration...")
    try:
        await start_backend_server()
    except KeyboardInterrupt:
        print(f"\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
