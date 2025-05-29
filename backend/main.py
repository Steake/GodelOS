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
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the parent directory to Python path for GödelOS imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.godelos_integration import GödelOSIntegration
from backend.websocket_manager import WebSocketManager
from backend.cognitive_transparency_integration import cognitive_transparency_api
from backend.models import (
    QueryRequest, QueryResponse, KnowledgeRequest, KnowledgeResponse,
    CognitiveStateResponse, ErrorResponse
)
from backend.knowledge_models import (
    URLImportRequest, FileImportRequest, WikipediaImportRequest,
    TextImportRequest, BatchImportRequest, SearchQuery, Category,
    ImportSource
)
from backend.knowledge_ingestion import knowledge_ingestion_service
from backend.knowledge_management import knowledge_management_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize WebSocket manager early (after logger is defined)
websocket_manager = WebSocketManager()

# Set WebSocket manager on services immediately
logger.info(f"🔍 IMPORT: Setting websocket_manager on services at import time")
knowledge_ingestion_service.websocket_manager = websocket_manager
logger.info(f"🔍 IMPORT: WebSocket manager set on knowledge_ingestion_service: {knowledge_ingestion_service.websocket_manager is not None}")

# Set knowledge management service reference for real-time updates
import backend.knowledge_ingestion as ki_module
ki_module.knowledge_management_service = knowledge_management_service
logger.info(f"🔍 IMPORT: Connected knowledge ingestion to knowledge management service")

# Global instances
godelos_integration: Optional[GödelOSIntegration] = None
# websocket_manager already initialized above at line 52
cognitive_streaming_task: Optional[asyncio.Task] = None


async def continuous_cognitive_streaming():
    """Background task to continuously stream cognitive state updates."""
    global godelos_integration, websocket_manager
    
    logger.info("Starting continuous cognitive streaming...")
    
    while True:
        try:
            # Only stream if there are active WebSocket connections
            if websocket_manager.has_connections() and godelos_integration:
                # Get current cognitive state from GödelOS
                cognitive_state = await godelos_integration.get_cognitive_state()
                
                # Format the data to match frontend expectations
                formatted_data = {
                    "timestamp": time.time(),
                    "manifest_consciousness": {
                        "attention_focus": cognitive_state.get("attention_focus", [{}])[0].get("salience", 0.5) * 100,
                        "working_memory": [
                            item.get("content", "Processing...")
                            for item in cognitive_state.get("working_memory", {}).get("active_items", [])
                        ] or ["System monitoring", "Background processing"]
                    },
                    "agentic_processes": [
                        {
                            "name": process.get("description", "Unknown Process"),
                            "status": "active" if process.get("status") == "active" else "idle",
                            "cpu_usage": process.get("progress", 0.5) * 100,
                            "memory_usage": 50 + (process.get("priority", 5) * 5)
                        }
                        for process in cognitive_state.get("agentic_processes", [])
                    ] or [
                        {"name": "Query Parser", "status": "idle", "cpu_usage": 20, "memory_usage": 30},
                        {"name": "Knowledge Retriever", "status": "idle", "cpu_usage": 15, "memory_usage": 25},
                        {"name": "Inference Engine", "status": "active", "cpu_usage": 45, "memory_usage": 60},
                        {"name": "Response Generator", "status": "idle", "cpu_usage": 10, "memory_usage": 20},
                        {"name": "Meta-Reasoner", "status": "active", "cpu_usage": 35, "memory_usage": 40}
                    ],
                    "daemon_threads": [
                        {
                            "name": process.get("description", "Unknown Daemon"),
                            "active": process.get("status") == "running",
                            "activity_level": process.get("progress", 0.5) * 100
                        }
                        for process in cognitive_state.get("daemon_threads", [])
                    ] or [
                        {"name": "Memory Consolidation", "active": True, "activity_level": 60},
                        {"name": "Background Learning", "active": True, "activity_level": 40},
                        {"name": "System Monitoring", "active": True, "activity_level": 80},
                        {"name": "Knowledge Indexing", "active": False, "activity_level": 10},
                        {"name": "Pattern Recognition", "active": True, "activity_level": 70}
                    ]
                }
                
                # Broadcast cognitive state update
                await websocket_manager.broadcast({
                    "type": "cognitive_state_update",
                    "timestamp": time.time(),
                    "data": formatted_data
                })
                
                logger.debug("Broadcasted cognitive state update")
            
            # Wait 4 seconds before next update
            await asyncio.sleep(4)
            
        except Exception as e:
            logger.error(f"Error in cognitive streaming: {e}")
            await asyncio.sleep(5)  # Wait longer on error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global godelos_integration, cognitive_streaming_task
    
    # Startup
    logger.info("🔍 BACKEND DIAGNOSTIC: Starting GödelOS system initialization...")
    try:
        logger.info("🔍 BACKEND DIAGNOSTIC: Creating GödelOS integration instance...")
        godelos_integration = GödelOSIntegration()
        
        logger.info("🔍 BACKEND DIAGNOSTIC: Calling initialize() method...")
        await godelos_integration.initialize()
        logger.info("✅ BACKEND DIAGNOSTIC: GödelOS system initialized successfully")
        
        # Initialize cognitive transparency system
        logger.info("🔍 BACKEND DIAGNOSTIC: Initializing cognitive transparency system...")
        await cognitive_transparency_api.initialize(godelos_integration)
        logger.info("✅ BACKEND DIAGNOSTIC: Cognitive transparency system initialized successfully")
        
        # Initialize knowledge ingestion and management services
        logger.info("🔍 BACKEND DIAGNOSTIC: Initializing knowledge services...")
        await knowledge_ingestion_service.initialize()
        await knowledge_management_service.initialize()
        logger.info("✅ BACKEND DIAGNOSTIC: Knowledge ingestion and management services initialized successfully")
        
        # Start continuous cognitive streaming
        logger.info("🔍 BACKEND DIAGNOSTIC: Starting cognitive streaming task...")
        cognitive_streaming_task = asyncio.create_task(continuous_cognitive_streaming())
        logger.info("✅ BACKEND DIAGNOSTIC: Started continuous cognitive streaming task")
        
    except Exception as e:
        logger.error(f"❌ BACKEND DIAGNOSTIC: Failed to initialize GödelOS system: {e}")
        logger.error(f"❌ BACKEND DIAGNOSTIC: Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ BACKEND DIAGNOSTIC: Full traceback: {traceback.format_exc()}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GödelOS system...")
    
    # Stop cognitive streaming task
    if cognitive_streaming_task:
        cognitive_streaming_task.cancel()
        try:
            await cognitive_streaming_task
        except asyncio.CancelledError:
            pass
        logger.info("Stopped cognitive streaming task")
    
    # Shutdown cognitive transparency system
    await cognitive_transparency_api.shutdown()
    
    # Shutdown knowledge services
    await knowledge_ingestion_service.shutdown()
    logger.info("Knowledge services shutdown complete")
    
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

# Include cognitive transparency routes
app.include_router(cognitive_transparency_api.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "GödelOS API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed diagnostics."""
    logger.info("🔍 BACKEND DIAGNOSTIC: Health check requested")
    
    if not godelos_integration:
        logger.error("❌ BACKEND DIAGNOSTIC: GödelOS integration not initialized")
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        health_status = await godelos_integration.get_health_status()
        logger.info(f"🔍 BACKEND DIAGNOSTIC: Health status retrieved: {health_status}")
        
        is_healthy = health_status.get("healthy", False)
        logger.info(f"🔍 BACKEND DIAGNOSTIC: System healthy: {is_healthy}")
        
        if not is_healthy:
            logger.warn(f"⚠️ BACKEND DIAGNOSTIC: System unhealthy - Components: {health_status.get('components', {})}")
            logger.warn(f"⚠️ BACKEND DIAGNOSTIC: Error count: {health_status.get('error_count', 0)}")
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": time.time(),
            "details": health_status
        }
    except Exception as e:
        logger.error(f"❌ BACKEND DIAGNOSTIC: Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


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
# Knowledge Ingestion API Endpoints

@app.post("/api/knowledge/import/url")
async def import_from_url(request: URLImportRequest):
    """Import knowledge from a URL."""
    try:
        import_id = await knowledge_ingestion_service.import_from_url(request)
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "url",
                "source": str(request.url)
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_id": import_id, "status": "queued"}
        
    except Exception as e:
        logger.error(f"Error starting URL import: {e}")
        raise HTTPException(status_code=500, detail=f"URL import failed: {str(e)}")


@app.post("/api/knowledge/import/file")
async def import_from_file(
    file: UploadFile = File(...),
    filename: str = Form(...),
    file_type: str = Form(...),
    encoding: str = Form(default="utf-8"),
    categorization_hints: str = Form(default="[]")
):
    """Import knowledge from an uploaded file."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse categorization hints
        try:
            hints = json.loads(categorization_hints)
        except:
            hints = []
        
        # Determine file type from extension if not provided properly
        if not file_type or file_type == "application/octet-stream":
            ext = filename.lower().split('.')[-1] if '.' in filename else 'txt'
            file_type_map = {
                'pdf': 'pdf',
                'txt': 'txt',
                'json': 'json',
                'csv': 'csv',
                'docx': 'docx',
                'md': 'txt'
            }
            file_type = file_type_map.get(ext, 'txt')
        
        # Create import request with proper structure
        request = FileImportRequest(
            source=ImportSource(
                source_type="file",
                source_identifier=filename,
                metadata={"original_filename": filename}
            ),
            filename=filename,
            file_type=file_type,
            encoding=encoding,
            categorization_hints=hints,
            processing_options={},
            priority=5
        )
        
        import_id = await knowledge_ingestion_service.import_from_file(request, file_content)
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "file",
                "source": filename
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_id": import_id, "status": "queued"}
        
    except Exception as e:
        logger.error(f"Error starting file import: {e}")
        raise HTTPException(status_code=500, detail=f"File import failed: {str(e)}")


@app.post("/api/knowledge/import/wikipedia")
async def import_from_wikipedia(request: WikipediaImportRequest):
    """Import knowledge from Wikipedia."""
    try:
        import_id = await knowledge_ingestion_service.import_from_wikipedia(request)
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "wikipedia",
                "source": request.page_title
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_id": import_id, "status": "queued"}
        
    except Exception as e:
        logger.error(f"Error starting Wikipedia import: {e}")
        raise HTTPException(status_code=500, detail=f"Wikipedia import failed: {str(e)}")


@app.post("/api/knowledge/import/text")
async def import_from_text(request: TextImportRequest):
    """Import knowledge from manual text input."""
    try:
        import_id = await knowledge_ingestion_service.import_from_text(request)
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "text",
                "source": request.title or "Manual Text"
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_id": import_id, "status": "queued"}
        
    except Exception as e:
        logger.error(f"Error starting text import: {e}")
        raise HTTPException(status_code=500, detail=f"Text import failed: {str(e)}")


@app.post("/api/knowledge/import/batch")
async def batch_import(request: BatchImportRequest):
    """Process multiple import requests in batch."""
    try:
        import_ids = await knowledge_ingestion_service.batch_import(request)
        
        # Broadcast batch import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "batch_import_started",
                "timestamp": time.time(),
                "import_ids": import_ids,
                "batch_size": len(import_ids)
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_ids": import_ids, "status": "queued", "batch_size": len(import_ids)}
        
    except Exception as e:
        logger.error(f"Error starting batch import: {e}")
        raise HTTPException(status_code=500, detail=f"Batch import failed: {str(e)}")


@app.get("/api/knowledge/import/progress/{import_id}")
async def get_import_progress(import_id: str):
    """Get the progress of an import operation."""
    try:
        progress = await knowledge_ingestion_service.get_import_progress(import_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Import operation not found")
        
        return progress.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting import progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get import progress: {str(e)}")


@app.delete("/api/knowledge/import/{import_id}")
async def cancel_import(import_id: str):
    """Cancel an import operation."""
    try:
        success = await knowledge_ingestion_service.cancel_import(import_id)
        if not success:
            raise HTTPException(status_code=404, detail="Import operation not found or cannot be cancelled")
        
        return {"status": "cancelled", "import_id": import_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling import: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel import: {str(e)}")


# Knowledge Management API Endpoints

@app.get("/api/knowledge/search")
async def search_knowledge(
    query: str,
    search_type: str = "hybrid",
    knowledge_types: Optional[str] = None,
    categories: Optional[str] = None,
    source_types: Optional[str] = None,
    confidence_threshold: float = 0.0,
    max_results: int = 50,
    include_snippets: bool = True,
    highlight_terms: bool = True
):
    """Search the knowledge base."""
    try:
        # Parse list parameters
        knowledge_types_list = json.loads(knowledge_types) if knowledge_types else []
        categories_list = json.loads(categories) if categories else []
        source_types_list = json.loads(source_types) if source_types else []
        
        search_query = SearchQuery(
            query_text=query,
            search_type=search_type,
            knowledge_types=knowledge_types_list,
            categories=categories_list,
            source_types=source_types_list,
            confidence_threshold=confidence_threshold,
            max_results=max_results,
            include_snippets=include_snippets,
            highlight_terms=highlight_terms
        )
        
        results = await knowledge_management_service.search_knowledge(search_query)
        return results.model_dump()
        
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {str(e)}")


@app.get("/api/knowledge/{item_id}")
async def get_knowledge_item(item_id: str):
    """Get a specific knowledge item by ID."""
    try:
        item = await knowledge_management_service.get_knowledge_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return item.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge item: {str(e)}")


@app.delete("/api/knowledge/{item_id}")
async def delete_knowledge_item(item_id: str):
    """Delete a knowledge item."""
    try:
        success = await knowledge_management_service.delete_knowledge_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        # Broadcast deletion event
        if websocket_manager.has_connections():
            delete_event = {
                "type": "knowledge_deleted",
                "timestamp": time.time(),
                "item_id": item_id
            }
            await websocket_manager.broadcast(delete_event)
        
        return {"status": "deleted", "item_id": item_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete knowledge item: {str(e)}")


@app.get("/api/knowledge/categories")
async def get_categories():
    """Get all knowledge categories."""
    try:
        categories = await knowledge_management_service.get_categories()
        return [category.model_dump() for category in categories]
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@app.post("/api/knowledge/categories")
async def create_category(category: Category):
    """Create a new knowledge category."""
    try:
        success = await knowledge_management_service.create_category(category)
        if not success:
            raise HTTPException(status_code=409, detail="Category already exists")
        
        return {"status": "created", "category_id": category.category_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")


@app.post("/api/knowledge/categorize")
async def categorize_items(
    item_ids: List[str],
    categories: List[str]
):
    """Add categories to knowledge items."""
    try:
        updated_count = await knowledge_management_service.categorize_items(item_ids, categories)
        
        return {"status": "updated", "updated_count": updated_count}
        
    except Exception as e:
        logger.error(f"Error categorizing items: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to categorize items: {str(e)}")


@app.get("/api/knowledge/statistics")
async def get_knowledge_statistics():
    """Get knowledge base analytics and statistics."""
    try:
        stats = await knowledge_management_service.get_knowledge_statistics()
        return stats.model_dump()
        
    except Exception as e:
        logger.error(f"Error getting knowledge statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge statistics: {str(e)}")


@app.get("/api/knowledge/export")
async def export_knowledge(
    format: str = "json",
    categories: Optional[str] = None,
    source_types: Optional[str] = None,
    include_metadata: bool = True
):
    """Export knowledge base in various formats."""
    try:
        # This would implement export functionality
        # For now, return a placeholder response
        return {
            "status": "export_ready",
            "format": format,
            "message": "Export functionality will be implemented in the next iteration"
        }
        
    except Exception as e:
        logger.error(f"Error exporting knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export knowledge: {str(e)}")
    return {"error": "Internal server error", "status_code": 500}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Initializing backend services...")
    
    try:
        # Initialize knowledge ingestion service with websocket manager
        logger.info(f"🔍 STARTUP: Initializing knowledge_ingestion_service with websocket_manager")
        logger.info(f"🔍 STARTUP: WebSocket manager available: {websocket_manager is not None}")
        await knowledge_ingestion_service.initialize(websocket_manager)
        logger.info("Knowledge ingestion service initialized")
        
        # Initialize knowledge management service
        await knowledge_management_service.initialize()
        logger.info("Knowledge management service initialized")
        
        logger.info("All backend services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Don't raise here as it would prevent the server from starting
        # The endpoints will handle errors gracefully


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown."""
    logger.info("Shutting down backend services...")
    
    try:
        await knowledge_ingestion_service.shutdown()
        logger.info("Knowledge ingestion service shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down knowledge ingestion service: {e}")


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )