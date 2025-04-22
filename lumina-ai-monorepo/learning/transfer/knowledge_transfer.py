"""
Knowledge Transfer Module for Lumina AI Enhanced Learning System

This module enables the sharing of learned information between agents,
allowing for collaborative learning and knowledge propagation across the system.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, field
import os
import json
import datetime
import uuid
import logging
import pickle
import hashlib
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeItem:
    """Representation of a transferable knowledge item."""
    knowledge_id: str
    source_agent_id: str
    knowledge_type: str  # e.g., "concept", "rule", "preference", "skill"
    content: Dict[str, Any]  # Knowledge content
    metadata: Dict[str, Any]  # Additional metadata
    confidence: float  # 0.0 to 1.0
    timestamp: str
    version: int = 1
    tags: List[str] = field(default_factory=list)


@dataclass
class KnowledgeTransferEvent:
    """Record of a knowledge transfer event between agents."""
    event_id: str
    source_agent_id: str
    target_agent_id: str
    knowledge_ids: List[str]
    transfer_type: str  # e.g., "push", "pull", "broadcast"
    status: str  # e.g., "pending", "completed", "failed"
    timestamp: str
    metadata: Dict[str, Any]  # Additional metadata


class KnowledgeRepository:
    """
    Repository for storing and retrieving knowledge items.
    
    This class provides methods for managing knowledge items, including
    storage, retrieval, versioning, and search.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the KnowledgeRepository.
        
        Args:
            storage_path: Path to store knowledge items
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # In-memory cache of knowledge items
        self.knowledge_cache = {}
        
        # Index for efficient search
        self.knowledge_index = {
            "by_agent": defaultdict(set),
            "by_type": defaultdict(set),
            "by_tag": defaultdict(set)
        }
    
    def store_knowledge(self, knowledge_item: KnowledgeItem) -> bool:
        """
        Store a knowledge item in the repository.
        
        Args:
            knowledge_item: Knowledge item to store
            
        Returns:
            success: Whether the operation was successful
        """
        # Check if item already exists
        if knowledge_item.knowledge_id in self.knowledge_cache:
            existing_item = self.knowledge_cache[knowledge_item.knowledge_id]
            
            # Check if this is a newer version
            if knowledge_item.version <= existing_item.version:
                # Update version to be one higher than existing
                knowledge_item.version = existing_item.version + 1
        
        # Store in cache
        self.knowledge_cache[knowledge_item.knowledge_id] = knowledge_item
        
        # Update index
        self.knowledge_index["by_agent"][knowledge_item.source_agent_id].add(knowledge_item.knowledge_id)
        self.knowledge_index["by_type"][knowledge_item.knowledge_type].add(knowledge_item.knowledge_id)
        
        for tag in knowledge_item.tags:
            self.knowledge_index["by_tag"][tag].add(knowledge_item.knowledge_id)
        
        # Store to disk if path is provided
        if self.storage_path:
            try:
                self._save_knowledge_item(knowledge_item)
                return True
            except Exception as e:
                logger.error(f"Error saving knowledge item {knowledge_item.knowledge_id}: {e}")
                return False
        
        return True
    
    def _save_knowledge_item(self, knowledge_item: KnowledgeItem):
        """
        Save a knowledge item to disk.
        
        Args:
            knowledge_item: Knowledge item to save
        """
        # Create agent directory
        agent_dir = os.path.join(self.storage_path, knowledge_item.source_agent_id)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Create knowledge item file path
        knowledge_file = os.path.join(
            agent_dir, 
            f"{knowledge_item.knowledge_id}_v{knowledge_item.version}.json"
        )
        
        # Convert to dict
        knowledge_dict = {
            "knowledge_id": knowledge_item.knowledge_id,
            "source_agent_id": knowledge_item.source_agent_id,
            "knowledge_type": knowledge_item.knowledge_type,
            "content": knowledge_item.content,
            "metadata": knowledge_item.metadata,
            "confidence": knowledge_item.confidence,
            "timestamp": knowledge_item.timestamp,
            "version": knowledge_item.version,
            "tags": knowledge_item.tags
        }
        
        # Save to file
        with open(knowledge_file, 'w') as f:
            json.dump(knowledge_dict, f, indent=2)
    
    def get_knowledge(self, knowledge_id: str, version: int = None) -> Optional[KnowledgeItem]:
        """
        Get a knowledge item from the repository.
        
        Args:
            knowledge_id: ID of the knowledge item
            version: Specific version to retrieve (if None, latest version)
            
        Returns:
            knowledge_item: The retrieved knowledge item, or None if not found
        """
        # Check cache first
        if knowledge_id in self.knowledge_cache and (version is None or version == self.knowledge_cache[knowledge_id].version):
            return self.knowledge_cache[knowledge_id]
            
        # If specific version requested or not in cache, check disk
        if self.storage_path:
            try:
                return self._load_knowledge_item(knowledge_id, version)
            except Exception as e:
                logger.error(f"Error loading knowledge item {knowledge_id}: {e}")
                
        return None
    
    def _load_knowledge_item(self, knowledge_id: str, version: int = None) -> Optional[KnowledgeItem]:
        """
        Load a knowledge item from disk.
        
        Args:
            knowledge_id: ID of the knowledge item
            version: Specific version to load (if None, latest version)
            
        Returns:
            knowledge_item: The loaded knowledge item, or None if not found
        """
        # Find all matching files
        matching_files = []
        
        for agent_dir in os.listdir(self.storage_path):
            agent_path = os.path.join(self.storage_path, agent_dir)
            if not os.path.isdir(agent_path):
                continue
                
            for filename in os.listdir(agent_path):
                if filename.startswith(f"{knowledge_id}_v") and filename.endswith(".json"):
                    file_path = os.path.join(agent_path, filename)
                    file_version = int(filename.split("_v")[1].split(".json")[0])
                    
                    matching_files.append((file_path, file_version))
        
        if not matching_files:
            return None
            
        # Sort by version
        matching_files.sort(key=lambda x: x[1], reverse=True)
        
        # Get the requested version or latest
        if version is not None:
            for file_path, file_version in matching_files:
                if file_version == version:
                    break
            else:
                return None
        else:
            file_path, file_version = matching_files[0]
        
        # Load from file
        with open(file_path, 'r') as f:
            knowledge_dict = json.load(f)
            
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_dict["knowledge_id"],
            source_agent_id=knowledge_dict["source_agent_id"],
            knowledge_type=knowledge_dict["knowledge_type"],
            content=knowledge_dict["content"],
            metadata=knowledge_dict["metadata"],
            confidence=knowledge_dict["confidence"],
            timestamp=knowledge_dict["timestamp"],
            version=knowledge_dict["version"],
            tags=knowledge_dict["tags"]
        )
        
        # Update cache
        self.knowledge_cache[knowledge_id] = knowledge_item
        
        # Update index
        self.knowledge_index["by_agent"][knowledge_item.source_agent_id].add(knowledge_item.knowledge_id)
        self.knowledge_index["by_type"][knowledge_item.knowledge_type].add(knowledge_item.knowledge_id)
        
        for tag in knowledge_item.tags:
            self.knowledge_index["by_tag"][tag].add(knowledge_item.knowledge_id)
        
        return knowledge_item
    
    def search_knowledge(self, 
                        agent_id: str = None,
                        knowledge_type: str = None,
                        tags: List[str] = None,
                        query: str = None,
                        min_confidence: float = 0.0,
                        limit: int = 100) -> List[KnowledgeItem]:
        """
        Search for knowledge items in the repository.
        
        Args:
            agent_id: Filter by source agent ID
            knowledge_type: Filter by knowledge type
            tags: Filter by tags (items must have all specified tags)
            query: Text query to search in content
            min_confidence: Minimum confidence level
            limit: Maximum number of items to return
            
        Returns:
            knowledge_items: List of matching knowledge items
        """
        # Start with all knowledge IDs
        matching_ids = set(self.knowledge_cache.keys())
        
        # Apply filters
        if agent_id:
            agent_ids = self.knowledge_index["by_agent"].get(agent_id, set())
            matching_ids = matching_ids.intersection(agent_ids)
            
        if knowledge_type:
            type_ids = self.knowledge_index["by_type"].get(knowledge_type, set())
            matching_ids = matching_ids.intersection(type_ids)
            
        if tags:
            for tag in tags:
                tag_ids = self.knowledge_index["by_tag"].get(tag, set())
                matching_ids = matching_ids.intersection(tag_ids)
        
        # Get matching items
        matching_items = []
        
        for knowledge_id in matching_ids:
            item = self.knowledge_cache[knowledge_id]
            
            # Apply confidence filter
            if item.confidence < min_confidence:
                continue
                
            # Apply text query filter
            if query and not self._matches_query(item, query):
                continue
                
            matching_items.append(item)
            
            if len(matching_items) >= limit:
                break
        
        # If we don't have enough items and storage path is provided, search disk
        if len(matching_items) < limit and self.storage_path:
            # This is a simplified implementation
            # In a real system, we would use a proper search index
            
            # Load all items from disk
            for agent_dir in os.listdir(self.storage_path):
                agent_path = os.path.join(self.storage_path, agent_dir)
                if not os.path.isdir(agent_path):
                    continue
                    
                # Skip if agent filter is applied and doesn't match
                if agent_id and agent_dir != agent_id:
                    continue
                    
                for filename in os.listdir(agent_path):
                    if not filename.endswith(".json"):
                        continue
                        
                    # Extract knowledge ID and version
                    parts = filename.split("_v")
                    if len(parts) != 2:
                        continue
                        
                    knowledge_id = parts[0]
                    version = int(parts[1].split(".json")[0])
                    
                    # Skip if already in results
                    if any(item.knowledge_id == knowledge_id for item in matching_items):
                        continue
                        
                    # Load item
                    item = self._load_knowledge_item(knowledge_id, version)
                    if not item:
                        continue
                        
                    # Apply filters
                    if knowledge_type and item.knowledge_type != knowledge_type:
                        continue
                        
                    if tags and not all(tag in item.tags for tag in tags):
                        continue
                        
                    if item.confidence < min_confidence:
                        continue
                        
                    if query and not self._matches_query(item, query):
                        continue
                        
                    matching_items.append(item)
                    
                    if len(matching_items) >= limit:
                        break
                
                if len(matching_items) >= limit:
                    break
        
        # Sort by timestamp (newest first)
        matching_items.sort(key=lambda x: x.timestamp, reverse=True)
        
        return matching_items[:limit]
    
    def _matches_query(self, item: KnowledgeItem, query: str) -> bool:
        """
        Check if a knowledge item matches a text query.
        
        Args:
            item: Knowledge item to check
            query: Text query
            
        Returns:
            matches: Whether the item matches the query
        """
        # Convert query to lowercase for case-insensitive matching
        query = query.lower()
        
        # Check in content
        content_str = json.dumps(item.content).lower()
        if query in content_str:
            return True
            
        # Check in metadata
        metadata_str = json.dumps(item.metadata).lower()
        if query in metadata_str:
            return True
            
        # Check in tags
        for tag in item.tags:
            if query in tag.lower():
                return True
                
        return False
    
    def get_knowledge_versions(self, knowledge_id: str) -> List[int]:
        """
        Get all versions of a knowledge item.
        
        Args:
            knowledge_id: ID of the knowledge item
            
        Returns:
            versions: List of available versions
        """
        versions = []
        
        # Check disk
        if self.storage_path:
            for agent_dir in os.listdir(self.storage_path):
                agent_path = os.path.join(self.storage_path, agent_dir)
                if not os.path.isdir(agent_path):
                    continue
                    
                for filename in os.listdir(agent_path):
                    if filename.startswith(f"{knowledge_id}_v") and filename.endswith(".json"):
                        version = int(filename.split("_v")[1].split(".json")[0])
                        versions.append(version)
        
        # Check cache
        if knowledge_id in self.knowledge_cache:
            versions.append(self.knowledge_cache[knowledge_id].version)
            
        # Remove duplicates and sort
        versions = sorted(set(versions))
        
        return versions
    
    def delete_knowledge(self, knowledge_id: str, version: int = None) -> bool:
        """
        Delete a knowledge item from the repository.
        
        Args:
            knowledge_id: ID of the knowledge item
            version: Specific version to delete (if None, all versions)
            
        Returns:
            success: Whether the operation was successful
        """
        success = True
        
        # Delete from cache
        if knowledge_id in self.knowledge_cache:
            if version is None or version == self.knowledge_cache[knowledge_id].version:
                item = self.knowledge_cache[knowledge_id]
                
                # Remove from index
                self.knowledge_index["by_agent"][item.source_agent_id].discard(knowledge_id)
                self.knowledge_index["by_type"][item.knowledge_type].discard(knowledge_id)
                
                for tag in item.tags:
                    self.knowledge_index["by_tag"][tag].discard(knowledge_id)
                
                # Remove from cache
                del self.knowledge_cache[knowledge_id]
        
        # Delete from disk
        if self.storage_path:
            try:
                for agent_dir in os.listdir(self.storage_path):
                    agent_path = os.path.join(self.storage_path, agent_dir)
                    if not os.path.isdir(agent_path):
                        continue
                        
                    for filename in os.listdir(agent_path):
                        if filename.startswith(f"{knowledge_id}_v") and filename.endswith(".json"):
                            if version is None:
                                # Delete all versions
                                os.remove(os.path.join(agent_path, filename))
                            else:
                                # Delete specific version
                                file_version = int(filename.split("_v")[1].split(".json")[0])
                                if file_version == version:
                                    os.remove(os.path.join(agent_path, filename))
            except Exception as e:
                logger.error(f"Error deleting knowledge item {knowledge_id}: {e}")
                success = False
        
        return success


class KnowledgeTransferManager:
    """
    Manager for knowledge transfer between agents.
    
    This class provides methods for transferring knowledge between agents,
    including push, pull, and broadcast operations.
    """
    
    def __init__(self, repository: KnowledgeRepository, storage_path: str = None):
        """
        Initialize the KnowledgeTransferManager.
        
        Args:
            repository: Knowledge repository
            storage_path: Path to store transfer events
        """
        self.repository = repository
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # In-memory cache of transfer events
        self.transfer_events = {}
        
        # Agent compatibility matrix
        self.compatibility_matrix = {}
        
        # Transfer policies
        self.transfer_policies = {}
    
    def push_knowledge(self, 
                      source_agent_id: str,
                      target_agent_id: str,
                      knowledge_ids: List[str],
                      metadata: Dict[str, Any] = None) -> KnowledgeTransferEvent:
        """
        Push knowledge from source agent to target agent.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            knowledge_ids: IDs of knowledge items to transfer
            metadata: Additional metadata for the transfer event
            
        Returns:
            transfer_event: The created transfer event
        """
        # Create transfer event
        event_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        transfer_event = KnowledgeTransferEvent(
            event_id=event_id,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            knowledge_ids=knowledge_ids,
            transfer_type="push",
            status="pending",
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        # Store event
        self.transfer_events[event_id] = transfer_event
        
        if self.storage_path:
            self._save_transfer_event(transfer_event)
        
        # Process transfer
        success = self._process_transfer(transfer_event)
        
        # Update status
        transfer_event.status = "completed" if success else "failed"
        
        if self.storage_path:
            self._save_transfer_event(transfer_event)
        
        return transfer_event
    
    def pull_knowledge(self, 
                      target_agent_id: str,
                      source_agent_id: str,
                      query: Dict[str, Any],
                      metadata: Dict[str, Any] = None) -> KnowledgeTransferEvent:
        """
        Pull knowledge from source agent to target agent based on query.
        
        Args:
            target_agent_id: ID of the target agent
            source_agent_id: ID of the source agent
            query: Query parameters for knowledge search
            metadata: Additional metadata for the transfer event
            
        Returns:
            transfer_event: The created transfer event
        """
        # Search for matching knowledge items
        knowledge_items = self.repository.search_knowledge(
            agent_id=source_agent_id,
            knowledge_type=query.get("knowledge_type"),
            tags=query.get("tags"),
            query=query.get("text_query"),
            min_confidence=query.get("min_confidence", 0.0),
            limit=query.get("limit", 100)
        )
        
        # Extract knowledge IDs
        knowledge_ids = [item.knowledge_id for item in knowledge_items]
        
        # Create transfer event
        event_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        transfer_event = KnowledgeTransferEvent(
            event_id=event_id,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            knowledge_ids=knowledge_ids,
            transfer_type="pull",
            status="pending",
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        # Store event
        self.transfer_events[event_id] = transfer_event
        
        if self.storage_path:
            self._save_transfer_event(transfer_event)
        
        # Process transfer
        success = self._process_transfer(transfer_event)
        
        # Update status
        transfer_event.status = "completed" if success else "failed"
        
        if self.storage_path:
            self._save_transfer_event(transfer_event)
        
        return transfer_event
    
    def broadcast_knowledge(self, 
                           source_agent_id: str,
                           target_agent_ids: List[str],
                           knowledge_ids: List[str],
                           metadata: Dict[str, Any] = None) -> List[KnowledgeTransferEvent]:
        """
        Broadcast knowledge from source agent to multiple target agents.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_ids: IDs of the target agents
            knowledge_ids: IDs of knowledge items to transfer
            metadata: Additional metadata for the transfer events
            
        Returns:
            transfer_events: List of created transfer events
        """
        transfer_events = []
        
        for target_agent_id in target_agent_ids:
            # Create transfer event
            event_id = str(uuid.uuid4())
            timestamp = datetime.datetime.now().isoformat()
            
            transfer_event = KnowledgeTransferEvent(
                event_id=event_id,
                source_agent_id=source_agent_id,
                target_agent_id=target_agent_id,
                knowledge_ids=knowledge_ids,
                transfer_type="broadcast",
                status="pending",
                timestamp=timestamp,
                metadata=metadata or {}
            )
            
            # Store event
            self.transfer_events[event_id] = transfer_event
            
            if self.storage_path:
                self._save_transfer_event(transfer_event)
            
            # Process transfer
            success = self._process_transfer(transfer_event)
            
            # Update status
            transfer_event.status = "completed" if success else "failed"
            
            if self.storage_path:
                self._save_transfer_event(transfer_event)
            
            transfer_events.append(transfer_event)
        
        return transfer_events
    
    def _process_transfer(self, transfer_event: KnowledgeTransferEvent) -> bool:
        """
        Process a knowledge transfer event.
        
        Args:
            transfer_event: Transfer event to process
            
        Returns:
            success: Whether the transfer was successful
        """
        # Check compatibility
        if not self._check_compatibility(transfer_event.source_agent_id, transfer_event.target_agent_id):
            logger.warning(f"Incompatible agents: {transfer_event.source_agent_id} -> {transfer_event.target_agent_id}")
            return False
            
        # Check transfer policy
        if not self._check_policy(transfer_event):
            logger.warning(f"Transfer policy rejected: {transfer_event.event_id}")
            return False
            
        # Process each knowledge item
        success = True
        
        for knowledge_id in transfer_event.knowledge_ids:
            # Get knowledge item
            knowledge_item = self.repository.get_knowledge(knowledge_id)
            
            if not knowledge_item:
                logger.warning(f"Knowledge item not found: {knowledge_id}")
                success = False
                continue
                
            # Create adapted copy for target agent
            adapted_item = self._adapt_knowledge(knowledge_item, transfer_event.target_agent_id)
            
            # Store adapted item
            if not self.repository.store_knowledge(adapted_item):
                logger.warning(f"Failed to store adapted knowledge item: {adapted_item.knowledge_id}")
                success = False
        
        return success
    
    def _check_compatibility(self, source_agent_id: str, target_agent_id: str) -> bool:
        """
        Check if two agents are compatible for knowledge transfer.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            
        Returns:
            compatible: Whether the agents are compatible
        """
        # Check compatibility matrix
        key = (source_agent_id, target_agent_id)
        
        if key in self.compatibility_matrix:
            return self.compatibility_matrix[key]
            
        # Default to compatible
        return True
    
    def _check_policy(self, transfer_event: KnowledgeTransferEvent) -> bool:
        """
        Check if a transfer event complies with transfer policies.
        
        Args:
            transfer_event: Transfer event to check
            
        Returns:
            compliant: Whether the transfer complies with policies
        """
        # Check source agent policy
        source_policy = self.transfer_policies.get(transfer_event.source_agent_id)
        if source_policy and not source_policy.check_outgoing(transfer_event):
            return False
            
        # Check target agent policy
        target_policy = self.transfer_policies.get(transfer_event.target_agent_id)
        if target_policy and not target_policy.check_incoming(transfer_event):
            return False
            
        # Check global policy
        global_policy = self.transfer_policies.get("global")
        if global_policy and not global_policy.check_transfer(transfer_event):
            return False
            
        return True
    
    def _adapt_knowledge(self, knowledge_item: KnowledgeItem, target_agent_id: str) -> KnowledgeItem:
        """
        Adapt a knowledge item for a target agent.
        
        Args:
            knowledge_item: Knowledge item to adapt
            target_agent_id: ID of the target agent
            
        Returns:
            adapted_item: Adapted knowledge item
        """
        # Create a copy with new ID
        adapted_id = f"{knowledge_item.knowledge_id}_adapted_{target_agent_id}"
        
        adapted_item = KnowledgeItem(
            knowledge_id=adapted_id,
            source_agent_id=target_agent_id,  # Change source to target
            knowledge_type=knowledge_item.knowledge_type,
            content=knowledge_item.content.copy(),  # Deep copy content
            metadata={
                **knowledge_item.metadata.copy(),  # Copy original metadata
                "adapted_from": knowledge_item.knowledge_id,
                "original_source": knowledge_item.source_agent_id
            },
            confidence=knowledge_item.confidence * 0.9,  # Slightly reduce confidence
            timestamp=datetime.datetime.now().isoformat(),
            version=1,  # Start with version 1
            tags=knowledge_item.tags.copy()  # Copy tags
        )
        
        return adapted_item
    
    def _save_transfer_event(self, transfer_event: KnowledgeTransferEvent):
        """
        Save a transfer event to disk.
        
        Args:
            transfer_event: Transfer event to save
        """
        # Create events directory
        events_dir = os.path.join(self.storage_path, "events")
        os.makedirs(events_dir, exist_ok=True)
        
        # Create event file path
        event_file = os.path.join(events_dir, f"{transfer_event.event_id}.json")
        
        # Convert to dict
        event_dict = {
            "event_id": transfer_event.event_id,
            "source_agent_id": transfer_event.source_agent_id,
            "target_agent_id": transfer_event.target_agent_id,
            "knowledge_ids": transfer_event.knowledge_ids,
            "transfer_type": transfer_event.transfer_type,
            "status": transfer_event.status,
            "timestamp": transfer_event.timestamp,
            "metadata": transfer_event.metadata
        }
        
        # Save to file
        with open(event_file, 'w') as f:
            json.dump(event_dict, f, indent=2)
    
    def get_transfer_event(self, event_id: str) -> Optional[KnowledgeTransferEvent]:
        """
        Get a transfer event by ID.
        
        Args:
            event_id: ID of the transfer event
            
        Returns:
            transfer_event: The retrieved transfer event, or None if not found
        """
        # Check cache first
        if event_id in self.transfer_events:
            return self.transfer_events[event_id]
            
        # Check disk
        if self.storage_path:
            event_file = os.path.join(self.storage_path, "events", f"{event_id}.json")
            
            if os.path.exists(event_file):
                try:
                    with open(event_file, 'r') as f:
                        event_dict = json.load(f)
                        
                    # Create transfer event
                    transfer_event = KnowledgeTransferEvent(
                        event_id=event_dict["event_id"],
                        source_agent_id=event_dict["source_agent_id"],
                        target_agent_id=event_dict["target_agent_id"],
                        knowledge_ids=event_dict["knowledge_ids"],
                        transfer_type=event_dict["transfer_type"],
                        status=event_dict["status"],
                        timestamp=event_dict["timestamp"],
                        metadata=event_dict["metadata"]
                    )
                    
                    # Update cache
                    self.transfer_events[event_id] = transfer_event
                    
                    return transfer_event
                    
                except Exception as e:
                    logger.error(f"Error loading transfer event {event_id}: {e}")
        
        return None
    
    def get_agent_transfers(self, 
                           agent_id: str, 
                           role: str = "any",
                           limit: int = 100) -> List[KnowledgeTransferEvent]:
        """
        Get transfer events involving an agent.
        
        Args:
            agent_id: ID of the agent
            role: Role of the agent ("source", "target", or "any")
            limit: Maximum number of events to return
            
        Returns:
            transfer_events: List of transfer events
        """
        events = []
        
        # Check cache
        for event in self.transfer_events.values():
            if (role == "source" or role == "any") and event.source_agent_id == agent_id:
                events.append(event)
            elif (role == "target" or role == "any") and event.target_agent_id == agent_id:
                events.append(event)
                
            if len(events) >= limit:
                break
        
        # Check disk if needed
        if len(events) < limit and self.storage_path:
            events_dir = os.path.join(self.storage_path, "events")
            
            if os.path.exists(events_dir):
                for filename in os.listdir(events_dir):
                    if not filename.endswith(".json"):
                        continue
                        
                    event_id = filename.split(".json")[0]
                    
                    # Skip if already in results
                    if any(event.event_id == event_id for event in events):
                        continue
                        
                    # Load event
                    event = self.get_transfer_event(event_id)
                    
                    if not event:
                        continue
                        
                    # Check role
                    if (role == "source" or role == "any") and event.source_agent_id == agent_id:
                        events.append(event)
                    elif (role == "target" or role == "any") and event.target_agent_id == agent_id:
                        events.append(event)
                        
                    if len(events) >= limit:
                        break
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    def set_agent_compatibility(self, source_agent_id: str, target_agent_id: str, compatible: bool):
        """
        Set compatibility between two agents.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            compatible: Whether the agents are compatible
        """
        self.compatibility_matrix[(source_agent_id, target_agent_id)] = compatible
    
    def register_transfer_policy(self, agent_id: str, policy):
        """
        Register a transfer policy for an agent.
        
        Args:
            agent_id: ID of the agent, or "global" for global policy
            policy: Transfer policy object
        """
        self.transfer_policies[agent_id] = policy


class TransferPolicy:
    """
    Policy for controlling knowledge transfer between agents.
    
    This class defines rules for allowing or blocking knowledge transfers
    based on various criteria.
    """
    
    def __init__(self, 
                allowed_sources: Set[str] = None,
                allowed_targets: Set[str] = None,
                allowed_types: Set[str] = None,
                blocked_sources: Set[str] = None,
                blocked_targets: Set[str] = None,
                blocked_types: Set[str] = None,
                min_confidence: float = 0.0):
        """
        Initialize the TransferPolicy.
        
        Args:
            allowed_sources: Set of allowed source agent IDs
            allowed_targets: Set of allowed target agent IDs
            allowed_types: Set of allowed knowledge types
            blocked_sources: Set of blocked source agent IDs
            blocked_targets: Set of blocked target agent IDs
            blocked_types: Set of blocked knowledge types
            min_confidence: Minimum confidence level for transfers
        """
        self.allowed_sources = allowed_sources or set()
        self.allowed_targets = allowed_targets or set()
        self.allowed_types = allowed_types or set()
        self.blocked_sources = blocked_sources or set()
        self.blocked_targets = blocked_targets or set()
        self.blocked_types = blocked_types or set()
        self.min_confidence = min_confidence
    
    def check_outgoing(self, transfer_event: KnowledgeTransferEvent) -> bool:
        """
        Check if an outgoing transfer is allowed.
        
        Args:
            transfer_event: Transfer event to check
            
        Returns:
            allowed: Whether the transfer is allowed
        """
        # Check blocked target
        if transfer_event.target_agent_id in self.blocked_targets:
            return False
            
        # Check allowed target
        if self.allowed_targets and transfer_event.target_agent_id not in self.allowed_targets:
            return False
            
        return True
    
    def check_incoming(self, transfer_event: KnowledgeTransferEvent) -> bool:
        """
        Check if an incoming transfer is allowed.
        
        Args:
            transfer_event: Transfer event to check
            
        Returns:
            allowed: Whether the transfer is allowed
        """
        # Check blocked source
        if transfer_event.source_agent_id in self.blocked_sources:
            return False
            
        # Check allowed source
        if self.allowed_sources and transfer_event.source_agent_id not in self.allowed_sources:
            return False
            
        return True
    
    def check_transfer(self, transfer_event: KnowledgeTransferEvent) -> bool:
        """
        Check if a transfer is allowed.
        
        Args:
            transfer_event: Transfer event to check
            
        Returns:
            allowed: Whether the transfer is allowed
        """
        # Check source and target
        if not self.check_outgoing(transfer_event) or not self.check_incoming(transfer_event):
            return False
            
        return True


class KnowledgeGraph:
    """
    Graph representation of knowledge and its relationships.
    
    This class provides methods for building, querying, and visualizing
    a graph of knowledge items and their relationships.
    """
    
    def __init__(self, repository: KnowledgeRepository):
        """
        Initialize the KnowledgeGraph.
        
        Args:
            repository: Knowledge repository
        """
        self.repository = repository
        self.graph = nx.DiGraph()
    
    def build_graph(self, 
                   agent_ids: List[str] = None,
                   knowledge_types: List[str] = None,
                   tags: List[str] = None,
                   min_confidence: float = 0.0):
        """
        Build the knowledge graph.
        
        Args:
            agent_ids: Filter by agent IDs
            knowledge_types: Filter by knowledge types
            tags: Filter by tags
            min_confidence: Minimum confidence level
        """
        # Clear existing graph
        self.graph.clear()
        
        # Get knowledge items
        if agent_ids:
            # Get items for each agent
            items = []
            for agent_id in agent_ids:
                agent_items = self.repository.search_knowledge(
                    agent_id=agent_id,
                    knowledge_type=knowledge_types[0] if knowledge_types else None,
                    tags=tags,
                    min_confidence=min_confidence,
                    limit=1000
                )
                items.extend(agent_items)
        else:
            # Get all items
            items = []
            for knowledge_type in knowledge_types or [None]:
                type_items = self.repository.search_knowledge(
                    knowledge_type=knowledge_type,
                    tags=tags,
                    min_confidence=min_confidence,
                    limit=1000
                )
                items.extend(type_items)
        
        # Add nodes for knowledge items
        for item in items:
            self.graph.add_node(
                item.knowledge_id,
                type="knowledge",
                knowledge_type=item.knowledge_type,
                agent_id=item.source_agent_id,
                confidence=item.confidence,
                timestamp=item.timestamp,
                tags=item.tags
            )
            
            # Add node for agent
            self.graph.add_node(
                item.source_agent_id,
                type="agent"
            )
            
            # Add edge from agent to knowledge
            self.graph.add_edge(
                item.source_agent_id,
                item.knowledge_id,
                type="created"
            )
            
            # Add edges for relationships
            if "related_to" in item.metadata:
                for related_id in item.metadata["related_to"]:
                    self.graph.add_edge(
                        item.knowledge_id,
                        related_id,
                        type="related"
                    )
            
            # Add edges for adaptations
            if "adapted_from" in item.metadata:
                original_id = item.metadata["adapted_from"]
                self.graph.add_edge(
                    original_id,
                    item.knowledge_id,
                    type="adapted"
                )
    
    def get_related_knowledge(self, knowledge_id: str, max_depth: int = 2) -> List[str]:
        """
        Get related knowledge items.
        
        Args:
            knowledge_id: ID of the knowledge item
            max_depth: Maximum depth to search
            
        Returns:
            related_ids: IDs of related knowledge items
        """
        if knowledge_id not in self.graph:
            return []
            
        # Get subgraph within max_depth
        related_nodes = set()
        current_nodes = {knowledge_id}
        
        for _ in range(max_depth):
            next_nodes = set()
            
            for node in current_nodes:
                # Get neighbors
                neighbors = set(self.graph.successors(node)) | set(self.graph.predecessors(node))
                
                # Filter to knowledge nodes
                knowledge_neighbors = {n for n in neighbors if self.graph.nodes[n].get("type") == "knowledge"}
                
                next_nodes |= knowledge_neighbors
            
            related_nodes |= next_nodes
            current_nodes = next_nodes
        
        # Remove the original node
        related_nodes.discard(knowledge_id)
        
        return list(related_nodes)
    
    def get_agent_knowledge(self, agent_id: str) -> List[str]:
        """
        Get knowledge items created by an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            knowledge_ids: IDs of knowledge items
        """
        if agent_id not in self.graph:
            return []
            
        # Get successors (knowledge created by agent)
        knowledge_nodes = [n for n in self.graph.successors(agent_id) 
                          if self.graph.nodes[n].get("type") == "knowledge"]
        
        return knowledge_nodes
    
    def get_knowledge_path(self, source_id: str, target_id: str) -> List[str]:
        """
        Get path between two knowledge items.
        
        Args:
            source_id: ID of the source knowledge item
            target_id: ID of the target knowledge item
            
        Returns:
            path: List of knowledge item IDs in the path
        """
        if source_id not in self.graph or target_id not in self.graph:
            return []
            
        try:
            # Find shortest path
            path = nx.shortest_path(self.graph, source_id, target_id)
            
            # Filter to knowledge nodes
            knowledge_path = [n for n in path if self.graph.nodes[n].get("type") == "knowledge"]
            
            return knowledge_path
            
        except nx.NetworkXNoPath:
            return []
    
    def visualize(self, highlight_nodes: List[str] = None) -> str:
        """
        Visualize the knowledge graph.
        
        Args:
            highlight_nodes: Nodes to highlight
            
        Returns:
            image_data: Base64-encoded PNG image
        """
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Get node positions
        pos = nx.spring_layout(self.graph)
        
        # Get node types
        agent_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get("type") == "agent"]
        knowledge_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get("type") == "knowledge"]
        
        # Get edge types
        created_edges = [(u, v) for u, v, attr in self.graph.edges(data=True) if attr.get("type") == "created"]
        related_edges = [(u, v) for u, v, attr in self.graph.edges(data=True) if attr.get("type") == "related"]
        adapted_edges = [(u, v) for u, v, attr in self.graph.edges(data=True) if attr.get("type") == "adapted"]
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, nodelist=agent_nodes, node_color="skyblue", node_size=500, alpha=0.8)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=knowledge_nodes, node_color="lightgreen", node_size=300, alpha=0.8)
        
        # Highlight nodes
        if highlight_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=highlight_nodes, node_color="red", node_size=400, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, edgelist=created_edges, edge_color="gray", arrows=True)
        nx.draw_networkx_edges(self.graph, pos, edgelist=related_edges, edge_color="blue", style="dashed", arrows=True)
        nx.draw_networkx_edges(self.graph, pos, edgelist=adapted_edges, edge_color="green", arrows=True)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8)
        
        # Add legend
        plt.legend(["Agents", "Knowledge", "Highlighted", "Created", "Related", "Adapted"], loc="upper right")
        
        # Remove axis
        plt.axis("off")
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode("utf-8")
        
        return image_data


class KnowledgeCreator:
    """
    Creator for knowledge items.
    
    This class provides methods for creating different types of knowledge items
    from various sources.
    """
    
    def __init__(self, repository: KnowledgeRepository):
        """
        Initialize the KnowledgeCreator.
        
        Args:
            repository: Knowledge repository
        """
        self.repository = repository
    
    def create_concept(self, 
                      agent_id: str,
                      concept_name: str,
                      description: str,
                      attributes: Dict[str, Any] = None,
                      examples: List[Dict[str, Any]] = None,
                      related_concepts: List[str] = None,
                      confidence: float = 1.0,
                      tags: List[str] = None) -> KnowledgeItem:
        """
        Create a concept knowledge item.
        
        Args:
            agent_id: ID of the creating agent
            concept_name: Name of the concept
            description: Description of the concept
            attributes: Attributes of the concept
            examples: Examples of the concept
            related_concepts: Related concept names
            confidence: Confidence level
            tags: Tags for the concept
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Generate ID
        knowledge_id = self._generate_id("concept", concept_name)
        
        # Create content
        content = {
            "name": concept_name,
            "description": description,
            "attributes": attributes or {},
            "examples": examples or []
        }
        
        # Create metadata
        metadata = {}
        
        if related_concepts:
            metadata["related_concepts"] = related_concepts
            
            # Try to find related concept IDs
            related_ids = []
            for concept in related_concepts:
                # Search for concept
                items = self.repository.search_knowledge(
                    knowledge_type="concept",
                    query=concept,
                    limit=1
                )
                
                if items:
                    related_ids.append(items[0].knowledge_id)
            
            if related_ids:
                metadata["related_to"] = related_ids
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            source_agent_id=agent_id,
            knowledge_type="concept",
            content=content,
            metadata=metadata,
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            version=1,
            tags=tags or []
        )
        
        # Store in repository
        self.repository.store_knowledge(knowledge_item)
        
        return knowledge_item
    
    def create_rule(self, 
                   agent_id: str,
                   rule_name: str,
                   conditions: List[Dict[str, Any]],
                   actions: List[Dict[str, Any]],
                   description: str = None,
                   context: Dict[str, Any] = None,
                   confidence: float = 1.0,
                   tags: List[str] = None) -> KnowledgeItem:
        """
        Create a rule knowledge item.
        
        Args:
            agent_id: ID of the creating agent
            rule_name: Name of the rule
            conditions: Conditions for the rule
            actions: Actions for the rule
            description: Description of the rule
            context: Context for the rule
            confidence: Confidence level
            tags: Tags for the rule
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Generate ID
        knowledge_id = self._generate_id("rule", rule_name)
        
        # Create content
        content = {
            "name": rule_name,
            "description": description or f"Rule: {rule_name}",
            "conditions": conditions,
            "actions": actions,
            "context": context or {}
        }
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            source_agent_id=agent_id,
            knowledge_type="rule",
            content=content,
            metadata={},
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            version=1,
            tags=tags or []
        )
        
        # Store in repository
        self.repository.store_knowledge(knowledge_item)
        
        return knowledge_item
    
    def create_preference(self, 
                         agent_id: str,
                         preference_type: str,
                         preference_value: Any,
                         context: Dict[str, Any] = None,
                         description: str = None,
                         confidence: float = 1.0,
                         tags: List[str] = None) -> KnowledgeItem:
        """
        Create a preference knowledge item.
        
        Args:
            agent_id: ID of the creating agent
            preference_type: Type of preference
            preference_value: Value of the preference
            context: Context for the preference
            description: Description of the preference
            confidence: Confidence level
            tags: Tags for the preference
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Generate ID
        knowledge_id = self._generate_id("preference", f"{preference_type}_{agent_id}")
        
        # Create content
        content = {
            "type": preference_type,
            "value": preference_value,
            "description": description or f"Preference: {preference_type}",
            "context": context or {}
        }
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            source_agent_id=agent_id,
            knowledge_type="preference",
            content=content,
            metadata={},
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            version=1,
            tags=tags or []
        )
        
        # Store in repository
        self.repository.store_knowledge(knowledge_item)
        
        return knowledge_item
    
    def create_skill(self, 
                    agent_id: str,
                    skill_name: str,
                    description: str,
                    parameters: List[Dict[str, Any]] = None,
                    examples: List[Dict[str, Any]] = None,
                    implementation: Dict[str, Any] = None,
                    confidence: float = 1.0,
                    tags: List[str] = None) -> KnowledgeItem:
        """
        Create a skill knowledge item.
        
        Args:
            agent_id: ID of the creating agent
            skill_name: Name of the skill
            description: Description of the skill
            parameters: Parameters for the skill
            examples: Examples of the skill
            implementation: Implementation details
            confidence: Confidence level
            tags: Tags for the skill
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Generate ID
        knowledge_id = self._generate_id("skill", skill_name)
        
        # Create content
        content = {
            "name": skill_name,
            "description": description,
            "parameters": parameters or [],
            "examples": examples or [],
            "implementation": implementation or {}
        }
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            source_agent_id=agent_id,
            knowledge_type="skill",
            content=content,
            metadata={},
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            version=1,
            tags=tags or []
        )
        
        # Store in repository
        self.repository.store_knowledge(knowledge_item)
        
        return knowledge_item
    
    def create_from_model(self, 
                         agent_id: str,
                         model_type: str,
                         model_data: Dict[str, Any],
                         description: str = None,
                         confidence: float = 1.0,
                         tags: List[str] = None) -> KnowledgeItem:
        """
        Create a knowledge item from a machine learning model.
        
        Args:
            agent_id: ID of the creating agent
            model_type: Type of model
            model_data: Model data
            description: Description of the model
            confidence: Confidence level
            tags: Tags for the model
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Generate ID
        knowledge_id = self._generate_id("model", f"{model_type}_{agent_id}")
        
        # Create content
        content = {
            "type": model_type,
            "description": description or f"Model: {model_type}",
            "data": model_data
        }
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            source_agent_id=agent_id,
            knowledge_type="model",
            content=content,
            metadata={},
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            version=1,
            tags=tags or []
        )
        
        # Store in repository
        self.repository.store_knowledge(knowledge_item)
        
        return knowledge_item
    
    def _generate_id(self, knowledge_type: str, name: str) -> str:
        """
        Generate a unique ID for a knowledge item.
        
        Args:
            knowledge_type: Type of knowledge
            name: Name or identifier
            
        Returns:
            knowledge_id: Generated ID
        """
        # Create base ID
        base_id = f"{knowledge_type}_{name.lower().replace(' ', '_')}"
        
        # Add hash for uniqueness
        hash_suffix = hashlib.md5(f"{base_id}_{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        return f"{base_id}_{hash_suffix}"


class KnowledgeTransferSystem:
    """
    Complete system for knowledge transfer between agents.
    
    This class integrates all components of the knowledge transfer system,
    providing a unified interface for knowledge management and transfer.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the KnowledgeTransferSystem.
        
        Args:
            storage_path: Path to store knowledge and transfer data
        """
        # Create storage directories
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            knowledge_path = os.path.join(storage_path, "knowledge")
            transfer_path = os.path.join(storage_path, "transfers")
            os.makedirs(knowledge_path, exist_ok=True)
            os.makedirs(transfer_path, exist_ok=True)
        else:
            knowledge_path = None
            transfer_path = None
        
        # Initialize components
        self.repository = KnowledgeRepository(storage_path=knowledge_path)
        self.transfer_manager = KnowledgeTransferManager(self.repository, storage_path=transfer_path)
        self.knowledge_creator = KnowledgeCreator(self.repository)
        self.knowledge_graph = KnowledgeGraph(self.repository)
        
        # Agent registry
        self.agents = {}
    
    def register_agent(self, 
                      agent_id: str,
                      agent_type: str,
                      capabilities: List[str] = None,
                      metadata: Dict[str, Any] = None):
        """
        Register an agent in the system.
        
        Args:
            agent_id: ID of the agent
            agent_type: Type of agent
            capabilities: List of agent capabilities
            metadata: Additional metadata
        """
        self.agents[agent_id] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
            "registered_at": datetime.datetime.now().isoformat()
        }
    
    def create_knowledge(self, 
                        agent_id: str,
                        knowledge_type: str,
                        content: Dict[str, Any],
                        metadata: Dict[str, Any] = None,
                        confidence: float = 1.0,
                        tags: List[str] = None) -> KnowledgeItem:
        """
        Create a generic knowledge item.
        
        Args:
            agent_id: ID of the creating agent
            knowledge_type: Type of knowledge
            content: Knowledge content
            metadata: Additional metadata
            confidence: Confidence level
            tags: Tags for the knowledge
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Check if agent is registered
        if agent_id not in self.agents:
            self.register_agent(agent_id, "unknown")
            
        # Generate ID
        knowledge_id = str(uuid.uuid4())
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            source_agent_id=agent_id,
            knowledge_type=knowledge_type,
            content=content,
            metadata=metadata or {},
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat(),
            version=1,
            tags=tags or []
        )
        
        # Store in repository
        self.repository.store_knowledge(knowledge_item)
        
        return knowledge_item
    
    def get_knowledge(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        """
        Get a knowledge item.
        
        Args:
            knowledge_id: ID of the knowledge item
            
        Returns:
            knowledge_item: The retrieved knowledge item
        """
        return self.repository.get_knowledge(knowledge_id)
    
    def search_knowledge(self, 
                        agent_id: str = None,
                        knowledge_type: str = None,
                        tags: List[str] = None,
                        query: str = None,
                        min_confidence: float = 0.0,
                        limit: int = 100) -> List[KnowledgeItem]:
        """
        Search for knowledge items.
        
        Args:
            agent_id: Filter by source agent ID
            knowledge_type: Filter by knowledge type
            tags: Filter by tags
            query: Text query to search in content
            min_confidence: Minimum confidence level
            limit: Maximum number of items to return
            
        Returns:
            knowledge_items: List of matching knowledge items
        """
        return self.repository.search_knowledge(
            agent_id=agent_id,
            knowledge_type=knowledge_type,
            tags=tags,
            query=query,
            min_confidence=min_confidence,
            limit=limit
        )
    
    def transfer_knowledge(self, 
                          source_agent_id: str,
                          target_agent_id: str,
                          knowledge_ids: List[str],
                          metadata: Dict[str, Any] = None) -> KnowledgeTransferEvent:
        """
        Transfer knowledge between agents.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            knowledge_ids: IDs of knowledge items to transfer
            metadata: Additional metadata
            
        Returns:
            transfer_event: The created transfer event
        """
        # Check if agents are registered
        if source_agent_id not in self.agents:
            self.register_agent(source_agent_id, "unknown")
            
        if target_agent_id not in self.agents:
            self.register_agent(target_agent_id, "unknown")
            
        # Transfer knowledge
        return self.transfer_manager.push_knowledge(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            knowledge_ids=knowledge_ids,
            metadata=metadata
        )
    
    def query_knowledge(self, 
                       target_agent_id: str,
                       source_agent_id: str,
                       query_params: Dict[str, Any],
                       metadata: Dict[str, Any] = None) -> KnowledgeTransferEvent:
        """
        Query and pull knowledge from another agent.
        
        Args:
            target_agent_id: ID of the target agent
            source_agent_id: ID of the source agent
            query_params: Query parameters
            metadata: Additional metadata
            
        Returns:
            transfer_event: The created transfer event
        """
        # Check if agents are registered
        if source_agent_id not in self.agents:
            self.register_agent(source_agent_id, "unknown")
            
        if target_agent_id not in self.agents:
            self.register_agent(target_agent_id, "unknown")
            
        # Pull knowledge
        return self.transfer_manager.pull_knowledge(
            target_agent_id=target_agent_id,
            source_agent_id=source_agent_id,
            query=query_params,
            metadata=metadata
        )
    
    def broadcast_knowledge(self, 
                           source_agent_id: str,
                           knowledge_ids: List[str],
                           target_agent_ids: List[str] = None,
                           metadata: Dict[str, Any] = None) -> List[KnowledgeTransferEvent]:
        """
        Broadcast knowledge to multiple agents.
        
        Args:
            source_agent_id: ID of the source agent
            knowledge_ids: IDs of knowledge items to broadcast
            target_agent_ids: IDs of target agents (if None, broadcast to all)
            metadata: Additional metadata
            
        Returns:
            transfer_events: List of created transfer events
        """
        # Check if source agent is registered
        if source_agent_id not in self.agents:
            self.register_agent(source_agent_id, "unknown")
            
        # If target_agent_ids is None, broadcast to all agents
        if target_agent_ids is None:
            target_agent_ids = [agent_id for agent_id in self.agents.keys() if agent_id != source_agent_id]
            
        # Register any unknown target agents
        for agent_id in target_agent_ids:
            if agent_id not in self.agents:
                self.register_agent(agent_id, "unknown")
                
        # Broadcast knowledge
        return self.transfer_manager.broadcast_knowledge(
            source_agent_id=source_agent_id,
            target_agent_ids=target_agent_ids,
            knowledge_ids=knowledge_ids,
            metadata=metadata
        )
    
    def visualize_knowledge_network(self, 
                                   agent_ids: List[str] = None,
                                   knowledge_types: List[str] = None,
                                   highlight_items: List[str] = None) -> str:
        """
        Visualize the knowledge network.
        
        Args:
            agent_ids: Filter by agent IDs
            knowledge_types: Filter by knowledge types
            highlight_items: Knowledge items to highlight
            
        Returns:
            image_data: Base64-encoded PNG image
        """
        # Build graph
        self.knowledge_graph.build_graph(
            agent_ids=agent_ids,
            knowledge_types=knowledge_types
        )
        
        # Visualize
        return self.knowledge_graph.visualize(highlight_nodes=highlight_items)
    
    def get_agent_knowledge(self, agent_id: str) -> List[KnowledgeItem]:
        """
        Get all knowledge items for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            knowledge_items: List of knowledge items
        """
        return self.repository.search_knowledge(agent_id=agent_id, limit=1000)
    
    def get_agent_transfers(self, 
                           agent_id: str, 
                           role: str = "any",
                           limit: int = 100) -> List[KnowledgeTransferEvent]:
        """
        Get transfer events involving an agent.
        
        Args:
            agent_id: ID of the agent
            role: Role of the agent ("source", "target", or "any")
            limit: Maximum number of events to return
            
        Returns:
            transfer_events: List of transfer events
        """
        return self.transfer_manager.get_agent_transfers(
            agent_id=agent_id,
            role=role,
            limit=limit
        )
    
    def get_related_knowledge(self, knowledge_id: str, max_depth: int = 2) -> List[KnowledgeItem]:
        """
        Get related knowledge items.
        
        Args:
            knowledge_id: ID of the knowledge item
            max_depth: Maximum depth to search
            
        Returns:
            related_items: List of related knowledge items
        """
        # Build graph if empty
        if not self.knowledge_graph.graph:
            self.knowledge_graph.build_graph()
            
        # Get related IDs
        related_ids = self.knowledge_graph.get_related_knowledge(knowledge_id, max_depth)
        
        # Get knowledge items
        related_items = []
        for related_id in related_ids:
            item = self.repository.get_knowledge(related_id)
            if item:
                related_items.append(item)
                
        return related_items
    
    def create_specialized_knowledge(self, 
                                    agent_id: str,
                                    knowledge_type: str,
                                    **kwargs) -> KnowledgeItem:
        """
        Create specialized knowledge using the appropriate creator method.
        
        Args:
            agent_id: ID of the creating agent
            knowledge_type: Type of knowledge
            **kwargs: Additional arguments for the creator method
            
        Returns:
            knowledge_item: The created knowledge item
        """
        # Check if agent is registered
        if agent_id not in self.agents:
            self.register_agent(agent_id, "unknown")
            
        # Call appropriate creator method
        if knowledge_type == "concept":
            return self.knowledge_creator.create_concept(agent_id=agent_id, **kwargs)
        elif knowledge_type == "rule":
            return self.knowledge_creator.create_rule(agent_id=agent_id, **kwargs)
        elif knowledge_type == "preference":
            return self.knowledge_creator.create_preference(agent_id=agent_id, **kwargs)
        elif knowledge_type == "skill":
            return self.knowledge_creator.create_skill(agent_id=agent_id, **kwargs)
        elif knowledge_type == "model":
            return self.knowledge_creator.create_from_model(agent_id=agent_id, **kwargs)
        else:
            # Generic knowledge
            return self.create_knowledge(
                agent_id=agent_id,
                knowledge_type=knowledge_type,
                content=kwargs.get("content", {}),
                metadata=kwargs.get("metadata", {}),
                confidence=kwargs.get("confidence", 1.0),
                tags=kwargs.get("tags", [])
            )
    
    def set_transfer_policy(self, 
                           agent_id: str,
                           allowed_sources: List[str] = None,
                           allowed_targets: List[str] = None,
                           blocked_sources: List[str] = None,
                           blocked_targets: List[str] = None,
                           min_confidence: float = 0.0):
        """
        Set transfer policy for an agent.
        
        Args:
            agent_id: ID of the agent
            allowed_sources: List of allowed source agent IDs
            allowed_targets: List of allowed target agent IDs
            blocked_sources: List of blocked source agent IDs
            blocked_targets: List of blocked target agent IDs
            min_confidence: Minimum confidence level for transfers
        """
        policy = TransferPolicy(
            allowed_sources=set(allowed_sources) if allowed_sources else None,
            allowed_targets=set(allowed_targets) if allowed_targets else None,
            blocked_sources=set(blocked_sources) if blocked_sources else None,
            blocked_targets=set(blocked_targets) if blocked_targets else None,
            min_confidence=min_confidence
        )
        
        self.transfer_manager.register_transfer_policy(agent_id, policy)
    
    def set_agent_compatibility(self, source_agent_id: str, target_agent_id: str, compatible: bool):
        """
        Set compatibility between two agents.
        
        Args:
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            compatible: Whether the agents are compatible
        """
        self.transfer_manager.set_agent_compatibility(source_agent_id, target_agent_id, compatible)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge transfer system.
        
        Returns:
            stats: System statistics
        """
        # Count knowledge items by type
        knowledge_by_type = defaultdict(int)
        for item in self.repository.knowledge_cache.values():
            knowledge_by_type[item.knowledge_type] += 1
            
        # Count knowledge items by agent
        knowledge_by_agent = defaultdict(int)
        for item in self.repository.knowledge_cache.values():
            knowledge_by_agent[item.source_agent_id] += 1
            
        # Count transfer events by type
        transfers_by_type = defaultdict(int)
        for event in self.transfer_manager.transfer_events.values():
            transfers_by_type[event.transfer_type] += 1
            
        # Count transfer events by status
        transfers_by_status = defaultdict(int)
        for event in self.transfer_manager.transfer_events.values():
            transfers_by_status[event.status] += 1
            
        return {
            "total_agents": len(self.agents),
            "total_knowledge_items": len(self.repository.knowledge_cache),
            "total_transfer_events": len(self.transfer_manager.transfer_events),
            "knowledge_by_type": dict(knowledge_by_type),
            "knowledge_by_agent": dict(knowledge_by_agent),
            "transfers_by_type": dict(transfers_by_type),
            "transfers_by_status": dict(transfers_by_status)
        }
