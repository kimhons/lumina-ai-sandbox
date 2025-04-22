"""
Model Registry for Lumina AI Enhanced Learning System

This module provides a comprehensive model registry for managing the lifecycle
of machine learning models in the Enhanced Learning System.
"""

import os
import json
import datetime
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class ModelMetadata:
    """Metadata for a machine learning model."""
    model_id: str
    name: str
    version: str
    description: str
    model_type: str
    algorithm: str
    created_at: str
    updated_at: str
    created_by: str
    tags: List[str]
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str]
    status: str  # "active", "archived", "deprecated"


class ModelRegistry:
    """
    Model Registry for managing machine learning models.
    
    The ModelRegistry handles:
    - Model registration and versioning
    - Model metadata management
    - Model discovery and selection
    - Model lifecycle management
    """
    
    def __init__(self, storage_path: str):
        """
        Initialize the ModelRegistry.
        
        Args:
            storage_path: Path to store model metadata and models
        """
        self.storage_path = storage_path
        self.metadata_path = os.path.join(storage_path, "metadata")
        self.models_path = os.path.join(storage_path, "models")
        
        # Create directories if they don't exist
        os.makedirs(self.metadata_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        # Cache for model metadata
        self._metadata_cache = {}
        self._load_metadata_cache()
    
    def _load_metadata_cache(self):
        """Load all model metadata into cache."""
        if not os.path.exists(self.metadata_path):
            return
            
        for filename in os.listdir(self.metadata_path):
            if filename.endswith(".json"):
                model_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(self.metadata_path, filename), 'r') as f:
                        metadata = json.load(f)
                        self._metadata_cache[model_id] = metadata
                except Exception as e:
                    print(f"Error loading metadata for model {model_id}: {e}")
    
    def register_model(self, 
                      name: str,
                      version: str,
                      description: str,
                      model_type: str,
                      algorithm: str,
                      created_by: str,
                      tags: List[str],
                      parameters: Dict[str, Any],
                      metrics: Dict[str, float],
                      input_schema: Dict[str, Any],
                      output_schema: Dict[str, Any],
                      dependencies: List[str] = None,
                      model_id: str = None) -> str:
        """
        Register a new model in the registry.
        
        Args:
            name: Name of the model
            version: Version of the model
            description: Description of the model
            model_type: Type of the model (e.g., "classifier", "regressor")
            algorithm: Algorithm used by the model
            created_by: User or system that created the model
            tags: List of tags for the model
            parameters: Model parameters
            metrics: Model performance metrics
            input_schema: Schema of the model inputs
            output_schema: Schema of the model outputs
            dependencies: List of dependencies for the model
            model_id: Optional model ID (generated if not provided)
            
        Returns:
            model_id: ID of the registered model
        """
        # Generate model ID if not provided
        if model_id is None:
            model_id = str(uuid.uuid4())
            
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create model metadata
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            description=description,
            model_type=model_type,
            algorithm=algorithm,
            created_at=timestamp,
            updated_at=timestamp,
            created_by=created_by,
            tags=tags,
            parameters=parameters,
            metrics=metrics,
            input_schema=input_schema,
            output_schema=output_schema,
            dependencies=dependencies or [],
            status="active"
        )
        
        # Save metadata
        self._save_metadata(metadata)
        
        return model_id
    
    def _save_metadata(self, metadata: ModelMetadata):
        """Save model metadata to file and update cache."""
        metadata_dict = asdict(metadata)
        model_id = metadata.model_id
        
        # Update cache
        self._metadata_cache[model_id] = metadata_dict
        
        # Save to file
        metadata_file = os.path.join(self.metadata_path, f"{model_id}.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            metadata: Model metadata or None if not found
        """
        return self._metadata_cache.get(model_id)
    
    def update_model_metadata(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update metadata for a specific model.
        
        Args:
            model_id: ID of the model
            updates: Dictionary of metadata fields to update
            
        Returns:
            success: True if update was successful, False otherwise
        """
        if model_id not in self._metadata_cache:
            return False
            
        metadata = self._metadata_cache[model_id].copy()
        
        # Update fields
        for key, value in updates.items():
            if key in metadata and key != "model_id":
                metadata[key] = value
                
        # Update timestamp
        metadata["updated_at"] = datetime.datetime.now().isoformat()
        
        # Convert back to ModelMetadata and save
        model_metadata = ModelMetadata(**metadata)
        self._save_metadata(model_metadata)
        
        return True
    
    def list_models(self, 
                   filters: Dict[str, Any] = None, 
                   sort_by: str = "updated_at", 
                   ascending: bool = False) -> List[Dict[str, Any]]:
        """
        List models in the registry with optional filtering and sorting.
        
        Args:
            filters: Dictionary of metadata fields to filter by
            sort_by: Metadata field to sort by
            ascending: Sort in ascending order if True, descending if False
            
        Returns:
            models: List of model metadata dictionaries
        """
        models = list(self._metadata_cache.values())
        
        # Apply filters
        if filters:
            filtered_models = []
            for model in models:
                match = True
                for key, value in filters.items():
                    if key in model:
                        if isinstance(value, list):
                            # For list values (like tags), check if any value matches
                            if isinstance(model[key], list):
                                if not any(v in model[key] for v in value):
                                    match = False
                                    break
                        else:
                            # For scalar values, check exact match
                            if model[key] != value:
                                match = False
                                break
                if match:
                    filtered_models.append(model)
            models = filtered_models
        
        # Sort models
        if sort_by in models[0] if models else {}:
            models.sort(key=lambda x: x.get(sort_by, ""), reverse=not ascending)
        
        return models
    
    def find_best_model(self, 
                       model_type: str, 
                       metric: str, 
                       tags: List[str] = None,
                       min_metric_value: float = None,
                       status: str = "active") -> Optional[Dict[str, Any]]:
        """
        Find the best model of a specific type based on a metric.
        
        Args:
            model_type: Type of model to find
            metric: Metric to optimize
            tags: Optional list of tags to filter by
            min_metric_value: Minimum acceptable value for the metric
            status: Model status to filter by (default: "active")
            
        Returns:
            model: Metadata of the best model or None if no suitable model found
        """
        filters = {"model_type": model_type, "status": status}
        if tags:
            filters["tags"] = tags
            
        models = self.list_models(filters=filters)
        
        if not models:
            return None
            
        # Filter by minimum metric value if specified
        if min_metric_value is not None:
            models = [m for m in models if m.get("metrics", {}).get(metric, 0) >= min_metric_value]
            
        if not models:
            return None
            
        # Find model with best metric
        best_model = max(models, key=lambda m: m.get("metrics", {}).get(metric, 0))
        
        return best_model
    
    def archive_model(self, model_id: str) -> bool:
        """
        Archive a model (mark as inactive but keep in registry).
        
        Args:
            model_id: ID of the model to archive
            
        Returns:
            success: True if archiving was successful, False otherwise
        """
        return self.update_model_metadata(model_id, {"status": "archived"})
    
    def deprecate_model(self, model_id: str) -> bool:
        """
        Deprecate a model (mark as deprecated but keep in registry).
        
        Args:
            model_id: ID of the model to deprecate
            
        Returns:
            success: True if deprecation was successful, False otherwise
        """
        return self.update_model_metadata(model_id, {"status": "deprecated"})
    
    def activate_model(self, model_id: str) -> bool:
        """
        Activate a previously archived or deprecated model.
        
        Args:
            model_id: ID of the model to activate
            
        Returns:
            success: True if activation was successful, False otherwise
        """
        return self.update_model_metadata(model_id, {"status": "active"})
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model from the registry.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            success: True if deletion was successful, False otherwise
        """
        if model_id not in self._metadata_cache:
            return False
            
        # Remove from cache
        del self._metadata_cache[model_id]
        
        # Remove metadata file
        metadata_file = os.path.join(self.metadata_path, f"{model_id}.json")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
            
        # Remove model file if it exists
        model_file = os.path.join(self.models_path, f"{model_id}.pkl")
        if os.path.exists(model_file):
            os.remove(model_file)
            
        return True
    
    def get_model_path(self, model_id: str) -> Optional[str]:
        """
        Get the file path for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            path: Path to the model file or None if model not found
        """
        if model_id not in self._metadata_cache:
            return None
            
        return os.path.join(self.models_path, f"{model_id}.pkl")
