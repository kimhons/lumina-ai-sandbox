"""
Shared Context Manager Module for Advanced Multi-Agent Collaboration System
This module provides enhanced shared context management capabilities for Lumina AI,
enabling efficient knowledge sharing between agents with sophisticated context
synchronization, memory integration, and versioning.
"""
import logging
from typing import List, Dict, Set, Optional, Tuple, Any, Union
import numpy as np
from dataclasses import dataclass, field
import json
import time
import uuid
from enum import Enum
import copy
import hashlib
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of shared contexts."""
    TASK = "TASK"
    KNOWLEDGE = "KNOWLEDGE"
    CONVERSATION = "CONVERSATION"
    ENVIRONMENT = "ENVIRONMENT"
    USER_PROFILE = "USER_PROFILE"
    SYSTEM_STATE = "SYSTEM_STATE"
    CUSTOM = "CUSTOM"

class AccessLevel(Enum):
    """Access levels for shared context."""
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"
    ADMIN = "ADMIN"
    NONE = "NONE"

class ContextOperation(Enum):
    """Operations that can be performed on shared context."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    MERGE = "MERGE"
    FORK = "FORK"
    SUBSCRIBE = "SUBSCRIBE"
    UNSUBSCRIBE = "UNSUBSCRIBE"

@dataclass
class ContextChange:
    """Represents a change to a shared context."""
    agent_id: str
    timestamp: float
    operation: ContextOperation
    path: str
    old_value: Any = None
    new_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"Change({self.operation.value} at {self.path} by {self.agent_id})"

@dataclass
class ContextVersion:
    """Represents a version of a shared context."""
    version_id: str
    timestamp: float
    agent_id: str
    parent_version_id: Optional[str] = None
    changes: List[ContextChange] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_value: str = ""
    
    def __post_init__(self):
        if not self.hash_value:
            self.compute_hash()
    
    def compute_hash(self):
        """Compute a hash value for this version."""
        content = f"{self.version_id}:{self.timestamp}:{self.agent_id}:{self.parent_version_id}"
        for change in self.changes:
            content += f":{change.operation.value}:{change.path}:{change.new_value}"
        self.hash_value = hashlib.sha256(content.encode()).hexdigest()
    
    def __str__(self) -> str:
        return f"Version({self.version_id}, changes={len(self.changes)})"

@dataclass
class ContextAccess:
    """Represents access control for an agent to a shared context."""
    agent_id: str
    access_level: AccessLevel
    granted_at: float = field(default_factory=time.time)
    granted_by: Optional[str] = None
    expires_at: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if access has expired."""
        return self.expires_at is not None and time.time() > self.expires_at
    
    def can_perform(self, operation: ContextOperation) -> bool:
        """Check if the agent can perform the specified operation."""
        if self.is_expired():
            return False
            
        if self.access_level == AccessLevel.ADMIN:
            return True
            
        if self.access_level == AccessLevel.READ_WRITE:
            return operation != ContextOperation.DELETE
            
        if self.access_level == AccessLevel.READ_ONLY:
            return operation == ContextOperation.READ or operation == ContextOperation.SUBSCRIBE
            
        return False
    
    def __str__(self) -> str:
        return f"Access({self.agent_id}, {self.access_level.value})"

@dataclass
class SharedContext:
    """Represents a shared context between multiple agents."""
    id: str
    name: str
    context_type: ContextType
    owner_id: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    content: Dict[str, Any] = field(default_factory=dict)
    access_control: List[ContextAccess] = field(default_factory=list)
    version_history: List[ContextVersion] = field(default_factory=list)
    current_version_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    subscribers: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if not self.current_version_id and self.version_history:
            self.current_version_id = self.version_history[-1].version_id
    
    def get_agent_access(self, agent_id: str) -> Optional[ContextAccess]:
        """Get access control for a specific agent."""
        for access in self.access_control:
            if access.agent_id == agent_id and not access.is_expired():
                return access
        return None
    
    def can_agent_perform(self, agent_id: str, operation: ContextOperation) -> bool:
        """Check if an agent can perform the specified operation."""
        # Owner can do anything
        if agent_id == self.owner_id:
            return True
            
        # Check access control
        access = self.get_agent_access(agent_id)
        return access is not None and access.can_perform(operation)
    
    def get_current_version(self) -> Optional[ContextVersion]:
        """Get the current version of the context."""
        if not self.current_version_id:
            return None
            
        for version in self.version_history:
            if version.version_id == self.current_version_id:
                return version
                
        return None
    
    def add_version(self, version: ContextVersion) -> None:
        """Add a new version to the history."""
        self.version_history.append(version)
        self.current_version_id = version.version_id
        self.updated_at = time.time()
    
    def __str__(self) -> str:
        return f"SharedContext({self.name}, type={self.context_type.value}, versions={len(self.version_history)})"

class SharedContextManager:
    """
    Enhanced shared context manager that provides sophisticated context management
    capabilities for efficient knowledge sharing between agents.
    """
    
    def __init__(self, memory_integration_enabled: bool = True):
        """
        Initialize the shared context manager.
        
        Args:
            memory_integration_enabled: Whether to enable integration with the memory system
        """
        self.contexts: Dict[str, SharedContext] = {}
        self.memory_integration_enabled = memory_integration_enabled
        self.memory_service = None
        
        if memory_integration_enabled:
            try:
                # Import memory service integration
                from memory_integration import MemoryServiceClient
                self.memory_service = MemoryServiceClient()
                logger.info("Memory integration enabled for shared context manager")
            except ImportError:
                logger.warning("Memory integration requested but MemoryServiceClient not available")
                self.memory_integration_enabled = False
    
    def create_context(self, 
                     name: str, 
                     context_type: ContextType, 
                     owner_id: str, 
                     initial_content: Dict[str, Any] = None,
                     access_control: List[ContextAccess] = None) -> SharedContext:
        """
        Create a new shared context.
        
        Args:
            name: Name of the context
            context_type: Type of the context
            owner_id: ID of the agent creating the context
            initial_content: Initial content of the context
            access_control: Initial access control settings
            
        Returns:
            The created shared context
        """
        context_id = str(uuid.uuid4())
        
        # Create initial version
        initial_version = ContextVersion(
            version_id=str(uuid.uuid4()),
            timestamp=time.time(),
            agent_id=owner_id,
            changes=[
                ContextChange(
                    agent_id=owner_id,
                    timestamp=time.time(),
                    operation=ContextOperation.CREATE,
                    path="/",
                    new_value=initial_content or {}
                )
            ]
        )
        
        # Create context
        context = SharedContext(
            id=context_id,
            name=name,
            context_type=context_type,
            owner_id=owner_id,
            content=initial_content or {},
            access_control=access_control or [],
            version_history=[initial_version],
            current_version_id=initial_version.version_id,
            subscribers={owner_id}  # Owner is automatically subscribed
        )
        
        # Store context
        self.contexts[context_id] = context
        
        # Integrate with memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._store_context_in_memory(context)
        
        logger.info(f"Created shared context: {name} (ID: {context_id}) of type {context_type.value}")
        return context
    
    def get_context(self, context_id: str) -> Optional[SharedContext]:
        """Get a shared context by ID."""
        # Try to get from local cache first
        context = self.contexts.get(context_id)
        
        # If not found and memory integration is enabled, try to retrieve from memory
        if context is None and self.memory_integration_enabled and self.memory_service:
            context = self._retrieve_context_from_memory(context_id)
            if context:
                # Cache it locally
                self.contexts[context_id] = context
        
        return context
    
    def update_context(self, 
                     context_id: str, 
                     agent_id: str, 
                     updates: Dict[str, Any],
                     metadata: Dict[str, Any] = None) -> Optional[SharedContext]:
        """
        Update a shared context.
        
        Args:
            context_id: ID of the context to update
            agent_id: ID of the agent making the update
            updates: Dictionary of updates to apply (path -> value)
            metadata: Optional metadata for the update
            
        Returns:
            The updated shared context, or None if update failed
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return None
        
        # Check if agent can update
        if not context.can_agent_perform(agent_id, ContextOperation.UPDATE):
            logger.warning(f"Agent {agent_id} does not have permission to update context {context_id}")
            return None
        
        # Create changes
        changes = []
        for path, new_value in updates.items():
            # Get old value
            old_value = self._get_value_at_path(context.content, path)
            
            # Create change
            change = ContextChange(
                agent_id=agent_id,
                timestamp=time.time(),
                operation=ContextOperation.UPDATE,
                path=path,
                old_value=old_value,
                new_value=new_value,
                metadata=metadata or {}
            )
            changes.append(change)
            
            # Apply update
            self._set_value_at_path(context.content, path, new_value)
        
        # Create new version
        new_version = ContextVersion(
            version_id=str(uuid.uuid4()),
            timestamp=time.time(),
            agent_id=agent_id,
            parent_version_id=context.current_version_id,
            changes=changes,
            metadata=metadata or {}
        )
        
        # Add version to history
        context.add_version(new_version)
        
        # Notify subscribers
        self._notify_subscribers(context, changes)
        
        # Update in memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._update_context_in_memory(context)
        
        logger.info(f"Updated context {context_id} with {len(changes)} changes by agent {agent_id}")
        return context
    
    def merge_contexts(self, 
                     target_context_id: str, 
                     source_context_id: str, 
                     agent_id: str,
                     conflict_resolution: str = "latest") -> Optional[SharedContext]:
        """
        Merge two shared contexts.
        
        Args:
            target_context_id: ID of the target context
            source_context_id: ID of the source context
            agent_id: ID of the agent performing the merge
            conflict_resolution: Strategy for resolving conflicts ("latest", "source", "target")
            
        Returns:
            The merged context, or None if merge failed
        """
        target_context = self.get_context(target_context_id)
        source_context = self.get_context(source_context_id)
        
        if not target_context or not source_context:
            logger.warning(f"One or both contexts not found: {target_context_id}, {source_context_id}")
            return None
        
        # Check if agent can update target and read source
        if not target_context.can_agent_perform(agent_id, ContextOperation.UPDATE):
            logger.warning(f"Agent {agent_id} does not have permission to update target context {target_context_id}")
            return None
            
        if not source_context.can_agent_perform(agent_id, ContextOperation.READ):
            logger.warning(f"Agent {agent_id} does not have permission to read source context {source_context_id}")
            return None
        
        # Perform merge
        merged_content = self._merge_contents(
            target_context.content, 
            source_context.content, 
            conflict_resolution
        )
        
        # Create changes
        changes = []
        change = ContextChange(
            agent_id=agent_id,
            timestamp=time.time(),
            operation=ContextOperation.MERGE,
            path="/",
            old_value=target_context.content,
            new_value=merged_content,
            metadata={"source_context_id": source_context_id}
        )
        changes.append(change)
        
        # Update target content
        target_context.content = merged_content
        
        # Create new version
        new_version = ContextVersion(
            version_id=str(uuid.uuid4()),
            timestamp=time.time(),
            agent_id=agent_id,
            parent_version_id=target_context.current_version_id,
            changes=changes,
            metadata={"merge_source": source_context_id, "conflict_resolution": conflict_resolution}
        )
        
        # Add version to history
        target_context.add_version(new_version)
        
        # Notify subscribers
        self._notify_subscribers(target_context, changes)
        
        # Update in memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._update_context_in_memory(target_context)
        
        logger.info(f"Merged context {source_context_id} into {target_context_id} by agent {agent_id}")
        return target_context
    
    def fork_context(self, 
                   context_id: str, 
                   agent_id: str, 
                   new_name: str = None) -> Optional[SharedContext]:
        """
        Fork a shared context to create a new one.
        
        Args:
            context_id: ID of the context to fork
            agent_id: ID of the agent performing the fork
            new_name: Name for the new context (defaults to "Fork of [original name]")
            
        Returns:
            The new forked context, or None if fork failed
        """
        source_context = self.get_context(context_id)
        if not source_context:
            logger.warning(f"Context not found: {context_id}")
            return None
        
        # Check if agent can read source
        if not source_context.can_agent_perform(agent_id, ContextOperation.READ):
            logger.warning(f"Agent {agent_id} does not have permission to read context {context_id}")
            return None
        
        # Create new context with copy of content
        new_name = new_name or f"Fork of {source_context.name}"
        new_content = copy.deepcopy(source_context.content)
        
        # Create new context
        forked_context = self.create_context(
            name=new_name,
            context_type=source_context.context_type,
            owner_id=agent_id,
            initial_content=new_content,
            access_control=[]  # Start with clean access control
        )
        
        # Add metadata about fork
        forked_context.metadata["forked_from"] = context_id
        forked_context.metadata["fork_time"] = time.time()
        
        # Update in memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._update_context_in_memory(forked_context)
        
        logger.info(f"Forked context {context_id} to new context {forked_context.id} by agent {agent_id}")
        return forked_context
    
    def grant_access(self, 
                   context_id: str, 
                   granting_agent_id: str, 
                   target_agent_id: str, 
                   access_level: AccessLevel,
                   expires_in: Optional[float] = None) -> bool:
        """
        Grant access to a shared context for an agent.
        
        Args:
            context_id: ID of the context
            granting_agent_id: ID of the agent granting access
            target_agent_id: ID of the agent receiving access
            access_level: Level of access to grant
            expires_in: Optional time in seconds until access expires
            
        Returns:
            True if access was granted, False otherwise
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return False
        
        # Check if granting agent has admin access
        if not context.can_agent_perform(granting_agent_id, ContextOperation.DELETE):  # DELETE requires ADMIN
            logger.warning(f"Agent {granting_agent_id} does not have admin permission for context {context_id}")
            return False
        
        # Calculate expiration time if provided
        expires_at = None
        if expires_in is not None:
            expires_at = time.time() + expires_in
        
        # Create or update access
        existing_access = None
        for access in context.access_control:
            if access.agent_id == target_agent_id:
                existing_access = access
                break
        
        if existing_access:
            # Update existing access
            existing_access.access_level = access_level
            existing_access.granted_at = time.time()
            existing_access.granted_by = granting_agent_id
            existing_access.expires_at = expires_at
        else:
            # Create new access
            new_access = ContextAccess(
                agent_id=target_agent_id,
                access_level=access_level,
                granted_at=time.time(),
                granted_by=granting_agent_id,
                expires_at=expires_at
            )
            context.access_control.append(new_access)
        
        # Update in memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._update_context_in_memory(context)
        
        logger.info(f"Granted {access_level.value} access to agent {target_agent_id} for context {context_id}")
        return True
    
    def revoke_access(self, 
                    context_id: str, 
                    revoking_agent_id: str, 
                    target_agent_id: str) -> bool:
        """
        Revoke access to a shared context for an agent.
        
        Args:
            context_id: ID of the context
            revoking_agent_id: ID of the agent revoking access
            target_agent_id: ID of the agent whose access is being revoked
            
        Returns:
            True if access was revoked, False otherwise
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return False
        
        # Check if revoking agent has admin access
        if not context.can_agent_perform(revoking_agent_id, ContextOperation.DELETE):  # DELETE requires ADMIN
            logger.warning(f"Agent {revoking_agent_id} does not have admin permission for context {context_id}")
            return False
        
        # Cannot revoke access for the owner
        if target_agent_id == context.owner_id:
            logger.warning(f"Cannot revoke access for owner of context {context_id}")
            return False
        
        # Find and remove access
        for i, access in enumerate(context.access_control):
            if access.agent_id == target_agent_id:
                context.access_control.pop(i)
                
                # Update in memory system if enabled
                if self.memory_integration_enabled and self.memory_service:
                    self._update_context_in_memory(context)
                
                logger.info(f"Revoked access for agent {target_agent_id} to context {context_id}")
                return True
        
        logger.warning(f"Agent {target_agent_id} did not have access to context {context_id}")
        return False
    
    def subscribe(self, context_id: str, agent_id: str) -> bool:
        """
        Subscribe an agent to updates for a shared context.
        
        Args:
            context_id: ID of the context
            agent_id: ID of the agent subscribing
            
        Returns:
            True if subscription was successful, False otherwise
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return False
        
        # Check if agent can read
        if not context.can_agent_perform(agent_id, ContextOperation.READ):
            logger.warning(f"Agent {agent_id} does not have read permission for context {context_id}")
            return False
        
        # Add to subscribers
        context.subscribers.add(agent_id)
        
        # Update in memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._update_context_in_memory(context)
        
        logger.info(f"Agent {agent_id} subscribed to context {context_id}")
        return True
    
    def unsubscribe(self, context_id: str, agent_id: str) -> bool:
        """
        Unsubscribe an agent from updates for a shared context.
        
        Args:
            context_id: ID of the context
            agent_id: ID of the agent unsubscribing
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return False
        
        # Remove from subscribers
        if agent_id in context.subscribers:
            context.subscribers.remove(agent_id)
            
            # Update in memory system if enabled
            if self.memory_integration_enabled and self.memory_service:
                self._update_context_in_memory(context)
            
            logger.info(f"Agent {agent_id} unsubscribed from context {context_id}")
            return True
        
        logger.warning(f"Agent {agent_id} was not subscribed to context {context_id}")
        return False
    
    def get_context_version(self, context_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of a shared context.
        
        Args:
            context_id: ID of the context
            version_id: ID of the version to retrieve
            
        Returns:
            The context content at the specified version, or None if not found
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return None
        
        # Find the specified version
        target_version = None
        for version in context.version_history:
            if version.version_id == version_id:
                target_version = version
                break
        
        if not target_version:
            logger.warning(f"Version {version_id} not found for context {context_id}")
            return None
        
        # Reconstruct content at this version
        return self._reconstruct_version_content(context, target_version)
    
    def compare_versions(self, 
                       context_id: str, 
                       version_id1: str, 
                       version_id2: str) -> Dict[str, Any]:
        """
        Compare two versions of a shared context.
        
        Args:
            context_id: ID of the context
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            A dictionary containing differences between the versions
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return {"error": "Context not found"}
        
        # Get content for both versions
        content1 = self.get_context_version(context_id, version_id1)
        content2 = self.get_context_version(context_id, version_id2)
        
        if not content1 or not content2:
            logger.warning(f"One or both versions not found: {version_id1}, {version_id2}")
            return {"error": "One or both versions not found"}
        
        # Find differences
        differences = self._find_differences(content1, content2)
        
        # Get metadata for both versions
        version1 = next((v for v in context.version_history if v.version_id == version_id1), None)
        version2 = next((v for v in context.version_history if v.version_id == version_id2), None)
        
        metadata1 = version1.metadata if version1 else {}
        metadata2 = version2.metadata if version2 else {}
        
        return {
            "differences": differences,
            "version1": {
                "id": version_id1,
                "timestamp": version1.timestamp if version1 else None,
                "agent_id": version1.agent_id if version1 else None,
                "metadata": metadata1
            },
            "version2": {
                "id": version_id2,
                "timestamp": version2.timestamp if version2 else None,
                "agent_id": version2.agent_id if version2 else None,
                "metadata": metadata2
            }
        }
    
    def revert_to_version(self, 
                        context_id: str, 
                        version_id: str, 
                        agent_id: str) -> Optional[SharedContext]:
        """
        Revert a shared context to a previous version.
        
        Args:
            context_id: ID of the context
            version_id: ID of the version to revert to
            agent_id: ID of the agent performing the revert
            
        Returns:
            The reverted context, or None if revert failed
        """
        context = self.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return None
        
        # Check if agent can update
        if not context.can_agent_perform(agent_id, ContextOperation.UPDATE):
            logger.warning(f"Agent {agent_id} does not have permission to update context {context_id}")
            return None
        
        # Get content at the specified version
        version_content = self.get_context_version(context_id, version_id)
        if not version_content:
            logger.warning(f"Version {version_id} not found for context {context_id}")
            return None
        
        # Create change
        change = ContextChange(
            agent_id=agent_id,
            timestamp=time.time(),
            operation=ContextOperation.UPDATE,
            path="/",
            old_value=context.content,
            new_value=version_content,
            metadata={"reverted_to": version_id}
        )
        
        # Update content
        context.content = copy.deepcopy(version_content)
        
        # Create new version
        new_version = ContextVersion(
            version_id=str(uuid.uuid4()),
            timestamp=time.time(),
            agent_id=agent_id,
            parent_version_id=context.current_version_id,
            changes=[change],
            metadata={"reverted_to": version_id}
        )
        
        # Add version to history
        context.add_version(new_version)
        
        # Notify subscribers
        self._notify_subscribers(context, [change])
        
        # Update in memory system if enabled
        if self.memory_integration_enabled and self.memory_service:
            self._update_context_in_memory(context)
        
        logger.info(f"Reverted context {context_id} to version {version_id} by agent {agent_id}")
        return context
    
    def search_contexts(self, 
                      query: str, 
                      context_type: Optional[ContextType] = None, 
                      agent_id: Optional[str] = None) -> List[SharedContext]:
        """
        Search for shared contexts matching a query.
        
        Args:
            query: Search query
            context_type: Optional filter by context type
            agent_id: Optional filter by agent with access
            
        Returns:
            List of matching contexts
        """
        results = []
        
        # If memory integration is enabled, try to search in memory first
        if self.memory_integration_enabled and self.memory_service:
            memory_results = self._search_contexts_in_memory(query, context_type, agent_id)
            if memory_results:
                # Cache results locally
                for context in memory_results:
                    self.contexts[context.id] = context
                return memory_results
        
        # Search locally
        for context in self.contexts.values():
            # Apply filters
            if context_type and context.context_type != context_type:
                continue
                
            if agent_id and not context.can_agent_perform(agent_id, ContextOperation.READ):
                continue
            
            # Check if query matches
            if (query.lower() in context.name.lower() or
                any(query.lower() in str(v).lower() for v in context.content.values())):
                results.append(context)
        
        return results
    
    def _get_value_at_path(self, content: Dict[str, Any], path: str) -> Any:
        """Get a value at a specific path in the content."""
        if path == "/":
            return content
            
        parts = path.strip("/").split("/")
        current = content
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
    
    def _set_value_at_path(self, content: Dict[str, Any], path: str, value: Any) -> None:
        """Set a value at a specific path in the content."""
        if path == "/":
            # Replace entire content
            content.clear()
            content.update(value)
            return
            
        parts = path.strip("/").split("/")
        current = content
        
        # Navigate to the parent of the target
        for i in range(len(parts) - 1):
            part = parts[i]
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
    
    def _merge_contents(self, 
                      target_content: Dict[str, Any], 
                      source_content: Dict[str, Any], 
                      conflict_resolution: str) -> Dict[str, Any]:
        """Merge two content dictionaries."""
        result = copy.deepcopy(target_content)
        
        def merge_recursive(target, source, path=""):
            for key, value in source.items():
                full_path = f"{path}/{key}".lstrip("/")
                
                if key in target:
                    # Handle conflict
                    if isinstance(value, dict) and isinstance(target[key], dict):
                        # Recursively merge dictionaries
                        merge_recursive(target[key], value, full_path)
                    else:
                        # Resolve conflict based on strategy
                        if conflict_resolution == "source":
                            target[key] = copy.deepcopy(value)
                        elif conflict_resolution == "target":
                            pass  # Keep target value
                        else:  # "latest" or default
                            target[key] = copy.deepcopy(value)
                else:
                    # No conflict, just add
                    target[key] = copy.deepcopy(value)
        
        merge_recursive(result, source_content)
        return result
    
    def _notify_subscribers(self, context: SharedContext, changes: List[ContextChange]) -> None:
        """Notify subscribers of changes to a context."""
        # In a real implementation, this would send notifications to subscribers
        # For now, we'll just log the notifications
        for subscriber_id in context.subscribers:
            logger.info(f"Notifying agent {subscriber_id} of {len(changes)} changes to context {context.id}")
    
    def _reconstruct_version_content(self, context: SharedContext, target_version: ContextVersion) -> Dict[str, Any]:
        """Reconstruct the content of a context at a specific version."""
        # Find the path from the target version to the initial version
        version_path = []
        current_version = target_version
        
        while current_version:
            version_path.append(current_version)
            
            if not current_version.parent_version_id:
                break
                
            # Find parent version
            current_version = next(
                (v for v in context.version_history if v.version_id == current_version.parent_version_id), 
                None
            )
        
        # Reverse to start from initial version
        version_path.reverse()
        
        # Start with empty content
        content = {}
        
        # Apply changes in order
        for version in version_path:
            for change in version.changes:
                if change.operation == ContextOperation.CREATE or change.operation == ContextOperation.UPDATE:
                    self._set_value_at_path(content, change.path, copy.deepcopy(change.new_value))
                elif change.operation == ContextOperation.DELETE:
                    # Handle delete operation if needed
                    pass
        
        return content
    
    def _find_differences(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> Dict[str, Any]:
        """Find differences between two content dictionaries."""
        differences = {
            "added": {},
            "removed": {},
            "modified": {}
        }
        
        def compare_recursive(dict1, dict2, path=""):
            # Find keys in dict2 that are not in dict1 (added)
            for key in dict2:
                if key not in dict1:
                    full_path = f"{path}/{key}".lstrip("/")
                    differences["added"][full_path] = dict2[key]
            
            # Find keys in dict1 that are not in dict2 (removed)
            for key in dict1:
                if key not in dict2:
                    full_path = f"{path}/{key}".lstrip("/")
                    differences["removed"][full_path] = dict1[key]
            
            # Find keys that are in both but with different values (modified)
            for key in dict1:
                if key in dict2:
                    full_path = f"{path}/{key}".lstrip("/")
                    
                    if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                        # Recursively compare dictionaries
                        compare_recursive(dict1[key], dict2[key], full_path)
                    elif dict1[key] != dict2[key]:
                        differences["modified"][full_path] = {
                            "from": dict1[key],
                            "to": dict2[key]
                        }
        
        compare_recursive(content1, content2)
        return differences
    
    def _store_context_in_memory(self, context: SharedContext) -> bool:
        """Store a context in the memory system."""
        if not self.memory_service:
            return False
            
        try:
            # Convert to format suitable for memory storage
            memory_item = {
                "id": context.id,
                "type": "shared_context",
                "name": context.name,
                "context_type": context.context_type.value,
                "content": context.content,
                "created_at": context.created_at,
                "updated_at": context.updated_at,
                "owner_id": context.owner_id,
                "current_version_id": context.current_version_id,
                "metadata": context.metadata
            }
            
            # Store in memory
            self.memory_service.store_item(memory_item)
            logger.info(f"Stored context {context.id} in memory system")
            return True
        except Exception as e:
            logger.error(f"Failed to store context in memory: {e}")
            return False
    
    def _update_context_in_memory(self, context: SharedContext) -> bool:
        """Update a context in the memory system."""
        return self._store_context_in_memory(context)
    
    def _retrieve_context_from_memory(self, context_id: str) -> Optional[SharedContext]:
        """Retrieve a context from the memory system."""
        if not self.memory_service:
            return None
            
        try:
            # Retrieve from memory
            memory_item = self.memory_service.retrieve_item(context_id, "shared_context")
            
            if not memory_item:
                return None
                
            # Convert back to SharedContext
            context = SharedContext(
                id=memory_item["id"],
                name=memory_item["name"],
                context_type=ContextType(memory_item["context_type"]),
                owner_id=memory_item["owner_id"],
                created_at=memory_item["created_at"],
                updated_at=memory_item["updated_at"],
                content=memory_item["content"],
                current_version_id=memory_item["current_version_id"],
                metadata=memory_item["metadata"],
                access_control=[],  # Will need to retrieve separately
                version_history=[],  # Will need to retrieve separately
                subscribers=set()  # Will need to retrieve separately
            )
            
            # Retrieve additional data
            self._retrieve_context_details(context)
            
            logger.info(f"Retrieved context {context_id} from memory system")
            return context
        except Exception as e:
            logger.error(f"Failed to retrieve context from memory: {e}")
            return None
    
    def _retrieve_context_details(self, context: SharedContext) -> None:
        """Retrieve additional details for a context from the memory system."""
        if not self.memory_service:
            return
            
        try:
            # Retrieve access control
            access_control_items = self.memory_service.retrieve_related_items(
                context.id, "context_access")
            
            for item in access_control_items:
                access = ContextAccess(
                    agent_id=item["agent_id"],
                    access_level=AccessLevel(item["access_level"]),
                    granted_at=item["granted_at"],
                    granted_by=item["granted_by"],
                    expires_at=item.get("expires_at")
                )
                context.access_control.append(access)
            
            # Retrieve version history
            version_items = self.memory_service.retrieve_related_items(
                context.id, "context_version")
            
            for item in version_items:
                # Retrieve changes for this version
                change_items = self.memory_service.retrieve_related_items(
                    item["version_id"], "context_change")
                
                changes = []
                for change_item in change_items:
                    change = ContextChange(
                        agent_id=change_item["agent_id"],
                        timestamp=change_item["timestamp"],
                        operation=ContextOperation(change_item["operation"]),
                        path=change_item["path"],
                        old_value=change_item.get("old_value"),
                        new_value=change_item.get("new_value"),
                        metadata=change_item.get("metadata", {})
                    )
                    changes.append(change)
                
                version = ContextVersion(
                    version_id=item["version_id"],
                    timestamp=item["timestamp"],
                    agent_id=item["agent_id"],
                    parent_version_id=item.get("parent_version_id"),
                    changes=changes,
                    metadata=item.get("metadata", {}),
                    hash_value=item.get("hash_value", "")
                )
                context.version_history.append(version)
            
            # Sort version history by timestamp
            context.version_history.sort(key=lambda v: v.timestamp)
            
            # Retrieve subscribers
            subscriber_items = self.memory_service.retrieve_related_items(
                context.id, "context_subscriber")
            
            for item in subscriber_items:
                context.subscribers.add(item["agent_id"])
                
        except Exception as e:
            logger.error(f"Failed to retrieve context details from memory: {e}")
    
    def _search_contexts_in_memory(self, 
                                 query: str, 
                                 context_type: Optional[ContextType] = None, 
                                 agent_id: Optional[str] = None) -> List[SharedContext]:
        """Search for contexts in the memory system."""
        if not self.memory_service:
            return []
            
        try:
            # Prepare search criteria
            criteria = {
                "type": "shared_context",
                "query": query
            }
            
            if context_type:
                criteria["context_type"] = context_type.value
                
            if agent_id:
                criteria["agent_id"] = agent_id
            
            # Search in memory
            memory_items = self.memory_service.search_items(criteria)
            
            # Convert to SharedContext objects
            contexts = []
            for item in memory_items:
                context = SharedContext(
                    id=item["id"],
                    name=item["name"],
                    context_type=ContextType(item["context_type"]),
                    owner_id=item["owner_id"],
                    created_at=item["created_at"],
                    updated_at=item["updated_at"],
                    content=item["content"],
                    current_version_id=item["current_version_id"],
                    metadata=item["metadata"],
                    access_control=[],  # Will retrieve separately
                    version_history=[],  # Will retrieve separately
                    subscribers=set()  # Will retrieve separately
                )
                
                # Retrieve additional data
                self._retrieve_context_details(context)
                
                contexts.append(context)
            
            logger.info(f"Found {len(contexts)} contexts in memory system matching query: {query}")
            return contexts
        except Exception as e:
            logger.error(f"Failed to search contexts in memory: {e}")
            return []
