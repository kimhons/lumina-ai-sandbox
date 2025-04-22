"""
Encryption module for Lumina AI.

This module provides encryption services for securing sensitive data
including data at rest and data in transit.
"""

import os
import base64
import json
from typing import Dict, Any, Optional, Union, Tuple
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class EncryptionManager:
    """Manages encryption for Lumina AI."""
    
    def __init__(self, 
                 master_key: Optional[str] = None,
                 persist_dir: str = "./data/encryption"):
        """
        Initialize the encryption manager.
        
        Args:
            master_key: Master encryption key (generated if not provided)
            persist_dir: Directory to persist encryption data
        """
        self.persist_dir = persist_dir
        self.master_key = master_key or os.environ.get('LUMINA_ENCRYPTION_KEY', self._generate_key())
        self.fernet = Fernet(self.master_key.encode() if isinstance(self.master_key, str) else self.master_key)
        self.logger = logging.getLogger(__name__)
        
        # Create persistence directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
    
    def encrypt_data(self, data: Union[str, bytes, Dict, list]) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string, bytes, dict, or list)
            
        Returns:
            Base64-encoded encrypted data
        """
        # Convert data to bytes if it's not already
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Encrypt the data
        encrypted_data = self.fernet.encrypt(data_bytes)
        
        # Return as base64 string
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict, list]:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Decrypted data (attempts to parse as JSON if possible)
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            
            # Decrypt the data
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                # Return as string if not valid JSON
                return decrypted_bytes.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.
        
        Args:
            input_path: Path to the file to encrypt
            output_path: Path to save the encrypted file (defaults to input_path + '.enc')
            
        Returns:
            Path to the encrypted file
        """
        if output_path is None:
            output_path = input_path + '.enc'
        
        try:
            # Read the file
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Encrypt the data
            encrypted_data = self.fernet.encrypt(data)
            
            # Write the encrypted data
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error encrypting file {input_path}: {e}")
            raise
    
    def decrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.
        
        Args:
            input_path: Path to the encrypted file
            output_path: Path to save the decrypted file (defaults to input_path without '.enc')
            
        Returns:
            Path to the decrypted file
        """
        if output_path is None:
            output_path = input_path.replace('.enc', '') if input_path.endswith('.enc') else input_path + '.dec'
        
        try:
            # Read the encrypted file
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Write the decrypted data
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error decrypting file {input_path}: {e}")
            raise
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive an encryption key from a password.
        
        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (key, salt)
        """
        # Generate salt if not provided
        if salt is None:
            salt = os.urandom(16)
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key, salt
    
    def _generate_key(self) -> str:
        """Generate a random encryption key."""
        key = Fernet.generate_key()
        
        # Save the key to a file
        key_path = os.path.join(self.persist_dir, "master_key.key")
        if not os.path.exists(key_path):
            with open(key_path, 'wb') as f:
                f.write(key)
        
        return key.decode('utf-8')
