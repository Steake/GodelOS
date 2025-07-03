#!/usr/bin/env python3
"""Simple import test for cognitive models."""

import sys
print("Testing cognitive models imports...")

try:
    print("1. Importing basic modules...")
    from dataclasses import dataclass, field, asdict
    from datetime import datetime
    from enum import Enum, auto
    from typing import Any, Dict, List, Optional, Union
    import uuid
    print("✅ Basic imports successful")

    print("2. Importing cognitive_models module...")
    import backend.metacognition_modules.cognitive_models as cm
    print("✅ Module imported")

    print("3. Testing individual imports...")
    from backend.metacognition_modules.cognitive_models import CognitiveEventType
    print("✅ CognitiveEventType imported")

    from backend.metacognition_modules.cognitive_models import KnowledgeGap
    print("✅ KnowledgeGap imported")

    from backend.metacognition_modules.cognitive_models import CognitiveEvent
    print("✅ CognitiveEvent imported")

    from backend.metacognition_modules.cognitive_models import AcquisitionPlan
    print("✅ AcquisitionPlan imported")

    print("4. Testing model creation...")
    gap = KnowledgeGap()
    print(f"✅ KnowledgeGap created: {gap.id}")

    event = CognitiveEvent(type=CognitiveEventType.REASONING)
    print(f"✅ CognitiveEvent created: {event.event_id}")

    plan = AcquisitionPlan()
    print(f"✅ AcquisitionPlan created: {plan.plan_id}")

    print("🎉 All cognitive models working correctly!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
