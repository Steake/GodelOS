#!/usr/bin/env python3
"""
Simple test to verify the query engine is working properly.
"""

import requests
import json
import time

def test_query_functionality():
    print("🧪 Testing GödelOS Query Engine")
    print("=" * 40)
    
    # Test 1: Backend Health
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
        return False
    
    # Test 2: Frontend Accessibility
    print("2. Testing frontend accessibility...")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
        else:
            print(f"   ❌ Frontend inaccessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend connection failed: {e}")
        return False
    
    # Test 3: Query API
    print("3. Testing query API...")
    try:
        test_query = {
            "query": "What is your current status?",
            "context": {"type": "knowledge"},
            "include_reasoning": True
        }
        
        response = requests.post(
            "http://localhost:8000/api/query",
            json=test_query,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Query API working")
            print(f"   📝 Response: {result.get('response', '')[:100]}...")
            print(f"   🎯 Confidence: {result.get('confidence', 0):.2f}")
            return True
        else:
            print(f"   ❌ Query API failed: {response.status_code}")
            print(f"   📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Query API error: {e}")
        return False

if __name__ == "__main__":
    success = test_query_functionality()
    
    print("\n🎯 Summary:")
    if success:
        print("✅ Query engine is WORKING!")
        print("🚀 Users can now:")
        print("   • Access frontend at http://localhost:3001")
        print("   • Submit queries via the interface")
        print("   • See responses in real-time")
    else:
        print("❌ Query engine has issues")
        print("⚠️  Check the logs above for details")
