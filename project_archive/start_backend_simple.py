#!/usr/bin/env python3
"""
Simple backend startup script for godelOS
"""
import sys
import os
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_backend():
    """Start the backend server"""
    try:
        print("🚀 Starting godelOS Backend...")
        from backend.main import app
        import uvicorn
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_backend()
