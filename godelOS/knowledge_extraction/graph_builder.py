"""
Knowledge Graph Builder for GodelOS.
"""

import logging
from typing import List, Dict, Any

from godelOS.unified_agent_core.knowledge_store.interfaces import (
    Fact,
    Relationship,
    UnifiedKnowledgeStoreInterface,
    Knowledge
)

logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """
    Builds a knowledge graph from extracted entities and relationships.
    """

    def __init__(self, knowledge_store: UnifiedKnowledgeStoreInterface):
        """
        Initialize the knowledge graph builder.

        Args:
            knowledge_store: The unified knowledge store to use for storing the graph.
        """
        self.knowledge_store = knowledge_store

    async def build_graph(self, processed_data: Dict[str, List[Any]]) -> List[Knowledge]:
        """
        Build the knowledge graph from processed data.

        Args:
            processed_data: A dictionary containing extracted entities and relationships.

        Returns:
            A list of all knowledge items that were created.
        """
        entities = processed_data.get("entities", [])
        relationships = processed_data.get("relationships", [])
        
        created_items = []

        # Create Fact objects for each entity
        entity_id_map = {}
        for entity_data in entities:
            fact = Fact(content=entity_data)
            await self.knowledge_store.store_knowledge(fact)
            entity_id_map[entity_data['text']] = fact.id
            created_items.append(fact)
            logger.info(f"Created Fact for entity: {entity_data['text']}")

        # Create Relationship objects
        for rel_data in relationships:
            source_text = rel_data['source']['text']
            target_text = rel_data['target']['text']

            if source_text in entity_id_map and target_text in entity_id_map:
                relationship = Relationship(
                    source_id=entity_id_map[source_text],
                    target_id=entity_id_map[target_text],
                    relation_type=rel_data['relation'],
                    content={"sentence": rel_data['sentence']}
                )
                await self.knowledge_store.store_knowledge(relationship)
                created_items.append(relationship)
                logger.info(f"Created Relationship: {source_text} -> {rel_data['relation']} -> {target_text}")

        return created_items