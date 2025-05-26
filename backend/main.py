#!/usr/bin/env python3
"""
GödelOS Backend API

FastAPI backend that interfaces with the GödelOS system to provide:
- Natural language query processing
- Knowledge base management
- Real-time cognitive state monitoring
- WebSocket streaming for cognitive events
"""

import asyncio
import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the parent directory to Python path for GödelOS imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.godelos_integration import GödelOSIntegration
from backend.websocket_manager import WebSocketManager
from backend.models import (
    QueryRequest, QueryResponse, KnowledgeRequest, KnowledgeResponse,
    CognitiveStateResponse, ErrorResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
godelos_integration: Optional[GödelOSIntegration] = None
websocket_manager: WebSocketManager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global godelos_integration
    
    # Startup
    logger.info("Initializing GödelOS system...")
    try:
        godelos_integration = GödelOSIntegration()
        await godelos_integration.initialize()
        logger.info("GödelOS system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize GödelOS system: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GödelOS system...")
    if godelos_integration:
        await godelos_integration.shutdown()


# Create FastAPI app
app = FastAPI(
    title="GödelOS API",
    description="Backend API for the GödelOS web demonstration interface",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "GödelOS API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    health_status = await godelos_integration.get_health_status()
    return {
        "status": "healthy" if health_status["healthy"] else "unhealthy",
        "timestamp": time.time(),
        "details": health_status
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Process the query through GödelOS
        result = await godelos_integration.process_natural_language_query(
            request.query,
            context=request.context,
            include_reasoning=request.include_reasoning
        )
        
        # Broadcast cognitive events if WebSocket clients are connected
        if websocket_manager.has_connections():
            cognitive_event = {
                "type": "query_processed",
                "timestamp": time.time(),
                "query": request.query,
                "response": result["response"],
                "reasoning_steps": result.get("reasoning_steps", []),
                "inference_time_ms": result.get("inference_time_ms", 0)
            }
            await websocket_manager.broadcast(cognitive_event)
        
        return QueryResponse(
            response=result["response"],
            confidence=result.get("confidence", 1.0),
            reasoning_steps=result.get("reasoning_steps", []),
            inference_time_ms=result.get("inference_time_ms", 0),
            knowledge_used=result.get("knowledge_used", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.get("/api/knowledge", response_model=KnowledgeResponse)
async def get_knowledge(
    context_id: Optional[str] = None,
    knowledge_type: Optional[str] = None,
    limit: int = 100
):
    """Retrieve knowledge base information."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        knowledge_data = await godelos_integration.get_knowledge(
            context_id=context_id,
            knowledge_type=knowledge_type,
            limit=limit
        )
        
        return KnowledgeResponse(
            facts=knowledge_data.get("facts", []),
            rules=knowledge_data.get("rules", []),
            concepts=knowledge_data.get("concepts", []),
            total_count=knowledge_data.get("total_count", 0),
            context_id=context_id
        )
        
    except Exception as e:
        logger.error(f"Error retrieving knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge retrieval failed: {str(e)}")


@app.post("/api/knowledge", response_model=Dict[str, str])
async def add_knowledge(request: KnowledgeRequest):
    """Add new knowledge to the system."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        result = await godelos_integration.add_knowledge(
            content=request.content,
            knowledge_type=request.knowledge_type,
            context_id=request.context_id,
            metadata=request.metadata
        )
        
        # Broadcast knowledge update event
        if websocket_manager.has_connections():
            knowledge_event = {
                "type": "knowledge_added",
                "timestamp": time.time(),
                "knowledge_type": request.knowledge_type,
                "context_id": request.context_id,
                "content": request.content
            }
            await websocket_manager.broadcast(knowledge_event)
        
        return {"status": "success", "message": result.get("message", "Knowledge added successfully")}
        
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge addition failed: {str(e)}")


@app.get("/api/cognitive-state", response_model=CognitiveStateResponse)
async def get_cognitive_state():
    """Get current cognitive layer states."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        cognitive_state = await godelos_integration.get_cognitive_state()
        
        return CognitiveStateResponse(
            manifest_consciousness=cognitive_state.get("manifest_consciousness", {}),
            agentic_processes=cognitive_state.get("agentic_processes", []),
            daemon_threads=cognitive_state.get("daemon_threads", []),
            working_memory=cognitive_state.get("working_memory", {}),
            attention_focus=cognitive_state.get("attention_focus", []),
            metacognitive_state=cognitive_state.get("metacognitive_state", {}),
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"Error getting cognitive state: {e}")
        raise HTTPException(status_code=500, detail=f"Cognitive state retrieval failed: {str(e)}")


@app.websocket("/ws/cognitive-stream")
async def cognitive_stream_websocket(websocket: WebSocket):
    """WebSocket endpoint for streaming real-time cognitive events."""
    await websocket_manager.connect(websocket)
    
    try:
        # Send initial cognitive state
        if godelos_integration:
            initial_state = await godelos_integration.get_cognitive_state()
            await websocket.send_json({
                "type": "initial_state",
                "timestamp": time.time(),
                "data": initial_state
            })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (e.g., subscription preferences)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "subscribe":
                    # Handle subscription to specific event types
                    event_types = message.get("event_types", [])
                    await websocket_manager.subscribe_to_events(websocket, event_types)
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "event_types": event_types
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status_code": 500}


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )