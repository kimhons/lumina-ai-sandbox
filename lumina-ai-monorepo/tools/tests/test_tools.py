"""
Tool Integration Framework Tests for Lumina AI.

This module provides tests for the Tool Integration Framework components.
"""

import unittest
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

from tools.interface import Tool
from tools.base import BaseTool
from tools.registry.registry import ToolRegistry
from tools.manager import ToolManager
from tools.implementations.file_operations import FileOperationsTool
from tools.implementations.web_search import WebSearchTool
from tools.implementations.api_integration import APIIntegrationTool
from tools.implementations.data_analysis import DataAnalysisTool

class TestToolInterface(unittest.TestCase):
    """Tests for the Tool interface."""
    
    def test_tool_interface(self):
        """Test that Tool interface defines required methods."""
        methods = [
            'get_name',
            'get_description',
            'get_parameters',
            'get_required_permissions',
            'execute'
        ]
        
        for method in methods:
            self.assertTrue(hasattr(Tool, method), f"Tool interface missing method: {method}")

class TestBaseTool(unittest.TestCase):
    """Tests for the BaseTool implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = BaseTool(
            name="test_tool",
            description="Test tool for unit tests",
            parameters_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                },
                "required": ["param1"]
            },
            required_permissions=["test_permission"]
        )
    
    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.tool.get_name(), "test_tool")
    
    def test_get_description(self):
        """Test get_description method."""
        self.assertEqual(self.tool.get_description(), "Test tool for unit tests")
    
    def test_get_parameters(self):
        """Test get_parameters method."""
        params = self.tool.get_parameters()
        self.assertEqual(params["type"], "object")
        self.assertIn("param1", params["properties"])
        self.assertIn("param2", params["properties"])
        self.assertIn("param1", params["required"])
    
    def test_get_required_permissions(self):
        """Test get_required_permissions method."""
        self.assertEqual(self.tool.get_required_permissions(), ["test_permission"])
    
    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        valid_params = {"param1": "test", "param2": 42}
        self.assertTrue(self.tool._validate_parameters(valid_params))
    
    def test_validate_parameters_invalid(self):
        """Test parameter validation with invalid parameters."""
        # Missing required parameter
        invalid_params = {"param2": 42}
        self.assertFalse(self.tool._validate_parameters(invalid_params))
        
        # Wrong type
        invalid_params = {"param1": "test", "param2": "not_an_integer"}
        self.assertFalse(self.tool._validate_parameters(invalid_params))
    
    def test_execute(self):
        """Test execute method."""
        # Mock _execute_tool method
        self.tool._execute_tool = MagicMock(return_value={"result": "success"})
        
        # Test with valid parameters
        result = self.tool.execute({"param1": "test", "param2": 42})
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], {"result": "success"})
        self.tool._execute_tool.assert_called_once()
        
        # Test with invalid parameters
        self.tool._execute_tool.reset_mock()
        result = self.tool.execute({"param2": 42})  # Missing required param
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.tool._execute_tool.assert_not_called()

class TestToolRegistry(unittest.TestCase):
    """Tests for the ToolRegistry."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
        
        # Create test tools
        self.tool1 = BaseTool(
            name="tool1",
            description="Test tool 1",
            parameters_schema={"type": "object"},
            required_permissions=[]
        )
        
        self.tool2 = BaseTool(
            name="tool2",
            description="Test tool 2",
            parameters_schema={"type": "object"},
            required_permissions=[]
        )
    
    def test_register_tool(self):
        """Test registering a tool."""
        # Register tool with categories
        success = self.registry.register_tool(self.tool1, ["category1", "category2"])
        self.assertTrue(success)
        
        # Check that tool is registered
        self.assertIn("tool1", self.registry.get_all_tools())
        
        # Check categories
        self.assertIn("category1", self.registry.get_categories())
        self.assertIn("category2", self.registry.get_categories())
        self.assertIn("tool1", self.registry.get_tools_by_category("category1"))
        self.assertIn("tool1", self.registry.get_tools_by_category("category2"))
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        # Register tools
        self.registry.register_tool(self.tool1, ["category1"])
        self.registry.register_tool(self.tool2, ["category1"])
        
        # Unregister tool1
        success = self.registry.unregister_tool("tool1")
        self.assertTrue(success)
        
        # Check that tool1 is unregistered
        self.assertNotIn("tool1", self.registry.get_all_tools())
        self.assertNotIn("tool1", self.registry.get_tools_by_category("category1"))
        
        # Check that tool2 is still registered
        self.assertIn("tool2", self.registry.get_all_tools())
        self.assertIn("tool2", self.registry.get_tools_by_category("category1"))
    
    def test_get_tool(self):
        """Test getting a tool."""
        # Register tool
        self.registry.register_tool(self.tool1)
        
        # Get tool
        tool = self.registry.get_tool("tool1")
        self.assertEqual(tool, self.tool1)
        
        # Get non-existent tool
        tool = self.registry.get_tool("non_existent")
        self.assertIsNone(tool)
    
    def test_get_tool_categories(self):
        """Test getting tool categories."""
        # Register tool with categories
        self.registry.register_tool(self.tool1, ["category1", "category2"])
        
        # Get categories
        categories = self.registry.get_tool_categories("tool1")
        self.assertIn("category1", categories)
        self.assertIn("category2", categories)
        
        # Get categories for non-existent tool
        categories = self.registry.get_tool_categories("non_existent")
        self.assertEqual(categories, [])
    
    def test_save_load_registry(self):
        """Test saving and loading the registry."""
        # Register tools
        self.registry.register_tool(self.tool1, ["category1"])
        self.registry.register_tool(self.tool2, ["category2"])
        
        # Save registry to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        
        try:
            self.registry.save_registry(temp_path)
            
            # Create new registry and load from file
            new_registry = ToolRegistry()
            new_registry.load_registry(temp_path)
            
            # Check that tools and categories are loaded
            self.assertIn("tool1", new_registry.get_all_tools())
            self.assertIn("tool2", new_registry.get_all_tools())
            self.assertIn("category1", new_registry.get_categories())
            self.assertIn("category2", new_registry.get_categories())
            self.assertIn("tool1", new_registry.get_tools_by_category("category1"))
            self.assertIn("tool2", new_registry.get_tools_by_category("category2"))
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

class TestToolManager(unittest.TestCase):
    """Tests for the ToolManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ToolManager()
        
        # Create test tools
        self.tool1 = BaseTool(
            name="tool1",
            description="Test tool 1",
            parameters_schema={"type": "object"},
            required_permissions=["permission1"]
        )
        
        self.tool2 = BaseTool(
            name="tool2",
            description="Test tool 2",
            parameters_schema={"type": "object"},
            required_permissions=["permission2"]
        )
        
        # Mock _execute_tool methods
        self.tool1._execute_tool = MagicMock(return_value={"result": "tool1_result"})
        self.tool2._execute_tool = MagicMock(return_value={"result": "tool2_result"})
    
    def test_register_unregister_tool(self):
        """Test registering and unregistering tools."""
        # Register tools
        self.manager.register_tool(self.tool1, ["category1"])
        self.manager.register_tool(self.tool2, ["category2"])
        
        # Check that tools are registered
        tools = self.manager.get_available_tools()
        self.assertIn("tool1", tools)
        self.assertIn("tool2", tools)
        
        # Unregister tool1
        success = self.manager.unregister_tool("tool1")
        self.assertTrue(success)
        
        # Check that tool1 is unregistered
        tools = self.manager.get_available_tools()
        self.assertNotIn("tool1", tools)
        self.assertIn("tool2", tools)
    
    def test_execute_tool(self):
        """Test executing a tool."""
        # Register tool
        self.manager.register_tool(self.tool1)
        
        # Execute tool with sufficient permissions
        result = self.manager.execute_tool("tool1", {}, {"permission1"})
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], {"result": "tool1_result"})
        
        # Execute tool with insufficient permissions
        result = self.manager.execute_tool("tool1", {}, {"other_permission"})
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Execute non-existent tool
        result = self.manager.execute_tool("non_existent", {})
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_get_available_tools(self):
        """Test getting available tools."""
        # Register tools
        self.manager.register_tool(self.tool1, ["category1"])
        self.manager.register_tool(self.tool2, ["category2"])
        
        # Get all tools (no permission filtering)
        tools = self.manager.get_available_tools()
        self.assertIn("tool1", tools)
        self.assertIn("tool2", tools)
        
        # Get tools with permission filtering
        tools = self.manager.get_available_tools({"permission1"})
        self.assertIn("tool1", tools)
        self.assertNotIn("tool2", tools)
        
        tools = self.manager.get_available_tools({"permission2"})
        self.assertNotIn("tool1", tools)
        self.assertIn("tool2", tools)
        
        tools = self.manager.get_available_tools({"permission1", "permission2"})
        self.assertIn("tool1", tools)
        self.assertIn("tool2", tools)
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        # Register tools
        self.manager.register_tool(self.tool1, ["category1"])
        self.manager.register_tool(self.tool2, ["category1", "category2"])
        
        # Get tools by category (no permission filtering)
        tools = self.manager.get_tools_by_category("category1")
        self.assertIn("tool1", tools)
        self.assertIn("tool2", tools)
        
        tools = self.manager.get_tools_by_category("category2")
        self.assertNotIn("tool1", tools)
        self.assertIn("tool2", tools)
        
        # Get tools by category with permission filtering
        tools = self.manager.get_tools_by_category("category1", {"permission1"})
        self.assertIn("tool1", tools)
        self.assertNotIn("tool2", tools)
        
        tools = self.manager.get_tools_by_category("category1", {"permission2"})
        self.assertNotIn("tool1", tools)
        self.assertIn("tool2", tools)

class TestToolImplementations(unittest.TestCase):
    """Tests for the concrete tool implementations."""
    
    def test_file_operations_tool(self):
        """Test FileOperationsTool."""
        # Create tool
        tool = FileOperationsTool()
        
        # Check basic properties
        self.assertEqual(tool.get_name(), "file_operations")
        self.assertIn("file_system", tool.get_required_permissions())
        
        # Test with temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Test write operation
            write_params = {
                "operation": "write",
                "path": temp_path,
                "content": "test content"
            }
            result = tool.execute(write_params)
            self.assertTrue(result["success"])
            
            # Test read operation
            read_params = {
                "operation": "read",
                "path": temp_path
            }
            result = tool.execute(read_params)
            self.assertTrue(result["success"])
            self.assertEqual(result["content"], "test content")
            
            # Test exists operation
            exists_params = {
                "operation": "exists",
                "path": temp_path
            }
            result = tool.execute(exists_params)
            self.assertTrue(result["success"])
            self.assertTrue(result["exists"])
            
            # Test delete operation
            delete_params = {
                "operation": "delete",
                "path": temp_path
            }
            result = tool.execute(delete_params)
            self.assertTrue(result["success"])
            
            # Verify file is deleted
            self.assertFalse(os.path.exists(temp_path))
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('tools.implementations.web_search.requests.get')
    def test_web_search_tool(self, mock_get):
        """Test WebSearchTool."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"title": "Result 1", "link": "http://example.com/1", "snippet": "Snippet 1"},
                {"title": "Result 2", "link": "http://example.com/2", "snippet": "Snippet 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Create tool
        tool = WebSearchTool()
        
        # Check basic properties
        self.assertEqual(tool.get_name(), "web_search")
        self.assertIn("internet_access", tool.get_required_permissions())
        
        # Test search operation
        search_params = {
            "query": "test query",
            "num_results": 2
        }
        result = tool.execute(search_params)
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["title"], "Result 1")
        self.assertEqual(result["results"][1]["title"], "Result 2")
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("test query", kwargs["params"]["q"])
    
    @patch('tools.implementations.api_integration.requests.request')
    def test_api_integration_tool(self, mock_request):
        """Test APIIntegrationTool."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.url = "http://example.com/api"
        mock_request.return_value = mock_response
        
        # Create tool
        tool = APIIntegrationTool()
        
        # Check basic properties
        self.assertEqual(tool.get_name(), "api_integration")
        self.assertIn("internet_access", tool.get_required_permissions())
        self.assertIn("api_access", tool.get_required_permissions())
        
        # Test API request
        request_params = {
            "method": "GET",
            "url": "http://example.com/api",
            "params": {"param1": "value1"},
            "headers": {"X-API-Key": "test_key"}
        }
        result = tool.execute(request_params)
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["content"]["data"], "test_data")
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], "http://example.com/api")
        self.assertEqual(kwargs["params"], {"param1": "value1"})
        self.assertEqual(kwargs["headers"], {"X-API-Key": "test_key"})

if __name__ == '__main__':
    unittest.main()
