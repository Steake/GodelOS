#!/usr/bin/env python3
import requests
import json
import time

def send_test_event():
    url = "http://localhost:8000/api/enhanced-cognitive/events"
    headers = {"Content-Type": "application/json"}
    
    event_data = {
        "type": "THOUGHT",
        "data": {
            "content": "Test event after frontend fix - should appear in Stream of Consciousness!",
            "source": "python_test",
            "priority": "high",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
    }
    
    try:
        response = requests.post(url, json=event_data, headers=headers)
        print(f"✅ Event sent successfully: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Failed to send event: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Sending test cognitive event...")
    send_test_event()
