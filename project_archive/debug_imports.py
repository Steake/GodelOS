import sys
import traceback

# Add the project root to the Python path
# This allows us to import 'backend' as a module
sys.path.insert(0, '.')

print("--- Starting Application Import Debugger ---")

try:
    print("Importing asyncio...")
    import asyncio
    print("Importing json...")
    import json
    print("Importing logging...")
    import logging
    print("Importing requests...")
    import requests
    print("Importing numpy...")
    import numpy as np
    print("--- Basic library imports successful ---")

except ImportError as e:
    print(f"\n\nCRITICAL FAILURE DURING BASIC IMPORT: {e}")
    traceback.print_exc()

print("\n--- Attempting to import application modules ---")
try:
    print("Importing backend.config...")
    from backend import config
    print("Importing backend.models...")
    from backend import models
    print("Importing backend.godelos_integration...")
    from backend import godelos_integration
    print("Importing backend.knowledge_pipeline_service...")
    from backend import knowledge_pipeline_service
    print("Importing backend.transparency_endpoints...")
    from backend import transparency_endpoints
    print("Importing backend.main...")
    from backend import main
    print("--- Application module imports successful ---")

except ImportError as e:
    print(f"\n\nFAILURE during application import: {e}")
    print("\n--- Traceback ---")
    traceback.print_exc()
    print("-----------------")
    print("\nThis error likely indicates a circular dependency. Check the imports in the file that failed.")

except Exception as e:
    print(f"\n\nAn unexpected error occurred: {e}")
    print("\n--- Traceback ---")
    traceback.print_exc()
    print("-----------------")
