import requests
import json
import time

BASE_URL = "http://localhost:8000"
KNOWLEDGE_ENDPOINT = f"{BASE_URL}/api/knowledge"
QUERY_ENDPOINT = f"{BASE_URL}/api/query"

def run_debug_test():
    """
    A focused test to debug the knowledge pipeline by adding a specific
    piece of knowledge and then immediately querying for it.
    """
    print("--- 🧠 Starting Knowledge Pipeline Debug Test ---")

    # 1. Define the specific piece of knowledge
    fact = {
        "source": "debug_test",
        "content": "The capital of Iceland is Reykjavik.",
        "type": "fact",
        "metadata": {"test_id": "kp_debug_001"}
    }
    print(f"\n1. ADDING KNOWLEDGE:\n{json.dumps(fact, indent=2)}")

    # 2. Add the knowledge to the system
    try:
        add_response = requests.post(KNOWLEDGE_ENDPOINT, json=fact, timeout=10)
        add_response.raise_for_status()
        print(f"\n   ✅ SUCCESS: Knowledge added. Server response:")
        print(json.dumps(add_response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"\n   ❌ FAILED to add knowledge: {e}")
        return

    # Give the backend a moment to process and index
    print("\n   ...waiting 2 seconds for indexing...")
    time.sleep(2)

    # 3. Define the query to retrieve the knowledge
    query = {
        "query": "What is the capital of Iceland?"
    }
    print(f"\n2. SENDING QUERY:\n{json.dumps(query, indent=2)}")

    # 4. Query the system
    try:
        query_response = requests.post(QUERY_ENDPOINT, json=query, timeout=10)
        query_response.raise_for_status()
        response_data = query_response.json()
        print(f"\n   ✅ SUCCESS: Query sent. Server response:")
        print(json.dumps(response_data, indent=2))

        # 5. Analyze the response
        print("\n3. ANALYSIS:")
        if "Reykjavik" in response_data.get("response", ""):
            print("   ✅ PASS: The response contains the correct specific knowledge.")
        else:
            print("   ❌ FAIL: The response did NOT contain the specific knowledge.")
            print("      This confirms a failure in the indexing-to-retrieval loop.")

    except requests.exceptions.RequestException as e:
        print(f"\n   ❌ FAILED to send query: {e}")

    print("\n--- 🧠 Debug Test Complete ---")

if __name__ == "__main__":
    run_debug_test()
