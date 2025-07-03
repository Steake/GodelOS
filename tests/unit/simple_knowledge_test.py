#!/usr/bin/env python3
"""
Simple Knowledge Test

Test basic knowledge functionality.
"""

def test_simple_knowledge():
    """Test simple knowledge functionality."""
    print("Testing simple knowledge functionality...")
    
    # Simple test knowledge
    knowledge_base = {
        "ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and act like humans.",
        "logic": "Logic is the systematic study of the principles of valid inference and correct reasoning.",
        "ml": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience."
    }
    
    print(f"Knowledge base has {len(knowledge_base)} items")
    
    # Test search
    query = "artificial intelligence"
    
    matches = []
    for key, content in knowledge_base.items():
        if any(word in content.lower() for word in query.lower().split()):
            matches.append((key, content))
    
    print(f"Query '{query}' found {len(matches)} matches:")
    for key, content in matches:
        print(f"  - {key}: {content[:80]}...")
    
    return len(matches) > 0

if __name__ == "__main__":
    success = test_simple_knowledge()
    print(f"Test {'PASSED' if success else 'FAILED'}")
