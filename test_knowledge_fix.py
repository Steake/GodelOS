#!/usr/bin/env python3
"""
Simple test script to verify the knowledge pipeline fix works
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.godelos_integration import GödelOSIntegration

async def test_knowledge_pipeline():
    """Test the knowledge pipeline functionality"""
    print("🧠 Testing Knowledge Pipeline Fix")
    print("=" * 50)
    
    # 1. Initialize integration
    integration = GödelOSIntegration()
    await integration.initialize()
    print("✅ Integration initialized")
    
    # 2. Add knowledge
    test_knowledge = "The capital of Iceland is Reykjavik."
    result = await integration.add_knowledge(
        content=test_knowledge,
        knowledge_type="fact",
        context_id="geography"
    )
    print(f"✅ Knowledge added: {result}")
    
    # 3. Query the knowledge
    query = "What is the capital of Iceland?"
    response = await integration.process_natural_language_query(
        query=query,
        include_reasoning=True
    )
    print(f"🔍 Query: {query}")
    print(f"📋 Response: {response['response']}")
    print(f"🎯 Confidence: {response['confidence']}")
    print(f"📚 Knowledge used: {response['knowledge_used']}")
    
    # 4. Check if the response contains the expected information
    if "reykjavik" in response['response'].lower():
        print("✅ SUCCESS: Knowledge pipeline is working correctly!")
        return True
    else:
        print("❌ FAILURE: Knowledge pipeline is not working correctly")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_knowledge_pipeline())
    sys.exit(0 if result else 1)
