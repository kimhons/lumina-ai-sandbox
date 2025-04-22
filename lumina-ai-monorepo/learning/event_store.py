import logging
import json
import os
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
import asyncio
import uuid

from .interfaces import (
    LearningEvent, FeedbackEvent, InteractionEvent, ErrorEvent, PerformanceEvent,
    LearningEventStore, LearningModel, LearningStrategy
)

logger = logging.getLogger(__name__)


class InMemoryLearningEventStore(LearningEventStore):
    """In-memory implementation of a learning event store."""
    
    def __init__(self):
        """Initialize a new in-memory learning event store."""
        self.events: Dict[str, LearningEvent] = {}
    
    async def store_event(self, event: LearningEvent) -> bool:
        """
        Store a learning event.
        
        Args:
            event: Learning event to store
            
        Returns:
            True if storing was successful, False otherwise
        """
        try:
            self.events[event.event_id] = event
            return True
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return False
    
    async def get_event(self, event_id: str) -> Optional[LearningEvent]:
        """
        Get a learning event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            The event if found, None otherwise
        """
        return self.events.get(event_id)
    
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
        result = []
        
        # Apply filters
        for event in self.events.values():
            if filters:
                match = True
                for key, value in filters.items():
                    if key == "event_type":
                        if event.event_type != value:
                            match = False
                            break
                    elif key == "user_id":
                        if event.user_id != value:
                            match = False
                            break
                    elif key == "agent_id":
                        if event.agent_id != value:
                            match = False
                            break
                    elif key == "conversation_id":
                        if event.conversation_id != value:
                            match = False
                            break
                    elif key.startswith("data."):
                        data_key = key[5:]  # Remove "data." prefix
                        if data_key not in event.data or event.data[data_key] != value:
                            match = False
                            break
                    elif key.startswith("metadata."):
                        metadata_key = key[9:]  # Remove "metadata." prefix
                        if metadata_key not in event.metadata or event.metadata[metadata_key] != value:
                            match = False
                            break
                
                if not match:
                    continue
            
            # Apply time filters
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            result.append(event)
        
        # Sort by timestamp
        result.sort(key=lambda e: e.timestamp)
        
        # Apply pagination
        if offset is not None:
            result = result[offset:]
        
        if limit is not None:
            result = result[:limit]
        
        return result
    
    async def delete_event(self, event_id: str) -> bool:
        """
        Delete a learning event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False


class FileLearningEventStore(LearningEventStore):
    """File-based implementation of a learning event store."""
    
    def __init__(self, file_path: str):
        """
        Initialize a new file-based learning event store.
        
        Args:
            file_path: Path to the file to store events in
        """
        self.file_path = file_path
        self.events: Dict[str, LearningEvent] = {}
        self._load_events()
    
    def _load_events(self):
        """Load events from the file."""
        if not os.path.exists(self.file_path):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            # Create an empty file
            with open(self.file_path, 'w') as f:
                f.write('{}')
            return
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                
                for event_id, event_data in data.items():
                    event_type = event_data.get("event_type")
                    
                    if event_type == "feedback":
                        event = FeedbackEvent.from_dict(event_data)
                    elif event_type == "interaction":
                        event = InteractionEvent.from_dict(event_data)
                    elif event_type == "error":
                        event = ErrorEvent.from_dict(event_data)
                    elif event_type == "performance":
                        event = PerformanceEvent.from_dict(event_data)
                    else:
                        event = LearningEvent.from_dict(event_data)
                    
                    self.events[event_id] = event
        
        except Exception as e:
            logger.error(f"Error loading events from file: {e}")
    
    def _save_events(self):
        """Save events to the file."""
        try:
            data = {event_id: event.to_dict() for event_id, event in self.events.items()}
            
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving events to file: {e}")
    
    async def store_event(self, event: LearningEvent) -> bool:
        """
        Store a learning event.
        
        Args:
            event: Learning event to store
            
        Returns:
            True if storing was successful, False otherwise
        """
        try:
            self.events[event.event_id] = event
            self._save_events()
            return True
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return False
    
    async def get_event(self, event_id: str) -> Optional[LearningEvent]:
        """
        Get a learning event by ID.
        
        Args:
            event_id: ID of the event to get
            
        Returns:
            The event if found, None otherwise
        """
        return self.events.get(event_id)
    
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
        result = []
        
        # Apply filters
        for event in self.events.values():
            if filters:
                match = True
                for key, value in filters.items():
                    if key == "event_type":
                        if event.event_type != value:
                            match = False
                            break
                    elif key == "user_id":
                        if event.user_id != value:
                            match = False
                            break
                    elif key == "agent_id":
                        if event.agent_id != value:
                            match = False
                            break
                    elif key == "conversation_id":
                        if event.conversation_id != value:
                            match = False
                            break
                    elif key.startswith("data."):
                        data_key = key[5:]  # Remove "data." prefix
                        if data_key not in event.data or event.data[data_key] != value:
                            match = False
                            break
                    elif key.startswith("metadata."):
                        metadata_key = key[9:]  # Remove "metadata." prefix
                        if metadata_key not in event.metadata or event.metadata[metadata_key] != value:
                            match = False
                            break
                
                if not match:
                    continue
            
            # Apply time filters
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            result.append(event)
        
        # Sort by timestamp
        result.sort(key=lambda e: e.timestamp)
        
        # Apply pagination
        if offset is not None:
            result = result[offset:]
        
        if limit is not None:
            result = result[:limit]
        
        return result
    
    async def delete_event(self, event_id: str) -> bool:
        """
        Delete a learning event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if event_id in self.events:
            del self.events[event_id]
            self._save_events()
            return True
        return False


class EventStoreFactory:
    """Factory for creating learning event stores."""
    
    @staticmethod
    def create_event_store(store_type: str, **kwargs) -> LearningEventStore:
        """
        Create a learning event store.
        
        Args:
            store_type: Type of event store to create
            **kwargs: Additional arguments for the event store
            
        Returns:
            The created event store
            
        Raises:
            ValueError: If the store type is not supported
        """
        if store_type == "memory":
            return InMemoryLearningEventStore()
        elif store_type == "file":
            file_path = kwargs.get("file_path")
            if not file_path:
                raise ValueError("file_path is required for file event store")
            return FileLearningEventStore(file_path)
        else:
            raise ValueError(f"Unsupported event store type: {store_type}")
