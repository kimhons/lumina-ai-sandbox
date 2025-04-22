"""
Integration module for connecting the Advanced Multi-Agent Collaboration system
with the Orchestration System.

This module provides adapters and utilities for integrating the collaboration
system's team formation and task negotiation with the existing orchestration components.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from orchestration.interfaces import Agent, Task, Orchestrator
from orchestration.manager import OrchestrationManager
from orchestration.agents import AgentRegistry

from collaboration.team_formation import TeamFormationManager, AgentCapabilityRegistry, TaskRequirement
from collaboration.negotiation import NegotiationService
from collaboration.integration import CollaborationManager

logger = logging.getLogger(__name__)

class OrchestrationAdapter:
    """
    Adapter for integrating the collaboration system with the orchestration system.
    """
    
    def __init__(
        self,
        collaboration_manager: CollaborationManager,
        orchestration_manager: OrchestrationManager,
        agent_registry: AgentRegistry
    ):
        """
        Initialize the orchestration adapter.
        
        Args:
            collaboration_manager: The collaboration manager from the collaboration system
            orchestration_manager: The orchestration manager from the orchestration system
            agent_registry: The agent registry from the orchestration system
        """
        self.collaboration_manager = collaboration_manager
        self.orchestration_manager = orchestration_manager
        self.agent_registry = agent_registry
        
        # Initialize mapping between systems
        self.agent_id_mapping: Dict[str, str] = {}
        self.task_id_mapping: Dict[str, str] = {}
        
        logger.info("Orchestration adapter initialized")
    
    def sync_agents_to_collaboration(self) -> Dict[str, str]:
        """
        Synchronize agents from orchestration system to collaboration system.
        
        Returns:
            Dictionary mapping orchestration agent IDs to collaboration agent IDs
        """
        # Get all agents from orchestration system
        orchestration_agents = self.agent_registry.get_all_agents()
        
        # Map to collaboration system
        for agent_id, agent in orchestration_agents.items():
            # Convert capabilities to collaboration format
            capabilities = {}
            for capability, level in agent.capabilities.items():
                # Normalize capability name and convert level to float between 0 and 1
                cap_name = capability.lower().replace(" ", "_")
                cap_level = float(level) / 10.0 if isinstance(level, int) else float(level)
                capabilities[cap_name] = min(max(cap_level, 0.0), 1.0)
            
            # Register agent in collaboration system
            collab_agent_id = self.collaboration_manager.register_agent(
                agent_id=f"orch_{agent_id}",
                name=agent.name,
                capabilities=capabilities,
                specializations=agent.specializations if hasattr(agent, "specializations") else []
            )
            
            # Update mapping
            self.agent_id_mapping[agent_id] = collab_agent_id
            
            logger.info(f"Synchronized agent {agent_id} to collaboration system as {collab_agent_id}")
        
        return self.agent_id_mapping
    
    def sync_tasks_to_collaboration(self) -> Dict[str, str]:
        """
        Synchronize tasks from orchestration system to collaboration system.
        
        Returns:
            Dictionary mapping orchestration task IDs to collaboration task IDs
        """
        # Get all active tasks from orchestration system
        orchestration_tasks = self.orchestration_manager.get_active_tasks()
        
        # Map to collaboration system
        for task_id, task in orchestration_tasks.items():
            # Convert requirements to collaboration format
            required_capabilities = {}
            for capability, level in task.requirements.items():
                # Normalize capability name and convert level to float between 0 and 1
                cap_name = capability.lower().replace(" ", "_")
                cap_level = float(level) / 10.0 if isinstance(level, int) else float(level)
                required_capabilities[cap_name] = min(max(cap_level, 0.0), 1.0)
            
            # Create task in collaboration system
            collab_task_id = self.collaboration_manager.create_task(
                name=task.name,
                description=task.description,
                required_capabilities=required_capabilities,
                domain_specializations=task.domains if hasattr(task, "domains") else [],
                priority=task.priority if hasattr(task, "priority") else 5,
                estimated_duration=task.estimated_duration if hasattr(task, "estimated_duration") else 1.0,
                complexity=task.complexity if hasattr(task, "complexity") else 5,
                min_team_size=task.min_agents if hasattr(task, "min_agents") else 1,
                max_team_size=task.max_agents if hasattr(task, "max_agents") else 5
            )
            
            # Update mapping
            self.task_id_mapping[task_id] = collab_task_id
            
            logger.info(f"Synchronized task {task_id} to collaboration system as {collab_task_id}")
        
        return self.task_id_mapping
    
    def create_collaborative_team_for_task(self, orchestration_task_id: str, strategy: str = "optimal_coverage") -> Optional[str]:
        """
        Create a collaborative team for an orchestration task.
        
        Args:
            orchestration_task_id: The ID of the task in the orchestration system
            strategy: The team formation strategy to use
            
        Returns:
            The ID of the created team, or None if team creation failed
        """
        # Check if task is already synchronized
        if orchestration_task_id not in self.task_id_mapping:
            # Synchronize task
            task = self.orchestration_manager.get_task(orchestration_task_id)
            if not task:
                logger.warning(f"Task {orchestration_task_id} not found in orchestration system")
                return None
            
            # Convert requirements to collaboration format
            required_capabilities = {}
            for capability, level in task.requirements.items():
                # Normalize capability name and convert level to float between 0 and 1
                cap_name = capability.lower().replace(" ", "_")
                cap_level = float(level) / 10.0 if isinstance(level, int) else float(level)
                required_capabilities[cap_name] = min(max(cap_level, 0.0), 1.0)
            
            # Create task in collaboration system
            collab_task_id = self.collaboration_manager.create_task(
                name=task.name,
                description=task.description,
                required_capabilities=required_capabilities,
                domain_specializations=task.domains if hasattr(task, "domains") else [],
                priority=task.priority if hasattr(task, "priority") else 5,
                estimated_duration=task.estimated_duration if hasattr(task, "estimated_duration") else 1.0,
                complexity=task.complexity if hasattr(task, "complexity") else 5,
                min_team_size=task.min_agents if hasattr(task, "min_agents") else 1,
                max_team_size=task.max_agents if hasattr(task, "max_agents") else 5
            )
            
            # Update mapping
            self.task_id_mapping[orchestration_task_id] = collab_task_id
        
        # Get collaboration task ID
        collab_task_id = self.task_id_mapping[orchestration_task_id]
        
        # Create team
        team_id = self.collaboration_manager.form_team(collab_task_id, strategy)
        if not team_id:
            logger.warning(f"Failed to create team for task {collab_task_id}")
            return None
        
        logger.info(f"Created collaborative team {team_id} for task {orchestration_task_id}")
        return team_id
    
    def assign_orchestration_agents_to_team(self, team_id: str) -> bool:
        """
        Assign orchestration agents to a collaborative team.
        
        Args:
            team_id: The ID of the team in the collaboration system
            
        Returns:
            True if assignment was successful, False otherwise
        """
        # Get team information
        team_info = self.collaboration_manager.get_team_info(team_id)
        if not team_info:
            logger.warning(f"Team {team_id} not found in collaboration system")
            return False
        
        # Get task information
        task_id = team_info.get("task_id")
        if not task_id:
            logger.warning(f"Team {team_id} has no associated task")
            return False
        
        # Find orchestration task ID
        orchestration_task_id = None
        for orch_id, collab_id in self.task_id_mapping.items():
            if collab_id == task_id:
                orchestration_task_id = orch_id
                break
        
        if not orchestration_task_id:
            logger.warning(f"No orchestration task found for collaboration task {task_id}")
            return False
        
        # Get team members
        members = team_info.get("members", [])
        
        # Map to orchestration agents
        orchestration_agents = []
        for member in members:
            # Extract original orchestration agent ID
            if member.startswith("orch_"):
                orch_agent_id = member[5:]  # Remove "orch_" prefix
                agent = self.agent_registry.get_agent(orch_agent_id)
                if agent:
                    orchestration_agents.append(agent)
        
        # Assign agents to task in orchestration system
        try:
            self.orchestration_manager.assign_agents_to_task(
                task_id=orchestration_task_id,
                agent_ids=[agent.id for agent in orchestration_agents]
            )
            
            logger.info(f"Assigned {len(orchestration_agents)} agents to task {orchestration_task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to assign agents to task {orchestration_task_id}: {e}")
            return False
    
    def handle_task_completion(self, orchestration_task_id: str) -> bool:
        """
        Handle task completion in both systems.
        
        Args:
            orchestration_task_id: The ID of the completed task in the orchestration system
            
        Returns:
            True if handling was successful, False otherwise
        """
        # Check if task is synchronized
        if orchestration_task_id not in self.task_id_mapping:
            logger.warning(f"Task {orchestration_task_id} not synchronized with collaboration system")
            return False
        
        # Get collaboration task ID
        collab_task_id = self.task_id_mapping[orchestration_task_id]
        
        # Get teams for task
        teams = self.collaboration_manager.get_teams_for_task(collab_task_id)
        
        # Disband teams
        for team_id in teams:
            self.collaboration_manager.disband_team(team_id)
            logger.info(f"Disbanded team {team_id} for completed task {collab_task_id}")
        
        # Remove task from mapping
        del self.task_id_mapping[orchestration_task_id]
        
        logger.info(f"Handled completion of task {orchestration_task_id}")
        return True
    
    def register_orchestration_events(self) -> None:
        """
        Register handlers for orchestration events to keep systems in sync.
        """
        # This would typically involve setting up event listeners or callbacks
        # Implementation depends on the specific event system used
        logger.info("Registered orchestration event handlers")


def create_orchestration_adapter(
    collaboration_manager: CollaborationManager,
    orchestration_manager: OrchestrationManager,
    agent_registry: AgentRegistry
) -> OrchestrationAdapter:
    """
    Create and initialize an orchestration adapter.
    
    Args:
        collaboration_manager: The collaboration manager from the collaboration system
        orchestration_manager: The orchestration manager from the orchestration system
        agent_registry: The agent registry from the orchestration system
        
    Returns:
        Initialized orchestration adapter
    """
    adapter = OrchestrationAdapter(
        collaboration_manager=collaboration_manager,
        orchestration_manager=orchestration_manager,
        agent_registry=agent_registry
    )
    
    # Synchronize agents and tasks
    adapter.sync_agents_to_collaboration()
    adapter.sync_tasks_to_collaboration()
    
    # Register event handlers
    adapter.register_orchestration_events()
    
    return adapter
