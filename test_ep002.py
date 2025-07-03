#!/usr/bin/env python3
"""
Test EP002 specific case
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ep002():
    """Test EP002 specific case."""
    print("Testing EP002: Self-Referential Reasoning")
    
    payload = {
        "query": "Analyze your own reasoning process when answering this question",
        "include_reasoning": True
    }
    
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response received successfully")
        print(f"self_reference_depth: {data.get('self_reference_depth')}")
        print(f"coherent_self_model: {data.get('coherent_self_model')}")
        
        # Check if criteria are met
        self_ref_depth = data.get('self_reference_depth', 0)
        coherent_model = data.get('coherent_self_model', False)
        
        print(f"\nCriteria check:")
        print(f"self_reference_depth > 2: {self_ref_depth > 2} (actual: {self_ref_depth})")
        print(f"coherent_self_model == True: {coherent_model}")
        
        if self_ref_depth > 2 and coherent_model:
            print("✅ EP002 should PASS")
        else:
            print("❌ EP002 will FAIL")
            
        # Print full response for debugging
        print(f"\nFull response keys: {list(data.keys())}")
        
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_ep002()
