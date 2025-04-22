from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)


class IntegrationSystem(ABC):
    """Abstract base class for integration systems."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the external system.
        
        Returns:
            True if connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the external system.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connected to the external system.
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute(self, operation: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an operation on the external system.
        
        Args:
            operation: Name of the operation to execute
            params: Parameters for the operation
            
        Returns:
            Result of the operation
        """
        pass


class AuthenticationProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    async def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the external system.
        
        Returns:
            Authentication result
        """
        pass
    
    @abstractmethod
    async def refresh(self) -> Dict[str, Any]:
        """
        Refresh authentication credentials.
        
        Returns:
            Refresh result
        """
        pass
    
    @abstractmethod
    async def revoke(self) -> bool:
        """
        Revoke authentication credentials.
        
        Returns:
            True if revocation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_credentials(self) -> Dict[str, Any]:
        """
        Get current authentication credentials.
        
        Returns:
            Current credentials
        """
        pass


class DataTransformer(ABC):
    """Abstract base class for data transformers."""
    
    @abstractmethod
    async def transform_to_external(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform data from internal format to external format.
        
        Args:
            data: Data in internal format
            
        Returns:
            Data in external format
        """
        pass
    
    @abstractmethod
    async def transform_to_internal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform data from external format to internal format.
        
        Args:
            data: Data in external format
            
        Returns:
            Data in internal format
        """
        pass


class IntegrationEvent:
    """Represents an event related to integration."""
    
    def __init__(
        self,
        event_id: str = None,
        event_type: str = None,
        timestamp: str = None,
        system_id: str = None,
        operation: str = None,
        status: str = None,
        data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new integration event.
        
        Args:
            event_id: Unique identifier for the event
            event_type: Type of the event
            timestamp: Timestamp of the event
            system_id: ID of the integration system
            operation: Operation that triggered the event
            status: Status of the operation
            data: Event data
            metadata: Additional metadata
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.timestamp = timestamp or datetime.datetime.now().isoformat()
        self.system_id = system_id
        self.operation = operation
        self.status = status
        self.data = data or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the integration event to a dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "system_id": self.system_id,
            "operation": self.operation,
            "status": self.status,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationEvent':
        """Create an integration event from a dictionary representation."""
        return cls(
            event_id=data.get("event_id"),
            event_type=data.get("event_type"),
            timestamp=data.get("timestamp"),
            system_id=data.get("system_id"),
            operation=data.get("operation"),
            status=data.get("status"),
            data=data.get("data", {}),
            metadata=data.get("metadata", {})
        )


class IntegrationConfig:
    """Configuration for an integration system."""
    
    def __init__(
        self,
        system_id: str,
        system_type: str,
        name: str,
        description: str = None,
        connection_params: Dict[str, Any] = None,
        auth_params: Dict[str, Any] = None,
        transform_params: Dict[str, Any] = None,
        enabled: bool = True,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new integration configuration.
        
        Args:
            system_id: Unique identifier for the system
            system_type: Type of the system
            name: Name of the system
            description: Description of the system
            connection_params: Parameters for connecting to the system
            auth_params: Parameters for authenticating with the system
            transform_params: Parameters for transforming data
            enabled: Whether the integration is enabled
            metadata: Additional metadata
        """
        self.system_id = system_id
        self.system_type = system_type
        self.name = name
        self.description = description
        self.connection_params = connection_params or {}
        self.auth_params = auth_params or {}
        self.transform_params = transform_params or {}
        self.enabled = enabled
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the integration configuration to a dictionary representation."""
        return {
            "system_id": self.system_id,
            "system_type": self.system_type,
            "name": self.name,
            "description": self.description,
            "connection_params": self.connection_params,
            "auth_params": self.auth_params,
            "transform_params": self.transform_params,
            "enabled": self.enabled,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationConfig':
        """Create an integration configuration from a dictionary representation."""
        return cls(
            system_id=data.get("system_id"),
            system_type=data.get("system_type"),
            name=data.get("name"),
            description=data.get("description"),
            connection_params=data.get("connection_params", {}),
            auth_params=data.get("auth_params", {}),
            transform_params=data.get("transform_params", {}),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {})
        )


class IntegrationRegistry(ABC):
    """Abstract base class for integration registries."""
    
    @abstractmethod
    async def register_system(self, config: IntegrationConfig) -> bool:
        """
        Register an integration system.
        
        Args:
            config: Configuration for the system
            
        Returns:
            True if registration was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def unregister_system(self, system_id: str) -> bool:
        """
        Unregister an integration system.
        
        Args:
            system_id: ID of the system to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_system(self, system_id: str) -> Optional[IntegrationConfig]:
        """
        Get an integration system by ID.
        
        Args:
            system_id: ID of the system to get
            
        Returns:
            The system configuration if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_systems(self, filter_params: Dict[str, Any] = None) -> List[IntegrationConfig]:
        """
        List integration systems.
        
        Args:
            filter_params: Parameters for filtering the list
            
        Returns:
            List of system configurations
        """
        pass
    
    @abstractmethod
    async def update_system(self, system_id: str, config: IntegrationConfig) -> bool:
        """
        Update an integration system.
        
        Args:
            system_id: ID of the system to update
            config: New configuration for the system
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
