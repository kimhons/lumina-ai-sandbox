"""
Enterprise Adapter Factory for Lumina AI.

This module implements the factory for creating adapters for various enterprise systems,
providing a unified way to instantiate and manage system-specific adapters.
"""

import logging
from typing import Dict, Any, Optional

from .interfaces import IntegrationSystem, IntegrationConfig

logger = logging.getLogger(__name__)


class UnsupportedSystemError(Exception):
    """Exception raised when an unsupported system type is requested."""
    pass


class EnterpriseAdapterFactory:
    """
    Factory for creating enterprise system adapters.
    
    This class is responsible for creating and managing adapters for various
    enterprise systems, ensuring that each system has an appropriate adapter
    implementation.
    """
    
    def __init__(self):
        """Initialize a new enterprise adapter factory."""
        self.adapters = {}
        self.adapter_classes = {}
        
    def register_adapter_class(self, system_type: str, adapter_class: type):
        """
        Register an adapter class for a system type.
        
        Args:
            system_type: Type of the system
            adapter_class: Class to use for creating adapters
        """
        self.adapter_classes[system_type] = adapter_class
        logger.info(f"Registered adapter class for system type: {system_type}")
        
    def create_adapter(self, system_config: IntegrationConfig) -> IntegrationSystem:
        """
        Create an adapter for the specified system.
        
        Args:
            system_config: Configuration for the system
            
        Returns:
            The created adapter
            
        Raises:
            UnsupportedSystemError: If the system type is not supported
        """
        system_id = system_config.system_id
        system_type = system_config.system_type
        
        # Return cached adapter if available
        if system_id in self.adapters:
            return self.adapters[system_id]
            
        # Check if we have a registered adapter class for this system type
        if system_type not in self.adapter_classes:
            raise UnsupportedSystemError(f"Unsupported system type: {system_type}")
            
        # Create new adapter
        adapter_class = self.adapter_classes[system_type]
        adapter = adapter_class(system_config)
        
        # Cache the adapter
        self.adapters[system_id] = adapter
        logger.info(f"Created adapter for system: {system_config.name} ({system_id})")
        
        return adapter
        
    def get_adapter(self, system_id: str) -> Optional[IntegrationSystem]:
        """
        Get an existing adapter by system ID.
        
        Args:
            system_id: ID of the system
            
        Returns:
            The adapter if found, None otherwise
        """
        return self.adapters.get(system_id)
        
    def remove_adapter(self, system_id: str) -> bool:
        """
        Remove an adapter from the cache.
        
        Args:
            system_id: ID of the system
            
        Returns:
            True if the adapter was removed, False otherwise
        """
        if system_id in self.adapters:
            del self.adapters[system_id]
            logger.info(f"Removed adapter for system: {system_id}")
            return True
            
        return False
        
    def clear_adapters(self):
        """Clear all cached adapters."""
        self.adapters = {}
        logger.info("Cleared all adapters")
