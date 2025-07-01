#!/usr/bin/env python3
"""
Simple test to start backend server with minimal initialization
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

import uvicorn
from fastapi import FastAPI

# Simple FastAPI app for testing
app = FastAPI(title="GödelOS Backend Test")

@app.get("/")
async def root():
    return {"message": "Test backend is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting minimal test backend...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
