"""
Weaviate Vector Database Provider for Lumina AI.

This module implements a Weaviate vector database provider
for production-grade vector search with semantic capabilities.
"""

import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from .base import VectorDatabaseProvider

try:
    import weaviate
    from weaviate.auth import AuthApiKey
except ImportError:
    raise ImportError("Weaviate package not installed. Install with 'pip install weaviate-client'")

class WeaviateVectorProvider(VectorDatabaseProvider):
    """Weaviate vector database provider for production deployments."""
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Weaviate vector provider.
        
        Args:
            url: Weaviate instance URL (defaults to WEAVIATE_URL env var)
            api_key: Weaviate API key (defaults to WEAVIATE_API_KEY env var)
        """
        self.url = url or os.environ.get("WEAVIATE_URL")
        self.api_key = api_key or os.environ.get("WEAVIATE_API_KEY")
        self.class_name = None
        self.dimension = None
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        if not self.url:
            self.logger.warning("Weaviate URL not provided. Set WEAVIATE_URL environment variable.")
    
    def initialize(self, dimension: int, **kwargs) -> bool:
        """
        Initialize the vector database.
        
        Args:
            dimension: Dimension of the embedding vectors
            **kwargs: Provider-specific initialization parameters
                - class_name: Name of the Weaviate class (required)
                - batch_size: Size of batches for operations (optional, default: 100)
                - distance: Distance metric to use (optional, default: "cosine")
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.url:
            self.logger.error("Weaviate URL must be provided")
            return False
        
        self.dimension = dimension
        self.class_name = kwargs.get("class_name")
        self.batch_size = kwargs.get("batch_size", 100)
        
        if not self.class_name:
            self.logger.error("class_name is required for Weaviate initialization")
            return False
        
        try:
            # Initialize Weaviate client
            auth_config = AuthApiKey(api_key=self.api_key) if self.api_key else None
            self.client = weaviate.Client(url=self.url, auth_client_secret=auth_config)
            
            # Check if class exists
            schema = self.client.schema.get()
            classes = [c["class"] for c in schema.get("classes", [])]
            
            if self.class_name not in classes:
                # Create class if it doesn't exist
                distance = kwargs.get("distance", "cosine")
                
                class_obj = {
                    "class": self.class_name,
                    "vectorizer": "none",  # We'll provide our own vectors
                    "vectorIndexConfig": {
                        "distance": distance
                    },
                    "properties": [
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "The content associated with this vector"
                        },
                        {
                            "name": "metadata",
                            "dataType": ["object"],
                            "description": "Metadata associated with this vector"
                        }
                    ]
                }
                
                self.client.schema.create_class(class_obj)
                self.logger.info(f"Created Weaviate class: {self.class_name}")
            
            self.logger.info(f"Connected to Weaviate instance: {self.url}")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing Weaviate: {e}")
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
        if not self.client:
            raise ValueError("Weaviate client not initialized")
        
        if len(vectors) != len(metadatas):
            raise ValueError("Number of vectors and metadata entries must match")
        
        if ids is not None and len(ids) != len(vectors):
            raise ValueError("Number of IDs must match number of vectors")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        # Start a batch process
        with self.client.batch as batch:
            batch.batch_size = self.batch_size
            
            for i, vector in enumerate(vectors):
                if len(vector) != self.dimension:
                    raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
                
                # Extract content from metadata if available
                content = metadatas[i].get("content", "")
                
                # Create object
                properties = {
                    "content": content,
                    "metadata": metadatas[i]
                }
                
                batch.add_data_object(
                    data_object=properties,
                    class_name=self.class_name,
                    uuid=ids[i],
                    vector=vector
                )
        
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
        if not self.client:
            raise ValueError("Weaviate client not initialized")
        
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
        
        # Generate ID if not provided
        vector_id = id if id is not None else str(uuid.uuid4())
        
        # Extract content from metadata if available
        content = metadata.get("content", "")
        
        # Create object
        properties = {
            "content": content,
            "metadata": metadata
        }
        
        self.client.data_object.create(
            data_object=properties,
            class_name=self.class_name,
            uuid=vector_id,
            vector=vector
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
        if not self.client:
            raise ValueError("Weaviate client not initialized")
        
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}")
        
        # Build query
        query = self.client.query.get(self.class_name, ["content", "metadata"])
        query = query.with_near_vector({"vector": query_vector})
        query = query.with_limit(top_k)
        
        # Add filter if provided
        if filter:
            where_filter = self._build_where_filter(filter)
            if where_filter:
                query = query.with_where(where_filter)
        
        # Execute query
        result = query.do()
        
        # Format results
        formatted_results = []
        if "data" in result and "Get" in result["data"] and self.class_name in result["data"]["Get"]:
            objects = result["data"]["Get"][self.class_name]
            for obj in objects:
                obj_id = obj.get("_additional", {}).get("id")
                metadata = obj.get("metadata", {})
                score = obj.get("_additional", {}).get("distance")
                
                # Convert distance to similarity score (1 - distance for cosine)
                if score is not None:
                    score = 1 - score
                
                formatted_results.append((obj_id, metadata, score))
        
        return formatted_results
    
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            ids: ID or list of IDs to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.client:
            raise ValueError("Weaviate client not initialized")
        
        if isinstance(ids, str):
            ids = [ids]
        
        try:
            for id_to_delete in ids:
                self.client.data_object.delete(
                    uuid=id_to_delete,
                    class_name=self.class_name
                )
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
        if not self.client:
            raise ValueError("Weaviate client not initialized")
        
        try:
            self.client.schema.delete_class(self.class_name)
            
            # Recreate the class
            class_obj = {
                "class": self.class_name,
                "vectorizer": "none",
                "vectorIndexConfig": {
                    "distance": "cosine"
                },
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "The content associated with this vector"
                    },
                    {
                        "name": "metadata",
                        "dataType": ["object"],
                        "description": "Metadata associated with this vector"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
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
        if not self.client:
            raise ValueError("Weaviate client not initialized")
        
        try:
            # Get class statistics
            result = self.client.query.aggregate(self.class_name).with_meta_count().do()
            count = result.get("data", {}).get("Aggregate", {}).get(self.class_name, [{}])[0].get("meta", {}).get("count", 0)
            
            return {
                "provider": "WeaviateVectorProvider",
                "class_name": self.class_name,
                "dimension": self.dimension,
                "vector_count": count
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {
                "provider": "WeaviateVectorProvider",
                "class_name": self.class_name,
                "dimension": self.dimension,
                "error": str(e)
            }
    
    def _build_where_filter(self, filter: Dict[str, Any]) -> Dict[str, Any]:
        """Build a Weaviate where filter from a simple filter dict."""
        where_filter = {"operator": "And", "operands": []}
        
        for key, value in filter.items():
            # Handle nested metadata fields
            if key.startswith("metadata."):
                path = key.split(".")
                operand = {
                    "path": path,
                    "operator": "Equal",
                    "valueText": value if isinstance(value, str) else None,
                    "valueNumber": value if isinstance(value, (int, float)) else None,
                    "valueBoolean": value if isinstance(value, bool) else None
                }
                where_filter["operands"].append(operand)
            else:
                operand = {
                    "path": [key],
                    "operator": "Equal",
                    "valueText": value if isinstance(value, str) else None,
                    "valueNumber": value if isinstance(value, (int, float)) else None,
                    "valueBoolean": value if isinstance(value, bool) else None
                }
                where_filter["operands"].append(operand)
        
        return where_filter if where_filter["operands"] else None
