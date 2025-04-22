"""
Integration module for connecting the Advanced Multi-Agent Collaboration system
with the Memory System.

This module provides adapters and utilities for integrating the collaboration
system's shared memory with the existing memory components.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from memory.vector.store import VectorStore
from memory.context.manager import ContextManager
from memory.hierarchical.memory import HierarchicalMemory

from collaboration.shared_memory import SharedMemoryService, MemoryScope, MemoryType

logger = logging.getLogger(__name__)

class MemorySystemAdapter:
    """
    Adapter for integrating the collaboration system's shared memory with
    the existing memory system components.
    """
    
    def __init__(
        self,
        shared_memory_service: SharedMemoryService,
        vector_store: VectorStore,
        context_manager: ContextManager,
        hierarchical_memory: HierarchicalMemory
    ):
        """
        Initialize the memory system adapter.
        
        Args:
            shared_memory_service: The shared memory service from the collaboration system
            vector_store: The vector store from the memory system
            context_manager: The context manager from the memory system
            hierarchical_memory: The hierarchical memory from the memory system
        """
        self.shared_memory_service = shared_memory_service
        self.vector_store = vector_store
        self.context_manager = context_manager
        self.hierarchical_memory = hierarchical_memory
        
        # Initialize mapping between memory systems
        self.memory_id_mapping: Dict[str, str] = {}
        self.context_id_mapping: Dict[str, str] = {}
        
        logger.info("Memory system adapter initialized")
    
    def sync_shared_to_vector(self, memory_id: str) -> Optional[str]:
        """
        Synchronize a memory item from shared memory to vector store.
        
        Args:
            memory_id: The ID of the memory item in shared memory
            
        Returns:
            The ID of the memory item in vector store, or None if synchronization failed
        """
        # Get memory item from shared memory
        memory_item = self.shared_memory_service.get_memory(memory_id)
        if not memory_item:
            logger.warning(f"Memory item {memory_id} not found in shared memory")
            return None
        
        # Convert memory item to vector store format
        metadata = {
            "source": "collaboration",
            "memory_type": memory_item.memory_type,
            "scope": memory_item.scope,
            "scope_id": memory_item.scope_id,
            "agent_id": memory_item.agent_id,
            "importance": memory_item.importance,
            "tags": ",".join(memory_item.tags),
            "shared_memory_id": memory_id
        }
        
        # Store in vector store
        try:
            vector_id = self.vector_store.add_item(
                text=str(memory_item.value),
                metadata=metadata,
                key=memory_item.key
            )
            
            # Update mapping
            self.memory_id_mapping[memory_id] = vector_id
            
            logger.info(f"Synchronized memory item {memory_id} to vector store as {vector_id}")
            return vector_id
        except Exception as e:
            logger.error(f"Failed to synchronize memory item {memory_id} to vector store: {e}")
            return None
    
    def sync_vector_to_shared(self, vector_id: str) -> Optional[str]:
        """
        Synchronize a memory item from vector store to shared memory.
        
        Args:
            vector_id: The ID of the memory item in vector store
            
        Returns:
            The ID of the memory item in shared memory, or None if synchronization failed
        """
        # Get memory item from vector store
        try:
            item = self.vector_store.get_item(vector_id)
            if not item:
                logger.warning(f"Memory item {vector_id} not found in vector store")
                return None
            
            # Extract metadata
            metadata = item.get("metadata", {})
            
            # Determine memory type
            memory_type_str = metadata.get("memory_type", "factual")
            try:
                memory_type = getattr(MemoryType, memory_type_str.upper())
            except AttributeError:
                memory_type = MemoryType.FACTUAL
            
            # Determine scope
            scope_str = metadata.get("scope", "agent")
            try:
                scope = getattr(MemoryScope, scope_str.upper())
            except AttributeError:
                scope = MemoryScope.AGENT
            
            # Extract tags
            tags_str = metadata.get("tags", "")
            tags = tags_str.split(",") if tags_str else []
            
            # Create memory item in shared memory
            memory_id = self.shared_memory_service.create_memory(
                key=item.get("key", f"vector_{vector_id}"),
                value=item.get("text", ""),
                memory_type=memory_type,
                scope=scope,
                scope_id=metadata.get("scope_id", "default"),
                agent_id=metadata.get("agent_id", "system"),
                importance=float(metadata.get("importance", 0.5)),
                tags=tags
            )
            
            # Update mapping
            self.memory_id_mapping[memory_id] = vector_id
            
            logger.info(f"Synchronized memory item {vector_id} to shared memory as {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to synchronize memory item {vector_id} to shared memory: {e}")
            return None
    
    def sync_shared_to_hierarchical(self, memory_id: str) -> bool:
        """
        Synchronize a memory item from shared memory to hierarchical memory.
        
        Args:
            memory_id: The ID of the memory item in shared memory
            
        Returns:
            True if synchronization was successful, False otherwise
        """
        # Get memory item from shared memory
        memory_item = self.shared_memory_service.get_memory(memory_id)
        if not memory_item:
            logger.warning(f"Memory item {memory_id} not found in shared memory")
            return False
        
        # Determine memory level based on importance
        if memory_item.importance >= 0.8:
            level = "core"
        elif memory_item.importance >= 0.5:
            level = "episodic"
        else:
            level = "buffer"
        
        # Store in hierarchical memory
        try:
            self.hierarchical_memory.store(
                level=level,
                key=memory_item.key,
                value=memory_item.value,
                metadata={
                    "source": "collaboration",
                    "memory_type": memory_item.memory_type,
                    "scope": memory_item.scope,
                    "scope_id": memory_item.scope_id,
                    "agent_id": memory_item.agent_id,
                    "importance": memory_item.importance,
                    "tags": memory_item.tags,
                    "shared_memory_id": memory_id
                }
            )
            
            logger.info(f"Synchronized memory item {memory_id} to hierarchical memory at level {level}")
            return True
        except Exception as e:
            logger.error(f"Failed to synchronize memory item {memory_id} to hierarchical memory: {e}")
            return False
    
    def sync_context_to_shared(self, context_id: str) -> Optional[str]:
        """
        Synchronize a context item from context manager to shared memory.
        
        Args:
            context_id: The ID of the context item in context manager
            
        Returns:
            The ID of the memory item in shared memory, or None if synchronization failed
        """
        # Get context item from context manager
        try:
            context = self.context_manager.get_context(context_id)
            if not context:
                logger.warning(f"Context item {context_id} not found in context manager")
                return None
            
            # Create memory item in shared memory
            memory_id = self.shared_memory_service.create_memory(
                key=f"context_{context_id}",
                value=context.get("value", {}),
                memory_type=MemoryType.CONTEXTUAL,
                scope=MemoryScope.TEAM,  # Context is typically shared with team
                scope_id=context.get("scope_id", "default"),
                agent_id=context.get("agent_id", "system"),
                importance=0.7,  # Context is typically important
                tags=["context", context.get("type", "general")]
            )
            
            # Update mapping
            self.context_id_mapping[context_id] = memory_id
            
            logger.info(f"Synchronized context item {context_id} to shared memory as {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to synchronize context item {context_id} to shared memory: {e}")
            return None
    
    def bulk_sync_shared_to_vector(self, memory_ids: List[str]) -> Dict[str, Optional[str]]:
        """
        Synchronize multiple memory items from shared memory to vector store.
        
        Args:
            memory_ids: List of memory item IDs in shared memory
            
        Returns:
            Dictionary mapping shared memory IDs to vector store IDs
        """
        results = {}
        for memory_id in memory_ids:
            vector_id = self.sync_shared_to_vector(memory_id)
            results[memory_id] = vector_id
        return results
    
    def bulk_sync_vector_to_shared(self, vector_ids: List[str]) -> Dict[str, Optional[str]]:
        """
        Synchronize multiple memory items from vector store to shared memory.
        
        Args:
            vector_ids: List of memory item IDs in vector store
            
        Returns:
            Dictionary mapping vector store IDs to shared memory IDs
        """
        results = {}
        for vector_id in vector_ids:
            memory_id = self.sync_vector_to_shared(vector_id)
            results[vector_id] = memory_id
        return results
    
    def search_and_sync_to_shared(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search vector store and synchronize results to shared memory.
        
        Args:
            query: Search query
            top_k: Number of top results to synchronize
            
        Returns:
            List of shared memory IDs for synchronized items
        """
        # Search vector store
        try:
            results = self.vector_store.search(query, top_k=top_k)
            
            # Synchronize results to shared memory
            memory_ids = []
            for result in results:
                vector_id = result.get("id")
                if vector_id:
                    memory_id = self.sync_vector_to_shared(vector_id)
                    if memory_id:
                        memory_ids.append(memory_id)
            
            logger.info(f"Synchronized {len(memory_ids)} search results to shared memory")
            return memory_ids
        except Exception as e:
            logger.error(f"Failed to search and sync to shared memory: {e}")
            return []
    
    def get_team_relevant_memories(self, team_id: str, query: Optional[str] = None, top_k: int = 10) -> Dict[str, Any]:
        """
        Get memories relevant to a team, combining shared memory and vector store.
        
        Args:
            team_id: Team ID
            query: Optional search query to filter results
            top_k: Number of top results to return
            
        Returns:
            Dictionary of relevant memories
        """
        # Get memories from shared memory
        team_memories = {}
        shared_memories = self.shared_memory_service.get_memories_by_scope(
            scope=MemoryScope.TEAM,
            scope_id=team_id
        )
        
        for memory_id, memory in shared_memories.items():
            team_memories[memory.key] = memory.value
        
        # If query is provided, search vector store and add results
        if query:
            try:
                # Search with team filter
                results = self.vector_store.search(
                    query, 
                    top_k=top_k,
                    filter_metadata={"scope": "team", "scope_id": team_id}
                )
                
                # Add results to team memories
                for result in results:
                    key = result.get("key", f"search_{result.get('id')}")
                    team_memories[key] = result.get("text", "")
            except Exception as e:
                logger.error(f"Failed to search vector store for team memories: {e}")
        
        # Limit to top_k results if needed
        if len(team_memories) > top_k:
            # Convert to list of tuples for slicing
            items = list(team_memories.items())[:top_k]
            team_memories = dict(items)
        
        return team_memories
    
    def register_memory_change_handler(self) -> None:
        """
        Register handlers for memory changes to keep systems in sync.
        """
        # This would typically involve setting up event listeners or callbacks
        # Implementation depends on the specific event system used
        logger.info("Registered memory change handlers")


def create_memory_system_adapter(
    shared_memory_service: SharedMemoryService,
    vector_store: VectorStore,
    context_manager: ContextManager,
    hierarchical_memory: HierarchicalMemory
) -> MemorySystemAdapter:
    """
    Create and initialize a memory system adapter.
    
    Args:
        shared_memory_service: The shared memory service from the collaboration system
        vector_store: The vector store from the memory system
        context_manager: The context manager from the memory system
        hierarchical_memory: The hierarchical memory from the memory system
        
    Returns:
        Initialized memory system adapter
    """
    adapter = MemorySystemAdapter(
        shared_memory_service=shared_memory_service,
        vector_store=vector_store,
        context_manager=context_manager,
        hierarchical_memory=hierarchical_memory
    )
    
    # Register change handlers
    adapter.register_memory_change_handler()
    
    return adapter
