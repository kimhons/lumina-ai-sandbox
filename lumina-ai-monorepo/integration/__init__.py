"""
Enterprise Integration Module for Lumina AI.

This module initializes the Enterprise Integration components and provides
a unified interface for interacting with enterprise systems.
"""

import logging
import asyncio
import os
from typing import Dict, List, Any, Optional, Union

from .interfaces import IntegrationConfig, IntegrationRegistry
from .registry import FileIntegrationRegistry, RegistryFactory
from .auth import AuthProviderFactory
from .security import CredentialEncryptor, SecretStore, WebhookVerifier, EnterpriseSecurityManager
from .data_transformer import SchemaRegistry, CanonicalDataModel, TransformerFactory
from .adapter_factory import EnterpriseAdapterFactory
from .monitoring import MetricsClient, LogClient, AlertManager, EnterpriseMonitoringService
from .enterprise_gateway import EnterpriseIntegrationGateway
from .adapters import SalesforceAdapter, MicrosoftTeamsAdapter, SapAdapter

logger = logging.getLogger(__name__)


class EnterpriseIntegrationModule:
    """
    Main module for Enterprise Integration.
    
    This class initializes and manages all components of the Enterprise Integration
    layer, providing a unified interface for interacting with enterprise systems.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the Enterprise Integration module.
        
        Args:
            config_dir: Directory for configuration and secrets (if None, uses default)
        """
        self.config_dir = config_dir or os.path.expanduser("~/.lumina/enterprise_integration")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Initialize components
        self._init_components()
        
        logger.info("Enterprise Integration module initialized")
        
    def _init_components(self):
        """Initialize all components of the Enterprise Integration layer."""
        # Create registry
        registry_file = os.path.join(self.config_dir, "registry.json")
        self.registry = FileIntegrationRegistry(registry_file)
        
        # Create security components
        master_key_file = os.path.join(self.config_dir, "master_key.txt")
        if os.path.exists(master_key_file):
            with open(master_key_file, 'r') as f:
                master_key = f.read().strip()
        else:
            # Generate new master key
            encryptor = CredentialEncryptor()
            master_key = encryptor.master_key
            with open(master_key_file, 'w') as f:
                f.write(master_key)
            logger.info("Generated new master key")
            
        self.encryptor = CredentialEncryptor(master_key)
        secrets_file = os.path.join(self.config_dir, "secrets.enc")
        self.secret_store = SecretStore(self.encryptor, secrets_file)
        self.webhook_verifier = WebhookVerifier()
        self.auth_factory = AuthProviderFactory()
        self.security_manager = EnterpriseSecurityManager(
            self.secret_store,
            self.auth_factory,
            self.webhook_verifier
        )
        
        # Create data transformation components
        self.schema_registry = SchemaRegistry()
        self.canonical_model = CanonicalDataModel(self.schema_registry)
        self.transformer_factory = TransformerFactory(
            self.schema_registry,
            self.canonical_model
        )
        
        # Create monitoring components
        self.metrics_client = MetricsClient()
        self.log_client = LogClient()
        self.alert_manager = AlertManager()
        self.monitoring_service = EnterpriseMonitoringService(
            self.metrics_client,
            self.log_client,
            self.alert_manager
        )
        
        # Create adapter factory and register adapters
        self.adapter_factory = EnterpriseAdapterFactory()
        self._register_adapters()
        
        # Create gateway
        self.gateway = EnterpriseIntegrationGateway(
            registry=self.registry,
            auth_factory=self.auth_factory,
            transformer_factory=self.transformer_factory,
            monitoring_service=self.monitoring_service,
            adapter_factory=self.adapter_factory
        )
        
    def _register_adapters(self):
        """Register system adapters with the adapter factory."""
        self.adapter_factory.register_adapter_class("salesforce", SalesforceAdapter)
        self.adapter_factory.register_adapter_class("microsoft_teams", MicrosoftTeamsAdapter)
        self.adapter_factory.register_adapter_class("sap", SapAdapter)
        
    async def register_system(self, config: IntegrationConfig) -> bool:
        """
        Register an enterprise system.
        
        Args:
            config: Configuration for the system
            
        Returns:
            True if registration was successful, False otherwise
        """
        return await self.registry.register_system(config)
        
    async def unregister_system(self, system_id: str) -> bool:
        """
        Unregister an enterprise system.
        
        Args:
            system_id: ID of the system to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        return await self.registry.unregister_system(system_id)
        
    async def get_system(self, system_id: str) -> Optional[IntegrationConfig]:
        """
        Get an enterprise system by ID.
        
        Args:
            system_id: ID of the system to get
            
        Returns:
            The system configuration if found, None otherwise
        """
        return await self.registry.get_system(system_id)
        
    async def list_systems(self, filter_params: Dict[str, Any] = None) -> List[IntegrationConfig]:
        """
        List enterprise systems.
        
        Args:
            filter_params: Parameters for filtering the list
            
        Returns:
            List of system configurations
        """
        return await self.registry.list_systems(filter_params)
        
    async def execute_operation(
        self,
        system_id: str,
        operation: str,
        params: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute an operation on an enterprise system.
        
        Args:
            system_id: ID of the target system
            operation: Operation to perform
            params: Parameters for the operation
            context: Context information for the request
            
        Returns:
            Result of the operation
        """
        return await self.gateway.route_request(
            system_id=system_id,
            operation=operation,
            params=params,
            context=context
        )
        
    async def execute_batch_operation(
        self,
        system_id: str,
        operation: str,
        items: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a batch operation on an enterprise system.
        
        Args:
            system_id: ID of the target system
            operation: Operation to perform
            items: List of items to process
            context: Context information for the request
            
        Returns:
            List of results for each item
        """
        return await self.gateway.execute_batch(
            system_id=system_id,
            operation=operation,
            items=items,
            context=context
        )
        
    async def register_webhook(
        self,
        system_id: str,
        event_type: str,
        callback_url: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Register a webhook with an enterprise system.
        
        Args:
            system_id: ID of the target system
            event_type: Type of event to subscribe to
            callback_url: URL to call when the event occurs
            context: Context information for the request
            
        Returns:
            Registration result
        """
        return await self.gateway.register_webhook(
            system_id=system_id,
            event_type=event_type,
            callback_url=callback_url,
            context=context
        )
        
    def store_credentials(self, system_id: str, credentials: Dict[str, str]) -> bool:
        """
        Store credentials for an enterprise system.
        
        Args:
            system_id: ID of the system
            credentials: Credentials to store
            
        Returns:
            True if storage was successful, False otherwise
        """
        return self.security_manager.store_credentials(system_id, credentials)
        
    async def rotate_credentials(self, system_id: str) -> bool:
        """
        Rotate credentials for an enterprise system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            True if rotation was successful, False otherwise
        """
        return await self.security_manager.rotate_credentials(system_id)
        
    def verify_webhook_signature(
        self,
        system_id: str,
        payload: str,
        headers: Dict[str, str]
    ) -> bool:
        """
        Verify a webhook signature.
        
        Args:
            system_id: ID of the system
            payload: Webhook payload
            headers: Webhook headers
            
        Returns:
            True if the signature is valid, False otherwise
        """
        return self.security_manager.verify_webhook_signature(
            system_id=system_id,
            payload=payload,
            headers=headers
        )
        
    def generate_webhook_secret(self, system_id: str) -> str:
        """
        Generate a new webhook secret for a system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            Generated secret
        """
        return self.security_manager.generate_webhook_secret(system_id)
        
    async def register_schema(
        self,
        entity_type: str,
        internal_schema: Dict[str, Any],
        external_schemas: Dict[str, Dict[str, Any]] = None
    ):
        """
        Register schemas for an entity type.
        
        Args:
            entity_type: Type of entity
            internal_schema: Schema for internal representation
            external_schemas: Schemas for external representations, keyed by system type
        """
        self.schema_registry.register_internal_schema(entity_type, internal_schema)
        
        if external_schemas:
            for system_type, schema in external_schemas.items():
                self.schema_registry.register_external_schema(
                    system_type=system_type,
                    entity_type=entity_type,
                    schema=schema
                )
                
        logger.info(f"Registered schemas for entity type: {entity_type}")
        
    async def shutdown(self):
        """Shutdown the Enterprise Integration module."""
        # Close any open connections
        for adapter in self.adapter_factory.adapters.values():
            try:
                await adapter.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting adapter: {e}")
                
        logger.info("Enterprise Integration module shutdown complete")


# Singleton instance
_instance = None

def get_instance(config_dir: str = None) -> EnterpriseIntegrationModule:
    """
    Get the singleton instance of the Enterprise Integration module.
    
    Args:
        config_dir: Directory for configuration and secrets
        
    Returns:
        Enterprise Integration module instance
    """
    global _instance
    if _instance is None:
        _instance = EnterpriseIntegrationModule(config_dir)
    return _instance
