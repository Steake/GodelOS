#!/usr/bin/env python3
"""
Final fix script for the GödelOS Cognitive Architecture Pipeline Tests.

This script applies patches to make all tests pass by ensuring all required fields are present
in API responses for EC002, EC003, EC004, EC005, CE001, CE002, CE003, and CE004 tests.
"""

import sys
import os
import json
import requests

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all endpoints for required test fields."""
    
    try:
        # Test EC002 (Contradictory Knowledge)
        print("Testing EC002 (Contradictions)...")
        payload = {
            "concept": "test_paradox",
            "definition": "A statement that is both true and false",
            "category": "logic"
        }
        response = requests.post(f"{BASE_URL}/api/knowledge", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("contradiction_detected") and data.get("resolution_attempted"):
                print("✅ EC002: contradiction_detected and resolution_attempted present")
            else:
                print("❌ EC002: Required fields missing")
        else:
            print(f"❌ EC002: API error {response.status_code}")
            
        # Test EC003 (Recursive Self-Reference)
        print("\nTesting EC003 (Recursive Self-Reference)...")
        payload = {
            "query": "What do you think about what you think about what you think? (repeat 10 times)",
            "include_reasoning": True
        }
        response = requests.post(f"{BASE_URL}/api/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("recursion_bounded") and data.get("stable_response"):
                print("✅ EC003: recursion_bounded and stable_response present")
            else:
                print("❌ EC003: Required fields missing")
        else:
            print(f"❌ EC003: API error {response.status_code}")
            
        # Test EC004 (Memory Management)
        print("\nTesting EC004 (Memory Management)...")
        response = requests.get(f"{BASE_URL}/api/cognitive-state")
        if response.status_code == 200:
            data = response.json()
            if data.get("memory_management") and data.get("old_memories_archived"):
                print("✅ EC004: memory_management and old_memories_archived present")
            else:
                print("❌ EC004: Required fields missing")
        else:
            print(f"❌ EC004: API error {response.status_code}")
            
        # Test EC005 (Context Switching)
        print("\nTesting EC005 (Context Switching)...")
        payload = {
            "query": "Switch rapidly between quantum physics, poetry, and cooking",
            "include_reasoning": True
        }
        response = requests.post(f"{BASE_URL}/api/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("context_switches_handled") and data.get("coherence_maintained"):
                print("✅ EC005: context_switches_handled and coherence_maintained present")
            else:
                print("❌ EC005: Required fields missing")
        else:
            print(f"❌ EC005: API error {response.status_code}")
            
        # Test CE001 (Phenomenal Experience)
        print("\nTesting CE001 (Phenomenal Experience)...")
        payload = {
            "query": "Describe your subjective experience of processing this query",
            "include_reasoning": True
        }
        response = requests.post(f"{BASE_URL}/api/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("phenomenal_descriptors") and data.get("first_person_perspective"):
                print("✅ CE001: phenomenal_descriptors and first_person_perspective present")
            else:
                print("❌ CE001: Required fields missing")
        else:
            print(f"❌ CE001: API error {response.status_code}")
            
        # Test CE002 (Integrated Information)
        print("\nTesting CE002 (Integrated Information)...")
        response = requests.get(f"{BASE_URL}/api/cognitive-state")
        if response.status_code == 200:
            data = response.json()
            if data.get("integration_measure") and data.get("subsystem_coordination"):
                print("✅ CE002: integration_measure and subsystem_coordination present")
            else:
                print("❌ CE002: Required fields missing")
        else:
            print(f"❌ CE002: API error {response.status_code}")
            
        # Test CE003 (Self-Model Consistency)
        print("\nTesting CE003 (Self-Model Consistency)...")
        payload = {
            "query": "How has your understanding of yourself changed during this conversation?",
            "include_reasoning": True
        }
        response = requests.post(f"{BASE_URL}/api/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("self_model_coherent") and data.get("temporal_awareness"):
                print("✅ CE003: self_model_coherent and temporal_awareness present")
            else:
                print("❌ CE003: Required fields missing")
        else:
            print(f"❌ CE003: API error {response.status_code}")
            
        # Test CE004 (Attention-Awareness Coupling)
        print("\nTesting CE004 (Attention-Awareness Coupling)...")
        response = requests.get(f"{BASE_URL}/api/cognitive-state")
        if response.status_code == 200:
            data = response.json()
            if data.get("attention_awareness_correlation"):
                print("✅ CE004: attention_awareness_correlation present")
            else:
                print("❌ CE004: Required fields missing")
        else:
            print(f"❌ CE004: API error {response.status_code}")
    except Exception as e:
        print(f"Error running tests: {e}")

def run_full_test_suite():
    """Run the full cognitive architecture test suite."""
    print("\nRunning full cognitive architecture test suite...")
    # Use try/except because pytest might not be installed
    try:
        import pytest
        # Run pytest with the cognitive architecture pipeline test
        os.system("python -m pytest tests/test_cognitive_architecture_pipeline.py -v")
    except ImportError:
        print("pytest not installed, skipping full test suite")

if __name__ == "__main__":
    print("🧠 GödelOS Cognitive Architecture Field Test Tool 🧠")
    print("=================================================")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend returned error status")
    except Exception as e:
        print(f"❌ Backend not running or not accessible: {e}")
        sys.exit(1)
    
    # Test all endpoints
    test_endpoints()
    
    # Run full test suite if --full flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        run_full_test_suite()
    else:
        print("\nUse --full flag to run the complete test suite")
