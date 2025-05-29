#!/usr/bin/env python3
"""
Test script to isolate the initialization issue
"""

import sys
import os
import asyncio
import time
import logging

# Add the parent directory to Python path for GödelOS imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_initialization():
    """Test the GödelOS initialization step by step"""
    
    print("🔍 Step 1: Testing basic imports...", flush=True)
    try:
        from backend.godelos_integration import GödelOSIntegration
        print("✅ Step 1: GödelOSIntegration import successful", flush=True)
    except Exception as e:
        print(f"❌ Step 1: Failed to import GödelOSIntegration: {e}", flush=True)
        return
    
    print("🔍 Step 2: Creating GödelOS integration instance...")
    try:
        godelos_integration = GödelOSIntegration()
        print("✅ Step 2: GödelOS integration instance created")
    except Exception as e:
        print(f"❌ Step 2: Failed to create instance: {e}")
        return
    
    print("🔍 Step 3: Starting initialization...")
    try:
        start_time = time.time()
        await godelos_integration.initialize()
        end_time = time.time()
        print(f"✅ Step 3: Initialization completed in {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Step 3: Initialization failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return
    
    print("🔍 Step 4: Testing health status...")
    try:
        health_status = godelos_integration.get_health_status()
        print(f"✅ Step 4: Health status: {health_status}")
    except Exception as e:
        print(f"❌ Step 4: Failed to get health status: {e}")
        return
    
    print("🎉 All tests passed! Backend should work correctly.")

if __name__ == "__main__":
    print("🚀 Starting GödelOS Backend Initialization Test...", flush=True)
    asyncio.run(test_initialization())
