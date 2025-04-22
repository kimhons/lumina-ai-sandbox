"""
Vector Memory Store for Lumina AI.

This module provides vector storage capabilities for long-term memory,
allowing for semantic search and retrieval of information.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

# In a production environment, we would use a proper vector database
# like Pinecone, Weaviate, or Milvus. For this implementation, we'll
# create a simple in-memory vector store with persistence to disk.

class VectorMemoryStore:
    """Vector-based memory storage for semantic search and retrieval."""
    
    def __init__(self, dimension: int = 1536, persist_dir: str = "./data/vector_store"):
        """
        Initialize the vector memory store.
        
        Args:
            dimension: Dimension of the embedding vectors
            persist_dir: Directory to persist vector data
        """
        self.dimension = dimension
        self.persist_dir = persist_dir
        self.vectors = []  # List of embedding vectors
        self.metadata = []  # List of metadata for each vector
        self.ids = []  # List of IDs for each vector
        
        # Create persistence directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Load existing data if available
        self._load()
        
        self.logger = logging.getLogger(__name__)
    
    def add(self, 
            embedding: List[float], 
            metadata: Dict[str, Any], 
            id: Optional[str] = None) -> str:
        """
        Add a vector to the store.
        
        Args:
            embedding: The embedding vector
            metadata: Metadata associated with the vector
            id: Optional ID for the vector
            
        Returns:
            The ID of the added vector
        """
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}")
        
        # Generate ID if not provided
        if id is None:
            id = f"vec_{len(self.vectors)}"
        
        # Add to store
        self.vectors.append(embedding)
        self.metadata.append(metadata)
        self.ids.append(id)
        
        # Persist to disk
        self._save()
        
        return id
    
    def search(self, 
               query_embedding: List[float], 
               top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: The query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of tuples (id, metadata, similarity_score)
        """
        if not self.vectors:
            return []
        
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query embedding dimension mismatch: expected {self.dimension}, got {len(query_embedding)}")
        
        # Convert to numpy for efficient computation
        query_np = np.array(query_embedding)
        vectors_np = np.array(self.vectors)
        
        # Compute cosine similarity
        norm_query = np.linalg.norm(query_np)
        norm_vectors = np.linalg.norm(vectors_np, axis=1)
        
        # Avoid division by zero
        if norm_query == 0 or np.any(norm_vectors == 0):
            self.logger.warning("Zero norm detected in vector similarity calculation")
            similarities = np.zeros(len(self.vectors))
        else:
            dot_products = np.dot(vectors_np, query_np)
            similarities = dot_products / (norm_vectors * norm_query)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return results
        results = []
        for idx in top_indices:
            results.append((self.ids[idx], self.metadata[idx], float(similarities[idx])))
        
        return results
    
    def delete(self, id: str) -> bool:
        """
        Delete a vector from the store.
        
        Args:
            id: ID of the vector to delete
            
        Returns:
            True if deleted, False if not found
        """
        if id in self.ids:
            idx = self.ids.index(id)
            self.vectors.pop(idx)
            self.metadata.pop(idx)
            self.ids.pop(idx)
            self._save()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all vectors from the store."""
        self.vectors = []
        self.metadata = []
        self.ids = []
        self._save()
    
    def _save(self) -> None:
        """Save the vector store to disk."""
        data = {
            "dimension": self.dimension,
            "vectors": self.vectors,
            "metadata": self.metadata,
            "ids": self.ids
        }
        with open(os.path.join(self.persist_dir, "vector_store.json"), "w") as f:
            json.dump(data, f)
    
    def _load(self) -> None:
        """Load the vector store from disk."""
        try:
            file_path = os.path.join(self.persist_dir, "vector_store.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                if data["dimension"] != self.dimension:
                    self.logger.warning(
                        f"Dimension mismatch in loaded data: expected {self.dimension}, got {data['dimension']}"
                    )
                    return
                
                self.vectors = data["vectors"]
                self.metadata = data["metadata"]
                self.ids = data["ids"]
        except Exception as e:
            self.logger.error(f"Error loading vector store: {e}")
