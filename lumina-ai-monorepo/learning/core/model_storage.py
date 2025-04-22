"""
Model Storage for Lumina AI Enhanced Learning System

This module provides a comprehensive storage system for machine learning models,
supporting versioning, serialization, and efficient retrieval.
"""

import os
import json
import pickle
import datetime
import hashlib
import shutil
from typing import Dict, List, Any, Optional, Union, BinaryIO
from dataclasses import dataclass
import joblib


@dataclass
class ModelInfo:
    """Information about a stored model."""
    model_id: str
    version: str
    storage_path: str
    format: str
    size_bytes: int
    hash: str
    metadata: Dict[str, Any]
    created_at: str


class ModelStorage:
    """
    Storage system for machine learning models.
    
    The ModelStorage handles:
    - Model serialization and deserialization
    - Version control and history
    - Efficient storage and retrieval
    - Model integrity verification
    """
    
    def __init__(self, base_path: str):
        """
        Initialize the ModelStorage.
        
        Args:
            base_path: Base directory for model storage
        """
        self.base_path = base_path
        self.models_path = os.path.join(base_path, "models")
        self.metadata_path = os.path.join(base_path, "metadata")
        
        # Create directories if they don't exist
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.metadata_path, exist_ok=True)
        
        # Cache for model metadata
        self._metadata_cache = {}
        self._load_metadata_cache()
    
    def _load_metadata_cache(self):
        """Load all model metadata into cache."""
        if not os.path.exists(self.metadata_path):
            return
            
        for filename in os.listdir(self.metadata_path):
            if filename.endswith(".json"):
                model_id = filename.split("_")[0]  # Extract model ID from filename
                try:
                    with open(os.path.join(self.metadata_path, filename), 'r') as f:
                        metadata = json.load(f)
                        
                        # Group by model ID
                        if model_id not in self._metadata_cache:
                            self._metadata_cache[model_id] = []
                            
                        self._metadata_cache[model_id].append(metadata)
                except Exception as e:
                    print(f"Error loading metadata for model {model_id}: {e}")
    
    def save_model(self, 
                  model: Any, 
                  model_id: str, 
                  version: str = None, 
                  format: str = "joblib", 
                  metadata: Dict[str, Any] = None) -> ModelInfo:
        """
        Save a model to storage.
        
        Args:
            model: Model to save
            model_id: ID of the model
            version: Version of the model (if None, generate based on timestamp)
            format: Format to save the model in ("joblib", "pickle", "tf", "pytorch")
            metadata: Additional metadata for the model
            
        Returns:
            info: Information about the stored model
        """
        # Generate version if not provided
        if version is None:
            version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            
        # Create model directory
        model_dir = os.path.join(self.models_path, model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # Determine file extension based on format
        if format == "joblib":
            file_ext = ".joblib"
        elif format == "pickle":
            file_ext = ".pkl"
        elif format == "tf":
            file_ext = ".keras"
        elif format == "pytorch":
            file_ext = ".pt"
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        # Create model path
        model_path = os.path.join(model_dir, f"{version}{file_ext}")
        
        # Save model
        if format == "joblib":
            joblib.dump(model, model_path)
        elif format == "pickle":
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        elif format == "tf":
            try:
                model.save(model_path)
            except AttributeError:
                raise ValueError("Model does not support TensorFlow format")
        elif format == "pytorch":
            try:
                import torch
                torch.save(model, model_path)
            except ImportError:
                raise ImportError("PyTorch is required for pytorch format")
            except AttributeError:
                raise ValueError("Model does not support PyTorch format")
        
        # Calculate file size and hash
        size_bytes = os.path.getsize(model_path)
        file_hash = self._calculate_file_hash(model_path)
        
        # Create model info
        info = ModelInfo(
            model_id=model_id,
            version=version,
            storage_path=model_path,
            format=format,
            size_bytes=size_bytes,
            hash=file_hash,
            metadata=metadata or {},
            created_at=datetime.datetime.now().isoformat()
        )
        
        # Save metadata
        self._save_metadata(info)
        
        return info
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            hash: SHA-256 hash of the file
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read and update hash in chunks
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        return sha256_hash.hexdigest()
    
    def _save_metadata(self, info: ModelInfo):
        """
        Save model metadata to file.
        
        Args:
            info: Model information to save
        """
        # Convert ModelInfo to dict
        metadata = {
            "model_id": info.model_id,
            "version": info.version,
            "storage_path": info.storage_path,
            "format": info.format,
            "size_bytes": info.size_bytes,
            "hash": info.hash,
            "metadata": info.metadata,
            "created_at": info.created_at
        }
        
        # Save to file
        metadata_file = os.path.join(self.metadata_path, f"{info.model_id}_{info.version}.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        # Update cache
        if info.model_id not in self._metadata_cache:
            self._metadata_cache[info.model_id] = []
            
        self._metadata_cache[info.model_id].append(metadata)
    
    def load_model(self, model_id: str, version: str = None) -> Any:
        """
        Load a model from storage.
        
        Args:
            model_id: ID of the model to load
            version: Version of the model to load (if None, load latest version)
            
        Returns:
            model: The loaded model
        """
        # Get model info
        info = self.get_model_info(model_id, version)
        if info is None:
            raise ValueError(f"Model {model_id} with version {version} not found")
            
        # Load model based on format
        if info["format"] == "joblib":
            return joblib.load(info["storage_path"])
        elif info["format"] == "pickle":
            with open(info["storage_path"], 'rb') as f:
                return pickle.load(f)
        elif info["format"] == "tf":
            try:
                import tensorflow as tf
                return tf.keras.models.load_model(info["storage_path"])
            except ImportError:
                raise ImportError("TensorFlow is required for tf format")
        elif info["format"] == "pytorch":
            try:
                import torch
                return torch.load(info["storage_path"])
            except ImportError:
                raise ImportError("PyTorch is required for pytorch format")
        else:
            raise ValueError(f"Unsupported format: {info['format']}")
    
    def get_model_info(self, model_id: str, version: str = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a model.
        
        Args:
            model_id: ID of the model
            version: Version of the model (if None, get latest version)
            
        Returns:
            info: Information about the model or None if not found
        """
        if model_id not in self._metadata_cache:
            return None
            
        versions = self._metadata_cache[model_id]
        
        if version is None:
            # Get latest version
            return max(versions, key=lambda v: v["created_at"])
        else:
            # Get specific version
            for v in versions:
                if v["version"] == version:
                    return v
                    
            return None
    
    def list_models(self) -> List[str]:
        """
        List all model IDs in storage.
        
        Returns:
            model_ids: List of model IDs
        """
        return list(self._metadata_cache.keys())
    
    def list_versions(self, model_id: str) -> List[Dict[str, Any]]:
        """
        List all versions of a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            versions: List of version information
        """
        if model_id not in self._metadata_cache:
            return []
            
        return sorted(self._metadata_cache[model_id], key=lambda v: v["created_at"])
    
    def delete_model(self, model_id: str, version: str = None) -> bool:
        """
        Delete a model from storage.
        
        Args:
            model_id: ID of the model to delete
            version: Version of the model to delete (if None, delete all versions)
            
        Returns:
            success: True if deletion was successful, False otherwise
        """
        if model_id not in self._metadata_cache:
            return False
            
        if version is None:
            # Delete all versions
            model_dir = os.path.join(self.models_path, model_id)
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
                
            # Delete metadata files
            for v in self._metadata_cache[model_id]:
                metadata_file = os.path.join(self.metadata_path, f"{model_id}_{v['version']}.json")
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)
                    
            # Remove from cache
            del self._metadata_cache[model_id]
            
            return True
        else:
            # Delete specific version
            info = self.get_model_info(model_id, version)
            if info is None:
                return False
                
            # Delete model file
            if os.path.exists(info["storage_path"]):
                os.remove(info["storage_path"])
                
            # Delete metadata file
            metadata_file = os.path.join(self.metadata_path, f"{model_id}_{version}.json")
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
                
            # Update cache
            self._metadata_cache[model_id] = [
                v for v in self._metadata_cache[model_id] if v["version"] != version
            ]
            
            # If no versions left, remove model ID from cache
            if not self._metadata_cache[model_id]:
                del self._metadata_cache[model_id]
                
            return True
    
    def verify_model(self, model_id: str, version: str = None) -> bool:
        """
        Verify the integrity of a model.
        
        Args:
            model_id: ID of the model to verify
            version: Version of the model to verify (if None, verify latest version)
            
        Returns:
            valid: True if the model is valid, False otherwise
        """
        # Get model info
        info = self.get_model_info(model_id, version)
        if info is None:
            return False
            
        # Check if file exists
        if not os.path.exists(info["storage_path"]):
            return False
            
        # Calculate hash and compare
        current_hash = self._calculate_file_hash(info["storage_path"])
        return current_hash == info["hash"]
    
    def export_model(self, model_id: str, version: str = None, output_path: str = None) -> Optional[str]:
        """
        Export a model to a file.
        
        Args:
            model_id: ID of the model to export
            version: Version of the model to export (if None, export latest version)
            output_path: Path to export the model to (if None, return path to model file)
            
        Returns:
            path: Path to the exported model or None if export failed
        """
        # Get model info
        info = self.get_model_info(model_id, version)
        if info is None:
            return None
            
        # If no output path, return path to model file
        if output_path is None:
            return info["storage_path"]
            
        # Copy model file to output path
        try:
            shutil.copy2(info["storage_path"], output_path)
            return output_path
        except Exception as e:
            print(f"Error exporting model: {e}")
            return None
    
    def import_model(self, 
                    model_path: str, 
                    model_id: str, 
                    version: str = None, 
                    format: str = None, 
                    metadata: Dict[str, Any] = None) -> Optional[ModelInfo]:
        """
        Import a model from a file.
        
        Args:
            model_path: Path to the model file
            model_id: ID to assign to the model
            version: Version to assign to the model (if None, generate based on timestamp)
            format: Format of the model file (if None, infer from file extension)
            metadata: Additional metadata for the model
            
        Returns:
            info: Information about the imported model or None if import failed
        """
        # Check if file exists
        if not os.path.exists(model_path):
            return None
            
        # Infer format from file extension if not provided
        if format is None:
            if model_path.endswith(".joblib"):
                format = "joblib"
            elif model_path.endswith(".pkl"):
                format = "pickle"
            elif model_path.endswith(".keras") or model_path.endswith(".h5"):
                format = "tf"
            elif model_path.endswith(".pt") or model_path.endswith(".pth"):
                format = "pytorch"
            else:
                raise ValueError("Could not infer format from file extension")
        
        # Generate version if not provided
        if version is None:
            version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            
        # Create model directory
        model_dir = os.path.join(self.models_path, model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # Determine file extension based on format
        if format == "joblib":
            file_ext = ".joblib"
        elif format == "pickle":
            file_ext = ".pkl"
        elif format == "tf":
            file_ext = ".keras"
        elif format == "pytorch":
            file_ext = ".pt"
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        # Create model path
        storage_path = os.path.join(model_dir, f"{version}{file_ext}")
        
        # Copy model file to storage
        try:
            shutil.copy2(model_path, storage_path)
        except Exception as e:
            print(f"Error importing model: {e}")
            return None
        
        # Calculate file size and hash
        size_bytes = os.path.getsize(storage_path)
        file_hash = self._calculate_file_hash(storage_path)
        
        # Create model info
        info = ModelInfo(
            model_id=model_id,
            version=version,
            storage_path=storage_path,
            format=format,
            size_bytes=size_bytes,
            hash=file_hash,
            metadata=metadata or {},
            created_at=datetime.datetime.now().isoformat()
        )
        
        # Save metadata
        self._save_metadata(info)
        
        return info
    
    def get_model_size(self, model_id: str, version: str = None) -> Optional[int]:
        """
        Get the size of a model in bytes.
        
        Args:
            model_id: ID of the model
            version: Version of the model (if None, get latest version)
            
        Returns:
            size: Size of the model in bytes or None if not found
        """
        info = self.get_model_info(model_id, version)
        if info is None:
            return None
            
        return info["size_bytes"]
    
    def get_total_storage_size(self) -> int:
        """
        Get the total size of all models in storage.
        
        Returns:
            size: Total size in bytes
        """
        total_size = 0
        
        for model_id in self.list_models():
            for version in self.list_versions(model_id):
                total_size += version["size_bytes"]
                
        return total_size
    
    def cleanup_old_versions(self, model_id: str, keep_latest: int = 3) -> int:
        """
        Delete old versions of a model, keeping only the latest N versions.
        
        Args:
            model_id: ID of the model
            keep_latest: Number of latest versions to keep
            
        Returns:
            deleted: Number of versions deleted
        """
        if model_id not in self._metadata_cache:
            return 0
            
        versions = sorted(self._metadata_cache[model_id], key=lambda v: v["created_at"], reverse=True)
        
        if len(versions) <= keep_latest:
            return 0
            
        versions_to_delete = versions[keep_latest:]
        deleted = 0
        
        for v in versions_to_delete:
            if self.delete_model(model_id, v["version"]):
                deleted += 1
                
        return deleted


class DistributedModelStorage(ModelStorage):
    """
    Distributed storage system for machine learning models.
    
    This class extends ModelStorage to support distributed storage across multiple nodes.
    """
    
    def __init__(self, base_path: str, remote_url: str = None, sync_interval: int = 3600):
        """
        Initialize the DistributedModelStorage.
        
        Args:
            base_path: Base directory for model storage
            remote_url: URL of the remote storage server
            sync_interval: Interval in seconds for automatic synchronization
        """
        super().__init__(base_path)
        self.remote_url = remote_url
        self.sync_interval = sync_interval
        self.last_sync = None
        
        # Initialize remote connection if URL is provided
        if remote_url:
            self._init_remote_connection()
    
    def _init_remote_connection(self):
        """Initialize connection to remote storage server."""
        try:
            import requests
            # Test connection
            response = requests.get(f"{self.remote_url}/ping")
            if response.status_code == 200:
                print(f"Connected to remote storage at {self.remote_url}")
                self.last_sync = datetime.datetime.now()
            else:
                print(f"Failed to connect to remote storage at {self.remote_url}")
        except Exception as e:
            print(f"Error connecting to remote storage: {e}")
    
    def sync_with_remote(self, force: bool = False) -> bool:
        """
        Synchronize with remote storage.
        
        Args:
            force: Force synchronization even if sync interval has not elapsed
            
        Returns:
            success: True if synchronization was successful, False otherwise
        """
        if not self.remote_url:
            return False
            
        # Check if sync interval has elapsed
        if not force and self.last_sync:
            elapsed = (datetime.datetime.now() - self.last_sync).total_seconds()
            if elapsed < self.sync_interval:
                return True
        
        try:
            import requests
            
            # Get list of models from remote
            response = requests.get(f"{self.remote_url}/models")
            if response.status_code != 200:
                return False
                
            remote_models = response.json()
            
            # Synchronize models
            for model_id in remote_models:
                # Get list of versions from remote
                response = requests.get(f"{self.remote_url}/models/{model_id}/versions")
                if response.status_code != 200:
                    continue
                    
                remote_versions = response.json()
                
                # Get list of local versions
                local_versions = self.list_versions(model_id)
                local_version_ids = [v["version"] for v in local_versions]
                
                # Download missing versions
                for version in remote_versions:
                    if version["version"] not in local_version_ids:
                        # Download model
                        response = requests.get(f"{self.remote_url}/models/{model_id}/{version['version']}/download")
                        if response.status_code != 200:
                            continue
                            
                        # Save model to temporary file
                        temp_path = os.path.join(self.base_path, "temp_download")
                        with open(temp_path, 'wb') as f:
                            f.write(response.content)
                            
                        # Import model
                        self.import_model(
                            model_path=temp_path,
                            model_id=model_id,
                            version=version["version"],
                            format=version["format"],
                            metadata=version["metadata"]
                        )
                        
                        # Remove temporary file
                        os.remove(temp_path)
            
            # Upload local models to remote
            for model_id in self.list_models():
                # Get list of versions from remote
                response = requests.get(f"{self.remote_url}/models/{model_id}/versions")
                remote_versions = []
                if response.status_code == 200:
                    remote_versions = response.json()
                    
                remote_version_ids = [v["version"] for v in remote_versions]
                
                # Upload missing versions
                for version in self.list_versions(model_id):
                    if version["version"] not in remote_version_ids:
                        # Upload model
                        with open(version["storage_path"], 'rb') as f:
                            files = {'model': f}
                            data = {
                                'model_id': model_id,
                                'version': version["version"],
                                'format': version["format"],
                                'metadata': json.dumps(version["metadata"])
                            }
                            response = requests.post(f"{self.remote_url}/models/upload", files=files, data=data)
                            
                            if response.status_code != 200:
                                print(f"Failed to upload model {model_id} version {version['version']}")
            
            # Update last sync time
            self.last_sync = datetime.datetime.now()
            
            return True
        except Exception as e:
            print(f"Error synchronizing with remote storage: {e}")
            return False
    
    def save_model(self, 
                  model: Any, 
                  model_id: str, 
                  version: str = None, 
                  format: str = "joblib", 
                  metadata: Dict[str, Any] = None,
                  sync: bool = True) -> ModelInfo:
        """
        Save a model to storage and optionally sync with remote.
        
        Args:
            model: Model to save
            model_id: ID of the model
            version: Version of the model (if None, generate based on timestamp)
            format: Format to save the model in ("joblib", "pickle", "tf", "pytorch")
            metadata: Additional metadata for the model
            sync: Whether to synchronize with remote storage
            
        Returns:
            info: Information about the stored model
        """
        # Save model locally
        info = super().save_model(model, model_id, version, format, metadata)
        
        # Sync with remote if requested
        if sync and self.remote_url:
            self.sync_with_remote(force=True)
            
        return info
    
    def delete_model(self, model_id: str, version: str = None, sync: bool = True) -> bool:
        """
        Delete a model from storage and optionally sync with remote.
        
        Args:
            model_id: ID of the model to delete
            version: Version of the model to delete (if None, delete all versions)
            sync: Whether to synchronize with remote storage
            
        Returns:
            success: True if deletion was successful, False otherwise
        """
        # Delete model locally
        success = super().delete_model(model_id, version)
        
        # Sync with remote if requested
        if success and sync and self.remote_url:
            try:
                import requests
                
                if version is None:
                    # Delete all versions
                    response = requests.delete(f"{self.remote_url}/models/{model_id}")
                else:
                    # Delete specific version
                    response = requests.delete(f"{self.remote_url}/models/{model_id}/{version}")
                    
                if response.status_code != 200:
                    print(f"Failed to delete model {model_id} from remote storage")
            except Exception as e:
                print(f"Error deleting model from remote storage: {e}")
                
        return success
