"""
Tool Manager for Lumina AI.

This module provides a central manager for integrating tools with the Lumina AI platform,
handling tool registration, execution, and permission management.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Set
import os
import json

from .registry.registry import ToolRegistry
from .interface import Tool

class ToolManager:
    """Central manager for tool integration with Lumina AI."""
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize the tool manager.
        
        Args:
            registry_path: Optional path to save/load the tool registry
        """
        self.registry = ToolRegistry()
        self.registry_path = registry_path
        self.logger = logging.getLogger("tools.manager")
        
        # Load registry if path is provided
        if registry_path and os.path.exists(registry_path):
            self.registry.load_registry(registry_path)
    
    def register_tool(self, tool: Tool, categories: List[str] = None) -> bool:
        """
        Register a tool with the manager.
        
        Args:
            tool: The tool to register
            categories: Optional list of categories to associate with the tool
            
        Returns:
            True if registration was successful, False otherwise
        """
        success = self.registry.register_tool(tool, categories)
        
        # Save registry if path is provided
        if success and self.registry_path:
            self.registry.save_registry(self.registry_path)
        
        return success
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the manager.
        
        Args:
            tool_name: The name of the tool to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        success = self.registry.unregister_tool(tool_name)
        
        # Save registry if path is provided
        if success and self.registry_path:
            self.registry.save_registry(self.registry_path)
        
        return success
    
    def discover_tools(self, package_path: str) -> int:
        """
        Discover and register tools from a package.
        
        Args:
            package_path: The path to the package to discover tools in
            
        Returns:
            Number of tools discovered and registered
        """
        count = self.registry.discover_tools(package_path)
        
        # Save registry if path is provided and tools were discovered
        if count > 0 and self.registry_path:
            self.registry.save_registry(self.registry_path)
        
        return count
    
    def execute_tool(self, 
                    tool_name: str, 
                    parameters: Dict[str, Any],
                    user_permissions: Set[str] = None) -> Dict[str, Any]:
        """
        Execute a tool with permission checking.
        
        Args:
            tool_name: The name of the tool to execute
            parameters: Dictionary of parameter values
            user_permissions: Set of permissions the user has
            
        Returns:
            Dictionary containing the execution results
        """
        # Get the tool
        tool = self.registry.get_tool(tool_name)
        
        if not tool:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not found",
                'result': None
            }
        
        # Check permissions
        if user_permissions is not None:
            required_permissions = set(tool.get_required_permissions())
            if not required_permissions.issubset(user_permissions):
                missing_permissions = required_permissions - user_permissions
                return {
                    'success': False,
                    'error': f"Missing required permissions: {', '.join(missing_permissions)}",
                    'result': None
                }
        
        # Execute the tool
        self.logger.info(f"Executing tool '{tool_name}'")
        return tool.execute(parameters)
    
    def get_available_tools(self, user_permissions: Set[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get all available tools, filtered by user permissions.
        
        Args:
            user_permissions: Optional set of permissions the user has
            
        Returns:
            Dictionary mapping tool names to tool metadata
        """
        all_tools = self.registry.get_all_tools()
        
        if user_permissions is None:
            # Return all tools if no permissions provided
            return {
                name: {
                    'name': tool.get_name(),
                    'description': tool.get_description(),
                    'parameters': tool.get_parameters(),
                    'categories': self.registry.get_tool_categories(name),
                    'required_permissions': tool.get_required_permissions()
                }
                for name, tool in all_tools.items()
            }
        
        # Filter tools by permissions
        available_tools = {}
        for name, tool in all_tools.items():
            required_permissions = set(tool.get_required_permissions())
            if required_permissions.issubset(user_permissions):
                available_tools[name] = {
                    'name': tool.get_name(),
                    'description': tool.get_description(),
                    'parameters': tool.get_parameters(),
                    'categories': self.registry.get_tool_categories(name),
                    'required_permissions': tool.get_required_permissions()
                }
        
        return available_tools
    
    def get_tools_by_category(self, category: str, user_permissions: Set[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get all tools in a category, filtered by user permissions.
        
        Args:
            category: The category to get tools for
            user_permissions: Optional set of permissions the user has
            
        Returns:
            Dictionary mapping tool names to tool metadata
        """
        category_tools = self.registry.get_tools_by_category(category)
        
        if user_permissions is None:
            # Return all category tools if no permissions provided
            return {
                name: {
                    'name': tool.get_name(),
                    'description': tool.get_description(),
                    'parameters': tool.get_parameters(),
                    'categories': self.registry.get_tool_categories(name),
                    'required_permissions': tool.get_required_permissions()
                }
                for name, tool in category_tools.items()
            }
        
        # Filter tools by permissions
        available_tools = {}
        for name, tool in category_tools.items():
            required_permissions = set(tool.get_required_permissions())
            if required_permissions.issubset(user_permissions):
                available_tools[name] = {
                    'name': tool.get_name(),
                    'description': tool.get_description(),
                    'parameters': tool.get_parameters(),
                    'categories': self.registry.get_tool_categories(name),
                    'required_permissions': tool.get_required_permissions()
                }
        
        return available_tools
    
    def get_categories(self) -> List[str]:
        """
        Get all tool categories.
        
        Returns:
            List of category names
        """
        return self.registry.get_categories()
    
    def save_registry(self) -> bool:
        """
        Save the tool registry.
        
        Returns:
            True if saving was successful, False otherwise
        """
        if not self.registry_path:
            self.logger.error("No registry path specified")
            return False
        
        return self.registry.save_registry(self.registry_path)
    
    def load_registry(self) -> bool:
        """
        Load the tool registry.
        
        Returns:
            True if loading was successful, False otherwise
        """
        if not self.registry_path:
            self.logger.error("No registry path specified")
            return False
        
        if not os.path.exists(self.registry_path):
            self.logger.error(f"Registry file not found: {self.registry_path}")
            return False
        
        return self.registry.load_registry(self.registry_path)
