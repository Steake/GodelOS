#!/usr/bin/env python3
"""
Analyze failing tests to identify patterns and root causes.
"""

import json
import sys

def analyze_test_failures():
    """Analyze the test report to identify failing tests and their reasons."""
    
    try:
        with open('cognitive_architecture_test_report.json', 'r') as f:
            report = json.load(f)
        
        # Get detailed results
        detailed_results = report.get('detailed_results', {})
        
        print("🔍 ANALYSIS OF FAILING TESTS")
        print("=" * 50)
        
        failing_tests = []
        passing_tests = []
        
        # Analyze by phase
        for phase_name, phase_data in detailed_results.items():
            print(f"\n📊 {phase_name}")
            print(f"Total: {len(phase_data)} tests")
            
            phase_failures = []
            phase_successes = []
            
            for test in phase_data:
                if test.get('success', False):
                    phase_successes.append(test)
                else:
                    phase_failures.append(test)
                    failing_tests.append(test)
            
            print(f"✅ Passing: {len(phase_successes)}")
            print(f"❌ Failing: {len(phase_failures)}")
            
            # Show failing test details
            for test in phase_failures:
                print(f"  ❌ {test.get('test_id', 'Unknown')}: {test.get('name', 'Unknown')}")
                if 'error_message' in test:
                    print(f"     Error: {test['error_message']}")
                
                # Check response data for clues
                response_data = test.get('response_data', {})
                if response_data:
                    # Check what fields are missing that might be expected
                    print(f"     Response keys: {list(response_data.keys())}")
        
        print(f"\n📈 OVERALL SUMMARY")
        print(f"Total tests: {len(failing_tests) + len(passing_tests)}")
        print(f"Passing: {len(passing_tests)}")
        print(f"Failing: {len(failing_tests)}")
        print(f"Success rate: {len(passing_tests) / (len(failing_tests) + len(passing_tests)) * 100:.1f}%")
        
        # Identify common failure patterns
        print(f"\n🔍 FAILURE PATTERNS")
        error_types = {}
        for test in failing_tests:
            error = test.get('error_message', 'No error message')
            if error in error_types:
                error_types[error] += 1
            else:
                error_types[error] = 1
        
        for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count}x: {error}")
    
    except Exception as e:
        print(f"Error analyzing failures: {e}")
        return False
    
    return True

if __name__ == "__main__":
    analyze_test_failures()
