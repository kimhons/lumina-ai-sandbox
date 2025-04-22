"""
Lumina AI Security Package - Authentication Module

This module implements authentication for Lumina AI, including:
- Multi-factor authentication
- Single sign-on
- JWT token management
- Session management
- Authentication policies

Copyright (c) 2025 AlienNova Technologies. All rights reserved.
"""

import uuid
import time
import json
import logging
import hashlib
import secrets
import base64
import jwt
from typing import Dict, List, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuthenticationPolicy:
    """Defines authentication requirements and policies."""
    id: str
    name: str
    description: str
    require_mfa: bool = False
    allowed_auth_methods: List[str] = field(default_factory=lambda: ["password"])
    session_timeout_minutes: int = 60
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    ip_restriction: List[str] = field(default_factory=list)
    device_restriction: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert authentication policy to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "require_mfa": self.require_mfa,
            "allowed_auth_methods": self.allowed_auth_methods,
            "session_timeout_minutes": self.session_timeout_minutes,
            "max_failed_attempts": self.max_failed_attempts,
            "lockout_duration_minutes": self.lockout_duration_minutes,
            "ip_restriction": self.ip_restriction,
            "device_restriction": self.device_restriction
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthenticationPolicy":
        """Create authentication policy from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            require_mfa=data.get("require_mfa", False),
            allowed_auth_methods=data.get("allowed_auth_methods", ["password"]),
            session_timeout_minutes=data.get("session_timeout_minutes", 60),
            max_failed_attempts=data.get("max_failed_attempts", 5),
            lockout_duration_minutes=data.get("lockout_duration_minutes", 30),
            ip_restriction=data.get("ip_restriction", []),
            device_restriction=data.get("device_restriction", [])
        )

@dataclass
class Session:
    """Represents a user session."""
    id: str
    user_id: str
    created_at: float
    expires_at: float
    last_activity_at: float
    ip_address: str
    user_agent: str
    mfa_verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the session is expired."""
        return time.time() > self.expires_at
    
    def is_active(self) -> bool:
        """Check if the session is active."""
        return not self.is_expired()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_activity_at": self.last_activity_at,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "mfa_verified": self.mfa_verified,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            last_activity_at=data["last_activity_at"],
            ip_address=data["ip_address"],
            user_agent=data["user_agent"],
            mfa_verified=data.get("mfa_verified", False),
            metadata=data.get("metadata", {})
        )

@dataclass
class FailedLoginAttempt:
    """Represents a failed login attempt."""
    id: str
    user_id: str
    timestamp: float
    ip_address: str
    user_agent: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert failed login attempt to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailedLoginAttempt":
        """Create failed login attempt from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            timestamp=data["timestamp"],
            ip_address=data["ip_address"],
            user_agent=data["user_agent"]
        )

class JwtManager:
    """Manages JWT token generation and validation."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", token_lifetime_minutes: int = 60):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_lifetime_minutes = token_lifetime_minutes
    
    def generate_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate a JWT token for a user."""
        now = int(time.time())
        expiry = now + (self.token_lifetime_minutes * 60)
        
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expiry
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Generated JWT token for user {user_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and return its payload if valid."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.info(f"Validated JWT token for user {payload.get('sub')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

class AuthenticationService:
    """Service for authenticating users."""
    
    def __init__(self, identity_service, jwt_secret_key: str):
        self.identity_service = identity_service
        self.jwt_manager = JwtManager(jwt_secret_key)
        self.sessions: Dict[str, Session] = {}
        self.failed_attempts: Dict[str, List[FailedLoginAttempt]] = {}
        self.auth_policies: Dict[str, AuthenticationPolicy] = {}
        self.default_policy_id: Optional[str] = None
    
    def create_auth_policy(self, name: str, description: str, **kwargs) -> AuthenticationPolicy:
        """Create a new authentication policy."""
        policy_id = str(uuid.uuid4())
        policy = AuthenticationPolicy(
            id=policy_id,
            name=name,
            description=description,
            **kwargs
        )
        
        self.auth_policies[policy_id] = policy
        
        # Set as default if it's the first policy
        if not self.default_policy_id:
            self.default_policy_id = policy_id
        
        logger.info(f"Created authentication policy: {name}")
        return policy
    
    def set_default_policy(self, policy_id: str) -> bool:
        """Set the default authentication policy."""
        if policy_id not in self.auth_policies:
            logger.error(f"Authentication policy {policy_id} not found")
            return False
        
        self.default_policy_id = policy_id
        logger.info(f"Set default authentication policy to {policy_id}")
        return True
    
    def get_policy(self, policy_id: Optional[str] = None) -> Optional[AuthenticationPolicy]:
        """Get an authentication policy by ID, or the default policy if no ID is provided."""
        if policy_id:
            return self.auth_policies.get(policy_id)
        elif self.default_policy_id:
            return self.auth_policies.get(self.default_policy_id)
        return None
    
    def authenticate_password(self, username: str, password: str, ip_address: str, user_agent: str, 
                             policy_id: Optional[str] = None) -> Optional[str]:
        """Authenticate a user with username and password."""
        # Get authentication policy
        policy = self.get_policy(policy_id)
        if not policy:
            logger.error("No authentication policy available")
            return None
        
        # Check if password authentication is allowed
        if "password" not in policy.allowed_auth_methods:
            logger.warning(f"Password authentication not allowed by policy {policy.name}")
            return None
        
        # Check IP restrictions
        if policy.ip_restriction and ip_address not in policy.ip_restriction:
            logger.warning(f"IP address {ip_address} not allowed by policy {policy.name}")
            return None
        
        # Check device restrictions
        if policy.device_restriction and not any(device in user_agent for device in policy.device_restriction):
            logger.warning(f"User agent {user_agent} not allowed by policy {policy.name}")
            return None
        
        # Find user by username
        # Note: In a real implementation, you would have a user service to look up users by username
        # For this example, we'll assume the username is the user_id
        user_id = username
        
        # Check if account is locked
        if self.is_account_locked(user_id, policy):
            logger.warning(f"Account {user_id} is locked due to too many failed attempts")
            return None
        
        # Verify password
        if not self.identity_service.verify_password(user_id, password):
            # Record failed attempt
            self.record_failed_attempt(user_id, ip_address, user_agent)
            logger.warning(f"Password authentication failed for user {user_id}")
            return None
        
        # Create session
        session_id = self.create_session(user_id, ip_address, user_agent, policy)
        
        # Clear failed attempts on successful login
        if user_id in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        logger.info(f"Password authentication successful for user {user_id}")
        return session_id
    
    def authenticate_api_key(self, api_key: str, ip_address: str, user_agent: str,
                            policy_id: Optional[str] = None) -> Optional[str]:
        """Authenticate a user with an API key."""
        # Get authentication policy
        policy = self.get_policy(policy_id)
        if not policy:
            logger.error("No authentication policy available")
            return None
        
        # Check if API key authentication is allowed
        if "api_key" not in policy.allowed_auth_methods:
            logger.warning(f"API key authentication not allowed by policy {policy.name}")
            return None
        
        # Check IP restrictions
        if policy.ip_restriction and ip_address not in policy.ip_restriction:
            logger.warning(f"IP address {ip_address} not allowed by policy {policy.name}")
            return None
        
        # Verify API key
        user_id = self.identity_service.verify_api_key(api_key)
        if not user_id:
            logger.warning("API key authentication failed")
            return None
        
        # Create session
        session_id = self.create_session(user_id, ip_address, user_agent, policy)
        
        logger.info(f"API key authentication successful for user {user_id}")
        return session_id
    
    def verify_mfa(self, session_id: str, mfa_type: str, code: str) -> bool:
        """Verify MFA for a session."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.is_active():
            logger.warning(f"Session {session_id} is expired")
            return False
        
        # Verify MFA code
        if not self.identity_service.verify_mfa(session.user_id, mfa_type, code):
            logger.warning(f"MFA verification failed for user {session.user_id}")
            return False
        
        # Mark session as MFA verified
        session.mfa_verified = True
        logger.info(f"MFA verified for user {session.user_id}")
        return True
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str, 
                      policy: AuthenticationPolicy) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        now = time.time()
        
        session = Session(
            id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + (policy.session_timeout_minutes * 60),
            last_activity_at=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=not policy.require_mfa  # If MFA is not required, mark as verified
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def validate_session(self, session_id: str, require_mfa: bool = False) -> Optional[str]:
        """Validate a session and return the user ID if valid."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.is_active():
            logger.warning(f"Session {session_id} is expired")
            return None
        
        # Check if MFA is required and verified
        if require_mfa and not session.mfa_verified:
            logger.warning(f"MFA required but not verified for session {session_id}")
            return None
        
        # Update last activity
        session.last_activity_at = time.time()
        
        logger.info(f"Session {session_id} validated for user {session.user_id}")
        return session.user_id
    
    def extend_session(self, session_id: str, minutes: int) -> bool:
        """Extend the expiration time of a session."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.is_active():
            logger.warning(f"Cannot extend expired session {session_id}")
            return False
        
        # Extend expiration
        session.expires_at = time.time() + (minutes * 60)
        logger.info(f"Extended session {session_id} by {minutes} minutes")
        return True
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        # Remove session
        session = self.sessions.pop(session_id)
        logger.info(f"Invalidated session {session_id} for user {session.user_id}")
        return True
    
    def invalidate_all_sessions(self, user_id: str) -> int:
        """Invalidate all sessions for a user."""
        count = 0
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.user_id == user_id:
                sessions_to_remove.append(session_id)
                count += 1
        
        for session_id in sessions_to_remove:
            self.sessions.pop(session_id)
        
        logger.info(f"Invalidated {count} sessions for user {user_id}")
        return count
    
    def generate_jwt(self, session_id: str) -> Optional[str]:
        """Generate a JWT token for a session."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.is_active():
            logger.warning(f"Cannot generate JWT for expired session {session_id}")
            return None
        
        # Generate token
        additional_claims = {
            "session_id": session_id,
            "mfa_verified": session.mfa_verified
        }
        
        token = self.jwt_manager.generate_token(session.user_id, additional_claims)
        logger.info(f"Generated JWT token for session {session_id}")
        return token
    
    def validate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and return its payload if valid."""
        payload = self.jwt_manager.validate_token(token)
        if not payload:
            return None
        
        # Check if session still exists and is valid
        session_id = payload.get("session_id")
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_active():
                logger.warning(f"JWT references expired session {session_id}")
                return None
            
            # Update session last activity
            session.last_activity_at = time.time()
        
        logger.info(f"Validated JWT token for user {payload.get('sub')}")
        return payload
    
    def record_failed_attempt(self, user_id: str, ip_address: str, user_agent: str) -> None:
        """Record a failed login attempt."""
        attempt_id = str(uuid.uuid4())
        attempt = FailedLoginAttempt(
            id=attempt_id,
            user_id=user_id,
            timestamp=time.time(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(attempt)
        logger.info(f"Recorded failed login attempt for user {user_id}")
    
    def is_account_locked(self, user_id: str, policy: AuthenticationPolicy) -> bool:
        """Check if an account is locked due to too many failed attempts."""
        if user_id not in self.failed_attempts:
            return False
        
        # Get recent failed attempts within lockout window
        recent_attempts = []
        lockout_window = time.time() - (policy.lockout_duration_minutes * 60)
        
        for attempt in self.failed_attempts[user_id]:
            if attempt.timestamp > lockout_window:
                recent_attempts.append(attempt)
        
        # Update failed attempts list to only include recent ones
        self.failed_attempts[user_id] = recent_attempts
        
        # Check if number of recent attempts exceeds threshold
        return len(recent_attempts) >= policy.max_failed_attempts
    
    def get_active_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        """Get all active sessions, optionally filtered by user ID."""
        active_sessions = []
        
        for session in self.sessions.values():
            if session.is_active() and (user_id is None or session.user_id == user_id):
                active_sessions.append(session)
        
        return active_sessions
    
    def export_to_json(self, file_path: str) -> bool:
        """Export authentication configuration to a JSON file."""
        try:
            data = {
                "auth_policies": [policy.to_dict() for policy in self.auth_policies.values()],
                "default_policy_id": self.default_policy_id,
                "sessions": [session.to_dict() for session in self.sessions.values()],
                "failed_attempts": {
                    user_id: [attempt.to_dict() for attempt in attempts]
                    for user_id, attempts in self.failed_attempts.items()
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported authentication configuration to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export authentication configuration: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """Import authentication configuration from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing data
            self.auth_policies = {}
            self.sessions = {}
            self.failed_attempts = {}
            
            # Import authentication policies
            for policy_data in data.get("auth_policies", []):
                policy = AuthenticationPolicy.from_dict(policy_data)
                self.auth_policies[policy.id] = policy
            
            # Import default policy ID
            self.default_policy_id = data.get("default_policy_id")
            
            # Import sessions
            for session_data in data.get("sessions", []):
                session = Session.from_dict(session_data)
                self.sessions[session.id] = session
            
            # Import failed attempts
            for user_id, attempts_data in data.get("failed_attempts", {}).items():
                self.failed_attempts[user_id] = [
                    FailedLoginAttempt.from_dict(attempt_data)
                    for attempt_data in attempts_data
                ]
            
            logger.info(f"Imported authentication configuration from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import authentication configuration: {e}")
            return False
