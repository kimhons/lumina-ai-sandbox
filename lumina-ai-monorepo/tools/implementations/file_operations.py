"""
File Operations Tool for Lumina AI.

This module implements a tool for performing file operations
such as reading, writing, and managing files.
"""

import os
import json
import base64
import logging
from typing import List, Dict, Any, Optional, Union, BinaryIO

from ..base import BaseTool

class FileOperationsTool(BaseTool):
    """Tool for performing file operations."""
    
    # Tool metadata for discovery
    TOOL_METADATA = {
        'categories': ['file', 'system', 'io']
    }
    
    def __init__(self, base_directory: Optional[str] = None):
        """
        Initialize the file operations tool.
        
        Args:
            base_directory: Optional base directory to restrict file operations to
        """
        # Define parameters schema
        parameters_schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The file operation to perform",
                    "enum": ["read", "write", "append", "delete", "list", "exists", "info"]
                },
                "path": {
                    "type": "string",
                    "description": "The path of the file or directory"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file (for write/append operations)"
                },
                "encoding": {
                    "type": "string",
                    "description": "The encoding to use for text operations",
                    "default": "utf-8"
                },
                "binary": {
                    "type": "boolean",
                    "description": "Whether to treat the file as binary",
                    "default": False
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to perform operations recursively (for directory operations)",
                    "default": False
                }
            },
            "required": ["operation", "path"]
        }
        
        # Initialize base tool
        super().__init__(
            name="file_operations",
            description="Perform file operations such as reading, writing, and managing files",
            parameters_schema=parameters_schema,
            required_permissions=["file_system"]
        )
        
        self.base_directory = base_directory
    
    def _execute_tool(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the file operation.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary containing operation results
        """
        operation = parameters["operation"]
        path = parameters["path"]
        
        # Validate path
        if self.base_directory:
            path = self._validate_path(path)
        
        self.logger.info(f"Performing file operation '{operation}' on '{path}'")
        
        if operation == "read":
            return self._read_file(path, parameters)
        elif operation == "write":
            return self._write_file(path, parameters, False)
        elif operation == "append":
            return self._write_file(path, parameters, True)
        elif operation == "delete":
            return self._delete_file(path, parameters)
        elif operation == "list":
            return self._list_directory(path, parameters)
        elif operation == "exists":
            return self._check_exists(path)
        elif operation == "info":
            return self._get_file_info(path)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    def _validate_path(self, path: str) -> str:
        """
        Validate and normalize a file path.
        
        Args:
            path: The path to validate
            
        Returns:
            The normalized path
            
        Raises:
            ValueError: If the path is outside the base directory
        """
        # Normalize path
        normalized_path = os.path.normpath(os.path.join(self.base_directory, path))
        
        # Check if path is within base directory
        if not normalized_path.startswith(self.base_directory):
            raise ValueError(f"Path '{path}' is outside the base directory")
        
        return normalized_path
    
    def _read_file(self, path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file."""
        binary = parameters.get("binary", False)
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            mode = "rb" if binary else "r"
            with open(path, mode) as f:
                content = f.read()
            
            if binary:
                # Encode binary content as base64
                content = base64.b64encode(content).decode("ascii")
                return {
                    "success": True,
                    "binary": True,
                    "content": content,
                    "encoding": "base64"
                }
            else:
                return {
                    "success": True,
                    "binary": False,
                    "content": content,
                    "encoding": encoding
                }
        
        except Exception as e:
            self.logger.error(f"Error reading file '{path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _write_file(self, path: str, parameters: Dict[str, Any], append: bool) -> Dict[str, Any]:
        """Write or append to a file."""
        content = parameters.get("content", "")
        binary = parameters.get("binary", False)
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            mode = "ab" if append and binary else "wb" if binary else "a" if append else "w"
            
            with open(path, mode) as f:
                if binary and isinstance(content, str):
                    # Decode base64 content
                    binary_content = base64.b64decode(content)
                    f.write(binary_content)
                elif binary:
                    f.write(content)
                else:
                    f.write(content)
            
            return {
                "success": True,
                "path": path,
                "size": os.path.getsize(path),
                "operation": "append" if append else "write"
            }
        
        except Exception as e:
            self.logger.error(f"Error writing to file '{path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _delete_file(self, path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file or directory."""
        recursive = parameters.get("recursive", False)
        
        try:
            if os.path.isdir(path):
                if recursive:
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
            else:
                os.remove(path)
            
            return {
                "success": True,
                "path": path,
                "was_directory": os.path.isdir(path)
            }
        
        except Exception as e:
            self.logger.error(f"Error deleting '{path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _list_directory(self, path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List contents of a directory."""
        recursive = parameters.get("recursive", False)
        
        try:
            if not os.path.isdir(path):
                return {
                    "success": False,
                    "error": f"Path '{path}' is not a directory"
                }
            
            if recursive:
                # Walk directory recursively
                results = []
                for root, dirs, files in os.walk(path):
                    for name in dirs:
                        full_path = os.path.join(root, name)
                        relative_path = os.path.relpath(full_path, path)
                        results.append({
                            "name": name,
                            "path": relative_path,
                            "type": "directory",
                            "size": 0
                        })
                    
                    for name in files:
                        full_path = os.path.join(root, name)
                        relative_path = os.path.relpath(full_path, path)
                        results.append({
                            "name": name,
                            "path": relative_path,
                            "type": "file",
                            "size": os.path.getsize(full_path)
                        })
            else:
                # List directory contents (non-recursive)
                results = []
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    is_dir = os.path.isdir(full_path)
                    results.append({
                        "name": name,
                        "path": name,
                        "type": "directory" if is_dir else "file",
                        "size": 0 if is_dir else os.path.getsize(full_path)
                    })
            
            return {
                "success": True,
                "path": path,
                "items": results,
                "count": len(results)
            }
        
        except Exception as e:
            self.logger.error(f"Error listing directory '{path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_exists(self, path: str) -> Dict[str, Any]:
        """Check if a file or directory exists."""
        exists = os.path.exists(path)
        
        if exists:
            is_dir = os.path.isdir(path)
            return {
                "success": True,
                "exists": True,
                "path": path,
                "type": "directory" if is_dir else "file"
            }
        else:
            return {
                "success": True,
                "exists": False,
                "path": path
            }
    
    def _get_file_info(self, path: str) -> Dict[str, Any]:
        """Get information about a file or directory."""
        try:
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"Path '{path}' does not exist"
                }
            
            is_dir = os.path.isdir(path)
            stat_info = os.stat(path)
            
            info = {
                "success": True,
                "path": path,
                "type": "directory" if is_dir else "file",
                "size": 0 if is_dir else stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "permissions": stat_info.st_mode
            }
            
            if not is_dir:
                info["extension"] = os.path.splitext(path)[1]
            
            return info
        
        except Exception as e:
            self.logger.error(f"Error getting info for '{path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
