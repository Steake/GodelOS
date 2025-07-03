"""
Knowledge Ingestion Service

Comprehensive service for ingesting knowledge from various sources including
URLs, files, Wikipedia, and manual text input with robust processing and validation.
"""

import asyncio
import hashlib
import json
import logging
import os
import tempfile
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

import aiofiles

# Optional imports for file processing
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    PyPDF2 = None

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    Document = None

from .knowledge_models import (
    ImportRequest, URLImportRequest, FileImportRequest, WikipediaImportRequest,
    TextImportRequest, BatchImportRequest, ImportProgress, ContentChunk,
    KnowledgeItem, ImportSource, ImportStatistics
)
from .external_apis import wikipedia_api, web_scraper, content_processor

# Will be set by main.py to avoid circular imports
knowledge_management_service = None

# Import knowledge pipeline service
from .knowledge_pipeline_service import knowledge_pipeline_service

logger = logging.getLogger(__name__)


class KnowledgeIngestionService:
    """Main service for knowledge ingestion operations."""
    
    def __init__(self, storage_path: str = "./knowledge_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.active_imports: Dict[str, ImportProgress] = {}
        self.knowledge_store: Dict[str, KnowledgeItem] = {}
        self.import_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.max_concurrent_imports = 5
        self.semaphore = asyncio.Semaphore(self.max_concurrent_imports)
        self.websocket_manager = None  # Will be set from main.py
        logger.info(f"🔍 INIT: KnowledgeIngestionService created, websocket_manager: {self.websocket_manager}")
    
    async def initialize(self, websocket_manager=None):
        """Initialize the knowledge ingestion service."""
        logger.info("Initializing Knowledge Ingestion Service...")
        
        # Set websocket manager if provided
        if websocket_manager:
            self.websocket_manager = websocket_manager
            logger.info(f"🔍 INITIALIZE: WebSocket manager set during initialization: {self.websocket_manager is not None}")
        
        # Initialize external APIs
        await wikipedia_api.initialize()
        await web_scraper.initialize()
        
        # Start processing task
        self.processing_task = asyncio.create_task(self._process_import_queue())
        
        # Load existing knowledge items
        await self._load_existing_knowledge()
        
        logger.info("Knowledge Ingestion Service initialized successfully")
    
    async def shutdown(self):
        """Shutdown the knowledge ingestion service."""
        logger.info("Shutting down Knowledge Ingestion Service...")
        
        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown external APIs
        await wikipedia_api.shutdown()
        await web_scraper.shutdown()
        
        logger.info("Knowledge Ingestion Service shutdown complete")
    
    async def import_from_url(self, request: URLImportRequest) -> str:
        """Import knowledge from a URL."""
        import_id = str(uuid.uuid4())
        
        progress = ImportProgress(
            import_id=import_id,
            status="queued",
            progress_percentage=0.0,
            current_step="Queued for processing",
            total_steps=5,
            completed_steps=0,
            started_at=time.time()
        )
        
        self.active_imports[import_id] = progress
        
        # Add to processing queue
        await self.import_queue.put(("url", import_id, request))
        
        logger.info(f"URL import queued: {import_id} for {request.url}")
        return import_id
    
    async def import_from_file(self, request: FileImportRequest, file_content: bytes) -> str:
        """Import knowledge from an uploaded file."""
        import_id = str(uuid.uuid4())
        
        progress = ImportProgress(
            import_id=import_id,
            status="queued",
            progress_percentage=0.0,
            current_step="Queued for processing",
            total_steps=6,
            completed_steps=0,
            started_at=time.time()
        )
        
        self.active_imports[import_id] = progress
        
        # Save file temporarily
        temp_file_path = self.storage_path / f"temp_{import_id}_{request.filename}"
        async with aiofiles.open(temp_file_path, 'wb') as f:
            await f.write(file_content)
        
        # Add to processing queue
        await self.import_queue.put(("file", import_id, request, str(temp_file_path)))
        
        logger.info(f"File import queued: {import_id} for {request.filename}")
        return import_id
    
    async def import_from_wikipedia(self, request: WikipediaImportRequest) -> str:
        """Import knowledge from Wikipedia."""
        import_id = str(uuid.uuid4())
        
        progress = ImportProgress(
            import_id=import_id,
            status="queued",
            progress_percentage=0.0,
            current_step="Queued for processing",
            total_steps=4,
            completed_steps=0,
            started_at=time.time()
        )
        
        self.active_imports[import_id] = progress
        
        # Add to processing queue
        await self.import_queue.put(("wikipedia", import_id, request))
        
        # IMMEDIATE FIX: Start background task to send progress updates
        logger.info(f"🔍 TASK: Creating background progress task for {import_id}")
        asyncio.create_task(self._send_wikipedia_progress_updates(import_id, request))
        logger.info(f"🔍 TASK: Background task created for {import_id}")
        
        logger.info(f"Wikipedia import queued: {import_id} for {request.page_title}")
        return import_id
    
    async def import_from_text(self, request: TextImportRequest) -> str:
        """Import knowledge from manual text input."""
        import_id = str(uuid.uuid4())
        
        progress = ImportProgress(
            import_id=import_id,
            status="queued",
            progress_percentage=0.0,
            current_step="Queued for processing",
            total_steps=3,
            completed_steps=0,
            started_at=time.time()
        )
        
        self.active_imports[import_id] = progress
        
        # Add to processing queue
        await self.import_queue.put(("text", import_id, request))
        
        logger.info(f"Text import queued: {import_id}")
        return import_id
    
    async def batch_import(self, request: BatchImportRequest) -> List[str]:
        """Process multiple import requests in batch."""
        import_ids = []
        
        for import_request in request.import_requests:
            if isinstance(import_request, URLImportRequest):
                import_id = await self.import_from_url(import_request)
            elif isinstance(import_request, WikipediaImportRequest):
                import_id = await self.import_from_wikipedia(import_request)
            elif isinstance(import_request, TextImportRequest):
                import_id = await self.import_from_text(import_request)
            else:
                logger.warning(f"Unsupported import request type: {type(import_request)}")
                continue
            
            import_ids.append(import_id)
        
        logger.info(f"Batch import queued: {len(import_ids)} items")
        return import_ids
    
    async def get_import_progress(self, import_id: str) -> Optional[ImportProgress]:
        """Get the progress of an import operation."""
        return self.active_imports.get(import_id)
    
    async def cancel_import(self, import_id: str) -> bool:
        """Cancel an import operation."""
        if import_id in self.active_imports:
            progress = self.active_imports[import_id]
            if progress.status in ["queued", "processing"]:
                progress.status = "cancelled"
                progress.error_message = "Import cancelled by user"
                logger.info(f"Import cancelled: {import_id}")
                return True
        return False
    
    async def _broadcast_progress_update(self, import_id: str, progress: ImportProgress):
        """Broadcast progress update via WebSocket if available."""
        logger.info(f"🔍 DEBUG: _broadcast_progress_update called for {import_id}")
        logger.info(f"🔍 DEBUG: websocket_manager exists: {self.websocket_manager is not None}")
        
        if self.websocket_manager:
            has_connections = self.websocket_manager.has_connections()
            logger.info(f"🔍 DEBUG: has_connections: {has_connections}")
            
            if has_connections:
                try:
                    progress_event = {
                        "type": "import_progress",
                        "timestamp": time.time(),
                        "import_id": import_id,
                        "progress": progress.progress_percentage,
                        "status": progress.status,
                        "message": progress.current_step,
                        "completed_steps": progress.completed_steps,
                        "total_steps": progress.total_steps
                    }
                    logger.info(f"🔍 DEBUG: Broadcasting progress event: {progress_event}")
                    await self.websocket_manager.broadcast(progress_event)
                    logger.info(f"🔍 DEBUG: Successfully broadcasted progress update for import {import_id}")
                except Exception as e:
                    logger.error(f"🔍 DEBUG: Failed to broadcast progress update: {e}")
                    import traceback
                    logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            else:
                logger.warning(f"🔍 DEBUG: No WebSocket connections available for progress update")
        else:
            logger.warning(f"🔍 DEBUG: websocket_manager is None, cannot broadcast progress")
    
    async def _broadcast_completion(self, import_id: str, success: bool, message: str = None):
        """Broadcast import completion via WebSocket if available."""
        logger.info(f"🔍 DEBUG: _broadcast_completion called for {import_id}, success: {success}")
        
        if self.websocket_manager and self.websocket_manager.has_connections():
            try:
                event_type = "import_completed" if success else "import_failed"
                completion_event = {
                    "type": event_type,
                    "timestamp": time.time(),
                    "import_id": import_id,
                    "message": message or ("Import completed successfully" if success else "Import failed"),
                    "success": success
                }
                logger.info(f"🔍 DEBUG: Broadcasting completion event: {completion_event}")
                await self.websocket_manager.broadcast(completion_event)
                logger.info(f"🔍 DEBUG: Successfully broadcasted import completion for {import_id}: {event_type}")
            except Exception as e:
                logger.error(f"🔍 DEBUG: Failed to broadcast completion event: {e}")
                import traceback
                logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"🔍 DEBUG: Cannot broadcast completion - websocket_manager or connections not available")
    
    async def _process_import_queue(self):
        """Background task to process the import queue."""
        while True:
            try:
                # Get next import from queue
                import_data = await self.import_queue.get()
                
                # Process with semaphore to limit concurrent imports
                async with self.semaphore:
                    await self._process_single_import(import_data)
                
                self.import_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in import queue processing: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_import(self, import_data: Tuple):
        """Process a single import operation."""
        import_type = import_data[0]
        import_id = import_data[1]
        request = import_data[2]
        
        try:
            progress = self.active_imports[import_id]
            progress.status = "processing"
            progress.current_step = "Starting import"
            
            logger.info(f"🔍 DEBUG: Starting processing for import {import_id}, type: {import_type}")
            
            # Broadcast initial progress update
            await self._broadcast_progress_update(import_id, progress)
            logger.info(f"🔍 DEBUG: Broadcasted initial progress for {import_id}")
            
            if import_type == "url":
                logger.info(f"🔍 DEBUG: Processing URL import {import_id}")
                await self._process_url_import(import_id, request)
            elif import_type == "file":
                logger.info(f"🔍 DEBUG: Processing file import {import_id}")
                file_path = import_data[3]
                await self._process_file_import(import_id, request, file_path)
            elif import_type == "wikipedia":
                logger.info(f"🔍 DEBUG: Processing Wikipedia import {import_id}")
                await self._process_wikipedia_import(import_id, request)
            elif import_type == "text":
                logger.info(f"🔍 DEBUG: Processing text import {import_id}")
                await self._process_text_import(import_id, request)
            
            logger.info(f"🔍 DEBUG: Individual processing completed for {import_id}")
            
            # Mark as completed
            progress.status = "completed"
            progress.progress_percentage = 100.0
            progress.current_step = "Import completed successfully"
            progress.completed_steps = progress.total_steps
            
            # Broadcast final progress update
            await self._broadcast_progress_update(import_id, progress)
            logger.info(f"🔍 DEBUG: Broadcasted final progress for {import_id}")
            
            # Broadcast completion event
            await self._broadcast_completion(import_id, True, "Import completed successfully")
            logger.info(f"🔍 DEBUG: Broadcasted completion event for {import_id}")
            
            logger.info(f"Import completed successfully: {import_id}")
            
        except Exception as e:
            logger.error(f"Import failed: {import_id} - {e}")
            logger.error(f"🔍 DEBUG: Exception details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            
            progress = self.active_imports[import_id]
            progress.status = "failed"
            progress.error_message = str(e)
            
            # Broadcast failure
            await self._broadcast_progress_update(import_id, progress)
            await self._broadcast_completion(import_id, False, str(e))
    
    async def _process_content(self, content: str, title: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw content using advanced knowledge extraction pipeline."""
        try:
            # Use the advanced knowledge pipeline for processing
            if knowledge_pipeline_service.initialized:
                logger.info("🔄 Using advanced knowledge extraction pipeline")
                
                # Process through the full pipeline
                pipeline_result = await knowledge_pipeline_service.process_text_document(
                    content=content,
                    title=title,
                    metadata=metadata
                )
                
                # Also do basic processing for backward compatibility
                cleaned_content = content_processor.clean_text(content)
                sentences = content_processor.extract_sentences(cleaned_content)
                chunks = content_processor.chunk_content(cleaned_content)
                keywords = content_processor.extract_keywords(cleaned_content)
                language = content_processor.detect_language(cleaned_content)
                
                return {
                    'title': title,
                    'content': cleaned_content,
                    'sentences': sentences,
                    'chunks': chunks,
                    'keywords': keywords,
                    'language': language,
                    'metadata': metadata,
                    'word_count': len(cleaned_content.split()),
                    'char_count': len(cleaned_content),
                    'pipeline_result': pipeline_result,  # Include advanced processing results
                    'entities_extracted': pipeline_result.get('entities_extracted', 0),
                    'relationships_extracted': pipeline_result.get('relationships_extracted', 0),
                    'knowledge_items': pipeline_result.get('knowledge_items', [])
                }
            else:
                logger.warning("⚠️ Knowledge pipeline not initialized, using basic processing")
                # Fallback to basic processing
                cleaned_content = content_processor.clean_text(content)
                sentences = content_processor.extract_sentences(cleaned_content)
                chunks = content_processor.chunk_content(cleaned_content)
                keywords = content_processor.extract_keywords(cleaned_content)
                language = content_processor.detect_language(cleaned_content)
                
                return {
                    'title': title,
                    'content': cleaned_content,
                    'sentences': sentences,
                    'chunks': chunks,
                    'keywords': keywords,
                    'language': language,
                    'metadata': metadata,
                    'word_count': len(cleaned_content.split()),
                    'char_count': len(cleaned_content)
                }
        except Exception as e:
            logger.error(f"❌ Error in content processing: {e}")
            # Fallback to basic processing on error
            cleaned_content = content_processor.clean_text(content)
            return {
                'title': title,
                'content': cleaned_content,
                'metadata': metadata,
                'word_count': len(cleaned_content.split()),
                'char_count': len(cleaned_content),
                'processing_error': str(e)
            }
    
    async def _load_existing_knowledge(self):
        """Load existing knowledge items from storage."""
        try:
            for item_file in self.storage_path.glob("*.json"):
                if item_file.name.startswith("temp_"):
                    continue
                
                try:
                    async with aiofiles.open(item_file, 'r') as f:
                        item_data = json.loads(await f.read())
                        knowledge_item = KnowledgeItem(**item_data)
                        self.knowledge_store[knowledge_item.id] = knowledge_item
                except Exception as e:
                    logger.warning(f"Failed to load knowledge item {item_file}: {e}")
            
            logger.info(f"Loaded {len(self.knowledge_store)} existing knowledge items")
        except Exception as e:
            logger.error(f"Error loading existing knowledge: {e}")

    async def _process_text_import(self, import_id: str, request):
        """Process text import request."""
        try:
            progress = self.active_imports[import_id]
            progress.current_step = "Processing text content"
            progress.progress_percentage = 25.0
            progress.completed_steps = 1
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            # Extract content and metadata
            content = request.content
            title = request.title or "Manual Text Entry"
            
            # Process the content
            progress.current_step = "Analyzing content"
            progress.progress_percentage = 50.0
            progress.completed_steps = 2
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            processed_data = await self._process_content(
                content=content,
                title=title,
                metadata=request.source.metadata
            )
            
            # Create knowledge item
            progress.current_step = "Creating knowledge item"
            progress.progress_percentage = 75.0
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            knowledge_item = KnowledgeItem(
                id=f"text-{import_id}",
                content=processed_data['content'],
                knowledge_type="fact",  # Default type, could be enhanced with classification
                title=processed_data['title'],
                source=request.source,
                import_id=import_id,
                confidence=0.9,  # High confidence for manual entry
                quality_score=0.85,  # Good quality score for manual entry
                categories=request.categorization_hints or ["manual"],
                auto_categories=[],
                manual_categories=request.categorization_hints or ["manual"],
                metadata={
                    'word_count': processed_data['word_count'],
                    'char_count': processed_data['char_count'],
                    'chunks': len(processed_data['chunks']),
                    'keywords': processed_data['keywords'],
                    'language': processed_data['language']
                }
            )
            
            # Store the knowledge item
            await self._store_knowledge_item(knowledge_item)
            self.knowledge_store[knowledge_item.id] = knowledge_item
            
            logger.info(f"Text import processed successfully: {import_id}")
            
        except Exception as e:
            logger.error(f"Failed to process text import {import_id}: {e}")
            raise

    async def _process_url_import(self, import_id: str, request):
        """Process URL import request."""
        try:
            progress = self.active_imports[import_id]
            progress.current_step = "Fetching URL content"
            progress.progress_percentage = 25.0
            progress.completed_steps = 1
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            # This is a placeholder - would need actual web scraping implementation
            content = f"Content from URL: {request.url}"
            title = f"Web Content from {request.url}"
            
            progress.current_step = "Processing web content"
            progress.progress_percentage = 50.0
            progress.completed_steps = 2
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            processed_data = await self._process_content(
                content=content,
                title=title,
                metadata=request.source.metadata
            )
            
            progress.current_step = "Creating knowledge item"
            progress.progress_percentage = 75.0
            progress.completed_steps = 3
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            # Create knowledge item
            knowledge_item = KnowledgeItem(
                id=f"url-{import_id}",
                content=processed_data['content'],
                knowledge_type="fact",
                title=processed_data['title'],
                source=request.source,
                import_id=import_id,
                confidence=0.7,
                quality_score=0.75,
                categories=request.categorization_hints or ["web"],
                auto_categories=[],
                manual_categories=request.categorization_hints or ["web"],
                relationships=[],
                metadata={
                    **processed_data.get('metadata', {}),
                    'source_url': request.url,
                    'max_depth': request.max_depth
                }
            )
            
            # Store the knowledge item
            await self._store_knowledge_item(knowledge_item)
            self.knowledge_store[knowledge_item.id] = knowledge_item
            
            logger.info(f"URL import processed successfully: {import_id}")
            
        except Exception as e:
            logger.error(f"Failed to process URL import {import_id}: {e}")
            raise

    async def _process_file_import(self, import_id: str, request, file_path: str):
        """Process file import request."""
        try:
            progress = self.active_imports[import_id]
            progress.current_step = "Reading file content"
            progress.progress_percentage = 25.0
            progress.completed_steps = 1
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            # Read file content based on type
            if request.file_type == "pdf" and not HAS_PDF:
                raise ValueError("PDF processing not available - install PyPDF2")
            elif request.file_type == "docx" and not HAS_DOCX:
                raise ValueError("DOCX processing not available - install python-docx")
            
            try:
                async with aiofiles.open(file_path, 'r', encoding=request.encoding) as f:
                    content = await f.read()
            except UnicodeDecodeError:
                # Try with different encoding for binary files
                async with aiofiles.open(file_path, 'rb') as f:
                    raw_content = await f.read()
                    content = f"Binary file content: {len(raw_content)} bytes"
            
            progress.current_step = "Processing file content"
            progress.progress_percentage = 50.0
            progress.completed_steps = 2
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            title = request.filename
            
            processed_data = await self._process_content(
                content=content,
                title=title,
                metadata=request.source.metadata
            )
            
            progress.current_step = "Creating knowledge item"
            progress.progress_percentage = 75.0
            progress.completed_steps = 3
            
            # Broadcast progress update
            await self._broadcast_progress_update(import_id, progress)
            
            # Create knowledge item
            knowledge_item = KnowledgeItem(
                id=f"file-{import_id}",
                content=processed_data['content'],
                knowledge_type="fact",
                title=processed_data['title'],
                source=request.source,
                import_id=import_id,
                confidence=0.8,
                quality_score=0.8,
                categories=request.categorization_hints or ["file"],
                auto_categories=[],
                manual_categories=request.categorization_hints or ["file"],
                relationships=[],
                metadata={
                    **processed_data.get('metadata', {}),
                    'filename': request.filename,
                    'file_type': request.file_type,
                    'encoding': request.encoding
                }
            )
            
            # Store the knowledge item
            await self._store_knowledge_item(knowledge_item)
            self.knowledge_store[knowledge_item.id] = knowledge_item
            
            logger.info(f"File import processed successfully: {import_id}")
            
        except Exception as e:
            logger.error(f"Failed to process file import {import_id}: {e}")
            raise

    async def _process_wikipedia_import(self, import_id: str, request):
        """Process Wikipedia import request."""
        try:
            logger.info(f"🔍 DEBUG: Starting Wikipedia processing for {import_id}")
            progress = self.active_imports[import_id]
            progress.current_step = "Fetching Wikipedia content"
            progress.progress_percentage = 25.0
            progress.completed_steps = 1
            
            # Broadcast progress update
            logger.info(f"🔍 DEBUG: Broadcasting progress update 1 for {import_id}")
            await self._broadcast_progress_update(import_id, progress)
            
            # This is a placeholder - would need actual Wikipedia API implementation
            logger.info(f"🔍 DEBUG: Fetching content for page: {request.page_title}")
            content = f"Wikipedia content for: {request.page_title}"
            title = request.page_title
            
            progress.current_step = "Processing Wikipedia content"
            progress.progress_percentage = 50.0
            progress.completed_steps = 2
            
            # Broadcast progress update
            logger.info(f"🔍 DEBUG: Broadcasting progress update 2 for {import_id}")
            await self._broadcast_progress_update(import_id, progress)
            
            logger.info(f"🔍 DEBUG: Processing content for {import_id}")
            processed_data = await self._process_content(
                content=content,
                title=title,
                metadata=request.source.metadata
            )
            logger.info(f"🔍 DEBUG: Content processed for {import_id}")
            
            progress.current_step = "Creating knowledge item"
            progress.progress_percentage = 75.0
            progress.completed_steps = 3
            
            # Broadcast progress update
            logger.info(f"🔍 DEBUG: Broadcasting progress update 3 for {import_id}")
            await self._broadcast_progress_update(import_id, progress)
            
            # Create knowledge item
            logger.info(f"🔍 DEBUG: Creating knowledge item for {import_id}")
            knowledge_item = KnowledgeItem(
                id=f"wikipedia-{import_id}",
                content=processed_data['content'],
                knowledge_type="fact",
                title=processed_data['title'],
                source=request.source,
                import_id=import_id,
                confidence=0.8,
                quality_score=0.8,
                categories=request.categorization_hints or ["wikipedia"],
                auto_categories=[],
                manual_categories=request.categorization_hints or ["wikipedia"],
                relationships=[],
                metadata={
                    **processed_data.get('metadata', {}),
                    'wikipedia_page': request.page_title,
                    'language': request.language
                }
            )
            logger.info(f"🔍 DEBUG: Knowledge item created for {import_id}")
            
            # Store the knowledge item
            logger.info(f"🔍 DEBUG: Storing knowledge item for {import_id}")
            await self._store_knowledge_item(knowledge_item)
            self.knowledge_store[knowledge_item.id] = knowledge_item
            logger.info(f"🔍 DEBUG: Knowledge item stored for {import_id}")
            
            progress.current_step = "Wikipedia import completed"
            progress.progress_percentage = 100.0
            progress.completed_steps = 4
            
            # Broadcast final progress update
            logger.info(f"🔍 DEBUG: Broadcasting final progress update for {import_id}")
            await self._broadcast_progress_update(import_id, progress)
            
            logger.info(f"Wikipedia import processed successfully: {import_id}")
            
        except Exception as e:
            logger.error(f"Failed to process Wikipedia import {import_id}: {e}")
            raise

    async def _store_knowledge_item(self, knowledge_item: KnowledgeItem):
        """Store a knowledge item to persistent storage and knowledge management service."""
        try:
            # Store to local file system
            file_path = self.storage_path / f"{knowledge_item.id}.json"
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(knowledge_item.model_dump_json(indent=2))

            logger.debug(f"Stored knowledge item: {knowledge_item.id}")
            
            # Add to knowledge management service for real-time updates
            global knowledge_management_service
            if knowledge_management_service:
                try:
                    knowledge_management_service.add_item(knowledge_item)
                    logger.info(f"🔍 KNOWLEDGE SYNC: Added item {knowledge_item.id} to knowledge management service")
                except Exception as e:
                    logger.warning(f"Failed to add item to knowledge management service: {e}")
            
            # Add to cognitive transparency knowledge graph for visualization
            await self._add_to_transparency_knowledge_graph(knowledge_item)
                    
            # Broadcast knowledge update via WebSocket
            if self.websocket_manager and self.websocket_manager.has_connections():
                await self.websocket_manager.broadcast({
                    "type": "knowledge_update",
                    "event": "item_added",
                    "data": {
                        "item_id": knowledge_item.id,
                        "title": knowledge_item.title,
                        "source": knowledge_item.source,
                        "categories": knowledge_item.categories,
                        "timestamp": time.time()
                    }
                })
                logger.info(f"🔍 KNOWLEDGE BROADCAST: Broadcasted knowledge update for {knowledge_item.id}")
                    
        except Exception as e:
            logger.error(f"Failed to store knowledge item {knowledge_item.id}: {e}")
            raise


    async def _add_to_transparency_knowledge_graph(self, knowledge_item: KnowledgeItem):
        """Add knowledge item to the cognitive transparency knowledge graph for visualization."""
        try:
            # Import here to avoid circular dependency
            from backend.cognitive_transparency_integration import cognitive_transparency_api
            
            if cognitive_transparency_api and cognitive_transparency_api.knowledge_graph:
                # Extract concepts from the knowledge item for graph nodes
                concepts = []
                
                # Add title as a main concept
                if knowledge_item.title:
                    concepts.append(knowledge_item.title)
                
                # Add categories as concepts
                if knowledge_item.categories:
                    concepts.extend(knowledge_item.categories)
                
                # Add keywords from metadata if available
                if knowledge_item.metadata and 'keywords' in knowledge_item.metadata:
                    keywords = knowledge_item.metadata['keywords']
                    if isinstance(keywords, list):
                        concepts.extend(keywords[:5])  # Limit to first 5 keywords
                
                # Add each concept as a node in the knowledge graph
                for concept in concepts:
                    if concept and isinstance(concept, str) and len(concept.strip()) > 0:
                        try:
                            result = cognitive_transparency_api.knowledge_graph.add_node(
                                concept=concept.strip(),
                                node_type="knowledge_item",
                                properties={
                                    "source_item_id": knowledge_item.id,
                                    "source": knowledge_item.source.source_type if knowledge_item.source else "unknown",
                                    "confidence": knowledge_item.confidence,
                                    "quality_score": knowledge_item.quality_score
                                },
                                confidence=knowledge_item.confidence
                            )
                            logger.info(f"🔍 GRAPH SYNC: Added concept '{concept}' to knowledge graph from item {knowledge_item.id}")
                        except Exception as e:
                            logger.warning(f"🔍 GRAPH SYNC: Failed to add concept '{concept}' to knowledge graph: {e}")
                
                # Create relationships between concepts from the same item
                if len(concepts) > 1:
                    main_concept = concepts[0]  # Use title as main concept
                    for related_concept in concepts[1:]:
                        if related_concept and isinstance(related_concept, str) and len(related_concept.strip()) > 0:
                            try:
                                result = cognitive_transparency_api.knowledge_graph.add_edge(
                                    source_concept=main_concept.strip(),
                                    target_concept=related_concept.strip(),
                                    relation_type="related_to",
                                    strength=0.7,
                                    properties={
                                        "source_item_id": knowledge_item.id,
                                        "relationship_source": "knowledge_ingestion"
                                    },
                                    confidence=0.7
                                )
                                logger.info(f"🔍 GRAPH SYNC: Added relationship '{main_concept}' -> '{related_concept}' from item {knowledge_item.id}")
                            except Exception as e:
                                logger.warning(f"🔍 GRAPH SYNC: Failed to add relationship '{main_concept}' -> '{related_concept}': {e}")
                
                # Broadcast knowledge graph update to frontend
                if self.websocket_manager and self.websocket_manager.has_connections():
                    try:
                        # Export updated graph data
                        graph_data = await cognitive_transparency_api.knowledge_graph.export_graph()
                        await self.websocket_manager.broadcast({
                            "type": "knowledge-graph-update",
                            "data": {
                                "nodes": graph_data.get("nodes", []),
                                "links": graph_data.get("edges", []),
                                "timestamp": time.time(),
                                "update_source": "knowledge_ingestion"
                            }
                        })
                        logger.info(f"🔍 GRAPH SYNC: Broadcasted updated knowledge graph with {len(graph_data.get('nodes', []))} nodes")
                    except Exception as e:
                        logger.warning(f"🔍 GRAPH SYNC: Failed to broadcast knowledge graph update: {e}")
                        
            else:
                logger.warning(f"🔍 GRAPH SYNC: Cognitive transparency knowledge graph not available")
                
        except Exception as e:
            logger.error(f"🔍 GRAPH SYNC: Failed to add knowledge item {knowledge_item.id} to transparency knowledge graph: {e}")
            # Don't raise the exception as this is not critical for the ingestion process
    
    async def _send_wikipedia_progress_updates(self, import_id: str, request: WikipediaImportRequest):
        """Send WebSocket progress updates for Wikipedia import processing."""
        logger.info(f"🔍 BACKGROUND TASK: Started for {import_id}")
        try:
            # Wait a tiny bit for the initial request to return
            await asyncio.sleep(0.1)
            logger.info(f"🔍 BACKGROUND TASK: Ready to send updates for {import_id}")
            
            # Progress update 1: Starting
            if self.websocket_manager and self.websocket_manager.has_connections():
                progress_event = {
                    "type": "import_progress",
                    "timestamp": time.time(),
                    "import_id": import_id,
                    "progress": 25.0,
                    "status": "processing",
                    "message": "Fetching Wikipedia content...",
                    "completed_steps": 1,
                    "total_steps": 4
                }
                await self.websocket_manager.broadcast(progress_event)
                logger.info(f"🔍 PROGRESS UPDATE: Sent 25% for {import_id}")
            
            await asyncio.sleep(0.5)
            
            # Progress update 2: Processing
            if self.websocket_manager and self.websocket_manager.has_connections():
                progress_event = {
                    "type": "import_progress",
                    "timestamp": time.time(),
                    "import_id": import_id,
                    "progress": 50.0,
                    "status": "processing",
                    "message": "Processing Wikipedia content...",
                    "completed_steps": 2,
                    "total_steps": 4
                }
                await self.websocket_manager.broadcast(progress_event)
                logger.info(f"🔍 PROGRESS UPDATE: Sent 50% for {import_id}")
            
            await asyncio.sleep(0.5)
            
            # Progress update 3: Creating
            if self.websocket_manager and self.websocket_manager.has_connections():
                progress_event = {
                    "type": "import_progress",
                    "timestamp": time.time(),
                    "import_id": import_id,
                    "progress": 75.0,
                    "status": "processing",
                    "message": "Creating knowledge item...",
                    "completed_steps": 3,
                    "total_steps": 4
                }
                await self.websocket_manager.broadcast(progress_event)
                logger.info(f"🔍 PROGRESS UPDATE: Sent 75% for {import_id}")
            
            # Wait for actual processing to complete (look for completion in active_imports)
            max_wait = 10  # 10 seconds max
            wait_time = 0
            while wait_time < max_wait:
                await asyncio.sleep(0.2)
                wait_time += 0.2
                
                if import_id in self.active_imports:
                    progress = self.active_imports[import_id]
                    if progress.status == "completed":
                        # Send completion event
                        if self.websocket_manager and self.websocket_manager.has_connections():
                            completion_event = {
                                "type": "import_completed",
                                "timestamp": time.time(),
                                "import_id": import_id,
                                "message": "Wikipedia import completed successfully",
                                "success": True
                            }
                            await self.websocket_manager.broadcast(completion_event)
                            logger.info(f"🔍 COMPLETION: Sent completion for {import_id}")
                        break
                    elif progress.status == "failed":
                        # Send failure event
                        if self.websocket_manager and self.websocket_manager.has_connections():
                            failure_event = {
                                "type": "import_failed",
                                "timestamp": time.time(),
                                "import_id": import_id,
                                "message": f"Wikipedia import failed: {progress.error_message}",
                                "success": False
                            }
                            await self.websocket_manager.broadcast(failure_event)
                            logger.info(f"🔍 FAILURE: Sent failure for {import_id}")
                        break
            
        except Exception as e:
            logger.error(f"🔍 ERROR: Failed to send progress updates for {import_id}: {e}")


# Global instance
knowledge_ingestion_service = KnowledgeIngestionService()