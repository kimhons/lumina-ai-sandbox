"""
Lumina AI Security Package - Encryption Module

This module implements enhanced encryption capabilities for Lumina AI, including:
- Data encryption at rest
- Data encryption in transit
- Key management
- Secure cryptographic operations
- Encryption policy enforcement

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

import os
import base64
import json
import time
import logging
import hashlib
import secrets
import threading
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, Callable, Tuple, ByteString
from dataclasses import dataclass, field

# Import cryptography libraries
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"
    FERNET = "fernet"

class KeyType(Enum):
    """Types of encryption keys."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    MASTER = "master"
    DATA = "data"
    TRANSPORT = "transport"

@dataclass
class EncryptionKey:
    """Represents an encryption key."""
    id: str
    type: KeyType
    algorithm: EncryptionAlgorithm
    created_at: float
    expires_at: Optional[float]
    key_material: ByteString
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self, include_material: bool = False) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "type": self.type.value,
            "algorithm": self.algorithm.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata
        }
        
        if include_material:
            result["key_material"] = base64.b64encode(self.key_material).decode('utf-8')
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncryptionKey":
        """Create from dictionary."""
        key_material = base64.b64decode(data["key_material"]) if "key_material" in data else b""
        
        return cls(
            id=data["id"],
            type=KeyType(data["type"]),
            algorithm=EncryptionAlgorithm(data["algorithm"]),
            created_at=data["created_at"],
            expires_at=data.get("expires_at"),
            key_material=key_material,
            metadata=data.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """Check if the key is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

@dataclass
class EncryptedData:
    """Represents encrypted data."""
    ciphertext: ByteString
    key_id: str
    algorithm: EncryptionAlgorithm
    iv: Optional[ByteString] = None
    tag: Optional[ByteString] = None
    aad: Optional[ByteString] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "ciphertext": base64.b64encode(self.ciphertext).decode('utf-8'),
            "key_id": self.key_id,
            "algorithm": self.algorithm.value,
            "metadata": self.metadata
        }
        
        if self.iv:
            result["iv"] = base64.b64encode(self.iv).decode('utf-8')
        
        if self.tag:
            result["tag"] = base64.b64encode(self.tag).decode('utf-8')
        
        if self.aad:
            result["aad"] = base64.b64encode(self.aad).decode('utf-8')
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncryptedData":
        """Create from dictionary."""
        ciphertext = base64.b64decode(data["ciphertext"])
        iv = base64.b64decode(data["iv"]) if "iv" in data else None
        tag = base64.b64decode(data["tag"]) if "tag" in data else None
        aad = base64.b64decode(data["aad"]) if "aad" in data else None
        
        return cls(
            ciphertext=ciphertext,
            key_id=data["key_id"],
            algorithm=EncryptionAlgorithm(data["algorithm"]),
            iv=iv,
            tag=tag,
            aad=aad,
            metadata=data.get("metadata", {})
        )
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "EncryptedData":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

class KeyManager:
    """Manages encryption keys."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.keys: Dict[str, EncryptionKey] = {}
        self.storage_path = storage_path
        self.lock = threading.RLock()
        
        if storage_path:
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            self.load_keys()
    
    def generate_key(self, key_type: KeyType, algorithm: EncryptionAlgorithm, 
                    expires_in: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> EncryptionKey:
        """Generate a new encryption key."""
        with self.lock:
            key_id = secrets.token_hex(16)
            created_at = time.time()
            expires_at = created_at + expires_in if expires_in else None
            
            # Generate key material based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM or algorithm == EncryptionAlgorithm.AES_256_CBC:
                key_material = os.urandom(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_material = os.urandom(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.FERNET:
                key_material = Fernet.generate_key()
            elif algorithm == EncryptionAlgorithm.RSA_2048:
                if key_type == KeyType.ASYMMETRIC_PRIVATE:
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=2048,
                        backend=default_backend()
                    )
                    key_material = private_key.private_bytes(
                        encoding=Encoding.PEM,
                        format=PrivateFormat.PKCS8,
                        encryption_algorithm=NoEncryption()
                    )
                else:  # KeyType.ASYMMETRIC_PUBLIC
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=2048,
                        backend=default_backend()
                    )
                    public_key = private_key.public_key()
                    key_material = public_key.public_bytes(
                        encoding=Encoding.PEM,
                        format=PublicFormat.SubjectPublicKeyInfo
                    )
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                if key_type == KeyType.ASYMMETRIC_PRIVATE:
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=4096,
                        backend=default_backend()
                    )
                    key_material = private_key.private_bytes(
                        encoding=Encoding.PEM,
                        format=PrivateFormat.PKCS8,
                        encryption_algorithm=NoEncryption()
                    )
                else:  # KeyType.ASYMMETRIC_PUBLIC
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=4096,
                        backend=default_backend()
                    )
                    public_key = private_key.public_key()
                    key_material = public_key.public_bytes(
                        encoding=Encoding.PEM,
                        format=PublicFormat.SubjectPublicKeyInfo
                    )
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Create key
            key = EncryptionKey(
                id=key_id,
                type=key_type,
                algorithm=algorithm,
                created_at=created_at,
                expires_at=expires_at,
                key_material=key_material,
                metadata=metadata or {}
            )
            
            # Store key
            self.keys[key_id] = key
            self.save_keys()
            
            return key
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Get a key by ID."""
        with self.lock:
            return self.keys.get(key_id)
    
    def list_keys(self, key_type: Optional[KeyType] = None, 
                 algorithm: Optional[EncryptionAlgorithm] = None,
                 include_expired: bool = False) -> List[EncryptionKey]:
        """List keys, optionally filtered by type and algorithm."""
        with self.lock:
            keys = list(self.keys.values())
            
            # Filter by type
            if key_type:
                keys = [k for k in keys if k.type == key_type]
            
            # Filter by algorithm
            if algorithm:
                keys = [k for k in keys if k.algorithm == algorithm]
            
            # Filter out expired keys
            if not include_expired:
                keys = [k for k in keys if not k.is_expired()]
            
            return keys
    
    def delete_key(self, key_id: str) -> bool:
        """Delete a key by ID."""
        with self.lock:
            if key_id in self.keys:
                del self.keys[key_id]
                self.save_keys()
                return True
            return False
    
    def rotate_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Rotate a key by generating a new one with the same properties."""
        with self.lock:
            old_key = self.get_key(key_id)
            if not old_key:
                return None
            
            # Calculate new expiration time
            expires_in = None
            if old_key.expires_at:
                expires_in = old_key.expires_at - old_key.created_at
            
            # Generate new key
            new_key = self.generate_key(
                key_type=old_key.type,
                algorithm=old_key.algorithm,
                expires_in=expires_in,
                metadata={**old_key.metadata, "rotated_from": key_id}
            )
            
            # Update old key metadata
            old_key.metadata["rotated_to"] = new_key.id
            self.save_keys()
            
            return new_key
    
    def load_keys(self) -> None:
        """Load keys from storage."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for key_data in data:
                    key = EncryptionKey.from_dict(key_data)
                    self.keys[key.id] = key
            logger.info(f"Loaded {len(self.keys)} keys from {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to load keys from {self.storage_path}: {e}")
    
    def save_keys(self) -> None:
        """Save keys to storage."""
        if not self.storage_path:
            return
        
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([k.to_dict(include_material=True) for k in self.keys.values()], f, indent=2)
            logger.info(f"Saved {len(self.keys)} keys to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save keys to {self.storage_path}: {e}")

class EncryptionService:
    """Provides encryption and decryption services."""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
    
    def encrypt_data(self, data: Union[str, bytes], key_id: str, 
                    aad: Optional[Union[str, bytes]] = None) -> EncryptedData:
        """Encrypt data using the specified key."""
        # Get key
        key = self.key_manager.get_key(key_id)
        if not key:
            raise ValueError(f"Key not found: {key_id}")
        
        if key.is_expired():
            raise ValueError(f"Key is expired: {key_id}")
        
        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Convert AAD to bytes if it's a string
        if isinstance(aad, str):
            aad = aad.encode('utf-8')
        
        # Encrypt based on algorithm
        if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
            # Generate IV
            iv = os.urandom(12)  # 96 bits for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key.key_material),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Add AAD if provided
            if aad:
                encryptor.authenticate_additional_data(aad)
            
            # Encrypt data
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Get authentication tag
            tag = encryptor.tag
            
            return EncryptedData(
                ciphertext=ciphertext,
                key_id=key_id,
                algorithm=key.algorithm,
                iv=iv,
                tag=tag,
                aad=aad
            )
        
        elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
            # Generate IV
            iv = os.urandom(16)  # 128 bits for CBC
            
            # Pad data
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key.key_material),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt data
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            return EncryptedData(
                ciphertext=ciphertext,
                key_id=key_id,
                algorithm=key.algorithm,
                iv=iv
            )
        
        elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            # Generate nonce
            nonce = os.urandom(12)  # 96 bits for ChaCha20Poly1305
            
            # Create cipher
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            chacha = ChaCha20Poly1305(key.key_material)
            
            # Encrypt data
            ciphertext = chacha.encrypt(nonce, data, aad)
            
            return EncryptedData(
                ciphertext=ciphertext,
                key_id=key_id,
                algorithm=key.algorithm,
                iv=nonce,
                aad=aad
            )
        
        elif key.algorithm == EncryptionAlgorithm.FERNET:
            # Create Fernet cipher
            f = Fernet(key.key_material)
            
            # Encrypt data
            ciphertext = f.encrypt(data)
            
            return EncryptedData(
                ciphertext=ciphertext,
                key_id=key_id,
                algorithm=key.algorithm
            )
        
        elif key.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            if key.type != KeyType.ASYMMETRIC_PUBLIC:
                raise ValueError("RSA encryption requires a public key")
            
            # Load public key
            public_key = load_pem_public_key(key.key_material, backend=default_backend())
            
            # Encrypt data
            ciphertext = public_key.encrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return EncryptedData(
                ciphertext=ciphertext,
                key_id=key_id,
                algorithm=key.algorithm
            )
        
        else:
            raise ValueError(f"Unsupported algorithm: {key.algorithm}")
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data."""
        # Get key
        key = self.key_manager.get_key(encrypted_data.key_id)
        if not key:
            raise ValueError(f"Key not found: {encrypted_data.key_id}")
        
        if key.is_expired():
            raise ValueError(f"Key is expired: {encrypted_data.key_id}")
        
        # Decrypt based on algorithm
        if encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM:
            if not encrypted_data.iv or not encrypted_data.tag:
                raise ValueError("IV and tag are required for AES-GCM decryption")
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key.key_material),
                modes.GCM(encrypted_data.iv, encrypted_data.tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Add AAD if provided
            if encrypted_data.aad:
                decryptor.authenticate_additional_data(encrypted_data.aad)
            
            # Decrypt data
            return decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CBC:
            if not encrypted_data.iv:
                raise ValueError("IV is required for AES-CBC decryption")
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key.key_material),
                modes.CBC(encrypted_data.iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            padded_data = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
            
            # Unpad data
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            return unpadder.update(padded_data) + unpadder.finalize()
        
        elif encrypted_data.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            if not encrypted_data.iv:
                raise ValueError("Nonce is required for ChaCha20Poly1305 decryption")
            
            # Create cipher
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            chacha = ChaCha20Poly1305(key.key_material)
            
            # Decrypt data
            return chacha.decrypt(encrypted_data.iv, encrypted_data.ciphertext, encrypted_data.aad)
        
        elif encrypted_data.algorithm == EncryptionAlgorithm.FERNET:
            # Create Fernet cipher
            f = Fernet(key.key_material)
            
            # Decrypt data
            return f.decrypt(encrypted_data.ciphertext)
        
        elif encrypted_data.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            if key.type != KeyType.ASYMMETRIC_PRIVATE:
                raise ValueError("RSA decryption requires a private key")
            
            # Load private key
            private_key = load_pem_private_key(
                key.key_material,
                password=None,
                backend=default_backend()
            )
            
            # Decrypt data
            return private_key.decrypt(
                encrypted_data.ciphertext,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        
        else:
            raise ValueError(f"Unsupported algorithm: {encrypted_data.algorithm}")
    
    def encrypt_string(self, data: str, key_id: str, 
                      aad: Optional[Union[str, bytes]] = None) -> str:
        """Encrypt a string and return a JSON string representation of the encrypted data."""
        encrypted_data = self.encrypt_data(data, key_id, aad)
        return encrypted_data.to_json()
    
    def decrypt_string(self, encrypted_json: str) -> str:
        """Decrypt a JSON string representation of encrypted data and return the original string."""
        encrypted_data = EncryptedData.from_json(encrypted_json)
        decrypted_bytes = self.decrypt_data(encrypted_data)
        return decrypted_bytes.decode('utf-8')
    
    def generate_key_pair(self, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.RSA_2048,
                         expires_in: Optional[float] = None, 
                         metadata: Optional[Dict[str, Any]] = None) -> Tuple[EncryptionKey, EncryptionKey]:
        """Generate a new asymmetric key pair."""
        if algorithm not in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            raise ValueError(f"Unsupported algorithm for key pair: {algorithm}")
        
        # Generate private key
        private_key = self.key_manager.generate_key(
            key_type=KeyType.ASYMMETRIC_PRIVATE,
            algorithm=algorithm,
            expires_in=expires_in,
            metadata=metadata
        )
        
        # Load private key
        rsa_private_key = load_pem_private_key(
            private_key.key_material,
            password=None,
            backend=default_backend()
        )
        
        # Extract public key
        rsa_public_key = rsa_private_key.public_key()
        public_key_material = rsa_public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        
        # Create public key
        public_key = EncryptionKey(
            id=f"{private_key.id}.pub",
            type=KeyType.ASYMMETRIC_PUBLIC,
            algorithm=algorithm,
            created_at=private_key.created_at,
            expires_at=private_key.expires_at,
            key_material=public_key_material,
            metadata={**private_key.metadata, "private_key_id": private_key.id}
        )
        
        # Store public key
        self.key_manager.keys[public_key.id] = public_key
        self.key_manager.save_keys()
        
        # Update private key metadata
        private_key.metadata["public_key_id"] = public_key.id
        self.key_manager.save_keys()
        
        return private_key, public_key
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """Hash data using the specified algorithm."""
        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Hash data
        if algorithm == 'sha256':
            digest = hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            digest = hashlib.sha512(data).hexdigest()
        elif algorithm == 'md5':
            digest = hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        return digest
    
    def generate_hmac(self, data: Union[str, bytes], key_id: str, 
                     algorithm: str = 'sha256') -> str:
        """Generate an HMAC for the data using the specified key."""
        # Get key
        key = self.key_manager.get_key(key_id)
        if not key:
            raise ValueError(f"Key not found: {key_id}")
        
        if key.is_expired():
            raise ValueError(f"Key is expired: {key_id}")
        
        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Create HMAC
        if algorithm == 'sha256':
            h = hmac.HMAC(key.key_material, hashes.SHA256(), backend=default_backend())
        elif algorithm == 'sha512':
            h = hmac.HMAC(key.key_material, hashes.SHA512(), backend=default_backend())
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        h.update(data)
        return h.finalize().hex()
    
    def verify_hmac(self, data: Union[str, bytes], signature: str, key_id: str,
                   algorithm: str = 'sha256') -> bool:
        """Verify an HMAC signature for the data using the specified key."""
        # Get key
        key = self.key_manager.get_key(key_id)
        if not key:
            raise ValueError(f"Key not found: {key_id}")
        
        if key.is_expired():
            raise ValueError(f"Key is expired: {key_id}")
        
        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Convert signature from hex to bytes
        signature_bytes = bytes.fromhex(signature)
        
        # Create HMAC
        if algorithm == 'sha256':
            h = hmac.HMAC(key.key_material, hashes.SHA256(), backend=default_backend())
        elif algorithm == 'sha512':
            h = hmac.HMAC(key.key_material, hashes.SHA512(), backend=default_backend())
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        h.update(data)
        
        # Verify signature
        try:
            h.verify(signature_bytes)
            return True
        except Exception:
            return False

class EncryptionPolicy:
    """Defines encryption policies for different types of data."""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
        self.policies: Dict[str, Dict[str, Any]] = {}
    
    def define_policy(self, data_type: str, algorithm: EncryptionAlgorithm,
                     key_type: KeyType, key_rotation_days: Optional[int] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """Define an encryption policy for a data type."""
        self.policies[data_type] = {
            "algorithm": algorithm,
            "key_type": key_type,
            "key_rotation_days": key_rotation_days,
            "metadata": metadata or {}
        }
        logger.info(f"Defined encryption policy for {data_type}")
    
    def get_policy(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Get the encryption policy for a data type."""
        return self.policies.get(data_type)
    
    def get_or_create_key(self, data_type: str) -> str:
        """Get or create a key for the specified data type according to policy."""
        policy = self.get_policy(data_type)
        if not policy:
            raise ValueError(f"No encryption policy defined for {data_type}")
        
        # Check for existing keys
        key_manager = self.encryption_service.key_manager
        keys = key_manager.list_keys(
            key_type=policy["key_type"],
            algorithm=policy["algorithm"]
        )
        
        # Filter keys by data type in metadata
        keys = [k for k in keys if k.metadata.get("data_type") == data_type]
        
        # If keys exist, use the newest one
        if keys:
            keys.sort(key=lambda k: k.created_at, reverse=True)
            key = keys[0]
            
            # Check if key rotation is needed
            if policy["key_rotation_days"] and key.created_at + (policy["key_rotation_days"] * 24 * 60 * 60) < time.time():
                # Rotate key
                logger.info(f"Rotating key for {data_type} due to rotation policy")
                new_key = key_manager.rotate_key(key.id)
                if new_key:
                    return new_key.id
            
            return key.id
        
        # No keys exist, create a new one
        metadata = {**policy["metadata"], "data_type": data_type}
        expires_in = policy["key_rotation_days"] * 24 * 60 * 60 if policy["key_rotation_days"] else None
        
        key = key_manager.generate_key(
            key_type=policy["key_type"],
            algorithm=policy["algorithm"],
            expires_in=expires_in,
            metadata=metadata
        )
        
        return key.id
    
    def encrypt_data_by_type(self, data: Union[str, bytes], data_type: str,
                            aad: Optional[Union[str, bytes]] = None) -> EncryptedData:
        """Encrypt data according to the policy for its type."""
        key_id = self.get_or_create_key(data_type)
        return self.encryption_service.encrypt_data(data, key_id, aad)
    
    def encrypt_string_by_type(self, data: str, data_type: str,
                              aad: Optional[Union[str, bytes]] = None) -> str:
        """Encrypt a string according to the policy for its type."""
        key_id = self.get_or_create_key(data_type)
        return self.encryption_service.encrypt_string(data, key_id, aad)

class TransportEncryption:
    """Provides encryption for data in transit."""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
    
    def establish_session(self, client_public_key_pem: str) -> Tuple[str, str]:
        """Establish a secure session with a client."""
        # Generate a session key
        session_key = self.encryption_service.key_manager.generate_key(
            key_type=KeyType.SYMMETRIC,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            expires_in=24 * 60 * 60,  # 24 hours
            metadata={"purpose": "transport"}
        )
        
        # Load client public key
        client_public_key = load_pem_public_key(
            client_public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        # Encrypt session key with client public key
        encrypted_key = client_public_key.encrypt(
            session_key.key_material,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Return session ID and encrypted key
        return session_key.id, base64.b64encode(encrypted_key).decode('utf-8')
    
    def encrypt_message(self, session_id: str, message: Union[str, bytes],
                       aad: Optional[Union[str, bytes]] = None) -> str:
        """Encrypt a message for transport using the session key."""
        encrypted_data = self.encryption_service.encrypt_data(message, session_id, aad)
        return encrypted_data.to_json()
    
    def decrypt_message(self, session_id: str, encrypted_message: str) -> bytes:
        """Decrypt a message received via transport."""
        encrypted_data = EncryptedData.from_json(encrypted_message)
        if encrypted_data.key_id != session_id:
            raise ValueError(f"Message was not encrypted with session key {session_id}")
        
        return self.encryption_service.decrypt_data(encrypted_data)
    
    def close_session(self, session_id: str) -> bool:
        """Close a secure session by deleting the session key."""
        return self.encryption_service.key_manager.delete_key(session_id)

# Initialize encryption system
def initialize_encryption_system(storage_path: Optional[str] = None) -> Tuple[KeyManager, EncryptionService, EncryptionPolicy, TransportEncryption]:
    """Initialize the encryption system."""
    # Create key manager
    key_manager = KeyManager(storage_path)
    
    # Create encryption service
    encryption_service = EncryptionService(key_manager)
    
    # Create encryption policy
    policy = EncryptionPolicy(encryption_service)
    
    # Define default policies
    policy.define_policy(
        data_type="user_data",
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_type=KeyType.SYMMETRIC,
        key_rotation_days=90,
        metadata={"sensitivity": "high"}
    )
    
    policy.define_policy(
        data_type="system_data",
        algorithm=EncryptionAlgorithm.AES_256_CBC,
        key_type=KeyType.SYMMETRIC,
        key_rotation_days=180,
        metadata={"sensitivity": "medium"}
    )
    
    policy.define_policy(
        data_type="configuration",
        algorithm=EncryptionAlgorithm.FERNET,
        key_type=KeyType.SYMMETRIC,
        key_rotation_days=365,
        metadata={"sensitivity": "low"}
    )
    
    # Create transport encryption
    transport = TransportEncryption(encryption_service)
    
    return key_manager, encryption_service, policy, transport
