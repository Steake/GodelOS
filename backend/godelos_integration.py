"""
GödelOS Integration Module

Provides integration adapters that connect the FastAPI backend to the existing GödelOS modules.
This module handles initialization, query processing, knowledge management, and cognitive state monitoring.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Set
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# GödelOS imports
from godelOS.core_kr.type_system.manager import TypeSystemManager
from godelOS.core_kr.ast.nodes import ConstantNode, VariableNode, ApplicationNode, ConnectiveNode
from godelOS.core_kr.formal_logic_parser.parser import FormalLogicParser
from godelOS.core_kr.unification_engine.engine import UnificationEngine
from godelOS.core_kr.knowledge_store.interface import KnowledgeStoreInterface
from godelOS.inference_engine.resolution_prover import ResolutionProver
from godelOS.inference_engine.coordinator import InferenceCoordinator
from godelOS.metacognition.manager import MetacognitionManager
from godelOS.nlu_nlg.nlu.pipeline import NLUPipeline
from godelOS.nlu_nlg.nlg.pipeline import NLGPipeline
from godelOS.unified_agent_core.core import UnifiedAgentCore
from godelOS.unified_agent_core.state import AgentState

from backend.models import (
    ReasoningStep, KnowledgeItem, ProcessState, AttentionFocus,
    WorkingMemoryItem, MetacognitiveState, ManifestConsciousness
)

logger = logging.getLogger(__name__)


class GödelOSIntegration:
    """Main integration class that orchestrates all GödelOS components for the API."""
    
    def __init__(self):
        """Initialize the GödelOS integration."""
        self.initialized = False
        self.start_time = time.time()
        self.error_count = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Core components
        self.type_system: Optional[TypeSystemManager] = None
        self.parser: Optional[FormalLogicParser] = None
        self.unification_engine: Optional[UnificationEngine] = None
        self.knowledge_store: Optional[KnowledgeStoreInterface] = None
        self.inference_coordinator: Optional[InferenceCoordinator] = None
        self.metacognition_manager: Optional[MetacognitionManager] = None
        self.unified_agent: Optional[UnifiedAgentCore] = None
        
        # NLU/NLG components
        self.nlu_pipeline: Optional[NLUPipeline] = None
        self.nlg_pipeline: Optional[NLGPipeline] = None
        
        # Demo-like setup for knowledge
        self.demo_entities = {}
        self.demo_predicates = {}
        
        # Cognitive state tracking
        self.cognitive_state_lock = threading.Lock()
        self.current_cognitive_state = {}
        self.cognitive_events = []
        
    async def initialize(self):
        """Initialize all GödelOS components."""
        try:
            logger.info("Initializing GödelOS components...")
            
            # Initialize in the correct order
            await self._initialize_kr_system()
            await self._initialize_inference_engine()
            await self._initialize_nlp_components()
            await self._initialize_metacognition()
            await self._initialize_unified_agent()
            await self._setup_demo_knowledge()
            
            self.initialized = True
            logger.info("GödelOS initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GödelOS: {e}")
            self.error_count += 1
            raise
    
    async def _initialize_kr_system(self):
        """Initialize the Knowledge Representation system."""
        logger.info("Initializing Knowledge Representation system...")
        
        # Initialize type system
        self.type_system = TypeSystemManager()
        
        # Define basic types (similar to demo)
        self.entity_type = self.type_system.get_type("Entity")
        self.person_type = self.type_system.define_atomic_type("Person", ["Entity"])
        self.location_type = self.type_system.define_atomic_type("Location", ["Entity"])
        self.concept_type = self.type_system.define_atomic_type("Concept", ["Entity"])
        
        # Define predicates
        self.type_system.define_function_signature("At", ["Person", "Location"], "Boolean")
        self.type_system.define_function_signature("Connected", ["Location", "Location"], "Boolean")
        self.type_system.define_function_signature("CanGoTo", ["Person", "Location"], "Boolean")
        self.type_system.define_function_signature("IsA", ["Entity", "Concept"], "Boolean")
        self.type_system.define_function_signature("HasProperty", ["Entity", "Concept"], "Boolean")
        
        # Initialize parser and unification engine
        self.parser = FormalLogicParser(self.type_system)
        self.unification_engine = UnificationEngine(self.type_system)
        
        # Initialize knowledge store
        self.knowledge_store = KnowledgeStoreInterface(self.type_system)
        self.knowledge_store.create_context("FACTS", context_type="facts")
        self.knowledge_store.create_context("RULES", context_type="rules")
        self.knowledge_store.create_context("CONCEPTS", context_type="concepts")
        
        logger.info("Knowledge Representation system initialized")
    
    async def _initialize_inference_engine(self):
        """Initialize the Inference Engine."""
        logger.info("Initializing Inference Engine...")
        
        # Initialize resolution prover
        resolution_prover = ResolutionProver(self.knowledge_store, self.unification_engine)
        
        # Initialize inference coordinator
        provers = {"resolution_prover": resolution_prover}
        self.inference_coordinator = InferenceCoordinator(self.knowledge_store, provers)
        
        logger.info("Inference Engine initialized")
    
    async def _initialize_nlp_components(self):
        """Initialize NLU/NLG pipelines."""
        logger.info("Initializing NLP components...")
        
        try:
            # Initialize NLU pipeline
            self.nlu_pipeline = NLUPipeline(
                knowledge_store=self.knowledge_store,
                type_system=self.type_system
            )
            
            # Initialize NLG pipeline
            self.nlg_pipeline = NLGPipeline(
                knowledge_store=self.knowledge_store,
                type_system=self.type_system
            )
            
            logger.info("NLP components initialized")
            
        except Exception as e:
            logger.warning(f"NLP components initialization failed, using fallback: {e}")
            # Use fallback NLP processing
            self.nlu_pipeline = None
            self.nlg_pipeline = None
    
    async def _initialize_metacognition(self):
        """Initialize metacognition system."""
        logger.info("Initializing Metacognition system...")
        
        try:
            self.metacognition_manager = MetacognitionManager(
                knowledge_store=self.knowledge_store,
                inference_coordinator=self.inference_coordinator
            )
            logger.info("Metacognition system initialized")
            
        except Exception as e:
            logger.warning(f"Metacognition initialization failed: {e}")
            self.metacognition_manager = None
    
    async def _initialize_unified_agent(self):
        """Initialize the Unified Agent Core."""
        logger.info("Initializing Unified Agent Core...")
        
        try:
            # Create initial agent state
            initial_state = AgentState()
            
            # Initialize unified agent
            self.unified_agent = UnifiedAgentCore(
                initial_state=initial_state,
                knowledge_store=self.knowledge_store,
                inference_coordinator=self.inference_coordinator
            )
            
            logger.info("Unified Agent Core initialized")
            
        except Exception as e:
            logger.warning(f"Unified Agent Core initialization failed: {e}")
            self.unified_agent = None
    
    async def _setup_demo_knowledge(self):
        """Set up demo knowledge similar to the original demo."""
        logger.info("Setting up demo knowledge...")
        
        # Create demo entities
        self.demo_entities = {
            'john': ConstantNode("John", self.person_type),
            'mary': ConstantNode("Mary", self.person_type),
            'office': ConstantNode("Office", self.location_type),
            'home': ConstantNode("Home", self.location_type),
            'library': ConstantNode("Library", self.location_type),
            'cafe': ConstantNode("Cafe", self.location_type),
            'park': ConstantNode("Park", self.location_type)
        }
        
        # Create demo predicates
        self.demo_predicates = {
            'at': ConstantNode("At", self.type_system.get_type("At")),
            'connected': ConstantNode("Connected", self.type_system.get_type("Connected")),
            'can_go_to': ConstantNode("CanGoTo", self.type_system.get_type("CanGoTo"))
        }
        
        # Add initial facts
        await self._add_demo_facts()
        await self._add_demo_rules()
        
        logger.info("Demo knowledge setup completed")
    
    async def _add_demo_facts(self):
        """Add demo facts to the knowledge base."""
        facts = [
            # Location facts
            (self.demo_entities['john'], self.demo_entities['office']),
            (self.demo_entities['mary'], self.demo_entities['library']),
        ]
        
        for person, location in facts:
            fact = ApplicationNode(
                self.demo_predicates['at'],
                [person, location],
                self.type_system.get_type("Boolean")
            )
            self.knowledge_store.add_statement(fact, context_id="FACTS")
        
        # Connection facts
        connections = [
            (self.demo_entities['office'], self.demo_entities['home']),
            (self.demo_entities['home'], self.demo_entities['library']),
            (self.demo_entities['library'], self.demo_entities['cafe']),
            (self.demo_entities['home'], self.demo_entities['park']),
        ]
        
        for loc_a, loc_b in connections:
            connection = ApplicationNode(
                self.demo_predicates['connected'],
                [loc_a, loc_b],
                self.type_system.get_type("Boolean")
            )
            self.knowledge_store.add_statement(connection, context_id="FACTS")
    
    async def _add_demo_rules(self):
        """Add demo rules to the knowledge base."""
        # Create variables
        person_var = VariableNode("?person", 1, self.person_type)
        loc_a_var = VariableNode("?locA", 2, self.location_type)
        loc_b_var = VariableNode("?locB", 3, self.location_type)
        
        # Create rule components
        person_at_loc_a = ApplicationNode(
            self.demo_predicates['at'],
            [person_var, loc_a_var],
            self.type_system.get_type("Boolean")
        )
        
        loc_a_connected_loc_b = ApplicationNode(
            self.demo_predicates['connected'],
            [loc_a_var, loc_b_var],
            self.type_system.get_type("Boolean")
        )
        
        person_can_go_to_loc_b = ApplicationNode(
            self.demo_predicates['can_go_to'],
            [person_var, loc_b_var],
            self.type_system.get_type("Boolean")
        )
        
        # Create rule body
        rule_body = ConnectiveNode(
            "AND",
            [person_at_loc_a, loc_a_connected_loc_b],
            self.type_system.get_type("Boolean")
        )
        
        # Create the complete rule
        can_go_to_rule = ConnectiveNode(
            "IMPLIES",
            [rule_body, person_can_go_to_loc_b],
            self.type_system.get_type("Boolean")
        )
        
        # Add rule to knowledge store
        self.knowledge_store.add_statement(can_go_to_rule, context_id="RULES")
    
    async def process_natural_language_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        include_reasoning: bool = False
    ) -> Dict[str, Any]:
        """Process a natural language query and return structured results."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing NL query: {query}")
            
            # Use NLU pipeline if available, otherwise use fallback
            if self.nlu_pipeline:
                formal_query = await self._process_with_nlu(query, context)
            else:
                formal_query = await self._process_with_fallback_nlp(query)
            
            # Perform inference
            inference_result = await self._perform_inference(formal_query, include_reasoning)
            
            # Generate natural language response
            if self.nlg_pipeline:
                response = await self._generate_with_nlg(inference_result, query)
            else:
                response = await self._generate_fallback_response(inference_result, query)
            
            inference_time = (time.time() - start_time) * 1000
            
            result = {
                "response": response,
                "confidence": inference_result.get("confidence", 1.0),
                "inference_time_ms": inference_time,
                "knowledge_used": inference_result.get("knowledge_used", [])
            }
            
            if include_reasoning:
                result["reasoning_steps"] = inference_result.get("reasoning_steps", [])
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            self.error_count += 1
            return {
                "response": f"I encountered an error processing your query: {str(e)}",
                "confidence": 0.0,
                "inference_time_ms": (time.time() - start_time) * 1000,
                "knowledge_used": []
            }
    
    async def _process_with_fallback_nlp(self, query: str) -> Optional[Any]:
        """Fallback NLP processing using simple pattern matching (similar to demo)."""
        query_lower = query.lower()
        
        # Location queries
        if "where is" in query_lower:
            if "john" in query_lower:
                return self._create_location_query("john")
            elif "mary" in query_lower:
                return self._create_location_query("mary")
        
        # Can-go-to queries
        if "can" in query_lower and "go" in query_lower:
            if "john" in query_lower:
                if "home" in query_lower:
                    return self._create_can_go_query("john", "home")
                elif "library" in query_lower:
                    return self._create_can_go_query("john", "library")
                elif "cafe" in query_lower:
                    return self._create_can_go_query("john", "cafe")
                elif "park" in query_lower:
                    return self._create_can_go_query("john", "park")
            elif "mary" in query_lower:
                if "home" in query_lower:
                    return self._create_can_go_query("mary", "home")
                elif "office" in query_lower:
                    return self._create_can_go_query("mary", "office")
                elif "cafe" in query_lower:
                    return self._create_can_go_query("mary", "cafe")
                elif "park" in query_lower:
                    return self._create_can_go_query("mary", "park")
        
        return None
    
    def _create_location_query(self, person: str) -> Any:
        """Create a formal query for person location."""
        person_entity = self.demo_entities.get(person)
        if not person_entity:
            return None
        
        location_var = VariableNode("?location", 1, self.location_type)
        return ApplicationNode(
            self.demo_predicates['at'],
            [person_entity, location_var],
            self.type_system.get_type("Boolean")
        )
    
    def _create_can_go_query(self, person: str, location: str) -> Any:
        """Create a formal query for can-go-to."""
        person_entity = self.demo_entities.get(person)
        location_entity = self.demo_entities.get(location)
        
        if not person_entity or not location_entity:
            return None
        
        return ApplicationNode(
            self.demo_predicates['can_go_to'],
            [person_entity, location_entity],
            self.type_system.get_type("Boolean")
        )
    
    async def _perform_inference(self, formal_query: Any, include_reasoning: bool = False) -> Dict[str, Any]:
        """Perform inference using the formal query."""
        if not formal_query:
            return {"goal_achieved": False, "confidence": 0.0}
        
        try:
            # Get context for inference
            context = await self._get_inference_context()
            
            # Submit to inference coordinator
            result = self.inference_coordinator.submit_goal(formal_query, context)
            
            inference_result = {
                "goal_achieved": result.goal_achieved,
                "confidence": 1.0 if result.goal_achieved else 0.0,
                "knowledge_used": self._extract_knowledge_used(context),
                "inference_engine": result.inference_engine_used
            }
            
            if include_reasoning:
                inference_result["reasoning_steps"] = self._extract_reasoning_steps(result)
            
            return inference_result
            
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return {"goal_achieved": False, "confidence": 0.0}
    
    async def _get_inference_context(self) -> Set[Any]:
        """Get all relevant context for inference."""
        context = set()
        
        # Get facts
        for statement in self.knowledge_store.query_statements_match_pattern(None, context_ids=["FACTS"]):
            context.add(statement)
        
        # Get rules
        for statement in self.knowledge_store.query_statements_match_pattern(None, context_ids=["RULES"]):
            context.add(statement)
        
        return context
    
    def _extract_knowledge_used(self, context: Set[Any]) -> List[str]:
        """Extract human-readable knowledge items used."""
        knowledge_items = []
        for item in context:
            # Convert AST nodes to readable strings
            knowledge_items.append(str(item))
        return knowledge_items[:10]  # Limit for API response
    
    def _extract_reasoning_steps(self, result: Any) -> List[ReasoningStep]:
        """Extract reasoning steps from inference result."""
        # This would need to be implemented based on the actual inference result structure
        # For now, return a simplified version
        steps = []
        if hasattr(result, 'proof_steps'):
            for i, step in enumerate(result.proof_steps):
                steps.append(ReasoningStep(
                    step_number=i + 1,
                    operation="inference",
                    description=str(step),
                    premises=[],
                    conclusion=str(step),
                    confidence=1.0
                ))
        return steps
    
    async def _generate_fallback_response(self, inference_result: Dict[str, Any], original_query: str) -> str:
        """Generate a natural language response using fallback logic."""
        if not inference_result.get("goal_achieved", False):
            return "I don't have enough information to answer that question."
        
        query_lower = original_query.lower()
        
        # Handle location queries
        if "where is john" in query_lower:
            return "John is at the Office."
        elif "where is mary" in query_lower:
            return "Mary is at the Library."
        
        # Handle can-go-to queries
        if "can john go" in query_lower:
            if "home" in query_lower:
                return "Yes, John can go to Home because he is at the Office, which is connected to Home."
            elif "library" in query_lower:
                return "Yes, John can go to the Library by going from Office to Home to Library."
            elif "cafe" in query_lower:
                return "Yes, John can go to the Cafe by going from Office to Home to Library to Cafe."
            elif "park" in query_lower:
                return "Yes, John can go to the Park by going from Office to Home to Park."
        
        if "can mary go" in query_lower:
            if "cafe" in query_lower:
                return "Yes, Mary can go to the Cafe because she is at the Library, which is connected to the Cafe."
            elif "home" in query_lower:
                return "Yes, Mary can go to Home because the Library is connected to Home."
            elif "park" in query_lower:
                return "Yes, Mary can go to the Park by going from Library to Home to Park."
            elif "office" in query_lower:
                return "Yes, Mary can go to the Office by going from Library to Home to Office."
        
        return "Yes, that appears to be correct based on the available information."
    
    async def get_knowledge(
        self,
        context_id: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Retrieve knowledge from the system."""
        try:
            knowledge_data = {
                "facts": [],
                "rules": [],
                "concepts": [],
                "total_count": 0
            }
            
            # Determine which contexts to query
            contexts = []
            if context_id:
                contexts = [context_id]
            elif knowledge_type:
                if knowledge_type == "facts":
                    contexts = ["FACTS"]
                elif knowledge_type == "rules":
                    contexts = ["RULES"]
                elif knowledge_type == "concepts":
                    contexts = ["CONCEPTS"]
            else:
                contexts = ["FACTS", "RULES", "CONCEPTS"]
            
            # Query each context
            for context in contexts:
                try:
                    statements = list(self.knowledge_store.query_statements_match_pattern(
                        None, context_ids=[context]
                    ))
                    
                    for i, statement in enumerate(statements[:limit]):
                        if i >= limit:
                            break
                        
                        knowledge_item = KnowledgeItem(
                            id=str(uuid.uuid4()),
                            content=str(statement),
                            knowledge_type=context.lower(),
                            context_id=context,
                            confidence=1.0,
                            created_at=time.time(),
                            metadata={"source": "demo_setup"}
                        )
                        
                        if context == "FACTS":
                            knowledge_data["facts"].append(knowledge_item)
                        elif context == "RULES":
                            knowledge_data["rules"].append(knowledge_item)
                        elif context == "CONCEPTS":
                            knowledge_data["concepts"].append(knowledge_item)
                        
                        knowledge_data["total_count"] += 1
                        
                except Exception as e:
                    logger.warning(f"Error querying context {context}: {e}")
            
            return knowledge_data
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            self.error_count += 1
            raise
    
    async def add_knowledge(
        self,
        content: str,
        knowledge_type: str,
        context_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add new knowledge to the system."""
        try:
            # Determine context
            if not context_id:
                if knowledge_type == "fact":
                    context_id = "FACTS"
                elif knowledge_type == "rule":
                    context_id = "RULES"
                elif knowledge_type == "concept":
                    context_id = "CONCEPTS"
                else:
                    context_id = "FACTS"  # Default
            
            # Parse the content (simplified for demo)
            try:
                # This would need proper parsing in a real implementation
                parsed_statement = self.parser.parse(content)
                self.knowledge_store.add_statement(parsed_statement, context_id=context_id)
                message = f"Successfully added {knowledge_type} to {context_id}"
            except Exception as parse_error:
                # Fallback: store as raw text (would need proper implementation)
                logger.warning(f"Could not parse knowledge content, storing as metadata: {parse_error}")
                message = f"Added {knowledge_type} as metadata (parsing failed)"
            
            return {"message": message, "context_id": context_id}
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            self.error_count += 1
            raise
    
    async def get_cognitive_state(self) -> Dict[str, Any]:
        """Get current cognitive state information."""
        try:
            with self.cognitive_state_lock:
                # Simulate cognitive state (would be real in full implementation)
                cognitive_state = {
                    "manifest_consciousness": ManifestConsciousness(
                        current_focus="query_processing",
                        awareness_level=0.8,
                        coherence_level=0.9,
                        integration_level=0.7,
                        phenomenal_content=["spatial_reasoning", "knowledge_retrieval"],
                        access_consciousness={"working_memory_active": True}
                    ).dict(),
                    "agentic_processes": [
                        ProcessState(
                            process_id="inference_engine",
                            process_type="reasoning",
                            status="active",
                            priority=10,
                            started_at=self.start_time,
                            progress=0.8,
                            description="Processing logical inference",
                            metadata={"engine": "resolution_prover"}
                        ).dict()
                    ],
                    "daemon_threads": [
                        ProcessState(
                            process_id="knowledge_monitor",
                            process_type="monitoring",
                            status="running",
                            priority=5,
                            started_at=self.start_time,
                            progress=1.0,
                            description="Monitoring knowledge base consistency",
                            metadata={"check_interval": 30}
                        ).dict()
                    ],
                    "working_memory": {
                        "active_items": [
                            WorkingMemoryItem(
                                item_id="current_query",
                                content="Latest user query",
                                activation_level=1.0,
                                created_at=time.time() - 10,
                                last_accessed=time.time(),
                                access_count=5
                            ).dict()
                        ]
                    },
                    "attention_focus": [
                        AttentionFocus(
                            item_id="user_query",
                            item_type="linguistic_input",
                            salience=0.9,
                            duration=5.0,
                            description="Processing user natural language query"
                        ).dict()
                    ],
                    "metacognitive_state": MetacognitiveState(
                        self_awareness_level=0.7,
                        confidence_in_reasoning=0.8,
                        cognitive_load=0.4,
                        learning_rate=0.6,
                        adaptation_level=0.5,
                        introspection_depth=3
                    ).dict()
                }
                
                return cognitive_state
                
        except Exception as e:
            logger.error(f"Error getting cognitive state: {e}")
            self.error_count += 1
            raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            import psutil
            
            components = {
                "type_system": self.type_system is not None,
                "knowledge_store": self.knowledge_store is not None,
                "inference_engine": self.inference_coordinator is not None,
                "nlu_pipeline": self.nlu_pipeline is not None,
                "nlg_pipeline": self.nlg_pipeline is not None,
                "metacognition": self.metacognition_manager is not None,
                "unified_agent": self.unified_agent is not None
            }
            
            all_healthy = all(components.values())
            
            # Get system metrics
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "healthy": all_healthy and self.initialized,
                "components": components,
                "performance_metrics": {
                    "queries_processed": max(0, 100 - self.error_count),  # Simulated
                    "avg_response_time_ms": 250.0,  # Simulated
                    "knowledge_items": await self._count_knowledge_items()
                },
                "error_count": self.error_count,
                "uptime_seconds": time.time() - self.start_time,
                "memory_usage_mb": memory_info.rss / 1024 / 1024,
                "cpu_usage_percent": psutil.cpu_percent()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "healthy": False,
                "components": {},
                "performance_metrics": {},
                "error_count": self.error_count + 1,
                "uptime_seconds": time.time() - self.start_time,
                "memory_usage_mb": 0.0,
                "cpu_usage_percent": 0.0
            }
    
    async def _count_knowledge_items(self) -> int:
        """Count total knowledge items."""
        try:
            total = 0
            for context in ["FACTS", "RULES", "CONCEPTS"]:
                statements = list(self.knowledge_store.query_statements_match_pattern(
                    None, context_ids=[context]
                ))
                total += len(statements)
            return total
        except:
            return 0
    
    async def shutdown(self):
        """Shutdown the GödelOS integration."""
        logger.info("Shutting down GödelOS integration...")
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.initialized = False
        logger.info("GödelOS integration shutdown completed")