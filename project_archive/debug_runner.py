import asyncio
import json
import logging
import sys
from cognitive_architecture_pipeline_spec import CognitiveArchitecturePipeline, CognitiveTest, TestPhase

# Basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_single_test():
    """Runs a single, isolated test and prints the raw result."""
    print("--- Starting isolated debug runner ---")
    
    pipeline = CognitiveArchitecturePipeline()
    
    # Define the single test we want to debug
    test_bf002 = CognitiveTest(
        test_id='BF002',
        phase=TestPhase.BASIC_FUNCTIONALITY,
        name='Basic Query Processing',
        description='Test NLU and response generation',
        endpoint='/api/query',
        method='POST',
        payload={'query': 'What is consciousness?', 'include_reasoning': True},
        success_criteria={'response': 'present'}
    )

    try:
        # Run the test
        result = await pipeline.run_test(test_bf002)
        
        # Print the raw response data
        print("\n--- RAW API RESPONSE ---")
        print(json.dumps(result.response_data, indent=2))
        
        # Print the final evaluation
        print("\n--- TEST RESULT ---")
        print(f"Success: {result.success}")
        print(f"Error: {result.error_message}")

    except Exception as e:
        print(f"An exception occurred in the test runner: {e}")

    print("\n--- Debug runner finished ---")

if __name__ == "__main__":
    # Ensure the backend is running before executing
    import requests
    try:
        requests.get("http://localhost:8000/health", timeout=2)
        print("Backend is accessible. Running test...")
        asyncio.run(run_single_test())
    except requests.exceptions.ConnectionError:
        print("❌ FATAL: Backend not running. Please start the server first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
