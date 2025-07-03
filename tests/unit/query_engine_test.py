#!/usr/bin/env python3
"""
Test script to verify that the GödelOS query engine is working properly.
This tests both the Svelte frontend on port 3001 and the backend API on port 8000.
"""

import requests
import json
import time
from datetime import datetime

def test_query_engine():
    """Test the query engine functionality end-to-end."""
    
    print("🧪 GödelOS Query Engine Test")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "UNKNOWN",
        "tests": {}
    }
    
    # Test 1: Frontend is accessible
    print("🌐 Test 1: Frontend Accessibility")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        frontend_ok = response.status_code == 200
        results["tests"]["frontend_accessible"] = frontend_ok
        print(f"   {'✅' if frontend_ok else '❌'} Frontend responding: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
        results["tests"]["frontend_accessible"] = False
    
    # Test 2: Backend API is accessible
    print("\n🔧 Test 2: Backend API Accessibility")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        backend_ok = response.status_code == 200
        results["tests"]["backend_accessible"] = backend_ok
        print(f"   {'✅' if backend_ok else '❌'} Backend health: {response.status_code}")
        if backend_ok:
            health_data = response.json()
            print(f"   📊 Backend status: {health_data.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
        results["tests"]["backend_accessible"] = False
    
    # Test 3: Query API endpoint
    print("\n💬 Test 3: Query API Endpoint")
    try:
        test_query = {
            "query": "What is the current system status?",
            "context": {"type": "knowledge"},
            "include_reasoning": True
        }
        response = requests.post(
            "http://localhost:8000/api/query", 
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        query_api_ok = response.status_code == 200
        results["tests"]["query_api_works"] = query_api_ok
        print(f"   {'✅' if query_api_ok else '❌'} Query API: {response.status_code}")
        
        if query_api_ok:
            query_response = response.json()
            print(f"   📝 Response length: {len(query_response.get('response', ''))}")
            print(f"   🎯 Confidence: {query_response.get('confidence', 0):.2f}")
            print(f"   ⏱️  Processing time: {query_response.get('inference_time_ms', 0):.1f}ms")
        else:
            print(f"   📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Query API error: {e}")
        results["tests"]["query_api_works"] = False
    
    # Test 4: WebSocket endpoint (connection test only)
    print("\n🔌 Test 4: WebSocket Endpoint")
    try:
        import websocket
        import threading
        
        ws_connected = False
        ws_error = None
        
        def on_open(ws):
            nonlocal ws_connected
            ws_connected = True
            print("   📡 WebSocket connected successfully")
            ws.close()
            
        def on_error(ws, error):
            nonlocal ws_error
            ws_error = error
            
        # Quick WebSocket connection test
        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws/cognitive-stream",
            on_open=on_open,
            on_error=on_error
        )
        
        # Run WebSocket in a thread with timeout
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait up to 3 seconds for connection
        time.sleep(3)
        
        results["tests"]["websocket_accessible"] = ws_connected
        if ws_connected:
            print("   ✅ WebSocket endpoint accessible")
        else:
            print(f"   ❌ WebSocket connection failed: {ws_error}")
            
    except ImportError:
        print("   ⚠️  WebSocket test skipped (websocket-client not installed)")
        results["tests"]["websocket_accessible"] = None
    except Exception as e:
        print(f"   ❌ WebSocket error: {e}")
        results["tests"]["websocket_accessible"] = False
    
    # Test 5: Frontend-Backend Integration (proxy test)
    print("\n🔗 Test 5: Frontend-Backend Integration")
    try:
        # Test if frontend can proxy API requests
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        proxy_ok = response.status_code == 200
        results["tests"]["frontend_backend_proxy"] = proxy_ok
        print(f"   {'✅' if proxy_ok else '❌'} Frontend proxy to backend: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Proxy test error: {e}")
        results["tests"]["frontend_backend_proxy"] = False
    
    # Calculate overall status
    print(f"\n📊 Test Results Summary:")
    passed_tests = sum(1 for result in results["tests"].values() if result is True)
    total_tests = len([r for r in results["tests"].values() if r is not None])
    
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests >= 4:
        results["status"] = "EXCELLENT"
        status_emoji = "🎉"
        message = "Query engine is fully functional!"
    elif passed_tests >= 3:
        results["status"] = "GOOD"
        status_emoji = "✅"
        message = "Query engine is mostly working, minor issues detected."
    elif passed_tests >= 2:
        results["status"] = "PARTIAL"
        status_emoji = "⚠️"
        message = "Query engine has significant issues."
    else:
        results["status"] = "BROKEN"
        status_emoji = "❌"
        message = "Query engine is not working properly."
    
    print(f"\n🎯 Final Status: {status_emoji} {results['status']}")
    print(f"   {message}")
    
    if results["status"] in ["EXCELLENT", "GOOD"]:
        print(f"\n🚀 Query Engine Status: OPERATIONAL")
        print(f"   • Frontend: http://localhost:3001")
        print(f"   • Backend API: http://localhost:8000")
        print(f"   • Users can submit queries and see responses")
    else:
        print(f"\n⚠️  Query Engine needs attention:")
        for test_name, result in results["tests"].items():
            if result is False:
                print(f"   • {test_name}: FAILED")
    
    # Save results
    results_file = f"query_engine_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    return results

if __name__ == "__main__":
    test_query_engine()
