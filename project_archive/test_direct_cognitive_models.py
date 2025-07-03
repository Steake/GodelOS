#!/usr/bin/env python3
"""Direct test of cognitive models without package imports."""

import sys
import os

# Add the specific directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'metacognition_modules'))

print("Testing direct import of cognitive_models.py...")

try:
    print("1. Testing basic imports...")
    from dataclasses import dataclass, field, asdict
    from datetime import datetime
    from enum import Enum, auto
    from typing import Any, Dict, List, Optional, Union
    import uuid
    print("✅ Basic imports successful")

    print("2. Importing cognitive_models directly...")
    import cognitive_models as cm
    print("✅ Module imported directly")

    print("3. Testing individual classes...")
    gap = cm.KnowledgeGap()
    print(f"✅ KnowledgeGap created: {gap.id}")

    event = cm.CognitiveEvent(type=cm.CognitiveEventType.QUERY_STARTED)
    print(f"✅ CognitiveEvent created: {event.event_id}")

    plan = cm.AcquisitionPlan()
    print(f"✅ AcquisitionPlan created: {plan.plan_id}")

    print("🎉 All cognitive models working correctly via direct import!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
