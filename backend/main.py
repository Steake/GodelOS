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
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add the parent directory to Python path for GödelOS imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.godelos_integration import GödelOSIntegration
from backend.websocket_manager import WebSocketManager
from backend.cognitive_transparency_integration import cognitive_transparency_api
from backend.enhanced_cognitive_api import router as enhanced_cognitive_router
from backend.config_manager import get_config, is_feature_enabled
from backend.models import (
    QueryRequest, QueryResponse, KnowledgeRequest, KnowledgeResponse,
    CognitiveStateResponse, ErrorResponse, SimpleKnowledgeRequest
)
from backend.knowledge_models import (
    URLImportRequest, FileImportRequest, WikipediaImportRequest,
    TextImportRequest, BatchImportRequest, SearchQuery, Category,
    ImportSource
)
from backend.knowledge_ingestion import knowledge_ingestion_service
from backend.knowledge_management import knowledge_management_service
from backend.knowledge_pipeline_service import knowledge_pipeline_service

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

# Set websocket manager on knowledge pipeline service
knowledge_pipeline_service.websocket_manager = websocket_manager
logger.info(f"🔍 IMPORT: WebSocket manager set on knowledge_pipeline_service")

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
        
        # Initialize knowledge pipeline service
        logger.info("🔍 BACKEND DIAGNOSTIC: Initializing knowledge pipeline service...")
        await knowledge_pipeline_service.initialize(websocket_manager)
        logger.info("✅ BACKEND DIAGNOSTIC: Knowledge pipeline service initialized successfully")
        
        # Initialize enhanced cognitive API
        logger.info("🔍 BACKEND DIAGNOSTIC: Initializing enhanced cognitive API...")
        from backend.enhanced_cognitive_api import initialize_enhanced_cognitive
        await initialize_enhanced_cognitive(websocket_manager, godelos_integration)
        logger.info("✅ BACKEND DIAGNOSTIC: Enhanced cognitive API initialized successfully")
        
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

# Get environment mode for CORS configuration
import re
ENVIRONMENT = os.getenv("GODELOS_ENVIRONMENT", "development")

# Configure CORS based on environment
if ENVIRONMENT == "production":
    # Strict CORS for production
    allowed_origins = [
        "https://godelos.com",
        "https://www.godelos.com",
        # Add your production domains here
    ]
    logger.info("🔒 CORS configured for production mode")
else:
    # Flexible CORS for development - allow any localhost port
    allowed_origins = [
        # Use regex pattern for any localhost port
        "http://localhost:*",
        "http://127.0.0.1:*"
    ]
    # For FastAPI, we need to use the origin callback approach for wildcard ports
    def cors_origin_check(origin: str) -> bool:
        """Check if origin is allowed for development."""
        if not origin:
            return False
        
        # Allow any localhost or 127.0\.0\.1 with any port for development
        localhost_pattern = re.compile(r'^https?://(localhost|127\.0\.0\.1):\d+$')
        return bool(localhost_pattern.match(origin))
    
    logger.info("🔓 CORS configured for development mode - allowing all localhost ports")

# Add CORS middleware with dynamic origin handling for development
if ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

logger.info(f"🔗 CORS configured for {ENVIRONMENT} mode")

# Include cognitive transparency routes
app.include_router(cognitive_transparency_api.router)
app.include_router(enhanced_cognitive_router, prefix="/api/enhanced-cognitive", tags=["Enhanced Cognitive API"])


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


@app.get("/api/health")
async def api_health_check():
    """Health check endpoint with API prefix (alias for /health)."""
    return await health_check()


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query using advanced semantic search."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        logger.info(f"Processing query: {request.query}")
        
        # First try semantic search if pipeline is available
        semantic_results = None
        if knowledge_pipeline_service.initialized:
            try:
                logger.info("🔍 Using advanced semantic search")
                semantic_results = await knowledge_pipeline_service.semantic_query(
                    request.query, 
                    k=5
                )
            except Exception as e:
                logger.warning(f"⚠️ Semantic search failed, falling back to basic: {e}")
        
        # Process the query through GödelOS (with semantic context if available)
        context = request.context or {}
        if semantic_results and semantic_results.get('success'):
            context['semantic_results'] = semantic_results['results']
            context['semantic_search_used'] = True
        
        result = await godelos_integration.process_natural_language_query(
            request.query,
            context=context,
            include_reasoning=request.include_reasoning
        )
        
        # Enhance response with semantic results if available
        if semantic_results and semantic_results.get('success'):
            result['semantic_results'] = semantic_results['results']
            result['semantic_search_time'] = semantic_results.get('query_time_seconds', 0)
        
        # Broadcast cognitive events if WebSocket clients are connected
        if websocket_manager.has_connections():
            cognitive_event = {
                "type": "query_processed",
                "timestamp": time.time(),
                "query": request.query,
                "response": result["response"],
                "reasoning_steps": result.get("reasoning_steps", []),
                "inference_time_ms": result.get("inference_time_ms", 0),
                "semantic_search_used": semantic_results is not None and semantic_results.get('success', False)
            }
            await websocket_manager.broadcast(cognitive_event)
        
        return QueryResponse(
            response=result["response"],
            confidence=result.get("confidence", 1.0),
            reasoning_steps=result.get("reasoning_steps", []),
            inference_time_ms=result.get("inference_time_ms", 0),
            knowledge_used=result.get("knowledge_used", []),
            # Test criteria fields
            response_generated=result.get("response_generated"),
            domains_integrated=result.get("domains_integrated"),
            novel_connections=result.get("novel_connections"),
            knowledge_gaps_identified=result.get("knowledge_gaps_identified"),
            acquisition_plan_created=result.get("acquisition_plan_created"),
            self_reference_depth=result.get("self_reference_depth"),
            coherent_self_model=result.get("coherent_self_model"),
            novelty_score=result.get("novelty_score"),
            feasibility_score=result.get("feasibility_score"),
            uncertainty_expressed=result.get("uncertainty_expressed"),
            confidence_calibrated=result.get("confidence_calibrated"),
            graceful_degradation=result.get("graceful_degradation"),
            priority_management=result.get("priority_management")
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.get("/api/simple-test")
async def simple_test():
    """Simple test route."""
    return {"message": "simple test works", "timestamp": time.time()}


# Knowledge API Routes

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


@app.post("/api/knowledge")
async def add_knowledge(request: Union[KnowledgeRequest, Dict[str, Any]]):
    """Add new knowledge to the system."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        # Handle both KnowledgeRequest and simple dict formats
        if isinstance(request, dict):
            # Try to convert dict to SimpleKnowledgeRequest for validation
            try:
                simple_request = SimpleKnowledgeRequest(**request)
                knowledge_request = simple_request.to_knowledge_request()
            except Exception as e:
                # If that fails, try to create KnowledgeRequest directly
                knowledge_request = KnowledgeRequest(
                    content=request.get('content', request.get('definition', request.get('concept', ''))),
                    knowledge_type=request.get('knowledge_type', 'concept'),
                    context_id=request.get('context_id', request.get('category')),
                    metadata=request.get('metadata', {'category': request.get('category', 'general')})
                )
        else:
            knowledge_request = request
        
        result = await godelos_integration.add_knowledge(
            content=knowledge_request.content,
            knowledge_type=knowledge_request.knowledge_type,
            context_id=knowledge_request.context_id,
            metadata=knowledge_request.metadata
        )
        
        # Broadcast knowledge update event
        if websocket_manager.has_connections():
            knowledge_event = {
                "type": "knowledge_added",
                "timestamp": time.time(),
                "knowledge_type": knowledge_request.knowledge_type,
                "context_id": knowledge_request.context_id,
                "content": knowledge_request.content
            }
            await websocket_manager.broadcast(knowledge_event)
        
        return result
        
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge addition failed: {str(e)}")


@app.get("/api/cognitive-state")
async def get_cognitive_state():
    """Get current cognitive layer states."""
    if not godelos_integration:
        raise HTTPException(status_code=503, detail="GödelOS system not initialized")
    
    try:
        cognitive_state = await godelos_integration.get_cognitive_state()
        cognitive_state["timestamp"] = time.time()
        return cognitive_state
        
    except Exception as e:
        logger.error(f"Error getting cognitive state: {e}")
        raise HTTPException(status_code=500, detail=f"Cognitive state retrieval failed: {str(e)}")


# Advanced Knowledge Pipeline API Endpoints

@app.post("/api/knowledge/pipeline/process")
async def process_text_with_pipeline(
    content: str = Form(...),
    title: str = Form(default="Untitled"),
    metadata: str = Form(default="{}")
):
    """Process text content through the advanced knowledge extraction pipeline."""
    try:
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
        except:
            metadata_dict = {}
        
        # Check if pipeline is available
        if not knowledge_pipeline_service.initialized:
            raise HTTPException(status_code=503, detail="Knowledge pipeline not initialized")
        
        # Process through pipeline
        result = await knowledge_pipeline_service.process_text_document(
            content=content,
            title=title,
            metadata=metadata_dict
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")


@app.post("/api/knowledge/pipeline/semantic-search")
async def semantic_search(
    query: str = Form(...),
    k: int = Form(default=5)
):
    """Perform semantic search using the advanced query engine."""
    try:
        if not knowledge_pipeline_service.initialized:
            raise HTTPException(status_code=503, detail="Knowledge pipeline not initialized")
        
        result = await knowledge_pipeline_service.semantic_query(query, k=k)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@app.get("/api/knowledge/pipeline/graph")
async def get_pipeline_knowledge_graph():
    """Get knowledge graph data from the advanced pipeline."""
    try:
        if not knowledge_pipeline_service.initialized:
            raise HTTPException(status_code=503, detail="Knowledge pipeline not initialized")
        
        graph_data = await knowledge_pipeline_service.get_knowledge_graph_data()
        return graph_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph export error: {e}")
        raise HTTPException(status_code=500, detail=f"Graph export failed: {str(e)}")


@app.get("/api/knowledge/pipeline/status")
async def get_pipeline_status():
    """Get the status of the knowledge extraction pipeline."""
    try:
        status = await knowledge_pipeline_service.get_pipeline_status()
        return status
        
    except Exception as e:
        logger.error(f"Pipeline status error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline status failed: {str(e)}")


# WebSocket Events Handling

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


# Error handlers - TEMPORARILY DISABLED FOR DEBUGGING
# @app.exception_handler(404)
# async def not_found_handler(request, exc):
#     return JSONResponse(
#         status_code=404,
#         content={"error": "Endpoint not found", "status_code": 404}
#     )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# Knowledge Ingestion API Endpoints

@app.post("/api/knowledge/import/url")
async def import_from_url(request: Union[URLImportRequest, Dict[str, Any]]):
    """Import knowledge from a URL."""
    try:
        # Handle simple dict format
        if isinstance(request, dict):
            url = request.get('url')
            category = request.get('category', 'web')
            
            if not url:
                raise HTTPException(status_code=422, detail="URL is required")
            
            # Create proper URLImportRequest
            import_source = ImportSource(
                source_type="url",
                source_identifier=str(url),
                metadata={"category": category}
            )
            
            url_request = URLImportRequest(
                source=import_source,
                url=url,
                categorization_hints=[category] if category else [],
                priority=5
            )
        else:
            url_request = request
        
        # For now, return a mock import ID since the full import system is complex
        import_id = f"url_import_{int(time.time())}"
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "url",
                "source": str(url_request.url)
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
        
        # Map MIME types to expected literal values, or determine from extension
        mime_to_file_type = {
            'application/pdf': 'pdf',
            'text/plain': 'txt',
            'text/csv': 'csv',
            'application/json': 'json',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.ms-word': 'docx',
            'text/markdown': 'txt'
        }
        
        # First try to map MIME type
        if file_type in mime_to_file_type:
            file_type = mime_to_file_type[file_type]
        elif not file_type or file_type == "application/octet-stream":
            # Fallback to file extension
            ext = filename.lower().split('.')[-1] if '.' in filename else 'txt'
            ext_to_file_type = {
                'pdf': 'pdf',
                'txt': 'txt',
                'json': 'json',
                'csv': 'csv',
                'docx': 'docx',
                'doc': 'docx',
                'md': 'txt',
                'markdown': 'txt'
            }
            file_type = ext_to_file_type.get(ext, 'txt')
        
        # Ensure file_type is one of the allowed values
        allowed_types = ['pdf', 'txt', 'json', 'csv', 'docx']
        if file_type not in allowed_types:
            file_type = 'txt'  # Default fallback
        
        logger.info(f"🔄 File type mapping: original='{file_type}' -> mapped='{file_type}'")
        
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
async def import_from_wikipedia(request: Union[WikipediaImportRequest, Dict[str, Any]]):
    """Import knowledge from Wikipedia."""
    try:
        # Handle simple dict format
        if isinstance(request, dict):
            topic = request.get('topic')
            category = request.get('category', 'encyclopedia')
            
            if not topic:
                raise HTTPException(status_code=422, detail="Topic is required")
            
            # Create proper WikipediaImportRequest
            import_source = ImportSource(
                source_type="wikipedia",
                source_identifier=topic,
                metadata={"category": category}
            )
            
            wiki_request = WikipediaImportRequest(
                source=import_source,
                page_title=topic,
                categorization_hints=[category] if category else [],
                priority=5
            )
        else:
            wiki_request = request
        
        # For now, return a mock import ID
        import_id = f"wiki_import_{int(time.time())}"
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "wikipedia",
                "source": wiki_request.page_title
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_id": import_id, "status": "queued"}
        
    except Exception as e:
        logger.error(f"Error starting Wikipedia import: {e}")
        raise HTTPException(status_code=500, detail=f"Wikipedia import failed: {str(e)}")


@app.post("/api/knowledge/import/text")
async def import_from_text(request: Union[TextImportRequest, Dict[str, Any]]):
    """Import knowledge from manual text input."""
    try:
        # Handle simple dict format
        if isinstance(request, dict):
            content = request.get('content')
            title = request.get('title', 'Manual Text Input')
            category = request.get('category', 'document')
            
            if not content:
                raise HTTPException(status_code=422, detail="Content is required")
            
            # Create proper TextImportRequest
            import_source = ImportSource(
                source_type="text",
                source_identifier=title,
                metadata={"category": category}
            )
            
            text_request = TextImportRequest(
                source=import_source,
                content=content,
                title=title,
                categorization_hints=[category] if category else [],
                priority=5
            )
        else:
            text_request = request
        
        # For now, return a mock import ID
        import_id = f"text_import_{int(time.time())}"
        
        # Broadcast import event
        if websocket_manager.has_connections():
            import_event = {
                "type": "import_started",
                "timestamp": time.time(),
                "import_id": import_id,
                "source_type": "text",
                "source": text_request.title or "Manual Text"
            }
            await websocket_manager.broadcast(import_event)
        
        return {"import_id": import_id, "status": "queued"}
        
    except Exception as e:
        logger.error(f"Error starting text import: {e}")
        raise HTTPException(status_code=500, detail=f"Text import failed: {str(e)}")


@app.post("/api/knowledge/import/batch")
async def batch_import(request: Union[BatchImportRequest, Dict[str, Any]]):
    """Process multiple import requests in batch."""
    try:
        # Handle simple dict format
        if isinstance(request, dict):
            sources = request.get('sources', [])
            
            if not sources:
                raise HTTPException(status_code=422, detail="Sources list is required")
            
            # Create mock import IDs for each source
            import_ids = [f"batch_import_{int(time.time())}_{i}" for i in range(len(sources))]
        else:
            # For complex BatchImportRequest, create mock IDs
            import_ids = [f"batch_import_{int(time.time())}_{i}" for i in range(len(request.sources or []))]
        
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
        # Return mock progress data
        progress = {
            "import_id": import_id,
            "status": "completed",  # could be: queued, processing, completed, failed
            "progress": 100,        # percentage
            "total_items": 5,
            "processed_items": 5,
            "failed_items": 0,
            "start_time": time.time() - 300,  # 5 minutes ago
            "completion_time": time.time() - 30,  # 30 seconds ago
            "estimated_remaining": 0,
            "message": "Import completed successfully",
            "details": {
                "source_type": "mock",
                "items_created": 5,
                "categories_added": 2
            }
        }
        
        return progress
        
    except Exception as e:
        logger.error(f"Error getting import progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get import progress: {str(e)}")


@app.delete("/api/knowledge/import/{import_id}")
async def cancel_import(import_id: str):
    """Cancel an import operation."""
    try:
        # Return mock cancellation success
        return {"status": "cancelled", "import_id": import_id, "message": "Import operation cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling import: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel import: {str(e)}")


# Knowledge Management API Endpoints

@app.get("/api/knowledge/search")
async def search_knowledge(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100, description="Number of results")
):
    """Search the knowledge base."""
    try:
        # Simple search implementation for now
        results = {
            "query": query,
            "category": category,
            "results": [
                {
                    "id": f"search_result_{i}",
                    "title": f"Search result {i} for: {query}",
                    "content": f"This is search result {i} for the query '{query}'",
                    "category": category or "general",
                    "confidence": 0.85 - (i * 0.1),
                    "snippet": f"...relevant content for {query}..."
                }
                for i in range(1, min(limit + 1, 4))  # Return up to 3 mock results
            ],
            "total": min(limit, 3),
            "limit": limit
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/knowledge/graph")
async def get_knowledge_graph():
    """Get knowledge graph structure for visualization."""
    # Return sample graph data for frontend testing
    return {
        "nodes": [
            {"id": "concept_1", "label": "Knowledge", "type": "concept", "size": 10},
            {"id": "concept_2", "label": "Learning", "type": "concept", "size": 8},
            {"id": "entity_1", "label": "GödelOS", "type": "entity", "size": 12},
            {"id": "fact_1", "label": "System Active", "type": "fact", "size": 6}
        ],
        "edges": [
            {"source": "entity_1", "target": "concept_1", "type": "relates_to", "weight": 1.0},
            {"source": "concept_1", "target": "concept_2", "type": "connected_to", "weight": 0.8},
            {"source": "entity_1", "target": "fact_1", "type": "has_property", "weight": 0.9}
        ],
        "statistics": {
            "node_count": 4,
            "edge_count": 3,
            "total_count": 7
        }
    }


@app.get("/api/knowledge/evolution")
async def get_knowledge_evolution():
    """Get knowledge evolution data over time."""
    # Return sample evolution data for frontend testing
    return {
        "evolution_data": [
            {"timestamp": time.time() - 3600, "node_count": 10, "edge_count": 8, "concepts": 5},
            {"timestamp": time.time() - 1800, "node_count": 15, "edge_count": 12, "concepts": 8},
            {"timestamp": time.time(), "node_count": 20, "edge_count": 18, "concepts": 12}
        ],
        "metrics": {
            "growth_rate": 0.25,
            "connectivity_increase": 0.3,
            "concept_expansion": 0.4
        }
    }


@app.get("/api/knowledge/{item_id}")
async def get_knowledge_item(item_id: str):
    """Get a specific knowledge item by ID."""
    try:
        # For now, return a mock knowledge item
        mock_item = {
            "id": item_id,
            "title": f"Knowledge Item {item_id}",
            "content": f"This is the content for knowledge item {item_id}",
            "category": "general",
            "knowledge_type": "concept",
            "confidence": 0.9,
            "created_at": time.time() - 3600,  # 1 hour ago
            "updated_at": time.time(),
            "metadata": {
                "source": "system",
                "tags": ["example", "mock"]
            }
        }
        
        return mock_item
        
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


@app.get("/api/knowledge/concepts")
async def get_knowledge_concepts():
    """Get all concepts from the knowledge base."""
    try:
        if not godelos_integration:
            return {"concepts": [], "total_count": 0}
        
        # Get concepts from knowledge base
        concepts = await godelos_integration.get_concepts()
        
        return {
            "concepts": concepts,
            "total_count": len(concepts)
        }
        
    except Exception as e:
        logger.error(f"Error getting concepts: {e}")
        return {"concepts": [], "total_count": 0}


@app.get("/api/test-route")
async def test_route():
    """Test route to verify routing is working."""
    logger.info("🔍 TEST ROUTE: This route is working!")
    return {"message": "test route works", "timestamp": time.time()}


@app.get("/api/evo-test")
async def get_evolution_test():
    """Test route for evolution data."""
    return {
        "evolution_data": [
            {"timestamp": time.time() - 3600, "node_count": 10, "edge_count": 8, "concepts": 5},
            {"timestamp": time.time() - 1800, "node_count": 15, "edge_count": 12, "concepts": 8},
            {"timestamp": time.time(), "node_count": 20, "edge_count": 18, "concepts": 12}
        ],
        "metrics": {
            "growth_rate": 0.25,
            "connectivity_increase": 0.3,
            "concept_expansion": 0.4
        }
    }


@app.get("/api/graph-test")
async def get_graph_test():
    """Test route for graph data."""
    return {
        "nodes": [
            {"id": "concept_1", "label": "Knowledge", "type": "concept", "size": 10},
            {"id": "concept_2", "label": "Learning", "type": "concept", "size": 8},
            {"id": "entity_1", "label": "GödelOS", "type": "entity", "size": 12},
            {"id": "fact_1", "label": "System Active", "type": "fact", "size": 6}
        ],
        "edges": [
            {"source": "entity_1", "target": "concept_1", "type": "relates_to", "weight": 1.0},
            {"source": "concept_1", "target": "concept_2", "type": "connected_to", "weight": 0.8},
            {"source": "entity_1", "target": "fact_1", "type": "has_property", "weight": 0.9}
        ],
        "statistics": {
            "node_count": 4,
            "edge_count": 3,
            "total_count": 7
        }
    }


@app.get("/api/capabilities")
async def get_system_capabilities():
    """Get system capabilities and features."""
    logger.info("🔍 CAPABILITIES ROUTE: Route called - testing if changes are picked up")
    return {
        "capabilities": [
            "natural_language_processing",
            "knowledge_management",
            "cognitive_reasoning",
            "real_time_learning",
            "uncertainty_quantification",
            "provenance_tracking"
        ],
        "features": {
            "query_processing": True,
            "knowledge_import": True,
            "real_time_streaming": True,
            "transparency": True,
            "self_modification": False  # Not yet implemented
        },
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/api/cognitive/state")
async def get_cognitive_state_alt():
    """Alternative endpoint for cognitive state (matches frontend expectations)."""
    return await get_cognitive_state()


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