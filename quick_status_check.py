#!/usr/bin/env python3
"""
Quick status check for GödelOS Enhanced Cognitive System
"""

import requests
import json

def check_system_status():
    """Check the status of the enhanced cognitive system."""
    print("🧠 GödelOS Enhanced Cognitive System Status Check")
    print("=" * 50)
    
    # Check basic health
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend Health: HEALTHY")
        else:
            print(f"❌ Backend Health: ERROR ({response.status_code})")
    except Exception as e:
        print(f"❌ Backend Health: OFFLINE ({e})")
        return
    
    # Check enhanced cognitive system
    try:
        response = requests.get("http://localhost:8000/api/enhanced-cognitive/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced Cognitive System: ACTIVE")
            
            # Show key metrics
            if "stream_coordinator" in data:
                coord = data["stream_coordinator"]
                print(f"📡 Stream Coordinator: {coord.get('status', 'unknown')}")
                print(f"🔗 Active Connections: {coord.get('total_connections', 0)}")
                print(f"🧠 Cognitive Connections: {coord.get('cognitive_connections', 0)}")
                
            if "autonomous_learning" in data:
                learning = data["autonomous_learning"]
                print(f"🤖 Autonomous Learning: {'ENABLED' if learning.get('enabled') else 'DISABLED'}")
                print(f"📚 Active Acquisitions: {learning.get('active_acquisitions', 0)}")
                
            if "cognitive_streaming" in data:
                streaming = data["streaming"]
                print(f"📺 Cognitive Streaming: {'ENABLED' if streaming.get('enabled') else 'DISABLED'}")
                print(f"👥 Connected Clients: {streaming.get('connected_clients', 0)}")
                
        else:
            print(f"❌ Enhanced Cognitive System: ERROR ({response.status_code})")
    except Exception as e:
        print(f"❌ Enhanced Cognitive System: ERROR ({e})")
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: ACCESSIBLE")
        else:
            print(f"❌ Frontend: ERROR ({response.status_code})")
    except Exception as e:
        print(f"❌ Frontend: OFFLINE ({e})")
    
    print("\n🌐 Access Points:")
    print("• Main Interface: http://localhost:3000")
    print("• Enhanced Demo: file://enhanced_cognitive_demo.html")
    print("• API Documentation: http://localhost:8000/docs")
    print("• Health Check: http://localhost:8000/health")

if __name__ == "__main__":
    check_system_status()
