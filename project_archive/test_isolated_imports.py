#!/usr/bin/env python3
"""Minimal test to isolate import issues."""

import sys
import time

def test_step_by_step():
    """Test imports one by one to isolate the issue."""
    
    print("Step 1: Testing standard library imports...")
    import asyncio, json, logging, time
    from typing import Dict, List, Optional, Set, Any
    from enum import Enum
    print("✅ Standard library imports work")
    
    print("Step 2: Testing direct cognitive models import...")
    # Import the file directly without going through the package
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cognitive_models", 
        "backend/metacognition_modules/cognitive_models.py"
    )
    cognitive_models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cognitive_models)
    print("✅ Direct cognitive models import works")
    
    print("Step 3: Testing websocket manager without main.py...")
    # Test if we can import websocket manager directly
    spec = importlib.util.spec_from_file_location(
        "websocket_manager", 
        "backend/websocket_manager.py"
    )
    websocket_manager = importlib.util.module_from_spec(spec)
    
    start_time = time.time()
    spec.loader.exec_module(websocket_manager)
    elapsed = time.time() - start_time
    print(f"✅ Websocket manager direct import works in {elapsed:.2f}s")
    
    print("Step 4: Testing package imports...")
    sys.path.insert(0, '.')
    
    # Try importing backend.websocket_manager through the package
    start_time = time.time()
    import backend.websocket_manager
    elapsed = time.time() - start_time
    print(f"✅ Backend websocket manager package import works in {elapsed:.2f}s")
    
    print("🎉 All isolated tests passed!")

if __name__ == "__main__":
    test_step_by_step()
