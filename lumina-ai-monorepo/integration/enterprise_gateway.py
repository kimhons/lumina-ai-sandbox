"""
Enterprise Integration Gateway for Lumina AI.

This module implements the central gateway for all enterprise system integrations,
providing a unified interface for interacting with external enterprise systems.
"""

import logging
import asyncio
import datetime
from typing import Dict, List, Any, Optional, Union

from .interfaces import (
    IntegrationSystem, AuthenticationProvider, DataTransformer,
    IntegrationEvent, IntegrationConfig, IntegrationRegistry
)
from .auth import AuthProviderFactory

logger = logging.getLogger(__name__)


class SystemNotFoundError(Exception):
    """Exception raised when a requested system is not found."""
    pass


class UnsupportedOperationError(Exception):
    """Exception raised when an unsupported operation is requested."""
    pass


class CircuitBreakerError(Exception):
    """Exception raised when a circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 5.0
    ):
        """
        Initialize a new circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            reset_timeout: Time in seconds before attempting to close the circuit
            half_open_timeout: Time in seconds to wait in half-open state
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def execute(self, func, *args, **kwargs):
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function
            
        Raises:
            CircuitBreakerError: If the circuit is open
            Exception: Any exception raised by the function
        """
        if self.state == "open":
            if self.last_failure_time is None:
                self.last_failure_time = datetime.datetime.now()
                
            elapsed = (datetime.datetime.now() - self.last_failure_time).total_seconds()
            
            if elapsed > self.reset_timeout:
                logger.info("Circuit breaker transitioning from open to half-open")
                self.state = "half-open"
            else:
                raise CircuitBreakerError("Circuit breaker is open")
        
        try:
            if self.state == "half-open":
                # In half-open state, only allow one request through
                # and wait for the result before allowing more
                result = await func(*args, **kwargs)
                
                logger.info("Circuit breaker transitioning from half-open to closed")
                self.state = "closed"
                self.failure_count = 0
                self.last_failure_time = None
                
                return result
            else:
                # Normal execution in closed state
                return await func(*args, **kwargs)
                
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.datetime.now()
            
            if self.state == "half-open" or self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit breaker transitioning to open state due to: {str(e)}")
                self.state = "open"
            
            raise


class EnterpriseIntegrationGateway:
    """
    Gateway for enterprise system integrations.
    
    This class serves as the central entry point for all enterprise integrations,
    providing a unified interface for interacting with external enterprise systems.
    """
    
    def __init__(
        self,
        registry: IntegrationRegistry,
        auth_factory: AuthProviderFactory,
        transformer_factory: Any,
        monitoring_service: Any,
        adapter_factory: Any
    ):
        """
        Initialize a new enterprise integration gateway.
        
        Args:
            registry: Registry of integration systems
            auth_factory: Factory for creating authentication providers
            transformer_factory: Factory for creating data transformers
            monitoring_service: Service for monitoring and logging
            adapter_factory: Factory for creating system adapters
        """
        self.registry = registry
        self.auth_factory = auth_factory
        self.transformer_factory = transformer_factory
        self.monitoring_service = monitoring_service
        self.adapter_factory = adapter_factory
        
        self.circuit_breakers = {}
    
    def _get_circuit_breaker(self, system_id: str) -> CircuitBreaker:
        """
        Get or create a circuit breaker for a system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            Circuit breaker for the system
        """
        if system_id not in self.circuit_breakers:
            self.circuit_breakers[system_id] = CircuitBreaker()
            
        return self.circuit_breakers[system_id]
    
    async def route_request(
        self,
        system_id: str,
        operation: str,
        params: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Route a request to the appropriate system.
        
        Args:
            system_id: ID of the target system
            operation: Operation to perform
            params: Parameters for the operation
            context: Context information for the request
            
        Returns:
            Result of the operation
            
        Raises:
            SystemNotFoundError: If the system is not found
            UnsupportedOperationError: If the operation is not supported
            CircuitBreakerError: If the circuit breaker is open
            Exception: Any exception raised by the system
        """
        start_time = datetime.datetime.now()
        request_id = context.get("request_id") if context else None
        
        try:
            # Get system configuration
            system_config = await self.registry.get_system(system_id)
            if not system_config:
                raise SystemNotFoundError(f"System not found: {system_id}")
                
            # Get adapter for the system
            adapter = self.adapter_factory.create_adapter(system_config)
            
            # Get authentication provider
            auth_provider = self.auth_factory.create_provider(
                auth_type=system_config.auth_params.get("type", "oauth2"),
                **system_config.auth_params
            )
            
            # Get credentials
            credentials = await auth_provider.get_credentials()
            
            # Get transformer
            transformer = self.transformer_factory.create_transformer(system_config)
            
            # Transform request parameters
            transformed_params = await transformer.transform_to_external(params or {})
            
            # Get circuit breaker
            circuit_breaker = self._get_circuit_breaker(system_id)
            
            # Execute operation with circuit breaker
            async def execute_operation():
                # Ensure connection
                if not await adapter.is_connected():
                    await adapter.connect()
                    
                # Execute operation
                return await adapter.execute(operation, transformed_params, credentials)
            
            # Execute with circuit breaker
            result = await circuit_breaker.execute(execute_operation)
            
            # Transform response
            internal_result = await transformer.transform_to_internal(result)
            
            # Log successful operation
            await self.monitoring_service.log_operation(
                system_id=system_id,
                operation=operation,
                status="success",
                duration=(datetime.datetime.now() - start_time).total_seconds(),
                request_id=request_id,
                context=context
            )
            
            return internal_result
            
        except Exception as e:
            # Log failed operation
            await self.monitoring_service.log_operation(
                system_id=system_id,
                operation=operation,
                status="error",
                error=str(e),
                duration=(datetime.datetime.now() - start_time).total_seconds(),
                request_id=request_id,
                context=context
            )
            
            # Re-raise the exception
            raise
    
    async def execute_batch(
        self,
        system_id: str,
        operation: str,
        items: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a batch operation on a system.
        
        Args:
            system_id: ID of the target system
            operation: Operation to perform
            items: List of items to process
            context: Context information for the request
            
        Returns:
            List of results for each item
            
        Raises:
            SystemNotFoundError: If the system is not found
            UnsupportedOperationError: If the operation is not supported
            CircuitBreakerError: If the circuit breaker is open
            Exception: Any exception raised by the system
        """
        start_time = datetime.datetime.now()
        request_id = context.get("request_id") if context else None
        
        try:
            # Get system configuration
            system_config = await self.registry.get_system(system_id)
            if not system_config:
                raise SystemNotFoundError(f"System not found: {system_id}")
                
            # Check if system supports batch operations
            if not system_config.metadata.get("supports_batch", False):
                # Fall back to individual operations
                results = []
                for item in items:
                    result = await self.route_request(
                        system_id=system_id,
                        operation=operation,
                        params=item,
                        context=context
                    )
                    results.append(result)
                    
                return results
                
            # Get adapter for the system
            adapter = self.adapter_factory.create_adapter(system_config)
            
            # Get authentication provider
            auth_provider = self.auth_factory.create_provider(
                auth_type=system_config.auth_params.get("type", "oauth2"),
                **system_config.auth_params
            )
            
            # Get credentials
            credentials = await auth_provider.get_credentials()
            
            # Get transformer
            transformer = self.transformer_factory.create_transformer(system_config)
            
            # Transform each item
            transformed_items = []
            for item in items:
                transformed_item = await transformer.transform_to_external(item)
                transformed_items.append(transformed_item)
            
            # Get circuit breaker
            circuit_breaker = self._get_circuit_breaker(system_id)
            
            # Execute batch operation with circuit breaker
            async def execute_batch_operation():
                # Ensure connection
                if not await adapter.is_connected():
                    await adapter.connect()
                    
                # Execute batch operation
                batch_params = {
                    "items": transformed_items
                }
                return await adapter.execute(f"batch_{operation}", batch_params, credentials)
            
            # Execute with circuit breaker
            batch_result = await circuit_breaker.execute(execute_batch_operation)
            
            # Transform each result
            results = []
            for result in batch_result.get("results", []):
                internal_result = await transformer.transform_to_internal(result)
                results.append(internal_result)
            
            # Log successful operation
            await self.monitoring_service.log_operation(
                system_id=system_id,
                operation=f"batch_{operation}",
                status="success",
                item_count=len(items),
                duration=(datetime.datetime.now() - start_time).total_seconds(),
                request_id=request_id,
                context=context
            )
            
            return results
            
        except Exception as e:
            # Log failed operation
            await self.monitoring_service.log_operation(
                system_id=system_id,
                operation=f"batch_{operation}",
                status="error",
                error=str(e),
                item_count=len(items),
                duration=(datetime.datetime.now() - start_time).total_seconds(),
                request_id=request_id,
                context=context
            )
            
            # Re-raise the exception
            raise
    
    async def register_webhook(
        self,
        system_id: str,
        event_type: str,
        callback_url: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Register a webhook with an external system.
        
        Args:
            system_id: ID of the target system
            event_type: Type of event to subscribe to
            callback_url: URL to call when the event occurs
            context: Context information for the request
            
        Returns:
            Registration result
            
        Raises:
            SystemNotFoundError: If the system is not found
            UnsupportedOperationError: If webhooks are not supported
            Exception: Any exception raised by the system
        """
        start_time = datetime.datetime.now()
        request_id = context.get("request_id") if context else None
        
        try:
            # Get system configuration
            system_config = await self.registry.get_system(system_id)
            if not system_config:
                raise SystemNotFoundError(f"System not found: {system_id}")
                
            # Check if system supports webhooks
            if not system_config.metadata.get("supports_webhooks", False):
                raise UnsupportedOperationError(f"System does not support webhooks: {system_id}")
                
            # Get adapter for the system
            adapter = self.adapter_factory.create_adapter(system_config)
            
            # Get authentication provider
            auth_provider = self.auth_factory.create_provider(
                auth_type=system_config.auth_params.get("type", "oauth2"),
                **system_config.auth_params
            )
            
            # Get credentials
            credentials = await auth_provider.get_credentials()
            
            # Get circuit breaker
            circuit_breaker = self._get_circuit_breaker(system_id)
            
            # Execute webhook registration with circuit breaker
            async def execute_webhook_registration():
                # Ensure connection
                if not await adapter.is_connected():
                    await adapter.connect()
                    
                # Execute webhook registration
                webhook_params = {
                    "event_type": event_type,
                    "callback_url": callback_url
                }
                return await adapter.execute("register_webhook", webhook_params, credentials)
            
            # Execute with circuit breaker
            result = await circuit_breaker.execute(execute_webhook_registration)
            
            # Log successful operation
            await self.monitoring_service.log_operation(
                system_id=system_id,
                operation="register_webhook",
                status="success",
                event_type=event_type,
                callback_url=callback_url,
                duration=(datetime.datetime.now() - start_time).total_seconds(),
                request_id=request_id,
                context=context
            )
            
            return result
            
        except Exception as e:
            # Log failed operation
            await self.monitoring_service.log_operation(
                system_id=system_id,
                operation="register_webhook",
                status="error",
                error=str(e),
                event_type=event_type,
                callback_url=callback_url,
                duration=(datetime.datetime.now() - start_time).total_seconds(),
                request_id=request_id,
                context=context
            )
            
            # Re-raise the exception
            raise
