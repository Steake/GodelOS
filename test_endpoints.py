#!/usr/bin/env python3
"""Quick test of API endpoints"""

import requests
import json

def test_endpoints():
    print('Testing basic endpoints...')

    # Test health
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f'Health: {response.status_code}')
    except Exception as e:
        print(f'Health error: {e}')

    # Test query
    try:
        response = requests.post('http://localhost:8000/api/query', 
                               json={'query': 'What is consciousness?', 'include_reasoning': True},
                               timeout=10)
        print(f'Query: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Has reasoning_steps: {"reasoning_steps" in data}')
            if 'reasoning_steps' in data:
                print(f'Reasoning steps count: {len(data["reasoning_steps"])}')
                if len(data["reasoning_steps"]) > 0:
                    print(f'First step structure: {list(data["reasoning_steps"][0].keys())}')
                    print(f'SUCCESS: Pydantic validation working!')
        else:
            print(f'Error response: {response.text}')
    except Exception as e:
        print(f'Query error: {e}')

    # Test cognitive state
    try:
        response = requests.get('http://localhost:8000/api/cognitive-state', timeout=10)
        print(f'Cognitive state: {response.status_code}')
    except Exception as e:
        print(f'Cognitive state error: {e}')

    # Test knowledge endpoint
    try:
        response = requests.post('http://localhost:8000/api/knowledge',
                               json={'concept': 'test', 'definition': 'test definition', 'category': 'test'},
                               timeout=10)
        print(f'Knowledge: {response.status_code}')
    except Exception as e:
        print(f'Knowledge error: {e}')

    print('Tests completed!')

if __name__ == "__main__":
    test_endpoints()
