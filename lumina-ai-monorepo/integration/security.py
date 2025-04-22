"""
Enterprise Security Manager for Lumina AI.

This module implements comprehensive security mechanisms for enterprise integrations,
providing secure authentication, credential management, and encryption capabilities.
"""

import logging
import json
import base64
import os
import time
import uuid
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .interfaces import AuthenticationProvider
from .auth import AuthProviderFactory

logger = logging.getLogger(__name__)


class CredentialEncryptor:
    """Encryptor for sensitive credentials."""
    
    def __init__(self, master_key: str = None):
        """
        Initialize a new credential encryptor.
        
        Args:
            master_key: Master key for encryption (if None, a key will be generated)
        """
        if master_key:
            # Use provided master key
            self.master_key = master_key
        else:
            # Generate a new master key
            self.master_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            logger.info("Generated new master key for credential encryption")
            
        # Derive encryption key from master key
        self.encryption_key = self._derive_key(self.master_key)
        self.fernet = Fernet(self.encryption_key)
        
    def _derive_key(self, master_key: str) -> bytes:
        """
        Derive an encryption key from the master key.
        
        Args:
            master_key: Master key
            
        Returns:
            Derived encryption key
        """
        # Use a fixed salt for deterministic key derivation
        salt = b'lumina_ai_enterprise_integration'
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        # Convert master key to bytes and derive key
        key_bytes = master_key.encode()
        derived_key = kdf.derive(key_bytes)
        
        # Return URL-safe base64 encoded key for Fernet
        return base64.urlsafe_b64encode(derived_key)
        
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as a string
        """
        if not data:
            return ""
            
        # Convert data to bytes, encrypt, and return as string
        data_bytes = data.encode()
        encrypted_bytes = self.fernet.encrypt(data_bytes)
        return encrypted_bytes.decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
            
        Raises:
            ValueError: If decryption fails
        """
        if not encrypted_data:
            return ""
            
        try:
            # Convert encrypted data to bytes, decrypt, and return as string
            encrypted_bytes = encrypted_data.encode()
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise ValueError("Failed to decrypt data")


class SecretStore:
    """Secure storage for sensitive credentials and secrets."""
    
    def __init__(self, encryptor: CredentialEncryptor, storage_path: str = None):
        """
        Initialize a new secret store.
        
        Args:
            encryptor: Encryptor for sensitive data
            storage_path: Path to store secrets (if None, in-memory storage will be used)
        """
        self.encryptor = encryptor
        self.storage_path = storage_path
        self.secrets = {}
        
        # Load secrets if storage path is provided
        if storage_path:
            self._load_secrets()
        
    def _load_secrets(self):
        """Load secrets from storage."""
        if not os.path.exists(self.storage_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            # Create empty secrets file
            with open(self.storage_path, 'w') as f:
                f.write('{}')
            return
            
        try:
            with open(self.storage_path, 'r') as f:
                encrypted_secrets = json.load(f)
                
                # Decrypt each secret
                for key, value in encrypted_secrets.items():
                    self.secrets[key] = self.encryptor.decrypt(value)
                    
            logger.info(f"Loaded {len(self.secrets)} secrets from {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Error loading secrets: {str(e)}")
            self.secrets = {}
    
    def _save_secrets(self):
        """Save secrets to storage."""
        if not self.storage_path:
            return
            
        try:
            # Encrypt each secret
            encrypted_secrets = {}
            for key, value in self.secrets.items():
                encrypted_secrets[key] = self.encryptor.encrypt(value)
                
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump(encrypted_secrets, f)
                
            logger.info(f"Saved {len(self.secrets)} secrets to {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Error saving secrets: {str(e)}")
    
    def set_secret(self, key: str, value: str):
        """
        Set a secret.
        
        Args:
            key: Secret key
            value: Secret value
        """
        self.secrets[key] = value
        self._save_secrets()
        
    def get_secret(self, key: str) -> Optional[str]:
        """
        Get a secret.
        
        Args:
            key: Secret key
            
        Returns:
            Secret value if found, None otherwise
        """
        return self.secrets.get(key)
        
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Secret key
            
        Returns:
            True if the secret was deleted, False otherwise
        """
        if key in self.secrets:
            del self.secrets[key]
            self._save_secrets()
            return True
            
        return False
        
    def get_secrets(self, system_id: str, secret_type: str) -> Dict[str, str]:
        """
        Get all secrets for a system and type.
        
        Args:
            system_id: ID of the system
            secret_type: Type of secrets to get
            
        Returns:
            Dictionary of secrets
        """
        prefix = f"{system_id}:{secret_type}:"
        result = {}
        
        for key, value in self.secrets.items():
            if key.startswith(prefix):
                # Remove prefix from key
                param_name = key[len(prefix):]
                result[param_name] = value
                
        return result


class WebhookVerifier:
    """Verifier for webhook signatures."""
    
    def verify_signature(
        self,
        payload: str,
        signature: str,
        secret: str,
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify a webhook signature.
        
        Args:
            payload: Webhook payload
            signature: Signature to verify
            secret: Secret key for verification
            algorithm: Hash algorithm to use
            
        Returns:
            True if the signature is valid, False otherwise
        """
        if not payload or not signature or not secret:
            return False
            
        try:
            # Compute expected signature
            if algorithm == 'sha256':
                digest = hmac.new(
                    secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
            elif algorithm == 'sha1':
                digest = hmac.new(
                    secret.encode(),
                    payload.encode(),
                    hashlib.sha1
                ).hexdigest()
            else:
                logger.error(f"Unsupported algorithm: {algorithm}")
                return False
                
            # Compare signatures
            return hmac.compare_digest(digest, signature)
            
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False


class EnterpriseSecurityManager:
    """
    Security manager for enterprise integrations.
    
    This class provides comprehensive security capabilities for enterprise
    integrations, including authentication, credential management, and encryption.
    """
    
    def __init__(
        self,
        secret_store: SecretStore,
        auth_factory: AuthProviderFactory,
        webhook_verifier: WebhookVerifier
    ):
        """
        Initialize a new enterprise security manager.
        
        Args:
            secret_store: Store for sensitive credentials
            auth_factory: Factory for creating authentication providers
            webhook_verifier: Verifier for webhook signatures
        """
        self.secret_store = secret_store
        self.auth_factory = auth_factory
        self.webhook_verifier = webhook_verifier
        self.provider_cache = {}
        
    def get_provider(self, system_config) -> AuthenticationProvider:
        """
        Get an authentication provider for a system.
        
        Args:
            system_config: Configuration for the system
            
        Returns:
            Authentication provider for the system
        """
        system_id = system_config.system_id
        
        if system_id in self.provider_cache:
            return self.provider_cache[system_id]
            
        # Get auth parameters from secure storage
        auth_params = self.secret_store.get_secrets(
            system_id=system_id,
            secret_type="auth"
        )
        
        # Merge with non-sensitive parameters from config
        for key, value in system_config.auth_params.items():
            if key not in auth_params and key != "type":
                auth_params[key] = value
        
        # Create appropriate auth provider
        auth_type = system_config.auth_params.get("type", "oauth2")
        provider = self.auth_factory.create_provider(
            auth_type=auth_type,
            **auth_params
        )
        
        # Cache the provider
        self.provider_cache[system_id] = provider
        
        return provider
        
    async def rotate_credentials(self, system_id: str) -> bool:
        """
        Rotate credentials for a system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            True if rotation was successful, False otherwise
        """
        if system_id in self.provider_cache:
            provider = self.provider_cache[system_id]
            
            try:
                # Revoke current credentials
                await provider.revoke()
                
                # Remove from cache to force recreation
                del self.provider_cache[system_id]
                
                return True
                
            except Exception as e:
                logger.error(f"Error rotating credentials: {str(e)}")
                return False
                
        return False
        
    def store_credentials(self, system_id: str, credentials: Dict[str, str]) -> bool:
        """
        Store credentials for a system.
        
        Args:
            system_id: ID of the system
            credentials: Credentials to store
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Store each credential
            for key, value in credentials.items():
                self.secret_store.set_secret(f"{system_id}:auth:{key}", value)
                
            return True
            
        except Exception as e:
            logger.error(f"Error storing credentials: {str(e)}")
            return False
            
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
        # Get webhook secret
        webhook_secret = self.secret_store.get_secret(f"{system_id}:webhook:secret")
        if not webhook_secret:
            logger.warning(f"No webhook secret found for system: {system_id}")
            return False
            
        # Get signature from headers based on system-specific header name
        signature_header = self.secret_store.get_secret(f"{system_id}:webhook:signature_header")
        if not signature_header:
            # Default to common signature headers
            for header in ["X-Hub-Signature-256", "X-Signature", "X-Webhook-Signature"]:
                if header in headers:
                    signature = headers[header]
                    break
            else:
                logger.warning(f"No signature header found for system: {system_id}")
                return False
        else:
            signature = headers.get(signature_header)
            if not signature:
                logger.warning(f"Signature header not found in request: {signature_header}")
                return False
                
        # Get algorithm
        algorithm = self.secret_store.get_secret(f"{system_id}:webhook:algorithm") or "sha256"
        
        # Verify signature
        return self.webhook_verifier.verify_signature(
            payload=payload,
            signature=signature,
            secret=webhook_secret,
            algorithm=algorithm
        )
        
    def generate_webhook_secret(self, system_id: str) -> str:
        """
        Generate a new webhook secret for a system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            Generated secret
        """
        # Generate a random secret
        secret = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Store the secret
        self.secret_store.set_secret(f"{system_id}:webhook:secret", secret)
        
        return secret
