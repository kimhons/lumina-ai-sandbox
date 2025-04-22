"""
Tool Composition module for Lumina AI's Expanded Tool Ecosystem.

This module provides functionality for creating and executing tool chains and compositions,
with support for sequential execution, conditional branching, and data flow management.
"""

import uuid
import datetime
import time
import copy
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
import logging

from .registry import ToolRegistry, ToolMetadata
from .execution import ToolExecutionEngine, ToolExecutionResult, ToolExecutionStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeType(Enum):
    """Types of nodes in a composition graph."""
    TOOL = "tool"
    START = "start"
    END = "end"
    CONDITION = "condition"
    TRANSFORM = "transform"
    MERGE = "merge"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"

class EdgeType(Enum):
    """Types of edges in a composition graph."""
    NORMAL = "normal"
    CONDITIONAL_TRUE = "conditional_true"
    CONDITIONAL_FALSE = "conditional_false"
    LOOP_ITERATION = "loop_iteration"
    LOOP_EXIT = "loop_exit"

class CompositionNode:
    """Node in a tool composition graph."""
    
    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        config: Dict[str, Any] = None
    ):
        """
        Initialize composition node.
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node
            name: Node name
            config: Node configuration
        """
        self.id = node_id
        self.type = node_type
        self.name = name
        self.config = config or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompositionNode':
        """Create node from dictionary."""
        return cls(
            node_id=data["id"],
            node_type=NodeType(data["type"]),
            name=data["name"],
            config=data.get("config", {})
        )

class CompositionEdge:
    """Edge in a tool composition graph."""
    
    def __init__(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.NORMAL,
        data_mapping: Dict[str, str] = None
    ):
        """
        Initialize composition edge.
        
        Args:
            edge_id: Unique edge identifier
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of edge
            data_mapping: Mapping from source to target parameters
        """
        self.id = edge_id
        self.source_id = source_id
        self.target_id = target_id
        self.type = edge_type
        self.data_mapping = data_mapping or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "data_mapping": self.data_mapping
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompositionEdge':
        """Create edge from dictionary."""
        return cls(
            edge_id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=EdgeType(data["type"]),
            data_mapping=data.get("data_mapping", {})
        )

class CompositionStatus(Enum):
    """Status of a tool composition execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeExecutionStatus(Enum):
    """Status of a node execution within a composition."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class NodeExecutionResult:
    """Result of a node execution within a composition."""
    
    def __init__(
        self,
        node_id: str,
        status: NodeExecutionStatus,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        execution_time: Optional[float] = None
    ):
        """
        Initialize node execution result.
        
        Args:
            node_id: Node ID
            status: Execution status
            output: Node output
            error: Error message
            start_time: Start time
            end_time: End time
            execution_time: Execution time in seconds
        """
        self.node_id = node_id
        self.status = status
        self.output = output
        self.error = error
        self.start_time = start_time
        self.end_time = end_time
        self.execution_time = execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "node_id": self.node_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time
        }

class CompositionExecutionResult:
    """Result of a tool composition execution."""
    
    def __init__(
        self,
        composition_id: str,
        execution_id: str,
        status: CompositionStatus,
        node_results: Dict[str, NodeExecutionResult] = None,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        execution_time: Optional[float] = None
    ):
        """
        Initialize composition execution result.
        
        Args:
            composition_id: Composition ID
            execution_id: Execution ID
            status: Execution status
            node_results: Results for individual nodes
            output: Final output
            error: Error message
            start_time: Start time
            end_time: End time
            execution_time: Execution time in seconds
        """
        self.composition_id = composition_id
        self.execution_id = execution_id
        self.status = status
        self.node_results = node_results or {}
        self.output = output
        self.error = error
        self.start_time = start_time
        self.end_time = end_time
        self.execution_time = execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "composition_id": self.composition_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "node_results": {
                node_id: result.to_dict()
                for node_id, result in self.node_results.items()
            },
            "output": self.output,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time
        }

class ToolComposition:
    """
    Represents a composition of tools as a directed graph.
    
    Provides functionality for:
    - Defining tool compositions with nodes and edges
    - Validating composition structure and data flow
    - Serializing and deserializing compositions
    - Versioning and tracking composition changes
    """
    
    def __init__(
        self,
        composition_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
        author: str = "Lumina AI"
    ):
        """
        Initialize tool composition.
        
        Args:
            composition_id: Unique composition identifier
            name: Composition name
            description: Composition description
            version: Composition version
            author: Composition author
        """
        self.id = composition_id
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        
        self.nodes: Dict[str, CompositionNode] = {}
        self.edges: Dict[str, CompositionEdge] = {}
        
        # Create start and end nodes
        start_id = str(uuid.uuid4())
        end_id = str(uuid.uuid4())
        
        self.start_node_id = start_id
        self.end_node_id = end_id
        
        self.nodes[start_id] = CompositionNode(
            node_id=start_id,
            node_type=NodeType.START,
            name="Start"
        )
        
        self.nodes[end_id] = CompositionNode(
            node_id=end_id,
            node_type=NodeType.END,
            name="End"
        )
    
    def add_tool_node(
        self,
        tool_id: str,
        name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Add a tool node to the composition.
        
        Args:
            tool_id: Tool ID
            name: Node name (defaults to tool ID)
            config: Node configuration
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        if name is None:
            name = f"Tool: {tool_id}"
        
        node_config = config or {}
        node_config["tool_id"] = tool_id
        
        self.nodes[node_id] = CompositionNode(
            node_id=node_id,
            node_type=NodeType.TOOL,
            name=name,
            config=node_config
        )
        
        self.updated_at = datetime.datetime.now()
        
        return node_id
    
    def add_condition_node(
        self,
        condition_expression: str,
        name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Add a condition node to the composition.
        
        Args:
            condition_expression: Expression to evaluate
            name: Node name
            config: Node configuration
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        if name is None:
            name = f"Condition: {condition_expression}"
        
        node_config = config or {}
        node_config["condition_expression"] = condition_expression
        
        self.nodes[node_id] = CompositionNode(
            node_id=node_id,
            node_type=NodeType.CONDITION,
            name=name,
            config=node_config
        )
        
        self.updated_at = datetime.datetime.now()
        
        return node_id
    
    def add_transform_node(
        self,
        transform_expression: str,
        name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Add a transform node to the composition.
        
        Args:
            transform_expression: Expression for data transformation
            name: Node name
            config: Node configuration
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        if name is None:
            name = f"Transform: {transform_expression}"
        
        node_config = config or {}
        node_config["transform_expression"] = transform_expression
        
        self.nodes[node_id] = CompositionNode(
            node_id=node_id,
            node_type=NodeType.TRANSFORM,
            name=name,
            config=node_config
        )
        
        self.updated_at = datetime.datetime.now()
        
        return node_id
    
    def add_merge_node(
        self,
        name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Add a merge node to the composition.
        
        Args:
            name: Node name
            config: Node configuration
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        if name is None:
            name = "Merge"
        
        self.nodes[node_id] = CompositionNode(
            node_id=node_id,
            node_type=NodeType.MERGE,
            name=name,
            config=config or {}
        )
        
        self.updated_at = datetime.datetime.now()
        
        return node_id
    
    def add_loop_start_node(
        self,
        loop_variable: str,
        iterable_expression: str,
        name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Add a loop start node to the composition.
        
        Args:
            loop_variable: Variable name for loop iteration
            iterable_expression: Expression for iterable collection
            name: Node name
            config: Node configuration
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        if name is None:
            name = f"Loop Start: {loop_variable} in {iterable_expression}"
        
        node_config = config or {}
        node_config["loop_variable"] = loop_variable
        node_config["iterable_expression"] = iterable_expression
        
        self.nodes[node_id] = CompositionNode(
            node_id=node_id,
            node_type=NodeType.LOOP_START,
            name=name,
            config=node_config
        )
        
        self.updated_at = datetime.datetime.now()
        
        return node_id
    
    def add_loop_end_node(
        self,
        loop_start_id: str,
        name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Add a loop end node to the composition.
        
        Args:
            loop_start_id: ID of corresponding loop start node
            name: Node name
            config: Node configuration
            
        Returns:
            Node ID
        """
        if loop_start_id not in self.nodes:
            raise ValueError(f"Loop start node with ID {loop_start_id} not found")
        
        if self.nodes[loop_start_id].type != NodeType.LOOP_START:
            raise ValueError(f"Node with ID {loop_start_id} is not a loop start node")
        
        node_id = str(uuid.uuid4())
        
        if name is None:
            name = f"Loop End: {self.nodes[loop_start_id].name}"
        
        node_config = config or {}
        node_config["loop_start_id"] = loop_start_id
        
        self.nodes[node_id] = CompositionNode(
            node_id=node_id,
            node_type=NodeType.LOOP_END,
            name=name,
            config=node_config
        )
        
        self.updated_at = datetime.datetime.now()
        
        return node_id
    
    def connect_nodes(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.NORMAL,
        data_mapping: Dict[str, str] = None
    ) -> str:
        """
        Connect two nodes with an edge.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of edge
            data_mapping: Mapping from source to target parameters
            
        Returns:
            Edge ID
        """
        if source_id not in self.nodes:
            raise ValueError(f"Source node with ID {source_id} not found")
        
        if target_id not in self.nodes:
            raise ValueError(f"Target node with ID {target_id} not found")
        
        # Validate edge type based on node types
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        
        if source_node.type == NodeType.END:
            raise ValueError("Cannot connect from an end node")
        
        if target_node.type == NodeType.START:
            raise ValueError("Cannot connect to a start node")
        
        if source_node.type == NodeType.CONDITION and edge_type not in [EdgeType.CONDITIONAL_TRUE, EdgeType.CONDITIONAL_FALSE]:
            raise ValueError("Connections from condition nodes must use conditional edge types")
        
        if source_node.type != NodeType.CONDITION and edge_type in [EdgeType.CONDITIONAL_TRUE, EdgeType.CONDITIONAL_FALSE]:
            raise ValueError("Conditional edge types can only be used with condition nodes")
        
        if source_node.type == NodeType.LOOP_START and edge_type != EdgeType.NORMAL:
            raise ValueError("Connections from loop start nodes must use normal edge type")
        
        if source_node.type == NodeType.LOOP_END and edge_type not in [EdgeType.LOOP_ITERATION, EdgeType.LOOP_EXIT]:
            raise ValueError("Connections from loop end nodes must use loop edge types")
        
        if source_node.type != NodeType.LOOP_END and edge_type in [EdgeType.LOOP_ITERATION, EdgeType.LOOP_EXIT]:
            raise ValueError("Loop edge types can only be used with loop end nodes")
        
        # Create edge
        edge_id = str(uuid.uuid4())
        
        self.edges[edge_id] = CompositionEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            data_mapping=data_mapping or {}
        )
        
        self.updated_at = datetime.datetime.now()
        
        return edge_id
    
    def remove_node(self, node_id: str) -> None:
        """
        Remove a node and its connected edges.
        
        Args:
            node_id: Node ID
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID {node_id} not found")
        
        if node_id in [self.start_node_id, self.end_node_id]:
            raise ValueError("Cannot remove start or end nodes")
        
        # Remove connected edges
        edges_to_remove = []
        for edge_id, edge in self.edges.items():
            if edge.source_id == node_id or edge.target_id == node_id:
                edges_to_remove.append(edge_id)
        
        for edge_id in edges_to_remove:
            del self.edges[edge_id]
        
        # Remove node
        del self.nodes[node_id]
        
        self.updated_at = datetime.datetime.now()
    
    def remove_edge(self, edge_id: str) -> None:
        """
        Remove an edge.
        
        Args:
            edge_id: Edge ID
        """
        if edge_id not in self.edges:
            raise ValueError(f"Edge with ID {edge_id} not found")
        
        del self.edges[edge_id]
        
        self.updated_at = datetime.datetime.now()
    
    def validate(self) -> bool:
        """
        Validate the composition structure.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Check for empty composition
        if len(self.nodes) <= 2:  # Only start and end nodes
            raise ValueError("Composition is empty")
        
        # Check for disconnected nodes
        connected_nodes = self._find_connected_nodes()
        disconnected_nodes = set(self.nodes.keys()) - connected_nodes
        
        if disconnected_nodes:
            node_names = [self.nodes[node_id].name for node_id in disconnected_nodes]
            raise ValueError(f"Disconnected nodes found: {', '.join(node_names)}")
        
        # Check for cycles (except in loops)
        if self._has_cycles():
            raise ValueError("Composition contains cycles outside of loops")
        
        # Check for proper loop structure
        loop_starts = [node_id for node_id, node in self.nodes.items() if node.type == NodeType.LOOP_START]
        loop_ends = [node_id for node_id, node in self.nodes.items() if node.type == NodeType.LOOP_END]
        
        if len(loop_starts) != len(loop_ends):
            raise ValueError("Mismatched loop start and end nodes")
        
        for loop_end_id in loop_ends:
            loop_end = self.nodes[loop_end_id]
            loop_start_id = loop_end.config.get("loop_start_id")
            
            if loop_start_id not in self.nodes:
                raise ValueError(f"Loop end node {loop_end.name} references non-existent loop start node")
            
            if self.nodes[loop_start_id].type != NodeType.LOOP_START:
                raise ValueError(f"Loop end node {loop_end.name} references non-loop start node")
        
        # Check for proper condition structure
        for node_id, node in self.nodes.items():
            if node.type == NodeType.CONDITION:
                true_edges = [edge for edge in self.edges.values() if edge.source_id == node_id and edge.type == EdgeType.CONDITIONAL_TRUE]
                false_edges = [edge for edge in self.edges.values() if edge.source_id == node_id and edge.type == EdgeType.CONDITIONAL_FALSE]
                
                if not true_edges:
                    raise ValueError(f"Condition node {node.name} has no true branch")
                
                if not false_edges:
                    raise ValueError(f"Condition node {node.name} has no false branch")
        
        return True
    
    def _find_connected_nodes(self) -> Set[str]:
        """
        Find all nodes connected to the start node.
        
        Returns:
            Set of connected node IDs
        """
        connected = set()
        queue = [self.start_node_id]
        
        while queue:
            node_id = queue.pop(0)
            if node_id in connected:
                continue
            
            connected.add(node_id)
            
            # Find outgoing edges
            for edge in self.edges.values():
                if edge.source_id == node_id and edge.target_id not in connected:
                    queue.append(edge.target_id)
        
        return connected
    
    def _has_cycles(self) -> bool:
        """
        Check if the composition has cycles outside of loops.
        
        Returns:
            True if cycles found, False otherwise
        """
        # Identify loop nodes
        loop_nodes = set()
        for node_id, node in self.nodes.items():
            if node.type in [NodeType.LOOP_START, NodeType.LOOP_END]:
                loop_nodes.add(node_id)
        
        # Create adjacency list excluding loop edges
        adjacency = {}
        for node_id in self.nodes:
            adjacency[node_id] = []
        
        for edge in self.edges.values():
            if edge.type not in [EdgeType.LOOP_ITERATION, EdgeType.LOOP_EXIT]:
                if edge.source_id not in loop_nodes or edge.target_id not in loop_nodes:
                    adjacency[edge.source_id].append(edge.target_id)
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def is_cyclic(node_id):
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in adjacency[node_id]:
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if is_cyclic(node_id):
                    return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert composition to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "start_node_id": self.start_node_id,
            "end_node_id": self.end_node_id,
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            },
            "edges": {
                edge_id: edge.to_dict()
                for edge_id, edge in self.edges.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolComposition':
        """Create composition from dictionary."""
        composition = cls(
            composition_id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            author=data["author"]
        )
        
        composition.created_at = datetime.datetime.fromisoformat(data["created_at"])
        composition.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        
        # Clear default nodes
        composition.nodes = {}
        composition.edges = {}
        
        # Set start and end node IDs
        composition.start_node_id = data["start_node_id"]
        composition.end_node_id = data["end_node_id"]
        
        # Load nodes
        for node_id, node_data in data["nodes"].items():
            composition.nodes[node_id] = CompositionNode.from_dict(node_data)
        
        # Load edges
        for edge_id, edge_data in data["edges"].items():
            composition.edges[edge_id] = CompositionEdge.from_dict(edge_data)
        
        return composition
    
    def to_json(self) -> str:
        """Convert composition to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ToolComposition':
        """Create composition from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def clone(self) -> 'ToolComposition':
        """Create a clone of this composition."""
        return ToolComposition.from_dict(self.to_dict())

class CompositionEngine:
    """
    Engine for executing tool compositions.
    
    Provides functionality for:
    - Executing tool compositions with parameter validation
    - Managing execution state and data flow
    - Handling conditional branching and loops
    - Error handling and recovery
    """
    
    def __init__(self, registry: ToolRegistry, execution_engine: ToolExecutionEngine):
        """
        Initialize composition engine.
        
        Args:
            registry: Tool registry
            execution_engine: Tool execution engine
        """
        self.registry = registry
        self.execution_engine = execution_engine
        self.compositions: Dict[str, ToolComposition] = {}
        self.executions: Dict[str, CompositionExecutionResult] = {}
    
    def register_composition(self, composition: ToolComposition) -> str:
        """
        Register a tool composition.
        
        Args:
            composition: Tool composition
            
        Returns:
            Composition ID
        """
        # Validate composition
        composition.validate()
        
        # Register composition
        self.compositions[composition.id] = composition
        logger.info(f"Registered composition: {composition.name} (ID: {composition.id})")
        
        return composition.id
    
    def get_composition(self, composition_id: str) -> ToolComposition:
        """
        Get a registered composition.
        
        Args:
            composition_id: Composition ID
            
        Returns:
            Tool composition
        """
        if composition_id not in self.compositions:
            raise ValueError(f"Composition with ID {composition_id} not found")
        
        return self.compositions[composition_id]
    
    def list_compositions(self) -> List[ToolComposition]:
        """
        List all registered compositions.
        
        Returns:
            List of tool compositions
        """
        return list(self.compositions.values())
    
    def execute_composition(
        self,
        composition_id: str,
        input_data: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> CompositionExecutionResult:
        """
        Execute a tool composition synchronously.
        
        Args:
            composition_id: Composition ID
            input_data: Input data for the composition
            timeout: Execution timeout in seconds
            
        Returns:
            Composition execution result
        """
        # Get composition
        if composition_id not in self.compositions:
            raise ValueError(f"Composition with ID {composition_id} not found")
        
        composition = self.compositions[composition_id]
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Create initial result
        result = CompositionExecutionResult(
            composition_id=composition_id,
            execution_id=execution_id,
            status=CompositionStatus.RUNNING,
            start_time=datetime.datetime.now()
        )
        
        self.executions[execution_id] = result
        
        try:
            # Execute composition
            output = self._execute_composition_internal(composition, input_data, result, timeout)
            
            # Record end time
            end_time = datetime.datetime.now()
            execution_time = (end_time - result.start_time).total_seconds()
            
            # Update result
            result.status = CompositionStatus.COMPLETED
            result.output = output
            result.end_time = end_time
            result.execution_time = execution_time
            
            logger.info(f"Composition execution completed: {execution_id} (Composition: {composition_id})")
            
        except Exception as e:
            # Handle errors
            result.status = CompositionStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            logger.error(f"Composition execution failed: {execution_id} (Composition: {composition_id})")
            logger.error(str(e))
        
        return result
    
    async def execute_composition_async(
        self,
        composition_id: str,
        input_data: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> str:
        """
        Execute a tool composition asynchronously.
        
        Args:
            composition_id: Composition ID
            input_data: Input data for the composition
            timeout: Execution timeout in seconds
            
        Returns:
            Execution ID
        """
        # Get composition
        if composition_id not in self.compositions:
            raise ValueError(f"Composition with ID {composition_id} not found")
        
        composition = self.compositions[composition_id]
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Create initial result
        result = CompositionExecutionResult(
            composition_id=composition_id,
            execution_id=execution_id,
            status=CompositionStatus.PENDING,
            start_time=datetime.datetime.now()
        )
        
        self.executions[execution_id] = result
        
        # Schedule execution
        import threading
        
        def execute_thread():
            try:
                # Update status
                result.status = CompositionStatus.RUNNING
                
                # Execute composition
                output = self._execute_composition_internal(composition, input_data, result, timeout)
                
                # Record end time
                end_time = datetime.datetime.now()
                execution_time = (end_time - result.start_time).total_seconds()
                
                # Update result
                result.status = CompositionStatus.COMPLETED
                result.output = output
                result.end_time = end_time
                result.execution_time = execution_time
                
                logger.info(f"Async composition execution completed: {execution_id} (Composition: {composition_id})")
                
            except Exception as e:
                # Handle errors
                result.status = CompositionStatus.FAILED
                result.error = str(e)
                result.end_time = datetime.datetime.now()
                result.execution_time = (result.end_time - result.start_time).total_seconds()
                
                logger.error(f"Async composition execution failed: {execution_id} (Composition: {composition_id})")
                logger.error(str(e))
        
        thread = threading.Thread(target=execute_thread)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Scheduled async composition execution: {execution_id} (Composition: {composition_id})")
        
        return execution_id
    
    def get_execution_result(self, execution_id: str) -> CompositionExecutionResult:
        """
        Get the result of a composition execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Composition execution result
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution with ID {execution_id} not found")
        
        return self.executions[execution_id]
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running composition execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            True if cancelled, False if already completed
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution with ID {execution_id} not found")
        
        result = self.executions[execution_id]
        
        if result.status in [CompositionStatus.COMPLETED, CompositionStatus.FAILED]:
            return False
        
        result.status = CompositionStatus.CANCELLED
        result.end_time = datetime.datetime.now()
        result.execution_time = (result.end_time - result.start_time).total_seconds()
        result.error = "Execution cancelled by user"
        
        logger.info(f"Composition execution cancelled: {execution_id} (Composition: {result.composition_id})")
        
        return True
    
    def _execute_composition_internal(
        self,
        composition: ToolComposition,
        input_data: Dict[str, Any],
        result: CompositionExecutionResult,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Internal method to execute a composition.
        
        Args:
            composition: Tool composition
            input_data: Input data
            result: Execution result to update
            timeout: Execution timeout
            
        Returns:
            Composition output
        """
        # Initialize execution state
        state = {
            "data": {
                "input": input_data
            },
            "current_node_id": composition.start_node_id,
            "visited_nodes": set(),
            "loop_states": {},
            "node_results": {}
        }
        
        # Execute until we reach the end node or encounter an error
        while state["current_node_id"] != composition.end_node_id:
            # Get current node
            current_node = composition.nodes[state["current_node_id"]]
            
            # Execute node
            try:
                node_result = self._execute_node(composition, current_node, state, timeout)
                result.node_results[current_node.id] = node_result
                
                # Update state with node result
                state["node_results"][current_node.id] = node_result.output
                
                # Find next node
                next_node_id = self._find_next_node(composition, current_node, state)
                
                if next_node_id is None:
                    raise ValueError(f"No valid path from node {current_node.name}")
                
                state["current_node_id"] = next_node_id
                
            except Exception as e:
                # Create failed node result
                node_result = NodeExecutionResult(
                    node_id=current_node.id,
                    status=NodeExecutionStatus.FAILED,
                    error=str(e),
                    start_time=datetime.datetime.now(),
                    end_time=datetime.datetime.now(),
                    execution_time=0
                )
                
                result.node_results[current_node.id] = node_result
                
                # Propagate error
                raise ValueError(f"Error executing node {current_node.name}: {str(e)}")
        
        # Return final output
        end_node_id = composition.end_node_id
        incoming_edges = [edge for edge in composition.edges.values() if edge.target_id == end_node_id]
        
        if not incoming_edges:
            return None
        
        # Get output from the last node before end
        last_node_id = incoming_edges[0].source_id
        return state["node_results"].get(last_node_id)
    
    def _execute_node(
        self,
        composition: ToolComposition,
        node: CompositionNode,
        state: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> NodeExecutionResult:
        """
        Execute a single node in the composition.
        
        Args:
            composition: Tool composition
            node: Node to execute
            state: Execution state
            timeout: Execution timeout
            
        Returns:
            Node execution result
        """
        # Record start time
        start_time = datetime.datetime.now()
        
        # Initialize result
        result = NodeExecutionResult(
            node_id=node.id,
            status=NodeExecutionStatus.RUNNING,
            start_time=start_time
        )
        
        try:
            # Execute based on node type
            if node.type == NodeType.START:
                # Start node just passes input data
                output = state["data"]["input"]
                
            elif node.type == NodeType.END:
                # End node has no output
                output = None
                
            elif node.type == NodeType.TOOL:
                # Execute tool
                tool_id = node.config["tool_id"]
                
                # Get input parameters
                parameters = self._get_node_input_parameters(composition, node, state)
                
                # Execute tool
                tool_result = self.execution_engine.execute_tool(tool_id, parameters, timeout)
                
                if tool_result.status != ToolExecutionStatus.COMPLETED:
                    raise ValueError(f"Tool execution failed: {tool_result.error}")
                
                output = tool_result.output
                
            elif node.type == NodeType.CONDITION:
                # Evaluate condition
                condition_expression = node.config["condition_expression"]
                
                # Get input parameters
                parameters = self._get_node_input_parameters(composition, node, state)
                
                # Evaluate condition
                output = self._evaluate_expression(condition_expression, parameters)
                
            elif node.type == NodeType.TRANSFORM:
                # Apply transformation
                transform_expression = node.config["transform_expression"]
                
                # Get input parameters
                parameters = self._get_node_input_parameters(composition, node, state)
                
                # Apply transformation
                output = self._evaluate_expression(transform_expression, parameters)
                
            elif node.type == NodeType.MERGE:
                # Merge inputs from multiple sources
                incoming_edges = [edge for edge in composition.edges.values() if edge.target_id == node.id]
                
                merged_data = {}
                for edge in incoming_edges:
                    source_id = edge.source_id
                    if source_id in state["node_results"]:
                        source_data = state["node_results"][source_id]
                        if isinstance(source_data, dict):
                            merged_data.update(source_data)
                
                output = merged_data
                
            elif node.type == NodeType.LOOP_START:
                # Initialize loop
                loop_variable = node.config["loop_variable"]
                iterable_expression = node.config["iterable_expression"]
                
                # Get input parameters
                parameters = self._get_node_input_parameters(composition, node, state)
                
                # Evaluate iterable
                iterable = self._evaluate_expression(iterable_expression, parameters)
                
                if not hasattr(iterable, "__iter__"):
                    raise ValueError(f"Expression '{iterable_expression}' did not evaluate to an iterable")
                
                # Initialize loop state
                state["loop_states"][node.id] = {
                    "iterable": iterable,
                    "index": 0,
                    "results": []
                }
                
                # Set first item as output if available
                if len(iterable) > 0:
                    output = {loop_variable: iterable[0]}
                else:
                    output = {loop_variable: None}
                
            elif node.type == NodeType.LOOP_END:
                # Process loop iteration
                loop_start_id = node.config["loop_start_id"]
                
                if loop_start_id not in state["loop_states"]:
                    raise ValueError(f"Loop state not found for loop start node {loop_start_id}")
                
                loop_state = state["loop_states"][loop_start_id]
                loop_variable = composition.nodes[loop_start_id].config["loop_variable"]
                
                # Get input parameters
                parameters = self._get_node_input_parameters(composition, node, state)
                
                # Store iteration result
                loop_state["results"].append(parameters)
                
                # Increment index
                loop_state["index"] += 1
                
                # Check if loop should continue
                if loop_state["index"] < len(loop_state["iterable"]):
                    # Continue loop
                    output = {
                        loop_variable: loop_state["iterable"][loop_state["index"]],
                        "loop_index": loop_state["index"],
                        "loop_continue": True
                    }
                else:
                    # End loop
                    output = {
                        "loop_results": loop_state["results"],
                        "loop_continue": False
                    }
            
            else:
                raise ValueError(f"Unsupported node type: {node.type}")
            
            # Record end time
            end_time = datetime.datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update result
            result.status = NodeExecutionStatus.COMPLETED
            result.output = output
            result.end_time = end_time
            result.execution_time = execution_time
            
            # Mark node as visited
            state["visited_nodes"].add(node.id)
            
            return result
            
        except Exception as e:
            # Handle errors
            end_time = datetime.datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            result.status = NodeExecutionStatus.FAILED
            result.error = str(e)
            result.end_time = end_time
            result.execution_time = execution_time
            
            raise
    
    def _get_node_input_parameters(
        self,
        composition: ToolComposition,
        node: CompositionNode,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get input parameters for a node based on incoming edges.
        
        Args:
            composition: Tool composition
            node: Target node
            state: Execution state
            
        Returns:
            Input parameters
        """
        # Start with input data
        parameters = copy.deepcopy(state["data"]["input"])
        
        # Get incoming edges
        incoming_edges = [edge for edge in composition.edges.values() if edge.target_id == node.id]
        
        # Apply data mappings from incoming edges
        for edge in incoming_edges:
            source_id = edge.source_id
            
            if source_id in state["node_results"]:
                source_data = state["node_results"][source_id]
                
                # Apply data mapping
                if edge.data_mapping:
                    for target_param, source_param in edge.data_mapping.items():
                        if isinstance(source_data, dict) and source_param in source_data:
                            parameters[target_param] = source_data[source_param]
                        elif source_param == "*":
                            # Special case: map all source data
                            if isinstance(source_data, dict):
                                parameters.update(source_data)
                else:
                    # No mapping, use source data directly
                    if isinstance(source_data, dict):
                        parameters.update(source_data)
                    else:
                        parameters["value"] = source_data
        
        return parameters
    
    def _find_next_node(
        self,
        composition: ToolComposition,
        current_node: CompositionNode,
        state: Dict[str, Any]
    ) -> Optional[str]:
        """
        Find the next node to execute.
        
        Args:
            composition: Tool composition
            current_node: Current node
            state: Execution state
            
        Returns:
            Next node ID or None if no valid path
        """
        # Get outgoing edges
        outgoing_edges = [edge for edge in composition.edges.values() if edge.source_id == current_node.id]
        
        if not outgoing_edges:
            return None
        
        # Handle based on node type
        if current_node.type == NodeType.CONDITION:
            # Get condition result
            condition_result = state["node_results"][current_node.id]
            
            # Find appropriate edge
            for edge in outgoing_edges:
                if condition_result and edge.type == EdgeType.CONDITIONAL_TRUE:
                    return edge.target_id
                elif not condition_result and edge.type == EdgeType.CONDITIONAL_FALSE:
                    return edge.target_id
            
            return None
            
        elif current_node.type == NodeType.LOOP_END:
            # Get loop result
            loop_result = state["node_results"][current_node.id]
            loop_continue = loop_result.get("loop_continue", False)
            
            # Find appropriate edge
            for edge in outgoing_edges:
                if loop_continue and edge.type == EdgeType.LOOP_ITERATION:
                    # Continue loop
                    loop_start_id = current_node.config["loop_start_id"]
                    return loop_start_id
                elif not loop_continue and edge.type == EdgeType.LOOP_EXIT:
                    # Exit loop
                    return edge.target_id
            
            return None
            
        else:
            # For other node types, just take the first edge
            return outgoing_edges[0].target_id
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """
        Evaluate an expression in the given context.
        
        Args:
            expression: Expression to evaluate
            context: Evaluation context
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would use a secure expression evaluator
        # For now, we'll use a simple eval with limited context
        
        # Create safe globals
        safe_globals = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "range": range,
            "round": round,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "zip": zip
        }
        
        # Evaluate expression
        try:
            return eval(expression, safe_globals, context)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expression}': {str(e)}")

class CompositionTemplate:
    """
    Template for creating tool compositions with predefined patterns.
    
    Provides functionality for:
    - Creating compositions from templates
    - Customizing template parameters
    - Generating common composition patterns
    """
    
    @staticmethod
    def create_sequential(
        name: str,
        description: str,
        tool_ids: List[str],
        registry: ToolRegistry
    ) -> ToolComposition:
        """
        Create a sequential composition of tools.
        
        Args:
            name: Composition name
            description: Composition description
            tool_ids: List of tool IDs to execute in sequence
            registry: Tool registry
            
        Returns:
            Tool composition
        """
        composition_id = str(uuid.uuid4())
        composition = ToolComposition(
            composition_id=composition_id,
            name=name,
            description=description
        )
        
        # Add tool nodes
        node_ids = []
        for tool_id in tool_ids:
            tool = registry.get_tool(tool_id)
            node_id = composition.add_tool_node(tool_id, f"Tool: {tool.name}")
            node_ids.append(node_id)
        
        # Connect start node to first tool
        if node_ids:
            composition.connect_nodes(composition.start_node_id, node_ids[0])
        
        # Connect tools in sequence
        for i in range(len(node_ids) - 1):
            composition.connect_nodes(node_ids[i], node_ids[i + 1])
        
        # Connect last tool to end node
        if node_ids:
            composition.connect_nodes(node_ids[-1], composition.end_node_id)
        
        return composition
    
    @staticmethod
    def create_conditional(
        name: str,
        description: str,
        condition_tool_id: str,
        true_tool_id: str,
        false_tool_id: str,
        registry: ToolRegistry,
        condition_expression: str = "value == True"
    ) -> ToolComposition:
        """
        Create a conditional composition with true/false branches.
        
        Args:
            name: Composition name
            description: Composition description
            condition_tool_id: Tool ID for condition evaluation
            true_tool_id: Tool ID for true branch
            false_tool_id: Tool ID for false branch
            registry: Tool registry
            condition_expression: Expression to evaluate condition result
            
        Returns:
            Tool composition
        """
        composition_id = str(uuid.uuid4())
        composition = ToolComposition(
            composition_id=composition_id,
            name=name,
            description=description
        )
        
        # Add tool nodes
        condition_tool = registry.get_tool(condition_tool_id)
        true_tool = registry.get_tool(true_tool_id)
        false_tool = registry.get_tool(false_tool_id)
        
        condition_node_id = composition.add_tool_node(condition_tool_id, f"Tool: {condition_tool.name}")
        
        # Add condition node
        condition_id = composition.add_condition_node(condition_expression, "Condition")
        
        # Add branch nodes
        true_node_id = composition.add_tool_node(true_tool_id, f"True Branch: {true_tool.name}")
        false_node_id = composition.add_tool_node(false_tool_id, f"False Branch: {false_tool.name}")
        
        # Add merge node
        merge_id = composition.add_merge_node("Merge Results")
        
        # Connect nodes
        composition.connect_nodes(composition.start_node_id, condition_node_id)
        composition.connect_nodes(condition_node_id, condition_id)
        composition.connect_nodes(condition_id, true_node_id, EdgeType.CONDITIONAL_TRUE)
        composition.connect_nodes(condition_id, false_node_id, EdgeType.CONDITIONAL_FALSE)
        composition.connect_nodes(true_node_id, merge_id)
        composition.connect_nodes(false_node_id, merge_id)
        composition.connect_nodes(merge_id, composition.end_node_id)
        
        return composition
    
    @staticmethod
    def create_loop(
        name: str,
        description: str,
        iterable_tool_id: str,
        loop_tool_id: str,
        registry: ToolRegistry,
        loop_variable: str = "item",
        iterable_expression: str = "value"
    ) -> ToolComposition:
        """
        Create a loop composition that processes items in an iterable.
        
        Args:
            name: Composition name
            description: Composition description
            iterable_tool_id: Tool ID that produces the iterable
            loop_tool_id: Tool ID to execute for each item
            registry: Tool registry
            loop_variable: Variable name for loop iteration
            iterable_expression: Expression to extract iterable
            
        Returns:
            Tool composition
        """
        composition_id = str(uuid.uuid4())
        composition = ToolComposition(
            composition_id=composition_id,
            name=name,
            description=description
        )
        
        # Add tool nodes
        iterable_tool = registry.get_tool(iterable_tool_id)
        loop_tool = registry.get_tool(loop_tool_id)
        
        iterable_node_id = composition.add_tool_node(iterable_tool_id, f"Tool: {iterable_tool.name}")
        
        # Add loop nodes
        loop_start_id = composition.add_loop_start_node(loop_variable, iterable_expression, "Loop Start")
        loop_body_id = composition.add_tool_node(loop_tool_id, f"Loop Body: {loop_tool.name}")
        loop_end_id = composition.add_loop_end_node(loop_start_id, "Loop End")
        
        # Connect nodes
        composition.connect_nodes(composition.start_node_id, iterable_node_id)
        composition.connect_nodes(iterable_node_id, loop_start_id)
        composition.connect_nodes(loop_start_id, loop_body_id)
        composition.connect_nodes(loop_body_id, loop_end_id)
        composition.connect_nodes(loop_end_id, composition.end_node_id, EdgeType.LOOP_EXIT)
        composition.connect_nodes(loop_end_id, loop_start_id, EdgeType.LOOP_ITERATION)
        
        return composition
