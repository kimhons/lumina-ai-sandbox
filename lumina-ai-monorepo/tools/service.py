"""
Tool Integration Service for Lumina AI.

This module provides a service for integrating the Tool Framework with the rest of the Lumina AI platform,
exposing tool capabilities through a REST API.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Set, Union
import os
import uuid
import time
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .manager import ToolManager
from .interface import Tool

# Define API models
class ToolExecutionRequest(BaseModel):
    """Model for tool execution requests."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    async_execution: bool = Field(default=False, description="Whether to execute the tool asynchronously")

class ToolExecutionResponse(BaseModel):
    """Model for tool execution responses."""
    request_id: str = Field(..., description="Unique ID for the request")
    tool_name: str = Field(..., description="Name of the tool that was executed")
    status: str = Field(..., description="Status of the execution (success, error, pending)")
    result: Optional[Dict[str, Any]] = Field(None, description="Result of the execution")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

class ToolListResponse(BaseModel):
    """Model for tool list responses."""
    tools: Dict[str, Dict[str, Any]] = Field(..., description="Dictionary of available tools")
    categories: List[str] = Field(..., description="List of tool categories")

class ToolStatusRequest(BaseModel):
    """Model for tool status requests."""
    request_id: str = Field(..., description="ID of the request to check status for")

class ToolService:
    """Service for integrating tools with the Lumina AI platform."""
    
    def __init__(self, tool_manager: ToolManager):
        """
        Initialize the tool service.
        
        Args:
            tool_manager: The tool manager to use
        """
        self.tool_manager = tool_manager
        self.logger = logging.getLogger("tools.service")
        self.app = FastAPI(title="Lumina AI Tool Service", version="1.0.0")
        self.async_results = {}  # request_id -> result
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, restrict to specific origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "tool-service"}
        
        @self.app.get("/tools", response_model=ToolListResponse)
        async def list_tools(request: Request):
            """List available tools."""
            # Get user permissions from request (in a real implementation, this would come from auth middleware)
            user_permissions = request.headers.get("X-User-Permissions", "").split(",")
            if user_permissions == [""]:
                user_permissions = None
            else:
                user_permissions = set(user_permissions)
            
            # Get available tools
            tools = self.tool_manager.get_available_tools(user_permissions)
            categories = self.tool_manager.get_categories()
            
            return {
                "tools": tools,
                "categories": categories
            }
        
        @self.app.get("/tools/category/{category}", response_model=Dict[str, Dict[str, Any]])
        async def get_tools_by_category(category: str, request: Request):
            """Get tools by category."""
            # Get user permissions from request
            user_permissions = request.headers.get("X-User-Permissions", "").split(",")
            if user_permissions == [""]:
                user_permissions = None
            else:
                user_permissions = set(user_permissions)
            
            # Get tools in category
            tools = self.tool_manager.get_tools_by_category(category, user_permissions)
            
            return tools
        
        @self.app.post("/tools/execute", response_model=ToolExecutionResponse)
        async def execute_tool(
            execution_request: ToolExecutionRequest,
            background_tasks: BackgroundTasks,
            request: Request
        ):
            """Execute a tool."""
            # Generate request ID
            request_id = str(uuid.uuid4())
            
            # Get user permissions from request
            user_permissions = request.headers.get("X-User-Permissions", "").split(",")
            if user_permissions == [""]:
                user_permissions = None
            else:
                user_permissions = set(user_permissions)
            
            # Check if tool exists
            tool = self.tool_manager.registry.get_tool(execution_request.tool_name)
            if not tool:
                raise HTTPException(status_code=404, detail=f"Tool '{execution_request.tool_name}' not found")
            
            # Check permissions
            if user_permissions is not None:
                required_permissions = set(tool.get_required_permissions())
                if not required_permissions.issubset(user_permissions):
                    missing_permissions = required_permissions - user_permissions
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                    )
            
            # Handle async execution
            if execution_request.async_execution:
                # Store pending result
                self.async_results[request_id] = {
                    "status": "pending",
                    "tool_name": execution_request.tool_name,
                    "start_time": time.time()
                }
                
                # Add task to background
                background_tasks.add_task(
                    self._execute_tool_async,
                    request_id,
                    execution_request.tool_name,
                    execution_request.parameters,
                    user_permissions
                )
                
                return {
                    "request_id": request_id,
                    "tool_name": execution_request.tool_name,
                    "status": "pending",
                    "result": None,
                    "error": None,
                    "execution_time": None
                }
            
            # Synchronous execution
            start_time = time.time()
            result = self.tool_manager.execute_tool(
                execution_request.tool_name,
                execution_request.parameters,
                user_permissions
            )
            execution_time = time.time() - start_time
            
            # Prepare response
            if result.get("success", False):
                return {
                    "request_id": request_id,
                    "tool_name": execution_request.tool_name,
                    "status": "success",
                    "result": result,
                    "error": None,
                    "execution_time": execution_time
                }
            else:
                return {
                    "request_id": request_id,
                    "tool_name": execution_request.tool_name,
                    "status": "error",
                    "result": None,
                    "error": result.get("error", "Unknown error"),
                    "execution_time": execution_time
                }
        
        @self.app.post("/tools/status", response_model=ToolExecutionResponse)
        async def check_tool_status(status_request: ToolStatusRequest):
            """Check the status of an asynchronous tool execution."""
            request_id = status_request.request_id
            
            if request_id not in self.async_results:
                raise HTTPException(status_code=404, detail=f"Request ID '{request_id}' not found")
            
            result = self.async_results[request_id]
            
            # Calculate execution time if completed
            execution_time = None
            if result.get("status") != "pending" and "start_time" in result:
                execution_time = result.get("end_time", time.time()) - result["start_time"]
            
            return {
                "request_id": request_id,
                "tool_name": result.get("tool_name"),
                "status": result.get("status"),
                "result": result.get("result"),
                "error": result.get("error"),
                "execution_time": execution_time
            }
    
    async def _execute_tool_async(self, request_id: str, tool_name: str, parameters: Dict[str, Any], user_permissions: Set[str] = None):
        """Execute a tool asynchronously."""
        try:
            # Execute tool
            result = self.tool_manager.execute_tool(tool_name, parameters, user_permissions)
            
            # Update result
            if result.get("success", False):
                self.async_results[request_id] = {
                    "status": "success",
                    "tool_name": tool_name,
                    "result": result,
                    "error": None,
                    "start_time": self.async_results[request_id]["start_time"],
                    "end_time": time.time()
                }
            else:
                self.async_results[request_id] = {
                    "status": "error",
                    "tool_name": tool_name,
                    "result": None,
                    "error": result.get("error", "Unknown error"),
                    "start_time": self.async_results[request_id]["start_time"],
                    "end_time": time.time()
                }
        
        except Exception as e:
            # Handle exceptions
            self.logger.error(f"Error executing tool '{tool_name}': {e}")
            self.async_results[request_id] = {
                "status": "error",
                "tool_name": tool_name,
                "result": None,
                "error": str(e),
                "start_time": self.async_results[request_id]["start_time"],
                "end_time": time.time()
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the tool service.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
    
    def cleanup_async_results(self, max_age_seconds: int = 3600):
        """
        Clean up old async results.
        
        Args:
            max_age_seconds: Maximum age of results to keep
        """
        current_time = time.time()
        to_remove = []
        
        for request_id, result in self.async_results.items():
            # Calculate age
            end_time = result.get("end_time")
            if end_time and (current_time - end_time) > max_age_seconds:
                to_remove.append(request_id)
        
        # Remove old results
        for request_id in to_remove:
            del self.async_results[request_id]
        
        self.logger.info(f"Cleaned up {len(to_remove)} old async results")
