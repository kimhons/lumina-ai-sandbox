"""
Collaborative Context Manager for Advanced Multi-Agent Collaboration.

This module implements the Collaborative Context Manager, which maintains shared context
between agents, enabling them to work with a common understanding of the task and environment.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import uuid
import time
import json
import logging
import copy
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ContextScope(Enum):
    """Enum representing different context scopes."""
    GLOBAL = "global"         # Visible to all agents
    TEAM = "team"             # Visible to team members only
    AGENT = "agent"           # Visible to specific agent only
    TASK = "task"             # Visible in the context of a specific task
    SESSION = "session"       # Visible for the duration of a session


class ContextType(Enum):
    """Enum representing different context types."""
    TASK_DEFINITION = "task_definition"
    USER_PREFERENCES = "user_preferences"
    CONVERSATION_HISTORY = "conversation_history"
    AGENT_OBSERVATIONS = "agent_observations"
    INTERMEDIATE_RESULTS = "intermediate_results"
    EXTERNAL_KNOWLEDGE = "external_knowledge"
    SYSTEM_STATE = "system_state"
    EXECUTION_PLAN = "execution_plan"


@dataclass
class ContextItem:
    """Represents a single context item."""
    item_id: str
    key: str
    value: Any
    context_type: ContextType
    scope: ContextScope
    scope_id: Optional[str] = None  # ID of team, agent, task, or session
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    created_by: Optional[str] = None  # Agent ID
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, value: Any, updated_by: Optional[str] = None) -> None:
        """Update the context item value."""
        self.value = value
        self.updated_at = time.time()
        if updated_by:
            self.metadata["last_updated_by"] = updated_by
        self.version += 1


@dataclass
class ContextChange:
    """Represents a change to the context."""
    change_id: str
    item_id: str
    key: str
    old_value: Any
    new_value: Any
    change_type: str  # "create", "update", "delete"
    timestamp: float
    agent_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextConflictResolver:
    """Resolves conflicts in context updates."""
    
    def resolve_conflict(
        self, 
        current_item: ContextItem, 
        conflicting_updates: List[Tuple[str, Any]]
    ) -> Any:
        """
        Resolve conflicts between multiple updates to the same context item.
        
        Args:
            current_item: The current context item
            conflicting_updates: List of (agent_id, value) tuples representing conflicting updates
            
        Returns:
            The resolved value
        """
        raise NotImplementedError("Subclasses must implement resolve_conflict method")


class LastWriteWinsResolver(ContextConflictResolver):
    """Resolver that uses the last write wins strategy."""
    
    def resolve_conflict(
        self, 
        current_item: ContextItem, 
        conflicting_updates: List[Tuple[str, Any]]
    ) -> Any:
        """Resolve conflicts by taking the last update."""
        if not conflicting_updates:
            return current_item.value
        
        # Return the last update
        return conflicting_updates[-1][1]


class MergeResolver(ContextConflictResolver):
    """Resolver that attempts to merge updates."""
    
    def resolve_conflict(
        self, 
        current_item: ContextItem, 
        conflicting_updates: List[Tuple[str, Any]]
    ) -> Any:
        """Resolve conflicts by merging updates when possible."""
        if not conflicting_updates:
            return current_item.value
        
        # Start with the current value
        result = copy.deepcopy(current_item.value)
        
        # Try to merge based on type
        if isinstance(result, dict):
            # For dictionaries, merge keys
            for _, update_value in conflicting_updates:
                if isinstance(update_value, dict):
                    result.update(update_value)
        elif isinstance(result, list):
            # For lists, append unique items
            for _, update_value in conflicting_updates:
                if isinstance(update_value, list):
                    for item in update_value:
                        if item not in result:
                            result.append(item)
        elif isinstance(result, str):
            # For strings, concatenate with separator
            for _, update_value in conflicting_updates:
                if isinstance(update_value, str):
                    result += "\n---\n" + update_value
        else:
            # For other types, use last write wins
            result = conflicting_updates[-1][1]
            
        return result


class VotingResolver(ContextConflictResolver):
    """Resolver that uses voting to resolve conflicts."""
    
    def resolve_conflict(
        self, 
        current_item: ContextItem, 
        conflicting_updates: List[Tuple[str, Any]]
    ) -> Any:
        """Resolve conflicts by voting."""
        if not conflicting_updates:
            return current_item.value
        
        # Count votes for each value
        value_counts = {}
        for _, value in conflicting_updates:
            # Convert value to string for counting
            value_str = str(value)
            if value_str not in value_counts:
                value_counts[value_str] = 0
            value_counts[value_str] += 1
        
        # Find the value with the most votes
        max_votes = 0
        max_value_str = None
        for value_str, count in value_counts.items():
            if count > max_votes:
                max_votes = count
                max_value_str = value_str
        
        # Find the original value object
        for _, value in conflicting_updates:
            if str(value) == max_value_str:
                return value
        
        # Fallback to current value
        return current_item.value


class ContextSynchronizer:
    """Handles context synchronization between agents."""
    
    def __init__(self, conflict_resolver: ContextConflictResolver = None):
        self.conflict_resolver = conflict_resolver or LastWriteWinsResolver()
        self.pending_updates: Dict[str, List[Tuple[str, Any]]] = {}
        self.change_log: List[ContextChange] = []
        
    def record_update(self, item_id: str, agent_id: str, value: Any) -> None:
        """Record an update to a context item."""
        if item_id not in self.pending_updates:
            self.pending_updates[item_id] = []
        self.pending_updates[item_id].append((agent_id, value))
        
    def has_conflicts(self, item_id: str) -> bool:
        """Check if there are conflicting updates for a context item."""
        return item_id in self.pending_updates and len(self.pending_updates[item_id]) > 1
    
    def resolve_conflicts(self, item: ContextItem) -> Any:
        """Resolve conflicts for a context item."""
        if item.item_id not in self.pending_updates:
            return item.value
            
        updates = self.pending_updates[item.item_id]
        if len(updates) <= 1:
            return updates[0][1] if updates else item.value
            
        resolved_value = self.conflict_resolver.resolve_conflict(item, updates)
        
        # Log the resolution
        self._log_resolution(item, updates, resolved_value)
        
        # Clear pending updates
        del self.pending_updates[item.item_id]
        
        return resolved_value
    
    def _log_resolution(
        self, 
        item: ContextItem, 
        updates: List[Tuple[str, Any]], 
        resolved_value: Any
    ) -> None:
        """Log a conflict resolution."""
        change = ContextChange(
            change_id=f"change-{uuid.uuid4()}",
            item_id=item.item_id,
            key=item.key,
            old_value=item.value,
            new_value=resolved_value,
            change_type="conflict_resolution",
            timestamp=time.time(),
            agent_id=None,  # System resolution
            metadata={
                "conflicting_agents": [agent_id for agent_id, _ in updates],
                "resolver": self.conflict_resolver.__class__.__name__
            }
        )
        self.change_log.append(change)
        
    def get_changes_since(self, timestamp: float) -> List[ContextChange]:
        """Get all changes since a specific timestamp."""
        return [
            change for change in self.change_log
            if change.timestamp > timestamp
        ]
    
    def set_conflict_resolver(self, resolver: ContextConflictResolver) -> None:
        """Set the conflict resolver."""
        self.conflict_resolver = resolver


class ContextManager:
    """Main interface for context operations."""
    
    def __init__(self, synchronizer: ContextSynchronizer = None):
        self.items: Dict[str, ContextItem] = {}
        self.synchronizer = synchronizer or ContextSynchronizer()
        
    def create_item(
        self,
        key: str,
        value: Any,
        context_type: ContextType,
        scope: ContextScope,
        scope_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new context item.
        
        Args:
            key: The key for the context item
            value: The value of the context item
            context_type: The type of context
            scope: The scope of the context
            scope_id: The ID of the scope (team, agent, task, or session)
            agent_id: The ID of the agent creating the item
            metadata: Additional metadata for the item
            
        Returns:
            The ID of the created item
        """
        item_id = f"ctx-{uuid.uuid4()}"
        
        item = ContextItem(
            item_id=item_id,
            key=key,
            value=value,
            context_type=context_type,
            scope=scope,
            scope_id=scope_id,
            created_by=agent_id,
            metadata=metadata or {}
        )
        
        self.items[item_id] = item
        
        # Log the creation
        self._log_change(
            item_id=item_id,
            key=key,
            old_value=None,
            new_value=value,
            change_type="create",
            agent_id=agent_id
        )
        
        logger.info(f"Created context item {item_id} with key {key}")
        return item_id
    
    def get_item(self, item_id: str) -> Optional[ContextItem]:
        """Get a context item by ID."""
        return self.items.get(item_id)
    
    def get_item_by_key(
        self, 
        key: str, 
        scope: ContextScope, 
        scope_id: Optional[str] = None
    ) -> Optional[ContextItem]:
        """Get a context item by key and scope."""
        for item in self.items.values():
            if (item.key == key and 
                item.scope == scope and 
                item.scope_id == scope_id):
                return item
        return None
    
    def update_item(
        self, 
        item_id: str, 
        value: Any, 
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Update a context item.
        
        Args:
            item_id: The ID of the item to update
            value: The new value
            agent_id: The ID of the agent making the update
            
        Returns:
            True if the update was successful, False otherwise
        """
        if item_id not in self.items:
            logger.warning(f"Attempted to update non-existent context item {item_id}")
            return False
            
        item = self.items[item_id]
        old_value = copy.deepcopy(item.value)
        
        # Record the update for synchronization
        self.synchronizer.record_update(item_id, agent_id or "unknown", value)
        
        # Check for conflicts
        if self.synchronizer.has_conflicts(item_id):
            # Resolve conflicts
            resolved_value = self.synchronizer.resolve_conflicts(item)
            item.update(resolved_value, agent_id)
            logger.info(f"Resolved conflicts for context item {item_id}")
        else:
            # No conflicts, just update
            item.update(value, agent_id)
            logger.info(f"Updated context item {item_id}")
        
        # Log the change
        self._log_change(
            item_id=item_id,
            key=item.key,
            old_value=old_value,
            new_value=item.value,
            change_type="update",
            agent_id=agent_id
        )
        
        return True
    
    def delete_item(self, item_id: str, agent_id: Optional[str] = None) -> bool:
        """
        Delete a context item.
        
        Args:
            item_id: The ID of the item to delete
            agent_id: The ID of the agent making the deletion
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        if item_id not in self.items:
            logger.warning(f"Attempted to delete non-existent context item {item_id}")
            return False
            
        item = self.items[item_id]
        old_value = copy.deepcopy(item.value)
        
        # Log the deletion
        self._log_change(
            item_id=item_id,
            key=item.key,
            old_value=old_value,
            new_value=None,
            change_type="delete",
            agent_id=agent_id
        )
        
        # Delete the item
        del self.items[item_id]
        logger.info(f"Deleted context item {item_id}")
        
        return True
    
    def query_items(
        self,
        context_type: Optional[ContextType] = None,
        scope: Optional[ContextScope] = None,
        scope_id: Optional[str] = None,
        key_prefix: Optional[str] = None,
        created_by: Optional[str] = None,
        created_after: Optional[float] = None,
        updated_after: Optional[float] = None
    ) -> List[ContextItem]:
        """
        Query context items based on various criteria.
        
        Args:
            context_type: Filter by context type
            scope: Filter by scope
            scope_id: Filter by scope ID
            key_prefix: Filter by key prefix
            created_by: Filter by creator agent ID
            created_after: Filter by creation time
            updated_after: Filter by update time
            
        Returns:
            List of matching context items
        """
        results = []
        
        for item in self.items.values():
            # Apply filters
            if context_type and item.context_type != context_type:
                continue
                
            if scope and item.scope != scope:
                continue
                
            if scope_id and item.scope_id != scope_id:
                continue
                
            if key_prefix and not item.key.startswith(key_prefix):
                continue
                
            if created_by and item.created_by != created_by:
                continue
                
            if created_after and item.created_at <= created_after:
                continue
                
            if updated_after and item.updated_at <= updated_after:
                continue
                
            results.append(item)
            
        return results
    
    def get_context_snapshot(
        self,
        scope: ContextScope,
        scope_id: Optional[str] = None,
        context_types: Optional[List[ContextType]] = None
    ) -> Dict[str, Any]:
        """
        Get a snapshot of the context for a specific scope.
        
        Args:
            scope: The scope to get the snapshot for
            scope_id: The ID of the scope
            context_types: Optional list of context types to include
            
        Returns:
            Dictionary mapping keys to values
        """
        snapshot = {}
        
        items = self.query_items(scope=scope, scope_id=scope_id)
        
        for item in items:
            if context_types and item.context_type not in context_types:
                continue
                
            snapshot[item.key] = item.value
            
        return snapshot
    
    def get_changes_since(self, timestamp: float) -> List[ContextChange]:
        """Get all changes since a specific timestamp."""
        return self.synchronizer.get_changes_since(timestamp)
    
    def _log_change(
        self,
        item_id: str,
        key: str,
        old_value: Any,
        new_value: Any,
        change_type: str,
        agent_id: Optional[str]
    ) -> None:
        """Log a change to the context."""
        change = ContextChange(
            change_id=f"change-{uuid.uuid4()}",
            item_id=item_id,
            key=key,
            old_value=old_value,
            new_value=new_value,
            change_type=change_type,
            timestamp=time.time(),
            agent_id=agent_id
        )
        self.synchronizer.change_log.append(change)


class ContextAccessController:
    """Controls access to context items based on permissions."""
    
    def __init__(self):
        self.agent_teams: Dict[str, Set[str]] = {}  # agent_id -> set of team_ids
        
    def register_agent_team(self, agent_id: str, team_id: str) -> None:
        """Register an agent as part of a team."""
        if agent_id not in self.agent_teams:
            self.agent_teams[agent_id] = set()
        self.agent_teams[agent_id].add(team_id)
        
    def unregister_agent_team(self, agent_id: str, team_id: str) -> None:
        """Unregister an agent from a team."""
        if agent_id in self.agent_teams:
            self.agent_teams[agent_id].discard(team_id)
            
    def can_access(
        self, 
        agent_id: str, 
        item: ContextItem
    ) -> bool:
        """
        Check if an agent can access a context item.
        
        Args:
            agent_id: The ID of the agent
            item: The context item
            
        Returns:
            True if the agent can access the item, False otherwise
        """
        # Global scope is accessible to all
        if item.scope == ContextScope.GLOBAL:
            return True
            
        # Agent scope is only accessible to the specific agent
        if item.scope == ContextScope.AGENT:
            return item.scope_id == agent_id
            
        # Team scope is accessible to team members
        if item.scope == ContextScope.TEAM:
            agent_teams = self.agent_teams.get(agent_id, set())
            return item.scope_id in agent_teams
            
        # Task scope is accessible to agents working on the task
        # In a real implementation, this would check task assignments
        if item.scope == ContextScope.TASK:
            # For now, assume all agents can access all tasks
            return True
            
        # Session scope is accessible to agents in the session
        # In a real implementation, this would check session participants
        if item.scope == ContextScope.SESSION:
            # For now, assume all agents can access all sessions
            return True
            
        return False


class CollaborativeContextService:
    """Service for managing collaborative context."""
    
    def __init__(
        self,
        context_manager: ContextManager = None,
        access_controller: ContextAccessController = None
    ):
        self.context_manager = context_manager or ContextManager()
        self.access_controller = access_controller or ContextAccessController()
        
    def create_context(
        self,
        key: str,
        value: Any,
        context_type: ContextType,
        scope: ContextScope,
        scope_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new context item.
        
        Args:
            key: The key for the context item
            value: The value of the context item
            context_type: The type of context
            scope: The scope of the context
            scope_id: The ID of the scope (team, agent, task, or session)
            agent_id: The ID of the agent creating the item
            metadata: Additional metadata for the item
            
        Returns:
            The ID of the created item, or None if creation failed
        """
        # Check if a similar item already exists
        existing_item = self.context_manager.get_item_by_key(key, scope, scope_id)
        if existing_item:
            logger.warning(f"Context item with key {key} already exists in scope {scope}")
            return None
            
        return self.context_manager.create_item(
            key=key,
            value=value,
            context_type=context_type,
            scope=scope,
            scope_id=scope_id,
            agent_id=agent_id,
            metadata=metadata
        )
    
    def get_context(
        self,
        item_id: str,
        agent_id: str
    ) -> Optional[Any]:
        """
        Get a context item value.
        
        Args:
            item_id: The ID of the item to get
            agent_id: The ID of the agent making the request
            
        Returns:
            The value of the context item, or None if not found or not accessible
        """
        item = self.context_manager.get_item(item_id)
        if not item:
            logger.warning(f"Context item {item_id} not found")
            return None
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to context item {item_id}")
            return None
            
        return item.value
    
    def update_context(
        self,
        item_id: str,
        value: Any,
        agent_id: str
    ) -> bool:
        """
        Update a context item.
        
        Args:
            item_id: The ID of the item to update
            value: The new value
            agent_id: The ID of the agent making the update
            
        Returns:
            True if the update was successful, False otherwise
        """
        item = self.context_manager.get_item(item_id)
        if not item:
            logger.warning(f"Context item {item_id} not found")
            return False
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to context item {item_id}")
            return False
            
        return self.context_manager.update_item(item_id, value, agent_id)
    
    def delete_context(
        self,
        item_id: str,
        agent_id: str
    ) -> bool:
        """
        Delete a context item.
        
        Args:
            item_id: The ID of the item to delete
            agent_id: The ID of the agent making the deletion
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        item = self.context_manager.get_item(item_id)
        if not item:
            logger.warning(f"Context item {item_id} not found")
            return False
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to context item {item_id}")
            return False
            
        return self.context_manager.delete_item(item_id, agent_id)
    
    def get_agent_context(
        self,
        agent_id: str,
        context_types: Optional[List[ContextType]] = None
    ) -> Dict[str, Any]:
        """
        Get all context accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            context_types: Optional list of context types to include
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        
        # Get global context
        global_context = self.context_manager.get_context_snapshot(
            scope=ContextScope.GLOBAL,
            context_types=context_types
        )
        result.update(global_context)
        
        # Get agent-specific context
        agent_context = self.context_manager.get_context_snapshot(
            scope=ContextScope.AGENT,
            scope_id=agent_id,
            context_types=context_types
        )
        result.update(agent_context)
        
        # Get team context for all teams the agent is part of
        agent_teams = self.access_controller.agent_teams.get(agent_id, set())
        for team_id in agent_teams:
            team_context = self.context_manager.get_context_snapshot(
                scope=ContextScope.TEAM,
                scope_id=team_id,
                context_types=context_types
            )
            result.update(team_context)
            
        # In a real implementation, would also get task and session context
        
        return result
    
    def get_team_context(
        self,
        team_id: str,
        context_types: Optional[List[ContextType]] = None
    ) -> Dict[str, Any]:
        """
        Get all context for a team.
        
        Args:
            team_id: The ID of the team
            context_types: Optional list of context types to include
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        
        # Get global context
        global_context = self.context_manager.get_context_snapshot(
            scope=ContextScope.GLOBAL,
            context_types=context_types
        )
        result.update(global_context)
        
        # Get team-specific context
        team_context = self.context_manager.get_context_snapshot(
            scope=ContextScope.TEAM,
            scope_id=team_id,
            context_types=context_types
        )
        result.update(team_context)
        
        return result
    
    def register_agent_team(self, agent_id: str, team_id: str) -> None:
        """Register an agent as part of a team."""
        self.access_controller.register_agent_team(agent_id, team_id)
        
    def unregister_agent_team(self, agent_id: str, team_id: str) -> None:
        """Unregister an agent from a team."""
        self.access_controller.unregister_agent_team(agent_id, team_id)
    
    def get_context_history(
        self,
        item_id: str,
        agent_id: str
    ) -> Optional[List[ContextChange]]:
        """
        Get the history of changes for a context item.
        
        Args:
            item_id: The ID of the item
            agent_id: The ID of the agent making the request
            
        Returns:
            List of changes, or None if not found or not accessible
        """
        item = self.context_manager.get_item(item_id)
        if not item:
            logger.warning(f"Context item {item_id} not found")
            return None
            
        if not self.access_controller.can_access(agent_id, item):
            logger.warning(f"Agent {agent_id} does not have access to context item {item_id}")
            return None
            
        # Get all changes for this item
        all_changes = self.context_manager.synchronizer.change_log
        item_changes = [
            change for change in all_changes
            if change.item_id == item_id
        ]
        
        return item_changes
    
    def get_context_updates(
        self,
        agent_id: str,
        since_timestamp: float
    ) -> List[ContextChange]:
        """
        Get all context updates since a specific timestamp that are accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            since_timestamp: The timestamp to get updates since
            
        Returns:
            List of context changes
        """
        all_changes = self.context_manager.get_changes_since(since_timestamp)
        
        # Filter changes to only include those the agent can access
        accessible_changes = []
        for change in all_changes:
            item = self.context_manager.get_item(change.item_id)
            if item and self.access_controller.can_access(agent_id, item):
                accessible_changes.append(change)
            elif not item and change.change_type == "delete":
                # For deleted items, we need to check if the agent could access it before deletion
                # This would require keeping a history of deleted items and their access rules
                # For simplicity, we'll include all deletion changes for now
                accessible_changes.append(change)
                
        return accessible_changes
