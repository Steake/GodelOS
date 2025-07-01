print("--- Starting Ultra-Basic Import Debugger ---")

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

except Exception as e:
    print(f"\n\nCRITICAL FAILURE DURING BASIC IMPORT: {e}")
