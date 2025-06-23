#!/usr/bin/env python3
"""
Generate Enhanced Cognitive Activity for Demo

This script triggers various cognitive activities to demonstrate
the real-time features in the frontend.
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# Backend API base URL
API_BASE = "http://localhost:8000"

async def trigger_cognitive_activity():
    """Generate various types of cognitive activity."""
    
    print("🧠 Generating Enhanced Cognitive Activity for Demo")
    print("=" * 50)
    
    # Test queries that should trigger different cognitive processes
    test_queries = [
        {
            "query": "Explain the philosophical implications of Gödel's incompleteness theorems for artificial intelligence",
            "context": "philosophy of mathematics and AI",
            "description": "Complex philosophical reasoning"
        },
        {
            "query": "How does quantum entanglement relate to information theory and computation?",
            "context": "quantum physics and computer science",
            "description": "Interdisciplinary knowledge integration"
        },
        {
            "query": "What are the ethical considerations of autonomous AI systems that can modify their own code?",
            "context": "AI ethics and self-modification",
            "description": "Self-reflection and ethical reasoning"
        },
        {
            "query": "Describe the relationship between consciousness, emergence, and complex systems",
            "context": "consciousness studies and complexity theory",
            "description": "Multi-domain conceptual synthesis"
        }
    ]
    
    # 1. Check system status
    print("1. 📊 Checking Enhanced Cognitive System Status...")
    try:
        response = requests.get(f"{API_BASE}/api/enhanced-cognitive/stream/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ System is running: {status.get('enhanced_metacognition', {}).get('is_running')}")
            print(f"   🔗 Stream coordinator available: {status.get('stream_coordinator_available')}")
            print(f"   🧠 Autonomous learning enabled: {status.get('enhanced_metacognition', {}).get('autonomous_learning', {}).get('enabled')}")
            print(f"   📡 Cognitive streaming enabled: {status.get('enhanced_metacognition', {}).get('cognitive_streaming', {}).get('enabled')}")
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error checking status: {e}")
        return
    
    print("\n2. 🎯 Triggering Cognitive Queries...")
    
    for i, query_data in enumerate(test_queries, 1):
        print(f"\n   Query {i}/4: {query_data['description']}")
        print(f"   📝 '{query_data['query'][:60]}...'")
        
        try:
            # Submit query
            response = requests.post(
                f"{API_BASE}/api/query",
                json={
                    "query": query_data["query"],
                    "context": query_data["context"],
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Query processed successfully")
                print(f"   📊 Response length: {len(result.get('response', ''))}")
                
                # Check if cognitive events were triggered
                if 'cognitive_events' in result:
                    print(f"   🧠 Cognitive events generated: {len(result['cognitive_events'])}")
                
            else:
                print(f"   ⚠️ Query failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        # Wait between queries to allow processing
        if i < len(test_queries):
            print(f"   ⏳ Waiting 3 seconds before next query...")
            await asyncio.sleep(3)
    
    print("\n3. 📡 Testing Enhanced Cognitive Endpoints...")
    
    # Test various enhanced cognitive endpoints
    endpoints = [
        "/api/enhanced-cognitive/stream/status",
        "/api/enhanced-cognitive/autonomous/status", 
        "/api/enhanced-cognitive/autonomous/gaps",
        "/api/enhanced-cognitive/autonomous/acquisitions"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint}: {response.status_code}")
                
                # Show key metrics
                if 'total_cognitive_connections' in data:
                    print(f"      🔗 Connections: {data['total_cognitive_connections']}")
                if 'enhanced_metacognition' in data:
                    meta = data['enhanced_metacognition']
                    if 'autonomous_learning' in meta:
                        al = meta['autonomous_learning']
                        print(f"      🤖 Active acquisitions: {al.get('active_acquisitions', 0)}")
                        print(f"      🕳️ Detected gaps: {al.get('detected_gaps', 0)}")
                
            else:
                print(f"   ⚠️ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    print("\n4. 🌟 Demo Activity Summary")
    print("   The following should now be visible in the frontend:")
    print("   • Real-time cognitive events in the Stream of Consciousness")
    print("   • Knowledge gap detections in Autonomous Learning Monitor")
    print("   • System health metrics in Enhanced Cognitive Dashboard")
    print("   • WebSocket connection status and event counts")
    print("")
    print("   🌐 Open your browser to: http://localhost:3000")
    print("   📍 Navigate to: Enhanced Cognition > Enhanced Dashboard")
    print("")

async def continuous_activity_generator():
    """Generate continuous low-level activity for demo purposes."""
    print("\n5. 🔄 Starting continuous activity generator...")
    print("   (This will generate periodic cognitive events for demo)")
    
    activity_count = 0
    
    while activity_count < 10:  # Limit for demo
        activity_count += 1
        
        # Generate a simple query to trigger activity
        simple_queries = [
            "What is consciousness?",
            "How does learning work?", 
            "What is artificial intelligence?",
            "Explain quantum mechanics",
            "What is emergence?"
        ]
        
        query = simple_queries[activity_count % len(simple_queries)]
        
        try:
            response = requests.post(
                f"{API_BASE}/api/query",
                json={
                    "query": query,
                    "context": f"demo_activity_{activity_count}",
                    "max_tokens": 50
                },
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"   ⚡ Activity {activity_count}: Query processed - '{query}'")
            else:
                print(f"   ⚠️ Activity {activity_count}: Failed with {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Activity {activity_count}: {e}")
        
        # Wait between activities
        await asyncio.sleep(5)
    
    print(f"   ✅ Generated {activity_count} activities for demo")

async def main():
    """Main demo function."""
    await trigger_cognitive_activity()
    await continuous_activity_generator()
    
    print("\n🎉 Enhanced Cognitive Activity Demo Complete!")
    print("   Check the frontend at http://localhost:3000")
    print("   Look for real-time updates in the Enhanced Cognitive Dashboard")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
