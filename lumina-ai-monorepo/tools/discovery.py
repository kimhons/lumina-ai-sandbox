"""
Tool Discovery module for Lumina AI's Expanded Tool Ecosystem.

This module provides functionality for discovering, searching, and filtering tools
based on various criteria, including capabilities, categories, and metadata.
"""

import re
from typing import Dict, List, Any, Optional, Union, Set, Callable
import logging

from .registry import ToolRegistry, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolCapability:
    """Represents a specific capability that tools can provide."""
    
    def __init__(self, name: str, description: str, required_parameters: List[str] = None):
        """
        Initialize tool capability.
        
        Args:
            name: Capability name
            description: Capability description
            required_parameters: Parameters required for this capability
        """
        self.name = name
        self.description = description
        self.required_parameters = required_parameters or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert capability to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "required_parameters": self.required_parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolCapability':
        """Create capability from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            required_parameters=data.get("required_parameters", [])
        )


class ToolDiscovery:
    """
    Service for discovering and searching tools based on various criteria.
    
    Provides functionality for:
    - Searching tools by name, description, or capability
    - Filtering tools by category, tags, or provider
    - Discovering tools based on input/output requirements
    - Suggesting tools based on user context
    """
    
    def __init__(self, registry: ToolRegistry):
        """
        Initialize tool discovery service.
        
        Args:
            registry: Tool registry
        """
        self.registry = registry
        self.capabilities: Dict[str, ToolCapability] = {}
        self.tool_capabilities: Dict[str, Set[str]] = {}  # tool_id -> set of capability names
    
    def register_capability(self, capability: ToolCapability) -> None:
        """
        Register a new capability.
        
        Args:
            capability: Tool capability
        """
        if capability.name in self.capabilities:
            raise ValueError(f"Capability with name '{capability.name}' already exists")
        
        self.capabilities[capability.name] = capability
        logger.info(f"Registered capability: {capability.name}")
    
    def assign_capability(self, tool_id: str, capability_name: str) -> None:
        """
        Assign a capability to a tool.
        
        Args:
            tool_id: Tool ID
            capability_name: Capability name
        """
        # Check if tool exists
        if tool_id not in self.registry.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        # Check if capability exists
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability '{capability_name}' not found")
        
        # Check if tool has required parameters for capability
        capability = self.capabilities[capability_name]
        tool = self.registry.get_tool(tool_id)
        
        for param in capability.required_parameters:
            if param not in tool.input_schema:
                raise ValueError(f"Tool {tool.name} missing required parameter '{param}' for capability '{capability_name}'")
        
        # Assign capability
        if tool_id not in self.tool_capabilities:
            self.tool_capabilities[tool_id] = set()
        
        self.tool_capabilities[tool_id].add(capability_name)
        logger.info(f"Assigned capability '{capability_name}' to tool {tool.name} (ID: {tool_id})")
    
    def get_tool_capabilities(self, tool_id: str) -> List[ToolCapability]:
        """
        Get capabilities of a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            List of tool capabilities
        """
        if tool_id not in self.registry.tools:
            raise ValueError(f"Tool with ID {tool_id} not found")
        
        capability_names = self.tool_capabilities.get(tool_id, set())
        return [self.capabilities[name] for name in capability_names]
    
    def find_tools_by_capability(self, capability_name: str) -> List[ToolMetadata]:
        """
        Find tools with a specific capability.
        
        Args:
            capability_name: Capability name
            
        Returns:
            List of tool metadata
        """
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability '{capability_name}' not found")
        
        tool_ids = [
            tool_id for tool_id, capabilities in self.tool_capabilities.items()
            if capability_name in capabilities
        ]
        
        return [self.registry.get_tool(tool_id) for tool_id in tool_ids]
    
    def search_tools(
        self,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        providers: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "relevance"
    ) -> List[ToolMetadata]:
        """
        Search for tools based on multiple criteria.
        
        Args:
            query: Search query for name and description
            categories: Filter by categories
            tags: Filter by tags
            providers: Filter by providers
            capabilities: Filter by capabilities
            min_rating: Minimum average rating
            sort_by: Sort order (relevance, name, rating, usage)
            
        Returns:
            List of matching tool metadata
        """
        # Start with all tools
        results = self.registry.list_tools()
        
        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                tool for tool in results
                if query_lower in tool.name.lower() or query_lower in tool.description.lower()
            ]
        
        # Filter by categories
        if categories:
            results = [tool for tool in results if tool.category in categories]
        
        # Filter by tags
        if tags:
            results = [
                tool for tool in results
                if any(tag in tool.tags for tag in tags)
            ]
        
        # Filter by providers
        if providers:
            results = [tool for tool in results if tool.provider in providers]
        
        # Filter by capabilities
        if capabilities:
            capability_tools = set()
            for capability in capabilities:
                try:
                    tools = self.find_tools_by_capability(capability)
                    capability_tools.update(tool.id for tool in tools)
                except ValueError:
                    # Skip invalid capabilities
                    pass
            
            results = [tool for tool in results if tool.id in capability_tools]
        
        # Filter by rating
        if min_rating is not None:
            results = [tool for tool in results if tool.average_rating >= min_rating]
        
        # Sort results
        if sort_by == "name":
            results.sort(key=lambda tool: tool.name)
        elif sort_by == "rating":
            results.sort(key=lambda tool: tool.average_rating, reverse=True)
        elif sort_by == "usage":
            results.sort(key=lambda tool: tool.usage_count, reverse=True)
        elif sort_by == "relevance" and query:
            # Simple relevance scoring based on query match position and frequency
            def relevance_score(tool):
                name_pos = tool.name.lower().find(query.lower())
                desc_pos = tool.description.lower().find(query.lower())
                name_count = tool.name.lower().count(query.lower())
                desc_count = tool.description.lower().count(query.lower())
                
                # Position score (earlier is better)
                pos_score = 0
                if name_pos != -1:
                    pos_score += 100 - min(name_pos, 100)
                if desc_pos != -1:
                    pos_score += 50 - min(desc_pos, 50)
                
                # Frequency score
                freq_score = name_count * 10 + desc_count * 5
                
                # Usage and rating bonus
                usage_bonus = min(tool.usage_count / 10, 20)
                rating_bonus = tool.average_rating * 5
                
                return pos_score + freq_score + usage_bonus + rating_bonus
            
            results.sort(key=relevance_score, reverse=True)
        
        return results
    
    def find_tools_by_input_type(self, input_type: str) -> List[ToolMetadata]:
        """
        Find tools that accept a specific input type.
        
        Args:
            input_type: Input parameter type
            
        Returns:
            List of tool metadata
        """
        results = []
        
        for tool in self.registry.list_tools():
            for param, schema in tool.input_schema.items():
                if schema.get("type", "").lower() == input_type.lower():
                    results.append(tool)
                    break
        
        return results
    
    def find_tools_by_output_type(self, output_type: str) -> List[ToolMetadata]:
        """
        Find tools that produce a specific output type.
        
        Args:
            output_type: Output type
            
        Returns:
            List of tool metadata
        """
        results = []
        
        for tool in self.registry.list_tools():
            if tool.output_schema.get("type", "").lower() == output_type.lower():
                results.append(tool)
        
        return results
    
    def suggest_tools_for_task(self, task_description: str, max_suggestions: int = 5) -> List[ToolMetadata]:
        """
        Suggest tools that might be useful for a described task.
        
        Args:
            task_description: Description of the task
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested tool metadata
        """
        # Extract key terms from task description
        task_lower = task_description.lower()
        
        # Simple keyword extraction (in a real system, this would use NLP)
        keywords = set()
        for word in re.findall(r'\b\w+\b', task_lower):
            if len(word) > 3:  # Skip short words
                keywords.add(word)
        
        # Score tools based on keyword matches
        scored_tools = []
        
        for tool in self.registry.list_tools():
            score = 0
            
            # Check name and description for keyword matches
            tool_text = (tool.name + " " + tool.description).lower()
            for keyword in keywords:
                if keyword in tool_text:
                    score += 1
            
            # Bonus for tags matching keywords
            for tag in tool.tags:
                if tag.lower() in keywords:
                    score += 2
            
            # Bonus for category matching keywords
            if tool.category.lower() in keywords:
                score += 3
            
            # Usage and rating bonus
            score += min(tool.usage_count / 20, 2)
            score += tool.average_rating / 2
            
            if score > 0:
                scored_tools.append((tool, score))
        
        # Sort by score and return top suggestions
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in scored_tools[:max_suggestions]]
