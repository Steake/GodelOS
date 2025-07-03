#!/usr/bin/env python3
"""
Run individual tests with detailed diagnostic output.
"""

import asyncio
import json
import logging
import time
import sys
from typing import Dict, Any, List
from tests.test_cognitive_architecture_pipeline import CognitiveArchitecturePipeline, PipelinePhase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_specific_tests():
    """Run specific failing tests with detailed diagnostics"""
    pipeline = CognitiveArchitecturePipeline()
    test_suite = pipeline.define_test_suite()
    
    # Extract problematic tests
    problem_tests = []
    for test in test_suite:
        if test.test_id in ["EC002", "EC003", "EC004", "EC005", "CE001", "CE002", "CE003", "CE004"]:
            problem_tests.append(test)
    
    print(f"Running {len(problem_tests)} problem tests with detailed diagnostics")
    
    for test in problem_tests:
        print(f"\n{'='*80}")
        print(f"TEST: {test.test_id} - {test.name}")
        print(f"Description: {test.description}")
        print(f"Endpoint: {test.endpoint}")
        print(f"Method: {test.method}")
        print(f"Payload: {test.payload}")
        print(f"Success Criteria: {test.success_criteria}")
        
        print("\nRUNNING TEST...")
        # Run the test
        if test.websocket_test:
            result = await pipeline._run_websocket_test(test)
        else:
            result = await pipeline._run_http_test(test)
            
        print("\nACTUAL RESPONSE:")
        print(json.dumps(result, indent=2))
        
        # Check criteria
        print("\nCRITERIA EVALUATION:")
        for criterion, expected_value in test.success_criteria.items():
            actual_value = result.get(criterion)
            print(f"- {criterion}:")
            print(f"  Expected: {expected_value}")
            print(f"  Actual: {actual_value}")
            print(f"  ✅ PASS" if check_criterion(actual_value, expected_value) else f"  ❌ FAIL")
            
    print("\n{'='*80}")
    print("Test run complete")
        
def check_criterion(actual_value, expected_value):
    """Check if a criterion is met"""
    if actual_value is None:
        return False
    
    if isinstance(expected_value, bool):
        return actual_value == expected_value
    elif isinstance(expected_value, str):
        if expected_value.startswith(">"):
            try:
                threshold = float(expected_value[1:])
                return float(actual_value) > threshold
            except (ValueError, TypeError):
                return False
        else:
            return actual_value == expected_value
    
    return False

if __name__ == "__main__":
    asyncio.run(run_specific_tests())
