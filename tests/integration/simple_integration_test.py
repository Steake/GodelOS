#!/usr/bin/env python3
"""
Simple test to check basic integration import.
"""

import sys
import os

# Add paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

print("🔍 Testing basic import...")

try:
    print("Step 1: Importing logging...")
    import logging
    print("✅ Logging imported")
    
    print("Step 2: Importing asyncio...")
    import asyncio
    print("✅ Asyncio imported")
    
    print("Step 3: Importing typing...")
    from typing import Dict, List, Optional, Any
    print("✅ Typing imported")
    
    print("Step 4: Checking backend path...")
    backend_path = os.path.join(project_root, 'backend')
    print(f"Backend path: {backend_path}")
    print(f"Backend exists: {os.path.exists(backend_path)}")
    
    print("Step 5: Checking integration file...")
    integration_file = os.path.join(backend_path, 'godelos_integration.py')
    print(f"Integration file: {integration_file}")
    print(f"Integration exists: {os.path.exists(integration_file)}")
    
    print("Step 6: Attempting import...")
    from backend.godelos_integration import GödelOSIntegration
    print("✅ Class import successful")
    
    print("Step 7: Creating instance...")
    integration = GödelOSIntegration()
    print("✅ Instance created successfully")
    print(f"✅ Instance type: {type(integration).__name__}")
    
    print("✅ All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
