"""
Base Tool Implementation for Lumina AI.

This module provides a base implementation of the Tool interface
with common functionality for all tools.
"""

import logging
import json
import jsonschema
from typing import List, Dict, Any, Optional, Union

from .interface import Tool

class BaseTool(Tool):
    """Base implementation of the Tool interface with common functionality."""
    
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any], required_permissions: List[str] = None):
        """
        Initialize the base tool.
        
        Args:
            name: The name of the tool
            description: The description of the tool
            parameters_schema: JSON Schema for the tool parameters
            required_permissions: List of required permission identifiers
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
        self.required_permissions = required_permissions or []
        self.logger = logging.getLogger(f"tools.{name}")
    
    def get_name(self) -> str:
        """
        Get the name of the tool.
        
        Returns:
            The tool name
        """
        return self.name
    
    def get_description(self) -> str:
        """
        Get the description of the tool.
        
        Returns:
            The tool description
        """
        return self.description
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """
        Get the parameters required by the tool.
        
        Returns:
            List of parameter specifications
        """
        parameters = []
        
        if 'properties' in self.parameters_schema:
            for param_name, param_schema in self.parameters_schema['properties'].items():
                parameter = {
                    'name': param_name,
                    'type': param_schema.get('type', 'string'),
                    'description': param_schema.get('description', ''),
                    'required': param_name in self.parameters_schema.get('required', []),
                    'default': param_schema.get('default'),
                    'enum': param_schema.get('enum')
                }
                parameters.append(parameter)
        
        return parameters
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate the parameters for the tool.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            jsonschema.validate(instance=parameters, schema=self.parameters_schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Parameter validation failed: {e}")
            return False
    
    def get_required_permissions(self) -> List[str]:
        """
        Get the permissions required to use this tool.
        
        Returns:
            List of required permission identifiers
        """
        return self.required_permissions
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the provided parameters.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary containing the execution results
        """
        # Validate parameters
        if not self.validate_parameters(parameters):
            return {
                'success': False,
                'error': 'Invalid parameters',
                'result': None
            }
        
        # Execute tool-specific implementation
        try:
            result = self._execute_tool(parameters)
            return {
                'success': True,
                'error': None,
                'result': result
            }
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'result': None
            }
    
    def _execute_tool(self, parameters: Dict[str, Any]) -> Any:
        """
        Tool-specific implementation of the execution logic.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Tool-specific execution result
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _execute_tool method")
