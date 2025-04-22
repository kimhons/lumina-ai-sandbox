"""
Integration module for connecting the Advanced Memory System with other Lumina AI components.

This module provides integration points between the memory system and other
core components of Lumina AI, including the learning system, collaboration system,
and UI components.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
import importlib
import os
import sys

# Import memory system components
from memory.compression.neural_compression import ContextCompressor
from memory.hierarchical.topic_management import TopicManager
from memory.cross_session.persistent_memory import CrossSessionMemory
from memory.retrieval.memory_retrieval import MemoryRetrievalOptimizer, EmbeddingProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemorySystemIntegration:
    """
    Integrates the Advanced Memory System with other Lumina AI components.
    
    This class serves as the main integration point between the memory system
    and other core components of Lumina AI, providing a unified interface for
    memory operations across the platform.
    """
    
    def __init__(self):
        """
        Initialize the memory system integration.
        """
        logger.info("Initializing Memory System Integration")
        
        # Initialize memory system components
        self.embedding_provider = EmbeddingProvider()
        self.context_compressor = ContextCompressor(self.embedding_provider)
        self.topic_manager = TopicManager(self.embedding_provider)
        self.cross_session_memory = CrossSessionMemory()
        self.retrieval_optimizer = MemoryRetrievalOptimizer(embedding_provider=self.embedding_provider)
        
        # Initialize integration components
        self._init_learning_integration()
        self._init_collaboration_integration()
        self._init_ui_integration()
        
        logger.info("Memory System Integration initialized successfully")
    
    def _init_learning_integration(self):
        """
        Initialize integration with the learning system.
        """
        logger.info("Initializing Learning System Integration")
        try:
            # Import learning system components
            from learning.integration.learning_system import LearningSystem
            from learning.core.model_registry import ModelRegistry
            
            self.learning_system = LearningSystem()
            self.model_registry = ModelRegistry()
            
            logger.info("Learning System Integration initialized successfully")
        except ImportError as e:
            logger.warning(f"Learning System components not available: {e}")
            self.learning_system = None
            self.model_registry = None
    
    def _init_collaboration_integration(self):
        """
        Initialize integration with the collaboration system.
        """
        logger.info("Initializing Collaboration System Integration")
        try:
            # Import collaboration system components
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from collaboration.agent_collaboration import AgentCollaborationManager
            from collaboration.user_collaboration import UserCollaborationManager
            
            self.agent_collaboration = AgentCollaborationManager()
            self.user_collaboration = UserCollaborationManager()
            
            logger.info("Collaboration System Integration initialized successfully")
        except ImportError as e:
            logger.warning(f"Collaboration System components not available: {e}")
            self.agent_collaboration = None
            self.user_collaboration = None
    
    def _init_ui_integration(self):
        """
        Initialize integration with UI components.
        """
        logger.info("Initializing UI Integration")
        try:
            # Import UI integration components if available
            # This is a placeholder as UI components might be in a different stack
            self.ui_integration_available = False
            logger.info("UI Integration initialized (limited functionality)")
        except Exception as e:
            logger.warning(f"UI Integration not available: {e}")
            self.ui_integration_available = False
    
    def store_memory(self, user_id: str, key: str, value: str, memory_type: str = "general", 
                    importance: float = 0.5, ttl_days: Optional[int] = None, 
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store a memory item with integration across systems.
        
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
        
        # If it's a learning-related memory, update the learning system
        if memory_type == "learning" and self.learning_system is not None:
            try:
                self.learning_system.update_knowledge(user_id, key, value, importance)
                logger.info(f"Updated learning system with memory: {key}")
            except Exception as e:
                logger.error(f"Failed to update learning system: {e}")
        
        # If it's a collaboration-related memory, update the collaboration system
        if memory_type == "collaboration" and self.agent_collaboration is not None:
            try:
                self.agent_collaboration.update_shared_context(user_id, key, value)
                logger.info(f"Updated collaboration system with memory: {key}")
            except Exception as e:
                logger.error(f"Failed to update collaboration system: {e}")
        
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
        
        # If not found and learning system is available, try there
        if memory_item is None and self.learning_system is not None:
            try:
                knowledge_item = self.learning_system.get_knowledge_item(user_id, key)
                if knowledge_item:
                    # Convert to memory item format
                    memory_item = {
                        "key": key,
                        "value": knowledge_item.get("content", ""),
                        "user_id": user_id,
                        "memory_type": "learning",
                        "importance_score": knowledge_item.get("importance", 0.5),
                        "created_at": knowledge_item.get("created_at"),
                        "updated_at": knowledge_item.get("updated_at"),
                        "source": "learning_system"
                    }
                    logger.info(f"Retrieved memory from learning system: {key}")
            except Exception as e:
                logger.error(f"Failed to retrieve from learning system: {e}")
        
        return memory_item
    
    def retrieve_by_context(self, user_id: str, context: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the current context.
        
        Args:
            user_id: ID of the user
            context: The conversation context
            limit: Maximum number of items to retrieve
            
        Returns:
            List of relevant memory items
        """
        logger.info(f"Retrieving memories by context for user {user_id}")
        
        # Get user's memory store
        memory_store = self.cross_session_memory.get_user_store(user_id)
        if not memory_store:
            return []
        
        # Retrieve memories using the retrieval optimizer
        results = self.retrieval_optimizer.retrieve_memories(
            memory_store=memory_store.get_all_items(),
            context=context,
            limit=limit,
            strategy="context"
        )
        
        # Extract memory items from results
        memories = [item for item, _ in results]
        
        # If learning system is available, augment with relevant knowledge
        if self.learning_system is not None:
            try:
                # Get relevant knowledge items
                knowledge_items = self.learning_system.retrieve_relevant_knowledge(user_id, context, limit=5)
                
                # Convert to memory item format and add to results
                for item in knowledge_items:
                    memory_item = {
                        "key": item.get("id", f"learning_{len(memories)}"),
                        "value": item.get("content", ""),
                        "user_id": user_id,
                        "memory_type": "learning",
                        "importance_score": item.get("importance", 0.5),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "source": "learning_system"
                    }
                    memories.append(memory_item)
                
                logger.info(f"Augmented with {len(knowledge_items)} items from learning system")
            except Exception as e:
                logger.error(f"Failed to retrieve from learning system: {e}")
        
        # If collaboration system is available, augment with relevant shared context
        if self.agent_collaboration is not None:
            try:
                # Get relevant shared context
                shared_items = self.agent_collaboration.get_relevant_shared_context(user_id, context, limit=3)
                
                # Convert to memory item format and add to results
                for item in shared_items:
                    memory_item = {
                        "key": item.get("id", f"collab_{len(memories)}"),
                        "value": item.get("content", ""),
                        "user_id": user_id,
                        "memory_type": "collaboration",
                        "importance_score": item.get("importance", 0.5),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "source": "collaboration_system"
                    }
                    memories.append(memory_item)
                
                logger.info(f"Augmented with {len(shared_items)} items from collaboration system")
            except Exception as e:
                logger.error(f"Failed to retrieve from collaboration system: {e}")
        
        # Ensure we don't exceed the limit
        if len(memories) > limit:
            memories = memories[:limit]
        
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
        
        # Augment with items from other systems based on memory_type
        if memory_type == "learning" and self.learning_system is not None:
            try:
                # Get relevant knowledge items
                knowledge_items = self.learning_system.retrieve_relevant_knowledge(
                    user_id, query or context, limit=limit)
                
                # Convert to memory item format and add to results
                for item in knowledge_items:
                    memory_item = {
                        "key": item.get("id", f"learning_{len(memories)}"),
                        "value": item.get("content", ""),
                        "user_id": user_id,
                        "memory_type": "learning",
                        "importance_score": item.get("importance", 0.5),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "source": "learning_system"
                    }
                    memories.append(memory_item)
                
                logger.info(f"Augmented with {len(knowledge_items)} items from learning system")
            except Exception as e:
                logger.error(f"Failed to retrieve from learning system: {e}")
        
        elif memory_type == "collaboration" and self.agent_collaboration is not None:
            try:
                # Get relevant shared context
                shared_items = self.agent_collaboration.get_relevant_shared_context(
                    user_id, query or context, limit=limit)
                
                # Convert to memory item format and add to results
                for item in shared_items:
                    memory_item = {
                        "key": item.get("id", f"collab_{len(memories)}"),
                        "value": item.get("content", ""),
                        "user_id": user_id,
                        "memory_type": "collaboration",
                        "importance_score": item.get("importance", 0.5),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "source": "collaboration_system"
                    }
                    memories.append(memory_item)
                
                logger.info(f"Augmented with {len(shared_items)} items from collaboration system")
            except Exception as e:
                logger.error(f"Failed to retrieve from collaboration system: {e}")
        
        # Ensure we don't exceed the limit
        if len(memories) > limit:
            memories = memories[:limit]
        
        return memories
    
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
    
    def update_learning_from_memory(self, user_id: str, memory_key: str) -> bool:
        """
        Update the learning system with a specific memory item.
        
        Args:
            user_id: ID of the user
            memory_key: Key of the memory to use for learning
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating learning system from memory {memory_key} for user {user_id}")
        
        if self.learning_system is None:
            logger.warning("Learning system not available")
            return False
        
        # Retrieve the memory item
        memory_item = self.retrieve_memory(user_id, memory_key)
        if not memory_item:
            logger.warning(f"Memory item not found: {memory_key}")
            return False
        
        try:
            # Update the learning system
            self.learning_system.update_knowledge(
                user_id, 
                memory_key, 
                memory_item["value"], 
                memory_item.get("importance_score", 0.5)
            )
            logger.info(f"Successfully updated learning system with memory: {memory_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to update learning system: {e}")
            return False
    
    def share_memory_in_collaboration(self, user_id: str, memory_key: str, 
                                     collaboration_id: str) -> bool:
        """
        Share a memory item in a collaboration session.
        
        Args:
            user_id: ID of the user
            memory_key: Key of the memory to share
            collaboration_id: ID of the collaboration session
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Sharing memory {memory_key} in collaboration {collaboration_id}")
        
        if self.agent_collaboration is None and self.user_collaboration is None:
            logger.warning("Collaboration systems not available")
            return False
        
        # Retrieve the memory item
        memory_item = self.retrieve_memory(user_id, memory_key)
        if not memory_item:
            logger.warning(f"Memory item not found: {memory_key}")
            return False
        
        try:
            # Share in agent collaboration if available
            if self.agent_collaboration is not None:
                self.agent_collaboration.share_context(
                    user_id,
                    collaboration_id,
                    memory_key,
                    memory_item["value"]
                )
            
            # Share in user collaboration if available
            if self.user_collaboration is not None:
                self.user_collaboration.share_memory(
                    user_id,
                    collaboration_id,
                    memory_key,
                    memory_item["value"]
                )
            
            logger.info(f"Successfully shared memory in collaboration: {memory_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to share memory in collaboration: {e}")
            return False
    
    def get_memory_for_ui(self, user_id: str, context: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get memory items formatted for UI display.
        
        Args:
            user_id: ID of the user
            context: Current conversation context
            limit: Maximum number of items to retrieve
            
        Returns:
            Dictionary with memory items organized for UI display
        """
        logger.info(f"Getting memory items for UI display for user {user_id}")
        
        # Retrieve relevant memories
        memories = self.retrieve_by_context(user_id, context, limit=limit)
        
        # Get user's topics
        topics = self.topic_manager.get_topics_for_user(user_id)
        
        # Organize by type for UI display
        result = {
            "recent_memories": [],
            "relevant_memories": memories,
            "topics": topics[:5],  # Top 5 topics
            "has_more": len(memories) >= limit or len(topics) > 5
        }
        
        # Get recent memories
        user_store = self.cross_session_memory.get_user_store(user_id)
        if user_store:
            recent = user_store.get_recent_items(5)
            result["recent_memories"] = recent
        
        return result
    
    def clear_expired_memories(self) -> int:
        """
        Clear expired memory items across the system.
        
        Returns:
            Number of items cleared
        """
        logger.info("Clearing expired memory items")
        
        # Clear from cross-session memory
        count = self.cross_session_memory.clear_expired()
        
        logger.info(f"Cleared {count} expired memory items")
        return count


# Singleton instance for global access
memory_integration = MemorySystemIntegration()
