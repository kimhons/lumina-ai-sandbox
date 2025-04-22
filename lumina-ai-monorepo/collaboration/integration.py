"""
Integration module for Advanced Multi-Agent Collaboration.

This module integrates all collaboration components together and connects them
with the existing Lumina AI system.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
import uuid
import time
import json
import logging
import threading
from dataclasses import dataclass, field
from enum import Enum

from collaboration.team_formation import (
    AgentCapability, AgentProfile, TaskRequirement, AgentTeam,
    AgentCapabilityRegistry, TeamPerformanceMonitor, TeamFormationManager
)
from collaboration.context_manager import (
    ContextScope, ContextType, ContextItem, CollaborativeContextService
)
from collaboration.negotiation import (
    NegotiationType, TaskDetails, NegotiationService
)
from collaboration.shared_memory import (
    MemoryScope, MemoryType, SharedMemoryService
)
from collaboration.learning import (
    LearningEventType, CollaborativeLearningService
)

# Import existing Lumina AI components
from lumina.common.interfaces import Provider, ProviderCapability
from lumina.providers.base import BaseProvider
from lumina.providers.selector import ProviderSelector

logger = logging.getLogger(__name__)

class CollaborationManager:
    """Main manager for multi-agent collaboration."""
    
    def __init__(
        self,
        team_formation_manager: Optional[TeamFormationManager] = None,
        context_service: Optional[CollaborativeContextService] = None,
        negotiation_service: Optional[NegotiationService] = None,
        memory_service: Optional[SharedMemoryService] = None,
        learning_service: Optional[CollaborativeLearningService] = None
    ):
        # Initialize collaboration components
        self.capability_registry = AgentCapabilityRegistry()
        self.performance_monitor = TeamPerformanceMonitor()
        self.team_formation_manager = team_formation_manager or TeamFormationManager(
            self.capability_registry, self.performance_monitor
        )
        self.context_service = context_service or CollaborativeContextService()
        self.negotiation_service = negotiation_service or NegotiationService()
        self.memory_service = memory_service or SharedMemoryService()
        self.learning_service = learning_service or CollaborativeLearningService()
        
        # Track active teams and tasks
        self.active_teams: Dict[str, AgentTeam] = {}
        self.active_tasks: Dict[str, TaskRequirement] = {}
        
        # Synchronization
        self.lock = threading.RLock()
    
    def register_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: Dict[str, float],
        specializations: List[str] = None
    ) -> bool:
        """
        Register an agent with the collaboration system.
        
        Args:
            agent_id: The ID of the agent
            name: The name of the agent
            capabilities: Dict mapping capability names to proficiency scores (0.0 to 1.0)
            specializations: Optional list of domain specializations
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self.lock:
            # Convert string capabilities to AgentCapability enum
            enum_capabilities = {}
            for cap_name, score in capabilities.items():
                try:
                    cap_enum = AgentCapability(cap_name)
                    enum_capabilities[cap_enum] = score
                except ValueError:
                    logger.warning(f"Unknown capability: {cap_name}")
            
            # Create agent profile
            profile = AgentProfile(
                agent_id=agent_id,
                name=name,
                capabilities=enum_capabilities,
                specializations=specializations or []
            )
            
            # Register with capability registry
            self.capability_registry.register_agent(profile)
            
            # Initialize agent memory
            self.memory_service.create_memory(
                key=f"agent_profile_{agent_id}",
                value={
                    "agent_id": agent_id,
                    "name": name,
                    "capabilities": {k.value: v for k, v in enum_capabilities.items()},
                    "specializations": specializations or []
                },
                memory_type=MemoryType.FACTUAL,
                scope=MemoryScope.AGENT,
                scope_id=agent_id,
                agent_id=agent_id,
                importance=0.8
            )
            
            # Record learning event
            self.learning_service.record_event(
                event_type=LearningEventType.KNOWLEDGE,
                agent_id=agent_id,
                content={
                    "type": "agent_registration",
                    "name": name,
                    "capabilities": {k.value: v for k, v in enum_capabilities.items()},
                    "specializations": specializations or []
                }
            )
            
            logger.info(f"Registered agent {name} with ID {agent_id}")
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the collaboration system.
        
        Args:
            agent_id: The ID of the agent to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self.lock:
            # Unregister from capability registry
            result = self.capability_registry.unregister_agent(agent_id)
            
            if result:
                # Remove from all teams
                for team_id, team in list(self.active_teams.items()):
                    if agent_id in team.members:
                        team.remove_member(agent_id)
                        
                        # If team is now empty, remove it
                        if team.get_size() == 0:
                            del self.active_teams[team_id]
                
                # Record learning event
                self.learning_service.record_event(
                    event_type=LearningEventType.KNOWLEDGE,
                    agent_id=agent_id,
                    content={
                        "type": "agent_unregistration"
                    }
                )
                
                logger.info(f"Unregistered agent with ID {agent_id}")
            
            return result
    
    def create_task(
        self,
        name: str,
        description: str,
        required_capabilities: Dict[str, float],
        domain_specializations: List[str] = None,
        priority: int = 5,
        estimated_duration: float = 1.0,
        complexity: int = 5,
        min_team_size: int = 1,
        max_team_size: int = 5
    ) -> str:
        """
        Create a new task.
        
        Args:
            name: The name of the task
            description: The description of the task
            required_capabilities: Dict mapping capability names to minimum proficiency scores
            domain_specializations: Optional list of domain specializations
            priority: Task priority (1 to 10)
            estimated_duration: Estimated duration in hours
            complexity: Task complexity (1 to 10)
            min_team_size: Minimum team size
            max_team_size: Maximum team size
            
        Returns:
            The ID of the created task
        """
        with self.lock:
            task_id = f"task-{uuid.uuid4()}"
            
            # Convert string capabilities to AgentCapability enum
            enum_capabilities = {}
            for cap_name, score in required_capabilities.items():
                try:
                    cap_enum = AgentCapability(cap_name)
                    enum_capabilities[cap_enum] = score
                except ValueError:
                    logger.warning(f"Unknown capability: {cap_name}")
            
            # Create task requirement
            task = TaskRequirement(
                task_id=task_id,
                name=name,
                description=description,
                required_capabilities=enum_capabilities,
                domain_specializations=domain_specializations or [],
                priority=priority,
                estimated_duration=estimated_duration,
                complexity=complexity,
                min_team_size=min_team_size,
                max_team_size=max_team_size
            )
            
            # Store task
            self.active_tasks[task_id] = task
            
            # Create task memory
            self.memory_service.create_memory(
                key=f"task_definition_{task_id}",
                value={
                    "task_id": task_id,
                    "name": name,
                    "description": description,
                    "required_capabilities": {k.value: v for k, v in enum_capabilities.items()},
                    "domain_specializations": domain_specializations or [],
                    "priority": priority,
                    "estimated_duration": estimated_duration,
                    "complexity": complexity
                },
                memory_type=MemoryType.FACTUAL,
                scope=MemoryScope.TASK,
                scope_id=task_id,
                importance=0.9
            )
            
            logger.info(f"Created task {name} with ID {task_id}")
            return task_id
    
    def form_team(
        self,
        task_id: str,
        strategy_name: str = "optimal_coverage"
    ) -> Optional[str]:
        """
        Form a team for a task.
        
        Args:
            task_id: The ID of the task
            strategy_name: The name of the team formation strategy to use
            
        Returns:
            The ID of the formed team, or None if team formation failed
        """
        with self.lock:
            if task_id not in self.active_tasks:
                logger.warning(f"Task {task_id} not found")
                return None
                
            task = self.active_tasks[task_id]
            
            # Form team
            team = self.team_formation_manager.create_team(task, strategy_name)
            if not team:
                logger.warning(f"Failed to form team for task {task_id}")
                return None
                
            # Store team
            self.active_teams[team.team_id] = team
            
            # Register team members with memory service
            for agent_id in team.members:
                self.memory_service.register_agent_task(agent_id, task_id)
                self.memory_service.register_agent_team(agent_id, team.team_id)
            
            # Create team context
            self.context_service.create_context(
                key=f"team_formation_{team.team_id}",
                value={
                    "team_id": team.team_id,
                    "task_id": task_id,
                    "members": list(team.members.keys()),
                    "roles": {agent_id: [role.value for role in roles] for agent_id, roles in team.roles.items()},
                    "formation_time": team.formation_time
                },
                context_type=ContextType.SYSTEM_STATE,
                scope=ContextScope.TEAM,
                scope_id=team.team_id
            )
            
            # Create team memory
            self.memory_service.create_memory(
                key=f"team_formation_{team.team_id}",
                value={
                    "team_id": team.team_id,
                    "task_id": task_id,
                    "members": list(team.members.keys()),
                    "roles": {agent_id: [role.value for role in roles] for agent_id, roles in team.roles.items()},
                    "formation_time": team.formation_time
                },
                memory_type=MemoryType.FACTUAL,
                scope=MemoryScope.TEAM,
                scope_id=team.team_id,
                importance=0.8
            )
            
            # Record learning event
            self.learning_service.record_event(
                event_type=LearningEventType.KNOWLEDGE,
                agent_id="system",
                content={
                    "type": "team_formation",
                    "team_id": team.team_id,
                    "task_id": task_id,
                    "members": list(team.members.keys()),
                    "strategy": strategy_name
                },
                team_id=team.team_id,
                task_id=task_id
            )
            
            logger.info(f"Formed team {team.team_id} for task {task_id} with {team.get_size()} members")
            return team.team_id
    
    def disband_team(self, team_id: str) -> bool:
        """
        Disband a team.
        
        Args:
            team_id: The ID of the team to disband
            
        Returns:
            True if disbanding was successful, False otherwise
        """
        with self.lock:
            if team_id not in self.active_teams:
                logger.warning(f"Team {team_id} not found")
                return False
                
            team = self.active_teams[team_id]
            
            # Unregister team members from memory service
            for agent_id in team.members:
                self.memory_service.unregister_agent_team(agent_id, team_id)
                if team.task_id:
                    self.memory_service.unregister_agent_task(agent_id, team.task_id)
            
            # Disband team
            result = self.team_formation_manager.disband_team(team_id)
            
            if result:
                # Remove from active teams
                del self.active_teams[team_id]
                
                # Record learning event
                self.learning_service.record_event(
                    event_type=LearningEventType.KNOWLEDGE,
                    agent_id="system",
                    content={
                        "type": "team_disbanding",
                        "team_id": team_id,
                        "task_id": team.task_id
                    },
                    team_id=team_id,
                    task_id=team.task_id
                )
                
                logger.info(f"Disbanded team {team_id}")
            
            return result
    
    def initiate_task_negotiation(
        self,
        team_id: str,
        initiator_id: str
    ) -> Optional[str]:
        """
        Initiate a task allocation negotiation within a team.
        
        Args:
            team_id: The ID of the team
            initiator_id: The ID of the initiating agent
            
        Returns:
            The ID of the created negotiation, or None if initiation failed
        """
        with self.lock:
            if team_id not in self.active_teams:
                logger.warning(f"Team {team_id} not found")
                return None
                
            team = self.active_teams[team_id]
            
            if initiator_id not in team.members:
                logger.warning(f"Agent {initiator_id} is not a member of team {team_id}")
                return None
                
            if not team.task_id or team.task_id not in self.active_tasks:
                logger.warning(f"Team {team_id} has no valid task")
                return None
                
            task = self.active_tasks[team.task_id]
            
            # Convert task to TaskDetails for negotiation
            task_details = TaskDetails(
                task_id=task.task_id,
                name=task.name,
                description=task.description,
                estimated_duration=task.estimated_duration,
                complexity=task.complexity,
                priority=task.priority,
                dependencies=[],
                required_resources={}
            )
            
            # Initiate negotiation
            negotiation_id = self.negotiation_service.initiate_task_allocation_negotiation(
                initiator_id=initiator_id,
                participants=list(team.members.keys()),
                tasks=[task_details],
                deadline=time.time() + 300  # 5 minutes
            )
            
            if negotiation_id:
                # Create negotiation context
                self.context_service.create_context(
                    key=f"negotiation_{negotiation_id}",
                    value={
                        "negotiation_id": negotiation_id,
                        "type": "task_allocation",
                        "team_id": team_id,
                        "task_id": task.task_id,
                        "initiator_id": initiator_id,
                        "participants": list(team.members.keys()),
                        "start_time": time.time()
                    },
                    context_type=ContextType.SYSTEM_STATE,
                    scope=ContextScope.TEAM,
                    scope_id=team_id
                )
                
                # Record learning event
                self.learning_service.record_event(
                    event_type=LearningEventType.INTERACTION,
                    agent_id=initiator_id,
                    content={
                        "type": "negotiation_initiation",
                        "negotiation_id": negotiation_id,
                        "negotiation_type": "task_allocation",
                        "team_id": team_id,
                        "task_id": task.task_id
                    },
                    team_id=team_id,
                    task_id=task.task_id
                )
                
                logger.info(f"Initiated task allocation negotiation {negotiation_id} for team {team_id}")
            
            return negotiation_id
    
    def share_context(
        self,
        key: str,
        value: Any,
        context_type: str,
        scope: str,
        scope_id: Optional[str],
        agent_id: str
    ) -> Optional[str]:
        """
        Share context with other agents.
        
        Args:
            key: The key for the context item
            value: The value of the context item
            context_type: The type of context (as string)
            scope: The scope of the context (as string)
            scope_id: The ID of the scope
            agent_id: The ID of the agent sharing the context
            
        Returns:
            The ID of the created context item, or None if sharing failed
        """
        try:
            # Convert string enums to actual enums
            ctx_type = ContextType(context_type)
            ctx_scope = ContextScope(scope)
            
            # Create context
            context_id = self.context_service.create_context(
                key=key,
                value=value,
                context_type=ctx_type,
                scope=ctx_scope,
                scope_id=scope_id,
                agent_id=agent_id
            )
            
            if context_id:
                # Record learning event
                self.learning_service.record_event(
                    event_type=LearningEventType.KNOWLEDGE,
                    agent_id=agent_id,
                    content={
                        "type": "context_sharing",
                        "context_id": context_id,
                        "key": key,
                        "context_type": context_type,
                        "scope": scope,
                        "scope_id": scope_id
                    },
                    team_id=scope_id if ctx_scope == ContextScope.TEAM else None,
                    task_id=scope_id if ctx_scope == ContextScope.TASK else None
                )
                
                logger.info(f"Agent {agent_id} shared context {key} with scope {scope}")
            
            return context_id
        except ValueError:
            logger.warning(f"Invalid context type or scope: {context_type}, {scope}")
            return None
    
    def store_memory(
        self,
        key: str,
        value: Any,
        memory_type: str,
        scope: str,
        scope_id: Optional[str],
        agent_id: str,
        importance: float = 0.5,
        tags: List[str] = None
    ) -> Optional[str]:
        """
        Store memory that can be accessed by other agents.
        
        Args:
            key: The key for the memory item
            value: The value of the memory item
            memory_type: The type of memory (as string)
            scope: The scope of the memory (as string)
            scope_id: The ID of the scope
            agent_id: The ID of the agent storing the memory
            importance: Importance score (0.0 to 1.0)
            tags: Optional list of tags
            
        Returns:
            The ID of the created memory item, or None if storing failed
        """
        try:
            # Convert string enums to actual enums
            mem_type = MemoryType(memory_type)
            mem_scope = MemoryScope(scope)
            
            # Create memory
            memory_id = self.memory_service.create_memory(
                key=key,
                value=value,
                memory_type=mem_type,
                scope=mem_scope,
                scope_id=scope_id,
                agent_id=agent_id,
                importance=importance,
                tags=tags or []
            )
            
            if memory_id:
                # Record learning event
                self.learning_service.record_event(
                    event_type=LearningEventType.KNOWLEDGE,
                    agent_id=agent_id,
                    content={
                        "type": "memory_storage",
                        "memory_id": memory_id,
                        "key": key,
                        "memory_type": memory_type,
                        "scope": scope,
                        "scope_id": scope_id,
                        "importance": importance
                    },
                    team_id=scope_id if mem_scope == MemoryScope.TEAM else None,
                    task_id=scope_id if mem_scope == MemoryScope.TASK else None
                )
                
                logger.info(f"Agent {agent_id} stored memory {key} with scope {scope}")
            
            return memory_id
        except ValueError:
            logger.warning(f"Invalid memory type or scope: {memory_type}, {scope}")
            return None
    
    def record_learning_event(
        self,
        event_type: str,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: List[str] = None
    ) -> Optional[str]:
        """
        Record a learning event.
        
        Args:
            event_type: The type of event (as string)
            agent_id: The ID of the agent
            content: The event content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            
        Returns:
            The ID of the created event, or None if recording failed
        """
        try:
            # Convert string enum to actual enum
            learn_type = LearningEventType(event_type)
            
            # Record event
            event_id = self.learning_service.record_event(
                event_type=learn_type,
                agent_id=agent_id,
                content=content,
                task_id=task_id,
                team_id=team_id,
                related_events=related_events or []
            )
            
            if event_id:
                logger.info(f"Recorded learning event {event_type} for agent {agent_id}")
            
            return event_id
        except ValueError:
            logger.warning(f"Invalid learning event type: {event_type}")
            return None
    
    def get_agent_context(
        self,
        agent_id: str,
        context_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get all context accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            context_types: Optional list of context types to include (as strings)
            
        Returns:
            Dictionary mapping keys to values
        """
        # Convert string enums to actual enums if provided
        enum_types = None
        if context_types:
            enum_types = []
            for type_str in context_types:
                try:
                    enum_types.append(ContextType(type_str))
                except ValueError:
                    logger.warning(f"Invalid context type: {type_str}")
        
        # Get agent context
        return self.context_service.get_agent_context(
            agent_id=agent_id,
            context_types=enum_types
        )
    
    def get_agent_memory(
        self,
        agent_id: str,
        memory_types: List[str] = None,
        min_importance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get all memory accessible to an agent.
        
        Args:
            agent_id: The ID of the agent
            memory_types: Optional list of memory types to include (as strings)
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        # Convert string enums to actual enums if provided
        enum_types = None
        if memory_types:
            enum_types = []
            for type_str in memory_types:
                try:
                    enum_types.append(MemoryType(type_str))
                except ValueError:
                    logger.warning(f"Invalid memory type: {type_str}")
        
        # Get agent memory
        return self.memory_service.get_agent_memory(
            agent_id=agent_id,
            memory_types=enum_types,
            min_importance=min_importance
        )
    
    def get_agent_learning_history(
        self,
        agent_id: str,
        limit: int = 100,
        event_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get learning history for an agent.
        
        Args:
            agent_id: The ID of the agent
            limit: Maximum number of events to return
            event_types: Optional list of event types to include (as strings)
            
        Returns:
            List of dictionaries with event information
        """
        # Convert string enums to actual enums if provided
        enum_types = None
        if event_types:
            enum_types = []
            for type_str in event_types:
                try:
                    enum_types.append(LearningEventType(type_str))
                except ValueError:
                    logger.warning(f"Invalid learning event type: {type_str}")
        
        # Get agent history
        return self.learning_service.get_agent_history(
            agent_id=agent_id,
            limit=limit,
            event_types=enum_types
        )
    
    def get_team_info(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a team.
        
        Args:
            team_id: The ID of the team
            
        Returns:
            Dictionary with team information, or None if team not found
        """
        with self.lock:
            if team_id not in self.active_teams:
                logger.warning(f"Team {team_id} not found")
                return None
                
            team = self.active_teams[team_id]
            
            return {
                "team_id": team.team_id,
                "task_id": team.task_id,
                "members": list(team.members.keys()),
                "roles": {agent_id: [role.value for role in roles] for agent_id, roles in team.roles.items()},
                "formation_time": team.formation_time,
                "status": team.status,
                "performance_score": team.performance_score
            }
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Dictionary with task information, or None if task not found
        """
        with self.lock:
            if task_id not in self.active_tasks:
                logger.warning(f"Task {task_id} not found")
                return None
                
            task = self.active_tasks[task_id]
            
            return {
                "task_id": task.task_id,
                "name": task.name,
                "description": task.description,
                "required_capabilities": {cap.value: score for cap, score in task.required_capabilities.items()},
                "domain_specializations": task.domain_specializations,
                "priority": task.priority,
                "estimated_duration": task.estimated_duration,
                "complexity": task.complexity,
                "min_team_size": task.min_team_size,
                "max_team_size": task.max_team_size
            }
    
    def get_negotiation_status(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation
            
        Returns:
            Dictionary with negotiation status information, or None if not found
        """
        return self.negotiation_service.get_negotiation_status(negotiation_id)
    
    def get_insights(
        self,
        tags: List[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get insights based on various criteria.
        
        Args:
            tags: Optional list of tags to filter by
            min_confidence: Minimum confidence threshold
            limit: Maximum number of insights to return
            
        Returns:
            List of dictionaries with insight information
        """
        return self.learning_service.get_insights(
            tags=tags,
            min_confidence=min_confidence,
            limit=limit
        )


class CollaborativeAgent:
    """Agent that can participate in multi-agent collaboration."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: Dict[str, float],
        specializations: List[str],
        collaboration_manager: CollaborationManager,
        provider: Optional[Provider] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.specializations = specializations
        self.collaboration_manager = collaboration_manager
        self.provider = provider
        
        # Register with collaboration manager
        self.collaboration_manager.register_agent(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            specializations=specializations
        )
        
        # Track teams and tasks
        self.teams: Set[str] = set()
        self.tasks: Set[str] = set()
        
        logger.info(f"Created collaborative agent {name} with ID {agent_id}")
    
    def join_team(self, team_id: str) -> bool:
        """
        Join a team.
        
        Args:
            team_id: The ID of the team to join
            
        Returns:
            True if joining was successful, False otherwise
        """
        team_info = self.collaboration_manager.get_team_info(team_id)
        if not team_info:
            logger.warning(f"Team {team_id} not found")
            return False
            
        if self.agent_id in team_info["members"]:
            # Already a member
            self.teams.add(team_id)
            if team_info["task_id"]:
                self.tasks.add(team_info["task_id"])
            return True
            
        # TODO: Implement proper team joining logic
        logger.warning(f"Direct team joining not implemented")
        return False
    
    def leave_team(self, team_id: str) -> bool:
        """
        Leave a team.
        
        Args:
            team_id: The ID of the team to leave
            
        Returns:
            True if leaving was successful, False otherwise
        """
        team_info = self.collaboration_manager.get_team_info(team_id)
        if not team_info:
            logger.warning(f"Team {team_id} not found")
            return False
            
        if self.agent_id not in team_info["members"]:
            # Not a member
            return True
            
        # TODO: Implement proper team leaving logic
        logger.warning(f"Direct team leaving not implemented")
        return False
    
    def share_context(
        self,
        key: str,
        value: Any,
        context_type: str,
        scope: str,
        scope_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Share context with other agents.
        
        Args:
            key: The key for the context item
            value: The value of the context item
            context_type: The type of context (as string)
            scope: The scope of the context (as string)
            scope_id: The ID of the scope
            
        Returns:
            The ID of the created context item, or None if sharing failed
        """
        return self.collaboration_manager.share_context(
            key=key,
            value=value,
            context_type=context_type,
            scope=scope,
            scope_id=scope_id,
            agent_id=self.agent_id
        )
    
    def store_memory(
        self,
        key: str,
        value: Any,
        memory_type: str,
        scope: str,
        scope_id: Optional[str] = None,
        importance: float = 0.5,
        tags: List[str] = None
    ) -> Optional[str]:
        """
        Store memory that can be accessed by other agents.
        
        Args:
            key: The key for the memory item
            value: The value of the memory item
            memory_type: The type of memory (as string)
            scope: The scope of the memory (as string)
            scope_id: The ID of the scope
            importance: Importance score (0.0 to 1.0)
            tags: Optional list of tags
            
        Returns:
            The ID of the created memory item, or None if storing failed
        """
        return self.collaboration_manager.store_memory(
            key=key,
            value=value,
            memory_type=memory_type,
            scope=scope,
            scope_id=scope_id,
            agent_id=self.agent_id,
            importance=importance,
            tags=tags
        )
    
    def record_observation(
        self,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: List[str] = None
    ) -> Optional[str]:
        """
        Record an observation.
        
        Args:
            content: The observation content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            
        Returns:
            The ID of the created event, or None if recording failed
        """
        return self.collaboration_manager.record_learning_event(
            event_type="observation",
            agent_id=self.agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events
        )
    
    def record_action(
        self,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: List[str] = None
    ) -> Optional[str]:
        """
        Record an action.
        
        Args:
            content: The action content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            
        Returns:
            The ID of the created event, or None if recording failed
        """
        return self.collaboration_manager.record_learning_event(
            event_type="action",
            agent_id=self.agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events
        )
    
    def record_insight(
        self,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: List[str] = None
    ) -> Optional[str]:
        """
        Record an insight.
        
        Args:
            content: The insight content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            
        Returns:
            The ID of the created event, or None if recording failed
        """
        return self.collaboration_manager.record_learning_event(
            event_type="insight",
            agent_id=self.agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events
        )
    
    def get_context(
        self,
        context_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get all context accessible to this agent.
        
        Args:
            context_types: Optional list of context types to include (as strings)
            
        Returns:
            Dictionary mapping keys to values
        """
        return self.collaboration_manager.get_agent_context(
            agent_id=self.agent_id,
            context_types=context_types
        )
    
    def get_memory(
        self,
        memory_types: List[str] = None,
        min_importance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get all memory accessible to this agent.
        
        Args:
            memory_types: Optional list of memory types to include (as strings)
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        return self.collaboration_manager.get_agent_memory(
            agent_id=self.agent_id,
            memory_types=memory_types,
            min_importance=min_importance
        )
    
    def get_learning_history(
        self,
        limit: int = 100,
        event_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get learning history for this agent.
        
        Args:
            limit: Maximum number of events to return
            event_types: Optional list of event types to include (as strings)
            
        Returns:
            List of dictionaries with event information
        """
        return self.collaboration_manager.get_agent_learning_history(
            agent_id=self.agent_id,
            limit=limit,
            event_types=event_types
        )
    
    def initiate_task_negotiation(self, team_id: str) -> Optional[str]:
        """
        Initiate a task allocation negotiation within a team.
        
        Args:
            team_id: The ID of the team
            
        Returns:
            The ID of the created negotiation, or None if initiation failed
        """
        if team_id not in self.teams:
            logger.warning(f"Agent {self.agent_id} is not a member of team {team_id}")
            return None
            
        return self.collaboration_manager.initiate_task_negotiation(
            team_id=team_id,
            initiator_id=self.agent_id
        )
    
    def propose_task_allocation(
        self,
        negotiation_id: str,
        allocation: Dict[str, List[str]]
    ) -> Optional[str]:
        """
        Propose a task allocation in a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation
            allocation: Dict mapping agent IDs to lists of task IDs
            
        Returns:
            The ID of the created proposal, or None if submission failed
        """
        return self.collaboration_manager.negotiation_service.propose_task_allocation(
            negotiation_id=negotiation_id,
            proposer_id=self.agent_id,
            allocation=allocation
        )
    
    def respond_to_proposal(
        self,
        negotiation_id: str,
        proposal_id: str,
        response: str  # "accept", "reject", "counter"
    ) -> bool:
        """
        Respond to a proposal.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposal_id: The ID of the proposal
            response: The response ("accept", "reject", "counter")
            
        Returns:
            True if the response was recorded, False otherwise
        """
        return self.collaboration_manager.negotiation_service.respond_to_proposal(
            negotiation_id=negotiation_id,
            proposal_id=proposal_id,
            agent_id=self.agent_id,
            response=response
        )


class CollaborativeProviderAdapter:
    """Adapter for integrating Lumina AI providers with the collaboration system."""
    
    def __init__(
        self,
        collaboration_manager: CollaborationManager,
        provider_selector: ProviderSelector
    ):
        self.collaboration_manager = collaboration_manager
        self.provider_selector = provider_selector
        self.collaborative_agents: Dict[str, CollaborativeAgent] = {}
        
        # Register providers as collaborative agents
        self._register_providers()
        
        logger.info(f"Initialized collaborative provider adapter with {len(self.collaborative_agents)} agents")
    
    def _register_providers(self) -> None:
        """Register all providers as collaborative agents."""
        providers = self.provider_selector.get_all_providers()
        
        for provider in providers:
            # Map provider capabilities to agent capabilities
            capabilities = {}
            for cap in provider.get_capabilities():
                if cap == ProviderCapability.TEXT_GENERATION:
                    capabilities["reasoning"] = 0.9
                    capabilities["creative_writing"] = 0.8
                elif cap == ProviderCapability.CODE_GENERATION:
                    capabilities["code_generation"] = 0.9
                elif cap == ProviderCapability.FUNCTION_CALLING:
                    capabilities["planning"] = 0.8
                elif cap == ProviderCapability.IMAGE_GENERATION:
                    capabilities["creative_writing"] = 0.7
                elif cap == ProviderCapability.EMBEDDING:
                    capabilities["research"] = 0.7
            
            # Create collaborative agent
            agent_id = f"provider-{provider.get_id()}"
            agent = CollaborativeAgent(
                agent_id=agent_id,
                name=provider.get_name(),
                capabilities=capabilities,
                specializations=[],
                collaboration_manager=self.collaboration_manager,
                provider=provider
            )
            
            self.collaborative_agents[agent_id] = agent
    
    def create_task_team(
        self,
        task_name: str,
        task_description: str,
        required_capabilities: Dict[str, float],
        min_team_size: int = 2,
        max_team_size: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Create a task and form a team of providers to handle it.
        
        Args:
            task_name: The name of the task
            task_description: The description of the task
            required_capabilities: Dict mapping capability names to minimum proficiency scores
            min_team_size: Minimum team size
            max_team_size: Maximum team size
            
        Returns:
            Dictionary with task and team information, or None if creation failed
        """
        # Create task
        task_id = self.collaboration_manager.create_task(
            name=task_name,
            description=task_description,
            required_capabilities=required_capabilities,
            min_team_size=min_team_size,
            max_team_size=max_team_size
        )
        
        if not task_id:
            logger.warning(f"Failed to create task {task_name}")
            return None
            
        # Form team
        team_id = self.collaboration_manager.form_team(task_id)
        
        if not team_id:
            logger.warning(f"Failed to form team for task {task_id}")
            return None
            
        # Get team and task info
        team_info = self.collaboration_manager.get_team_info(team_id)
        task_info = self.collaboration_manager.get_task_info(task_id)
        
        # Update agent team memberships
        for agent_id in team_info["members"]:
            if agent_id in self.collaborative_agents:
                self.collaborative_agents[agent_id].teams.add(team_id)
                self.collaborative_agents[agent_id].tasks.add(task_id)
        
        return {
            "task": task_info,
            "team": team_info
        }
    
    def get_provider_agent(self, provider_id: str) -> Optional[CollaborativeAgent]:
        """
        Get the collaborative agent for a provider.
        
        Args:
            provider_id: The ID of the provider
            
        Returns:
            The collaborative agent, or None if not found
        """
        agent_id = f"provider-{provider_id}"
        return self.collaborative_agents.get(agent_id)
    
    def get_team_providers(self, team_id: str) -> List[Provider]:
        """
        Get all providers in a team.
        
        Args:
            team_id: The ID of the team
            
        Returns:
            List of providers
        """
        team_info = self.collaboration_manager.get_team_info(team_id)
        if not team_info:
            logger.warning(f"Team {team_id} not found")
            return []
            
        providers = []
        for agent_id in team_info["members"]:
            agent = self.collaborative_agents.get(agent_id)
            if agent and agent.provider:
                providers.append(agent.provider)
                
        return providers
    
    def share_provider_context(
        self,
        provider_id: str,
        key: str,
        value: Any,
        context_type: str,
        scope: str,
        scope_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Share context from a provider.
        
        Args:
            provider_id: The ID of the provider
            key: The key for the context item
            value: The value of the context item
            context_type: The type of context (as string)
            scope: The scope of the context (as string)
            scope_id: The ID of the scope
            
        Returns:
            The ID of the created context item, or None if sharing failed
        """
        agent = self.get_provider_agent(provider_id)
        if not agent:
            logger.warning(f"Provider agent {provider_id} not found")
            return None
            
        return agent.share_context(
            key=key,
            value=value,
            context_type=context_type,
            scope=scope,
            scope_id=scope_id
        )
    
    def get_provider_context(
        self,
        provider_id: str,
        context_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get all context accessible to a provider.
        
        Args:
            provider_id: The ID of the provider
            context_types: Optional list of context types to include (as strings)
            
        Returns:
            Dictionary mapping keys to values
        """
        agent = self.get_provider_agent(provider_id)
        if not agent:
            logger.warning(f"Provider agent {provider_id} not found")
            return {}
            
        return agent.get_context(context_types=context_types)
    
    def get_provider_memory(
        self,
        provider_id: str,
        memory_types: List[str] = None,
        min_importance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get all memory accessible to a provider.
        
        Args:
            provider_id: The ID of the provider
            memory_types: Optional list of memory types to include (as strings)
            min_importance: Optional minimum importance threshold
            
        Returns:
            Dictionary mapping keys to values
        """
        agent = self.get_provider_agent(provider_id)
        if not agent:
            logger.warning(f"Provider agent {provider_id} not found")
            return {}
            
        return agent.get_memory(
            memory_types=memory_types,
            min_importance=min_importance
        )


# Initialize the collaboration system
def initialize_collaboration_system(provider_selector: ProviderSelector) -> Tuple[CollaborationManager, CollaborativeProviderAdapter]:
    """
    Initialize the collaboration system and integrate with Lumina AI providers.
    
    Args:
        provider_selector: The provider selector
        
    Returns:
        Tuple of (collaboration_manager, provider_adapter)
    """
    # Create collaboration components
    collaboration_manager = CollaborationManager()
    
    # Create provider adapter
    provider_adapter = CollaborativeProviderAdapter(
        collaboration_manager=collaboration_manager,
        provider_selector=provider_selector
    )
    
    logger.info("Initialized collaboration system")
    return (collaboration_manager, provider_adapter)
