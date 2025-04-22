import logging
import json
import os
from typing import Dict, List, Any, Optional, Union
import asyncio
import uuid

from .interfaces import (
    IntegrationSystem, AuthenticationProvider, DataTransformer,
    IntegrationEvent, IntegrationConfig, IntegrationRegistry
)

logger = logging.getLogger(__name__)


class InMemoryIntegrationRegistry(IntegrationRegistry):
    """In-memory implementation of an integration registry."""
    
    def __init__(self):
        """Initialize a new in-memory integration registry."""
        self.systems: Dict[str, IntegrationConfig] = {}
    
    async def register_system(self, config: IntegrationConfig) -> bool:
        """
        Register an integration system.
        
        Args:
            config: Configuration for the system
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            if not config.system_id:
                config.system_id = str(uuid.uuid4())
            
            self.systems[config.system_id] = config
            logger.info(f"Registered integration system: {config.name} ({config.system_id})")
            return True
        
        except Exception as e:
            logger.error(f"Error registering integration system: {e}")
            return False
    
    async def unregister_system(self, system_id: str) -> bool:
        """
        Unregister an integration system.
        
        Args:
            system_id: ID of the system to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if system_id in self.systems:
            del self.systems[system_id]
            logger.info(f"Unregistered integration system: {system_id}")
            return True
        
        logger.warning(f"Integration system not found: {system_id}")
        return False
    
    async def get_system(self, system_id: str) -> Optional[IntegrationConfig]:
        """
        Get an integration system by ID.
        
        Args:
            system_id: ID of the system to get
            
        Returns:
            The system configuration if found, None otherwise
        """
        return self.systems.get(system_id)
    
    async def list_systems(self, filter_params: Dict[str, Any] = None) -> List[IntegrationConfig]:
        """
        List integration systems.
        
        Args:
            filter_params: Parameters for filtering the list
            
        Returns:
            List of system configurations
        """
        result = list(self.systems.values())
        
        if filter_params:
            filtered_result = []
            
            for system in result:
                match = True
                
                for key, value in filter_params.items():
                    if key == "system_type" and system.system_type != value:
                        match = False
                        break
                    elif key == "enabled" and system.enabled != value:
                        match = False
                        break
                    elif key.startswith("metadata."):
                        metadata_key = key[9:]  # Remove "metadata." prefix
                        if metadata_key not in system.metadata or system.metadata[metadata_key] != value:
                            match = False
                            break
                
                if match:
                    filtered_result.append(system)
            
            return filtered_result
        
        return result
    
    async def update_system(self, system_id: str, config: IntegrationConfig) -> bool:
        """
        Update an integration system.
        
        Args:
            system_id: ID of the system to update
            config: New configuration for the system
            
        Returns:
            True if update was successful, False otherwise
        """
        if system_id not in self.systems:
            logger.warning(f"Integration system not found: {system_id}")
            return False
        
        try:
            # Ensure system_id remains the same
            config.system_id = system_id
            self.systems[system_id] = config
            logger.info(f"Updated integration system: {config.name} ({system_id})")
            return True
        
        except Exception as e:
            logger.error(f"Error updating integration system: {e}")
            return False


class FileIntegrationRegistry(IntegrationRegistry):
    """File-based implementation of an integration registry."""
    
    def __init__(self, file_path: str):
        """
        Initialize a new file-based integration registry.
        
        Args:
            file_path: Path to the file to store configurations in
        """
        self.file_path = file_path
        self.systems: Dict[str, IntegrationConfig] = {}
        self._load_systems()
    
    def _load_systems(self):
        """Load systems from the file."""
        if not os.path.exists(self.file_path):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            # Create an empty file
            with open(self.file_path, 'w') as f:
                f.write('{}')
            return
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                
                for system_id, system_data in data.items():
                    self.systems[system_id] = IntegrationConfig.from_dict(system_data)
        
        except Exception as e:
            logger.error(f"Error loading systems from file: {e}")
    
    def _save_systems(self):
        """Save systems to the file."""
        try:
            data = {system_id: system.to_dict() for system_id, system in self.systems.items()}
            
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving systems to file: {e}")
    
    async def register_system(self, config: IntegrationConfig) -> bool:
        """
        Register an integration system.
        
        Args:
            config: Configuration for the system
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            if not config.system_id:
                config.system_id = str(uuid.uuid4())
            
            self.systems[config.system_id] = config
            self._save_systems()
            logger.info(f"Registered integration system: {config.name} ({config.system_id})")
            return True
        
        except Exception as e:
            logger.error(f"Error registering integration system: {e}")
            return False
    
    async def unregister_system(self, system_id: str) -> bool:
        """
        Unregister an integration system.
        
        Args:
            system_id: ID of the system to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if system_id in self.systems:
            del self.systems[system_id]
            self._save_systems()
            logger.info(f"Unregistered integration system: {system_id}")
            return True
        
        logger.warning(f"Integration system not found: {system_id}")
        return False
    
    async def get_system(self, system_id: str) -> Optional[IntegrationConfig]:
        """
        Get an integration system by ID.
        
        Args:
            system_id: ID of the system to get
            
        Returns:
            The system configuration if found, None otherwise
        """
        return self.systems.get(system_id)
    
    async def list_systems(self, filter_params: Dict[str, Any] = None) -> List[IntegrationConfig]:
        """
        List integration systems.
        
        Args:
            filter_params: Parameters for filtering the list
            
        Returns:
            List of system configurations
        """
        result = list(self.systems.values())
        
        if filter_params:
            filtered_result = []
            
            for system in result:
                match = True
                
                for key, value in filter_params.items():
                    if key == "system_type" and system.system_type != value:
                        match = False
                        break
                    elif key == "enabled" and system.enabled != value:
                        match = False
                        break
                    elif key.startswith("metadata."):
                        metadata_key = key[9:]  # Remove "metadata." prefix
                        if metadata_key not in system.metadata or system.metadata[metadata_key] != value:
                            match = False
                            break
                
                if match:
                    filtered_result.append(system)
            
            return filtered_result
        
        return result
    
    async def update_system(self, system_id: str, config: IntegrationConfig) -> bool:
        """
        Update an integration system.
        
        Args:
            system_id: ID of the system to update
            config: New configuration for the system
            
        Returns:
            True if update was successful, False otherwise
        """
        if system_id not in self.systems:
            logger.warning(f"Integration system not found: {system_id}")
            return False
        
        try:
            # Ensure system_id remains the same
            config.system_id = system_id
            self.systems[system_id] = config
            self._save_systems()
            logger.info(f"Updated integration system: {config.name} ({system_id})")
            return True
        
        except Exception as e:
            logger.error(f"Error updating integration system: {e}")
            return False


class RegistryFactory:
    """Factory for creating integration registries."""
    
    @staticmethod
    def create_registry(registry_type: str, **kwargs) -> IntegrationRegistry:
        """
        Create an integration registry.
        
        Args:
            registry_type: Type of registry to create
            **kwargs: Additional arguments for the registry
            
        Returns:
            The created registry
            
        Raises:
            ValueError: If the registry type is not supported
        """
        if registry_type == "memory":
            return InMemoryIntegrationRegistry()
        elif registry_type == "file":
            file_path = kwargs.get("file_path")
            if not file_path:
                raise ValueError("file_path is required for file registry")
            return FileIntegrationRegistry(file_path)
        else:
            raise ValueError(f"Unsupported registry type: {registry_type}")
