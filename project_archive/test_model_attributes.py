#!/usr/bin/env python3
"""Quick test to verify model attributes."""

from backend.metacognition_modules.cognitive_models import KnowledgeGap, CognitiveEvent

def test_model_attributes():
    """Test that model attributes exist."""
    
    # Test KnowledgeGap
    gap = KnowledgeGap()
    print("KnowledgeGap attributes:")
    for attr in dir(gap):
        if not attr.startswith('_'):
            value = getattr(gap, attr)
            if not callable(value):
                print(f"  {attr}: {type(value)} = {value}")
    
    print("\nCognitiveEvent attributes:")
    event = CognitiveEvent(type="reasoning")
    for attr in dir(event):
        if not attr.startswith('_'):
            value = getattr(event, attr)
            if not callable(value):
                print(f"  {attr}: {type(value)} = {value}")

if __name__ == "__main__":
    test_model_attributes()
