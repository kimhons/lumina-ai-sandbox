"""
Tool Execution Engine for Lumina AI's Expanded Tool Ecosystem.

This module provides functionality for executing tools, managing their lifecycle,
handling errors, and supporting both synchronous and asynchronous execution.
"""

import uuid
import datetime
import time
import threading
import queue
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import json
import traceback
import asyncio
import concurrent.futures

from .registry import ToolRegistry, ToolMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolExecutionStatus:
    """Status of a tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ToolExecutionResult:
    """Result of a tool execution."""
    
    def __init__(
        self,
        execution_id: str,
        tool_id: str,
        status: str,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        execution_time: Optional[float] = None
    ):
        """
        Initialize execution result.
        
        Args:
            execution_id: Unique ID for this execution
            tool_id: ID of the executed tool
            status: Execution status
            output: Tool output (if successful)
            error: Error message (if failed)
            start_time: Execution start time
            end_time: Execution end time
            execution_time: Execution duration in seconds
        """
        self.execution_id = execution_id
        self.tool_id = tool_id
        self.status = status
        self.output = output
        self.error = error
        self.start_time = start_time
        self.end_time = end_time
        self.execution_time = execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "execution_id": self.execution_id,
            "tool_id": self.tool_id,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolExecutionResult':
        """Create result from dictionary."""
        start_time = datetime.datetime.fromisoformat(data["start_time"]) if data["start_time"] else None
        end_time = datetime.datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
        
        return cls(
            execution_id=data["execution_id"],
            tool_id=data["tool_id"],
            status=data["status"],
            output=data["output"],
            error=data["error"],
            start_time=start_time,
            end_time=end_time,
            execution_time=data["execution_time"]
        )

class ToolExecutor:
    """Base class for tool executors."""
    
    def __init__(self, tool_id: str, tool_metadata: ToolMetadata):
        """
        Initialize tool executor.
        
        Args:
            tool_id: ID of the tool
            tool_metadata: Metadata for the tool
        """
        self.tool_id = tool_id
        self.tool_metadata = tool_metadata
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate input parameters against schema.
        
        Args:
            parameters: Input parameters
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # In a real implementation, this would use JSON Schema validation
        # For now, we'll just check that required parameters are present
        required_params = [
            param for param, schema in self.tool_metadata.input_schema.items()
            if schema.get("required", False)
        ]
        
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
        
        return True
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the tool with given parameters.
        
        Args:
            parameters: Input parameters
            
        Returns:
            Tool output
        """
        raise NotImplementedError("Subclasses must implement execute method")

class PythonFunctionToolExecutor(ToolExecutor):
    """Executor for Python function-based tools."""
    
    def __init__(self, tool_id: str, tool_metadata: ToolMetadata, function: Callable):
        """
        Initialize Python function executor.
        
        Args:
            tool_id: ID of the tool
            tool_metadata: Metadata for the tool
            function: Python function to execute
        """
        super().__init__(tool_id, tool_metadata)
        self.function = function
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the Python function with given parameters.
        
        Args:
            parameters: Input parameters
            
        Returns:
            Function output
        """
        self.validate_parameters(parameters)
        return self.function(**parameters)

class CommandLineToolExecutor(ToolExecutor):
    """Executor for command-line tools."""
    
    def __init__(self, tool_id: str, tool_metadata: ToolMetadata, command_template: str):
        """
        Initialize command-line executor.
        
        Args:
            tool_id: ID of the tool
            tool_metadata: Metadata for the tool
            command_template: Command template with parameter placeholders
        """
        super().__init__(tool_id, tool_metadata)
        self.command_template = command_template
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the command-line tool with given parameters.
        
        Args:
            parameters: Input parameters
            
        Returns:
            Command output
        """
        import subprocess
        
        self.validate_parameters(parameters)
        
        # Format command with parameters
        command = self.command_template.format(**parameters)
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {result.returncode}: {result.stderr}")
        
        return result.stdout

class WebAPIToolExecutor(ToolExecutor):
    """Executor for web API-based tools."""
    
    def __init__(self, tool_id: str, tool_metadata: ToolMetadata, api_url: str, method: str = "POST"):
        """
        Initialize web API executor.
        
        Args:
            tool_id: ID of the tool
            tool_metadata: Metadata for the tool
            api_url: URL of the API endpoint
            method: HTTP method (GET, POST, etc.)
        """
        super().__init__(tool_id, tool_metadata)
        self.api_url = api_url
        self.method = method
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the web API call with given parameters.
        
        Args:
            parameters: Input parameters
            
        Returns:
            API response
        """
        import requests
        
        self.validate_parameters(parameters)
        
        # Make API request
        if self.method.upper() == "GET":
            response = requests.get(self.api_url, params=parameters)
        else:
            response = requests.post(self.api_url, json=parameters)
        
        # Check for errors
        response.raise_for_status()
        
        # Return response data
        return response.json()

class ToolExecutionEngine:
    """
    Engine for executing tools and managing their lifecycle.
    
    Provides functionality for:
    - Tool invocation with parameter validation
    - Execution monitoring and timeout handling
    - Result processing and transformation
    - Error handling and recovery
    - Asynchronous execution management
    - Parallel execution coordination
    """
    
    def __init__(self, registry: ToolRegistry, max_workers: int = 10):
        """
        Initialize the execution engine.
        
        Args:
            registry: Tool registry
            max_workers: Maximum number of concurrent executions
        """
        self.registry = registry
        self.max_workers = max_workers
        self.executors: Dict[str, ToolExecutor] = {}
        self.executions: Dict[str, ToolExecutionResult] = {}
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.async_loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()
    
    def _run_async_loop(self) -> None:
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.async_loop)
        self.async_loop.run_forever()
    
    def register_executor(self, executor: ToolExecutor) -> None:
        """
        Register a tool executor.
        
        Args:
            executor: Tool executor
        """
        self.executors[executor.tool_id] = executor
        logger.info(f"Registered executor for tool: {executor.tool_metadata.name} (ID: {executor.tool_id})")
    
    def register_python_function(self, tool_id: str, function: Callable) -> None:
        """
        Register a Python function as a tool.
        
        Args:
            tool_id: ID of the tool
            function: Python function to execute
        """
        tool_metadata = self.registry.get_tool(tool_id)
        executor = PythonFunctionToolExecutor(tool_id, tool_metadata, function)
        self.register_executor(executor)
    
    def register_command_line_tool(self, tool_id: str, command_template: str) -> None:
        """
        Register a command-line tool.
        
        Args:
            tool_id: ID of the tool
            command_template: Command template with parameter placeholders
        """
        tool_metadata = self.registry.get_tool(tool_id)
        executor = CommandLineToolExecutor(tool_id, tool_metadata, command_template)
        self.register_executor(executor)
    
    def register_web_api_tool(self, tool_id: str, api_url: str, method: str = "POST") -> None:
        """
        Register a web API tool.
        
        Args:
            tool_id: ID of the tool
            api_url: URL of the API endpoint
            method: HTTP method (GET, POST, etc.)
        """
        tool_metadata = self.registry.get_tool(tool_id)
        executor = WebAPIToolExecutor(tool_id, tool_metadata, api_url, method)
        self.register_executor(executor)
    
    def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> ToolExecutionResult:
        """
        Execute a tool synchronously.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Input parameters
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result
        """
        # Check if tool exists in registry
        if tool_id not in self.registry.tools:
            raise ValueError(f"Tool with ID {tool_id} not found in registry")
        
        # Check if executor exists
        if tool_id not in self.executors:
            raise ValueError(f"No executor registered for tool with ID {tool_id}")
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Record start time
        start_time = datetime.datetime.now()
        
        # Create initial result
        result = ToolExecutionResult(
            execution_id=execution_id,
            tool_id=tool_id,
            status=ToolExecutionStatus.RUNNING,
            start_time=start_time
        )
        
        self.executions[execution_id] = result
        
        try:
            # Get executor
            executor = self.executors[tool_id]
            
            # Execute with timeout
            if timeout:
                future = self.thread_pool.submit(executor.execute, parameters)
                output = future.result(timeout=timeout)
            else:
                output = executor.execute(parameters)
            
            # Record end time
            end_time = datetime.datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update result
            result.status = ToolExecutionStatus.COMPLETED
            result.output = output
            result.end_time = end_time
            result.execution_time = execution_time
            
            # Record usage
            self.registry.record_usage(tool_id)
            
            logger.info(f"Tool execution completed: {execution_id} (Tool: {tool_id})")
            
        except concurrent.futures.TimeoutError:
            # Handle timeout
            result.status = ToolExecutionStatus.TIMEOUT
            result.error = f"Execution timed out after {timeout} seconds"
            result.end_time = datetime.datetime.now()
            result.execution_time = (result.end_time - start_time).total_seconds()
            
            logger.warning(f"Tool execution timed out: {execution_id} (Tool: {tool_id})")
            
        except Exception as e:
            # Handle other errors
            result.status = ToolExecutionStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.datetime.now()
            result.execution_time = (result.end_time - start_time).total_seconds()
            
            logger.error(f"Tool execution failed: {execution_id} (Tool: {tool_id})")
            logger.error(traceback.format_exc())
        
        return result
    
    async def execute_tool_async(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> str:
        """
        Execute a tool asynchronously.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Input parameters
            timeout: Execution timeout in seconds
            
        Returns:
            Execution ID
        """
        # Check if tool exists in registry
        if tool_id not in self.registry.tools:
            raise ValueError(f"Tool with ID {tool_id} not found in registry")
        
        # Check if executor exists
        if tool_id not in self.executors:
            raise ValueError(f"No executor registered for tool with ID {tool_id}")
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Record start time
        start_time = datetime.datetime.now()
        
        # Create initial result
        result = ToolExecutionResult(
            execution_id=execution_id,
            tool_id=tool_id,
            status=ToolExecutionStatus.PENDING,
            start_time=start_time
        )
        
        self.executions[execution_id] = result
        
        # Schedule execution
        asyncio.run_coroutine_threadsafe(
            self._execute_async(execution_id, tool_id, parameters, timeout),
            self.async_loop
        )
        
        logger.info(f"Scheduled async tool execution: {execution_id} (Tool: {tool_id})")
        
        return execution_id
    
    async def _execute_async(
        self,
        execution_id: str,
        tool_id: str,
        parameters: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> None:
        """
        Execute a tool asynchronously (internal implementation).
        
        Args:
            execution_id: Execution ID
            tool_id: ID of the tool to execute
            parameters: Input parameters
            timeout: Execution timeout in seconds
        """
        # Get result object
        result = self.executions[execution_id]
        
        # Update status
        result.status = ToolExecutionStatus.RUNNING
        
        try:
            # Get executor
            executor = self.executors[tool_id]
            
            # Execute with timeout
            loop = asyncio.get_event_loop()
            if timeout:
                output = await asyncio.wait_for(
                    loop.run_in_executor(None, executor.execute, parameters),
                    timeout=timeout
                )
            else:
                output = await loop.run_in_executor(None, executor.execute, parameters)
            
            # Record end time
            end_time = datetime.datetime.now()
            execution_time = (end_time - result.start_time).total_seconds()
            
            # Update result
            result.status = ToolExecutionStatus.COMPLETED
            result.output = output
            result.end_time = end_time
            result.execution_time = execution_time
            
            # Record usage
            self.registry.record_usage(tool_id)
            
            logger.info(f"Async tool execution completed: {execution_id} (Tool: {tool_id})")
            
        except asyncio.TimeoutError:
            # Handle timeout
            result.status = ToolExecutionStatus.TIMEOUT
            result.error = f"Execution timed out after {timeout} seconds"
            result.end_time = datetime.datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            logger.warning(f"Async tool execution timed out: {execution_id} (Tool: {tool_id})")
            
        except Exception as e:
            # Handle other errors
            result.status = ToolExecutionStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            logger.error(f"Async tool execution failed: {execution_id} (Tool: {tool_id})")
            logger.error(traceback.format_exc())
    
    def get_execution_result(self, execution_id: str) -> ToolExecutionResult:
        """
        Get the result of a tool execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution result
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution with ID {execution_id} not found")
        
        return self.executions[execution_id]
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running tool execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            True if cancelled, False if already completed
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution with ID {execution_id} not found")
        
        result = self.executions[execution_id]
        
        if result.status in [ToolExecutionStatus.COMPLETED, ToolExecutionStatus.FAILED, ToolExecutionStatus.TIMEOUT]:
            return False
        
        result.status = ToolExecutionStatus.CANCELLED
        result.end_time = datetime.datetime.now()
        result.execution_time = (result.end_time - result.start_time).total_seconds()
        result.error = "Execution cancelled by user"
        
        logger.info(f"Tool execution cancelled: {execution_id} (Tool: {result.tool_id})")
        
        return True
    
    def execute_tools_parallel(
        self,
        executions: List[Tuple[str, Dict[str, Any]]],
        timeout: Optional[float] = None
    ) -> Dict[str, ToolExecutionResult]:
        """
        Execute multiple tools in parallel.
        
        Args:
            executions: List of (tool_id, parameters) tuples
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary mapping execution IDs to results
        """
        # Create futures for all executions
        futures = {}
        execution_ids = {}
        
        for tool_id, parameters in executions:
            execution_id = str(uuid.uuid4())
            future = self.thread_pool.submit(self.execute_tool, tool_id, parameters, timeout)
            futures[future] = execution_id
            execution_ids[execution_id] = tool_id
        
        # Wait for all futures to complete
        results = {}
        
        for future in concurrent.futures.as_completed(futures.keys()):
            execution_id = futures[future]
            try:
                result = future.result()
                results[execution_id] = result
            except Exception as e:
                # Handle unexpected errors
                tool_id = execution_ids[execution_id]
                result = ToolExecutionResult(
                    execution_id=execution_id,
                    tool_id=tool_id,
                    status=ToolExecutionStatus.FAILED,
                    error=str(e)
                )
                results[execution_id] = result
        
        return results
    
    def shutdown(self) -> None:
        """Shutdown the execution engine."""
        self.thread_pool.shutdown()
        self.async_loop.call_soon_threadsafe(self.async_loop.stop)
        self.async_thread.join(timeout=1.0)
        logger.info("Tool execution engine shut down")
