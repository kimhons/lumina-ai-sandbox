"""
Cross-session memory module for the Advanced Memory System.

This module provides functionality for maintaining persistent memory
across different conversation sessions, enabling long-term knowledge
retention and recall.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
import uuid
import json
import datetime
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryItem:
    """
    Represents a single memory item that persists across sessions.
    
    Memory items store key information that should be remembered
    across different conversation sessions.
    """
    
    def __init__(
        self, 
        key: str, 
        value: Any, 
        user_id: str, 
        memory_type: str = "general",
        embedding: Optional[np.ndarray] = None,
        importance_score: float = 0.5,
        ttl_days: Optional[int] = None
    ):
        """
        Initialize a memory item.
        
        Args:
            key: Unique identifier for this memory
            value: The content of the memory
            user_id: ID of the user this memory belongs to
            memory_type: Type of memory (e.g., "preference", "fact", "interaction")
            embedding: Vector embedding representing the memory's semantic meaning
            importance_score: Importance score between 0 and 1
            ttl_days: Time-to-live in days (None for no expiration)
        """
        self.id = str(uuid.uuid4())
        self.key = key
        self.value = value
        self.user_id = user_id
        self.memory_type = memory_type
        self.embedding = embedding
        self.importance_score = importance_score
        
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.last_accessed = self.created_at
        self.access_count = 0
        
        # Calculate expiration date if TTL is provided
        if ttl_days is not None:
            self.expires_at = self.created_at + datetime.timedelta(days=ttl_days)
        else:
            self.expires_at = None
    
    def access(self) -> None:
        """Record an access to this memory item."""
        self.last_accessed = datetime.datetime.now()
        self.access_count += 1
    
    def update(self, value: Any) -> None:
        """
        Update the memory value.
        
        Args:
            value: New value for the memory
        """
        self.value = value
        self.updated_at = datetime.datetime.now()
    
    def is_expired(self) -> bool:
        """
        Check if the memory item has expired.
        
        Returns:
            True if the memory has expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return datetime.datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary representation.
        
        Returns:
            Dictionary representation of the memory item
        """
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "user_id": self.user_id,
            "memory_type": self.memory_type,
            "importance_score": self.importance_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """
        Create a memory item from a dictionary representation.
        
        Args:
            data: Dictionary representation of a memory item
            
        Returns:
            Reconstructed memory item
        """
        item = cls(
            key=data["key"],
            value=data["value"],
            user_id=data["user_id"],
            memory_type=data["memory_type"],
            importance_score=data["importance_score"],
            ttl_days=None  # We'll set expires_at directly
        )
        
        item.id = data["id"]
        item.created_at = datetime.datetime.fromisoformat(data["created_at"])
        item.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        item.last_accessed = datetime.datetime.fromisoformat(data["last_accessed"])
        item.access_count = data["access_count"]
        
        if data["expires_at"]:
            item.expires_at = datetime.datetime.fromisoformat(data["expires_at"])
        else:
            item.expires_at = None
        
        return item


class UserMemoryStore:
    """
    Manages memory items for a specific user.
    
    This class provides operations for storing, retrieving, and managing
    memory items for a single user across different sessions.
    """
    
    def __init__(self, user_id: str):
        """
        Initialize a user memory store.
        
        Args:
            user_id: ID of the user this store belongs to
        """
        self.user_id = user_id
        self.memories = {}  # key -> MemoryItem
        self.memory_types = defaultdict(list)  # type -> list of keys
        self.last_cleanup = datetime.datetime.now()
    
    def store(
        self, 
        key: str, 
        value: Any, 
        memory_type: str = "general",
        embedding: Optional[np.ndarray] = None,
        importance_score: float = 0.5,
        ttl_days: Optional[int] = None
    ) -> MemoryItem:
        """
        Store a memory item.
        
        Args:
            key: Unique identifier for this memory
            value: The content of the memory
            memory_type: Type of memory
            embedding: Vector embedding representing the memory's semantic meaning
            importance_score: Importance score between 0 and 1
            ttl_days: Time-to-live in days (None for no expiration)
            
        Returns:
            The stored memory item
        """
        # Create memory item
        memory = MemoryItem(
            key=key,
            value=value,
            user_id=self.user_id,
            memory_type=memory_type,
            embedding=embedding,
            importance_score=importance_score,
            ttl_days=ttl_days
        )
        
        # Store the memory
        self.memories[key] = memory
        self.memory_types[memory_type].append(key)
        
        logger.info(f"Stored memory for user {self.user_id}: {key}")
        return memory
    
    def retrieve(self, key: str) -> Optional[MemoryItem]:
        """
        Retrieve a memory item by key.
        
        Args:
            key: Key of the memory to retrieve
            
        Returns:
            The memory item if found and not expired, None otherwise
        """
        memory = self.memories.get(key)
        
        if memory is None:
            return None
        
        if memory.is_expired():
            logger.info(f"Memory {key} for user {self.user_id} has expired")
            self.delete(key)
            return None
        
        # Record access
        memory.access()
        logger.info(f"Retrieved memory for user {self.user_id}: {key}")
        
        return memory
    
    def update(self, key: str, value: Any) -> Optional[MemoryItem]:
        """
        Update a memory item.
        
        Args:
            key: Key of the memory to update
            value: New value for the memory
            
        Returns:
            The updated memory item if found and not expired, None otherwise
        """
        memory = self.retrieve(key)
        
        if memory is None:
            return None
        
        # Update the memory
        memory.update(value)
        logger.info(f"Updated memory for user {self.user_id}: {key}")
        
        return memory
    
    def delete(self, key: str) -> bool:
        """
        Delete a memory item.
        
        Args:
            key: Key of the memory to delete
            
        Returns:
            True if the memory was deleted, False if it wasn't found
        """
        if key not in self.memories:
            return False
        
        # Get the memory type before deleting
        memory_type = self.memories[key].memory_type
        
        # Delete the memory
        del self.memories[key]
        
        # Remove from memory types
        if key in self.memory_types[memory_type]:
            self.memory_types[memory_type].remove(key)
        
        logger.info(f"Deleted memory for user {self.user_id}: {key}")
        return True
    
    def get_all(self, include_expired: bool = False) -> List[MemoryItem]:
        """
        Get all memory items for the user.
        
        Args:
            include_expired: Whether to include expired memories
            
        Returns:
            List of memory items
        """
        if include_expired:
            return list(self.memories.values())
        
        # Filter out expired memories
        return [memory for memory in self.memories.values() if not memory.is_expired()]
    
    def get_by_type(self, memory_type: str, include_expired: bool = False) -> List[MemoryItem]:
        """
        Get memory items of a specific type.
        
        Args:
            memory_type: Type of memories to retrieve
            include_expired: Whether to include expired memories
            
        Returns:
            List of memory items of the specified type
        """
        keys = self.memory_types.get(memory_type, [])
        
        if include_expired:
            return [self.memories[key] for key in keys if key in self.memories]
        
        # Filter out expired memories
        return [self.memories[key] for key in keys if key in self.memories and not self.memories[key].is_expired()]
    
    def get_by_importance(self, min_importance: float = 0.0, max_importance: float = 1.0) -> List[MemoryItem]:
        """
        Get memory items with importance score in the specified range.
        
        Args:
            min_importance: Minimum importance score (inclusive)
            max_importance: Maximum importance score (inclusive)
            
        Returns:
            List of memory items with importance in the specified range
        """
        return [
            memory for memory in self.memories.values()
            if min_importance <= memory.importance_score <= max_importance
            and not memory.is_expired()
        ]
    
    def get_most_accessed(self, limit: int = 10) -> List[MemoryItem]:
        """
        Get the most frequently accessed memory items.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of most frequently accessed memory items
        """
        memories = [memory for memory in self.memories.values() if not memory.is_expired()]
        memories.sort(key=lambda x: x.access_count, reverse=True)
        return memories[:limit]
    
    def get_most_recent(self, limit: int = 10) -> List[MemoryItem]:
        """
        Get the most recently accessed memory items.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of most recently accessed memory items
        """
        memories = [memory for memory in self.memories.values() if not memory.is_expired()]
        memories.sort(key=lambda x: x.last_accessed, reverse=True)
        return memories[:limit]
    
    def cleanup_expired(self) -> int:
        """
        Remove expired memory items.
        
        Returns:
            Number of expired items removed
        """
        # Find expired memories
        expired_keys = [key for key, memory in self.memories.items() if memory.is_expired()]
        
        # Delete expired memories
        for key in expired_keys:
            self.delete(key)
        
        self.last_cleanup = datetime.datetime.now()
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired memories for user {self.user_id}")
        
        return len(expired_keys)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the user memory store to a dictionary representation.
        
        Returns:
            Dictionary representation of the user memory store
        """
        return {
            "user_id": self.user_id,
            "memories": {key: memory.to_dict() for key, memory in self.memories.items()},
            "last_cleanup": self.last_cleanup.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMemoryStore':
        """
        Create a user memory store from a dictionary representation.
        
        Args:
            data: Dictionary representation of a user memory store
            
        Returns:
            Reconstructed user memory store
        """
        store = cls(user_id=data["user_id"])
        
        # Reconstruct memories
        for key, memory_data in data["memories"].items():
            memory = MemoryItem.from_dict(memory_data)
            store.memories[key] = memory
            store.memory_types[memory.memory_type].append(key)
        
        store.last_cleanup = datetime.datetime.fromisoformat(data["last_cleanup"])
        
        return store


class CrossSessionMemory:
    """
    Manages persistent memory across different conversation sessions.
    
    This class provides a centralized system for storing and retrieving
    memory items that persist across different conversation sessions,
    enabling long-term knowledge retention and recall.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the cross-session memory system.
        
        Args:
            storage_path: Path to the storage file (None for in-memory only)
        """
        logger.info("Initializing CrossSessionMemory")
        self.user_stores = {}  # user_id -> UserMemoryStore
        self.storage_path = storage_path
        
        # Load from storage if path is provided
        if storage_path:
            self.load()
    
    def get_user_store(self, user_id: str) -> UserMemoryStore:
        """
        Get the memory store for a user, creating it if it doesn't exist.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Memory store for the user
        """
        if user_id not in self.user_stores:
            self.user_stores[user_id] = UserMemoryStore(user_id)
        
        return self.user_stores[user_id]
    
    def store(
        self, 
        user_id: str, 
        key: str, 
        value: Any, 
        memory_type: str = "general",
        embedding: Optional[np.ndarray] = None,
        importance_score: float = 0.5,
        ttl_days: Optional[int] = None
    ) -> MemoryItem:
        """
        Store a memory item for a user.
        
        Args:
            user_id: ID of the user
            key: Unique identifier for this memory
            value: The content of the memory
            memory_type: Type of memory
            embedding: Vector embedding representing the memory's semantic meaning
            importance_score: Importance score between 0 and 1
            ttl_days: Time-to-live in days (None for no expiration)
            
        Returns:
            The stored memory item
        """
        store = self.get_user_store(user_id)
        memory = store.store(
            key=key,
            value=value,
            memory_type=memory_type,
            embedding=embedding,
            importance_score=importance_score,
            ttl_days=ttl_days
        )
        
        # Save to storage if path is provided
        if self.storage_path:
            self.save()
        
        return memory
    
    def retrieve(self, user_id: str, key: str) -> Optional[MemoryItem]:
        """
        Retrieve a memory item for a user.
        
        Args:
            user_id: ID of the user
            key: Key of the memory to retrieve
            
        Returns:
            The memory item if found and not expired, None otherwise
        """
        store = self.get_user_store(user_id)
        return store.retrieve(key)
    
    def update(self, user_id: str, key: str, value: Any) -> Optional[MemoryItem]:
        """
        Update a memory item for a user.
        
        Args:
            user_id: ID of the user
            key: Key of the memory to update
            value: New value for the memory
            
        Returns:
            The updated memory item if found and not expired, None otherwise
        """
        store = self.get_user_store(user_id)
        memory = store.update(key, value)
        
        # Save to storage if path is provided and update was successful
        if memory and self.storage_path:
            self.save()
        
        return memory
    
    def delete(self, user_id: str, key: str) -> bool:
        """
        Delete a memory item for a user.
        
        Args:
            user_id: ID of the user
            key: Key of the memory to delete
            
        Returns:
            True if the memory was deleted, False if it wasn't found
        """
        store = self.get_user_store(user_id)
        success = store.delete(key)
        
        # Save to storage if path is provided and deletion was successful
        if success and self.storage_path:
            self.save()
        
        return success
    
    def get_all(self, user_id: str, include_expired: bool = False) -> List[MemoryItem]:
        """
        Get all memory items for a user.
        
        Args:
            user_id: ID of the user
            include_expired: Whether to include expired memories
            
        Returns:
            List of memory items
        """
        store = self.get_user_store(user_id)
        return store.get_all(include_expired)
    
    def get_by_type(self, user_id: str, memory_type: str, include_expired: bool = False) -> List[MemoryItem]:
        """
        Get memory items of a specific type for a user.
        
        Args:
            user_id: ID of the user
            memory_type: Type of memories to retrieve
            include_expired: Whether to include expired memories
            
        Returns:
            List of memory items of the specified type
        """
        store = self.get_user_store(user_id)
        return store.get_by_type(memory_type, include_expired)
    
    def get_by_importance(self, user_id: str, min_importance: float = 0.0, max_importance: float = 1.0) -> List[MemoryItem]:
        """
        Get memory items with importance score in the specified range for a user.
        
        Args:
            user_id: ID of the user
            min_importance: Minimum importance score (inclusive)
            max_importance: Maximum importance score (inclusive)
            
        Returns:
            List of memory items with importance in the specified range
        """
        store = self.get_user_store(user_id)
        return store.get_by_importance(min_importance, max_importance)
    
    def get_most_accessed(self, user_id: str, limit: int = 10) -> List[MemoryItem]:
        """
        Get the most frequently accessed memory items for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of items to return
            
        Returns:
            List of most frequently accessed memory items
        """
        store = self.get_user_store(user_id)
        return store.get_most_accessed(limit)
    
    def get_most_recent(self, user_id: str, limit: int = 10) -> List[MemoryItem]:
        """
        Get the most recently accessed memory items for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of items to return
            
        Returns:
            List of most recently accessed memory items
        """
        store = self.get_user_store(user_id)
        return store.get_most_recent(limit)
    
    def cleanup_expired(self, user_id: Optional[str] = None) -> int:
        """
        Remove expired memory items.
        
        Args:
            user_id: ID of the user (None to clean up for all users)
            
        Returns:
            Number of expired items removed
        """
        total_removed = 0
        
        if user_id:
            # Clean up for a specific user
            store = self.get_user_store(user_id)
            total_removed = store.cleanup_expired()
        else:
            # Clean up for all users
            for store in self.user_stores.values():
                total_removed += store.cleanup_expired()
        
        # Save to storage if path is provided and items were removed
        if total_removed > 0 and self.storage_path:
            self.save()
        
        return total_removed
    
    def save(self) -> None:
        """Save the memory system to storage."""
        if not self.storage_path:
            logger.warning("No storage path provided, cannot save")
            return
        
        try:
            # Convert user stores to dictionaries
            data = {
                user_id: store.to_dict()
                for user_id, store in self.user_stores.items()
            }
            
            # Convert numpy arrays to lists for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, default=convert_numpy)
            
            logger.info(f"Saved cross-session memory to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving cross-session memory: {e}")
    
    def load(self) -> None:
        """Load the memory system from storage."""
        if not self.storage_path:
            logger.warning("No storage path provided, cannot load")
            return
        
        try:
            # Check if file exists
            import os
            if not os.path.exists(self.storage_path):
                logger.info(f"Storage file {self.storage_path} does not exist, starting with empty memory")
                return
            
            # Load from file
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Convert dictionaries to user stores
            for user_id, store_data in data.items():
                self.user_stores[user_id] = UserMemoryStore.from_dict(store_data)
            
            logger.info(f"Loaded cross-session memory from {self.storage_path}")
        except Exception as e:
            logger.error(f"Error loading cross-session memory: {e}")
            # Start with empty memory
            self.user_stores = {}
