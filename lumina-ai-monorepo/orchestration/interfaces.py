from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import uuid
import json
import datetime


class AgentType(Enum):
    """Enumeration of agent types in the orchestration system."""
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"
    TOOL = "tool"


class AgentRole(Enum):
    """Enumeration of agent roles in the orchestration system."""
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    ASSISTANT = "assistant"
    CRITIC = "critic"
    EXECUTOR = "executor"
    OBSERVER = "observer"
    USER = "user"


class AgentStatus(Enum):
    """Enumeration of agent statuses in the orchestration system."""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentCapability:
    """Represents a capability that an agent can have."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        """
        Initialize a new agent capability.
        
        Args:
            name: The name of the capability
            description: A description of what the capability does
            parameters: Optional parameters that define how the capability works
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the capability to a dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCapability':
        """Create a capability from a dictionary representation."""
        return cls(
            name=data["name"],
            description=data["description"],
            parameters=data.get("parameters", {})
        )


class Agent(ABC):
    """Base abstract class for all agents in the orchestration system."""
    
    def __init__(
        self,
        agent_id: str = None,
        name: str = None,
        agent_type: AgentType = None,
        role: AgentRole = None,
        capabilities: List[AgentCapability] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new agent.
        
        Args:
            agent_id: Unique identifier for the agent (auto-generated if not provided)
            name: Human-readable name for the agent
            agent_type: Type of the agent (AI, HUMAN, SYSTEM, TOOL)
            role: Role of the agent in the orchestration system
            capabilities: List of capabilities this agent has
            metadata: Additional metadata about the agent
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent-{self.agent_id[:8]}"
        self.agent_type = agent_type
        self.role = role
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.status = AgentStatus.IDLE
        self.created_at = datetime.datetime.now().isoformat()
        self.last_active = self.created_at
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response.
        
        Args:
            message: The message to process
            
        Returns:
            The response message
        """
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        Args:
            task: The task to execute
            
        Returns:
            The result of the task execution
        """
        pass
    
    def has_capability(self, capability_name: str) -> bool:
        """
        Check if the agent has a specific capability.
        
        Args:
            capability_name: The name of the capability to check for
            
        Returns:
            True if the agent has the capability, False otherwise
        """
        return any(cap.name == capability_name for cap in self.capabilities)
    
    def add_capability(self, capability: AgentCapability) -> None:
        """
        Add a capability to the agent.
        
        Args:
            capability: The capability to add
        """
        if not self.has_capability(capability.name):
            self.capabilities.append(capability)
    
    def remove_capability(self, capability_name: str) -> None:
        """
        Remove a capability from the agent.
        
        Args:
            capability_name: The name of the capability to remove
        """
        self.capabilities = [cap for cap in self.capabilities if cap.name != capability_name]
    
    def update_status(self, status: AgentStatus) -> None:
        """
        Update the agent's status.
        
        Args:
            status: The new status
        """
        self.status = status
        if status == AgentStatus.ACTIVE:
            self.last_active = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type.value if self.agent_type else None,
            "role": self.role.value if self.role else None,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_active": self.last_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create an agent from a dictionary representation."""
        # This is a factory method that should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement from_dict")


class Message:
    """Represents a message in the orchestration system."""
    
    def __init__(
        self,
        message_id: str = None,
        content: str = None,
        sender_id: str = None,
        recipient_id: str = None,
        conversation_id: str = None,
        message_type: str = "text",
        metadata: Dict[str, Any] = None,
        attachments: List[Dict[str, Any]] = None,
        parent_id: str = None,
        timestamp: str = None
    ):
        """
        Initialize a new message.
        
        Args:
            message_id: Unique identifier for the message
            content: The content of the message
            sender_id: ID of the agent that sent the message
            recipient_id: ID of the agent that should receive the message
            conversation_id: ID of the conversation this message belongs to
            message_type: Type of the message (text, image, file, etc.)
            metadata: Additional metadata about the message
            attachments: List of attachments to the message
            parent_id: ID of the parent message if this is a reply
            timestamp: When the message was created
        """
        self.message_id = message_id or str(uuid.uuid4())
        self.content = content or ""
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.conversation_id = conversation_id
        self.message_type = message_type
        self.metadata = metadata or {}
        self.attachments = attachments or []
        self.parent_id = parent_id
        self.timestamp = timestamp or datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary representation."""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "conversation_id": self.conversation_id,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "attachments": self.attachments,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a message from a dictionary representation."""
        return cls(
            message_id=data.get("message_id"),
            content=data.get("content"),
            sender_id=data.get("sender_id"),
            recipient_id=data.get("recipient_id"),
            conversation_id=data.get("conversation_id"),
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata", {}),
            attachments=data.get("attachments", []),
            parent_id=data.get("parent_id"),
            timestamp=data.get("timestamp")
        )


class Task:
    """Represents a task in the orchestration system."""
    
    def __init__(
        self,
        task_id: str = None,
        title: str = None,
        description: str = None,
        status: str = "pending",
        priority: int = 1,
        assigned_to: str = None,
        created_by: str = None,
        deadline: str = None,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None,
        created_at: str = None,
        updated_at: str = None
    ):
        """
        Initialize a new task.
        
        Args:
            task_id: Unique identifier for the task
            title: Title of the task
            description: Detailed description of the task
            status: Current status of the task
            priority: Priority level (1-5, with 5 being highest)
            assigned_to: ID of the agent assigned to the task
            created_by: ID of the agent that created the task
            deadline: When the task should be completed by
            dependencies: List of task IDs that must be completed before this one
            metadata: Additional metadata about the task
            created_at: When the task was created
            updated_at: When the task was last updated
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.title = title or f"Task-{self.task_id[:8]}"
        self.description = description or ""
        self.status = status
        self.priority = priority
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.deadline = deadline
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
    
    def update_status(self, status: str) -> None:
        """
        Update the task's status.
        
        Args:
            status: The new status
        """
        self.status = status
        self.updated_at = datetime.datetime.now().isoformat()
    
    def reassign(self, agent_id: str) -> None:
        """
        Reassign the task to a different agent.
        
        Args:
            agent_id: ID of the agent to assign the task to
        """
        self.assigned_to = agent_id
        self.updated_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary representation."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "deadline": self.deadline,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a task from a dictionary representation."""
        return cls(
            task_id=data.get("task_id"),
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status", "pending"),
            priority=data.get("priority", 1),
            assigned_to=data.get("assigned_to"),
            created_by=data.get("created_by"),
            deadline=data.get("deadline"),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class Conversation:
    """Represents a conversation in the orchestration system."""
    
    def __init__(
        self,
        conversation_id: str = None,
        title: str = None,
        participants: List[str] = None,
        metadata: Dict[str, Any] = None,
        created_at: str = None,
        updated_at: str = None
    ):
        """
        Initialize a new conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            title: Title of the conversation
            participants: List of agent IDs participating in the conversation
            metadata: Additional metadata about the conversation
            created_at: When the conversation was created
            updated_at: When the conversation was last updated
        """
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.title = title or f"Conversation-{self.conversation_id[:8]}"
        self.participants = participants or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.messages = []
    
    def add_message(self, message: Message) -> None:
        """
        Add a message to the conversation.
        
        Args:
            message: The message to add
        """
        if message.conversation_id is None:
            message.conversation_id = self.conversation_id
        self.messages.append(message)
        self.updated_at = datetime.datetime.now().isoformat()
    
    def add_participant(self, agent_id: str) -> None:
        """
        Add a participant to the conversation.
        
        Args:
            agent_id: ID of the agent to add
        """
        if agent_id not in self.participants:
            self.participants.append(agent_id)
            self.updated_at = datetime.datetime.now().isoformat()
    
    def remove_participant(self, agent_id: str) -> None:
        """
        Remove a participant from the conversation.
        
        Args:
            agent_id: ID of the agent to remove
        """
        if agent_id in self.participants:
            self.participants.remove(agent_id)
            self.updated_at = datetime.datetime.now().isoformat()
    
    def get_messages(self, limit: int = None, offset: int = 0) -> List[Message]:
        """
        Get messages from the conversation.
        
        Args:
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of messages
        """
        messages = sorted(self.messages, key=lambda m: m.timestamp)
        if limit is not None:
            return messages[offset:offset + limit]
        return messages[offset:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the conversation to a dictionary representation."""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "participants": self.participants,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [message.to_dict() for message in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create a conversation from a dictionary representation."""
        conversation = cls(
            conversation_id=data.get("conversation_id"),
            title=data.get("title"),
            participants=data.get("participants", []),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        
        # Add messages if present
        if "messages" in data:
            for message_data in data["messages"]:
                conversation.add_message(Message.from_dict(message_data))
        
        return conversation


class OrchestrationInterface(ABC):
    """Interface for the orchestration system."""
    
    @abstractmethod
    async def register_agent(self, agent: Agent) -> str:
        """
        Register an agent with the orchestration system.
        
        Args:
            agent: The agent to register
            
        Returns:
            The ID of the registered agent
        """
        pass
    
    @abstractmethod
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestration system.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            The agent if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_agents(self, filters: Dict[str, Any] = None) -> List[Agent]:
        """
        List agents in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of agents matching the filters
        """
        pass
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: The message to send
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def create_conversation(self, conversation: Conversation) -> str:
        """
        Create a new conversation.
        
        Args:
            conversation: The conversation to create
            
        Returns:
            The ID of the created conversation
        """
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to get
            
        Returns:
            The conversation if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_conversations(self, filters: Dict[str, Any] = None) -> List[Conversation]:
        """
        List conversations in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of conversations matching the filters
        """
        pass
    
    @abstractmethod
    async def create_task(self, task: Task) -> str:
        """
        Create a new task.
        
        Args:
            task: The task to create
            
        Returns:
            The ID of the created task
        """
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            The task if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_tasks(self, filters: Dict[str, Any] = None) -> List[Task]:
        """
        List tasks in the orchestration system.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of tasks matching the filters
        """
        pass
    
    @abstractmethod
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a task.
        
        Args:
            task_id: ID of the task to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
