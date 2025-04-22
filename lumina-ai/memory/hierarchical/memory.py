"""
Hierarchical Memory System for Lumina AI.

This module provides hierarchical memory structures for organizing
and retrieving information at different levels of abstraction.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
import logging
import time
import json
import os

class MemoryNode:
    """A node in the hierarchical memory structure."""
    
    def __init__(self, 
                 id: str,
                 content: str,
                 node_type: str,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a memory node.
        
        Args:
            id: Unique identifier for the node
            content: The content stored in the node
            node_type: Type of node (concept, fact, task, etc.)
            metadata: Additional metadata for the node
        """
        self.id = id
        self.content = content
        self.node_type = node_type
        self.metadata = metadata or {}
        self.parent_ids: Set[str] = set()
        self.child_ids: Set[str] = set()
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "node_type": self.node_type,
            "metadata": self.metadata,
            "parent_ids": list(self.parent_ids),
            "child_ids": list(self.child_ids),
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryNode':
        """Create node from dictionary."""
        node = cls(
            id=data["id"],
            content=data["content"],
            node_type=data["node_type"],
            metadata=data["metadata"]
        )
        node.parent_ids = set(data["parent_ids"])
        node.child_ids = set(data["child_ids"])
        node.created_at = data["created_at"]
        node.last_accessed = data["last_accessed"]
        node.access_count = data["access_count"]
        return node


class HierarchicalMemory:
    """Hierarchical memory system for organizing information at different levels."""
    
    def __init__(self, persist_dir: str = "./data/hierarchical_memory"):
        """
        Initialize the hierarchical memory system.
        
        Args:
            persist_dir: Directory to persist memory data
        """
        self.persist_dir = persist_dir
        self.nodes: Dict[str, MemoryNode] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create persistence directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Load existing data if available
        self._load()
    
    def add_node(self, 
                 content: str, 
                 node_type: str,
                 parent_ids: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new node to the memory.
        
        Args:
            content: The content to store
            node_type: Type of node
            parent_ids: Optional list of parent node IDs
            metadata: Optional metadata
            
        Returns:
            ID of the created node
        """
        # Generate a unique ID
        node_id = f"{node_type}_{int(time.time() * 1000)}_{len(self.nodes)}"
        
        # Create the node
        node = MemoryNode(
            id=node_id,
            content=content,
            node_type=node_type,
            metadata=metadata
        )
        
        # Add to parents if specified
        if parent_ids:
            for parent_id in parent_ids:
                if parent_id in self.nodes:
                    node.parent_ids.add(parent_id)
                    self.nodes[parent_id].child_ids.add(node_id)
                else:
                    self.logger.warning(f"Parent node {parent_id} not found")
        
        # Add to memory
        self.nodes[node_id] = node
        
        # Persist changes
        self._save()
        
        return node_id
    
    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        """
        Get a node by ID.
        
        Args:
            node_id: ID of the node to retrieve
            
        Returns:
            The node if found, None otherwise
        """
        node = self.nodes.get(node_id)
        if node:
            node.last_accessed = time.time()
            node.access_count += 1
            return node
        return None
    
    def get_children(self, node_id: str) -> List[MemoryNode]:
        """
        Get all children of a node.
        
        Args:
            node_id: ID of the parent node
            
        Returns:
            List of child nodes
        """
        node = self.nodes.get(node_id)
        if not node:
            return []
        
        return [self.nodes[child_id] for child_id in node.child_ids if child_id in self.nodes]
    
    def get_parents(self, node_id: str) -> List[MemoryNode]:
        """
        Get all parents of a node.
        
        Args:
            node_id: ID of the child node
            
        Returns:
            List of parent nodes
        """
        node = self.nodes.get(node_id)
        if not node:
            return []
        
        return [self.nodes[parent_id] for parent_id in node.parent_ids if parent_id in self.nodes]
    
    def get_ancestors(self, node_id: str, max_depth: int = 10) -> List[MemoryNode]:
        """
        Get all ancestors of a node up to a maximum depth.
        
        Args:
            node_id: ID of the node
            max_depth: Maximum depth to traverse
            
        Returns:
            List of ancestor nodes
        """
        ancestors = []
        visited = set()
        
        def traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            node = self.nodes.get(current_id)
            if not node:
                return
            
            for parent_id in node.parent_ids:
                parent = self.nodes.get(parent_id)
                if parent and parent_id not in visited:
                    ancestors.append(parent)
                    traverse(parent_id, depth + 1)
        
        traverse(node_id, 0)
        return ancestors
    
    def get_descendants(self, node_id: str, max_depth: int = 10) -> List[MemoryNode]:
        """
        Get all descendants of a node up to a maximum depth.
        
        Args:
            node_id: ID of the node
            max_depth: Maximum depth to traverse
            
        Returns:
            List of descendant nodes
        """
        descendants = []
        visited = set()
        
        def traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            node = self.nodes.get(current_id)
            if not node:
                return
            
            for child_id in node.child_ids:
                child = self.nodes.get(child_id)
                if child and child_id not in visited:
                    descendants.append(child)
                    traverse(child_id, depth + 1)
        
        traverse(node_id, 0)
        return descendants
    
    def search_by_type(self, node_type: str) -> List[MemoryNode]:
        """
        Search for nodes by type.
        
        Args:
            node_type: Type of nodes to search for
            
        Returns:
            List of matching nodes
        """
        return [node for node in self.nodes.values() if node.node_type == node_type]
    
    def search_by_content(self, query: str, limit: int = 10) -> List[Tuple[MemoryNode, float]]:
        """
        Search for nodes by content similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of (node, score) tuples
        """
        # Simple keyword matching for now
        # In a real implementation, this would use embeddings and vector similarity
        
        results = []
        query_lower = query.lower()
        
        for node in self.nodes.values():
            content_lower = node.content.lower()
            
            # Simple relevance score based on substring matching
            if query_lower in content_lower:
                # Calculate a basic relevance score
                score = content_lower.count(query_lower) / len(content_lower)
                results.append((node, score))
        
        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def delete_node(self, node_id: str, recursive: bool = False) -> bool:
        """
        Delete a node from memory.
        
        Args:
            node_id: ID of the node to delete
            recursive: Whether to recursively delete descendants
            
        Returns:
            True if deleted, False otherwise
        """
        node = self.nodes.get(node_id)
        if not node:
            return False
        
        if recursive:
            # Get all descendants
            descendants = self.get_descendants(node_id)
            
            # Delete descendants
            for desc in descendants:
                self._remove_node_references(desc.id)
                del self.nodes[desc.id]
        
        # Update parent and child references
        self._remove_node_references(node_id)
        
        # Delete the node
        del self.nodes[node_id]
        
        # Persist changes
        self._save()
        
        return True
    
    def _remove_node_references(self, node_id: str) -> None:
        """Remove all references to a node from other nodes."""
        node = self.nodes.get(node_id)
        if not node:
            return
        
        # Remove from parent nodes
        for parent_id in node.parent_ids:
            if parent_id in self.nodes:
                self.nodes[parent_id].child_ids.discard(node_id)
        
        # Remove from child nodes
        for child_id in node.child_ids:
            if child_id in self.nodes:
                self.nodes[child_id].parent_ids.discard(node_id)
    
    def _save(self) -> None:
        """Save the memory to disk."""
        data = {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        with open(os.path.join(self.persist_dir, "hierarchical_memory.json"), "w") as f:
            json.dump(data, f)
    
    def _load(self) -> None:
        """Load the memory from disk."""
        try:
            file_path = os.path.join(self.persist_dir, "hierarchical_memory.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                for node_id, node_data in data.items():
                    self.nodes[node_id] = MemoryNode.from_dict(node_data)
                
                self.logger.info(f"Loaded {len(self.nodes)} nodes from disk")
        except Exception as e:
            self.logger.error(f"Error loading hierarchical memory: {e}")
