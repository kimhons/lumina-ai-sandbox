"""
API Integration Tool for Lumina AI.

This module implements a tool for integrating with external APIs
and services, allowing for data retrieval and operations.
"""

import requests
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union

from ..base import BaseTool

class APIIntegrationTool(BaseTool):
    """Tool for integrating with external APIs and services."""
    
    # Tool metadata for discovery
    TOOL_METADATA = {
        'categories': ['api', 'integration', 'external']
    }
    
    def __init__(self, default_headers: Optional[Dict[str, str]] = None):
        """
        Initialize the API integration tool.
        
        Args:
            default_headers: Optional default headers to include in all requests
        """
        # Define parameters schema
        parameters_schema = {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "description": "HTTP method to use",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
                    "default": "GET"
                },
                "url": {
                    "type": "string",
                    "description": "URL to send the request to"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers to include in the request",
                    "additionalProperties": {
                        "type": "string"
                    }
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters to include in the request",
                    "additionalProperties": true
                },
                "data": {
                    "type": "object",
                    "description": "Data to include in the request body (for POST, PUT, PATCH)",
                    "additionalProperties": true
                },
                "json": {
                    "type": "boolean",
                    "description": "Whether to parse the response as JSON",
                    "default": true
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds",
                    "default": 30
                },
                "retry": {
                    "type": "integer",
                    "description": "Number of retry attempts for failed requests",
                    "default": 0
                }
            },
            "required": ["url"]
        }
        
        # Initialize base tool
        super().__init__(
            name="api_integration",
            description="Integrate with external APIs and services",
            parameters_schema=parameters_schema,
            required_permissions=["internet_access", "api_access"]
        )
        
        self.default_headers = default_headers or {}
    
    def _execute_tool(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the API request.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary containing the API response
        """
        method = parameters.get("method", "GET")
        url = parameters["url"]
        headers = {**self.default_headers, **(parameters.get("headers", {}))}
        params = parameters.get("params", {})
        data = parameters.get("data", {})
        parse_json = parameters.get("json", True)
        timeout = parameters.get("timeout", 30)
        retry_count = parameters.get("retry", 0)
        
        self.logger.info(f"Sending {method} request to {url}")
        
        # Execute request with retry logic
        response = None
        last_error = None
        
        for attempt in range(retry_count + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data if method in ["POST", "PUT", "PATCH"] else None,
                    timeout=timeout
                )
                
                # Break on successful request
                break
            
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Request failed (attempt {attempt+1}/{retry_count+1}): {e}")
                
                if attempt < retry_count:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        # Handle request failure
        if response is None:
            return {
                "success": False,
                "error": last_error or "Request failed",
                "status_code": None,
                "content": None
            }
        
        # Process response
        try:
            result = {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url
            }
            
            # Parse content based on content type
            if parse_json:
                try:
                    result["content"] = response.json()
                except ValueError:
                    result["content"] = response.text
            else:
                result["content"] = response.text
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error processing response: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": response.status_code if response else None,
                "content": None
            }
