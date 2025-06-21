"""
Vector Store for GodelOS Semantic Search.
"""

import logging
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Manages vector embeddings for semantic search using FAISS.
    """

    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2', dimension: int = 384):
        """
        Initialize the vector store.

        Args:
            embedding_model: The name of the SentenceTransformer model to use.
            dimension: The dimension of the embeddings.
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.id_map = []
        logger.info("VectorStore initialized.")

    def add_items(self, items: List[Tuple[str, str]]):
        """
        Add items to the vector store.

        Args:
            items: A list of tuples, where each tuple contains an ID and the text to embed.
        """
        if not items:
            return

        ids, texts = zip(*items)
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
        
        if embeddings.shape[0] > 0:
            self.index.add(embeddings.astype('float32'))
            self.id_map.extend(ids)
            logger.info(f"Added {len(items)} items to the vector store.")

    def search(self, query_text: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar items in the vector store.

        Args:
            query_text: The text to search for.
            k: The number of similar items to return.

        Returns:
            A list of tuples, where each tuple contains the ID of a similar item and its distance.
        """
        if self.index.ntotal == 0:
            return []

        query_embedding = self.embedding_model.encode([query_text], convert_to_tensor=False)
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.id_map):
                results.append((self.id_map[idx], distances[0][i]))
        
        logger.info(f"Found {len(results)} results for query: '{query_text[:50]}...'")
        return results