"""
Enhanced Cognitive API for autonomous learning and stream of consciousness.

This module provides API endpoints for:
- Cognitive event streaming configuration
- Autonomous learning management
- Knowledge acquisition monitoring
- Stream of consciousness access
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends
from pydantic import BaseModel, Field

# Import configuration and enhanced metacognition modules
from backend.config_manager import get_config, is_feature_enabled
from backend.metacognition_modules.enhanced_metacognition_manager import EnhancedMetacognitionManager
from backend.metacognition_modules.cognitive_models import KnowledgeGap, CognitiveEvent

logger = logging.getLogger(__name__)

# Request/Response Models

class CognitiveStreamConfig(BaseModel):
    """Configuration for cognitive event streaming."""
    granularity: str = Field(default="standard", description="Event granularity level")
    subscriptions: List[str] = Field(default=[], description="Event types to subscribe to")
    max_event_rate: Optional[int] = Field(default=None, description="Maximum events per second")


class AutonomousLearningConfig(BaseModel):
    """Configuration for autonomous learning."""
    enabled: bool = Field(default=True, description="Enable autonomous learning")
    gap_detection_interval: int = Field(default=300, description="Gap detection interval in seconds")
    confidence_threshold: float = Field(default=0.7, description="Confidence threshold for gaps")
    auto_approval_threshold: float = Field(default=0.8, description="Auto-approval threshold")
    max_concurrent_acquisitions: int = Field(default=3, description="Maximum concurrent acquisitions")


class KnowledgeAcquisitionTrigger(BaseModel):
    """Manual knowledge acquisition trigger."""
    concepts: List[str] = Field(description="Concepts to acquire knowledge about")
    priority: float = Field(default=0.5, description="Acquisition priority")
    strategy: Optional[str] = Field(default=None, description="Preferred acquisition strategy")


class CognitiveEventFilter(BaseModel):
    """Filter for cognitive events."""
    event_types: Optional[List[str]] = Field(default=None, description="Event types to include")
    granularity: Optional[str] = Field(default=None, description="Maximum granularity level")
    limit: int = Field(default=100, description="Maximum number of events")


# API Router
router = APIRouter(tags=["Enhanced Cognitive"])

# Global reference to enhanced metacognition manager
enhanced_metacognition_manager: Optional[EnhancedMetacognitionManager] = None
websocket_manager = None
config = None


def get_enhanced_metacognition():
    """Dependency to get enhanced metacognition manager."""
    if not enhanced_metacognition_manager:
        raise HTTPException(status_code=503, detail="Enhanced metacognition not available")
    return enhanced_metacognition_manager


def get_websocket_manager():
    """Dependency to get WebSocket manager."""
    if not websocket_manager:
        raise HTTPException(status_code=503, detail="WebSocket manager not available")
    return websocket_manager


async def initialize_enhanced_cognitive(ws_manager, godelos_integration=None):
    """Initialize the enhanced cognitive API with required dependencies."""
    global enhanced_metacognition_manager, websocket_manager, config
    
    try:
        logger.info("Initializing enhanced cognitive API...")
        
        # Load configuration
        config = get_config()
        logger.info(f"Configuration loaded. Enhanced metacognition enabled: {is_feature_enabled('enhanced_metacognition')}")
        
        # Set WebSocket manager
        websocket_manager = ws_manager
        
        # Check if enhanced metacognition is enabled
        if is_feature_enabled('enhanced_metacognition'):
            # Initialize enhanced metacognition manager
            enhanced_metacognition_manager = EnhancedMetacognitionManager(
                websocket_manager=ws_manager,
                config=config
            )
            
            # Initialize with GödelOS integration if available
            if godelos_integration:
                await enhanced_metacognition_manager.initialize(godelos_integration)
            else:
                await enhanced_metacognition_manager.initialize()
            
            logger.info("Enhanced metacognition manager initialized successfully")
        else:
            logger.info("Enhanced metacognition disabled in configuration")
        
        logger.info("Enhanced cognitive API initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced cognitive API: {e}")
        raise


# Cognitive Streaming Endpoints

@router.websocket("/stream")
async def cognitive_stream_websocket(
    websocket: WebSocket,
    granularity: str = Query(default="standard", description="Event granularity"),
    subscriptions: str = Query(default="", description="Comma-separated event types")
):
    """
    WebSocket endpoint for real-time cognitive event streaming.
    
    Query Parameters:
    - granularity: Event granularity level (minimal, standard, detailed, debug)
    - subscriptions: Comma-separated list of event types to subscribe to
    """
    ws_manager = websocket_manager
    if not ws_manager:
        await websocket.close(code=1011, reason="WebSocket manager not available")
        return
    
    # Parse subscriptions
    subscription_list = [s.strip() for s in subscriptions.split(",") if s.strip()] if subscriptions else []
    
    client_id = None
    try:
        # Connect to cognitive stream
        client_id = await ws_manager.connect_cognitive_stream(
            websocket=websocket,
            granularity=granularity,
            subscriptions=subscription_list
        )
        
        logger.info(f"Cognitive stream WebSocket connected: {client_id}")
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (configuration updates, etc.)
                message = await websocket.receive_json()
                await handle_cognitive_stream_message(client_id, message)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling cognitive stream message: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error in cognitive stream WebSocket: {e}")
    finally:
        if client_id and ws_manager:
            await ws_manager.disconnect_cognitive_stream(client_id)
        logger.info(f"Cognitive stream WebSocket disconnected: {client_id}")


async def handle_cognitive_stream_message(client_id: str, message: Dict[str, Any]):
    """Handle incoming messages from cognitive stream clients."""
    try:
        message_type = message.get("type")
        ws_manager = websocket_manager
        
        if message_type == "configure":
            # Update client configuration
            config = message.get("config", {})
            await ws_manager.configure_cognitive_stream(
                client_id=client_id,
                granularity=config.get("granularity"),
                subscriptions=config.get("subscriptions")
            )
            
        elif message_type == "get_history":
            # Send event history
            filter_data = message.get("filter", {})
            history = await ws_manager.get_cognitive_event_history(
                client_id=client_id,
                limit=filter_data.get("limit", 100),
                event_types=filter_data.get("event_types")
            )
            
            await ws_manager._send_cognitive_event(client_id, {
                "type": "event_history",
                "timestamp": datetime.now().isoformat(),
                "events": history
            })
            
        elif message_type == "ping":
            # Respond to ping
            await ws_manager._send_cognitive_event(client_id, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            logger.warning(f"Unknown message type from cognitive client {client_id}: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling message from cognitive client {client_id}: {e}")


@router.get("/stream/status")
async def get_cognitive_stream_status(
    ws_manager = Depends(get_websocket_manager)
):
    """Get status of cognitive streaming connections."""
    try:
        status = await ws_manager.get_cognitive_stream_status()
        
        # Add enhanced metacognition status if available
        if enhanced_metacognition_manager:
            metacognition_status = await enhanced_metacognition_manager.get_status()
            status["enhanced_metacognition"] = metacognition_status
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting cognitive stream status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/configure")
async def configure_cognitive_streaming(
    config: CognitiveStreamConfig,
    metacognition = Depends(get_enhanced_metacognition)
):
    """Configure global cognitive streaming settings."""
    try:
        # Convert to internal config format
        from ..metacognition_modules import CognitiveStreamingConfig, GranularityLevel
        
        internal_config = CognitiveStreamingConfig(
            enabled=True,
            default_granularity=GranularityLevel(config.granularity),
            max_event_rate=config.max_event_rate or 100
        )
        
        success = await metacognition.configure_cognitive_streaming(internal_config)
        
        if success:
            return {"status": "success", "message": "Cognitive streaming configured"}
        else:
            raise HTTPException(status_code=500, detail="Failed to configure cognitive streaming")
            
    except Exception as e:
        logger.error(f"Error configuring cognitive streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Autonomous Learning Endpoints

@router.get("/autonomous/status")
async def get_autonomous_learning_status(
    metacognition = Depends(get_enhanced_metacognition)
):
    """Get status of autonomous learning system."""
    try:
        status = await metacognition.get_status()
        return status.get("autonomous_learning", {})
        
    except Exception as e:
        logger.error(f"Error getting autonomous learning status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/configure")
async def configure_autonomous_learning(
    config: AutonomousLearningConfig,
    metacognition = Depends(get_enhanced_metacognition)
):
    """Configure autonomous learning settings."""
    try:
        # Convert to internal config format
        from ..metacognition_modules import AutonomousLearningConfig as InternalConfig
        
        internal_config = InternalConfig(
            enabled=config.enabled,
            gap_detection_interval=config.gap_detection_interval,
            confidence_threshold=config.confidence_threshold,
            auto_approval_threshold=config.auto_approval_threshold,
            max_concurrent_acquisitions=config.max_concurrent_acquisitions
        )
        
        success = await metacognition.configure_autonomous_learning(internal_config)
        
        if success:
            return {"status": "success", "message": "Autonomous learning configured"}
        else:
            raise HTTPException(status_code=500, detail="Failed to configure autonomous learning")
            
    except Exception as e:
        logger.error(f"Error configuring autonomous learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autonomous/gaps")
async def get_detected_gaps(
    metacognition = Depends(get_enhanced_metacognition)
):
    """Get currently detected knowledge gaps."""
    try:
        gaps = []
        if hasattr(metacognition, 'detected_gaps'):
            gaps = [gap.to_dict() for gap in metacognition.detected_gaps]
        
        return {
            "gaps": gaps,
            "total_count": len(gaps)
        }
        
    except Exception as e:
        logger.error(f"Error getting detected gaps: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/trigger-acquisition")
async def trigger_knowledge_acquisition(
    trigger: KnowledgeAcquisitionTrigger,
    metacognition = Depends(get_enhanced_metacognition)
):
    """Manually trigger knowledge acquisition for specific concepts."""
    try:
        # Create a knowledge gap for the concepts
        from ..metacognition_modules import KnowledgeGap, KnowledgeGapType, AcquisitionStrategy
        
        gap = KnowledgeGap(
            type=KnowledgeGapType.CONCEPT_MISSING,
            missing_concepts=trigger.concepts,
            priority=trigger.priority,
            suggested_acquisitions=[
                AcquisitionStrategy(trigger.strategy) if trigger.strategy 
                else AcquisitionStrategy.CONCEPT_EXPANSION
            ]
        )
        
        # Trigger acquisition
        await metacognition._trigger_knowledge_acquisition([gap])
        
        return {
            "status": "success",
            "message": f"Knowledge acquisition triggered for {len(trigger.concepts)} concepts",
            "gap_id": gap.id
        }
        
    except Exception as e:
        logger.error(f"Error triggering knowledge acquisition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autonomous/history")
async def get_acquisition_history(
    limit: int = Query(default=50, description="Maximum number of results"),
    metacognition = Depends(get_enhanced_metacognition)
):
    """Get history of knowledge acquisition attempts."""
    try:
        history = []
        if hasattr(metacognition, 'acquisition_history'):
            recent_history = metacognition.acquisition_history[-limit:]
            history = [result.to_dict() for result in recent_history]
        
        return {
            "history": history,
            "total_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting acquisition history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Monitoring and Health Endpoints

@router.get("/health")
async def get_cognitive_health(
    metacognition = Depends(get_enhanced_metacognition)
):
    """Get comprehensive cognitive system health."""
    try:
        # Get enhanced monitoring if available
        if hasattr(metacognition, 'enhanced_monitoring'):
            monitoring = metacognition.enhanced_monitoring
            if hasattr(monitoring, 'get_comprehensive_health_report'):
                return await monitoring.get_comprehensive_health_report()
        
        # Fallback to basic status
        status = await metacognition.get_status()
        return {
            "overall_status": "healthy" if status.get("is_running") else "stopped",
            "basic_status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting cognitive health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/history")
async def get_cognitive_event_history(
    filter_params: CognitiveEventFilter = Depends(),
    ws_manager = Depends(get_websocket_manager)
):
    """Get cognitive event history with filtering."""
    try:
        # This would require a default client or system-wide event history
        # For now, return empty as this typically requires a WebSocket connection
        return {
            "events": [],
            "message": "Event history requires an active WebSocket connection"
        }
        
    except Exception as e:
        logger.error(f"Error getting cognitive event history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cognitive Event Management

class CognitiveEventInput(BaseModel):
    """Input model for cognitive events."""
    type: str = Field(description="Type of cognitive event")
    data: Dict[str, Any] = Field(description="Event data")
    timestamp: Optional[str] = Field(default=None, description="Event timestamp")
    scenario: Optional[str] = Field(default=None, description="Scenario name")
    sequence: Optional[int] = Field(default=None, description="Sequence number")
    total_in_sequence: Optional[int] = Field(default=None, description="Total in sequence")


@router.post("/events")
async def send_cognitive_event(
    event_input: CognitiveEventInput,
    ws_manager = Depends(get_websocket_manager)
):
    """Send a cognitive event to the streaming system."""
    try:
        # Add metadata to the event data
        enhanced_data = {
            **event_input.data,
            "timestamp": event_input.timestamp or datetime.now(timezone.utc).isoformat(),
            "scenario": event_input.scenario,
            "sequence": event_input.sequence,
            "total_in_sequence": event_input.total_in_sequence
        }
        
        # Send to all connected cognitive stream clients
        if hasattr(ws_manager, 'broadcast_cognitive_event'):
            await ws_manager.broadcast_cognitive_event(event_input.type, enhanced_data)
        else:
            # Fallback: send as regular message
            event_data = {
                "event_type": event_input.type,
                "data": enhanced_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await ws_manager.broadcast_message(event_data, message_type="cognitive_event")
        
        return {
            "status": "success",
            "message": f"Cognitive event '{event_input.type}' sent",
            "event_id": f"{event_input.type}_{int(datetime.now(timezone.utc).timestamp())}"
        }
        
    except Exception as e:
        logger.error(f"Error sending cognitive event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Management Endpoints

@router.post("/start")
async def start_enhanced_cognitive_system(
    metacognition = Depends(get_enhanced_metacognition)
):
    """Start the enhanced cognitive system."""
    try:
        success = await metacognition.start()
        
        if success:
            return {"status": "success", "message": "Enhanced cognitive system started"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start enhanced cognitive system")
            
    except Exception as e:
        logger.error(f"Error starting enhanced cognitive system: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_enhanced_cognitive_system(
    metacognition = Depends(get_enhanced_metacognition)
):
    """Stop the enhanced cognitive system."""
    try:
        await metacognition.stop()
        return {"status": "success", "message": "Enhanced cognitive system stopped"}
        
    except Exception as e:
        logger.error(f"Error stopping enhanced cognitive system: {e}")
        raise HTTPException(status_code=500, detail=str(e))
