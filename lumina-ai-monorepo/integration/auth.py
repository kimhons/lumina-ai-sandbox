import logging
import aiohttp
import json
import base64
import time
from typing import Dict, List, Any, Optional, Union
import asyncio
import ssl
import certifi

from .interfaces import (
    IntegrationSystem, AuthenticationProvider, DataTransformer,
    IntegrationEvent, IntegrationConfig
)

logger = logging.getLogger(__name__)


class BasicAuthProvider(AuthenticationProvider):
    """Basic authentication provider using username and password."""
    
    def __init__(self, username: str, password: str):
        """
        Initialize a new basic authentication provider.
        
        Args:
            username: Username for authentication
            password: Password for authentication
        """
        self.username = username
        self.password = password
        self.credentials = None
    
    async def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the external system.
        
        Returns:
            Authentication result
        """
        auth_string = f"{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.credentials = {
            "type": "basic",
            "value": encoded_auth,
            "timestamp": time.time()
        }
        
        return self.credentials
    
    async def refresh(self) -> Dict[str, Any]:
        """
        Refresh authentication credentials.
        
        Returns:
            Refresh result
        """
        # Basic auth doesn't need refreshing
        if not self.credentials:
            return await self.authenticate()
        
        return self.credentials
    
    async def revoke(self) -> bool:
        """
        Revoke authentication credentials.
        
        Returns:
            True if revocation was successful, False otherwise
        """
        self.credentials = None
        return True
    
    async def get_credentials(self) -> Dict[str, Any]:
        """
        Get current authentication credentials.
        
        Returns:
            Current credentials
        """
        if not self.credentials:
            return await self.authenticate()
        
        return self.credentials


class OAuth2Provider(AuthenticationProvider):
    """OAuth2 authentication provider."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        auth_url: str = None,
        scope: str = None,
        redirect_uri: str = None
    ):
        """
        Initialize a new OAuth2 authentication provider.
        
        Args:
            client_id: Client ID for OAuth2
            client_secret: Client secret for OAuth2
            token_url: URL for obtaining tokens
            auth_url: URL for authorization
            scope: OAuth2 scope
            redirect_uri: Redirect URI for OAuth2
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.auth_url = auth_url
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.credentials = None
    
    async def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the external system.
        
        Returns:
            Authentication result
        """
        try:
            # Client credentials flow
            async with aiohttp.ClientSession() as session:
                data = {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                if self.scope:
                    data["scope"] = self.scope
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OAuth2 authentication failed: {error_text}")
                        return {}
                    
                    result = await response.json()
                    
                    self.credentials = {
                        "type": "oauth2",
                        "access_token": result.get("access_token"),
                        "refresh_token": result.get("refresh_token"),
                        "token_type": result.get("token_type", "Bearer"),
                        "expires_in": result.get("expires_in"),
                        "timestamp": time.time()
                    }
                    
                    return self.credentials
        
        except Exception as e:
            logger.error(f"Error during OAuth2 authentication: {e}")
            return {}
    
    async def refresh(self) -> Dict[str, Any]:
        """
        Refresh authentication credentials.
        
        Returns:
            Refresh result
        """
        if not self.credentials or not self.credentials.get("refresh_token"):
            return await self.authenticate()
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.credentials["refresh_token"],
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OAuth2 token refresh failed: {error_text}")
                        return await self.authenticate()
                    
                    result = await response.json()
                    
                    self.credentials = {
                        "type": "oauth2",
                        "access_token": result.get("access_token"),
                        "refresh_token": result.get("refresh_token", self.credentials.get("refresh_token")),
                        "token_type": result.get("token_type", "Bearer"),
                        "expires_in": result.get("expires_in"),
                        "timestamp": time.time()
                    }
                    
                    return self.credentials
        
        except Exception as e:
            logger.error(f"Error during OAuth2 token refresh: {e}")
            return await self.authenticate()
    
    async def revoke(self) -> bool:
        """
        Revoke authentication credentials.
        
        Returns:
            True if revocation was successful, False otherwise
        """
        if not self.credentials:
            return True
        
        try:
            # Some OAuth2 providers have a revocation endpoint
            # This is a simplified implementation
            self.credentials = None
            return True
        
        except Exception as e:
            logger.error(f"Error during OAuth2 token revocation: {e}")
            return False
    
    async def get_credentials(self) -> Dict[str, Any]:
        """
        Get current authentication credentials.
        
        Returns:
            Current credentials
        """
        if not self.credentials:
            return await self.authenticate()
        
        # Check if token is expired
        if "expires_in" in self.credentials and "timestamp" in self.credentials:
            elapsed = time.time() - self.credentials["timestamp"]
            if elapsed >= self.credentials["expires_in"]:
                return await self.refresh()
        
        return self.credentials


class ApiKeyProvider(AuthenticationProvider):
    """API key authentication provider."""
    
    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        """
        Initialize a new API key authentication provider.
        
        Args:
            api_key: API key for authentication
            header_name: Name of the header to use for the API key
        """
        self.api_key = api_key
        self.header_name = header_name
        self.credentials = None
    
    async def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the external system.
        
        Returns:
            Authentication result
        """
        self.credentials = {
            "type": "api_key",
            "header_name": self.header_name,
            "value": self.api_key,
            "timestamp": time.time()
        }
        
        return self.credentials
    
    async def refresh(self) -> Dict[str, Any]:
        """
        Refresh authentication credentials.
        
        Returns:
            Refresh result
        """
        # API key doesn't need refreshing
        if not self.credentials:
            return await self.authenticate()
        
        return self.credentials
    
    async def revoke(self) -> bool:
        """
        Revoke authentication credentials.
        
        Returns:
            True if revocation was successful, False otherwise
        """
        self.credentials = None
        return True
    
    async def get_credentials(self) -> Dict[str, Any]:
        """
        Get current authentication credentials.
        
        Returns:
            Current credentials
        """
        if not self.credentials:
            return await self.authenticate()
        
        return self.credentials


class AuthProviderFactory:
    """Factory for creating authentication providers."""
    
    @staticmethod
    def create_provider(auth_type: str, **kwargs) -> AuthenticationProvider:
        """
        Create an authentication provider.
        
        Args:
            auth_type: Type of provider to create
            **kwargs: Additional arguments for the provider
            
        Returns:
            The created provider
            
        Raises:
            ValueError: If the provider type is not supported
        """
        if auth_type == "basic":
            username = kwargs.get("username")
            password = kwargs.get("password")
            
            if not username or not password:
                raise ValueError("username and password are required for basic auth")
            
            return BasicAuthProvider(username, password)
        
        elif auth_type == "oauth2":
            client_id = kwargs.get("client_id")
            client_secret = kwargs.get("client_secret")
            token_url = kwargs.get("token_url")
            
            if not client_id or not client_secret or not token_url:
                raise ValueError("client_id, client_secret, and token_url are required for OAuth2")
            
            return OAuth2Provider(
                client_id=client_id,
                client_secret=client_secret,
                token_url=token_url,
                auth_url=kwargs.get("auth_url"),
                scope=kwargs.get("scope"),
                redirect_uri=kwargs.get("redirect_uri")
            )
        
        elif auth_type == "api_key":
            api_key = kwargs.get("api_key")
            
            if not api_key:
                raise ValueError("api_key is required for API key auth")
            
            return ApiKeyProvider(
                api_key=api_key,
                header_name=kwargs.get("header_name", "X-API-Key")
            )
        
        else:
            raise ValueError(f"Unsupported auth provider type: {auth_type}")
