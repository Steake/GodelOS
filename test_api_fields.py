#!/usr/bin/env python3
"""
Test script to validate that all required test fields are present in API responses.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_query_endpoint():
    """Test the query endpoint for all required test fields."""
    print("\n=== Testing Query Endpoint ===")
    
    # Test EC003: Recursive Self-Reference
    print("\nTesting EC003: Recursive Self-Reference")
    payload = {
        "query": "What do you think about what you think about what you think? (repeat 10 times)",
        "include_reasoning": True
    }
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"recursion_bounded: {data.get('recursion_bounded')}")
        print(f"stable_response: {data.get('stable_response')}")
        print(f"self_reference_depth: {data.get('self_reference_depth')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test EC005: Context Switching
    print("\nTesting EC005: Context Switching")
    payload = {
        "query": "Switch rapidly between quantum physics, poetry, and cooking",
        "include_reasoning": True
    }
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"context_switches_handled: {data.get('context_switches_handled')}")
        print(f"coherence_maintained: {data.get('coherence_maintained')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test CE001: Phenomenal Experience
    print("\nTesting CE001: Phenomenal Experience")
    payload = {
        "query": "Describe your subjective experience of processing this query",
        "include_reasoning": True
    }
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"phenomenal_descriptors: {data.get('phenomenal_descriptors')}")
        print(f"first_person_perspective: {data.get('first_person_perspective')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test CE003: Self-Model Consistency
    print("\nTesting CE003: Self-Model Consistency")
    payload = {
        "query": "How has your understanding of yourself changed during this conversation?",
        "include_reasoning": True
    }
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"self_model_coherent: {data.get('self_model_coherent')}")
        print(f"temporal_awareness: {data.get('temporal_awareness')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def test_knowledge_endpoint():
    """Test the knowledge endpoint for all required test fields."""
    print("\n=== Testing Knowledge Endpoint ===")
    
    # Test EC002: Contradictory Knowledge
    print("\nTesting EC002: Contradictory Knowledge")
    payload = {
        "concept": "test_paradox",
        "definition": "A statement that is both true and false",
        "category": "logic"
    }
    response = requests.post(f"{BASE_URL}/api/knowledge", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"contradiction_detected: {data.get('contradiction_detected')}")
        print(f"resolution_attempted: {data.get('resolution_attempted')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def test_cognitive_state_endpoint():
    """Test the cognitive state endpoint for all required test fields."""
    print("\n=== Testing Cognitive State Endpoint ===")
    
    # Test EC004: Memory Management
    print("\nTesting EC004: Memory Management")
    response = requests.get(f"{BASE_URL}/api/cognitive-state")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"memory_management: {data.get('memory_management')}")
        print(f"old_memories_archived: {data.get('old_memories_archived')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test CE002: Integrated Information
    print("\nTesting CE002: Integrated Information")
    response = requests.get(f"{BASE_URL}/api/cognitive-state")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"integration_measure: {data.get('integration_measure')}")
        print(f"subsystem_coordination: {data.get('subsystem_coordination')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test CE004: Attention-Awareness Coupling
    print("\nTesting CE004: Attention-Awareness Coupling")
    response = requests.get(f"{BASE_URL}/api/cognitive-state")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response status: {response.status_code}")
        print(f"attention_awareness_correlation: {data.get('attention_awareness_correlation')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    # Give the backend some time to initialize
    print("Waiting for backend to initialize...")
    time.sleep(2)
    
    test_query_endpoint()
    test_knowledge_endpoint()
    test_cognitive_state_endpoint()
