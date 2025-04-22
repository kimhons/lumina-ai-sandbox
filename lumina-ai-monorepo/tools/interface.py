"""
Tool Interface module for Lumina AI's Expanded Tool Ecosystem.

This module provides standardized interfaces for tool definition, parameter handling,
and integration with the Tool Registry and Tool Execution Engine.
"""

import inspect
import functools
from typing import Dict, List, Any, Optional, Union, Callable, Type, TypeVar, get_type_hints
import logging

from .registry import ToolRegistry, ToolMetadata
from .execution import ToolExecutionEngine, ToolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class ToolInterface:
    """Base class for tool interfaces."""
    
    @staticmethod
    def register_function(
        registry: ToolRegistry,
        engine: ToolExecutionEngine,
        name: str,
        description: str,
        category: str,
        tags: List[str],
        provider: str = "Lumina AI",
        version: str = "1.0.0"
    ) -> Callable[[Callable], Callable]:
        """
        Decorator to register a Python function as a tool.
        
        Args:
            registry: Tool registry
            engine: Tool execution engine
            name: Tool name
            description: Tool description
            category: Tool category
            tags: Tool tags
            provider: Tool provider
            version: Tool version
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            # Get function signature
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            # Create input schema
            input_schema = {}
            for param_name, param in sig.parameters.items():
                param_type = type_hints.get(param_name, Any).__name__
                required = param.default == inspect.Parameter.empty
                
                input_schema[param_name] = {
                    "type": param_type,
                    "required": required,
                    "description": f"Parameter: {param_name}"
                }
            
            # Create output schema
            return_type = type_hints.get('return', Any).__name__
            output_schema = {
                "type": return_type,
                "description": "Tool output"
            }
            
            # Create tool metadata
            metadata = ToolMetadata(
                name=name,
                description=description,
                version=version,
                provider=provider,
                category=category,
                tags=tags,
                input_schema=input_schema,
                output_schema=output_schema,
                execution_requirements={},
                permissions=[]
            )
            
            # Register tool
            tool_id = registry.register_tool(metadata)
            
            # Register executor
            engine.register_python_function(tool_id, func)
            
            # Add tool_id to function
            func.tool_id = tool_id
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    @staticmethod
    def register_command_line_tool(
        registry: ToolRegistry,
        engine: ToolExecutionEngine,
        name: str,
        description: str,
        category: str,
        tags: List[str],
        command_template: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        provider: str = "Lumina AI",
        version: str = "1.0.0"
    ) -> str:
        """
        Register a command-line tool.
        
        Args:
            registry: Tool registry
            engine: Tool execution engine
            name: Tool name
            description: Tool description
            category: Tool category
            tags: Tool tags
            command_template: Command template with parameter placeholders
            input_schema: Schema for input parameters
            output_schema: Schema for output format
            provider: Tool provider
            version: Tool version
            
        Returns:
            Tool ID
        """
        # Create tool metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            version=version,
            provider=provider,
            category=category,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            execution_requirements={},
            permissions=[]
        )
        
        # Register tool
        tool_id = registry.register_tool(metadata)
        
        # Register executor
        engine.register_command_line_tool(tool_id, command_template)
        
        return tool_id
    
    @staticmethod
    def register_web_api_tool(
        registry: ToolRegistry,
        engine: ToolExecutionEngine,
        name: str,
        description: str,
        category: str,
        tags: List[str],
        api_url: str,
        method: str = "POST",
        input_schema: Dict[str, Any] = None,
        output_schema: Dict[str, Any] = None,
        provider: str = "Lumina AI",
        version: str = "1.0.0"
    ) -> str:
        """
        Register a web API tool.
        
        Args:
            registry: Tool registry
            engine: Tool execution engine
            name: Tool name
            description: Tool description
            category: Tool category
            tags: Tool tags
            api_url: URL of the API endpoint
            method: HTTP method (GET, POST, etc.)
            input_schema: Schema for input parameters
            output_schema: Schema for output format
            provider: Tool provider
            version: Tool version
            
        Returns:
            Tool ID
        """
        # Default schemas if not provided
        if input_schema is None:
            input_schema = {
                "parameters": {
                    "type": "object",
                    "required": True,
                    "description": "API parameters"
                }
            }
        
        if output_schema is None:
            output_schema = {
                "type": "object",
                "description": "API response"
            }
        
        # Create tool metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            version=version,
            provider=provider,
            category=category,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            execution_requirements={},
            permissions=[]
        )
        
        # Register tool
        tool_id = registry.register_tool(metadata)
        
        # Register executor
        engine.register_web_api_tool(tool_id, api_url, method)
        
        return tool_id
    
    @staticmethod
    def register_custom_executor(
        registry: ToolRegistry,
        engine: ToolExecutionEngine,
        executor_class: Type[ToolExecutor],
        name: str,
        description: str,
        category: str,
        tags: List[str],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        executor_args: Dict[str, Any],
        provider: str = "Lumina AI",
        version: str = "1.0.0"
    ) -> str:
        """
        Register a custom tool executor.
        
        Args:
            registry: Tool registry
            engine: Tool execution engine
            executor_class: Custom executor class
            name: Tool name
            description: Tool description
            category: Tool category
            tags: Tool tags
            input_schema: Schema for input parameters
            output_schema: Schema for output format
            executor_args: Arguments for executor initialization
            provider: Tool provider
            version: Tool version
            
        Returns:
            Tool ID
        """
        # Create tool metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            version=version,
            provider=provider,
            category=category,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            execution_requirements={},
            permissions=[]
        )
        
        # Register tool
        tool_id = registry.register_tool(metadata)
        
        # Create and register executor
        executor = executor_class(tool_id, metadata, **executor_args)
        engine.register_executor(executor)
        
        return tool_id

class ToolParameter:
    """Descriptor for tool parameters with validation."""
    
    def __init__(self, param_type: Type[T], required: bool = True, description: str = ""):
        """
        Initialize parameter descriptor.
        
        Args:
            param_type: Parameter type
            required: Whether parameter is required
            description: Parameter description
        """
        self.param_type = param_type
        self.required = required
        self.description = description
        self.name = None
    
    def __set_name__(self, owner, name):
        """Set parameter name when used in a class."""
        self.name = name
    
    def __get__(self, instance, owner):
        """Get parameter value."""
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        """Set parameter value with validation."""
        if value is None:
            if self.required:
                raise ValueError(f"Parameter {self.name} is required")
            instance.__dict__[self.name] = None
            return
        
        if not isinstance(value, self.param_type):
            try:
                value = self.param_type(value)
            except (ValueError, TypeError):
                raise TypeError(f"Parameter {self.name} must be of type {self.param_type.__name__}")
        
        instance.__dict__[self.name] = value

class ToolClass:
    """Base class for defining tools as classes."""
    
    def __init_subclass__(cls, **kwargs):
        """Register tool class when subclassed."""
        super().__init_subclass__(**kwargs)
        
        # Store parameter descriptors
        cls._tool_parameters = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, ToolParameter):
                cls._tool_parameters[name] = attr
    
    @classmethod
    def register(
        cls,
        registry: ToolRegistry,
        engine: ToolExecutionEngine,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        provider: str = "Lumina AI",
        version: str = "1.0.0"
    ) -> str:
        """
        Register the tool class.
        
        Args:
            registry: Tool registry
            engine: Tool execution engine
            name: Tool name (defaults to class name)
            description: Tool description (defaults to class docstring)
            category: Tool category
            tags: Tool tags
            provider: Tool provider
            version: Tool version
            
        Returns:
            Tool ID
        """
        # Use class name and docstring if not provided
        if name is None:
            name = cls.__name__
        
        if description is None:
            description = cls.__doc__ or f"Tool class: {cls.__name__}"
        
        if category is None:
            category = "Class-based Tool"
        
        if tags is None:
            tags = ["class-based"]
        
        # Create input schema from parameters
        input_schema = {}
        for param_name, param in cls._tool_parameters.items():
            input_schema[param_name] = {
                "type": param.param_type.__name__,
                "required": param.required,
                "description": param.description
            }
        
        # Create output schema from execute method
        output_schema = {
            "type": "object",
            "description": "Tool output"
        }
        
        # Create executor function
        def executor_function(**kwargs):
            instance = cls()
            for param_name, value in kwargs.items():
                setattr(instance, param_name, value)
            return instance.execute()
        
        # Create tool metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            version=version,
            provider=provider,
            category=category,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            execution_requirements={},
            permissions=[]
        )
        
        # Register tool
        tool_id = registry.register_tool(metadata)
        
        # Register executor
        engine.register_python_function(tool_id, executor_function)
        
        # Store tool_id in class
        cls.tool_id = tool_id
        
        return tool_id
    
    def execute(self) -> Any:
        """
        Execute the tool.
        
        Returns:
            Tool output
        """
        raise NotImplementedError("Subclasses must implement execute method")
