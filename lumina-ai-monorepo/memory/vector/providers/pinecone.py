"""
Pinecone Vector Database Provider for Lumina AI.

This module implements a Pinecone vector database provider
for production-grade vector search capabilities.
"""

import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from .base import VectorDatabaseProvider

try:
    import pinecone
except ImportError:
    raise ImportError("Pinecone package not installed. Install with 'pip install pinecone-client'")

class PineconeVectorProvider(VectorDatabaseProvider):
    """Pinecone vector database provider for production deployments."""
    
    def __init__(self, api_key: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize the Pinecone vector provider.
        
        Args:
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var)
            environment: Pinecone environment (defaults to PINECONE_ENVIRONMENT env var)
        """
        self.api_key = api_key or os.environ.get("PINECONE_API_KEY")
        self.environment = environment or os.environ.get("PINECONE_ENVIRONMENT")
        self.index_name = None
        self.dimension = None
        self.index = None
        self.namespace = "default"
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            self.logger.warning("Pinecone API key not provided. Set PINECONE_API_KEY environment variable.")
    
    def initialize(self, dimension: int, **kwargs) -> bool:
        """
        Initialize the vector database.
        
        Args:
            dimension: Dimension of the embedding vectors
            **kwargs: Provider-specific initialization parameters
                - index_name: Name of the Pinecone index (required)
                - namespace: Namespace within the index (optional, default: "default")
                - metric: Distance metric to use (optional, default: "cosine")
                - pod_type: Pinecone pod type (optional)
                - replicas: Number of replicas (optional, default: 1)
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.api_key or not self.environment:
            self.logger.error("Pinecone API key and environment must be provided")
            return False
        
        self.dimension = dimension
        self.index_name = kwargs.get("index_name")
        self.namespace = kwargs.get("namespace", "default")
        
        if not self.index_name:
            self.logger.error("index_name is required for Pinecone initialization")
            return False
        
        try:
            # Initialize Pinecone
            pinecone.init(api_key=self.api_key, environment=self.environment)
            
            # Check if index exists
            if self.index_name not in pinecone.list_indexes():
                # Create index if it doesn't exist
                metric = kwargs.get("metric", "cosine")
                pod_type = kwargs.get("pod_type")
                replicas = kwargs.get("replicas", 1)
                
                create_args = {
                    "name": self.index_name,
                    "dimension": dimension,
                    "metric": metric,
                    "replicas": replicas
                }
                
                if pod_type:
                    create_args["pod_type"] = pod_type
                
                pinecone.create_index(**create_args)
                self.logger.info(f"Created Pinecone index: {self.index_name}")
            
            # Connect to the index
            self.index = pinecone.Index(self.index_name)
            self.logger.info(f"Connected to Pinecone index: {self.index_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error initializing Pinecone: {e}")
            return False
    
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
        if not self.index:
            raise ValueError("Pinecone index not initialized")
        
        if len(vectors) != len(metadatas):
            raise ValueError("Number of vectors and metadata entries must match")
        
        if ids is not None and len(ids) != len(vectors):
            raise ValueError("Number of IDs must match number of vectors")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"vec_{uuid.uuid4()}" for _ in range(len(vectors))]
        
        # Prepare vectors for upsert
        items = []
        for i, vector in enumerate(vectors):
            if len(vector) != self.dimension:
                raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
            
            items.append({
                "id": ids[i],
                "values": vector,
                "metadata": metadatas[i]
            })
        
        # Upsert vectors in batches of 100
        batch_size = 100
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            self.index.upsert(vectors=batch, namespace=self.namespace)
        
        return ids
    
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
        if not self.index:
            raise ValueError("Pinecone index not initialized")
        
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
        
        # Generate ID if not provided
        vector_id = id if id is not None else f"vec_{uuid.uuid4()}"
        
        # Upsert vector
        self.index.upsert(
            vectors=[{
                "id": vector_id,
                "values": vector,
                "metadata": metadata
            }],
            namespace=self.namespace
        )
        
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
        if not self.index:
            raise ValueError("Pinecone index not initialized")
        
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}")
        
        # Perform query
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=self.namespace,
            include_metadata=True,
            filter=filter
        )
        
        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append((match.id, match.metadata, match.score))
        
        return formatted_results
    
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            ids: ID or list of IDs to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized")
        
        if isinstance(ids, str):
            ids = [ids]
        
        try:
            self.index.delete(ids=ids, namespace=self.namespace)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting vectors: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all vectors from the database.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized")
        
        try:
            self.index.delete(delete_all=True, namespace=self.namespace)
            return True
        except Exception as e:
            self.logger.error(f"Error clearing vectors: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary of statistics
        """
        if not self.index:
            raise ValueError("Pinecone index not initialized")
        
        try:
            stats = self.index.describe_index_stats()
            namespaces = stats.get("namespaces", {})
            namespace_stats = namespaces.get(self.namespace, {})
            
            return {
                "provider": "PineconeVectorProvider",
                "index_name": self.index_name,
                "namespace": self.namespace,
                "dimension": self.dimension,
                "vector_count": namespace_stats.get("vector_count", 0),
                "total_vector_count": stats.get("total_vector_count", 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {
                "provider": "PineconeVectorProvider",
                "index_name": self.index_name,
                "namespace": self.namespace,
                "dimension": self.dimension,
                "error": str(e)
            }
