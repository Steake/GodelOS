#!/usr/bin/env python3
"""
Simplified GödelOS Backend API for Demo
Provides mock responses to test frontend integration
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simplified models for demo
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    include_reasoning: bool = False

class ReasoningStep(BaseModel):
    step_number: int
    operation: str
    description: str
    premises: List[str] = []
    conclusion: str
    confidence: float

class QueryResponse(BaseModel):
    response: str
    confidence: float
    reasoning_steps: List[ReasoningStep] = []
    inference_time_ms: float
    knowledge_used: List[str] = []

class KnowledgeItem(BaseModel):
    id: str
    content: str
    knowledge_type: str
    context_id: Optional[str] = None
    confidence: float
    created_at: float
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeResponse(BaseModel):
    facts: List[KnowledgeItem] = []
    rules: List[KnowledgeItem] = []
    concepts: List[KnowledgeItem] = []
    total_count: int
    context_id: Optional[str] = None

class CognitiveStateResponse(BaseModel):
    manifest_consciousness: Dict[str, Any]
    agentic_processes: List[Dict[str, Any]] = []
    daemon_threads: List[Dict[str, Any]] = []
    working_memory: Dict[str, List[Dict[str, Any]]] = {}
    attention_focus: List[Dict[str, Any]] = []
    metacognitive_state: Dict[str, Any] = {}
    timestamp: float

# Create FastAPI app
app = FastAPI(
    title="GödelOS Demo API",
    description="Simplified backend API for GödelOS web demonstration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "GödelOS Demo API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "details": {
            "healthy": True,
            "components": {
                "api": True,
                "websocket": True,
                "demo_mode": True
            },
            "performance_metrics": {
                "response_time_ms": 10.5,
                "memory_usage_mb": 128.0
            }
        }
    }

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query with mock responses."""
    start_time = time.time()
    
    # Generate mock response based on query
    query_lower = request.query.lower()
    
    if "consciousness" in query_lower:
        response_text = "Consciousness in GödelOS is modeled as a multi-layered architecture with manifest consciousness at the top level, supported by agentic processes and daemon threads that handle various cognitive functions."
        knowledge_used = ["consciousness_model", "cognitive_architecture", "awareness_theory"]
    elif "artificial intelligence" in query_lower or "ai" in query_lower:
        response_text = "Artificial Intelligence in the GödelOS framework combines symbolic reasoning, probabilistic inference, and metacognitive monitoring to create a comprehensive cognitive system."
        knowledge_used = ["ai_definition", "symbolic_reasoning", "probabilistic_logic"]
    elif "reasoning" in query_lower:
        response_text = "The reasoning system employs multiple inference engines including resolution-based theorem proving, modal logic reasoning, and analogical reasoning to process complex logical queries."
        knowledge_used = ["inference_engines", "logical_reasoning", "theorem_proving"]
    else:
        response_text = f"I've processed your query about '{request.query}' using the GödelOS knowledge base and reasoning systems. The system analyzed the semantic content and retrieved relevant information."
        knowledge_used = ["general_knowledge", "semantic_analysis", "query_processing"]
    
    # Generate reasoning steps
    reasoning_steps = [
        ReasoningStep(
            step_number=1,
            operation="parse",
            description="Parse and analyze the natural language query",
            premises=["natural_language_input"],
            conclusion="structured_query_representation",
            confidence=0.95
        ),
        ReasoningStep(
            step_number=2,
            operation="retrieve",
            description="Search knowledge base for relevant information",
            premises=["structured_query", "knowledge_base"],
            conclusion="relevant_knowledge_items",
            confidence=0.88
        ),
        ReasoningStep(
            step_number=3,
            operation="reason",
            description="Apply inference rules to derive conclusions",
            premises=["relevant_knowledge", "inference_rules"],
            conclusion="logical_conclusions",
            confidence=0.82
        ),
        ReasoningStep(
            step_number=4,
            operation="generate",
            description="Generate natural language response",
            premises=["logical_conclusions", "language_model"],
            conclusion="natural_language_response",
            confidence=0.90
        )
    ]
    
    inference_time = (time.time() - start_time) * 1000
    
    # Broadcast cognitive event via WebSocket
    if manager.active_connections:
        cognitive_event = {
            "type": "query_processed",
            "timestamp": time.time(),
            "query": request.query,
            "response": response_text,
            "reasoning_steps": [step.dict() for step in reasoning_steps],
            "inference_time_ms": inference_time
        }
        await manager.broadcast(cognitive_event)
    
    return QueryResponse(
        response=response_text,
        confidence=0.85,
        reasoning_steps=reasoning_steps,
        inference_time_ms=inference_time,
        knowledge_used=knowledge_used
    )

@app.get("/api/knowledge", response_model=KnowledgeResponse)
async def get_knowledge(
    context_id: Optional[str] = None,
    knowledge_type: Optional[str] = None,
    limit: int = 100
):
    """Retrieve knowledge base information with mock data."""
    
    # Generate mock knowledge items
    facts = [
        KnowledgeItem(
            id="fact_1",
            content="Consciousness involves awareness and subjective experience",
            knowledge_type="fact",
            confidence=0.9,
            created_at=time.time() - 3600,
            metadata={"source": "cognitive_science"}
        ),
        KnowledgeItem(
            id="fact_2", 
            content="Artificial intelligence systems can exhibit reasoning capabilities",
            knowledge_type="fact",
            confidence=0.95,
            created_at=time.time() - 7200,
            metadata={"source": "ai_research"}
        )
    ]
    
    rules = [
        KnowledgeItem(
            id="rule_1",
            content="If X is conscious, then X has subjective experiences",
            knowledge_type="rule",
            confidence=0.85,
            created_at=time.time() - 1800,
            metadata={"logical_form": "conscious(X) → subjective_experience(X)"}
        )
    ]
    
    concepts = [
        KnowledgeItem(
            id="concept_1",
            content="Consciousness: The state of being aware and having subjective experiences",
            knowledge_type="concept",
            confidence=0.88,
            created_at=time.time() - 5400,
            metadata={"category": "cognitive_science"}
        )
    ]
    
    return KnowledgeResponse(
        facts=facts[:limit//3],
        rules=rules[:limit//3],
        concepts=concepts[:limit//3],
        total_count=len(facts) + len(rules) + len(concepts),
        context_id=context_id
    )

@app.get("/api/cognitive-state", response_model=CognitiveStateResponse)
async def get_cognitive_state():
    """Get current cognitive layer states with mock data."""
    
    return CognitiveStateResponse(
        manifest_consciousness={
            "current_focus": "Query processing and response generation",
            "awareness_level": 0.85,
            "coherence_level": 0.92,
            "integration_level": 0.78,
            "phenomenal_content": ["linguistic_processing", "semantic_analysis", "response_generation"],
            "access_consciousness": {
                "working_memory_contents": ["current_query", "retrieved_knowledge", "reasoning_chain"],
                "attention_focus": "natural_language_understanding"
            }
        },
        agentic_processes=[
            {
                "process_id": "query_parser",
                "process_type": "linguistic_analysis",
                "status": "active",
                "priority": 8,
                "started_at": time.time() - 2,
                "progress": 0.95,
                "description": "Parsing natural language query into structured representation"
            },
            {
                "process_id": "knowledge_retriever", 
                "process_type": "information_retrieval",
                "status": "idle",
                "priority": 6,
                "started_at": time.time() - 10,
                "progress": 1.0,
                "description": "Retrieving relevant knowledge from the knowledge base"
            },
            {
                "process_id": "inference_engine",
                "process_type": "logical_reasoning", 
                "status": "active",
                "priority": 9,
                "started_at": time.time() - 1,
                "progress": 0.7,
                "description": "Applying inference rules to derive conclusions"
            }
        ],
        daemon_threads=[
            {
                "process_id": "memory_consolidation",
                "process_type": "memory_management",
                "status": "running",
                "priority": 3,
                "started_at": time.time() - 300,
                "progress": 0.4,
                "description": "Consolidating episodic memories into long-term storage"
            },
            {
                "process_id": "background_learning",
                "process_type": "knowledge_acquisition",
                "status": "running", 
                "priority": 2,
                "started_at": time.time() - 600,
                "progress": 0.2,
                "description": "Learning patterns from recent interactions"
            },
            {
                "process_id": "system_monitoring",
                "process_type": "health_monitoring",
                "status": "running",
                "priority": 5,
                "started_at": time.time() - 1200,
                "progress": 0.8,
                "description": "Monitoring system performance and health metrics"
            }
        ],
        working_memory={
            "linguistic": [
                {"item_id": "current_query", "content": "User's natural language query", "activation_level": 0.95},
                {"item_id": "parsed_structure", "content": "Structured query representation", "activation_level": 0.88}
            ],
            "semantic": [
                {"item_id": "concept_map", "content": "Activated concept network", "activation_level": 0.75},
                {"item_id": "context_frame", "content": "Current conversational context", "activation_level": 0.65}
            ]
        },
        attention_focus=[
            {
                "item_id": "query_processing",
                "item_type": "cognitive_task",
                "salience": 0.9,
                "duration": 2.5,
                "description": "Processing current user query"
            },
            {
                "item_id": "knowledge_integration", 
                "item_type": "cognitive_process",
                "salience": 0.7,
                "duration": 1.8,
                "description": "Integrating retrieved knowledge with reasoning"
            }
        ],
        metacognitive_state={
            "self_awareness_level": 0.75,
            "confidence_in_reasoning": 0.82,
            "cognitive_load": 0.45,
            "learning_rate": 0.65,
            "adaptation_level": 0.58,
            "introspection_depth": 3
        },
        timestamp=time.time()
    )

@app.websocket("/ws/cognitive-stream")
async def cognitive_stream_websocket(websocket: WebSocket):
    """WebSocket endpoint for streaming real-time cognitive events."""
    await manager.connect(websocket)
    
    try:
        # Send initial cognitive state
        initial_state = await get_cognitive_state()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "timestamp": time.time(),
            "data": initial_state.dict()
        }))
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "subscribe":
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "event_types": message.get("event_types", [])
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "demo_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )