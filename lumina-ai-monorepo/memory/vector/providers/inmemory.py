"""
In-Memory Vector Database Provider for Lumina AI.

This module implements a simple in-memory vector database provider
for development and testing purposes.
"""

import os
import json
import numpy as np
import uuid
from typing import List, Dict, Any, Optional, Tuple, Union
import logging

from .base import VectorDatabaseProvider

class InMemoryVectorProvider(VectorDatabaseProvider):
    """In-memory vector database provider for development and testing."""
    
    def __init__(self, persist_dir: str = "./data/vector_store"):
        """
        Initialize the in-memory vector provider.
        
        Args:
            persist_dir: Directory to persist vector data
        """
        self.persist_dir = persist_dir
        self.dimension = None
        self.vectors = []
        self.metadata = []
        self.ids = []
        self.logger = logging.getLogger(__name__)
        
        # Create persistence directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
    
    def initialize(self, dimension: int, **kwargs) -> bool:
        """
        Initialize the vector database.
        
        Args:
            dimension: Dimension of the embedding vectors
            **kwargs: Provider-specific initialization parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.dimension = dimension
        
        # Load existing data if available
        try:
            file_path = os.path.join(self.persist_dir, "vector_store.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                if data["dimension"] != self.dimension:
                    self.logger.warning(
                        f"Dimension mismatch in loaded data: expected {self.dimension}, got {data['dimension']}"
                    )
                    return False
                
                self.vectors = data["vectors"]
                self.metadata = data["metadata"]
                self.ids = data["ids"]
                self.logger.info(f"Loaded {len(self.vectors)} vectors from disk")
        except Exception as e:
            self.logger.error(f"Error loading vector store: {e}")
            return False
            
        return True
    
    def add_vectors(self, 
                   vectors: List[List[float]], 
                   metadatas: List[Dict[str, Any]], 
                   ids: Optional[List[str]] = None) -> List[str]:
        """
        Add multiple vectors to the database.
        
        Args:
            vectors: List of embedding vectors
            metadatas: List of metadata dictionaries for each vector
            ids: Optional list of IDs for the vectors
            
        Returns:
            List of IDs for the added vectors
        """
        if len(vectors) != len(metadatas):
            raise ValueError("Number of vectors and metadata entries must match")
        
        if ids is not None and len(ids) != len(vectors):
            raise ValueError("Number of IDs must match number of vectors")
        
        result_ids = []
        
        for i, vector in enumerate(vectors):
            if len(vector) != self.dimension:
                raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
            
            # Generate ID if not provided
            vector_id = ids[i] if ids is not None else f"vec_{uuid.uuid4()}"
            
            # Add to store
            self.vectors.append(vector)
            self.metadata.append(metadatas[i])
            self.ids.append(vector_id)
            result_ids.append(vector_id)
        
        # Persist to disk
        self._save()
        
        return result_ids
    
    def add_vector(self, 
                  vector: List[float], 
                  metadata: Dict[str, Any], 
                  id: Optional[str] = None) -> str:
        """
        Add a single vector to the database.
        
        Args:
            vector: The embedding vector
            metadata: Metadata associated with the vector
            id: Optional ID for the vector
            
        Returns:
            The ID of the added vector
        """
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
        
        # Generate ID if not provided
        vector_id = id if id is not None else f"vec_{uuid.uuid4()}"
        
        # Add to store
        self.vectors.append(vector)
        self.metadata.append(metadata)
        self.ids.append(vector_id)
        
        # Persist to disk
        self._save()
        
        return vector_id
    
    def search(self, 
              query_vector: List[float], 
              top_k: int = 5, 
              filter: Optional[Dict[str, Any]] = None) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (id, metadata, similarity_score)
        """
        if not self.vectors:
            return []
        
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}")
        
        # Convert to numpy for efficient computation
        query_np = np.array(query_vector)
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
        
        # Apply filter if provided
        filtered_indices = list(range(len(self.vectors)))
        if filter:
            filtered_indices = [
                i for i in filtered_indices
                if all(
                    k in self.metadata[i] and self.metadata[i][k] == v
                    for k, v in filter.items()
                )
            ]
        
        # Get top-k indices from filtered set
        filtered_similarities = [(i, similarities[i]) for i in filtered_indices]
        top_filtered = sorted(filtered_similarities, key=lambda x: x[1], reverse=True)[:top_k]
        
        # Return results
        results = []
        for idx, score in top_filtered:
            results.append((self.ids[idx], self.metadata[idx], float(score)))
        
        return results
    
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            ids: ID or list of IDs to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if isinstance(ids, str):
            ids = [ids]
        
        deleted = False
        for id_to_delete in ids:
            if id_to_delete in self.ids:
                idx = self.ids.index(id_to_delete)
                self.vectors.pop(idx)
                self.metadata.pop(idx)
                self.ids.pop(idx)
                deleted = True
        
        if deleted:
            self._save()
        
        return deleted
    
    def clear(self) -> bool:
        """
        Clear all vectors from the database.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        self.vectors = []
        self.metadata = []
        self.ids = []
        self._save()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "provider": "InMemoryVectorProvider",
            "vector_count": len(self.vectors),
            "dimension": self.dimension,
            "persist_dir": self.persist_dir
        }
    
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
