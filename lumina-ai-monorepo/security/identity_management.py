"""
Lumina AI Security Package - Identity Management Module

This module implements identity management for Lumina AI, including:
- User identity lifecycle management
- Identity verification and validation
- Identity federation and synchronization
- Identity attribute management

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

import uuid
import time
import json
import logging
import hashlib
import secrets
import re
from typing import Dict, List, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Credential:
    """Represents a user credential in the system."""
    id: str
    user_id: str
    type: str  # password, api_key, certificate, etc.
    status: str  # active, expired, revoked, etc.
    created_at: float
    expires_at: Optional[float] = None
    last_used_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the credential is expired."""
        if not self.expires_at:
            return False
        return time.time() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert credential to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used_at": self.last_used_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Credential":
        """Create credential from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            type=data["type"],
            status=data["status"],
            created_at=data["created_at"],
            expires_at=data.get("expires_at"),
            last_used_at=data.get("last_used_at"),
            metadata=data.get("metadata", {})
        )

@dataclass
class PasswordCredential(Credential):
    """Represents a password credential."""
    password_hash: str = ""
    salt: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert password credential to dictionary."""
        data = super().to_dict()
        data["password_hash"] = self.password_hash
        data["salt"] = self.salt
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PasswordCredential":
        """Create password credential from dictionary."""
        cred = super().from_dict(data)
        return cls(
            id=cred.id,
            user_id=cred.user_id,
            type=cred.type,
            status=cred.status,
            created_at=cred.created_at,
            expires_at=cred.expires_at,
            last_used_at=cred.last_used_at,
            metadata=cred.metadata,
            password_hash=data.get("password_hash", ""),
            salt=data.get("salt", "")
        )

@dataclass
class ApiKeyCredential(Credential):
    """Represents an API key credential."""
    key_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert API key credential to dictionary."""
        data = super().to_dict()
        data["key_hash"] = self.key_hash
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiKeyCredential":
        """Create API key credential from dictionary."""
        cred = super().from_dict(data)
        return cls(
            id=cred.id,
            user_id=cred.user_id,
            type=cred.type,
            status=cred.status,
            created_at=cred.created_at,
            expires_at=cred.expires_at,
            last_used_at=cred.last_used_at,
            metadata=cred.metadata,
            key_hash=data.get("key_hash", "")
        )

@dataclass
class MfaCredential(Credential):
    """Represents a multi-factor authentication credential."""
    mfa_type: str = ""  # totp, sms, email, etc.
    secret: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MFA credential to dictionary."""
        data = super().to_dict()
        data["mfa_type"] = self.mfa_type
        data["secret"] = self.secret
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MfaCredential":
        """Create MFA credential from dictionary."""
        cred = super().from_dict(data)
        return cls(
            id=cred.id,
            user_id=cred.user_id,
            type=cred.type,
            status=cred.status,
            created_at=cred.created_at,
            expires_at=cred.expires_at,
            last_used_at=cred.last_used_at,
            metadata=cred.metadata,
            mfa_type=data.get("mfa_type", ""),
            secret=data.get("secret", "")
        )

@dataclass
class IdentityProvider:
    """Represents an external identity provider."""
    id: str
    name: str
    type: str  # oauth, saml, ldap, etc.
    status: str  # active, inactive
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert identity provider to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IdentityProvider":
        """Create identity provider from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            status=data["status"],
            config=data.get("config", {})
        )

@dataclass
class ExternalIdentity:
    """Represents a user's identity in an external system."""
    id: str
    user_id: str
    provider_id: str
    external_id: str
    created_at: float
    last_verified_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert external identity to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider_id": self.provider_id,
            "external_id": self.external_id,
            "created_at": self.created_at,
            "last_verified_at": self.last_verified_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExternalIdentity":
        """Create external identity from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            provider_id=data["provider_id"],
            external_id=data["external_id"],
            created_at=data["created_at"],
            last_verified_at=data.get("last_verified_at"),
            metadata=data.get("metadata", {})
        )

class PasswordPolicy:
    """Defines password requirements and validation."""
    
    def __init__(self, 
                 min_length: int = 8, 
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_numbers: bool = True,
                 require_special_chars: bool = True,
                 max_age_days: Optional[int] = 90,
                 prevent_reuse: int = 5):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special_chars = require_special_chars
        self.max_age_days = max_age_days
        self.prevent_reuse = prevent_reuse
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate a password against the policy."""
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if self.require_special_chars and not any(not c.isalnum() for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password meets requirements"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert password policy to dictionary."""
        return {
            "min_length": self.min_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_numbers": self.require_numbers,
            "require_special_chars": self.require_special_chars,
            "max_age_days": self.max_age_days,
            "prevent_reuse": self.prevent_reuse
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PasswordPolicy":
        """Create password policy from dictionary."""
        return cls(
            min_length=data.get("min_length", 8),
            require_uppercase=data.get("require_uppercase", True),
            require_lowercase=data.get("require_lowercase", True),
            require_numbers=data.get("require_numbers", True),
            require_special_chars=data.get("require_special_chars", True),
            max_age_days=data.get("max_age_days", 90),
            prevent_reuse=data.get("prevent_reuse", 5)
        )

class IdentityManagementService:
    """Service for managing user identities and credentials."""
    
    def __init__(self):
        self.credentials: Dict[str, Credential] = {}
        self.identity_providers: Dict[str, IdentityProvider] = {}
        self.external_identities: Dict[str, ExternalIdentity] = {}
        self.password_policy = PasswordPolicy()
        self.password_history: Dict[str, List[str]] = {}  # user_id -> list of password hashes
    
    def create_password_credential(self, user_id: str, password: str) -> Optional[PasswordCredential]:
        """Create a new password credential for a user."""
        # Validate password against policy
        valid, message = self.password_policy.validate_password(password)
        if not valid:
            logger.error(f"Password validation failed: {message}")
            return None
        
        # Check password history
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        if user_id in self.password_history:
            for old_hash in self.password_history[user_id]:
                if self._verify_password_hash(password, old_hash):
                    logger.error("Password has been used recently")
                    return None
        
        # Create credential
        cred_id = str(uuid.uuid4())
        credential = PasswordCredential(
            id=cred_id,
            user_id=user_id,
            type="password",
            status="active",
            created_at=time.time(),
            expires_at=time.time() + (self.password_policy.max_age_days * 86400) if self.password_policy.max_age_days else None,
            password_hash=password_hash,
            salt=salt
        )
        
        # Store credential
        self.credentials[cred_id] = credential
        
        # Update password history
        if user_id not in self.password_history:
            self.password_history[user_id] = []
        
        self.password_history[user_id].append(password_hash)
        
        # Trim history if needed
        if len(self.password_history[user_id]) > self.password_policy.prevent_reuse:
            self.password_history[user_id] = self.password_history[user_id][-self.password_policy.prevent_reuse:]
        
        logger.info(f"Created password credential for user {user_id}")
        return credential
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify a user's password."""
        # Find active password credential for user
        for cred in self.credentials.values():
            if (cred.user_id == user_id and 
                cred.type == "password" and 
                cred.status == "active" and 
                isinstance(cred, PasswordCredential) and
                not cred.is_expired()):
                
                # Verify password
                if self._verify_password(password, cred.password_hash, cred.salt):
                    # Update last used timestamp
                    cred.last_used_at = time.time()
                    logger.info(f"Password verified for user {user_id}")
                    return True
        
        logger.info(f"Password verification failed for user {user_id}")
        return False
    
    def create_api_key(self, user_id: str, expires_in_days: Optional[int] = 30) -> tuple[str, ApiKeyCredential]:
        """Create a new API key for a user."""
        # Generate API key
        api_key = f"lmn_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_api_key(api_key)
        
        # Create credential
        cred_id = str(uuid.uuid4())
        credential = ApiKeyCredential(
            id=cred_id,
            user_id=user_id,
            type="api_key",
            status="active",
            created_at=time.time(),
            expires_at=time.time() + (expires_in_days * 86400) if expires_in_days else None,
            key_hash=key_hash
        )
        
        # Store credential
        self.credentials[cred_id] = credential
        
        logger.info(f"Created API key for user {user_id}")
        return api_key, credential
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify an API key and return the associated user ID if valid."""
        key_hash = self._hash_api_key(api_key)
        
        # Find matching API key credential
        for cred in self.credentials.values():
            if (cred.type == "api_key" and 
                cred.status == "active" and 
                isinstance(cred, ApiKeyCredential) and
                not cred.is_expired() and
                cred.key_hash == key_hash):
                
                # Update last used timestamp
                cred.last_used_at = time.time()
                logger.info(f"API key verified for user {cred.user_id}")
                return cred.user_id
        
        logger.info("API key verification failed")
        return None
    
    def create_mfa_credential(self, user_id: str, mfa_type: str) -> tuple[str, MfaCredential]:
        """Create a new MFA credential for a user."""
        # Generate MFA secret
        secret = secrets.token_hex(20)
        
        # Create credential
        cred_id = str(uuid.uuid4())
        credential = MfaCredential(
            id=cred_id,
            user_id=user_id,
            type="mfa",
            status="active",
            created_at=time.time(),
            mfa_type=mfa_type,
            secret=secret
        )
        
        # Store credential
        self.credentials[cred_id] = credential
        
        logger.info(f"Created MFA credential ({mfa_type}) for user {user_id}")
        return secret, credential
    
    def verify_mfa(self, user_id: str, mfa_type: str, code: str) -> bool:
        """Verify an MFA code."""
        # Find active MFA credential for user
        for cred in self.credentials.values():
            if (cred.user_id == user_id and 
                cred.type == "mfa" and 
                cred.status == "active" and 
                isinstance(cred, MfaCredential) and
                cred.mfa_type == mfa_type):
                
                # Verify code (implementation depends on MFA type)
                if self._verify_mfa_code(cred, code):
                    # Update last used timestamp
                    cred.last_used_at = time.time()
                    logger.info(f"MFA code verified for user {user_id}")
                    return True
        
        logger.info(f"MFA verification failed for user {user_id}")
        return False
    
    def register_identity_provider(self, name: str, provider_type: str, config: Dict[str, Any]) -> IdentityProvider:
        """Register a new identity provider."""
        provider_id = str(uuid.uuid4())
        provider = IdentityProvider(
            id=provider_id,
            name=name,
            type=provider_type,
            status="active",
            config=config
        )
        
        self.identity_providers[provider_id] = provider
        logger.info(f"Registered identity provider: {name} ({provider_type})")
        return provider
    
    def link_external_identity(self, user_id: str, provider_id: str, external_id: str, 
                              metadata: Dict[str, Any] = None) -> ExternalIdentity:
        """Link a user to an external identity."""
        # Check if provider exists
        if provider_id not in self.identity_providers:
            raise ValueError(f"Identity provider {provider_id} not found")
        
        # Check if link already exists
        for ext_id in self.external_identities.values():
            if ext_id.user_id == user_id and ext_id.provider_id == provider_id:
                raise ValueError(f"User {user_id} already linked to provider {provider_id}")
        
        # Create external identity
        identity_id = str(uuid.uuid4())
        external_identity = ExternalIdentity(
            id=identity_id,
            user_id=user_id,
            provider_id=provider_id,
            external_id=external_id,
            created_at=time.time(),
            last_verified_at=time.time(),
            metadata=metadata or {}
        )
        
        self.external_identities[identity_id] = external_identity
        logger.info(f"Linked user {user_id} to external identity {external_id} with provider {provider_id}")
        return external_identity
    
    def find_user_by_external_identity(self, provider_id: str, external_id: str) -> Optional[str]:
        """Find a user by their external identity."""
        for ext_id in self.external_identities.values():
            if ext_id.provider_id == provider_id and ext_id.external_id == external_id:
                logger.info(f"Found user {ext_id.user_id} by external identity {external_id}")
                return ext_id.user_id
        
        logger.info(f"No user found for external identity {external_id} with provider {provider_id}")
        return None
    
    def revoke_credential(self, credential_id: str) -> bool:
        """Revoke a credential."""
        if credential_id not in self.credentials:
            logger.error(f"Credential {credential_id} not found")
            return False
        
        credential = self.credentials[credential_id]
        credential.status = "revoked"
        logger.info(f"Revoked credential {credential_id} for user {credential.user_id}")
        return True
    
    def revoke_all_credentials(self, user_id: str, credential_type: Optional[str] = None) -> int:
        """Revoke all credentials for a user, optionally of a specific type."""
        count = 0
        for cred in self.credentials.values():
            if cred.user_id == user_id and (credential_type is None or cred.type == credential_type):
                cred.status = "revoked"
                count += 1
        
        logger.info(f"Revoked {count} credentials for user {user_id}")
        return count
    
    def get_user_credentials(self, user_id: str, active_only: bool = True) -> List[Credential]:
        """Get all credentials for a user."""
        result = []
        for cred in self.credentials.values():
            if cred.user_id == user_id and (not active_only or (cred.status == "active" and not cred.is_expired())):
                result.append(cred)
        
        return result
    
    def get_user_external_identities(self, user_id: str) -> List[ExternalIdentity]:
        """Get all external identities for a user."""
        return [ext_id for ext_id in self.external_identities.values() if ext_id.user_id == user_id]
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with the given salt."""
        return hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        ).hex()
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify a password against a hash."""
        return self._hash_password(password, salt) == password_hash
    
    def _verify_password_hash(self, password: str, password_hash: str) -> bool:
        """Verify if a password matches a hash from history."""
        # Extract salt from hash if stored together
        if ":" in password_hash:
            salt, hash_part = password_hash.split(":", 1)
            return self._hash_password(password, salt) == hash_part
        return False
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash an API key."""
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    def _verify_mfa_code(self, credential: MfaCredential, code: str) -> bool:
        """Verify an MFA code against a credential."""
        # Implementation depends on MFA type
        if credential.mfa_type == "totp":
            # TOTP verification would go here
            # For simplicity, we'll just check if code is "123456" in this example
            return code == "123456"
        elif credential.mfa_type == "sms":
            # SMS verification would go here
            return code == "123456"
        elif credential.mfa_type == "email":
            # Email verification would go here
            return code == "123456"
        
        return False
    
    def export_to_json(self, file_path: str) -> bool:
        """Export identity management configuration to a JSON file."""
        try:
            data = {
                "credentials": [cred.to_dict() for cred in self.credentials.values()],
                "identity_providers": [provider.to_dict() for provider in self.identity_providers.values()],
                "external_identities": [ext_id.to_dict() for ext_id in self.external_identities.values()],
                "password_policy": self.password_policy.to_dict()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported identity management configuration to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export identity management configuration: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """Import identity management configuration from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing data
            self.credentials = {}
            self.identity_providers = {}
            self.external_identities = {}
            
            # Import password policy
            if "password_policy" in data:
                self.password_policy = PasswordPolicy.from_dict(data["password_policy"])
            
            # Import credentials
            for cred_data in data.get("credentials", []):
                cred_type = cred_data.get("type")
                if cred_type == "password":
                    cred = PasswordCredential.from_dict(cred_data)
                elif cred_type == "api_key":
                    cred = ApiKeyCredential.from_dict(cred_data)
                elif cred_type == "mfa":
                    cred = MfaCredential.from_dict(cred_data)
                else:
                    cred = Credential.from_dict(cred_data)
                
                self.credentials[cred.id] = cred
            
            # Import identity providers
            for provider_data in data.get("identity_providers", []):
                provider = IdentityProvider.from_dict(provider_data)
                self.identity_providers[provider.id] = provider
            
            # Import external identities
            for ext_id_data in data.get("external_identities", []):
                ext_id = ExternalIdentity.from_dict(ext_id_data)
                self.external_identities[ext_id.id] = ext_id
            
            logger.info(f"Imported identity management configuration from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import identity management configuration: {e}")
            return False
