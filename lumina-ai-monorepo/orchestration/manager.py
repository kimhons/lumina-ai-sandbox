from typing import Dict, List, Any, Optional, Union, Set
import asyncio
import json
import datetime
import uuid
import logging
from .interfaces import (
    Agent, AgentType, AgentRole, AgentStatus, AgentCapability,
    Message, Task, Conversation, OrchestrationInterface
)

logger = logging.getLogger(__name__)


class OrchestrationManager:
    """
    Central orchestration manager that coordinates multiple agents, conversations, and tasks.
    This is the concrete implementation of the OrchestrationInterface.
    """
    
    def __init__(self):
        """Initialize a new orchestration manager."""
        self.agents: Dict[str, Agent] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.tasks: Dict[str, Task] = {}
        self.agent_capabilities: Dict[str, Set[str]] = {}  # agent_id -> set of capability names
        self.message_queue = asyncio.Queue()
        self.task_queue = asyncio.Queue()
        self._running = False
        self._workers = []
    
    async def register_agent(self, agent: Agent) -> str:
        """
        Register an agent with the orchestration system.
        
        Args:
            agent: The agent to register
            
        Returns:
            The ID of the registered agent
        """
        if agent.agent_id in self.agents:
            logger.warning(f"Agent with ID {agent.agent_id} already registered, updating")
        
        self.agents[agent.agent_id] = agent
        
        # Update capability index
        capability_names = {cap.name for cap in agent.capabilities}
        self.agent_capabilities[agent.agent_id] = capability_names
        
        logger.info(f"Registered agent {agent.name} with ID {agent.agent_id}")
        return agent.agent_id
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestration system.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent with ID {agent_id} not found")
            return False
        
        # Remove from all conversations
        for conversation in self.conversations.values():
            if agent_id in conversation.participants:
                conversation.remove_participant(agent_id)
        
        # Reassign tasks
        for task in self.tasks.values():
            if task.assigned_to == agent_id:
                task.update_status("unassigned")
                task.assigned_to = None
        
        # Remove from capability index
        if agent_id in self.agent_capabilities:
            del self.agent_capabilities[agent_id]
        
        # Remove the agent
        agent = self.agents.pop(agent_id)
        logger.info(f"Unregistered agent {agent.name} with ID {agent_id}")
        return True
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            The agent if found, None otherwise
        """
        return self.agents.get(agent_id)
    
    async def list_agents(self, filters: Dict[str, Any] = None) -> List[Agent]:
        """
        List agents in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of agents matching the filters
        """
        if not filters:
            return list(self.agents.values())
        
        result = []
        for agent in self.agents.values():
            match = True
            for key, value in filters.items():
                if key == "agent_type" and agent.agent_type:
                    if agent.agent_type.value != value:
                        match = False
                        break
                elif key == "role" and agent.role:
                    if agent.role.value != value:
                        match = False
                        break
                elif key == "status" and agent.status:
                    if agent.status.value != value:
                        match = False
                        break
                elif key == "capability":
                    if not agent.has_capability(value):
                        match = False
                        break
                elif hasattr(agent, key):
                    if getattr(agent, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                result.append(agent)
        
        return result
    
    async def find_agents_by_capability(self, capability_name: str) -> List[Agent]:
        """
        Find agents that have a specific capability.
        
        Args:
            capability_name: The name of the capability to search for
            
        Returns:
            List of agents with the specified capability
        """
        matching_agents = []
        for agent_id, capabilities in self.agent_capabilities.items():
            if capability_name in capabilities:
                agent = self.agents.get(agent_id)
                if agent:
                    matching_agents.append(agent)
        
        return matching_agents
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: The message to send
            
        Returns:
            True if successful, False otherwise
        """
        # Validate message
        if not message.sender_id or not message.recipient_id:
            logger.error("Message must have both sender and recipient")
            return False
        
        if message.sender_id not in self.agents:
            logger.error(f"Sender agent {message.sender_id} not found")
            return False
        
        if message.recipient_id not in self.agents:
            logger.error(f"Recipient agent {message.recipient_id} not found")
            return False
        
        # Add to conversation if specified
        if message.conversation_id:
            conversation = self.conversations.get(message.conversation_id)
            if conversation:
                conversation.add_message(message)
            else:
                logger.warning(f"Conversation {message.conversation_id} not found")
        
        # Queue the message for delivery
        await self.message_queue.put(message)
        logger.info(f"Queued message from {message.sender_id} to {message.recipient_id}")
        return True
    
    async def create_conversation(self, conversation: Conversation) -> str:
        """
        Create a new conversation.
        
        Args:
            conversation: The conversation to create
            
        Returns:
            The ID of the created conversation
        """
        # Validate participants
        valid_participants = []
        for participant_id in conversation.participants:
            if participant_id in self.agents:
                valid_participants.append(participant_id)
            else:
                logger.warning(f"Agent {participant_id} not found, skipping")
        
        conversation.participants = valid_participants
        
        # Store the conversation
        self.conversations[conversation.conversation_id] = conversation
        logger.info(f"Created conversation {conversation.title} with ID {conversation.conversation_id}")
        return conversation.conversation_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to get
            
        Returns:
            The conversation if found, None otherwise
        """
        return self.conversations.get(conversation_id)
    
    async def list_conversations(self, filters: Dict[str, Any] = None) -> List[Conversation]:
        """
        List conversations in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of conversations matching the filters
        """
        if not filters:
            return list(self.conversations.values())
        
        result = []
        for conversation in self.conversations.values():
            match = True
            for key, value in filters.items():
                if key == "participant":
                    if value not in conversation.participants:
                        match = False
                        break
                elif hasattr(conversation, key):
                    if getattr(conversation, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                result.append(conversation)
        
        return result
    
    async def create_task(self, task: Task) -> str:
        """
        Create a new task.
        
        Args:
            task: The task to create
            
        Returns:
            The ID of the created task
        """
        # Validate assigned agent if specified
        if task.assigned_to and task.assigned_to not in self.agents:
            logger.warning(f"Agent {task.assigned_to} not found, task will be unassigned")
            task.assigned_to = None
            task.status = "unassigned"
        
        # Store the task
        self.tasks[task.task_id] = task
        
        # Queue the task for processing
        await self.task_queue.put(task)
        
        logger.info(f"Created task {task.title} with ID {task.task_id}")
        return task.task_id
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            The task if found, None otherwise
        """
        return self.tasks.get(task_id)
    
    async def list_tasks(self, filters: Dict[str, Any] = None) -> List[Task]:
        """
        List tasks in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of tasks matching the filters
        """
        if not filters:
            return list(self.tasks.values())
        
        result = []
        for task in self.tasks.values():
            match = True
            for key, value in filters.items():
                if hasattr(task, key):
                    if getattr(task, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                result.append(task)
        
        return result
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a task.
        
        Args:
            task_id: ID of the task to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return False
        
        # Apply updates
        for key, value in updates.items():
            if key == "status":
                task.update_status(value)
            elif key == "assigned_to":
                if value is None or value in self.agents:
                    task.reassign(value)
                else:
                    logger.warning(f"Agent {value} not found, skipping reassignment")
            elif hasattr(task, key):
                setattr(task, key, value)
                task.updated_at = datetime.datetime.now().isoformat()
        
        logger.info(f"Updated task {task.title} with ID {task_id}")
        return True
    
    async def start(self):
        """Start the orchestration manager."""
        if self._running:
            logger.warning("Orchestration manager already running")
            return
        
        self._running = True
        
        # Start message worker
        message_worker = asyncio.create_task(self._process_messages())
        self._workers.append(message_worker)
        
        # Start task worker
        task_worker = asyncio.create_task(self._process_tasks())
        self._workers.append(task_worker)
        
        logger.info("Orchestration manager started")
    
    async def stop(self):
        """Stop the orchestration manager."""
        if not self._running:
            logger.warning("Orchestration manager not running")
            return
        
        self._running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []
        
        logger.info("Orchestration manager stopped")
    
    async def _process_messages(self):
        """Process messages from the message queue."""
        while self._running:
            try:
                message = await self.message_queue.get()
                
                # Get recipient agent
                recipient = self.agents.get(message.recipient_id)
                if not recipient:
                    logger.error(f"Recipient agent {message.recipient_id} not found")
                    continue
                
                # Update agent status
                recipient.update_status(AgentStatus.ACTIVE)
                
                # Process message
                try:
                    response = await recipient.process_message(message.to_dict())
                    
                    # Create response message if one was returned
                    if response:
                        response_message = Message.from_dict(response)
                        await self.send_message(response_message)
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    recipient.update_status(AgentStatus.ERROR)
                
                # Mark message as processed
                self.message_queue.task_done()
            
            except asyncio.CancelledError:
                break
            
            except Exception as e:
                logger.error(f"Error in message worker: {e}")
    
    async def _process_tasks(self):
        """Process tasks from the task queue."""
        while self._running:
            try:
                task = await self.task_queue.get()
                
                # Skip tasks that are not assigned
                if not task.assigned_to:
                    logger.warning(f"Task {task.task_id} is not assigned, skipping")
                    self.task_queue.task_done()
                    continue
                
                # Get assigned agent
                agent = self.agents.get(task.assigned_to)
                if not agent:
                    logger.error(f"Assigned agent {task.assigned_to} not found")
                    task.update_status("unassigned")
                    task.assigned_to = None
                    self.task_queue.task_done()
                    continue
                
                # Check dependencies
                dependencies_met = True
                for dep_id in task.dependencies:
                    dep_task = self.tasks.get(dep_id)
                    if not dep_task or dep_task.status != "completed":
                        dependencies_met = False
                        break
                
                if not dependencies_met:
                    logger.warning(f"Dependencies for task {task.task_id} not met, requeuing")
                    await self.task_queue.put(task)
                    self.task_queue.task_done()
                    continue
                
                # Update task status
                task.update_status("in_progress")
                
                # Update agent status
                agent.update_status(AgentStatus.ACTIVE)
                
                # Execute task
                try:
                    result = await agent.execute_task(task.to_dict())
                    
                    # Update task with result
                    if result:
                        task.metadata["result"] = result
                        task.update_status("completed")
                    else:
                        task.update_status("failed")
                
                except Exception as e:
                    logger.error(f"Error executing task: {e}")
                    task.update_status("failed")
                    task.metadata["error"] = str(e)
                    agent.update_status(AgentStatus.ERROR)
                
                # Mark task as processed
                self.task_queue.task_done()
            
            except asyncio.CancelledError:
                break
            
            except Exception as e:
                logger.error(f"Error in task worker: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the orchestration manager to a dictionary representation."""
        return {
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()},
            "conversations": {conv_id: conv.to_dict() for conv_id, conv in self.conversations.items()},
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrchestrationManager':
        """Create an orchestration manager from a dictionary representation."""
        manager = cls()
        
        # Load agents
        if "agents" in data:
            for agent_data in data["agents"].values():
                # This requires a factory to create the right type of agent
                # which would be implemented elsewhere
                pass
        
        # Load conversations
        if "conversations" in data:
            for conv_id, conv_data in data["conversations"].items():
                conversation = Conversation.from_dict(conv_data)
                manager.conversations[conv_id] = conversation
        
        # Load tasks
        if "tasks" in data:
            for task_id, task_data in data["tasks"].items():
                task = Task.from_dict(task_data)
                manager.tasks[task_id] = task
        
        return manager
