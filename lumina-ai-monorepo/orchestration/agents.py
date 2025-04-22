from typing import Dict, List, Any, Optional, Type, Callable
import asyncio
import logging
from .interfaces import Agent, AgentType, AgentRole, AgentStatus, AgentCapability, Message, Task

logger = logging.getLogger(__name__)


class AIAgent(Agent):
    """
    Implementation of an AI agent that can process messages and execute tasks.
    This agent uses AI providers to generate responses and perform actions.
    """
    
    def __init__(
        self,
        agent_id: str = None,
        name: str = None,
        role: AgentRole = None,
        capabilities: List[AgentCapability] = None,
        metadata: Dict[str, Any] = None,
        provider_name: str = None,
        model_name: str = None,
        system_prompt: str = None,
        tools: List[Dict[str, Any]] = None,
        memory_manager = None,
        tool_manager = None
    ):
        """
        Initialize a new AI agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            role: Role of the agent in the orchestration system
            capabilities: List of capabilities this agent has
            metadata: Additional metadata about the agent
            provider_name: Name of the AI provider to use (e.g., "openai", "claude")
            model_name: Name of the model to use (e.g., "gpt-4o", "claude-3-opus")
            system_prompt: System prompt to use for the agent
            tools: List of tools the agent can use
            memory_manager: Memory manager for the agent
            tool_manager: Tool manager for the agent
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type=AgentType.AI,
            role=role,
            capabilities=capabilities,
            metadata=metadata
        )
        
        self.provider_name = provider_name
        self.model_name = model_name
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.tools = tools or []
        self.memory_manager = memory_manager
        self.tool_manager = tool_manager
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response.
        
        Args:
            message: The message to process
            
        Returns:
            The response message
        """
        try:
            # Extract message details
            content = message.get("content", "")
            sender_id = message.get("sender_id")
            conversation_id = message.get("conversation_id")
            
            # Initialize conversation history if needed
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            
            # Add message to conversation history
            self.conversation_history[conversation_id].append({
                "role": "user",
                "content": content,
                "metadata": {
                    "sender_id": sender_id,
                    "message_id": message.get("message_id")
                }
            })
            
            # Retrieve relevant memories if memory manager is available
            context = []
            if self.memory_manager and content:
                memories = await self.memory_manager.retrieve_relevant(
                    content, 
                    limit=5, 
                    conversation_id=conversation_id
                )
                if memories:
                    context = [{"role": "system", "content": f"Relevant context: {m.content}"} for m in memories]
            
            # Prepare messages for the AI provider
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add context from memory
            messages.extend(context)
            
            # Add conversation history (limited to last 10 messages)
            history = self.conversation_history[conversation_id][-10:]
            messages.extend(history)
            
            # Generate response using the appropriate AI provider
            from lumina.providers.selector import get_provider
            provider = get_provider(self.provider_name)
            
            if not provider:
                logger.error(f"Provider {self.provider_name} not found")
                return {
                    "message_id": str(uuid.uuid4()),
                    "content": "I'm sorry, I'm having trouble connecting to my AI provider.",
                    "sender_id": self.agent_id,
                    "recipient_id": sender_id,
                    "conversation_id": conversation_id,
                    "message_type": "text",
                    "parent_id": message.get("message_id")
                }
            
            # Call the provider with tools if available
            if self.tools and self.tool_manager:
                response = await provider.generate_with_tools(
                    messages=messages,
                    model=self.model_name,
                    tools=self.tools,
                    tool_executor=self.tool_manager.execute_tool
                )
            else:
                response = await provider.generate(
                    messages=messages,
                    model=self.model_name
                )
            
            # Extract the response content
            response_content = response.get("content", "")
            
            # Add response to conversation history
            self.conversation_history[conversation_id].append({
                "role": "assistant",
                "content": response_content,
                "metadata": {
                    "sender_id": self.agent_id
                }
            })
            
            # Store in memory if memory manager is available
            if self.memory_manager and response_content:
                await self.memory_manager.store(
                    content=response_content,
                    metadata={
                        "sender_id": self.agent_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                )
            
            # Create response message
            return {
                "message_id": str(uuid.uuid4()),
                "content": response_content,
                "sender_id": self.agent_id,
                "recipient_id": sender_id,
                "conversation_id": conversation_id,
                "message_type": "text",
                "parent_id": message.get("message_id")
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message_id": str(uuid.uuid4()),
                "content": f"I encountered an error: {str(e)}",
                "sender_id": self.agent_id,
                "recipient_id": message.get("sender_id"),
                "conversation_id": message.get("conversation_id"),
                "message_type": "text",
                "parent_id": message.get("message_id")
            }
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        Args:
            task: The task to execute
            
        Returns:
            The result of the task execution
        """
        try:
            # Extract task details
            task_id = task.get("task_id")
            title = task.get("title", "")
            description = task.get("description", "")
            
            # Prepare messages for the AI provider
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"You are being asked to complete the following task: {title}"},
                {"role": "user", "content": description}
            ]
            
            # Generate response using the appropriate AI provider
            from lumina.providers.selector import get_provider
            provider = get_provider(self.provider_name)
            
            if not provider:
                logger.error(f"Provider {self.provider_name} not found")
                return {
                    "status": "failed",
                    "error": f"Provider {self.provider_name} not found"
                }
            
            # Call the provider with tools if available
            if self.tools and self.tool_manager:
                response = await provider.generate_with_tools(
                    messages=messages,
                    model=self.model_name,
                    tools=self.tools,
                    tool_executor=self.tool_manager.execute_tool
                )
            else:
                response = await provider.generate(
                    messages=messages,
                    model=self.model_name
                )
            
            # Extract the response content
            response_content = response.get("content", "")
            
            # Store in memory if memory manager is available
            if self.memory_manager and response_content:
                await self.memory_manager.store(
                    content=response_content,
                    metadata={
                        "task_id": task_id,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                )
            
            # Return the result
            return {
                "status": "completed",
                "result": response_content
            }
        
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIAgent':
        """Create an AI agent from a dictionary representation."""
        # Extract base agent fields
        agent_id = data.get("agent_id")
        name = data.get("name")
        role_value = data.get("role")
        role = AgentRole(role_value) if role_value else None
        
        # Extract capabilities
        capabilities = []
        for cap_data in data.get("capabilities", []):
            capabilities.append(AgentCapability.from_dict(cap_data))
        
        # Extract AI-specific fields
        provider_name = data.get("metadata", {}).get("provider_name")
        model_name = data.get("metadata", {}).get("model_name")
        system_prompt = data.get("metadata", {}).get("system_prompt")
        tools = data.get("metadata", {}).get("tools", [])
        
        # Create the agent
        return cls(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            metadata=data.get("metadata", {}),
            provider_name=provider_name,
            model_name=model_name,
            system_prompt=system_prompt,
            tools=tools
        )


class HumanAgent(Agent):
    """
    Implementation of a human agent that represents a user in the system.
    This agent primarily serves as a proxy for human interactions.
    """
    
    def __init__(
        self,
        agent_id: str = None,
        name: str = None,
        capabilities: List[AgentCapability] = None,
        metadata: Dict[str, Any] = None,
        user_id: str = None
    ):
        """
        Initialize a new human agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            capabilities: List of capabilities this agent has
            metadata: Additional metadata about the agent
            user_id: ID of the user this agent represents
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type=AgentType.HUMAN,
            role=AgentRole.USER,
            capabilities=capabilities,
            metadata=metadata
        )
        
        self.user_id = user_id or agent_id
        self.metadata["user_id"] = self.user_id
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.
        
        For human agents, this method doesn't generate a response automatically,
        but could notify the user through external channels.
        
        Args:
            message: The message to process
            
        Returns:
            None, as human responses are handled separately
        """
        # Human agents don't automatically respond to messages
        # This method could be used to notify the user through external channels
        logger.info(f"Message received for human agent {self.name}: {message.get('content', '')[:50]}...")
        return None
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        For human agents, this method doesn't execute the task automatically,
        but could notify the user about the task.
        
        Args:
            task: The task to execute
            
        Returns:
            Status indicating the task is pending human action
        """
        # Human agents don't automatically execute tasks
        # This method could be used to notify the user about the task
        logger.info(f"Task assigned to human agent {self.name}: {task.get('title', '')}")
        return {
            "status": "pending",
            "message": "Waiting for human action"
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanAgent':
        """Create a human agent from a dictionary representation."""
        # Extract base agent fields
        agent_id = data.get("agent_id")
        name = data.get("name")
        
        # Extract capabilities
        capabilities = []
        for cap_data in data.get("capabilities", []):
            capabilities.append(AgentCapability.from_dict(cap_data))
        
        # Extract human-specific fields
        user_id = data.get("metadata", {}).get("user_id")
        
        # Create the agent
        return cls(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            metadata=data.get("metadata", {}),
            user_id=user_id
        )


class ToolAgent(Agent):
    """
    Implementation of a tool agent that can execute specific tools or services.
    This agent serves as a wrapper around tools in the system.
    """
    
    def __init__(
        self,
        agent_id: str = None,
        name: str = None,
        capabilities: List[AgentCapability] = None,
        metadata: Dict[str, Any] = None,
        tool_id: str = None,
        tool_executor: Callable = None
    ):
        """
        Initialize a new tool agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            capabilities: List of capabilities this agent has
            metadata: Additional metadata about the agent
            tool_id: ID of the tool this agent represents
            tool_executor: Function to execute the tool
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            agent_type=AgentType.TOOL,
            role=AgentRole.EXECUTOR,
            capabilities=capabilities,
            metadata=metadata
        )
        
        self.tool_id = tool_id or agent_id
        self.tool_executor = tool_executor
        self.metadata["tool_id"] = self.tool_id
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message by treating it as a tool execution request.
        
        Args:
            message: The message to process, expected to contain tool parameters
            
        Returns:
            The result of the tool execution
        """
        try:
            # Extract message details
            content = message.get("content", "")
            sender_id = message.get("sender_id")
            conversation_id = message.get("conversation_id")
            
            # Parse parameters from content
            # This is a simple implementation; in practice, you might use a more robust parser
            parameters = {}
            try:
                # Try to parse as JSON
                import json
                parameters = json.loads(content)
            except json.JSONDecodeError:
                # Fall back to simple key-value parsing
                for line in content.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        parameters[key.strip()] = value.strip()
            
            # Execute the tool
            if self.tool_executor:
                result = await self.tool_executor(self.tool_id, parameters)
            else:
                result = {"error": "No tool executor available"}
            
            # Create response message
            return {
                "message_id": str(uuid.uuid4()),
                "content": str(result),
                "sender_id": self.agent_id,
                "recipient_id": sender_id,
                "conversation_id": conversation_id,
                "message_type": "tool_result",
                "parent_id": message.get("message_id"),
                "metadata": {
                    "tool_id": self.tool_id,
                    "parameters": parameters,
                    "result": result
                }
            }
        
        except Exception as e:
            logger.error(f"Error processing tool request: {e}")
            return {
                "message_id": str(uuid.uuid4()),
                "content": f"Error executing tool: {str(e)}",
                "sender_id": self.agent_id,
                "recipient_id": message.get("sender_id"),
                "conversation_id": message.get("conversation_id"),
                "message_type": "error",
                "parent_id": message.get("message_id")
            }
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent by treating it as a tool execution request.
        
        Args:
            task: The task to execute, expected to contain tool parameters
            
        Returns:
            The result of the tool execution
        """
        try:
            # Extract task details
            description = task.get("description", "")
            metadata = task.get("metadata", {})
            
            # Get parameters from metadata or description
            parameters = metadata.get("parameters", {})
            if not parameters and description:
                try:
                    # Try to parse description as JSON
                    import json
                    parameters = json.loads(description)
                except json.JSONDecodeError:
                    # Fall back to simple key-value parsing
                    for line in description.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            parameters[key.strip()] = value.strip()
            
            # Execute the tool
            if self.tool_executor:
                result = await self.tool_executor(self.tool_id, parameters)
            else:
                result = {"error": "No tool executor available"}
            
            # Return the result
            return {
                "status": "completed",
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Error executing tool task: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolAgent':
        """Create a tool agent from a dictionary representation."""
        # Extract base agent fields
        agent_id = data.get("agent_id")
        name = data.get("name")
        
        # Extract capabilities
        capabilities = []
        for cap_data in data.get("capabilities", []):
            capabilities.append(AgentCapability.from_dict(cap_data))
        
        # Extract tool-specific fields
        tool_id = data.get("metadata", {}).get("tool_id")
        
        # Create the agent
        return cls(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            metadata=data.get("metadata", {}),
            tool_id=tool_id
        )


class AgentFactory:
    """
    Factory class for creating agents of different types.
    """
    
    _agent_types: Dict[AgentType, Type[Agent]] = {
        AgentType.AI: AIAgent,
        AgentType.HUMAN: HumanAgent,
        AgentType.TOOL: ToolAgent
    }
    
    @classmethod
    def register_agent_type(cls, agent_type: AgentType, agent_class: Type[Agent]) -> None:
        """
        Register a new agent type with the factory.
        
        Args:
            agent_type: The type of agent to register
            agent_class: The class to use for creating agents of this type
        """
        cls._agent_types[agent_type] = agent_class
    
    @classmethod
    def create_agent(cls, agent_type: AgentType, **kwargs) -> Agent:
        """
        Create a new agent of the specified type.
        
        Args:
            agent_type: The type of agent to create
            **kwargs: Additional arguments to pass to the agent constructor
            
        Returns:
            A new agent of the specified type
            
        Raises:
            ValueError: If the agent type is not registered
        """
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_types[agent_type]
        return agent_class(**kwargs)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Agent:
        """
        Create an agent from a dictionary representation.
        
        Args:
            data: Dictionary representation of the agent
            
        Returns:
            A new agent based on the dictionary
            
        Raises:
            ValueError: If the agent type is not registered
        """
        agent_type_value = data.get("agent_type")
        if not agent_type_value:
            raise ValueError("Agent type not specified")
        
        agent_type = AgentType(agent_type_value)
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_types[agent_type]
        return agent_class.from_dict(data)
