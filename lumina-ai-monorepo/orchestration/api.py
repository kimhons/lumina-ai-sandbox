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
from .orchestrator import MultiAgentOrchestrator

logger = logging.getLogger(__name__)


class OrchestrationAPI:
    """
    API for interacting with the multi-agent orchestration system.
    This class provides a simplified interface for client applications.
    """
    
    def __init__(self, orchestrator: MultiAgentOrchestrator = None):
        """
        Initialize a new orchestration API.
        
        Args:
            orchestrator: The multi-agent orchestrator to use
        """
        self.orchestrator = orchestrator or MultiAgentOrchestrator()
    
    async def start(self):
        """Start the orchestration system."""
        await self.orchestrator.start()
    
    async def stop(self):
        """Stop the orchestration system."""
        await self.orchestrator.stop()
    
    # Agent management
    
    async def create_ai_agent(
        self,
        name: str,
        provider_name: str,
        model_name: str,
        role: str = None,
        system_prompt: str = None,
        capabilities: List[Dict[str, Any]] = None,
        tools: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new AI agent.
        
        Args:
            name: Name of the agent
            provider_name: Name of the AI provider
            model_name: Name of the model
            role: Role of the agent
            system_prompt: System prompt for the agent
            capabilities: List of capabilities
            tools: List of tools
            metadata: Additional metadata
            
        Returns:
            Dictionary with agent details
        """
        # Convert role string to enum
        agent_role = None
        if role:
            try:
                agent_role = AgentRole(role)
            except ValueError:
                logger.warning(f"Invalid role: {role}, using default")
        
        # Convert capabilities to AgentCapability objects
        agent_capabilities = []
        if capabilities:
            for cap in capabilities:
                agent_capabilities.append(AgentCapability(
                    name=cap.get("name", ""),
                    description=cap.get("description", ""),
                    parameters=cap.get("parameters", {})
                ))
        
        # Create the agent
        agent_id = await self.orchestrator.create_agent(
            agent_type=AgentType.AI,
            name=name,
            role=agent_role,
            provider_name=provider_name,
            model_name=model_name,
            system_prompt=system_prompt,
            capabilities=agent_capabilities,
            tools=tools,
            metadata=metadata or {}
        )
        
        # Get the created agent
        agent = await self.orchestrator.orchestration_manager.get_agent(agent_id)
        
        # Return agent details
        return agent.to_dict()
    
    async def create_human_agent(
        self,
        name: str,
        user_id: str,
        capabilities: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new human agent.
        
        Args:
            name: Name of the agent
            user_id: ID of the user
            capabilities: List of capabilities
            metadata: Additional metadata
            
        Returns:
            Dictionary with agent details
        """
        # Convert capabilities to AgentCapability objects
        agent_capabilities = []
        if capabilities:
            for cap in capabilities:
                agent_capabilities.append(AgentCapability(
                    name=cap.get("name", ""),
                    description=cap.get("description", ""),
                    parameters=cap.get("parameters", {})
                ))
        
        # Create the agent
        agent_id = await self.orchestrator.create_agent(
            agent_type=AgentType.HUMAN,
            name=name,
            user_id=user_id,
            capabilities=agent_capabilities,
            metadata=metadata or {}
        )
        
        # Get the created agent
        agent = await self.orchestrator.orchestration_manager.get_agent(agent_id)
        
        # Return agent details
        return agent.to_dict()
    
    async def create_tool_agent(
        self,
        name: str,
        tool_id: str,
        capabilities: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new tool agent.
        
        Args:
            name: Name of the agent
            tool_id: ID of the tool
            capabilities: List of capabilities
            metadata: Additional metadata
            
        Returns:
            Dictionary with agent details
        """
        # Convert capabilities to AgentCapability objects
        agent_capabilities = []
        if capabilities:
            for cap in capabilities:
                agent_capabilities.append(AgentCapability(
                    name=cap.get("name", ""),
                    description=cap.get("description", ""),
                    parameters=cap.get("parameters", {})
                ))
        
        # Create the agent
        agent_id = await self.orchestrator.create_agent(
            agent_type=AgentType.TOOL,
            name=name,
            tool_id=tool_id,
            capabilities=agent_capabilities,
            metadata=metadata or {}
        )
        
        # Get the created agent
        agent = await self.orchestrator.orchestration_manager.get_agent(agent_id)
        
        # Return agent details
        return agent.to_dict()
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with agent details, or None if not found
        """
        agent = await self.orchestrator.orchestration_manager.get_agent(agent_id)
        if agent:
            return agent.to_dict()
        return None
    
    async def list_agents(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List agents.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of dictionaries with agent details
        """
        agents = await self.orchestrator.orchestration_manager.list_agents(filters)
        return [agent.to_dict() for agent in agents]
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.orchestration_manager.unregister_agent(agent_id)
    
    # Team management
    
    async def create_team(
        self,
        name: str,
        description: str = None,
        leader_id: str = None,
        member_ids: List[str] = None,
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new team.
        
        Args:
            name: Name of the team
            description: Description of the team
            leader_id: ID of the team leader
            member_ids: IDs of team members
            capabilities: List of team capabilities
            metadata: Additional metadata
            
        Returns:
            Dictionary with team details
        """
        from .orchestrator import TeamDefinition
        
        # Create the team
        team = TeamDefinition(
            name=name,
            description=description,
            leader_id=leader_id,
            member_ids=member_ids or [],
            capabilities=capabilities or [],
            metadata=metadata or {}
        )
        
        # Register the team
        team_id = await self.orchestrator.create_team(team)
        
        # Get the created team
        team = await self.orchestrator.get_team(team_id)
        
        # Return team details
        return team.to_dict()
    
    async def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a team by ID.
        
        Args:
            team_id: ID of the team
            
        Returns:
            Dictionary with team details, or None if not found
        """
        team = await self.orchestrator.get_team(team_id)
        if team:
            return team.to_dict()
        return None
    
    async def list_teams(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List teams.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of dictionaries with team details
        """
        teams = await self.orchestrator.list_teams(filters)
        return [team.to_dict() for team in teams]
    
    async def update_team(self, team_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a team.
        
        Args:
            team_id: ID of the team
            updates: Dictionary of updates
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.update_team(team_id, updates)
    
    async def delete_team(self, team_id: str) -> bool:
        """
        Delete a team.
        
        Args:
            team_id: ID of the team
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.delete_team(team_id)
    
    # Workflow management
    
    async def create_workflow(
        self,
        name: str,
        description: str = None,
        steps: List[Dict[str, Any]] = None,
        start_step_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            steps: List of workflow steps
            start_step_id: ID of the start step
            metadata: Additional metadata
            
        Returns:
            Dictionary with workflow details
        """
        from .orchestrator import Workflow, WorkflowStep
        
        # Create workflow steps
        workflow_steps = {}
        if steps:
            for step_data in steps:
                step = WorkflowStep(
                    step_id=step_data.get("step_id"),
                    name=step_data.get("name", ""),
                    description=step_data.get("description", ""),
                    agent_id=step_data.get("agent_id"),
                    team_id=step_data.get("team_id"),
                    input_schema=step_data.get("input_schema", {}),
                    output_schema=step_data.get("output_schema", {}),
                    next_steps=step_data.get("next_steps", []),
                    condition=step_data.get("condition"),
                    metadata=step_data.get("metadata", {})
                )
                workflow_steps[step.step_id] = step
        
        # Create the workflow
        workflow = Workflow(
            name=name,
            description=description,
            steps=workflow_steps,
            start_step_id=start_step_id,
            metadata=metadata or {}
        )
        
        # Register the workflow
        workflow_id = await self.orchestrator.create_workflow(workflow)
        
        # Get the created workflow
        workflow = await self.orchestrator.get_workflow(workflow_id)
        
        # Return workflow details
        return workflow.to_dict()
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary with workflow details, or None if not found
        """
        workflow = await self.orchestrator.get_workflow(workflow_id)
        if workflow:
            return workflow.to_dict()
        return None
    
    async def list_workflows(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List workflows.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of dictionaries with workflow details
        """
        workflows = await self.orchestrator.list_workflows(filters)
        return [workflow.to_dict() for workflow in workflows]
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a workflow.
        
        Args:
            workflow_id: ID of the workflow
            updates: Dictionary of updates
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.update_workflow(workflow_id, updates)
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.delete_workflow(workflow_id)
    
    # Workflow execution
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow
            input_data: Input data for the workflow
            metadata: Additional metadata
            
        Returns:
            Dictionary with execution details
        """
        # Execute the workflow
        execution_id = await self.orchestrator.execute_workflow(
            workflow_id=workflow_id,
            input_data=input_data or {},
            metadata=metadata or {}
        )
        
        # Get the execution
        execution = await self.orchestrator.get_execution(execution_id)
        
        # Return execution details
        return execution.to_dict()
    
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow execution by ID.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Dictionary with execution details, or None if not found
        """
        execution = await self.orchestrator.get_execution(execution_id)
        if execution:
            return execution.to_dict()
        return None
    
    async def list_executions(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List workflow executions.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of dictionaries with execution details
        """
        executions = await self.orchestrator.list_executions(filters)
        return [execution.to_dict() for execution in executions]
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a workflow execution.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.cancel_execution(execution_id)
    
    # Messaging
    
    async def send_message(
        self,
        content: str,
        sender_id: str,
        recipient_id: str,
        conversation_id: str = None,
        message_type: str = "text",
        metadata: Dict[str, Any] = None,
        attachments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message.
        
        Args:
            content: Message content
            sender_id: ID of the sender
            recipient_id: ID of the recipient
            conversation_id: ID of the conversation
            message_type: Type of the message
            metadata: Additional metadata
            attachments: List of attachments
            
        Returns:
            Dictionary with message details
        """
        # Create the message
        message = Message(
            content=content,
            sender_id=sender_id,
            recipient_id=recipient_id,
            conversation_id=conversation_id,
            message_type=message_type,
            metadata=metadata or {},
            attachments=attachments or []
        )
        
        # Send the message
        success = await self.orchestrator.orchestration_manager.send_message(message)
        
        if not success:
            raise ValueError("Failed to send message")
        
        # Return message details
        return message.to_dict()
    
    async def create_conversation(
        self,
        title: str,
        participants: List[str],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            title: Title of the conversation
            participants: IDs of participants
            metadata: Additional metadata
            
        Returns:
            Dictionary with conversation details
        """
        # Create the conversation
        conversation = Conversation(
            title=title,
            participants=participants,
            metadata=metadata or {}
        )
        
        # Register the conversation
        conversation_id = await self.orchestrator.orchestration_manager.create_conversation(conversation)
        
        # Get the created conversation
        conversation = await self.orchestrator.orchestration_manager.get_conversation(conversation_id)
        
        # Return conversation details
        return conversation.to_dict()
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with conversation details, or None if not found
        """
        conversation = await self.orchestrator.orchestration_manager.get_conversation(conversation_id)
        if conversation:
            return conversation.to_dict()
        return None
    
    async def list_conversations(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List conversations.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of dictionaries with conversation details
        """
        conversations = await self.orchestrator.orchestration_manager.list_conversations(filters)
        return [conversation.to_dict() for conversation in conversations]
    
    # Task management
    
    async def create_task(
        self,
        title: str,
        description: str = None,
        assigned_to: str = None,
        created_by: str = None,
        priority: int = 1,
        deadline: str = None,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            title: Title of the task
            description: Description of the task
            assigned_to: ID of the agent assigned to the task
            created_by: ID of the agent that created the task
            priority: Priority level (1-5)
            deadline: Deadline for the task
            dependencies: IDs of dependent tasks
            metadata: Additional metadata
            
        Returns:
            Dictionary with task details
        """
        # Create the task
        task = Task(
            title=title,
            description=description,
            status="pending",
            priority=priority,
            assigned_to=assigned_to,
            created_by=created_by,
            deadline=deadline,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        # Register the task
        task_id = await self.orchestrator.orchestration_manager.create_task(task)
        
        # Get the created task
        task = await self.orchestrator.orchestration_manager.get_task(task_id)
        
        # Return task details
        return task.to_dict()
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dictionary with task details, or None if not found
        """
        task = await self.orchestrator.orchestration_manager.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    async def list_tasks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        List tasks.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of dictionaries with task details
        """
        tasks = await self.orchestrator.orchestration_manager.list_tasks(filters)
        return [task.to_dict() for task in tasks]
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a task.
        
        Args:
            task_id: ID of the task
            updates: Dictionary of updates
            
        Returns:
            True if successful, False otherwise
        """
        return await self.orchestrator.orchestration_manager.update_task(task_id, updates)
