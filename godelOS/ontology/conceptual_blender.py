"""
Conceptual Blender & Analogy-Driven Novelty (CBAN) for GödelOS.

This module provides mechanisms for conceptual blending, analogy-based concept creation,
and novelty detection and generation.
"""

from typing import Dict, List, Set, Optional, Any, Tuple, Callable
import logging
import random
from collections import defaultdict

# Setup logging
logger = logging.getLogger(__name__)

class ConceptualBlender:
    """
    Implements conceptual blending and analogy-driven novelty mechanisms.
    
    The ConceptualBlender is responsible for:
    - Implementing conceptual blending mechanisms to create new concepts from existing ones
    - Supporting analogy-based concept creation
    - Implementing novelty detection and generation
    - Ensuring semantic coherence of blended concepts
    - Providing methods for evaluating the utility of new concepts
    """
    
    def __init__(self, ontology_manager):
        """
        Initialize the ConceptualBlender.
        
        Args:
            ontology_manager: Reference to the OntologyManager
        """
        self._ontology_manager = ontology_manager
        self._blend_strategies = {
            "property_merge": self._blend_by_property_merge,
            "structure_mapping": self._blend_by_structure_mapping,
            "selective_projection": self._blend_by_selective_projection,
            "cross_space_mapping": self._blend_by_cross_space_mapping
        }
        self._analogy_strategies = {
            "structure_mapping": self._analogy_by_structure_mapping,
            "attribute_mapping": self._analogy_by_attribute_mapping,
            "relational_mapping": self._analogy_by_relational_mapping
        }
        self._novelty_metrics = {
            "property_divergence": self._compute_property_divergence,
            "structural_novelty": self._compute_structural_novelty,
            "taxonomic_distance": self._compute_taxonomic_distance
        }
        
        # Cache for computed blends and analogies
        self._blend_cache = {}
        self._analogy_cache = {}
        
        logger.info("ConceptualBlender initialized")
    
    # Conceptual blending methods
    
    def blend_concepts(self, 
                       concept_ids: List[str], 
                       strategy: str = "property_merge", 
                       constraints: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Blend multiple concepts to create a new concept.
        
        Args:
            concept_ids: List of concept IDs to blend
            strategy: Blending strategy to use
            constraints: Optional constraints on the blending process
            
        Returns:
            Optional[Dict[str, Any]]: The blended concept data if successful, None otherwise
        """
        if len(concept_ids) < 2:
            logger.warning("At least two concepts are required for blending")
            return None
        
        # Check if all concepts exist
        for concept_id in concept_ids:
            if not self._ontology_manager.get_concept(concept_id):
                logger.warning(f"Concept {concept_id} does not exist")
                return None
        
        # Check if this blend is cached
        cache_key = (tuple(sorted(concept_ids)), strategy, str(constraints))
        if cache_key in self._blend_cache:
            logger.info(f"Using cached blend for concepts {concept_ids}")
            return self._blend_cache[cache_key]
        
        # Apply the selected blending strategy
        if strategy not in self._blend_strategies:
            logger.warning(f"Unknown blending strategy: {strategy}")
            return None
        
        blend_result = self._blend_strategies[strategy](concept_ids, constraints or {})
        
        if blend_result:
            # Ensure semantic coherence
            coherence_issues = self._check_semantic_coherence(blend_result)
            if coherence_issues:
                logger.warning(f"Semantic coherence issues detected: {coherence_issues}")
                # Try to repair coherence issues
                blend_result = self._repair_coherence_issues(blend_result, coherence_issues)
            
            # Cache the result
            self._blend_cache[cache_key] = blend_result
            
            logger.info(f"Successfully blended concepts {concept_ids} using strategy {strategy}")
        
        return blend_result
    
    def _blend_by_property_merge(self, concept_ids: List[str], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Blend concepts by merging their properties.
        
        Args:
            concept_ids: List of concept IDs to blend
            constraints: Constraints on the blending process
            
        Returns:
            Dict[str, Any]: The blended concept data
        """
        concepts = [self._ontology_manager.get_concept(cid) for cid in concept_ids]
        
        # Create a new concept with merged properties
        blended_concept = {
            "name": self._generate_blend_name(concepts),
            "description": f"Blend of {', '.join(c.get('name', cid) for c, cid in zip(concepts, concept_ids))}",
            "source_concepts": concept_ids,
            "blend_strategy": "property_merge",
            "properties": {},
            "relations": []
        }
        
        # Merge properties
        property_weights = constraints.get("property_weights", {})
        for concept, cid in zip(concepts, concept_ids):
            for prop_id, prop_value in self._get_concept_properties(cid).items():
                # Skip properties explicitly excluded in constraints
                if prop_id in constraints.get("excluded_properties", []):
                    continue
                
                # If property already exists in the blend, decide how to combine
                if prop_id in blended_concept["properties"]:
                    # Default: weighted average for numeric properties, first non-None for others
                    if isinstance(prop_value, (int, float)) and isinstance(blended_concept["properties"][prop_id], (int, float)):
                        weight = property_weights.get(prop_id, {}).get(cid, 1.0)
                        current_weight = sum(property_weights.get(prop_id, {}).get(c, 1.0) for c in concept_ids 
                                            if c in blended_concept["properties"].get(f"{prop_id}_sources", []))
                        
                        blended_concept["properties"][prop_id] = (
                            (blended_concept["properties"][prop_id] * current_weight + prop_value * weight) / 
                            (current_weight + weight)
                        )
                        blended_concept["properties"].setdefault(f"{prop_id}_sources", []).append(cid)
                else:
                    # Add new property
                    blended_concept["properties"][prop_id] = prop_value
                    blended_concept["properties"].setdefault(f"{prop_id}_sources", []).append(cid)
        
        # Merge relations (only include relations that apply to multiple source concepts)
        relation_counts = defaultdict(int)
        for cid in concept_ids:
            for relation_id in self._ontology_manager._concept_relations.get(cid, []):
                relation_counts[relation_id] += 1
        
        for relation_id, count in relation_counts.items():
            # Include relation if it appears in multiple source concepts or is in the include_relations constraint
            if count > 1 or relation_id in constraints.get("include_relations", []):
                # For each source concept, get the objects of this relation
                for cid in concept_ids:
                    related_objects = self._ontology_manager.get_related_concepts(cid, relation_id)
                    for obj_id in related_objects:
                        # Skip if the relation is in excluded_relations
                        if relation_id in constraints.get("excluded_relations", []):
                            continue
                        
                        blended_concept["relations"].append({
                            "relation_id": relation_id,
                            "object_id": obj_id,
                            "source_concept": cid
                        })
        
        return blended_concept
    
    def _blend_by_structure_mapping(self, concept_ids: List[str], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Blend concepts by mapping their structural elements."""
        # Implementation simplified for brevity
        return self._blend_by_property_merge(concept_ids, constraints)  # Fallback to property merge
    
    def _blend_by_selective_projection(self, concept_ids: List[str], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Blend concepts by selectively projecting elements from each input concept."""
        # Implementation simplified for brevity
        return self._blend_by_property_merge(concept_ids, constraints)  # Fallback to property merge
    
    def _blend_by_cross_space_mapping(self, concept_ids: List[str], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Blend concepts by mapping across conceptual spaces."""
        # Implementation simplified for brevity
        return self._blend_by_property_merge(concept_ids, constraints)  # Fallback to property merge
    
    # Analogy methods
    
    def create_analogy(self, 
                      source_id: str, 
                      target_id: str, 
                      strategy: str = "structure_mapping",
                      constraints: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create an analogy between two concepts.
        
        Args:
            source_id: ID of the source concept
            target_id: ID of the target concept
            strategy: Analogy strategy to use
            constraints: Optional constraints on the analogy process
            
        Returns:
            Optional[Dict[str, Any]]: The analogy data if successful, None otherwise
        """
        # Check if both concepts exist
        source = self._ontology_manager.get_concept(source_id)
        target = self._ontology_manager.get_concept(target_id)
        
        if not source or not target:
            logger.warning("Source or target concept not found")
            return None
        
        # Check if this analogy is cached
        cache_key = (source_id, target_id, strategy, str(constraints))
        if cache_key in self._analogy_cache:
            logger.info(f"Using cached analogy for {source_id} -> {target_id}")
            return self._analogy_cache[cache_key]
        
        # Apply the selected analogy strategy
        if strategy not in self._analogy_strategies:
            logger.warning(f"Unknown analogy strategy: {strategy}")
            return None
        
        analogy_result = self._analogy_strategies[strategy](source_id, target_id, constraints or {})
        
        if analogy_result:
            # Cache the result
            self._analogy_cache[cache_key] = analogy_result
            logger.info(f"Successfully created analogy from {source_id} to {target_id} using strategy {strategy}")
        
        return analogy_result
    
    def _analogy_by_structure_mapping(self, source_id: str, target_id: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Create an analogy by mapping structural elements between concepts."""
        # Simplified implementation
        return {
            "source_id": source_id,
            "target_id": target_id,
            "strategy": "structure_mapping",
            "correspondences": self._find_structural_correspondences(source_id, target_id),
            "novel_inferences": []
        }
    
    def _analogy_by_attribute_mapping(self, source_id: str, target_id: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Create an analogy by mapping attributes between concepts."""
        # Simplified implementation
        return {
            "source_id": source_id,
            "target_id": target_id,
            "strategy": "attribute_mapping",
            "correspondences": {},
            "novel_inferences": []
        }
    
    def _analogy_by_relational_mapping(self, source_id: str, target_id: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Create an analogy by mapping relations between concepts."""
        # Simplified implementation
        return {
            "source_id": source_id,
            "target_id": target_id,
            "strategy": "relational_mapping",
            "correspondences": {},
            "novel_inferences": []
        }
    
    # Novelty detection and generation methods
    
    def detect_novelty(self, concept_data: Dict[str, Any], metric: str = "property_divergence") -> float:
        """
        Detect the novelty of a concept relative to existing concepts.
        
        Args:
            concept_data: The concept data to evaluate
            metric: The novelty metric to use
            
        Returns:
            float: The novelty score (0.0-1.0, higher is more novel)
        """
        if metric not in self._novelty_metrics:
            logger.warning(f"Unknown novelty metric: {metric}")
            return 0.0
        
        return self._novelty_metrics[metric](concept_data)
    
    def generate_novel_concept(self, 
                              seed_concept_ids: List[str], 
                              novelty_threshold: float = 0.5,
                              max_attempts: int = 10) -> Optional[Dict[str, Any]]:
        """
        Generate a novel concept based on seed concepts.
        
        Args:
            seed_concept_ids: List of concept IDs to use as seeds
            novelty_threshold: Minimum novelty score required
            max_attempts: Maximum number of generation attempts
            
        Returns:
            Optional[Dict[str, Any]]: The novel concept data if successful, None otherwise
        """
        # Check if all seed concepts exist
        for concept_id in seed_concept_ids:
            if not self._ontology_manager.get_concept(concept_id):
                logger.warning(f"Seed concept {concept_id} does not exist")
                return None
        
        # Try different blending strategies and constraints to generate a novel concept
        strategies = list(self._blend_strategies.keys())
        
        for _ in range(max_attempts):
            # Randomly select a strategy
            strategy = random.choice(strategies)
            
            # Generate random constraints
            constraints = self._generate_random_constraints(seed_concept_ids)
            
            # Blend the concepts
            blended_concept = self.blend_concepts(seed_concept_ids, strategy, constraints)
            
            if blended_concept:
                # Check novelty
                novelty_score = self.detect_novelty(blended_concept)
                
                if novelty_score >= novelty_threshold:
                    logger.info(f"Generated novel concept with novelty score {novelty_score}")
                    blended_concept["novelty_score"] = novelty_score
                    return blended_concept
        
        logger.warning(f"Failed to generate a novel concept after {max_attempts} attempts")
        return None
    
    def _compute_property_divergence(self, concept_data: Dict[str, Any]) -> float:
        """Compute novelty based on property divergence from existing concepts."""
        # Simplified implementation
        return random.uniform(0.3, 0.9)  # Placeholder
    
    def _compute_structural_novelty(self, concept_data: Dict[str, Any]) -> float:
        """Compute novelty based on structural differences from existing concepts."""
        # Simplified implementation
        return random.uniform(0.3, 0.9)  # Placeholder
    
    def _compute_taxonomic_distance(self, concept_data: Dict[str, Any]) -> float:
        """Compute novelty based on taxonomic distance from existing concepts."""
        # Simplified implementation
        return random.uniform(0.3, 0.9)  # Placeholder
    
    # Semantic coherence methods
    
    def _check_semantic_coherence(self, concept_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check the semantic coherence of a concept and return any issues found.
        
        Args:
            concept_data: The concept data to check
            
        Returns:
            List[Dict[str, Any]]: List of coherence issues
        """
        # Simplified implementation
        return []  # Placeholder - no issues found
    
    def _repair_coherence_issues(self, concept_data: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Attempt to repair coherence issues in a concept.
        
        Args:
            concept_data: The concept data to repair
            issues: List of coherence issues to repair
            
        Returns:
            Dict[str, Any]: The repaired concept data
        """
        # Simplified implementation - just return the original concept data
        return concept_data
    
    # Utility evaluation methods
    
    def evaluate_concept_utility(self, concept_data: Dict[str, Any], metric: str = "explanatory_power") -> float:
        """
        Evaluate the utility of a concept.
        
        Args:
            concept_data: The concept data to evaluate
            metric: The utility metric to use
            
        Returns:
            float: The utility score (0.0-1.0, higher is more useful)
        """
        # Simplified implementation
        return random.uniform(0.5, 1.0)  # Placeholder
    
    # Helper methods
    
    def _generate_blend_name(self, concepts: List[Dict[str, Any]]) -> str:
        """Generate a name for a blended concept."""
        # Simple implementation: combine the first parts of each concept name
        name_parts = []
        for concept in concepts:
            if "name" in concept:
                name = concept["name"]
                # Take the first part of the name (up to 3 characters)
                name_parts.append(name[:3])
        
        if name_parts:
            return "-".join(name_parts)
        else:
            return f"BlendedConcept-{random.randint(1000, 9999)}"
    
    def _get_concept_properties(self, concept_id: str) -> Dict[str, Any]:
        """Get all properties of a concept."""
        concept = self._ontology_manager.get_concept(concept_id)
        if not concept:
            return {}
        
        # Get properties directly from the concept data if available
        if "properties" in concept:
            return concept["properties"]
        
        # Otherwise, get from the ontology manager's property storage
        properties = {}
        for prop_id in self._ontology_manager._properties:
            value = self._ontology_manager.get_concept_property(concept_id, prop_id)
            if value is not None:
                properties[prop_id] = value
        
        return properties
    
    def _find_structural_correspondences(self, source_id: str, target_id: str) -> Dict[str, Dict[str, str]]:
        """Find structural correspondences between two concepts."""
        # Simplified implementation
        return {
            "concepts": {},  # source_concept_id -> target_concept_id
            "relations": {},  # source_relation_id -> target_relation_id
            "properties": {}  # source_property_id -> target_property_id
        }
    
    def _generate_random_constraints(self, concept_ids: List[str]) -> Dict[str, Any]:
        """Generate random constraints for concept blending."""
        # Simplified implementation
        return {
            "excluded_properties": [],
            "excluded_relations": []
        }