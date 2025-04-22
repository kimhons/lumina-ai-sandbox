import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
import uuid
import datetime
import json

from .interfaces import (
    Agent, AgentType, AgentRole, AgentStatus, AgentCapability,
    Message, Task, Conversation, OrchestrationInterface
)
from .manager import OrchestrationManager
from .agents import AgentFactory, AIAgent, HumanAgent, ToolAgent

logger = logging.getLogger(__name__)


class TeamDefinition:
    """Defines a team of agents with specific roles and responsibilities."""
    
    def __init__(
        self,
        team_id: str = None,
        name: str = None,
        description: str = None,
        leader_id: str = None,
        member_ids: List[str] = None,
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new team definition.
        
        Args:
            team_id: Unique identifier for the team
            name: Human-readable name for the team
            description: Description of the team's purpose
            leader_id: ID of the agent that leads the team
            member_ids: IDs of agents that are members of the team
            capabilities: List of capabilities the team provides
            metadata: Additional metadata about the team
        """
        self.team_id = team_id or str(uuid.uuid4())
        self.name = name or f"Team-{self.team_id[:8]}"
        self.description = description or ""
        self.leader_id = leader_id
        self.member_ids = member_ids or []
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def add_member(self, agent_id: str) -> None:
        """
        Add a member to the team.
        
        Args:
            agent_id: ID of the agent to add
        """
        if agent_id not in self.member_ids:
            self.member_ids.append(agent_id)
            self.updated_at = datetime.datetime.now().isoformat()
    
    def remove_member(self, agent_id: str) -> None:
        """
        Remove a member from the team.
        
        Args:
            agent_id: ID of the agent to remove
        """
        if agent_id in self.member_ids:
            self.member_ids.remove(agent_id)
            self.updated_at = datetime.datetime.now().isoformat()
            
            # If the leader is removed, clear the leader_id
            if agent_id == self.leader_id:
                self.leader_id = None
    
    def set_leader(self, agent_id: str) -> None:
        """
        Set the team leader.
        
        Args:
            agent_id: ID of the agent to set as leader
        """
        if agent_id in self.member_ids:
            self.leader_id = agent_id
            self.updated_at = datetime.datetime.now().isoformat()
        else:
            raise ValueError(f"Agent {agent_id} is not a member of the team")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the team definition to a dictionary representation."""
        return {
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "leader_id": self.leader_id,
            "member_ids": self.member_ids,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamDefinition':
        """Create a team definition from a dictionary representation."""
        return cls(
            team_id=data.get("team_id"),
            name=data.get("name"),
            description=data.get("description"),
            leader_id=data.get("leader_id"),
            member_ids=data.get("member_ids", []),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {})
        )


class WorkflowStep:
    """Represents a step in a workflow."""
    
    def __init__(
        self,
        step_id: str = None,
        name: str = None,
        description: str = None,
        agent_id: str = None,
        team_id: str = None,
        input_schema: Dict[str, Any] = None,
        output_schema: Dict[str, Any] = None,
        next_steps: List[str] = None,
        condition: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new workflow step.
        
        Args:
            step_id: Unique identifier for the step
            name: Human-readable name for the step
            description: Description of what the step does
            agent_id: ID of the agent responsible for this step
            team_id: ID of the team responsible for this step
            input_schema: Schema defining the expected input
            output_schema: Schema defining the expected output
            next_steps: IDs of steps that follow this one
            condition: Condition for determining which next step to take
            metadata: Additional metadata about the step
        """
        self.step_id = step_id or str(uuid.uuid4())
        self.name = name or f"Step-{self.step_id[:8]}"
        self.description = description or ""
        self.agent_id = agent_id
        self.team_id = team_id
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.next_steps = next_steps or []
        self.condition = condition
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow step to a dictionary representation."""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "agent_id": self.agent_id,
            "team_id": self.team_id,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "next_steps": self.next_steps,
            "condition": self.condition,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """Create a workflow step from a dictionary representation."""
        return cls(
            step_id=data.get("step_id"),
            name=data.get("name"),
            description=data.get("description"),
            agent_id=data.get("agent_id"),
            team_id=data.get("team_id"),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            next_steps=data.get("next_steps", []),
            condition=data.get("condition"),
            metadata=data.get("metadata", {})
        )


class Workflow:
    """Represents a workflow that can be executed by the orchestration system."""
    
    def __init__(
        self,
        workflow_id: str = None,
        name: str = None,
        description: str = None,
        steps: Dict[str, WorkflowStep] = None,
        start_step_id: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable name for the workflow
            description: Description of what the workflow does
            steps: Dictionary of steps in the workflow
            start_step_id: ID of the first step in the workflow
            metadata: Additional metadata about the workflow
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.name = name or f"Workflow-{self.workflow_id[:8]}"
        self.description = description or ""
        self.steps = steps or {}
        self.start_step_id = start_step_id
        self.metadata = metadata or {}
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def add_step(self, step: WorkflowStep) -> None:
        """
        Add a step to the workflow.
        
        Args:
            step: The step to add
        """
        self.steps[step.step_id] = step
        self.updated_at = datetime.datetime.now().isoformat()
        
        # If this is the first step, set it as the start step
        if not self.start_step_id:
            self.start_step_id = step.step_id
    
    def remove_step(self, step_id: str) -> None:
        """
        Remove a step from the workflow.
        
        Args:
            step_id: ID of the step to remove
        """
        if step_id in self.steps:
            # Remove the step
            self.steps.pop(step_id)
            self.updated_at = datetime.datetime.now().isoformat()
            
            # If the start step is removed, clear the start_step_id
            if step_id == self.start_step_id:
                self.start_step_id = None
            
            # Remove the step from next_steps of all other steps
            for step in self.steps.values():
                if step_id in step.next_steps:
                    step.next_steps.remove(step_id)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """
        Get a step by ID.
        
        Args:
            step_id: ID of the step to get
            
        Returns:
            The step if found, None otherwise
        """
        return self.steps.get(step_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a dictionary representation."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "start_step_id": self.start_step_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create a workflow from a dictionary representation."""
        workflow = cls(
            workflow_id=data.get("workflow_id"),
            name=data.get("name"),
            description=data.get("description"),
            start_step_id=data.get("start_step_id"),
            metadata=data.get("metadata", {})
        )
        
        # Add steps
        steps_data = data.get("steps", {})
        for step_id, step_data in steps_data.items():
            workflow.steps[step_id] = WorkflowStep.from_dict(step_data)
        
        return workflow


class WorkflowExecution:
    """Represents an execution of a workflow."""
    
    def __init__(
        self,
        execution_id: str = None,
        workflow_id: str = None,
        status: str = "pending",
        current_step_id: str = None,
        input_data: Dict[str, Any] = None,
        output_data: Dict[str, Any] = None,
        step_results: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new workflow execution.
        
        Args:
            execution_id: Unique identifier for the execution
            workflow_id: ID of the workflow being executed
            status: Current status of the execution
            current_step_id: ID of the current step being executed
            input_data: Input data for the workflow
            output_data: Output data from the workflow
            step_results: Results from each step
            metadata: Additional metadata about the execution
        """
        self.execution_id = execution_id or str(uuid.uuid4())
        self.workflow_id = workflow_id
        self.status = status
        self.current_step_id = current_step_id
        self.input_data = input_data or {}
        self.output_data = output_data or {}
        self.step_results = step_results or {}
        self.metadata = metadata or {}
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.completed_at = None
    
    def update_status(self, status: str) -> None:
        """
        Update the execution status.
        
        Args:
            status: The new status
        """
        self.status = status
        self.updated_at = datetime.datetime.now().isoformat()
        
        if status in ["completed", "failed", "cancelled"]:
            self.completed_at = self.updated_at
    
    def set_current_step(self, step_id: str) -> None:
        """
        Set the current step.
        
        Args:
            step_id: ID of the current step
        """
        self.current_step_id = step_id
        self.updated_at = datetime.datetime.now().isoformat()
    
    def add_step_result(self, step_id: str, result: Any) -> None:
        """
        Add a result for a step.
        
        Args:
            step_id: ID of the step
            result: Result from the step
        """
        self.step_results[step_id] = result
        self.updated_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow execution to a dictionary representation."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "current_step_id": self.current_step_id,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "step_results": self.step_results,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowExecution':
        """Create a workflow execution from a dictionary representation."""
        execution = cls(
            execution_id=data.get("execution_id"),
            workflow_id=data.get("workflow_id"),
            status=data.get("status", "pending"),
            current_step_id=data.get("current_step_id"),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            step_results=data.get("step_results", {}),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps
        if "created_at" in data:
            execution.created_at = data["created_at"]
        if "updated_at" in data:
            execution.updated_at = data["updated_at"]
        if "completed_at" in data:
            execution.completed_at = data["completed_at"]
        
        return execution


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents, teams, and workflows.
    This is the main entry point for the multi-agent orchestration system.
    """
    
    def __init__(self, orchestration_manager: OrchestrationManager = None):
        """
        Initialize a new multi-agent orchestrator.
        
        Args:
            orchestration_manager: The orchestration manager to use
        """
        self.orchestration_manager = orchestration_manager or OrchestrationManager()
        self.teams: Dict[str, TeamDefinition] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.agent_factory = AgentFactory()
        self._running = False
        self._workers = []
    
    async def start(self):
        """Start the orchestrator and its components."""
        if self._running:
            logger.warning("Multi-agent orchestrator already running")
            return
        
        self._running = True
        
        # Start the orchestration manager
        await self.orchestration_manager.start()
        
        # Start workflow execution worker
        workflow_worker = asyncio.create_task(self._process_workflow_executions())
        self._workers.append(workflow_worker)
        
        logger.info("Multi-agent orchestrator started")
    
    async def stop(self):
        """Stop the orchestrator and its components."""
        if not self._running:
            logger.warning("Multi-agent orchestrator not running")
            return
        
        self._running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []
        
        # Stop the orchestration manager
        await self.orchestration_manager.stop()
        
        logger.info("Multi-agent orchestrator stopped")
    
    async def create_agent(self, agent_type: AgentType, **kwargs) -> str:
        """
        Create a new agent and register it with the orchestration system.
        
        Args:
            agent_type: The type of agent to create
            **kwargs: Additional arguments for the agent
            
        Returns:
            The ID of the created agent
        """
        # Create the agent
        agent = self.agent_factory.create_agent(agent_type, **kwargs)
        
        # Register the agent
        agent_id = await self.orchestration_manager.register_agent(agent)
        
        logger.info(f"Created and registered agent {agent.name} with ID {agent_id}")
        return agent_id
    
    async def create_team(self, team: TeamDefinition) -> str:
        """
        Create a new team.
        
        Args:
            team: The team to create
            
        Returns:
            The ID of the created team
        """
        # Validate team members
        valid_members = []
        for member_id in team.member_ids:
            agent = await self.orchestration_manager.get_agent(member_id)
            if agent:
                valid_members.append(member_id)
            else:
                logger.warning(f"Agent {member_id} not found, skipping")
        
        team.member_ids = valid_members
        
        # Validate team leader
        if team.leader_id and team.leader_id not in team.member_ids:
            logger.warning(f"Leader {team.leader_id} is not a team member, clearing leader")
            team.leader_id = None
        
        # Store the team
        self.teams[team.team_id] = team
        
        logger.info(f"Created team {team.name} with ID {team.team_id}")
        return team.team_id
    
    async def get_team(self, team_id: str) -> Optional[TeamDefinition]:
        """
        Get a team by ID.
        
        Args:
            team_id: ID of the team to get
            
        Returns:
            The team if found, None otherwise
        """
        return self.teams.get(team_id)
    
    async def list_teams(self, filters: Dict[str, Any] = None) -> List[TeamDefinition]:
        """
        List teams in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of teams matching the filters
        """
        if not filters:
            return list(self.teams.values())
        
        result = []
        for team in self.teams.values():
            match = True
            for key, value in filters.items():
                if key == "member":
                    if value not in team.member_ids:
                        match = False
                        break
                elif key == "capability":
                    if value not in team.capabilities:
                        match = False
                        break
                elif hasattr(team, key):
                    if getattr(team, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                result.append(team)
        
        return result
    
    async def update_team(self, team_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a team.
        
        Args:
            team_id: ID of the team to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        team = self.teams.get(team_id)
        if not team:
            logger.error(f"Team {team_id} not found")
            return False
        
        # Apply updates
        for key, value in updates.items():
            if key == "member_ids":
                # Validate members
                valid_members = []
                for member_id in value:
                    agent = await self.orchestration_manager.get_agent(member_id)
                    if agent:
                        valid_members.append(member_id)
                    else:
                        logger.warning(f"Agent {member_id} not found, skipping")
                
                team.member_ids = valid_members
                
                # Validate leader
                if team.leader_id and team.leader_id not in team.member_ids:
                    logger.warning(f"Leader {team.leader_id} is not a team member, clearing leader")
                    team.leader_id = None
            elif key == "leader_id":
                if value is None or value in team.member_ids:
                    team.leader_id = value
                else:
                    logger.warning(f"Leader {value} is not a team member, skipping")
            elif hasattr(team, key):
                setattr(team, key, value)
        
        team.updated_at = datetime.datetime.now().isoformat()
        
        logger.info(f"Updated team {team.name} with ID {team_id}")
        return True
    
    async def delete_team(self, team_id: str) -> bool:
        """
        Delete a team.
        
        Args:
            team_id: ID of the team to delete
            
        Returns:
            True if successful, False otherwise
        """
        if team_id not in self.teams:
            logger.error(f"Team {team_id} not found")
            return False
        
        # Remove the team
        team = self.teams.pop(team_id)
        
        logger.info(f"Deleted team {team.name} with ID {team_id}")
        return True
    
    async def create_workflow(self, workflow: Workflow) -> str:
        """
        Create a new workflow.
        
        Args:
            workflow: The workflow to create
            
        Returns:
            The ID of the created workflow
        """
        # Validate steps
        for step in workflow.steps.values():
            # Validate agent
            if step.agent_id and not await self.orchestration_manager.get_agent(step.agent_id):
                logger.warning(f"Agent {step.agent_id} not found for step {step.name}, clearing agent")
                step.agent_id = None
            
            # Validate team
            if step.team_id and step.team_id not in self.teams:
                logger.warning(f"Team {step.team_id} not found for step {step.name}, clearing team")
                step.team_id = None
            
            # Validate next steps
            valid_next_steps = []
            for next_step_id in step.next_steps:
                if next_step_id in workflow.steps:
                    valid_next_steps.append(next_step_id)
                else:
                    logger.warning(f"Next step {next_step_id} not found for step {step.name}, skipping")
            
            step.next_steps = valid_next_steps
        
        # Validate start step
        if workflow.start_step_id and workflow.start_step_id not in workflow.steps:
            logger.warning(f"Start step {workflow.start_step_id} not found, clearing start step")
            workflow.start_step_id = None
        
        # Store the workflow
        self.workflows[workflow.workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow.name} with ID {workflow.workflow_id}")
        return workflow.workflow_id
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            The workflow if found, None otherwise
        """
        return self.workflows.get(workflow_id)
    
    async def list_workflows(self, filters: Dict[str, Any] = None) -> List[Workflow]:
        """
        List workflows in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of workflows matching the filters
        """
        if not filters:
            return list(self.workflows.values())
        
        result = []
        for workflow in self.workflows.values():
            match = True
            for key, value in filters.items():
                if hasattr(workflow, key):
                    if getattr(workflow, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                result.append(workflow)
        
        return result
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a workflow.
        
        Args:
            workflow_id: ID of the workflow to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        # Apply updates
        for key, value in updates.items():
            if key == "steps":
                # Validate steps
                valid_steps = {}
                for step_id, step_data in value.items():
                    if isinstance(step_data, WorkflowStep):
                        step = step_data
                    else:
                        step = WorkflowStep.from_dict(step_data)
                    
                    # Validate agent
                    if step.agent_id and not await self.orchestration_manager.get_agent(step.agent_id):
                        logger.warning(f"Agent {step.agent_id} not found for step {step.name}, clearing agent")
                        step.agent_id = None
                    
                    # Validate team
                    if step.team_id and step.team_id not in self.teams:
                        logger.warning(f"Team {step.team_id} not found for step {step.name}, clearing team")
                        step.team_id = None
                    
                    valid_steps[step_id] = step
                
                workflow.steps = valid_steps
                
                # Validate start step
                if workflow.start_step_id and workflow.start_step_id not in workflow.steps:
                    logger.warning(f"Start step {workflow.start_step_id} not found, clearing start step")
                    workflow.start_step_id = None
                
                # Validate next steps for all steps
                for step in workflow.steps.values():
                    valid_next_steps = []
                    for next_step_id in step.next_steps:
                        if next_step_id in workflow.steps:
                            valid_next_steps.append(next_step_id)
                        else:
                            logger.warning(f"Next step {next_step_id} not found for step {step.name}, skipping")
                    
                    step.next_steps = valid_next_steps
            elif key == "start_step_id":
                if value is None or value in workflow.steps:
                    workflow.start_step_id = value
                else:
                    logger.warning(f"Start step {value} not found, skipping")
            elif hasattr(workflow, key):
                setattr(workflow, key, value)
        
        workflow.updated_at = datetime.datetime.now().isoformat()
        
        logger.info(f"Updated workflow {workflow.name} with ID {workflow_id}")
        return True
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: ID of the workflow to delete
            
        Returns:
            True if successful, False otherwise
        """
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        # Check if there are any active executions
        active_executions = [
            execution for execution in self.executions.values()
            if execution.workflow_id == workflow_id and execution.status in ["pending", "running"]
        ]
        
        if active_executions:
            logger.error(f"Cannot delete workflow {workflow_id} with active executions")
            return False
        
        # Remove the workflow
        workflow = self.workflows.pop(workflow_id)
        
        logger.info(f"Deleted workflow {workflow.name} with ID {workflow_id}")
        return True
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            input_data: Input data for the workflow
            metadata: Additional metadata for the execution
            
        Returns:
            The ID of the workflow execution
            
        Raises:
            ValueError: If the workflow is not found or has no start step
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if not workflow.start_step_id:
            raise ValueError(f"Workflow {workflow_id} has no start step")
        
        # Create execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status="pending",
            current_step_id=workflow.start_step_id,
            input_data=input_data or {},
            metadata=metadata or {}
        )
        
        # Store the execution
        self.executions[execution.execution_id] = execution
        
        logger.info(f"Created execution {execution.execution_id} for workflow {workflow.name}")
        return execution.execution_id
    
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """
        Get a workflow execution by ID.
        
        Args:
            execution_id: ID of the execution to get
            
        Returns:
            The execution if found, None otherwise
        """
        return self.executions.get(execution_id)
    
    async def list_executions(self, filters: Dict[str, Any] = None) -> List[WorkflowExecution]:
        """
        List workflow executions in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of executions matching the filters
        """
        if not filters:
            return list(self.executions.values())
        
        result = []
        for execution in self.executions.values():
            match = True
            for key, value in filters.items():
                if hasattr(execution, key):
                    if getattr(execution, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                result.append(execution)
        
        return result
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a workflow execution.
        
        Args:
            execution_id: ID of the execution to cancel
            
        Returns:
            True if successful, False otherwise
        """
        execution = self.executions.get(execution_id)
        if not execution:
            logger.error(f"Execution {execution_id} not found")
            return False
        
        if execution.status not in ["pending", "running"]:
            logger.warning(f"Execution {execution_id} is not active (status: {execution.status})")
            return False
        
        # Update status
        execution.update_status("cancelled")
        
        logger.info(f"Cancelled execution {execution_id}")
        return True
    
    async def _process_workflow_executions(self):
        """Process workflow executions."""
        while self._running:
            try:
                # Find pending executions
                pending_executions = [
                    execution for execution in self.executions.values()
                    if execution.status == "pending"
                ]
                
                for execution in pending_executions:
                    # Start execution
                    execution.update_status("running")
                    
                    # Process the execution in a separate task
                    task = asyncio.create_task(self._execute_workflow(execution))
                    self._workers.append(task)
                    
                    # Remove the task when done
                    task.add_done_callback(lambda t: self._workers.remove(t) if t in self._workers else None)
                
                # Sleep before checking again
                await asyncio.sleep(1)
            
            except asyncio.CancelledError:
                break
            
            except Exception as e:
                logger.error(f"Error in workflow execution worker: {e}")
                await asyncio.sleep(5)  # Sleep longer on error
    
    async def _execute_workflow(self, execution: WorkflowExecution):
        """
        Execute a workflow.
        
        Args:
            execution: The workflow execution to process
        """
        try:
            workflow_id = execution.workflow_id
            workflow = self.workflows.get(workflow_id)
            
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found for execution {execution.execution_id}")
                execution.update_status("failed")
                execution.metadata["error"] = f"Workflow {workflow_id} not found"
                return
            
            # Initialize execution context
            context = {
                "input": execution.input_data,
                "output": {},
                "step_results": execution.step_results,
                "metadata": execution.metadata
            }
            
            # Start from the current step
            current_step_id = execution.current_step_id
            
            while current_step_id:
                # Get the current step
                step = workflow.steps.get(current_step_id)
                if not step:
                    logger.error(f"Step {current_step_id} not found in workflow {workflow_id}")
                    execution.update_status("failed")
                    execution.metadata["error"] = f"Step {current_step_id} not found"
                    return
                
                # Update execution
                execution.set_current_step(current_step_id)
                
                # Execute the step
                try:
                    step_result = await self._execute_step(step, context)
                    
                    # Store the result
                    execution.add_step_result(current_step_id, step_result)
                    context["step_results"][current_step_id] = step_result
                    
                    # Determine the next step
                    next_step_id = await self._determine_next_step(step, context)
                    
                    # Move to the next step
                    current_step_id = next_step_id
                
                except Exception as e:
                    logger.error(f"Error executing step {current_step_id}: {e}")
                    execution.update_status("failed")
                    execution.metadata["error"] = f"Error in step {current_step_id}: {str(e)}"
                    return
            
            # Workflow completed successfully
            execution.output_data = context["output"]
            execution.update_status("completed")
        
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            execution.update_status("failed")
            execution.metadata["error"] = str(e)
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """
        Execute a workflow step.
        
        Args:
            step: The step to execute
            context: The execution context
            
        Returns:
            The result of the step execution
        """
        # Prepare step input
        step_input = {
            "step_id": step.step_id,
            "name": step.name,
            "description": step.description,
            "context": context
        }
        
        # Determine the executor (agent or team)
        if step.agent_id:
            # Execute with agent
            agent = await self.orchestration_manager.get_agent(step.agent_id)
            if not agent:
                raise ValueError(f"Agent {step.agent_id} not found")
            
            # Create a task for the agent
            task = Task(
                title=f"Execute workflow step: {step.name}",
                description=json.dumps(step_input),
                status="pending",
                assigned_to=step.agent_id,
                metadata={
                    "step_id": step.step_id,
                    "workflow_step": True
                }
            )
            
            # Submit the task
            task_id = await self.orchestration_manager.create_task(task)
            
            # Wait for the task to complete
            while True:
                task = await self.orchestration_manager.get_task(task_id)
                if task.status in ["completed", "failed"]:
                    break
                await asyncio.sleep(1)
            
            # Check the result
            if task.status == "failed":
                raise ValueError(f"Task failed: {task.metadata.get('error', 'Unknown error')}")
            
            # Return the result
            return task.metadata.get("result")
        
        elif step.team_id:
            # Execute with team
            team = self.teams.get(step.team_id)
            if not team:
                raise ValueError(f"Team {step.team_id} not found")
            
            # Get the team leader
            leader_id = team.leader_id
            if not leader_id:
                # If no leader, use the first member
                if not team.member_ids:
                    raise ValueError(f"Team {step.team_id} has no members")
                leader_id = team.member_ids[0]
            
            # Create a conversation for the team
            conversation = Conversation(
                title=f"Team execution of step: {step.name}",
                participants=team.member_ids,
                metadata={
                    "step_id": step.step_id,
                    "team_id": step.team_id,
                    "workflow_step": True
                }
            )
            
            # Submit the conversation
            conversation_id = await self.orchestration_manager.create_conversation(conversation)
            
            # Create a message for the team
            message = Message(
                content=json.dumps(step_input),
                sender_id="system",
                recipient_id=leader_id,
                conversation_id=conversation_id,
                message_type="workflow_step",
                metadata={
                    "step_id": step.step_id,
                    "team_id": step.team_id,
                    "workflow_step": True
                }
            )
            
            # Send the message
            await self.orchestration_manager.send_message(message)
            
            # Wait for the conversation to complete
            # This is a simplified implementation; in practice, you would need a more robust mechanism
            # to determine when a team has completed a step
            await asyncio.sleep(10)
            
            # Get the conversation
            conversation = await self.orchestration_manager.get_conversation(conversation_id)
            
            # Get the last message from the leader
            leader_messages = [
                msg for msg in conversation.messages
                if msg.sender_id == leader_id and msg.message_type == "workflow_step_result"
            ]
            
            if not leader_messages:
                raise ValueError(f"No result message from team leader")
            
            # Return the result
            last_message = sorted(leader_messages, key=lambda m: m.timestamp)[-1]
            return json.loads(last_message.content)
        
        else:
            # No executor specified, return empty result
            return {}
    
    async def _determine_next_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Optional[str]:
        """
        Determine the next step to execute.
        
        Args:
            step: The current step
            context: The execution context
            
        Returns:
            The ID of the next step, or None if there are no more steps
        """
        # If there are no next steps, we're done
        if not step.next_steps:
            return None
        
        # If there's only one next step, use it
        if len(step.next_steps) == 1:
            return step.next_steps[0]
        
        # If there's a condition, evaluate it
        if step.condition:
            # This is a simplified implementation; in practice, you would use a more robust
            # condition evaluation mechanism
            try:
                # The condition should be a Python expression that evaluates to the next step ID
                # It can access the context through the 'context' variable
                locals_dict = {"context": context}
                next_step_id = eval(step.condition, {"__builtins__": {}}, locals_dict)
                
                # Verify that the next step exists
                if next_step_id in step.next_steps:
                    return next_step_id
                else:
                    logger.warning(f"Condition evaluated to invalid step ID: {next_step_id}")
                    return step.next_steps[0]  # Fall back to the first step
            
            except Exception as e:
                logger.error(f"Error evaluating condition: {e}")
                return step.next_steps[0]  # Fall back to the first step
        
        # If there's no condition, use the first next step
        return step.next_steps[0]
