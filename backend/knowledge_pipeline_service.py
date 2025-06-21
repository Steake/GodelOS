"""
Knowledge Pipeline Service

Integrates the advanced knowledge extraction pipeline with the backend API.
Provides a service layer that connects the sophisticated NLP processing
to the existing backend infrastructure.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Import the knowledge extraction pipeline
from godelOS.knowledge_extraction.pipeline import DataExtractionPipeline
from godelOS.knowledge_extraction.nlp_processor import NlpProcessor
from godelOS.knowledge_extraction.graph_builder import KnowledgeGraphBuilder
from godelOS.semantic_search.query_engine import QueryEngine
from godelOS.semantic_search.vector_store import VectorStore
from godelOS.unified_agent_core.knowledge_store.store import UnifiedKnowledgeStore
from godelOS.unified_agent_core.knowledge_store.interfaces import Knowledge, Fact, Relationship

logger = logging.getLogger(__name__)

class KnowledgePipelineService:
    """
    Service that integrates the advanced knowledge extraction pipeline
    with the backend API infrastructure.
    """
    
    def __init__(self):
        """Initialize the knowledge pipeline service."""
        self.initialized = False
        self.nlp_processor = None
        self.knowledge_store = None
        self.graph_builder = None
        self.pipeline = None
        self.vector_store = None
        self.query_engine = None
        self.websocket_manager = None
        
        # Metrics tracking
        self.documents_processed = 0
        self.entities_extracted = 0
        self.relationships_extracted = 0
        self.queries_processed = 0
        
    async def initialize(self, websocket_manager=None):
        """Initialize all pipeline components."""
        try:
            logger.info("🔄 Initializing Knowledge Pipeline Service...")
            
            # Store websocket manager for progress updates
            self.websocket_manager = websocket_manager
            
            # Initialize knowledge store
            logger.info("🔄 Initializing UnifiedKnowledgeStore...")
            self.knowledge_store = UnifiedKnowledgeStore()
            await self.knowledge_store.initialize()
            await self.knowledge_store.start()  # Start the store
            
            # Initialize NLP processor
            logger.info("🔄 Initializing NLP Processor...")
            self.nlp_processor = NlpProcessor()
            
            # Initialize graph builder
            logger.info("🔄 Initializing Knowledge Graph Builder...")
            self.graph_builder = KnowledgeGraphBuilder(self.knowledge_store)
            
            # Initialize data extraction pipeline
            logger.info("🔄 Initializing Data Extraction Pipeline...")
            self.pipeline = DataExtractionPipeline(self.nlp_processor, self.graph_builder)
            
            # Initialize vector store
            logger.info("🔄 Initializing Vector Store...")
            self.vector_store = VectorStore()
            
            # Initialize query engine
            logger.info("🔄 Initializing Query Engine...")
            self.query_engine = QueryEngine(self.vector_store, self.knowledge_store)
            
            self.initialized = True
            logger.info("✅ Knowledge Pipeline Service initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Knowledge Pipeline Service: {e}")
            raise
    
    async def process_text_document(self, content: str, title: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Process a text document through the full knowledge extraction pipeline.
        
        Args:
            content: The text content to process
            title: Optional title for the document
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary containing processing results and created knowledge items
        """
        if not self.initialized:
            raise RuntimeError("Knowledge Pipeline Service not initialized")
        
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Processing text document: {title or 'Untitled'}")
            
            # Broadcast processing start if websocket available
            await self._broadcast_event({
                "type": "knowledge_processing_started",
                "timestamp": time.time(),
                "title": title or "Untitled",
                "content_length": len(content)
            })
            
            # Process through the extraction pipeline
            created_items = await self.pipeline.process_documents([content])
            
            # Update metrics
            self.documents_processed += 1
            entities_count = len([item for item in created_items if isinstance(item, Fact)])
            relationships_count = len([item for item in created_items if isinstance(item, Relationship)])
            self.entities_extracted += entities_count
            self.relationships_extracted += relationships_count
            
            # Add items to vector store for semantic search
            vector_items = []
            for item in created_items:
                if hasattr(item, 'content'):
                    if isinstance(item.content, dict):
                        # For Facts (entities)
                        if 'text' in item.content:
                            vector_items.append((item.id, item.content['text']))
                        # For Relationships
                        elif 'sentence' in item.content:
                            vector_items.append((item.id, item.content['sentence']))
                    elif isinstance(item.content, str):
                        vector_items.append((item.id, item.content))
            
            if vector_items:
                self.vector_store.add_items(vector_items)
                logger.info(f"Added {len(vector_items)} items to vector store")
            
            processing_time = time.time() - start_time
            
            # Log metrics
            logger.info(f"✅ Document processed successfully:")
            logger.info(f"   - Entities extracted: {entities_count}")
            logger.info(f"   - Relationships extracted: {relationships_count}")
            logger.info(f"   - Processing time: {processing_time:.2f}s")
            logger.info(f"   - Total documents processed: {self.documents_processed}")
            
            # Broadcast processing completion
            await self._broadcast_event({
                "type": "knowledge_processing_completed",
                "timestamp": time.time(),
                "title": title or "Untitled",
                "entities_extracted": entities_count,
                "relationships_extracted": relationships_count,
                "processing_time_seconds": processing_time,
                "total_items_created": len(created_items)
            })
            
            return {
                "success": True,
                "items_created": len(created_items),
                "entities_extracted": entities_count,
                "relationships_extracted": relationships_count,
                "processing_time_seconds": processing_time,
                "knowledge_items": [{"id": item.id, "type": item.type.value} for item in created_items]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process document: {e}")
            await self._broadcast_event({
                "type": "knowledge_processing_failed",
                "timestamp": time.time(),
                "title": title or "Untitled",
                "error": str(e)
            })
            raise
    
    async def semantic_query(self, query_text: str, k: int = 5) -> Dict[str, Any]:
        """
        Perform semantic search using the query engine.
        
        Args:
            query_text: The natural language query
            k: Number of results to return
            
        Returns:
            Dictionary containing query results
        """
        if not self.initialized:
            raise RuntimeError("Knowledge Pipeline Service not initialized")
        
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Processing semantic query: {query_text}")
            
            # Use the query engine for semantic search
            query_result = await self.query_engine.query(query_text, k=k)
            
            # Update metrics
            self.queries_processed += 1
            query_time = time.time() - start_time
            
            # Format results
            results = []
            for item in query_result.items:
                result_data = {
                    "id": item.id,
                    "type": item.type.value,
                    "confidence": getattr(item, 'confidence', 1.0),
                    "content": item.content
                }
                results.append(result_data)
            
            logger.info(f"✅ Query processed: {len(results)} results in {query_time:.2f}s")
            
            # Broadcast query event
            await self._broadcast_event({
                "type": "semantic_query_processed",
                "timestamp": time.time(),
                "query": query_text,
                "results_count": len(results),
                "query_time_seconds": query_time
            })
            
            return {
                "success": True,
                "query": query_text,
                "results": results,
                "total_results": len(results),
                "query_time_seconds": query_time
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process query: {e}")
            raise
    
    async def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """
        Export knowledge graph data for visualization.
        
        Returns:
            Dictionary containing nodes and edges for graph visualization
        """
        if not self.initialized:
            raise RuntimeError("Knowledge Pipeline Service not initialized")
        
        try:
            # Query all knowledge items from the store
            from godelOS.unified_agent_core.knowledge_store.interfaces import Query
            
            # Create a query to get all items
            all_items_query = Query(
                content={},
                max_results=1000  # Get up to 1000 items
            )
            
            query_result = await self.knowledge_store.query_knowledge(all_items_query)
            all_items = query_result.items
            
            nodes = []
            edges = []
            
            # Create nodes for entities (Facts)
            entity_nodes = {}
            for item in all_items:
                if isinstance(item, Fact) and isinstance(item.content, dict) and 'text' in item.content:
                    node = {
                        "id": item.id,
                        "label": item.content['text'],
                        "type": "entity",
                        "category": item.content.get('label', 'UNKNOWN'),
                        "confidence": getattr(item, 'confidence', 1.0)
                    }
                    nodes.append(node)
                    entity_nodes[item.id] = node
            
            # Create edges for relationships
            for item in all_items:
                if isinstance(item, Relationship):
                    if item.source_id in entity_nodes and item.target_id in entity_nodes:
                        edge = {
                            "source": item.source_id,
                            "target": item.target_id,
                            "label": item.relation_type,
                            "type": "relationship"
                        }
                        edges.append(edge)
            
            logger.info(f"📊 Knowledge graph exported: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                "nodes": nodes,
                "edges": edges,
                "statistics": {
                    "total_entities": len(nodes),
                    "total_relationships": len(edges),
                    "documents_processed": self.documents_processed,
                    "entities_extracted": self.entities_extracted,
                    "relationships_extracted": self.relationships_extracted,
                    "queries_processed": self.queries_processed
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to export knowledge graph: {e}")
            raise
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the current status of the knowledge pipeline."""
        return {
            "initialized": self.initialized,
            "components": {
                "nlp_processor": self.nlp_processor is not None,
                "knowledge_store": self.knowledge_store is not None,
                "graph_builder": self.graph_builder is not None,
                "pipeline": self.pipeline is not None,
                "vector_store": self.vector_store is not None,
                "query_engine": self.query_engine is not None
            },
            "metrics": {
                "documents_processed": self.documents_processed,
                "entities_extracted": self.entities_extracted,
                "relationships_extracted": self.relationships_extracted,
                "queries_processed": self.queries_processed
            }
        }
    
    async def _broadcast_event(self, event: Dict[str, Any]):
        """Broadcast an event via websocket if available."""
        if self.websocket_manager and self.websocket_manager.has_connections():
            try:
                await self.websocket_manager.broadcast(event)
            except Exception as e:
                logger.warning(f"Failed to broadcast event: {e}")

# Global instance
knowledge_pipeline_service = KnowledgePipelineService()
