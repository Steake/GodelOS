#!/usr/bin/env python3

import asyncio
import sys
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append('.')
from cognitive_architecture_pipeline_spec import CognitiveArchitecturePipeline, CognitiveTest, TestPhase

async def debug_test():
    pipeline = CognitiveArchitecturePipeline()
    
    # Test 1: Manual API call
    print("=== Manual API Test ===")
    try:
        response = requests.post('http://localhost:8000/api/query', 
                               json={'query': 'What is consciousness?', 'include_reasoning': True}, 
                               timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response keys: {list(result.keys())}")
        print(f"Has 'response': {'response' in result}")
        print(f"Response content: {result.get('response', 'NOT FOUND')[:100]}...")
    except Exception as e:
        print(f"Manual API call failed: {e}")
        return
    
    # Test 2: Pipeline HTTP test
    print("\n=== Pipeline HTTP Test ===")
    test = CognitiveTest(
        test_id='DEBUG',
        phase=TestPhase.BASIC_FUNCTIONALITY,
        name='Debug Test',
        description='Debug test',
        endpoint='/api/query',
        method='POST',
        payload={'query': 'What is consciousness?', 'include_reasoning': True},
        success_criteria={'response': 'present'}
    )
    
    try:
        http_result = await pipeline._run_http_test(test)
        print(f"HTTP result keys: {list(http_result.keys())}")
        print(f"Has 'response': {'response' in http_result}")
    except Exception as e:
        print(f"Pipeline HTTP test failed: {e}")
        return
    
    # Test 3: Success criteria evaluation
    print("\n=== Success Criteria Test ===")
    success = pipeline._evaluate_success_criteria(test, http_result, {})
    print(f"Success: {success}")
    
    # Test 4: Full test run
    print("\n=== Full Test Run ===")
    full_result = await pipeline.run_test(test)
    print(f"Full test result:")
    print(f"  Success: {full_result.success}")
    print(f"  Error: {full_result.error_message}")
    print(f"  Duration: {full_result.duration}")
    print(f"  Response data keys: {list(full_result.response_data.keys()) if full_result.response_data else 'None'}")

if __name__ == "__main__":
    asyncio.run(debug_test())
