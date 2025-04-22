"""
Vector Database Provider Factory for Lumina AI.

This module provides a factory for creating vector database providers,
allowing for easy switching between different vector database backends.
"""

import logging
from typing import Dict, Any, Optional

from .providers.base import VectorDatabaseProvider
from .providers.inmemory import InMemoryVectorProvider
from .providers.pinecone import PineconeVectorProvider
from .providers.weaviate import WeaviateVectorProvider

class VectorProviderFactory:
    """Factory for creating vector database providers."""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> VectorDatabaseProvider:
        """
        Create a vector database provider of the specified type.
        
        Args:
            provider_type: Type of provider to create ('inmemory', 'pinecone', 'weaviate')
            **kwargs: Provider-specific initialization parameters
            
        Returns:
            An initialized vector database provider
            
        Raises:
            ValueError: If the provider type is not supported
        """
        logger = logging.getLogger(__name__)
        
        if provider_type.lower() == 'inmemory':
            persist_dir = kwargs.get('persist_dir', './data/vector_store')
            return InMemoryVectorProvider(persist_dir=persist_dir)
        
        elif provider_type.lower() == 'pinecone':
            api_key = kwargs.get('api_key')
            environment = kwargs.get('environment')
            return PineconeVectorProvider(api_key=api_key, environment=environment)
        
        elif provider_type.lower() == 'weaviate':
            url = kwargs.get('url')
            api_key = kwargs.get('api_key')
            return WeaviateVectorProvider(url=url, api_key=api_key)
        
        else:
            logger.error(f"Unsupported vector provider type: {provider_type}")
            raise ValueError(f"Unsupported vector provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> Dict[str, str]:
        """
        Get a dictionary of available provider types and their descriptions.
        
        Returns:
            Dictionary mapping provider types to descriptions
        """
        return {
            'inmemory': 'In-memory vector database for development and testing',
            'pinecone': 'Pinecone vector database for production deployments',
            'weaviate': 'Weaviate vector database with semantic capabilities'
        }
