"""
Vector Database Provider Interface for Lumina AI.

This module defines the interface for vector database providers,
allowing for pluggable vector database backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

class VectorDatabaseProvider(ABC):
    """Abstract base class for vector database providers."""
    
    @abstractmethod
    def initialize(self, dimension: int, **kwargs) -> bool:
        """
        Initialize the vector database.
        
        Args:
            dimension: Dimension of the embedding vectors
            **kwargs: Provider-specific initialization parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            ids: ID or list of IDs to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all vectors from the database.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary of statistics
        """
        pass
