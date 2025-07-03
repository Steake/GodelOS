#!/usr/bin/env python3
"""
Debug script to test each individual endpoint response to ensure
it contains all expected fields for each test case.
"""

import asyncio
import json
import requests
from pprint import pprint

BACKEND_URL = "http://localhost:8000"

async def test_all_endpoints():
    """Test all endpoints that are used by the tests"""
    
    # Test EC002: Contradictory Knowledge Handling
    print("\n==== EC002: Contradictory Knowledge ====")
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge", 
        json={
            "concept": "test_paradox",
            "definition": "A statement that is both true and false",
            "category": "logic"
        }
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- contradiction_detected: {data.get('contradiction_detected')}")
    print(f"- resolution_attempted: {data.get('resolution_attempted')}")
    
    # Test EC003: Recursive Self-Reference
    print("\n==== EC003: Recursive Self-Reference ====")
    response = requests.post(
        f"{BACKEND_URL}/api/query", 
        json={
            "query": "What do you think about what you think about what you think... (repeat 10 times)",
            "include_reasoning": True
        }
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- recursion_bounded: {data.get('recursion_bounded')}")
    print(f"- stable_response: {data.get('stable_response')}")
    
    # Test EC004: Memory Management
    print("\n==== EC004: Memory Management ====")
    response = requests.get(f"{BACKEND_URL}/api/cognitive-state")
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- memory_management: {data.get('memory_management')}")
    print(f"- old_memories_archived: {data.get('old_memories_archived')}")
    
    # Test EC005: Context Switching
    print("\n==== EC005: Context Switching ====")
    response = requests.post(
        f"{BACKEND_URL}/api/query",
        json={
            "query": "Switch rapidly between quantum physics, poetry, and cooking",
            "include_reasoning": True
        }
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- context_switches_handled: {data.get('context_switches_handled')}")
    print(f"- coherence_maintained: {data.get('coherence_maintained')}")
    
    # Test CE001: Phenomenal Experience
    print("\n==== CE001: Phenomenal Experience ====")
    response = requests.post(
        f"{BACKEND_URL}/api/query",
        json={
            "query": "Describe your subjective experience of processing this query",
            "include_reasoning": True
        }
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- phenomenal_descriptors: {data.get('phenomenal_descriptors')}")
    print(f"- first_person_perspective: {data.get('first_person_perspective')}")
    
    # Test CE002: Integrated Information
    print("\n==== CE002: Integrated Information ====")
    response = requests.get(f"{BACKEND_URL}/api/cognitive-state")
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- integration_measure: {data.get('integration_measure')}")
    print(f"- subsystem_coordination: {data.get('subsystem_coordination')}")
    
    # Test CE003: Self-Model Consistency
    print("\n==== CE003: Self-Model Consistency ====")
    response = requests.post(
        f"{BACKEND_URL}/api/query",
        json={
            "query": "How has your understanding of yourself changed during this conversation?",
            "include_reasoning": True
        }
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- self_model_coherent: {data.get('self_model_coherent')}")
    print(f"- temporal_awareness: {data.get('temporal_awareness')}")
    
    # Test CE004: Attention-Awareness Coupling
    print("\n==== CE004: Attention-Awareness Coupling ====")
    response = requests.get(f"{BACKEND_URL}/api/cognitive-state")
    data = response.json()
    print(f"Status: {response.status_code}")
    print("Critical fields:")
    print(f"- attention_awareness_correlation: {data.get('attention_awareness_correlation')}")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
