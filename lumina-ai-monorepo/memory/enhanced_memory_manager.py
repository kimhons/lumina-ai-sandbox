"""
Enhanced Memory Manager for the Advanced Memory System.

This module provides a unified interface for all memory operations,
integrating the various components of the Advanced Memory System.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import time
from datetime import datetime, timedelta

from memory.compression.neural_compression import ContextCompressor
from memory.hierarchical.topic_management import TopicManager
from memory.cross_session.persistent_memory import CrossSessionMemory, MemoryItem
from memory.retrieval.memory_retrieval import MemoryRetrievalOptimizer, EmbeddingProvider
from memory.context.manager import context_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedMemoryManager:
    """
    Enhanced Memory Manager for the Advanced Memory System.
    
    This class provides a unified interface for all memory operations,
    integrating neural compression, hierarchical memory, cross-session memory,
    and memory retrieval optimization.
    """
    
    def __init__(self):
        """
        Initialize the enhanced memory manager.
        """
        logger.info("Initializing Enhanced Memory Manager")
        
        # Initialize components
        self.embedding_provider = EmbeddingProvider()
        self.context_compressor = ContextCompressor(self.embedding_provider)
        self.topic_manager = TopicManager(self.embedding_provider)
        self.cross_session_memory = CrossSessionMemory()
        self.retrieval_optimizer = MemoryRetrievalOptimizer(embedding_provider=self.embedding_provider)
        
        # Use the global context manager
        self.context_manager = context_manager
        
        logger.info("Enhanced Memory Manager initialized successfully")
    
    def process_message(self, user_id: str, message: str, role: str = "user") -> Dict[str, Any]:
        """
        Process a new message, updating context and extracting memories.
        
        Args:
            user_id: ID of the user
            message: Message content
            role: Role of the message sender (user or assistant)
            
        Returns:
            Processing results
        """
        logger.info(f"Processing message for user {user_id}")
        
        # Add message to context
        context_data = self.context_manager.add_to_context(user_id, message, role)
        
        # Extract potential memories from user messages
        memories = []
        if role == "user":
            # Simple memory extraction (in a real system, this would be more sophisticated)
            if len(message) > 50:  # Only extract from substantial messages
                memory_item = self.cross_session_memory.store(
                    user_id=user_id,
                    key=f"msg_{int(time.time())}",
                    value=message,
                    memory_type="conversation",
                    importance_score=0.5  # Default importance
                )
                memories.append(memory_item)
                
                # Assign to topics
                self.topic_manager.assign_memory_to_topics(user_id, memory_item)
        
        # Analyze context
        context_analysis = self.context_manager.analyze_context(user_id)
        
        return {
            "context_data": context_data,
            "memories_extracted": memories,
            "context_analysis": context_analysis
        }
    
    def retrieve_relevant_memories(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the current context.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        logger.info(f"Retrieving relevant memories for user {user_id}")
        
        # Get current context
        context_data = self.context_manager.get_context(user_id)
        context_text = context_data["full_text"]
        
        # Get user's memory store
        memory_store = self.cross_session_memory.get_user_store(user_id)
        if not memory_store:
            return []
        
        # Retrieve memories using the retrieval optimizer
        results = self.retrieval_optimizer.retrieve_memories(
            memory_store=memory_store.get_all_items(),
            context=context_text,
            limit=limit,
            strategy="context"
        )
        
        # Extract memory items from results
        memories = [item for item, _ in results]
        
        return memories
    
    def store_memory(self, user_id: str, key: str, value: str, memory_type: str = "general", 
                    importance: float = 0.5, ttl_days: Optional[int] = None, 
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store a memory item.
        
        Args:
            user_id: ID of the user
            key: Key for the memory item
            value: Content of the memory item
            memory_type: Type of memory (e.g., "general", "user_preference", "learning")
            importance: Importance score (0-1)
            ttl_days: Time-to-live in days (None for no expiration)
            metadata: Additional metadata for the memory item
            
        Returns:
            The stored memory item
        """
        logger.info(f"Storing memory for user {user_id}: {key}")
        
        # Generate embedding for the memory
        embedding = self.embedding_provider.get_embedding(value)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Add memory to cross-session store
        memory_item = self.cross_session_memory.store(
            user_id=user_id,
            key=key,
            value=value,
            memory_type=memory_type,
            importance_score=importance,
            ttl_days=ttl_days,
            embedding=embedding,
            metadata=metadata
        )
        
        # Organize memory into topics
        try:
            self.topic_manager.assign_memory_to_topics(user_id, memory_item)
            logger.info(f"Assigned memory to topics: {key}")
        except Exception as e:
            logger.error(f"Failed to assign memory to topics: {e}")
        
        return memory_item
    
    def retrieve_memory(self, user_id: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory item by key.
        
        Args:
            user_id: ID of the user
            key: Key of the memory to retrieve
            
        Returns:
            The memory item if found, None otherwise
        """
        logger.info(f"Retrieving memory for user {user_id}: {key}")
        
        # Retrieve from cross-session memory
        memory_item = self.cross_session_memory.retrieve(user_id, key)
        
        return memory_item
    
    def update_memory(self, user_id: str, key: str, value: str, 
                     importance: Optional[float] = None) -> bool:
        """
        Update an existing memory item.
        
        Args:
            user_id: ID of the user
            key: Key of the memory to update
            value: New content for the memory
            importance: New importance score (optional)
            
        Returns:
            True if update was successful, False otherwise
        """
        logger.info(f"Updating memory for user {user_id}: {key}")
        
        # Update the memory
        updated = self.cross_session_memory.update(
            user_id=user_id,
            key=key,
            value=value,
            importance_score=importance
        )
        
        if updated:
            # Re-assign to topics if value changed
            memory_item = self.cross_session_memory.retrieve(user_id, key)
            if memory_item:
                self.topic_manager.assign_memory_to_topics(user_id, memory_item)
        
        return updated
    
    def delete_memory(self, user_id: str, key: str) -> bool:
        """
        Delete a memory item.
        
        Args:
            user_id: ID of the user
            key: Key of the memory to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        logger.info(f"Deleting memory for user {user_id}: {key}")
        
        # Delete the memory
        deleted = self.cross_session_memory.delete(user_id, key)
        
        return deleted
    
    def compress_context(self, context: str, compression_ratio: float = 0.5) -> str:
        """
        Compress conversation context using neural compression.
        
        Args:
            context: The conversation context to compress
            compression_ratio: Target compression ratio (0-1)
            
        Returns:
            Compressed context
        """
        logger.info(f"Compressing context (ratio: {compression_ratio})")
        
        # Compress using the context compressor
        compressed_context = self.context_compressor.compress(context, compression_ratio)
        
        return compressed_context
    
    def get_topics_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all topics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of topics
        """
        logger.info(f"Getting topics for user {user_id}")
        
        # Get topics from the topic manager
        topics = self.topic_manager.get_topics_for_user(user_id)
        
        return topics
    
    def get_memories_by_topic(self, user_id: str, topic_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a specific topic.
        
        Args:
            user_id: ID of the user
            topic_id: ID of the topic
            
        Returns:
            List of memory items in the topic
        """
        logger.info(f"Getting memories for topic {topic_id} for user {user_id}")
        
        # Get memories from the topic manager
        memories = self.topic_manager.get_memories_by_topic(user_id, topic_id)
        
        return memories
    
    def optimize_retrieval(self, user_id: str, context: str, query: Optional[str] = None,
                         memory_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Optimize memory retrieval based on inputs.
        
        Args:
            user_id: ID of the user
            context: The conversation context
            query: Explicit search query (optional)
            memory_type: Type of memories to retrieve (optional)
            limit: Maximum number of items to retrieve
            
        Returns:
            List of relevant memory items
        """
        logger.info(f"Optimizing memory retrieval for user {user_id}")
        
        # Get user's memory store
        memory_store = self.cross_session_memory.get_user_store(user_id)
        if not memory_store:
            return []
        
        # Optimize retrieval using the retrieval optimizer
        results = self.retrieval_optimizer.optimize_retrieval_strategy(
            memory_store=memory_store.get_all_items(),
            context=context,
            query=query,
            memory_type=memory_type,
            limit=limit
        )
        
        # Extract memory items from results
        memories = [item for item, _ in results]
        
        return memories
    
    def clear_expired_memories(self) -> int:
        """
        Clear expired memory items.
        
        Returns:
            Number of items cleared
        """
        logger.info("Clearing expired memory items")
        
        # Clear from cross-session memory
        count = self.cross_session_memory.clear_expired()
        
        logger.info(f"Cleared {count} expired memory items")
        return count
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Memory statistics
        """
        logger.info(f"Getting memory statistics for user {user_id}")
        
        # Get user's memory store
        memory_store = self.cross_session_memory.get_user_store(user_id)
        if not memory_store:
            return {
                "total_memories": 0,
                "memory_types": {},
                "topic_count": 0,
                "average_importance": 0.0,
                "oldest_memory": None,
                "newest_memory": None
            }
        
        # Get all memories
        memories = memory_store.get_all_items()
        
        # Count by type
        memory_types = {}
        for memory in memories:
            memory_type = memory.memory_type
            memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
        
        # Get topics
        topics = self.topic_manager.get_topics_for_user(user_id)
        
        # Calculate average importance
        if memories:
            avg_importance = sum(memory.importance_score for memory in memories) / len(memories)
        else:
            avg_importance = 0.0
        
        # Find oldest and newest
        if memories:
            oldest = min(memories, key=lambda x: x.created_at)
            newest = max(memories, key=lambda x: x.created_at)
            oldest_time = oldest.created_at
            newest_time = newest.created_at
        else:
            oldest_time = None
            newest_time = None
        
        return {
            "total_memories": len(memories),
            "memory_types": memory_types,
            "topic_count": len(topics),
            "average_importance": avg_importance,
            "oldest_memory": oldest_time,
            "newest_memory": newest_time
        }


# Singleton instance for global access
memory_manager = EnhancedMemoryManager()
