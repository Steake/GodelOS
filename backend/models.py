"""
Pydantic models for the GödelOS API

Defines request and response models for type validation and documentation.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str = Field(..., description="Natural language query to process")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")
    include_reasoning: bool = Field(False, description="Whether to include reasoning steps in response")


class ReasoningStep(BaseModel):
    """Model for individual reasoning steps."""
    step_number: int = Field(..., description="Sequential step number")
    operation: str = Field(..., description="Type of reasoning operation")
    description: str = Field(..., description="Human-readable description of the step")
    premises: List[str] = Field(default_factory=list, description="Premises used in this step")
    conclusion: str = Field(..., description="Conclusion reached in this step")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level for this step")


class QueryResponse(BaseModel):
    """Response model for natural language queries."""
    response: str = Field(..., description="Natural language response to the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in the response")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list, description="Step-by-step reasoning process")
    inference_time_ms: float = Field(..., description="Time taken for inference in milliseconds")
    knowledge_used: List[str] = Field(default_factory=list, description="Knowledge base items used in reasoning")


class KnowledgeRequest(BaseModel):
    """Request model for adding knowledge to the system."""
    content: str = Field(..., description="Knowledge content to add")
    knowledge_type: str = Field(..., description="Type of knowledge (fact, rule, concept)")
    context_id: Optional[str] = Field(None, description="Context ID for organizing knowledge")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the knowledge")


class SimpleKnowledgeRequest(BaseModel):
    """Simplified request model for adding knowledge (frontend-friendly)."""
    concept: Optional[str] = Field(None, description="Concept name (alternative to content)")
    content: Optional[str] = Field(None, description="Knowledge content")
    definition: Optional[str] = Field(None, description="Definition (alternative to content)")
    title: Optional[str] = Field(None, description="Title for the knowledge")
    category: Optional[str] = Field("general", description="Category for the knowledge")
    
    def to_knowledge_request(self) -> 'KnowledgeRequest':
        """Convert to standard KnowledgeRequest format."""
        content = self.content or self.definition or self.concept or ""
        return KnowledgeRequest(
            content=content,
            knowledge_type="concept",
            context_id=self.category,
            metadata={"category": self.category, "title": self.title}
        )
    knowledge_type: Optional[str] = Field("concept", description="Type of knowledge")
    
    def to_knowledge_request(self) -> "KnowledgeRequest":
        """Convert to standard KnowledgeRequest format."""
        # Use content if provided, otherwise use definition, otherwise use concept
        content = self.content or self.definition or self.concept or ""
        if not content:
            raise ValueError("Must provide either content, definition, or concept")
            
        return KnowledgeRequest(
            content=content,
            knowledge_type=self.knowledge_type or "concept",
            context_id=self.category,
            metadata={
                "title": self.title,
                "category": self.category,
                "original_format": "simple"
            }
        )


class KnowledgeItem(BaseModel):
    """Model for individual knowledge items."""
    id: str = Field(..., description="Unique identifier for the knowledge item")
    content: str = Field(..., description="Knowledge content")
    knowledge_type: str = Field(..., description="Type of knowledge")
    context_id: Optional[str] = Field(None, description="Context ID")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in this knowledge")
    created_at: float = Field(0.0, description="Timestamp when knowledge was added")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class KnowledgeResponse(BaseModel):
    """Response model for knowledge retrieval."""
    facts: List[KnowledgeItem] = Field(default_factory=list, description="Factual knowledge items")
    rules: List[KnowledgeItem] = Field(default_factory=list, description="Rule-based knowledge items")
    concepts: List[KnowledgeItem] = Field(default_factory=list, description="Conceptual knowledge items")
    total_count: int = Field(..., description="Total number of knowledge items")
    context_id: Optional[str] = Field(None, description="Context ID filter applied")


class ProcessState(BaseModel):
    """Model for individual cognitive processes."""
    process_id: str = Field(..., description="Unique identifier for the process")
    process_type: str = Field(..., description="Type of cognitive process")
    status: str = Field(..., description="Current status of the process")
    priority: int = Field(..., description="Process priority level")
    started_at: float = Field(0.0, description="Timestamp when process started")
    progress: float = Field(..., ge=0.0, le=1.0, description="Process completion progress")
    description: str = Field("", description="Human-readable description of the process")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional process metadata")


class AttentionFocus(BaseModel):
    """Model for attention focus items."""
    item_id: str = Field(..., description="Identifier for the attention item")
    item_type: str = Field(..., description="Type of attention item")
    salience: float = Field(..., ge=0.0, le=1.0, description="Salience/importance level")
    duration: float = Field(0.0, description="How long this item has been in focus (seconds)")
    description: str = Field("", description="Description of the attention item")


class WorkingMemoryItem(BaseModel):
    """Model for working memory items."""
    item_id: str = Field(..., description="Unique identifier for the memory item")
    content: str = Field(..., description="Content of the memory item")
    activation_level: float = Field(..., ge=0.0, le=1.0, description="Current activation level")
    created_at: float = Field(0.0, description="Timestamp when item was created")
    last_accessed: float = Field(0.0, description="Timestamp when item was last accessed")
    access_count: int = Field(0, description="Number of times item has been accessed")


class MetacognitiveState(BaseModel):
    """Model for metacognitive state information."""
    self_awareness_level: float = Field(..., ge=0.0, le=1.0, description="Current self-awareness level")
    confidence_in_reasoning: float = Field(..., ge=0.0, le=1.0, description="Confidence in current reasoning")
    cognitive_load: float = Field(0.0, ge=0.0, le=1.0, description="Current cognitive load")
    learning_rate: float = Field(0.0, ge=0.0, le=1.0, description="Current learning effectiveness")
    adaptation_level: float = Field(0.0, ge=0.0, le=1.0, description="System adaptation level")
    introspection_depth: int = Field(0, description="Current depth of introspective analysis")


class ManifestConsciousness(BaseModel):
    """Model for manifest consciousness state."""
    current_focus: str = Field(..., description="Current primary focus of consciousness")
    awareness_level: float = Field(..., ge=0.0, le=1.0, description="Overall awareness level")
    coherence_level: float = Field(..., ge=0.0, le=1.0, description="Coherence of conscious experience")
    integration_level: float = Field(0.0, ge=0.0, le=1.0, description="Integration across cognitive systems")
    phenomenal_content: List[str] = Field(default_factory=list, description="Current phenomenal experiences")
    access_consciousness: Dict[str, Any] = Field(default_factory=dict, description="Accessible conscious content")
    attention_focus: List[AttentionFocus] = Field(default_factory=list, description="Current attention focus items")
    working_memory: Dict[str, List[WorkingMemoryItem]] = Field(default_factory=dict, description="Working memory contents")


class CognitiveStateResponse(BaseModel):
    """Response model for cognitive state information."""
    manifest_consciousness: ManifestConsciousness = Field(..., description="Manifest consciousness state")
    agentic_processes: List[ProcessState] = Field(default_factory=list, description="Active agentic processes")
    daemon_threads: List[ProcessState] = Field(default_factory=list, description="Background daemon processes")
    working_memory: Dict[str, List[WorkingMemoryItem]] = Field(default_factory=dict, description="Working memory contents")
    attention_focus: List[AttentionFocus] = Field(default_factory=list, description="Current attention focus items")
    metacognitive_state: MetacognitiveState = Field(..., description="Metacognitive state information")
    timestamp: float = Field(..., description="Timestamp of the cognitive state snapshot")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: float = Field(..., description="Timestamp when error occurred")


class WebSocketMessage(BaseModel):
    """Model for WebSocket messages."""
    type: str = Field(..., description="Message type")
    timestamp: float = Field(..., description="Message timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Message data")


class CognitiveEvent(BaseModel):
    """Model for cognitive events broadcasted via WebSocket."""
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of cognitive event")
    timestamp: float = Field(..., description="Event timestamp")
    source_process: Optional[str] = Field(None, description="Process that generated the event")
    description: str = Field(..., description="Human-readable event description")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event metadata")


class HealthStatus(BaseModel):
    """Model for system health status."""
    healthy: bool = Field(..., description="Overall system health status")
    components: Dict[str, bool] = Field(default_factory=dict, description="Health status of individual components")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    error_count: int = Field(..., description="Number of recent errors")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    memory_usage_mb: float = Field(..., description="Memory usage in megabytes")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")