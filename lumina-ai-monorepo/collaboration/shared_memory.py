"""
Shared Memory System for Advanced Multi-Agent Collaboration.

This module implements the Shared Memory System, which provides a shared knowledge base
that all agents can access and update.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, Union
import uuid
import time
import json
import logging
import copy
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class MemoryScope(Enum):
    """Enum representing different memory scopes."""
    GLOBAL = "global"         # Accessible to all agents
    TEAM = "team"             # Accessible to team members only
    AGENT = "agent"           # Accessible to specific agent only
    TASK = "task"             # Accessible in the context of a specific task
    SESSION = "session"       # Accessible for the duration of a session


class MemoryType(Enum):
    """Enum representing different memory types."""
    FACTUAL = "factual"               # Verified facts
    PROCEDURAL = "procedural"         # How to do things
    EPISODIC = "episodic"             # Past experiences
    SEMANTIC = "semantic"             # Conceptual understanding
    WORKING = "working"               # Temporary information
    DECLARATIVE = "declarative"       # Explicit knowledge
    IMPLICIT = "implicit"             # Implied knowledge


@dataclass
class MemoryItem:
    """Represents a single memory item."""
    item_id: str
    key: str
    value: Any
    memory_type: MemoryType
    scope: MemoryScope
    scope_id: Optional[str] = None  # ID of team, agent, task, or session
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    created_by: Optional[str] = None  # Agent ID
    version: int = 1
    ttl: Optional[float] = None  # Time to live in seconds, None for permanent
    importance: float = 0.5  # 0.0 to 1.0
    confidence: float = 1.0  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, value: Any, updated_by: Optional[str] = None) -> None:
        """Update the memory item value."""
        self.value = value
        self.updated_at = time.time()
        if updated_by:
            self.metadata["last_updated_by"] = updated_by
        self.version += 1
    
    def is_expired(self) -> bool:
        """Check if the memory item has expired."""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)


@dataclass
class MemoryChange:
    """Represents a change to the memory."""
    change_id: str
    item_id: str
    key: str
    old_value: Any
    new_value: Any
    change_type: str  # "create", "update", "delete"
    timestamp: float
    agent_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemorySynchronizer:
    """Handles memory synchronization between agents."""
    
    def __init__(self):
        self.change_log: List[MemoryChange] = []
        self.lock = threading.RLock()
        
    def record_change(
        self,
        item_id: str,
        key: str,
        old_value: Any,
        new_value: Any,
        change_type: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a change to memory."""
        with self.lock:
            change = MemoryChange(
                change_id=f"change-{uuid.uuid4()}",
                item_id=item_id,
                key=key,
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                timestamp=time.time(),
                agent_id=agent_id,
                metadata=metadata or {}
            )
            self.change_log.append(change)
    
    def get_changes_since(self, timestamp: float) -> List[MemoryChange]:
        """Get all changes since a specific timestamp."""
        with self.lock:
            return [
                change for change in self.change_log
                if change.timestamp > timestamp
            ]


class MemoryAccessController:
    """Controls access to memory items based on permissions."""
    
    def __init__(self):
        self.agent_teams: Dict[str, Set[str]] = {}  # agent_id -> set of team_ids
        self.agent_tasks: Dict[str, Set[str]] = {}  # agent_id -> set of task_ids
        self.agent_sessions: Dict[str, Set[str]] = {}  # agent_id -> set of session_ids
        self.lock = threading.RLock()
        
    def register_agent_team(self, agent_id: str, team_id: str) -> None:
        """Register an agent as part of a team."""
        with self.lock:
            if agent_id not in self.agent_teams:
                self.agent_teams[agent_id] = set()
            self.agent_teams[agent_id].add(team_id)
        
    def unregister_agent_team(self, agent_id: str, team_id: str) -> None:
        """Unregister an agent from a team."""
        with self.lock:
            if agent_id in self.agent_teams:
                self.agent_teams[agent_id].discard(team_id)
    
    def register_agent_task(self, agent_id: str, task_id: str) -> None:
        """Register an agent as working on a task."""
        with self.lock:
            if agent_id not in self.agent_tasks:
                self.agent_tasks[agent_id] = set()
            self.agent_tasks[agent_id].add(task_id)
        
    def unregister_agent_task(self, agent_id: str, task_id: str) -> None:
        """Unregister an agent from a task."""
        with self.lock:
            if agent_id in self.agent_tasks:
                self.agent_tasks[agent_id].discard(task_id)
    
    def register_agent_session(self, agent_id: str, session_id: str) -> None:
        """Register an agent as part of a session."""
        with self.lock:
            if agent_id not in self.agent_sessions:
                self.agent_sessions[agent_id] = set()
            self.agent_sessions[agent_id].add(session_id)
        
    def unregister_agent_session(self, agent_id: str, session_id: str) -> None:
        """Unregister an agent from a session."""
        with self.lock:
            if agent_id in self.agent_sessions:
                self.agent_sessions[agent_id].discard(session_id)
            
    def can_access(
        self, 
        agent_id: str, 
        item: MemoryItem
    ) -> bool:
        """
        Check if an agent can access a memory item.
        
        Args:
            agent_id: The ID of the agent
            item: The memory item
            
        Returns:
            True if the agent can access the item, False otherwise
        """
        with self.lock:
            # Global scope is accessible to all
            if item.scope == MemoryScope.GLOBAL:
                return True
                
            # Agent scope is only accessible to the specific agent
            if item.scope == MemoryScope.AGENT:
                return item.scope_id == agent_id
                
            # Team scope is accessible to team members
            if item.scope == MemoryScope.TEAM:
                agent_teams = self.agent_teams.get(agent_id, set())
                return item.scope_id in agent_teams
                
            # Task scope is accessible to agents working on the task
            if item.scope == MemoryScope.TASK:
                agent_tasks = self.agent_tasks.get(agent_id, set())
                return item.scope_id in agent_tasks
                
            # Session scope is accessible to agents in the session
            if item.scope == MemoryScope.SESSION:
                agent_sessions = self.agent_sessions.get(agent_id, set())
                return item.scope_id in agent_sessions
                
            return False


class MemoryManager:
    """Main interface for memory operations."""
    
    def __init__(
        self,
        synchronizer: MemorySynchronizer = None,
        access_controller: MemoryAccessController = None
    ):
        self.items: Dict[str, MemoryItem] = {}
        self.synchronizer = synchronizer or MemorySynchronizer()
        self.access_controller = access_controller or MemoryAccessController()
        self.lock = threading.RLock()
        
    def create_item(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType,
        scope: MemoryScope,
        scope_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        ttl: Optional[float] = None,
        importance: float = 0.5,
        confidence: float = 1.0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new memory item.
        
        Args:
            key: The key for the memory item
            value: The value of the memory item
            memory_type: The type of memory
            scope: The scope of the memory
            scope_id: The ID of the scope (team, agent, task, or session)
            agent_id: The ID of the agent creating the item
            ttl: Optional time to live in seconds
            importance: Importance score (0.0 to 1.0)
            confidence: Confidence score (0.0 to 1.0)
            tags: Optional list of tags
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created item
        """
        with self.lock:
            item_id = f"mem-{uuid.uuid4()}"
            
            item = MemoryItem(
                item_id=item_id,
                key=key,
                value=value,
                memory_type=memory_type,
                scope=scope,
                scope_id=scope_id,
                created_by=agent_id,
                ttl=ttl,
                importance=importance,
                confidence=confidence,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self.items[item_id] = item
            
            # Log the creation
            self.synchronizer.record_change(
                item_id=item_id,
                key=key,
                old_value=None,
                new_value=value,
                change_type="create",
                agent_id=agent_id,
                metadata={"memory_type": memory_type.value, "scope": scope.value}
            )
            
            logger.info(f"Created memory item {item_id} with key {key}")
            return item_id
    
    def get_item(self, item_id: str) -> Optional[MemoryItem]:
        """Get a memory item by ID."""
        with self.lock:
            item = self.items.get(item_id)
            
            # Check if item has expired
            if item and item.is_expired():
                logger.info(f"Memory item {item_id} has expired")
                del self.items[item_id]
                return None
                
            return item
    
    def get_item_by_key(
        self, 
        key: str, 
        scope: MemoryScope, 
        scope_id: Optional[str] = None
    ) -> Optional[MemoryItem]:
        """Get a memory item by key and scope."""
        with self.lock:
            for item in list(self.items.values()):
                # Check if item has expired
                if item.is_expired():
                    logger.info(f"Memory item {item.item_id} has expired")
                    del self.items[item.item_id]
                    continue
                    
                if (item.key == key and 
                    item.scope == scope and 
                    item.scope_id == scope_id):
                    return item
            return None
    
    def update_item(
        self, 
        item_id: str, 
        value: Any, 
        agent_id: Optional[str] = None,
        update_importance: Optional[float] = None,
        update_confidence: Optional[float] = None,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update a memory item.
        
        Args:
            item_id: The ID of the item to update
            value: The new value
            agent_id: The ID of the agent making the update
            update_importance: Optional new importance score
            update_confidence: Optional new confidence score
            add_tags: Optional tags to add
            remove_tags: Optional tags to remove
            
        Returns:
            True if the update was successful, False otherwise
        """
        with self.lock:
            if item_id not in self.items:
                logger.warning(f"Attempted to update non-existent memory item {item_id}")
                return False
                
            item = self.items[item_id]
            
            # Check if item has expired
            if item.is_expired():
                logger.info(f"Memory item {item_id} has expired")
                del self.items[item_id]
                return False
                
            old_value = copy.deepcopy(item.value)
            
            # Update value
            item.update(value, agent_id)
            
            # Update importance if provided
            if update_importance is not None:
                item.importance = max(0.0, min(1.0, update_importance))
                
            # Update confidence if provided
            if update_confidence is not None:
                item.confidence = max(0.0, min(1.0, update_confidence))
                
            # Add tags if provided
            if add_tags:
                for tag in add_tags:
                    if tag not in item.tags:
                        item.tags.append(tag)
                        
            # Remove tags if provided
            if remove_tags:
                item.tags = [tag for tag in item.tags if tag not in remove_tags]
            
            # Log the change
            self.synchronizer.record_change(
                item_id=item_id,
                key=item.key,
                old_value=old_value,
                new_value=value,
                change_type="update",
                agent_id=agent_id
            )
            
            logger.info(f"Updated memory item {item_id}")
            return True
    
    def delete_item(self, item_id: str, agent_id: Optional[str] = None) -> bool:
        """
        Delete a memory item.
        
        Args:
            item_id: The ID of the item to delete
            agent_id: The ID of the agent making the deletion
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        with self.lock:
            if item_id not in self.items:
                logger.warning(f"Attempted to delete non-existent memory item {item_id}")
                return False
                
            item = self.items[item_id]
            old_value = copy.deepcopy(item.value)
            
            # Log the deletion
            self.synchronizer.record_change(
                item_id=item_id,
                key=item.key,
                old_value=old_value,
                new_value=None,
                change_type="delete",
                agent_id=agent_id
            )
            
            # Delete the item
            del self.items[item_id]
            logger.info(f"Deleted memory item {item_id}")
            
            return True
    
    def query_items(
        self,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None,
        key_prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: Optional[float] = None,
        min_confidence: Optional[float] = None,
        created_by: Optional[str] = None,
        created_after: Optional[float] = None,
        updated_after: Optional[float] = None
    ) -> List[MemoryItem]:
        """
        Query memory items based on various criteria.
        
        Args:
            memory_type: Filter by memory type
            scope: Filter by scope
            scope_id: Filter by scope ID
            key_prefix: Filter by key prefix
            tags: Filter by tags (items must have all specified tags)
            min_importance: Filter by minimum importance
            min_confidence: Filter by minimum confidence
            created_by: Filter by creator agent ID
            created_after: Filter by creation time
            updated_after: Filter by update time
            
        Returns:
            List of matching memory items
        """
        with self.lock:
            results = []
            
            for item_id, item in list(self.items.items()):
                # Check if item has expired
                if item.is_expired():
                    logger.info(f"Memory item {item_id} has expired")
                    del self.items[item_id]
                    continue
                    
                # Apply filters
                if memory_type and item.memory_type != memory_type:
                    continue
                    
                if scope and item.scope != scope:
                    continue
                    
                if scope_id and item.scope_id != scope_id:
                    continue
                    
                if key_prefix and not item.key.startswith(key_prefix):
                    continue
                    
                if tags and not all(tag in item.tags for tag in tags):
                    continue
                    
                if min_importance is not None and item.importance < min_importance:
                    continue
                    
                if min_confidence is not None and item.confidence < min_confidence:
                    continue
                    
                if created_by and item.created_by != created_by:
                    continue
                    
                if created_after and item.created_at <= created_after:
                    continue
                    
                if updated_after and item.updated_at <= updated_after:
                    continue
                    
                results.append(item)
                
            return results
    
    def search_by_value(
        self,
        search_term: str,
        case_sensitive: bool = False,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None
    ) -> List[MemoryItem]:
        """
        Search memory items by value content.
        
        Args:
            search_term: The term to search for
            case_sensitive: Whether the search is case sensitive
            memory_type: Optional filter by memory type
            scope: Optional filter by scope
            scope_id: Optional filter by scope ID
            
        Returns:
            List of matching memory items
        """
        with self.lock:
            results = []
            
            for item_id, item in list(self.items.items()):
                # Check if item has expired
                if item.is_expired():
                    logger.info(f"Memory item {item_id} has expired")
                    del self.items[item_id]
                    continue
                    
                # Apply type and scope filters
                if memory_type and item.memory_type != memory_type:
                    continue
                    
                if scope and item.scope != scope:
                    continue
                    
                if scope_id and item.scope_id != scope_id:
                    continue
                
                # Convert value to string for searching
                value_str = str(item.value)
                
                # Perform search
                if not case_sensitive:
                    if search_term.lower() in value_str.lower():
                        results.append(item)
                else:
                    if search_term in value_str:
                        results.append(item)
                
            return results
    
    def get_memory_snapshot(
        self,
        scope: MemoryScope,
        scope_id: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        min_importance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get a snapshot of the memory for a specific scope.
        
        Args:
            scope: The scope to get the snapshot for
            scope_id: The ID of the scope
            memory_types: Optional list of memory types to include
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        with self.lock:
            snapshot = {}
            
            items = self.query_items(
                scope=scope, 
                scope_id=scope_id,
                min_importance=min_importance
            )
            
            for item in items:
                if memory_types and item.memory_type not in memory_types:
                    continue
                    
                snapshot[item.key] = item.value
                
            return snapshot
    
    def get_changes_since(self, timestamp: float) -> List[MemoryChange]:
        """Get all changes since a specific timestamp."""
        return self.synchronizer.get_changes_since(timestamp)
    
    def cleanup_expired_items(self) -> int:
        """
        Remove all expired items from memory.
        
        Returns:
            Number of items removed
        """
        with self.lock:
            count = 0
            for item_id, item in list(self.items.items()):
                if item.is_expired():
                    del self.items[item_id]
                    count += 1
                    
            if count > 0:
                logger.info(f"Cleaned up {count} expired memory items")
                
            return count


class SharedMemoryService:
    """Service for managing shared memory."""
    
    def __init__(
        self,
        memory_manager: MemoryManager = None,
        access_controller: MemoryAccessController = None
    ):
        self.memory_manager = memory_manager or MemoryManager()
        self.access_controller = access_controller or self.memory_manager.access_controller
        
    def create_memory(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType,
        scope: MemoryScope,
        scope_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        ttl: Optional[float] = None,
        importance: float = 0.5,
        confidence: float = 1.0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new memory item.
        
        Args:
            key: The key for the memory item
            value: The value of the memory item
            memory_type: The type of memory
            scope: The scope of the memory
            scope_id: The ID of the scope (team, agent, task, or session)
            agent_id: The ID of the agent creating the item
            ttl: Optional time to live in seconds
            importance: Importance score (0.0 to 1.0)
            confidence: Confidence score (0.0 to 1.0)
            tags: Optional list of tags
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created item, or None if creation failed
        """
        # Check if a similar item already exists
        existing_item = self.memory_manager.get_item_by_key(key, scope, scope_id)
        if existing_item:
            logger.warning(f"Memory item with key {key} already exists in scope {scope}")
            return None
            
        return self.memory_manager.create_item(
            key=key,
            value=value,
            memory_type=memory_type,
            scope=scope,
            scope_id=scope_id,
            agent_id=agent_id,
            ttl=ttl,
            importance=importance,
            confidence=confidence,
            tags=tags,
            metadata=metadata
        )
    
    def get_memory(
        self,
        item_id: str,
        agent_id: str
    ) -> Optional[Any]:
        """
        Get a memory item value.
        
        Args:
            item_id: The ID of the item to get
            agent_id: The ID of the agent making the request
            
        Returns:
            The value of the memory item, or None if not found or not accessible
        """
        item = self.memory_manager.get_item(item_id)
        if not item:
            logger.warning(f"Memory item {item_id} not found")
            return None
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to memory item {item_id}")
            return None
            
        return item.value
    
    def update_memory(
        self,
        item_id: str,
        value: Any,
        agent_id: str,
        update_importance: Optional[float] = None,
        update_confidence: Optional[float] = None,
        add_tags: Optional[List[str]] = None,
        remove_tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update a memory item.
        
        Args:
            item_id: The ID of the item to update
            value: The new value
            agent_id: The ID of the agent making the update
            update_importance: Optional new importance score
            update_confidence: Optional new confidence score
            add_tags: Optional tags to add
            remove_tags: Optional tags to remove
            
        Returns:
            True if the update was successful, False otherwise
        """
        item = self.memory_manager.get_item(item_id)
        if not item:
            logger.warning(f"Memory item {item_id} not found")
            return False
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to memory item {item_id}")
            return False
            
        return self.memory_manager.update_item(
            item_id=item_id,
            value=value,
            agent_id=agent_id,
            update_importance=update_importance,
            update_confidence=update_confidence,
            add_tags=add_tags,
            remove_tags=remove_tags
        )
    
    def delete_memory(
        self,
        item_id: str,
        agent_id: str
    ) -> bool:
        """
        Delete a memory item.
        
        Args:
            item_id: The ID of the item to delete
            agent_id: The ID of the agent making the deletion
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        item = self.memory_manager.get_item(item_id)
        if not item:
            logger.warning(f"Memory item {item_id} not found")
            return False
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to memory item {item_id}")
            return False
            
        return self.memory_manager.delete_item(item_id, agent_id)
    
    def query_accessible_memory(
        self,
        agent_id: str,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None,
        key_prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: Optional[float] = None,
        min_confidence: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Query memory items accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            memory_type: Filter by memory type
            scope: Filter by scope
            scope_id: Filter by scope ID
            key_prefix: Filter by key prefix
            tags: Filter by tags
            min_importance: Filter by minimum importance
            min_confidence: Filter by minimum confidence
            
        Returns:
            List of dictionaries with memory item information
        """
        # Query all items matching the criteria
        items = self.memory_manager.query_items(
            memory_type=memory_type,
            scope=scope,
            scope_id=scope_id,
            key_prefix=key_prefix,
            tags=tags,
            min_importance=min_importance,
            min_confidence=min_confidence
        )
        
        # Filter to only include items the agent can access
        accessible_items = [
            item for item in items
            if self.access_controller.can_access(agent_id, item)
        ]
        
        # Convert to dictionaries
        return [
            {
                "item_id": item.item_id,
                "key": item.key,
                "value": item.value,
                "memory_type": item.memory_type.value,
                "scope": item.scope.value,
                "scope_id": item.scope_id,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "created_by": item.created_by,
                "version": item.version,
                "importance": item.importance,
                "confidence": item.confidence,
                "tags": item.tags
            }
            for item in accessible_items
        ]
    
    def search_accessible_memory(
        self,
        agent_id: str,
        search_term: str,
        case_sensitive: bool = False,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memory items by value content, filtered to those accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            search_term: The term to search for
            case_sensitive: Whether the search is case sensitive
            memory_type: Optional filter by memory type
            scope: Optional filter by scope
            scope_id: Optional filter by scope ID
            
        Returns:
            List of dictionaries with memory item information
        """
        # Search all items matching the criteria
        items = self.memory_manager.search_by_value(
            search_term=search_term,
            case_sensitive=case_sensitive,
            memory_type=memory_type,
            scope=scope,
            scope_id=scope_id
        )
        
        # Filter to only include items the agent can access
        accessible_items = [
            item for item in items
            if self.access_controller.can_access(agent_id, item)
        ]
        
        # Convert to dictionaries
        return [
            {
                "item_id": item.item_id,
                "key": item.key,
                "value": item.value,
                "memory_type": item.memory_type.value,
                "scope": item.scope.value,
                "scope_id": item.scope_id,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "created_by": item.created_by,
                "version": item.version,
                "importance": item.importance,
                "confidence": item.confidence,
                "tags": item.tags
            }
            for item in accessible_items
        ]
    
    def get_agent_memory(
        self,
        agent_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        min_importance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get all memory accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            memory_types: Optional list of memory types to include
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        
        # Get global memory
        global_memory = self.memory_manager.get_memory_snapshot(
            scope=MemoryScope.GLOBAL,
            memory_types=memory_types,
            min_importance=min_importance
        )
        result.update(global_memory)
        
        # Get agent-specific memory
        agent_memory = self.memory_manager.get_memory_snapshot(
            scope=MemoryScope.AGENT,
            scope_id=agent_id,
            memory_types=memory_types,
            min_importance=min_importance
        )
        result.update(agent_memory)
        
        # Get team memory for all teams the agent is part of
        agent_teams = self.access_controller.agent_teams.get(agent_id, set())
        for team_id in agent_teams:
            team_memory = self.memory_manager.get_memory_snapshot(
                scope=MemoryScope.TEAM,
                scope_id=team_id,
                memory_types=memory_types,
                min_importance=min_importance
            )
            result.update(team_memory)
            
        # Get task memory for all tasks the agent is working on
        agent_tasks = self.access_controller.agent_tasks.get(agent_id, set())
        for task_id in agent_tasks:
            task_memory = self.memory_manager.get_memory_snapshot(
                scope=MemoryScope.TASK,
                scope_id=task_id,
                memory_types=memory_types,
                min_importance=min_importance
            )
            result.update(task_memory)
            
        # Get session memory for all sessions the agent is part of
        agent_sessions = self.access_controller.agent_sessions.get(agent_id, set())
        for session_id in agent_sessions:
            session_memory = self.memory_manager.get_memory_snapshot(
                scope=MemoryScope.SESSION,
                scope_id=session_id,
                memory_types=memory_types,
                min_importance=min_importance
            )
            result.update(session_memory)
        
        return result
    
    def get_team_memory(
        self,
        team_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        min_importance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get all memory for a team.
        
        Args:
            team_id: The ID of the team
            memory_types: Optional list of memory types to include
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        
        # Get global memory
        global_memory = self.memory_manager.get_memory_snapshot(
            scope=MemoryScope.GLOBAL,
            memory_types=memory_types,
            min_importance=min_importance
        )
        result.update(global_memory)
        
        # Get team-specific memory
        team_memory = self.memory_manager.get_memory_snapshot(
            scope=MemoryScope.TEAM,
            scope_id=team_id,
            memory_types=memory_types,
            min_importance=min_importance
        )
        result.update(team_memory)
        
        return result
    
    def get_task_memory(
        self,
        task_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        min_importance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get all memory for a task.
        
        Args:
            task_id: The ID of the task
            memory_types: Optional list of memory types to include
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        
        # Get global memory
        global_memory = self.memory_manager.get_memory_snapshot(
            scope=MemoryScope.GLOBAL,
            memory_types=memory_types,
            min_importance=min_importance
        )
        result.update(global_memory)
        
        # Get task-specific memory
        task_memory = self.memory_manager.get_memory_snapshot(
            scope=MemoryScope.TASK,
            scope_id=task_id,
            memory_types=memory_types,
            min_importance=min_importance
        )
        result.update(task_memory)
        
        return result
    
    def register_agent_team(self, agent_id: str, team_id: str) -> None:
        """Register an agent as part of a team."""
        self.access_controller.register_agent_team(agent_id, team_id)
        
    def unregister_agent_team(self, agent_id: str, team_id: str) -> None:
        """Unregister an agent from a team."""
        self.access_controller.unregister_agent_team(agent_id, team_id)
    
    def register_agent_task(self, agent_id: str, task_id: str) -> None:
        """Register an agent as working on a task."""
        self.access_controller.register_agent_task(agent_id, task_id)
        
    def unregister_agent_task(self, agent_id: str, task_id: str) -> None:
        """Unregister an agent from a task."""
        self.access_controller.unregister_agent_task(agent_id, task_id)
    
    def register_agent_session(self, agent_id: str, session_id: str) -> None:
        """Register an agent as part of a session."""
        self.access_controller.register_agent_session(agent_id, session_id)
        
    def unregister_agent_session(self, agent_id: str, session_id: str) -> None:
        """Unregister an agent from a session."""
        self.access_controller.unregister_agent_session(agent_id, session_id)
    
    def get_memory_updates(
        self,
        agent_id: str,
        since_timestamp: float
    ) -> List[Dict[str, Any]]:
        """
        Get all memory updates since a specific timestamp that are accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            since_timestamp: The timestamp to get updates since
            
        Returns:
            List of dictionaries with memory change information
        """
        all_changes = self.memory_manager.get_changes_since(since_timestamp)
        
        # Filter changes to only include those the agent can access
        accessible_changes = []
        for change in all_changes:
            item = self.memory_manager.get_item(change.item_id)
            if item and self.access_controller.can_access(agent_id, item):
                accessible_changes.append(change)
            elif not item and change.change_type == "delete":
                # For deleted items, we need to check if the agent could access it before deletion
                # This would require keeping a history of deleted items and their access rules
                # For simplicity, we'll include all deletion changes for now
                accessible_changes.append(change)
                
        # Convert to dictionaries
        return [
            {
                "change_id": change.change_id,
                "item_id": change.item_id,
                "key": change.key,
                "change_type": change.change_type,
                "timestamp": change.timestamp,
                "agent_id": change.agent_id,
                "new_value": change.new_value if change.change_type != "delete" else None
            }
            for change in accessible_changes
        ]
    
    def cleanup_expired_memory(self) -> int:
        """
        Remove all expired memory items.
        
        Returns:
            Number of items removed
        """
        return self.memory_manager.cleanup_expired_items()


class MemoryIntegration:
    """Integration with external memory systems."""
    
    def __init__(self, shared_memory_service: SharedMemoryService):
        self.shared_memory_service = shared_memory_service
        
    def import_from_vector_store(
        self,
        vector_store_data: List[Dict[str, Any]],
        memory_type: MemoryType,
        scope: MemoryScope,
        scope_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        importance_key: Optional[str] = None,
        confidence_key: Optional[str] = None,
        tags_key: Optional[str] = None
    ) -> int:
        """
        Import data from a vector store into shared memory.
        
        Args:
            vector_store_data: List of dictionaries with vector store data
            memory_type: The type of memory to create
            scope: The scope of the memory
            scope_id: The ID of the scope
            agent_id: The ID of the agent importing the data
            importance_key: Optional key for importance in vector store data
            confidence_key: Optional key for confidence in vector store data
            tags_key: Optional key for tags in vector store data
            
        Returns:
            Number of items imported
        """
        count = 0
        
        for item in vector_store_data:
            if "id" not in item or "content" not in item:
                logger.warning("Vector store item missing required fields")
                continue
                
            key = f"vector_store_{item['id']}"
            value = item["content"]
            
            # Extract importance if available
            importance = 0.5
            if importance_key and importance_key in item:
                importance = float(item[importance_key])
                
            # Extract confidence if available
            confidence = 1.0
            if confidence_key and confidence_key in item:
                confidence = float(item[confidence_key])
                
            # Extract tags if available
            tags = []
            if tags_key and tags_key in item:
                tags = item[tags_key]
                
            # Create memory item
            item_id = self.shared_memory_service.create_memory(
                key=key,
                value=value,
                memory_type=memory_type,
                scope=scope,
                scope_id=scope_id,
                agent_id=agent_id,
                importance=importance,
                confidence=confidence,
                tags=tags,
                metadata={"source": "vector_store", "original_id": item["id"]}
            )
            
            if item_id:
                count += 1
                
        logger.info(f"Imported {count} items from vector store")
        return count
    
    def export_to_vector_store(
        self,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None,
        min_importance: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Export data from shared memory to a format suitable for vector stores.
        
        Args:
            memory_type: Optional filter by memory type
            scope: Optional filter by scope
            scope_id: Optional filter by scope ID
            min_importance: Optional minimum importance threshold
            tags: Optional filter by tags
            
        Returns:
            List of dictionaries with vector store data
        """
        # Query items matching the criteria
        items = self.shared_memory_service.memory_manager.query_items(
            memory_type=memory_type,
            scope=scope,
            scope_id=scope_id,
            min_importance=min_importance,
            tags=tags
        )
        
        # Convert to vector store format
        vector_store_data = []
        for item in items:
            vector_store_data.append({
                "id": item.item_id,
                "content": item.value,
                "metadata": {
                    "key": item.key,
                    "memory_type": item.memory_type.value,
                    "scope": item.scope.value,
                    "scope_id": item.scope_id,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "created_by": item.created_by,
                    "importance": item.importance,
                    "confidence": item.confidence,
                    "tags": item.tags
                }
            })
            
        return vector_store_data
    
    def synchronize_with_external_memory(
        self,
        external_memory: Dict[str, Any],
        memory_type: MemoryType,
        scope: MemoryScope,
        scope_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Tuple[int, int, int]:
        """
        Synchronize shared memory with an external memory system.
        
        Args:
            external_memory: Dictionary mapping keys to values from external memory
            memory_type: The type of memory
            scope: The scope of the memory
            scope_id: The ID of the scope
            agent_id: The ID of the agent performing the synchronization
            
        Returns:
            Tuple of (items_added, items_updated, items_unchanged)
        """
        items_added = 0
        items_updated = 0
        items_unchanged = 0
        
        # Get current memory snapshot
        current_memory = self.shared_memory_service.memory_manager.get_memory_snapshot(
            scope=scope,
            scope_id=scope_id,
            memory_types=[memory_type]
        )
        
        # Process each item in external memory
        for key, value in external_memory.items():
            if key in current_memory:
                # Item exists, check if it needs updating
                if current_memory[key] != value:
                    # Find the item by key
                    item = self.shared_memory_service.memory_manager.get_item_by_key(
                        key=key,
                        scope=scope,
                        scope_id=scope_id
                    )
                    
                    if item:
                        # Update the item
                        self.shared_memory_service.update_memory(
                            item_id=item.item_id,
                            value=value,
                            agent_id=agent_id
                        )
                        items_updated += 1
                else:
                    items_unchanged += 1
            else:
                # Item doesn't exist, create it
                self.shared_memory_service.create_memory(
                    key=key,
                    value=value,
                    memory_type=memory_type,
                    scope=scope,
                    scope_id=scope_id,
                    agent_id=agent_id,
                    metadata={"source": "external_sync"}
                )
                items_added += 1
                
        logger.info(f"Synchronized with external memory: {items_added} added, {items_updated} updated, {items_unchanged} unchanged")
        return (items_added, items_updated, items_unchanged)
