#!/usr/bin/env python3
"""
Test script to verify the GödelOS query engine functionality.
"""

import requests
import json
import time
from datetime import datetime

def test_query_engine():
    """Test the complete query engine functionality."""
    
    print("🔍 GödelOS Query Engine Test")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Frontend accessibility
    print("1️⃣ Testing frontend accessibility...")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        results["tests"]["frontend"] = {
            "status": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "accessible": response.status_code == 200
        }
        print(f"   ✅ Frontend: HTTP {response.status_code} ({response.elapsed.total_seconds() * 1000:.1f}ms)")
    except Exception as e:
        results["tests"]["frontend"] = {"error": str(e), "accessible": False}
        print(f"   ❌ Frontend error: {e}")
    
    # Test 2: Backend API
    print("\n2️⃣ Testing backend API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        results["tests"]["backend"] = {
            "status": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "accessible": response.status_code == 200
        }
        print(f"   ✅ Backend: HTTP {response.status_code} ({response.elapsed.total_seconds() * 1000:.1f}ms)")
    except Exception as e:
        results["tests"]["backend"] = {"error": str(e), "accessible": False}
        print(f"   ❌ Backend error: {e}")
    
    # Test 3: Query API
    print("\n3️⃣ Testing query API...")
    try:
        query_data = {
            "query": "What is the current system status?",
            "context": {"type": "knowledge"},
            "include_reasoning": True
        }
        response = requests.post("http://localhost:8000/api/query", 
                               json=query_data, 
                               timeout=10)
        results["tests"]["query_api"] = {
            "status": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "working": response.status_code == 200,
            "response_length": len(response.text) if response.status_code == 200 else 0
        }
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"   ✅ Query API: Working (got {len(json_response.get('response', ''))} chars)")
                print(f"       Response: {json_response.get('response', '')[:100]}...")
                results["tests"]["query_api"]["has_response"] = bool(json_response.get('response'))
            except:
                print(f"   ⚠️ Query API: Responded but not JSON format")
        else:
            print(f"   ❌ Query API: HTTP {response.status_code}")
            
    except Exception as e:
        results["tests"]["query_api"] = {"error": str(e), "working": False}
        print(f"   ❌ Query API error: {e}")
    
    # Test 4: Frontend proxy to backend
    print("\n4️⃣ Testing frontend proxy to backend...")
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        proxy_working = response.status_code == 200
        results["tests"]["frontend_proxy"] = {
            "status": response.status_code,
            "working": proxy_working
        }
        print(f"   {'✅' if proxy_working else '❌'} Frontend proxy: {'Working' if proxy_working else 'Not working'}")
    except Exception as e:
        results["tests"]["frontend_proxy"] = {"error": str(e), "working": False}
        print(f"   ❌ Frontend proxy error: {e}")
    
    # Test 5: WebSocket endpoint
    print("\n5️⃣ Testing WebSocket endpoint...")
    try:
        # Just check if the WebSocket endpoint exists (will get 400 for non-WS request)
        response = requests.get("http://localhost:8000/ws/cognitive-stream", timeout=5)
        ws_available = response.status_code in [400, 426]  # Expected for WS endpoints
        results["tests"]["websocket"] = {
            "endpoint_exists": ws_available,
            "status": response.status_code
        }
        print(f"   {'✅' if ws_available else '❌'} WebSocket endpoint: {'Available' if ws_available else 'Not available'}")
    except Exception as e:
        results["tests"]["websocket"] = {"error": str(e), "endpoint_exists": False}
        print(f"   ❌ WebSocket error: {e}")
    
    # Summary
    print("\n📊 Test Summary:")
    all_tests = results["tests"]
    frontend_ok = all_tests.get("frontend", {}).get("accessible", False)
    backend_ok = all_tests.get("backend", {}).get("accessible", False)
    query_ok = all_tests.get("query_api", {}).get("working", False)
    proxy_ok = all_tests.get("frontend_proxy", {}).get("working", False)
    ws_ok = all_tests.get("websocket", {}).get("endpoint_exists", False)
    
    print(f"   Frontend:       {'✅' if frontend_ok else '❌'}")
    print(f"   Backend:        {'✅' if backend_ok else '❌'}")
    print(f"   Query API:      {'✅' if query_ok else '❌'}")
    print(f"   Frontend Proxy: {'✅' if proxy_ok else '❌'}")
    print(f"   WebSocket:      {'✅' if ws_ok else '❌'}")
    
    if frontend_ok and backend_ok and query_ok and proxy_ok:
        print("\n🎉 Query engine should be working!")
        print("💡 Try submitting a query in the web interface at http://localhost:3001")
        results["overall_status"] = "WORKING"
    else:
        print("\n⚠️ Some issues detected that may prevent queries from working")
        results["overall_status"] = "ISSUES_DETECTED"
        
        if not frontend_ok:
            print("   - Frontend not accessible")
        if not backend_ok:
            print("   - Backend not accessible") 
        if not query_ok:
            print("   - Query API not working")
        if not proxy_ok:
            print("   - Frontend proxy not working")
    
    # Save results
    results_file = f"query_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    return results

if __name__ == "__main__":
    test_query_engine()
