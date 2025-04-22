"""
Authentication module for Lumina AI.

This module provides authentication services including user management,
token generation, and session handling.
"""

import os
import time
import json
import uuid
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime, timedelta

class AuthManager:
    """Manages authentication for Lumina AI."""
    
    def __init__(self, 
                 secret_key: Optional[str] = None, 
                 token_expiry: int = 86400,
                 persist_dir: str = "./data/auth"):
        """
        Initialize the authentication manager.
        
        Args:
            secret_key: Secret key for token signing (generated if not provided)
            token_expiry: Token expiry time in seconds (default: 24 hours)
            persist_dir: Directory to persist authentication data
        """
        self.secret_key = secret_key or os.environ.get('LUMINA_AUTH_SECRET', self._generate_secret())
        self.token_expiry = token_expiry
        self.persist_dir = persist_dir
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create persistence directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Load existing data if available
        self._load()
    
    def register_user(self, 
                      username: str, 
                      password: str, 
                      email: str,
                      role: str = "user",
                      metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Password
            email: Email address
            role: User role (default: "user")
            metadata: Additional user metadata
            
        Returns:
            Tuple of (success, message)
        """
        # Check if username already exists
        if username in self.users:
            return False, "Username already exists"
        
        # Hash the password
        password_hash, salt = self._hash_password(password)
        
        # Create user record
        user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
            "created_at": time.time(),
            "last_login": None,
            "metadata": metadata or {},
            "active": True
        }
        
        # Add to users
        self.users[username] = user
        
        # Persist changes
        self._save()
        
        return True, "User registered successfully"
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str], str]:
        """
        Authenticate a user and generate a session token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, token, message)
        """
        # Check if user exists
        user = self.users.get(username)
        if not user:
            return False, None, "Invalid username or password"
        
        # Check if user is active
        if not user.get("active", True):
            return False, None, "Account is inactive"
        
        # Verify password
        if not self._verify_password(password, user["password_hash"], user["salt"]):
            return False, None, "Invalid username or password"
        
        # Generate token
        token = self._generate_token(username)
        
        # Update last login
        user["last_login"] = time.time()
        
        # Create session
        session = {
            "token": token,
            "username": username,
            "created_at": time.time(),
            "expires_at": time.time() + self.token_expiry,
            "ip_address": None,  # Would be set in a real implementation
            "user_agent": None   # Would be set in a real implementation
        }
        
        # Add to sessions
        self.sessions[token] = session
        
        # Persist changes
        self._save()
        
        return True, token, "Authentication successful"
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[str], str]:
        """
        Validate a session token.
        
        Args:
            token: Session token
            
        Returns:
            Tuple of (valid, username, message)
        """
        # Check if token exists
        session = self.sessions.get(token)
        if not session:
            return False, None, "Invalid token"
        
        # Check if token has expired
        if session["expires_at"] < time.time():
            # Clean up expired session
            del self.sessions[token]
            self._save()
            return False, None, "Token expired"
        
        # Check if user still exists and is active
        username = session["username"]
        user = self.users.get(username)
        if not user or not user.get("active", True):
            # Clean up invalid session
            del self.sessions[token]
            self._save()
            return False, None, "User inactive or deleted"
        
        return True, username, "Token valid"
    
    def invalidate_token(self, token: str) -> bool:
        """
        Invalidate a session token (logout).
        
        Args:
            token: Session token
            
        Returns:
            True if token was invalidated, False if not found
        """
        if token in self.sessions:
            del self.sessions[token]
            self._save()
            return True
        return False
    
    def invalidate_all_user_tokens(self, username: str) -> int:
        """
        Invalidate all tokens for a specific user.
        
        Args:
            username: Username
            
        Returns:
            Number of tokens invalidated
        """
        count = 0
        tokens_to_remove = []
        
        for token, session in self.sessions.items():
            if session["username"] == username:
                tokens_to_remove.append(token)
                count += 1
        
        for token in tokens_to_remove:
            del self.sessions[token]
        
        if count > 0:
            self._save()
        
        return count
    
    def update_user(self, 
                    username: str, 
                    updates: Dict[str, Any],
                    admin_override: bool = False) -> Tuple[bool, str]:
        """
        Update user information.
        
        Args:
            username: Username
            updates: Dictionary of updates to apply
            admin_override: Whether this is an admin operation
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        user = self.users.get(username)
        if not user:
            return False, "User not found"
        
        # Apply updates
        for key, value in updates.items():
            # Don't allow updating certain fields directly
            if key in ["password_hash", "salt", "created_at"] and not admin_override:
                continue
            
            # Special handling for password
            if key == "password":
                password_hash, salt = self._hash_password(value)
                user["password_hash"] = password_hash
                user["salt"] = salt
            else:
                user[key] = value
        
        # Persist changes
        self._save()
        
        return True, "User updated successfully"
    
    def deactivate_user(self, username: str) -> Tuple[bool, str]:
        """
        Deactivate a user account.
        
        Args:
            username: Username
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        user = self.users.get(username)
        if not user:
            return False, "User not found"
        
        # Deactivate user
        user["active"] = False
        
        # Invalidate all sessions
        self.invalidate_all_user_tokens(username)
        
        # Persist changes
        self._save()
        
        return True, "User deactivated successfully"
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash a password with a random salt.
        
        Args:
            password: Password to hash
            
        Returns:
            Tuple of (password_hash, salt)
        """
        # Generate a random salt
        salt = base64.b64encode(os.urandom(32)).decode('utf-8')
        
        # Hash the password with the salt
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # Number of iterations
        )
        
        # Convert to base64 for storage
        password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
        
        return password_hash_b64, salt
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: Password to verify
            password_hash: Stored password hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        # Hash the provided password with the same salt
        test_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # Number of iterations
        )
        
        # Convert to base64 for comparison
        test_hash_b64 = base64.b64encode(test_hash).decode('utf-8')
        
        # Compare hashes
        return hmac.compare_digest(test_hash_b64, password_hash)
    
    def _generate_token(self, username: str) -> str:
        """
        Generate a secure session token.
        
        Args:
            username: Username
            
        Returns:
            Session token
        """
        # Generate a random token
        token_data = os.urandom(32)
        
        # Add timestamp and username for uniqueness
        timestamp = str(time.time()).encode('utf-8')
        username_bytes = username.encode('utf-8')
        
        # Combine data
        combined = token_data + timestamp + username_bytes
        
        # Sign the token with HMAC
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            combined,
            hashlib.sha256
        ).digest()
        
        # Combine signature and data, encode as base64
        token = base64.urlsafe_b64encode(signature + combined).decode('utf-8')
        
        # Make it a bit shorter but still secure
        return token[:64]
    
    def _generate_secret(self) -> str:
        """Generate a random secret key."""
        return base64.b64encode(os.urandom(32)).decode('utf-8')
    
    def _save(self) -> None:
        """Save authentication data to disk."""
        # Save users
        with open(os.path.join(self.persist_dir, "users.json"), "w") as f:
            json.dump(self.users, f)
        
        # Save sessions
        with open(os.path.join(self.persist_dir, "sessions.json"), "w") as f:
            json.dump(self.sessions, f)
    
    def _load(self) -> None:
        """Load authentication data from disk."""
        try:
            # Load users
            users_path = os.path.join(self.persist_dir, "users.json")
            if os.path.exists(users_path):
                with open(users_path, "r") as f:
                    self.users = json.load(f)
            
            # Load sessions
            sessions_path = os.path.join(self.persist_dir, "sessions.json")
            if os.path.exists(sessions_path):
                with open(sessions_path, "r") as f:
                    self.sessions = json.load(f)
                
                # Clean up expired sessions
                now = time.time()
                expired = [token for token, session in self.sessions.items() 
                          if session["expires_at"] < now]
                
                for token in expired:
                    del self.sessions[token]
                
                if expired:
                    self._save()
        except Exception as e:
            self.logger.error(f"Error loading authentication data: {e}")
