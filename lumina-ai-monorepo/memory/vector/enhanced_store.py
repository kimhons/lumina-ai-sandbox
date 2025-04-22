"""
Enhanced Vector Store for Lumina AI.

This module provides an enhanced vector storage system with pluggable
vector database providers and advanced features.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from .provider_factory import VectorProviderFactory
from .providers.base import VectorDatabaseProvider

class EnhancedVectorStore:
    """Enhanced vector-based memory storage with pluggable providers."""
    
    def __init__(self, 
                 provider_type: str = "inmemory", 
                 dimension: int = 1536,
                 **provider_kwargs):
        """
        Initialize the enhanced vector store.
        
        Args:
            provider_type: Type of vector database provider to use
            dimension: Dimension of the embedding vectors
            **provider_kwargs: Provider-specific initialization parameters
        """
        self.dimension = dimension
        self.logger = logging.getLogger(__name__)
        
        # Create provider
        self.provider = VectorProviderFactory.create_provider(provider_type, **provider_kwargs)
        
        # Initialize provider
        provider_init_kwargs = provider_kwargs.copy()
        provider_init_kwargs.pop('api_key', None)  # Already passed to provider constructor
        provider_init_kwargs.pop('url', None)  # Already passed to provider constructor
        provider_init_kwargs.pop('environment', None)  # Already passed to provider constructor
        provider_init_kwargs.pop('persist_dir', None)  # Already passed to provider constructor
        
        success = self.provider.initialize(dimension, **provider_init_kwargs)
        if not success:
            self.logger.error(f"Failed to initialize vector provider: {provider_type}")
            raise RuntimeError(f"Failed to initialize vector provider: {provider_type}")
    
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
        return self.provider.add_vector(embedding, metadata, id)
    
    def add_batch(self,
                 embeddings: List[List[float]],
                 metadatas: List[Dict[str, Any]],
                 ids: Optional[List[str]] = None) -> List[str]:
        """
        Add multiple vectors to the store.
        
        Args:
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries for each vector
            ids: Optional list of IDs for the vectors
            
        Returns:
            List of IDs for the added vectors
        """
        return self.provider.add_vectors(embeddings, metadatas, ids)
    
    def search(self, 
               query_embedding: List[float], 
               top_k: int = 5,
               filter: Optional[Dict[str, Any]] = None) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: The query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (id, metadata, similarity_score)
        """
        return self.provider.search(query_embedding, top_k, filter)
    
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        Delete vectors from the store.
        
        Args:
            ids: ID or list of IDs to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        return self.provider.delete(ids)
    
    def clear(self) -> bool:
        """
        Clear all vectors from the store.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        return self.provider.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary of statistics
        """
        return self.provider.get_stats()
    
    @staticmethod
    def list_providers() -> Dict[str, str]:
        """
        List available vector database providers.
        
        Returns:
            Dictionary mapping provider types to descriptions
        """
        return VectorProviderFactory.get_available_providers()
