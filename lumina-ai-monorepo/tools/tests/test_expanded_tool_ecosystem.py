"""
Tests for Lumina AI's Expanded Tool Ecosystem.

This module provides comprehensive tests for all components of the
Expanded Tool Ecosystem, including complex tool interactions, tool composition
and chaining, context-based recommendations, and the third-party marketplace.
"""

import unittest
import os
import tempfile
import json
import datetime
from typing import Dict, List, Any, Optional, Union, Set, Tuple

from tools.registry import ToolRegistry, ToolMetadata
from tools.execution import ToolExecutionEngine, ToolExecutor, ExecutionResult
from tools.interface import ToolInterface
from tools.discovery import ToolDiscovery
from tools.monitoring import ToolMonitoring
from tools.composition import CompositionEngine, ToolComposition, NodeType, Node, Edge
from tools.recommendation import (
    RecommendationEngine, ToolRecommendationContext, FeatureExtractor,
    ToolUsageHistory
)
from tools.marketplace import (
    ToolMarketplace, ToolVerifier, ToolDeveloper, MarketplaceTool,
    ToolCategory, ToolVerificationStatus, ToolPublishStatus
)

class TestToolRegistry(unittest.TestCase):
    """Tests for the Tool Registry component."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
    
    def test_register_tool(self):
        """Test registering a tool."""
        # Create a test tool
        tool = ToolMetadata(
            id="test-tool",
            name="Test Tool",
            description="A tool for testing",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        # Register the tool
        self.registry.register_tool(tool)
        
        # Check if tool was registered
        self.assertIn("test-tool", self.registry.tools)
        self.assertEqual(self.registry.tools["test-tool"].name, "Test Tool")
    
    def test_get_tool(self):
        """Test getting a tool."""
        # Create and register a test tool
        tool = ToolMetadata(
            id="test-tool",
            name="Test Tool",
            description="A tool for testing",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        self.registry.register_tool(tool)
        
        # Get the tool
        retrieved_tool = self.registry.get_tool("test-tool")
        
        # Check if the correct tool was retrieved
        self.assertIsNotNone(retrieved_tool)
        self.assertEqual(retrieved_tool.id, "test-tool")
        self.assertEqual(retrieved_tool.name, "Test Tool")
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        # Create and register a test tool
        tool = ToolMetadata(
            id="test-tool",
            name="Test Tool",
            description="A tool for testing",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        self.registry.register_tool(tool)
        
        # Unregister the tool
        self.registry.unregister_tool("test-tool")
        
        # Check if tool was unregistered
        self.assertNotIn("test-tool", self.registry.tools)
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        # Create and register test tools
        tool1 = ToolMetadata(
            id="test-tool-1",
            name="Test Tool 1",
            description="A tool for testing",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        tool2 = ToolMetadata(
            id="test-tool-2",
            name="Test Tool 2",
            description="Another tool for testing",
            version="1.0.0",
            categories=["analysis"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
        
        # Get tools by category
        testing_tools = self.registry.get_tools_by_category("testing")
        analysis_tools = self.registry.get_tools_by_category("analysis")
        
        # Check if the correct tools were retrieved
        self.assertEqual(len(testing_tools), 1)
        self.assertEqual(testing_tools[0].id, "test-tool-1")
        
        self.assertEqual(len(analysis_tools), 1)
        self.assertEqual(analysis_tools[0].id, "test-tool-2")
    
    def test_get_tools_by_tag(self):
        """Test getting tools by tag."""
        # Create and register test tools
        tool1 = ToolMetadata(
            id="test-tool-1",
            name="Test Tool 1",
            description="A tool for testing",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        tool2 = ToolMetadata(
            id="test-tool-2",
            name="Test Tool 2",
            description="Another tool for testing",
            version="1.0.0",
            categories=["analysis"],
            tags=["analysis", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1): return {'result': param1}"
        )
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
        
        # Get tools by tag
        test_tools = self.registry.get_tools_by_tag("test")
        example_tools = self.registry.get_tools_by_tag("example")
        analysis_tools = self.registry.get_tools_by_tag("analysis")
        
        # Check if the correct tools were retrieved
        self.assertEqual(len(test_tools), 1)
        self.assertEqual(test_tools[0].id, "test-tool-1")
        
        self.assertEqual(len(example_tools), 2)
        self.assertEqual(set(tool.id for tool in example_tools), {"test-tool-1", "test-tool-2"})
        
        self.assertEqual(len(analysis_tools), 1)
        self.assertEqual(analysis_tools[0].id, "test-tool-2")

class TestToolExecution(unittest.TestCase):
    """Tests for the Tool Execution component."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
        self.execution_engine = ToolExecutionEngine(self.registry)
        
        # Create and register a test tool
        tool = ToolMetadata(
            id="test-tool",
            name="Test Tool",
            description="A tool for testing",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="def execute(param1):\n    return {'result': param1}"
        )
        
        self.registry.register_tool(tool)
    
    def test_execute_tool(self):
        """Test executing a tool."""
        # Execute the tool
        result = self.execution_engine.execute_tool("test-tool", {"param1": "test value"})
        
        # Check if execution was successful
        self.assertTrue(result.success)
        self.assertEqual(result.result, {"result": "test value"})
    
    def test_execute_nonexistent_tool(self):
        """Test executing a nonexistent tool."""
        # Execute a nonexistent tool
        result = self.execution_engine.execute_tool("nonexistent-tool", {})
        
        # Check if execution failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_execute_tool_with_invalid_parameters(self):
        """Test executing a tool with invalid parameters."""
        # Execute the tool with missing parameters
        result = self.execution_engine.execute_tool("test-tool", {})
        
        # Check if execution failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_execute_tool_with_error(self):
        """Test executing a tool that raises an error."""
        # Create and register a tool that raises an error
        tool = ToolMetadata(
            id="error-tool",
            name="Error Tool",
            description="A tool that raises an error",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "error"],
            parameters={},
            implementation_type="python",
            implementation="def execute():\n    raise ValueError('Test error')"
        )
        
        self.registry.register_tool(tool)
        
        # Execute the tool
        result = self.execution_engine.execute_tool("error-tool", {})
        
        # Check if execution failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertIn("Test error", str(result.error))
    
    def test_async_execution(self):
        """Test asynchronous tool execution."""
        # Create and register a tool with a delay
        tool = ToolMetadata(
            id="async-tool",
            name="Async Tool",
            description="A tool that takes time to execute",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "async"],
            parameters={},
            implementation_type="python",
            implementation="def execute():\n    import time\n    time.sleep(0.1)\n    return {'result': 'done'}"
        )
        
        self.registry.register_tool(tool)
        
        # Execute the tool asynchronously
        execution_id = self.execution_engine.execute_tool_async("async-tool", {})
        
        # Check if execution is pending
        status = self.execution_engine.get_execution_status(execution_id)
        self.assertIn(status.status, ["pending", "running"])
        
        # Wait for execution to complete
        import time
        time.sleep(0.2)
        
        # Check if execution completed
        status = self.execution_engine.get_execution_status(execution_id)
        self.assertEqual(status.status, "completed")
        
        # Get the result
        result = self.execution_engine.get_execution_result(execution_id)
        
        # Check if execution was successful
        self.assertTrue(result.success)
        self.assertEqual(result.result, {"result": "done"})

class TestToolComposition(unittest.TestCase):
    """Tests for the Tool Composition component."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
        self.execution_engine = ToolExecutionEngine(self.registry)
        self.composition_engine = CompositionEngine(self.registry, self.execution_engine)
        
        # Create and register test tools
        tool1 = ToolMetadata(
            id="string-tool",
            name="String Tool",
            description="A tool that returns a string",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "string"],
            parameters={"input": {"type": "string", "description": "Input string"}},
            implementation_type="python",
            implementation="def execute(input):\n    return {'output': input.upper()}"
        )
        
        tool2 = ToolMetadata(
            id="length-tool",
            name="Length Tool",
            description="A tool that returns the length of a string",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "length"],
            parameters={"input": {"type": "string", "description": "Input string"}},
            implementation_type="python",
            implementation="def execute(input):\n    return {'length': len(input)}"
        )
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
    
    def test_create_composition(self):
        """Test creating a tool composition."""
        # Create a composition
        composition = ToolComposition("test-composition", "Test Composition")
        
        # Add nodes
        start_node = composition.add_node(NodeType.START, "start", {})
        string_node = composition.add_node(NodeType.TOOL, "string-tool", {"tool_id": "string-tool"})
        length_node = composition.add_node(NodeType.TOOL, "length-tool", {"tool_id": "length-tool"})
        end_node = composition.add_node(NodeType.END, "end", {})
        
        # Add edges
        composition.add_edge(start_node, string_node, {"output_mapping": {"input": "$.input"}})
        composition.add_edge(string_node, length_node, {"output_mapping": {"input": "$.output"}})
        composition.add_edge(length_node, end_node, {"output_mapping": {"result": "$.length"}})
        
        # Register the composition
        self.composition_engine.register_composition(composition)
        
        # Check if composition was registered
        self.assertIn("test-composition", self.composition_engine.compositions)
    
    def test_execute_composition(self):
        """Test executing a tool composition."""
        # Create a composition
        composition = ToolComposition("test-composition", "Test Composition")
        
        # Add nodes
        start_node = composition.add_node(NodeType.START, "start", {})
        string_node = composition.add_node(NodeType.TOOL, "string-tool", {"tool_id": "string-tool"})
        length_node = composition.add_node(NodeType.TOOL, "length-tool", {"tool_id": "length-tool"})
        end_node = composition.add_node(NodeType.END, "end", {})
        
        # Add edges
        composition.add_edge(start_node, string_node, {"output_mapping": {"input": "$.input"}})
        composition.add_edge(string_node, length_node, {"output_mapping": {"input": "$.output"}})
        composition.add_edge(length_node, end_node, {"output_mapping": {"result": "$.length"}})
        
        # Register the composition
        self.composition_engine.register_composition(composition)
        
        # Execute the composition
        result = self.composition_engine.execute_composition("test-composition", {"input": "hello"})
        
        # Check if execution was successful
        self.assertTrue(result.success)
        self.assertEqual(result.result, {"result": 5})
    
    def test_conditional_composition(self):
        """Test a composition with conditional execution."""
        # Create a composition
        composition = ToolComposition("conditional-composition", "Conditional Composition")
        
        # Add nodes
        start_node = composition.add_node(NodeType.START, "start", {})
        length_node = composition.add_node(NodeType.TOOL, "length-tool", {"tool_id": "length-tool"})
        condition_node = composition.add_node(NodeType.CONDITION, "condition", {"condition": "$.length > 5"})
        string_node = composition.add_node(NodeType.TOOL, "string-tool", {"tool_id": "string-tool"})
        end_node = composition.add_node(NodeType.END, "end", {})
        
        # Add edges
        composition.add_edge(start_node, length_node, {"output_mapping": {"input": "$.input"}})
        composition.add_edge(length_node, condition_node, {})
        composition.add_edge(condition_node, string_node, {"condition_result": True, "output_mapping": {"input": "$.input"}})
        composition.add_edge(condition_node, end_node, {"condition_result": False, "output_mapping": {"result": "$.length"}})
        composition.add_edge(string_node, end_node, {"output_mapping": {"result": "$.output"}})
        
        # Register the composition
        self.composition_engine.register_composition(composition)
        
        # Execute the composition with short input
        result1 = self.composition_engine.execute_composition("conditional-composition", {"input": "hello"})
        
        # Check if execution followed the false branch
        self.assertTrue(result1.success)
        self.assertEqual(result1.result, {"result": 5})
        
        # Execute the composition with long input
        result2 = self.composition_engine.execute_composition("conditional-composition", {"input": "hello world"})
        
        # Check if execution followed the true branch
        self.assertTrue(result2.success)
        self.assertEqual(result2.result, {"result": "HELLO WORLD"})
    
    def test_loop_composition(self):
        """Test a composition with a loop."""
        # Create and register a counter tool
        counter_tool = ToolMetadata(
            id="counter-tool",
            name="Counter Tool",
            description="A tool that counts",
            version="1.0.0",
            categories=["testing"],
            tags=["test", "counter"],
            parameters={"count": {"type": "integer", "description": "Current count"}},
            implementation_type="python",
            implementation="def execute(count):\n    return {'count': count + 1, 'original': count}"
        )
        
        self.registry.register_tool(counter_tool)
        
        # Create a composition
        composition = ToolComposition("loop-composition", "Loop Composition")
        
        # Add nodes
        start_node = composition.add_node(NodeType.START, "start", {})
        counter_node = composition.add_node(NodeType.TOOL, "counter-tool", {"tool_id": "counter-tool"})
        condition_node = composition.add_node(NodeType.CONDITION, "condition", {"condition": "$.count < 5"})
        end_node = composition.add_node(NodeType.END, "end", {})
        
        # Add edges
        composition.add_edge(start_node, counter_node, {"output_mapping": {"count": "$.count"}})
        composition.add_edge(counter_node, condition_node, {})
        composition.add_edge(condition_node, counter_node, {"condition_result": True, "output_mapping": {"count": "$.count"}})
        composition.add_edge(condition_node, end_node, {"condition_result": False, "output_mapping": {"result": "$.count"}})
        
        # Register the composition
        self.composition_engine.register_composition(composition)
        
        # Execute the composition
        result = self.composition_engine.execute_composition("loop-composition", {"count": 0})
        
        # Check if execution was successful and looped the correct number of times
        self.assertTrue(result.success)
        self.assertEqual(result.result, {"result": 5})

class TestToolRecommendation(unittest.TestCase):
    """Tests for the Tool Recommendation component."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
        self.execution_engine = ToolExecutionEngine(self.registry)
        self.monitoring = ToolMonitoring()
        self.recommendation_engine = RecommendationEngine(self.registry, self.execution_engine, self.monitoring)
        
        # Create and register test tools
        tool1 = ToolMetadata(
            id="string-tool",
            name="String Tool",
            description="A tool that processes strings",
            version="1.0.0",
            categories=["data_processing"],
            tags=["string", "text", "process"],
            parameters={"input": {"type": "string", "description": "Input string"}},
            implementation_type="python",
            implementation="def execute(input):\n    return {'output': input.upper()}"
        )
        
        tool2 = ToolMetadata(
            id="email-tool",
            name="Email Tool",
            description="A tool that sends emails",
            version="1.0.0",
            categories=["communication"],
            tags=["email", "send", "message"],
            parameters={"to": {"type": "string", "description": "Recipient email"}, "subject": {"type": "string", "description": "Email subject"}, "body": {"type": "string", "description": "Email body"}},
            implementation_type="python",
            implementation="def execute(to, subject, body):\n    return {'status': 'sent'}"
        )
        
        tool3 = ToolMetadata(
            id="file-tool",
            name="File Tool",
            description="A tool that manages files",
            version="1.0.0",
            categories=["file_management"],
            tags=["file", "read", "write"],
            parameters={"path": {"type": "string", "description": "File path"}, "content": {"type": "string", "description": "File content"}},
            implementation_type="python",
            implementation="def execute(path, content=None):\n    if content:\n        return {'status': 'written'}\n    else:\n        return {'content': 'file content'}"
        )
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
        self.registry.register_tool(tool3)
    
    def test_feature_extraction(self):
        """Test feature extraction from context."""
        # Create a context
        context = ToolRecommendationContext(
            user_id="test-user",
            task_description="I need to send an email to john@example.com",
            input_data={"email": "john@example.com", "message": "Hello, John!"}
        )
        
        # Extract features
        feature_extractor = FeatureExtractor()
        feature_extractor.extract_features(context)
        
        # Check if features were extracted
        self.assertIsNotNone(context.get_feature("keywords"))
        self.assertIsNotNone(context.get_feature("categories"))
        self.assertIsNotNone(context.get_feature("entities"))
        self.assertIsNotNone(context.get_feature("actions"))
        
        # Check specific features
        keywords = context.get_feature("keywords").value
        self.assertIn("email", keywords)
        self.assertIn("send", keywords)
        
        categories = context.get_feature("categories").value
        self.assertIn("communication", categories)
        
        entities = context.get_feature("entities").value
        self.assertIn("john@example.com", entities)
        
        actions = context.get_feature("actions").value
        self.assertIn("send", actions)
    
    def test_tool_recommendation(self):
        """Test tool recommendation based on context."""
        # Create a context
        context = ToolRecommendationContext(
            user_id="test-user",
            task_description="I need to send an email to john@example.com",
            input_data={"email": "john@example.com", "message": "Hello, John!"}
        )
        
        # Get recommendations
        recommendations = self.recommendation_engine.recommend_tools(context)
        
        # Check if recommendations were generated
        self.assertGreater(len(recommendations), 0)
        
        # Check if the email tool was recommended
        email_tool_recommended = any(rec.tool_id == "email-tool" for rec in recommendations)
        self.assertTrue(email_tool_recommended)
        
        # Check if the email tool has a high score
        email_tool_rec = next((rec for rec in recommendations if rec.tool_id == "email-tool"), None)
        self.assertIsNotNone(email_tool_rec)
        self.assertGreater(email_tool_rec.score, 0.3)
    
    def test_parameter_suggestion(self):
        """Test parameter suggestion for recommended tools."""
        # Create a context
        context = ToolRecommendationContext(
            user_id="test-user",
            task_description="I need to send an email to john@example.com with subject 'Hello'",
            input_data={"email": "john@example.com", "subject": "Hello", "message": "Hello, John!"}
        )
        
        # Get recommendations
        recommendations = self.recommendation_engine.recommend_tools(context)
        
        # Find the email tool recommendation
        email_tool_rec = next((rec for rec in recommendations if rec.tool_id == "email-tool"), None)
        self.assertIsNotNone(email_tool_rec)
        
        # Check if parameters were suggested
        self.assertIn("to", email_tool_rec.parameters)
        self.assertEqual(email_tool_rec.parameters["to"], "john@example.com")
        
        self.assertIn("subject", email_tool_rec.parameters)
        self.assertEqual(email_tool_rec.parameters["subject"], "Hello")
    
    def test_usage_history(self):
        """Test tool usage history tracking."""
        # Create a usage history
        history = ToolUsageHistory("test-user")
        
        # Record tool usage
        history.record_usage("string-tool", True)
        history.record_usage("email-tool", True)
        history.record_usage("file-tool", False)
        history.record_usage("string-tool", True)
        
        # Check usage counts
        self.assertEqual(history.get_usage_count("string-tool"), 2)
        self.assertEqual(history.get_usage_count("email-tool"), 1)
        self.assertEqual(history.get_usage_count("file-tool"), 1)
        
        # Check success rates
        self.assertEqual(history.get_success_rate("string-tool"), 1.0)
        self.assertEqual(history.get_success_rate("email-tool"), 1.0)
        self.assertEqual(history.get_success_rate("file-tool"), 0.0)
        
        # Record a sequence
        history.record_usage("string-tool", True)
        history.record_usage("email-tool", True)
        history.end_sequence()
        
        history.record_usage("string-tool", True)
        history.record_usage("email-tool", True)
        history.end_sequence()
        
        # Check common sequences
        common_sequences = history.get_common_sequences()
        self.assertEqual(len(common_sequences), 1)
        self.assertEqual(common_sequences[0], ["string-tool", "email-tool"])

class TestToolMarketplace(unittest.TestCase):
    """Tests for the Tool Marketplace component."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
        self.execution_engine = ToolExecutionEngine(self.registry)
        
        # Create a temporary directory for marketplace data
        self.temp_dir = tempfile.mkdtemp()
        self.marketplace = ToolMarketplace(self.registry, self.execution_engine, self.temp_dir)
        
        # Register a test developer
        self.developer_id = self.marketplace.register_developer(
            name="Test Developer",
            email="developer@example.com",
            organization="Test Organization",
            website="https://example.com"
        )
        
        # Verify the developer
        self.marketplace.verify_developer(self.developer_id)
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_publish_tool(self):
        """Test publishing a tool to the marketplace."""
        # Publish a tool
        tool_id, issues = self.marketplace.publish_tool(
            name="Test Tool",
            description="A tool for testing with proper error handling and validation",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="""def execute(param1):
    try:
        if param1 is None:
            raise ValueError("param1 cannot be None")
        return {'result': param1}
    except Exception as e:
        raise Exception(f"Error processing param1: {e}")
""",
            documentation_url="https://example.com/docs",
            icon_url="https://example.com/icon.png"
        )
        
        # Check if tool was published
        self.assertIsNotNone(tool_id)
        self.assertIn(tool_id, self.marketplace.tools)
        
        # Check if there are no issues
        self.assertEqual(len(issues), 0)
        
        # Check if tool is in developer's tools
        self.assertIn(tool_id, self.marketplace.developers[self.developer_id].tools)
    
    def test_tool_verification(self):
        """Test tool verification."""
        # Publish a tool with security issues
        tool_id, issues = self.marketplace.publish_tool(
            name="Insecure Tool",
            description="A tool with security issues",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["testing"],
            tags=["test", "insecure"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="""def execute(param1):
    import os
    os.system("echo " + param1)
    return {'result': 'done'}
""",
            documentation_url="https://example.com/docs"
        )
        
        # Check if tool was published but has issues
        self.assertIsNotNone(tool_id)
        self.assertGreater(len(issues), 0)
        
        # Check if tool is pending verification
        self.assertEqual(self.marketplace.tools[tool_id].verification_status, ToolVerificationStatus.PENDING)
    
    def test_search_tools(self):
        """Test searching for tools in the marketplace."""
        # Publish some tools
        tool_id1, _ = self.marketplace.publish_tool(
            name="String Tool",
            description="A tool that processes strings",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["data_processing"],
            tags=["string", "text", "process"],
            parameters={"input": {"type": "string", "description": "Input string"}},
            implementation_type="python",
            implementation="""def execute(input):
    try:
        return {'output': input.upper()}
    except Exception as e:
        raise Exception(f"Error processing input: {e}")
""",
            documentation_url="https://example.com/docs"
        )
        
        tool_id2, _ = self.marketplace.publish_tool(
            name="Email Tool",
            description="A tool that sends emails",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["communication"],
            tags=["email", "send", "message"],
            parameters={"to": {"type": "string", "description": "Recipient email"}},
            implementation_type="python",
            implementation="""def execute(to):
    try:
        if not to:
            raise ValueError("Recipient email is required")
        return {'status': 'sent'}
    except Exception as e:
        raise Exception(f"Error sending email: {e}")
""",
            documentation_url="https://example.com/docs"
        )
        
        # Set tools to published status
        self.marketplace.tools[tool_id1].publish_status = ToolPublishStatus.PUBLISHED
        self.marketplace.tools[tool_id2].publish_status = ToolPublishStatus.PUBLISHED
        
        # Search for tools
        results = self.marketplace.search_tools(query="string")
        
        # Check if the correct tool was found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "String Tool")
        
        # Search by category
        results = self.marketplace.search_tools(categories=["communication"])
        
        # Check if the correct tool was found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Email Tool")
        
        # Search by tag
        results = self.marketplace.search_tools(tags=["email"])
        
        # Check if the correct tool was found
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Email Tool")
    
    def test_install_tool(self):
        """Test installing a tool from the marketplace."""
        # Publish a tool
        tool_id, _ = self.marketplace.publish_tool(
            name="Test Tool",
            description="A tool for testing with proper error handling and validation",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="""def execute(param1):
    try:
        if param1 is None:
            raise ValueError("param1 cannot be None")
        return {'result': param1}
    except Exception as e:
        raise Exception(f"Error processing param1: {e}")
""",
            documentation_url="https://example.com/docs"
        )
        
        # Set tool to published and approved status
        self.marketplace.tools[tool_id].publish_status = ToolPublishStatus.PUBLISHED
        self.marketplace.tools[tool_id].verification_status = ToolVerificationStatus.APPROVED
        
        # Install the tool
        success = self.marketplace.install_tool(tool_id)
        
        # Check if installation was successful
        self.assertTrue(success)
        
        # Check if tool was registered in the registry
        self.assertIn(tool_id, self.registry.tools)
        
        # Check if download count was incremented
        self.assertEqual(self.marketplace.tools[tool_id].downloads, 1)
    
    def test_rate_tool(self):
        """Test rating a tool in the marketplace."""
        # Publish a tool
        tool_id, _ = self.marketplace.publish_tool(
            name="Test Tool",
            description="A tool for testing",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["testing"],
            tags=["test", "example"],
            parameters={"param1": {"type": "string", "description": "A test parameter"}},
            implementation_type="python",
            implementation="""def execute(param1):
    try:
        return {'result': param1}
    except Exception as e:
        raise Exception(f"Error: {e}")
""",
            documentation_url="https://example.com/docs"
        )
        
        # Rate the tool
        success = self.marketplace.rate_tool(
            tool_id=tool_id,
            user_id="test-user",
            rating=5,
            review="Great tool!"
        )
        
        # Check if rating was successful
        self.assertTrue(success)
        
        # Check if rating was added to the tool
        self.assertEqual(len(self.marketplace.tools[tool_id].ratings), 1)
        self.assertEqual(self.marketplace.tools[tool_id].ratings[0].rating, 5)
        self.assertEqual(self.marketplace.tools[tool_id].ratings[0].review, "Great tool!")
        
        # Check if average rating was updated
        self.assertEqual(self.marketplace.tools[tool_id].average_rating, 5.0)
        
        # Add another rating
        self.marketplace.rate_tool(
            tool_id=tool_id,
            user_id="another-user",
            rating=3,
            review="Decent tool"
        )
        
        # Check if average rating was updated
        self.assertEqual(self.marketplace.tools[tool_id].average_rating, 4.0)

class TestIntegration(unittest.TestCase):
    """Integration tests for the Expanded Tool Ecosystem."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
        self.execution_engine = ToolExecutionEngine(self.registry)
        self.composition_engine = CompositionEngine(self.registry, self.execution_engine)
        self.monitoring = ToolMonitoring()
        self.recommendation_engine = RecommendationEngine(self.registry, self.execution_engine, self.monitoring)
        
        # Set composition engine in recommendation engine
        self.recommendation_engine.set_composition_engine(self.composition_engine)
        
        # Create a temporary directory for marketplace data
        self.temp_dir = tempfile.mkdtemp()
        self.marketplace = ToolMarketplace(self.registry, self.execution_engine, self.temp_dir)
        
        # Register a test developer
        self.developer_id = self.marketplace.register_developer(
            name="Test Developer",
            email="developer@example.com",
            organization="Test Organization",
            website="https://example.com"
        )
        
        # Verify the developer
        self.marketplace.verify_developer(self.developer_id)
        
        # Create and register test tools
        tool1 = ToolMetadata(
            id="string-tool",
            name="String Tool",
            description="A tool that processes strings",
            version="1.0.0",
            categories=["data_processing"],
            tags=["string", "text", "process"],
            parameters={"input": {"type": "string", "description": "Input string"}},
            implementation_type="python",
            implementation="def execute(input):\n    return {'output': input.upper()}"
        )
        
        tool2 = ToolMetadata(
            id="length-tool",
            name="Length Tool",
            description="A tool that returns the length of a string",
            version="1.0.0",
            categories=["data_processing"],
            tags=["string", "length"],
            parameters={"input": {"type": "string", "description": "Input string"}},
            implementation_type="python",
            implementation="def execute(input):\n    return {'length': len(input)}"
        )
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test an end-to-end workflow using all components."""
        # 1. Publish a tool to the marketplace
        tool_id, issues = self.marketplace.publish_tool(
            name="Email Validator",
            description="A tool that validates email addresses",
            version="1.0.0",
            developer_id=self.developer_id,
            categories=["data_processing", "communication"],
            tags=["email", "validation"],
            parameters={"email": {"type": "string", "description": "Email address to validate"}},
            implementation_type="python",
            implementation="""def execute(email):
    try:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))
        return {'is_valid': is_valid, 'email': email}
    except Exception as e:
        raise Exception(f"Error validating email: {e}")
""",
            documentation_url="https://example.com/docs"
        )
        
        # Set tool to published and approved status
        self.marketplace.tools[tool_id].publish_status = ToolPublishStatus.PUBLISHED
        self.marketplace.tools[tool_id].verification_status = ToolVerificationStatus.APPROVED
        
        # 2. Install the tool
        self.marketplace.install_tool(tool_id)
        
        # 3. Create a composition using the installed tool
        composition = ToolComposition("email-workflow", "Email Workflow")
        
        # Add nodes
        start_node = composition.add_node(NodeType.START, "start", {})
        validator_node = composition.add_node(NodeType.TOOL, "validator", {"tool_id": "email-validator"})
        condition_node = composition.add_node(NodeType.CONDITION, "condition", {"condition": "$.is_valid"})
        string_node = composition.add_node(NodeType.TOOL, "string-tool", {"tool_id": "string-tool"})
        end_node = composition.add_node(NodeType.END, "end", {})
        
        # Add edges
        composition.add_edge(start_node, validator_node, {"output_mapping": {"email": "$.email"}})
        composition.add_edge(validator_node, condition_node, {})
        composition.add_edge(condition_node, string_node, {"condition_result": True, "output_mapping": {"input": "$.email"}})
        composition.add_edge(condition_node, end_node, {"condition_result": False, "output_mapping": {"result": "Invalid email"}})
        composition.add_edge(string_node, end_node, {"output_mapping": {"result": "$.output"}})
        
        # Register the composition
        self.composition_engine.register_composition(composition)
        
        # 4. Get recommendations based on context
        context = ToolRecommendationContext(
            user_id="test-user",
            task_description="I need to validate and process an email address",
            input_data={"email": "test@example.com"}
        )
        
        recommendations = self.recommendation_engine.recommend_tools(context)
        
        # Check if the email validator tool was recommended
        validator_recommended = any(rec.tool_id == "email-validator" for rec in recommendations)
        self.assertTrue(validator_recommended)
        
        # Get composition recommendations
        composition_recommendations = self.recommendation_engine.recommend_compositions(context)
        
        # Check if the email workflow composition was recommended
        workflow_recommended = any(rec.composition_id == "email-workflow" for rec in composition_recommendations)
        self.assertTrue(workflow_recommended)
        
        # 5. Execute the recommended composition
        result = self.composition_engine.execute_composition("email-workflow", {"email": "test@example.com"})
        
        # Check if execution was successful
        self.assertTrue(result.success)
        self.assertEqual(result.result, {"result": "TEST@EXAMPLE.COM"})
        
        # 6. Record tool usage
        self.recommendation_engine.record_tool_usage("test-user", "email-validator", True, context)
        
        # 7. Rate the tool
        self.marketplace.rate_tool(
            tool_id="email-validator",
            user_id="test-user",
            rating=5,
            review="Works perfectly!"
        )
        
        # Check if rating was added
        self.assertEqual(self.marketplace.tools["email-validator"].average_rating, 5.0)

if __name__ == "__main__":
    unittest.main()
