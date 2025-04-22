"""
Tool Registry for Lumina AI.

This module provides a registry for managing and accessing tools
that can be integrated with Lumina AI.
"""

import logging
from typing import List, Dict, Any, Optional, Type, Set
import importlib
import inspect
import os
import json
import pkgutil

from ..interface import Tool
from ..base import BaseTool

class ToolRegistry:
    """Registry for managing and accessing tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {}  # name -> tool instance
        self.categories = {}  # category -> set of tool names
        self.logger = logging.getLogger("tools.registry")
    
    def register_tool(self, tool: Tool, categories: List[str] = None) -> bool:
        """
        Register a tool with the registry.
        
        Args:
            tool: The tool to register
            categories: Optional list of categories to associate with the tool
            
        Returns:
            True if registration was successful, False otherwise
        """
        tool_name = tool.get_name()
        
        if tool_name in self.tools:
            self.logger.warning(f"Tool '{tool_name}' is already registered. Overwriting.")
        
        self.tools[tool_name] = tool
        
        # Register categories
        if categories:
            for category in categories:
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].add(tool_name)
        
        self.logger.info(f"Registered tool '{tool_name}'")
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_name: The name of the tool to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if tool_name not in self.tools:
            self.logger.warning(f"Tool '{tool_name}' is not registered")
            return False
        
        # Remove from tools
        del self.tools[tool_name]
        
        # Remove from categories
        for category, tools in self.categories.items():
            if tool_name in tools:
                tools.remove(tool_name)
        
        self.logger.info(f"Unregistered tool '{tool_name}'")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: The name of the tool to get
            
        Returns:
            The tool instance, or None if not found
        """
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """
        Get all registered tools.
        
        Returns:
            Dictionary mapping tool names to tool instances
        """
        return self.tools.copy()
    
    def get_tools_by_category(self, category: str) -> Dict[str, Tool]:
        """
        Get all tools in a category.
        
        Args:
            category: The category to get tools for
            
        Returns:
            Dictionary mapping tool names to tool instances
        """
        if category not in self.categories:
            return {}
        
        return {name: self.tools[name] for name in self.categories[category] if name in self.tools}
    
    def get_categories(self) -> List[str]:
        """
        Get all categories.
        
        Returns:
            List of category names
        """
        return list(self.categories.keys())
    
    def get_tool_categories(self, tool_name: str) -> List[str]:
        """
        Get the categories a tool belongs to.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            List of category names
        """
        return [category for category, tools in self.categories.items() if tool_name in tools]
    
    def discover_tools(self, package_path: str) -> int:
        """
        Discover and register tools from a package.
        
        Args:
            package_path: The path to the package to discover tools in
            
        Returns:
            Number of tools discovered and registered
        """
        count = 0
        
        try:
            # Import the package
            package_name = os.path.basename(package_path)
            spec = importlib.util.spec_from_file_location(package_name, os.path.join(package_path, "__init__.py"))
            if not spec or not spec.loader:
                self.logger.error(f"Could not load package from {package_path}")
                return 0
            
            package = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(package)
            
            # Walk through the package
            for _, name, is_pkg in pkgutil.iter_modules([package_path]):
                if is_pkg:
                    # Recursively discover tools in subpackages
                    count += self.discover_tools(os.path.join(package_path, name))
                else:
                    # Import the module
                    module_name = f"{package_name}.{name}"
                    module_path = os.path.join(package_path, f"{name}.py")
                    
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if not spec or not spec.loader:
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find tool classes
                    for item_name, item in inspect.getmembers(module):
                        if (inspect.isclass(item) and 
                            issubclass(item, Tool) and 
                            item != Tool and 
                            item != BaseTool):
                            
                            try:
                                # Check if the class has metadata
                                if hasattr(item, 'TOOL_METADATA'):
                                    metadata = getattr(item, 'TOOL_METADATA')
                                    categories = metadata.get('categories', [])
                                    
                                    # Instantiate and register the tool
                                    tool = item()
                                    if self.register_tool(tool, categories):
                                        count += 1
                            except Exception as e:
                                self.logger.error(f"Error registering tool {item_name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error discovering tools in {package_path}: {e}")
        
        return count
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name.
        
        Args:
            tool_name: The name of the tool to execute
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary containing the execution results
        """
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not found",
                'result': None
            }
        
        return tool.execute(parameters)
    
    def save_registry(self, file_path: str) -> bool:
        """
        Save the registry to a file.
        
        Args:
            file_path: The path to save the registry to
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Create a serializable representation
            registry_data = {
                'tools': {},
                'categories': {category: list(tools) for category, tools in self.categories.items()}
            }
            
            # We can't serialize the actual tool objects, so just save their metadata
            for name, tool in self.tools.items():
                registry_data['tools'][name] = {
                    'name': tool.get_name(),
                    'description': tool.get_description(),
                    'parameters': tool.get_parameters(),
                    'required_permissions': tool.get_required_permissions()
                }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            self.logger.info(f"Saved registry to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving registry: {e}")
            return False
    
    def load_registry(self, file_path: str) -> bool:
        """
        Load the registry from a file.
        
        Note: This only loads the category information, not the actual tool instances.
        Tools must be registered separately.
        
        Args:
            file_path: The path to load the registry from
            
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            # Load from file
            with open(file_path, 'r') as f:
                registry_data = json.load(f)
            
            # Load categories
            self.categories = {category: set(tools) for category, tools in registry_data.get('categories', {}).items()}
            
            self.logger.info(f"Loaded registry from {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading registry: {e}")
            return False
