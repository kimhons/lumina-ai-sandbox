"""
Tool Registry module for Lumina AI's Expanded Tool Ecosystem.

This module provides a central registry for all available tools and their metadata,
enabling tool discovery, registration, and management.
"""

import uuid
import datetime
from typing import Dict, List, Any, Optional, Union
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolMetadata:
    """Metadata for a tool in the registry."""
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        provider: str,
        category: str,
        tags: List[str],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        execution_requirements: Dict[str, Any],
        permissions: List[str]
    ):
        """
        Initialize tool metadata.
        
        Args:
            name: Name of the tool
            description: Description of the tool's functionality
            version: Version string
            provider: Name of the tool provider
            category: Primary category of the tool
            tags: List of tags for categorization
            input_schema: JSON schema for input parameters
            output_schema: JSON schema for output format
            execution_requirements: Resource requirements for execution
            permissions: Required permissions for tool execution
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.version = version
        self.provider = provider
        self.category = category
        self.tags = tags
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.execution_requirements = execution_requirements
        self.permissions = permissions
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.usage_count = 0
        self.average_rating = 0.0
        self.review_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "provider": self.provider,
            "category": self.category,
            "tags": self.tags,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "execution_requirements": self.execution_requirements,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "usage_count": self.usage_count,
            "average_rating": self.average_rating,
            "review_count": self.review_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMetadata':
        """Create metadata from dictionary."""
        metadata = cls(
            name=data["name"],
            description=data["description"],
            version=data["version"],
            provider=data["provider"],
            category=data["category"],
            tags=data["tags"],
            input_schema=data["input_schema"],
            output_schema=data["output_schema"],
            execution_requirements=data["execution_requirements"],
            permissions=data["permissions"]
        )
        metadata.id = data["id"]
        metadata.created_at = datetime.datetime.fromisoformat(data["created_at"])
        metadata.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        metadata.usage_count = data["usage_count"]
        metadata.average_rating = data["average_rating"]
        metadata.review_count = data["review_count"]
        return metadata
    
    def update(self, **kwargs) -> None:
        """Update metadata fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.datetime.now()
    
    def increment_usage(self) -> None:
        """Increment usage count."""
        self.usage_count += 1
        self.updated_at = datetime.datetime.now()
    
    def add_rating(self, rating: float) -> None:
        """Add a new rating and update average."""
        if not 0 <= rating <= 5:
            raise ValueError("Rating must be between 0 and 5")
        
        total_rating = self.average_rating * self.review_count
        self.review_count += 1
        self.average_rating = (total_rating + rating) / self.review_count
        self.updated_at = datetime.datetime.now()


class ToolRegistry:
    """
    Central registry for all available tools in the Lumina AI ecosystem.
    
    Provides functionality for:
    - Tool registration and deregistration
    - Tool discovery and querying
    - Tool metadata management
    - Tool versioning
    - Tool categorization
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the tool registry.
        
        Args:
            storage_path: Optional path to persistent storage file
        """
        self.tools: Dict[str, ToolMetadata] = {}
        self.storage_path = storage_path
        if storage_path:
            try:
                self.load()
            except (FileNotFoundError, json.JSONDecodeError):
                logger.info(f"No existing registry found at {storage_path}, starting fresh")
    
    def register_tool(self, metadata: ToolMetadata) -> str:
        """
        Register a new tool in the registry.
        
        Args:
            metadata: Tool metadata
            
        Returns:
            Tool ID
        """
        if metadata.id in self.tools:
            raise ValueError(f"Tool with ID {metadata.id} already exists")
        
        self.tools[metadata.id] = metadata
        logger.info(f"Registered tool: {metadata.name} (ID: {metadata.id})")
        
        if self.storage_path:
            self.save()
            
        return metadata.id
    
    def update_tool(self, tool_id: str, **kwargs) -> None:
        """
        Update tool metadata.
        
        Args:
            tool_id: ID of the tool to update
            **kwargs: Metadata fields to update
        """
        if tool_id not in self.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        self.tools[tool_id].update(**kwargs)
        logger.info(f"Updated tool: {self.tools[tool_id].name} (ID: {tool_id})")
        
        if self.storage_path:
            self.save()
    
    def deregister_tool(self, tool_id: str) -> None:
        """
        Remove a tool from the registry.
        
        Args:
            tool_id: ID of the tool to remove
        """
        if tool_id not in self.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        tool_name = self.tools[tool_id].name
        del self.tools[tool_id]
        logger.info(f"Deregistered tool: {tool_name} (ID: {tool_id})")
        
        if self.storage_path:
            self.save()
    
    def get_tool(self, tool_id: str) -> ToolMetadata:
        """
        Get tool metadata by ID.
        
        Args:
            tool_id: ID of the tool
            
        Returns:
            Tool metadata
        """
        if tool_id not in self.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        return self.tools[tool_id]
    
    def list_tools(self) -> List[ToolMetadata]:
        """
        List all registered tools.
        
        Returns:
            List of all tool metadata
        """
        return list(self.tools.values())
    
    def search_tools(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        provider: Optional[str] = None
    ) -> List[ToolMetadata]:
        """
        Search for tools based on criteria.
        
        Args:
            query: Search query for name and description
            category: Filter by category
            tags: Filter by tags (tool must have all specified tags)
            provider: Filter by provider
            
        Returns:
            List of matching tool metadata
        """
        results = list(self.tools.values())
        
        if query:
            query = query.lower()
            results = [
                tool for tool in results
                if query in tool.name.lower() or query in tool.description.lower()
            ]
        
        if category:
            results = [tool for tool in results if tool.category == category]
        
        if tags:
            results = [
                tool for tool in results
                if all(tag in tool.tags for tag in tags)
            ]
        
        if provider:
            results = [tool for tool in results if tool.provider == provider]
        
        return results
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories in the registry.
        
        Returns:
            List of categories
        """
        return list(set(tool.category for tool in self.tools.values()))
    
    def get_tags(self) -> List[str]:
        """
        Get all unique tags in the registry.
        
        Returns:
            List of tags
        """
        tags = set()
        for tool in self.tools.values():
            tags.update(tool.tags)
        return list(tags)
    
    def get_providers(self) -> List[str]:
        """
        Get all unique providers in the registry.
        
        Returns:
            List of providers
        """
        return list(set(tool.provider for tool in self.tools.values()))
    
    def record_usage(self, tool_id: str) -> None:
        """
        Record usage of a tool.
        
        Args:
            tool_id: ID of the tool used
        """
        if tool_id not in self.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        self.tools[tool_id].increment_usage()
        
        if self.storage_path:
            self.save()
    
    def add_rating(self, tool_id: str, rating: float) -> None:
        """
        Add a rating for a tool.
        
        Args:
            tool_id: ID of the tool
            rating: Rating value (0-5)
        """
        if tool_id not in self.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        self.tools[tool_id].add_rating(rating)
        
        if self.storage_path:
            self.save()
    
    def save(self) -> None:
        """Save registry to persistent storage."""
        if not self.storage_path:
            return
        
        data = {
            tool_id: tool.to_dict()
            for tool_id, tool in self.tools.items()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved registry to {self.storage_path}")
    
    def load(self) -> None:
        """Load registry from persistent storage."""
        if not self.storage_path:
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        self.tools = {
            tool_id: ToolMetadata.from_dict(tool_data)
            for tool_id, tool_data in data.items()
        }
        
        logger.info(f"Loaded registry from {self.storage_path} with {len(self.tools)} tools")
