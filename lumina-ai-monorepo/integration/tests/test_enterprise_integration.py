"""
Enterprise Integration Tests for Lumina AI.

This module contains tests for the enterprise integration components,
ensuring that they function correctly and meet requirements.
"""

import unittest
import asyncio
import json
import os
import logging
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEnterpriseIntegration(unittest.TestCase):
    """Test suite for enterprise integration components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test directory if it doesn't exist
        os.makedirs("test_data", exist_ok=True)
        
        # Set up test event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        """Clean up test environment."""
        self.loop.close()
        
    def test_integration_config(self):
        """Test IntegrationConfig class."""
        from integration.interfaces import IntegrationConfig
        
        # Create a test configuration
        config = IntegrationConfig(
            system_id="test-system",
            system_type="salesforce",
            name="Test Salesforce",
            description="Test Salesforce instance",
            connection_params={"instance_url": "https://test.salesforce.com"},
            auth_params={"type": "oauth2"},
            transform_params={"rules": {}},
            enabled=True,
            metadata={"supports_webhooks": True}
        )
        
        # Test properties
        self.assertEqual(config.system_id, "test-system")
        self.assertEqual(config.system_type, "salesforce")
        self.assertEqual(config.name, "Test Salesforce")
        self.assertEqual(config.description, "Test Salesforce instance")
        self.assertEqual(config.connection_params, {"instance_url": "https://test.salesforce.com"})
        self.assertEqual(config.auth_params, {"type": "oauth2"})
        self.assertEqual(config.transform_params, {"rules": {}})
        self.assertTrue(config.enabled)
        self.assertEqual(config.metadata, {"supports_webhooks": True})
        
        # Test to_dict and from_dict
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        
        new_config = IntegrationConfig.from_dict(config_dict)
        self.assertEqual(new_config.system_id, config.system_id)
        self.assertEqual(new_config.system_type, config.system_type)
        self.assertEqual(new_config.name, config.name)
        
    def test_in_memory_registry(self):
        """Test InMemoryIntegrationRegistry class."""
        from integration.interfaces import IntegrationConfig
        from integration.registry import InMemoryIntegrationRegistry
        
        # Create registry
        registry = InMemoryIntegrationRegistry()
        
        # Create test configurations
        config1 = IntegrationConfig(
            system_id="system-1",
            system_type="salesforce",
            name="Salesforce 1",
            enabled=True
        )
        
        config2 = IntegrationConfig(
            system_id="system-2",
            system_type="microsoft_teams",
            name="Microsoft Teams",
            enabled=True
        )
        
        config3 = IntegrationConfig(
            system_id="system-3",
            system_type="salesforce",
            name="Salesforce 2",
            enabled=False
        )
        
        # Test register_system
        result = self.loop.run_until_complete(registry.register_system(config1))
        self.assertTrue(result)
        
        result = self.loop.run_until_complete(registry.register_system(config2))
        self.assertTrue(result)
        
        result = self.loop.run_until_complete(registry.register_system(config3))
        self.assertTrue(result)
        
        # Test get_system
        system = self.loop.run_until_complete(registry.get_system("system-1"))
        self.assertEqual(system.name, "Salesforce 1")
        
        # Test list_systems
        systems = self.loop.run_until_complete(registry.list_systems())
        self.assertEqual(len(systems), 3)
        
        # Test list_systems with filter
        systems = self.loop.run_until_complete(registry.list_systems({"system_type": "salesforce"}))
        self.assertEqual(len(systems), 2)
        
        systems = self.loop.run_until_complete(registry.list_systems({"enabled": True}))
        self.assertEqual(len(systems), 2)
        
        # Test update_system
        config1.name = "Updated Salesforce"
        result = self.loop.run_until_complete(registry.update_system("system-1", config1))
        self.assertTrue(result)
        
        system = self.loop.run_until_complete(registry.get_system("system-1"))
        self.assertEqual(system.name, "Updated Salesforce")
        
        # Test unregister_system
        result = self.loop.run_until_complete(registry.unregister_system("system-1"))
        self.assertTrue(result)
        
        system = self.loop.run_until_complete(registry.get_system("system-1"))
        self.assertIsNone(system)
        
    def test_file_registry(self):
        """Test FileIntegrationRegistry class."""
        from integration.interfaces import IntegrationConfig
        from integration.registry import FileIntegrationRegistry
        
        # Create registry with test file
        test_file = "test_data/test_registry.json"
        registry = FileIntegrationRegistry(test_file)
        
        # Create test configuration
        config = IntegrationConfig(
            system_id="file-system-1",
            system_type="sap",
            name="SAP System",
            enabled=True
        )
        
        # Test register_system
        result = self.loop.run_until_complete(registry.register_system(config))
        self.assertTrue(result)
        
        # Test get_system
        system = self.loop.run_until_complete(registry.get_system("file-system-1"))
        self.assertEqual(system.name, "SAP System")
        
        # Test persistence by creating a new registry instance
        new_registry = FileIntegrationRegistry(test_file)
        system = self.loop.run_until_complete(new_registry.get_system("file-system-1"))
        self.assertEqual(system.name, "SAP System")
        
        # Clean up
        os.remove(test_file)
        
    def test_auth_providers(self):
        """Test authentication providers."""
        from integration.auth import BasicAuthProvider, OAuth2Provider, ApiKeyProvider
        
        # Test BasicAuthProvider
        basic_provider = BasicAuthProvider("testuser", "testpass")
        credentials = self.loop.run_until_complete(basic_provider.authenticate())
        
        self.assertEqual(credentials["type"], "basic")
        self.assertIn("value", credentials)
        
        # Test ApiKeyProvider
        api_key_provider = ApiKeyProvider("test-api-key")
        credentials = self.loop.run_until_complete(api_key_provider.authenticate())
        
        self.assertEqual(credentials["type"], "api_key")
        self.assertEqual(credentials["value"], "test-api-key")
        self.assertEqual(credentials["header_name"], "X-API-Key")
        
        # Test OAuth2Provider with mocked HTTP client
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = MagicMock(return_value={
                "access_token": "test-access-token",
                "refresh_token": "test-refresh-token",
                "expires_in": 3600
            })
            
            mock_session.return_value.post.return_value.__aenter__.return_value = mock_response
            
            oauth_provider = OAuth2Provider(
                client_id="test-client",
                client_secret="test-secret",
                token_url="https://test.com/token"
            )
            
            credentials = self.loop.run_until_complete(oauth_provider.authenticate())
            
            self.assertEqual(credentials["type"], "oauth2")
            self.assertEqual(credentials["access_token"], "test-access-token")
            self.assertEqual(credentials["refresh_token"], "test-refresh-token")
            
    def test_security_manager(self):
        """Test EnterpriseSecurityManager class."""
        from integration.security import CredentialEncryptor, SecretStore, WebhookVerifier, EnterpriseSecurityManager
        from integration.auth import AuthProviderFactory
        
        # Create dependencies
        encryptor = CredentialEncryptor("test-master-key")
        secret_store = SecretStore(encryptor)
        auth_factory = AuthProviderFactory()
        webhook_verifier = WebhookVerifier()
        
        # Create security manager
        security_manager = EnterpriseSecurityManager(secret_store, auth_factory, webhook_verifier)
        
        # Test store_credentials
        credentials = {
            "client_id": "test-client",
            "client_secret": "test-secret",
            "token_url": "https://test.com/token"
        }
        
        result = security_manager.store_credentials("test-system", credentials)
        self.assertTrue(result)
        
        # Test webhook signature verification
        with patch.object(webhook_verifier, "verify_signature", return_value=True):
            # Store webhook secret
            secret_store.set_secret("test-system:webhook:secret", "test-webhook-secret")
            
            # Test verification
            result = security_manager.verify_webhook_signature(
                "test-system",
                '{"event":"test"}',
                {"X-Hub-Signature-256": "test-signature"}
            )
            
            self.assertTrue(result)
            
    def test_data_transformer(self):
        """Test EnterpriseDataTransformer class."""
        from integration.interfaces import IntegrationConfig
        from integration.data_transformer import SchemaRegistry, CanonicalDataModel, EnterpriseDataTransformer
        
        # Create dependencies
        schema_registry = SchemaRegistry()
        canonical_model = CanonicalDataModel(schema_registry)
        
        # Register schemas
        schema_registry.register_internal_schema("contact", {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"}
            }
        })
        
        schema_registry.register_external_schema("salesforce", "contact", {
            "type": "object",
            "properties": {
                "Id": {"type": "string"},
                "FirstName": {"type": "string"},
                "LastName": {"type": "string"},
                "Email": {"type": "string"},
                "Phone": {"type": "string"}
            }
        })
        
        # Create test configuration with transformation rules
        config = IntegrationConfig(
            system_id="test-system",
            system_type="salesforce",
            name="Test Salesforce",
            transform_params={
                "rules": {
                    "contact": {
                        "outbound": {
                            "mode": "selective",
                            "field_mappings": {
                                "id": "Id",
                                "first_name": "FirstName",
                                "last_name": "LastName",
                                "email": "Email",
                                "phone": "Phone"
                            }
                        },
                        "inbound": {
                            "mode": "selective",
                            "field_mappings": {
                                "Id": "id",
                                "FirstName": "first_name",
                                "LastName": "last_name",
                                "Email": "email",
                                "Phone": "phone"
                            }
                        }
                    }
                }
            }
        )
        
        # Create transformer
        transformer = EnterpriseDataTransformer(config, schema_registry, canonical_model)
        
        # Test transform_to_external
        internal_data = {
            "_entity_type": "contact",
            "id": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234"
        }
        
        external_data = self.loop.run_until_complete(transformer.transform_to_external(internal_data))
        
        self.assertEqual(external_data["Id"], "12345")
        self.assertEqual(external_data["FirstName"], "John")
        self.assertEqual(external_data["LastName"], "Doe")
        
        # Test transform_to_internal
        external_data = {
            "Id": "67890",
            "FirstName": "Jane",
            "LastName": "Smith",
            "Email": "jane.smith@example.com",
            "Phone": "555-5678"
        }
        
        internal_data = self.loop.run_until_complete(transformer.transform_to_internal(external_data))
        
        self.assertEqual(internal_data["id"], "67890")
        self.assertEqual(internal_data["first_name"], "Jane")
        self.assertEqual(internal_data["last_name"], "Smith")
        self.assertEqual(internal_data["_entity_type"], "default")  # Default since not specified in external data
        
    def test_enterprise_gateway(self):
        """Test EnterpriseIntegrationGateway class."""
        from integration.interfaces import IntegrationConfig, IntegrationSystem
        from integration.enterprise_gateway import EnterpriseIntegrationGateway, CircuitBreaker
        
        # Create mock dependencies
        mock_registry = MagicMock()
        mock_auth_factory = MagicMock()
        mock_transformer_factory = MagicMock()
        mock_monitoring_service = MagicMock()
        mock_adapter_factory = MagicMock()
        
        # Create gateway
        gateway = EnterpriseIntegrationGateway(
            registry=mock_registry,
            auth_factory=mock_auth_factory,
            transformer_factory=mock_transformer_factory,
            monitoring_service=mock_monitoring_service,
            adapter_factory=mock_adapter_factory
        )
        
        # Set up mocks for a successful request
        mock_config = IntegrationConfig(
            system_id="test-system",
            system_type="salesforce",
            name="Test Salesforce",
            auth_params={"type": "oauth2"}
        )
        
        mock_registry.get_system.return_value = mock_config
        
        mock_adapter = MagicMock(spec=IntegrationSystem)
        mock_adapter.is_connected.return_value = False
        mock_adapter.connect.return_value = True
        mock_adapter.execute.return_value = {"id": "12345", "name": "Test Record"}
        
        mock_adapter_factory.create_adapter.return_value = mock_adapter
        
        mock_auth_provider = MagicMock()
        mock_auth_provider.get_credentials.return_value = {"access_token": "test-token"}
        
        mock_auth_factory.create_provider.return_value = mock_auth_provider
        
        mock_transformer = MagicMock()
        mock_transformer.transform_to_external.return_value = {"Name": "Test Record"}
        mock_transformer.transform_to_internal.return_value = {"name": "Test Record", "id": "12345"}
        
        mock_transformer_factory.create_transformer.return_value = mock_transformer
        
        # Test route_request
        result = self.loop.run_until_complete(gateway.route_request(
            system_id="test-system",
            operation="create",
            params={"name": "Test Record"},
            context={"request_id": "test-request"}
        ))
        
        # Verify result
        self.assertEqual(result["name"], "Test Record")
        self.assertEqual(result["id"], "12345")
        
        # Verify mocks were called correctly
        mock_registry.get_system.assert_called_once_with("test-system")
        mock_adapter_factory.create_adapter.assert_called_once_with(mock_config)
        mock_auth_factory.create_provider.assert_called_once()
        mock_auth_provider.get_credentials.assert_called_once()
        mock_transformer_factory.create_transformer.assert_called_once_with(mock_config)
        mock_transformer.transform_to_external.assert_called_once()
        mock_adapter.connect.assert_called_once()
        mock_adapter.execute.assert_called_once()
        mock_transformer.transform_to_internal.assert_called_once()
        mock_monitoring_service.log_operation.assert_called_once()
        
    def test_circuit_breaker(self):
        """Test CircuitBreaker class."""
        from integration.enterprise_gateway import CircuitBreaker, CircuitBreakerError
        
        # Create circuit breaker with low threshold for testing
        circuit_breaker = CircuitBreaker(failure_threshold=2, reset_timeout=0.1)
        
        # Test successful execution
        async def success_func():
            return "success"
            
        result = self.loop.run_until_complete(circuit_breaker.execute(success_func))
        self.assertEqual(result, "success")
        self.assertEqual(circuit_breaker.state, "closed")
        
        # Test failed execution
        async def fail_func():
            raise ValueError("test error")
            
        # First failure
        with self.assertRaises(ValueError):
            self.loop.run_until_complete(circuit_breaker.execute(fail_func))
            
        self.assertEqual(circuit_breaker.state, "closed")
        self.assertEqual(circuit_breaker.failure_count, 1)
        
        # Second failure - should open the circuit
        with self.assertRaises(ValueError):
            self.loop.run_until_complete(circuit_breaker.execute(fail_func))
            
        self.assertEqual(circuit_breaker.state, "open")
        self.assertEqual(circuit_breaker.failure_count, 2)
        
        # Try again - should fail with CircuitBreakerError
        with self.assertRaises(CircuitBreakerError):
            self.loop.run_until_complete(circuit_breaker.execute(success_func))
            
        # Wait for reset timeout
        self.loop.run_until_complete(asyncio.sleep(0.2))
        
        # Try again - should go to half-open state
        result = self.loop.run_until_complete(circuit_breaker.execute(success_func))
        self.assertEqual(result, "success")
        self.assertEqual(circuit_breaker.state, "closed")
        self.assertEqual(circuit_breaker.failure_count, 0)
        
    def test_salesforce_adapter(self):
        """Test SalesforceAdapter class."""
        from integration.interfaces import IntegrationConfig
        from integration.adapters import SalesforceAdapter
        
        # Create test configuration
        config = IntegrationConfig(
            system_id="test-salesforce",
            system_type="salesforce",
            name="Test Salesforce",
            connection_params={
                "instance_url": "https://test.salesforce.com",
                "api_version": "v58.0"
            }
        )
        
        # Create adapter
        adapter = SalesforceAdapter(config)
        
        # Test connect
        with patch("aiohttp.ClientSession") as mock_session:
            result = self.loop.run_until_complete(adapter.connect())
            self.assertTrue(result)
            self.assertIsNotNone(adapter.client)
            
        # Test execute with mocked HTTP client
        with patch.object(adapter, "client") as mock_client:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = MagicMock(return_value={"records": [{"Id": "12345", "Name": "Test Account"}]})
            
            mock_client.get.return_value.__aenter__.return_value = mock_response
            
            # Test query operation
            result = self.loop.run_until_complete(adapter.execute(
                operation="query",
                params={"soql": "SELECT Id, Name FROM Account"},
                credentials={"access_token": "test-token"}
            ))
            
            self.assertIn("records", result)
            mock_client.get.assert_called_once()
            
        # Test disconnect
        with patch.object(adapter, "client") as mock_client:
            result = self.loop.run_until_complete(adapter.disconnect())
            self.assertTrue(result)
            mock_client.close.assert_called_once()
            
    def test_microsoft_teams_adapter(self):
        """Test MicrosoftTeamsAdapter class."""
        from integration.interfaces import IntegrationConfig
        from integration.adapters import MicrosoftTeamsAdapter
        
        # Create test configuration
        config = IntegrationConfig(
            system_id="test-teams",
            system_type="microsoft_teams",
            name="Test Microsoft Teams"
        )
        
        # Create adapter
        adapter = MicrosoftTeamsAdapter(config)
        
        # Test connect
        with patch("aiohttp.ClientSession") as mock_session:
            result = self.loop.run_until_complete(adapter.connect())
            self.assertTrue(result)
            self.assertIsNotNone(adapter.client)
            
        # Test execute with mocked HTTP client
        with patch.object(adapter, "client") as mock_client:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = MagicMock(return_value={"value": [{"id": "team1", "displayName": "Team 1"}]})
            
            mock_client.get.return_value.__aenter__.return_value = mock_response
            
            # Test get_teams operation
            result = self.loop.run_until_complete(adapter.execute(
                operation="get_teams",
                params={},
                credentials={"access_token": "test-token"}
            ))
            
            self.assertIn("value", result)
            mock_client.get.assert_called_once()
            
        # Test disconnect
        with patch.object(adapter, "client") as mock_client:
            result = self.loop.run_until_complete(adapter.disconnect())
            self.assertTrue(result)
            mock_client.close.assert_called_once()
            
    def test_sap_adapter(self):
        """Test SapAdapter class."""
        from integration.interfaces import IntegrationConfig
        from integration.adapters import SapAdapter
        
        # Create test configuration
        config = IntegrationConfig(
            system_id="test-sap",
            system_type="sap",
            name="Test SAP",
            connection_params={
                "base_url": "https://test-sap.example.com/odata/v2"
            }
        )
        
        # Create adapter
        adapter = SapAdapter(config)
        
        # Test connect
        with patch("aiohttp.ClientSession") as mock_session:
            result = self.loop.run_until_complete(adapter.connect())
            self.assertTrue(result)
            self.assertIsNotNone(adapter.client)
            
        # Test execute with mocked HTTP client
        with patch.object(adapter, "client") as mock_client:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = MagicMock(return_value={"d": {"results": [{"ID": "12345", "Name": "Test Material"}]}})
            
            mock_client.get.return_value.__aenter__.return_value = mock_response
            
            # Test query_entities operation
            result = self.loop.run_until_complete(adapter.execute(
                operation="query_entities",
                params={"entity_set": "Materials", "filter": "Name eq 'Test Material'"},
                credentials={"access_token": "test-token"}
            ))
            
            self.assertIn("d", result)
            mock_client.get.assert_called_once()
            
        # Test disconnect
        with patch.object(adapter, "client") as mock_client:
            result = self.loop.run_until_complete(adapter.disconnect())
            self.assertTrue(result)
            mock_client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
