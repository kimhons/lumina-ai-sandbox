from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)


class LearningEvent:
    """Represents an event that can be used for learning."""
    
    def __init__(
        self,
        event_id: str = None,
        event_type: str = None,
        timestamp: str = None,
        user_id: str = None,
        agent_id: str = None,
        conversation_id: str = None,
        data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new learning event.
        
        Args:
            event_id: Unique identifier for the event
            event_type: Type of the event
            timestamp: Timestamp of the event
            user_id: ID of the user associated with the event
            agent_id: ID of the agent associated with the event
            conversation_id: ID of the conversation associated with the event
            data: Event data
            metadata: Additional metadata
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.timestamp = timestamp or datetime.datetime.now().isoformat()
        self.user_id = user_id
        self.agent_id = agent_id
        self.conversation_id = conversation_id
        self.data = data or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the learning event to a dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningEvent':
        """Create a learning event from a dictionary representation."""
        return cls(
            event_id=data.get("event_id"),
            event_type=data.get("event_type"),
            timestamp=data.get("timestamp"),
            user_id=data.get("user_id"),
            agent_id=data.get("agent_id"),
            conversation_id=data.get("conversation_id"),
            data=data.get("data", {}),
            metadata=data.get("metadata", {})
        )


class FeedbackEvent(LearningEvent):
    """Represents a feedback event from a user."""
    
    def __init__(
        self,
        rating: int = None,
        feedback_text: str = None,
        feedback_type: str = None,
        **kwargs
    ):
        """
        Initialize a new feedback event.
        
        Args:
            rating: Numerical rating (e.g., 1-5)
            feedback_text: Textual feedback
            feedback_type: Type of feedback (e.g., "response_quality", "helpfulness")
            **kwargs: Additional arguments for LearningEvent
        """
        super().__init__(event_type="feedback", **kwargs)
        self.data["rating"] = rating
        self.data["feedback_text"] = feedback_text
        self.data["feedback_type"] = feedback_type


class InteractionEvent(LearningEvent):
    """Represents an interaction event between a user and an agent."""
    
    def __init__(
        self,
        interaction_type: str = None,
        content: str = None,
        duration: float = None,
        **kwargs
    ):
        """
        Initialize a new interaction event.
        
        Args:
            interaction_type: Type of interaction (e.g., "message", "command")
            content: Content of the interaction
            duration: Duration of the interaction in seconds
            **kwargs: Additional arguments for LearningEvent
        """
        super().__init__(event_type="interaction", **kwargs)
        self.data["interaction_type"] = interaction_type
        self.data["content"] = content
        self.data["duration"] = duration


class ErrorEvent(LearningEvent):
    """Represents an error event during agent operation."""
    
    def __init__(
        self,
        error_type: str = None,
        error_message: str = None,
        stack_trace: str = None,
        severity: str = None,
        **kwargs
    ):
        """
        Initialize a new error event.
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace
            severity: Severity of the error (e.g., "info", "warning", "error", "critical")
            **kwargs: Additional arguments for LearningEvent
        """
        super().__init__(event_type="error", **kwargs)
        self.data["error_type"] = error_type
        self.data["error_message"] = error_message
        self.data["stack_trace"] = stack_trace
        self.data["severity"] = severity


class PerformanceEvent(LearningEvent):
    """Represents a performance event for an agent."""
    
    def __init__(
        self,
        metric_name: str = None,
        metric_value: float = None,
        context: Dict[str, Any] = None,
        **kwargs
    ):
        """
        Initialize a new performance event.
        
        Args:
            metric_name: Name of the performance metric
            metric_value: Value of the performance metric
            context: Context in which the metric was measured
            **kwargs: Additional arguments for LearningEvent
        """
        super().__init__(event_type="performance", **kwargs)
        self.data["metric_name"] = metric_name
        self.data["metric_value"] = metric_value
        self.data["context"] = context or {}


class LearningModel(ABC):
    """Abstract base class for learning models."""
    
    @abstractmethod
    async def train(self, events: List[LearningEvent]) -> bool:
        """
        Train the model on a list of events.
        
        Args:
            events: List of learning events
            
        Returns:
            True if training was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def predict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction based on the context.
        
        Args:
            context: Context for the prediction
            
        Returns:
            Prediction result
        """
        pass
    
    @abstractmethod
    async def save(self, path: str) -> bool:
        """
        Save the model to a file.
        
        Args:
            path: Path to save the model
            
        Returns:
            True if saving was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def load(self, path: str) -> bool:
        """
        Load the model from a file.
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if loading was successful, False otherwise
        """
        pass


class LearningEventStore(ABC):
    """Abstract base class for learning event stores."""
    
    @abstractmethod
    async def store_event(self, event: LearningEvent) -> bool:
        """
        Store a learning event.
        
        Args:
            event: Learning event to store
            
        Returns:
            True if storing was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[LearningEvent]:
        """
        Get a learning event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            The event if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def query_events(
        self,
        filters: Dict[str, Any] = None,
        start_time: str = None,
        end_time: str = None,
        limit: int = None,
        offset: int = None
    ) -> List[LearningEvent]:
        """
        Query learning events.
        
        Args:
            filters: Filters to apply
            start_time: Start time for time-based filtering
            end_time: End time for time-based filtering
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of events matching the query
        """
        pass
    
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """
        Delete a learning event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass


class LearningStrategy(ABC):
    """Abstract base class for learning strategies."""
    
    @abstractmethod
    async def process_event(self, event: LearningEvent) -> bool:
        """
        Process a learning event.
        
        Args:
            event: Learning event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def train_models(self) -> bool:
        """
        Train models based on collected events.
        
        Returns:
            True if training was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def apply_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learning to a context.
        
        Args:
            context: Context to apply learning to
            
        Returns:
            Modified context
        """
        pass
