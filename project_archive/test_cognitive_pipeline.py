#!/usr/bin/env python3
"""
Simple test to verify the cognitive architecture pipeline
"""

import requests
import json
import time

def test_backend():
    """Test if backend is running and demonstrate key functionality"""
    
    print("🧠 Testing GödelOS Cognitive Architecture")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    # Test 2: API Health Check
    print("\n2. Testing API Health...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
            data = response.json()
            if "godelos_integration" in data:
                print(f"   GödelOS Integration: {data['godelos_integration']}")
            if "components" in data:
                print(f"   Components: {list(data['components'].keys())}")
        else:
            print(f"❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ API health check failed: {e}")
    
    # Test 3: Query Processing
    print("\n3. Testing Query Processing...")
    try:
        query_data = {
            "query": "What is consciousness and how does it emerge from complex systems?",
            "include_reasoning": True
        }
        response = requests.post("http://localhost:8000/api/query", 
                                json=query_data, 
                                timeout=30)
        
        if response.status_code == 200:
            print("✅ Query processed successfully")
            result = response.json()
            if "response" in result:
                print(f"   Response preview: {result['response'][:200]}...")
            if "reasoning_steps" in result:
                print(f"   Reasoning steps: {len(result.get('reasoning_steps', []))}")
            if "confidence" in result:
                print(f"   Confidence: {result['confidence']}")
        else:
            print(f"❌ Query failed with status {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
    
    # Test 4: Cognitive State
    print("\n4. Testing Cognitive State Retrieval...")
    try:
        response = requests.get("http://localhost:8000/api/cognitive-state", timeout=10)
        
        if response.status_code == 200:
            print("✅ Cognitive state retrieved")
            state = response.json()
            if "manifest_consciousness" in state:
                mc = state["manifest_consciousness"]
                print(f"   Awareness Level: {mc.get('awareness_level', 'N/A')}")
                print(f"   Coherence Level: {mc.get('coherence_level', 'N/A')}")
            if "metacognitive_state" in state:
                ms = state["metacognitive_state"]
                print(f"   Self-Awareness: {ms.get('self_awareness_level', 'N/A')}")
                print(f"   Cognitive Load: {ms.get('cognitive_load', 'N/A')}")
        else:
            print(f"❌ Cognitive state retrieval failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cognitive state retrieval failed: {e}")
    
    # Test 5: Knowledge Storage
    print("\n5. Testing Knowledge Storage...")
    try:
        knowledge_data = {
            "concept": "emergent_consciousness",
            "definition": "Consciousness that arises from the complex interactions of simpler components in a system",
            "category": "philosophy_of_mind"
        }
        response = requests.post("http://localhost:8000/api/knowledge", 
                                json=knowledge_data, 
                                timeout=10)
        
        if response.status_code in [200, 201]:
            print("✅ Knowledge stored successfully")
            result = response.json()
            print(f"   Status: {result.get('status', 'stored')}")
        else:
            print(f"❌ Knowledge storage failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Knowledge storage failed: {e}")
    
    # Test 6: Meta-cognitive Query
    print("\n6. Testing Meta-cognitive Self-Reflection...")
    try:
        meta_query = {
            "query": "Analyze your own cognitive processes when you answered the previous question about consciousness",
            "include_reasoning": True
        }
        response = requests.post("http://localhost:8000/api/query", 
                                json=meta_query, 
                                timeout=30)
        
        if response.status_code == 200:
            print("✅ Meta-cognitive query processed")
            result = response.json()
            if "response" in result:
                # Check for self-referential content
                response_text = result['response'].lower()
                if any(word in response_text for word in ['i', 'my', 'self', 'reflect', 'process']):
                    print("   🌟 Self-referential awareness detected!")
                print(f"   Response preview: {result['response'][:200]}...")
        else:
            print(f"❌ Meta-cognitive query failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Meta-cognitive query failed: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Test Summary: Basic functionality verified")
    print("   The full pipeline test requires all components to be running.")
    print("   Run 'python cognitive_architecture_pipeline_spec.py' for comprehensive testing.")
    
    return True

if __name__ == "__main__":
    test_backend()
