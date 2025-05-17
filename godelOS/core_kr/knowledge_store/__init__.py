"""
Knowledge Store Interface.

This module provides a unified API for storing, retrieving, updating, and deleting
knowledge from the underlying knowledge base backend(s).
"""

from godelOS.core_kr.knowledge_store.interface import (
    KnowledgeStoreInterface,
    KnowledgeStoreBackend,
    InMemoryKnowledgeStore,
    DynamicContextModel,
    CachingMemoizationLayer
)

__all__ = [
    "KnowledgeStoreInterface",
    "KnowledgeStoreBackend",
    "InMemoryKnowledgeStore",
    "DynamicContextModel",
    "CachingMemoizationLayer"
]