"""
Knowledge Transfer Integration Module for Lumina AI.

This module implements the integration between the Enhanced Learning System's
Knowledge Transfer Module and the Multi-Agent Collaboration System's Shared Memory.
"""

import os
import logging
import datetime
import json
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
import requests
from dataclasses import dataclass, field

# Import Enhanced Learning System components
from lumina_ai_monorepo.learning.transfer.knowledge_transfer import (
    KnowledgeTransferSystem,
    KnowledgeItem,
    KnowledgeRepository,
    TransferPolicy
)

# Import Multi-Agent Collaboration System components
from lumina_ai_monorepo.collaboration.shared_memory import (
    SharedMemory,
    MemoryItem,
    AccessPolicy
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeTransferConfig:
    """Configuration for knowledge transfer integration."""
    
    # General settings
    enabled: bool = True
    storage_path: str = "/tmp/lumina_knowledge_transfer"
    
    # Transfer settings
    default_transfer_method: str = "push"  # "push", "pull", or "broadcast"
    auto_transfer_enabled: bool = True
    transfer_batch_size: int = 10
    
    # Security settings
    encryption_enabled: bool = True
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True
    
    # Performance settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    compression_enabled: bool = True
    
    # Integration settings
    learning_system_api_url: str = "http://localhost:8080/api/learning"
    collaboration_system_api_url: str = "http://localhost:8081/api/collaboration"


class KnowledgeTransferIntegration:
    """
    Integration between Enhanced Learning System's Knowledge Transfer and
    Multi-Agent Collaboration System's Shared Memory.
    
    This class provides a unified interface for knowledge transfer between
    individual learning agents and collaborative agent teams.
    """
    
    def __init__(self, config: KnowledgeTransferConfig = None):
        """
        Initialize the Knowledge Transfer Integration.
        
        Args:
            config: Configuration for knowledge transfer integration
        """
        # Load configuration
        self.config = config or KnowledgeTransferConfig()
        
        # Create storage directory
        os.makedirs(self.config.storage_path, exist_ok=True)
        
        # Initialize components
        self.knowledge_transfer = KnowledgeTransferSystem(
            transfer_method=self.config.default_transfer_method,
            knowledge_retention=0.8  # Default value, can be configured
        )
        
        self.shared_memory = SharedMemory()
        
        # Initialize cache if enabled
        self.cache = {} if self.config.cache_enabled else None
        self.cache_timestamps = {} if self.config.cache_enabled else None
        
        # Initialize metrics
        self.metrics = {
            "transfers": 0,
            "transfer_failures": 0,
            "bytes_transferred": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "last_transfer_timestamp": None
        }
        
        logger.info("Knowledge Transfer Integration initialized")
    
    def transfer_knowledge_to_collaboration(self, 
                                           knowledge_item_id: str,
                                           agent_id: str,
                                           team_id: str,
                                           access_policy: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Transfer knowledge from an individual agent to a collaborative team.
        
        Args:
            knowledge_item_id: ID of the knowledge item to transfer
            agent_id: ID of the source agent
            team_id: ID of the target team
            access_policy: Access policy for the shared memory item
            
        Returns:
            result: Transfer result
        """
        try:
            # Get knowledge item from repository
            knowledge_item = self.knowledge_transfer.repository.get_item(knowledge_item_id)
            
            if knowledge_item is None:
                logger.error(f"Knowledge item {knowledge_item_id} not found")
                return {
                    "status": "error",
                    "message": f"Knowledge item {knowledge_item_id} not found",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Convert knowledge item to memory item
            memory_item = self._convert_knowledge_to_memory(
                knowledge_item, agent_id, team_id, access_policy
            )
            
            # Store in shared memory
            memory_result = self.shared_memory.store_item(memory_item)
            
            # Update metrics
            self.metrics["transfers"] += 1
            self.metrics["bytes_transferred"] += len(str(knowledge_item.content))
            self.metrics["last_transfer_timestamp"] = datetime.datetime.now().isoformat()
            
            # Log the transfer
            if self.config.audit_logging_enabled:
                self._log_transfer(
                    "to_collaboration",
                    knowledge_item_id,
                    agent_id,
                    team_id,
                    memory_result.get("item_id")
                )
            
            return {
                "status": "success",
                "source_id": knowledge_item_id,
                "target_id": memory_result.get("item_id"),
                "agent_id": agent_id,
                "team_id": team_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error transferring knowledge to collaboration: {e}")
            self.metrics["transfer_failures"] += 1
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def transfer_knowledge_from_collaboration(self,
                                             memory_item_id: str,
                                             team_id: str,
                                             agent_id: str,
                                             transfer_policy: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Transfer knowledge from a collaborative team to an individual agent.
        
        Args:
            memory_item_id: ID of the memory item to transfer
            team_id: ID of the source team
            agent_id: ID of the target agent
            transfer_policy: Transfer policy for the knowledge item
            
        Returns:
            result: Transfer result
        """
        try:
            # Get memory item from shared memory
            memory_item = self.shared_memory.get_item(memory_item_id)
            
            if memory_item is None:
                logger.error(f"Memory item {memory_item_id} not found")
                return {
                    "status": "error",
                    "message": f"Memory item {memory_item_id} not found",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Check access permission
            if not self._check_access_permission(memory_item, agent_id):
                logger.error(f"Agent {agent_id} does not have access to memory item {memory_item_id}")
                return {
                    "status": "error",
                    "message": f"Access denied for memory item {memory_item_id}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Convert memory item to knowledge item
            knowledge_item = self._convert_memory_to_knowledge(
                memory_item, team_id, agent_id, transfer_policy
            )
            
            # Store in knowledge repository
            knowledge_result = self.knowledge_transfer.repository.store_item(knowledge_item)
            
            # Update metrics
            self.metrics["transfers"] += 1
            self.metrics["bytes_transferred"] += len(str(memory_item.content))
            self.metrics["last_transfer_timestamp"] = datetime.datetime.now().isoformat()
            
            # Log the transfer
            if self.config.audit_logging_enabled:
                self._log_transfer(
                    "from_collaboration",
                    memory_item_id,
                    team_id,
                    agent_id,
                    knowledge_result.get("item_id")
                )
            
            return {
                "status": "success",
                "source_id": memory_item_id,
                "target_id": knowledge_result.get("item_id"),
                "team_id": team_id,
                "agent_id": agent_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error transferring knowledge from collaboration: {e}")
            self.metrics["transfer_failures"] += 1
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def broadcast_knowledge_to_team(self,
                                   knowledge_item_id: str,
                                   agent_id: str,
                                   team_id: str,
                                   access_policy: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Broadcast knowledge from an agent to all members of a team.
        
        Args:
            knowledge_item_id: ID of the knowledge item to broadcast
            agent_id: ID of the source agent
            team_id: ID of the target team
            access_policy: Access policy for the shared memory item
            
        Returns:
            result: Broadcast result
        """
        try:
            # First transfer to shared memory
            transfer_result = self.transfer_knowledge_to_collaboration(
                knowledge_item_id, agent_id, team_id, access_policy
            )
            
            if transfer_result["status"] != "success":
                return transfer_result
            
            # Get team members
            team_members = self._get_team_members(team_id)
            
            if not team_members:
                logger.warning(f"No members found for team {team_id}")
                return {
                    "status": "warning",
                    "message": f"No members found for team {team_id}",
                    "transfer_result": transfer_result,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Broadcast to all team members except the source agent
            broadcast_results = []
            memory_item_id = transfer_result["target_id"]
            
            for member_id in team_members:
                if member_id != agent_id:
                    # Create transfer policy for this member
                    transfer_policy = self._create_transfer_policy(agent_id, member_id)
                    
                    # Transfer to this member
                    member_result = self.transfer_knowledge_from_collaboration(
                        memory_item_id, team_id, member_id, transfer_policy
                    )
                    
                    broadcast_results.append({
                        "agent_id": member_id,
                        "result": member_result
                    })
            
            # Update metrics
            self.metrics["transfers"] += len(broadcast_results)
            
            return {
                "status": "success",
                "source_id": knowledge_item_id,
                "shared_id": memory_item_id,
                "agent_id": agent_id,
                "team_id": team_id,
                "broadcast_count": len(broadcast_results),
                "broadcast_results": broadcast_results,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting knowledge to team: {e}")
            self.metrics["transfer_failures"] += 1
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def sync_agent_with_team_knowledge(self,
                                      agent_id: str,
                                      team_id: str,
                                      knowledge_types: List[str] = None,
                                      max_items: int = 100) -> Dict[str, Any]:
        """
        Synchronize an agent with the latest knowledge from a team.
        
        Args:
            agent_id: ID of the agent to synchronize
            team_id: ID of the team to synchronize with
            knowledge_types: Types of knowledge to synchronize (if None, all types)
            max_items: Maximum number of items to synchronize
            
        Returns:
            result: Synchronization result
        """
        try:
            # Get latest team knowledge
            team_knowledge = self._get_team_knowledge(team_id, knowledge_types, max_items)
            
            if not team_knowledge:
                logger.info(f"No knowledge found for team {team_id}")
                return {
                    "status": "success",
                    "message": f"No knowledge found for team {team_id}",
                    "sync_count": 0,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Get agent's current knowledge
            agent_knowledge = self._get_agent_knowledge(agent_id, knowledge_types)
            
            # Identify new or updated knowledge
            sync_items = []
            for item in team_knowledge:
                # Skip if agent already has this knowledge
                if item["id"] in agent_knowledge:
                    agent_item = agent_knowledge[item["id"]]
                    # Skip if agent's version is newer or same
                    if agent_item["timestamp"] >= item["timestamp"]:
                        continue
                
                sync_items.append(item)
            
            # Limit to max_items
            sync_items = sync_items[:max_items]
            
            # Transfer each item to the agent
            sync_results = []
            for item in sync_items:
                # Create transfer policy
                transfer_policy = self._create_transfer_policy(None, agent_id)
                
                # Transfer to agent
                transfer_result = self.transfer_knowledge_from_collaboration(
                    item["id"], team_id, agent_id, transfer_policy
                )
                
                sync_results.append({
                    "item_id": item["id"],
                    "result": transfer_result
                })
            
            # Update metrics
            self.metrics["transfers"] += len(sync_results)
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "team_id": team_id,
                "sync_count": len(sync_results),
                "sync_results": sync_results,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error synchronizing agent with team knowledge: {e}")
            self.metrics["transfer_failures"] += 1
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def get_transfer_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for knowledge transfer.
        
        Returns:
            metrics: Knowledge transfer metrics
        """
        return {
            **self.metrics,
            "current_timestamp": datetime.datetime.now().isoformat()
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear the knowledge transfer cache.
        
        Returns:
            result: Cache clear result
        """
        if not self.config.cache_enabled:
            return {
                "status": "warning",
                "message": "Cache is not enabled",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        cache_size = len(self.cache) if self.cache else 0
        
        self.cache = {}
        self.cache_timestamps = {}
        
        return {
            "status": "success",
            "cleared_items": cache_size,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _convert_knowledge_to_memory(self,
                                    knowledge_item: KnowledgeItem,
                                    agent_id: str,
                                    team_id: str,
                                    access_policy: Dict[str, Any] = None) -> MemoryItem:
        """
        Convert a knowledge item to a memory item.
        
        Args:
            knowledge_item: Knowledge item to convert
            agent_id: ID of the source agent
            team_id: ID of the target team
            access_policy: Access policy for the memory item
            
        Returns:
            memory_item: Converted memory item
        """
        # Create default access policy if not provided
        if access_policy is None:
            access_policy = {
                "read": ["team_member"],
                "write": ["team_admin", agent_id],
                "delete": ["team_admin", agent_id],
                "share": ["team_admin", agent_id]
            }
        
        # Create memory item
        memory_item = MemoryItem(
            id=str(uuid.uuid4()),
            content=knowledge_item.content,
            content_type=knowledge_item.content_type,
            metadata={
                "source_type": "knowledge_item",
                "source_id": knowledge_item.id,
                "source_agent": agent_id,
                "team_id": team_id,
                "original_timestamp": knowledge_item.timestamp,
                "original_metadata": knowledge_item.metadata,
                "transfer_timestamp": datetime.datetime.now().isoformat()
            },
            tags=knowledge_item.tags,
            access_policy=AccessPolicy(**access_policy),
            timestamp=datetime.datetime.now().isoformat()
        )
        
        return memory_item
    
    def _convert_memory_to_knowledge(self,
                                    memory_item: MemoryItem,
                                    team_id: str,
                                    agent_id: str,
                                    transfer_policy: Dict[str, Any] = None) -> KnowledgeItem:
        """
        Convert a memory item to a knowledge item.
        
        Args:
            memory_item: Memory item to convert
            team_id: ID of the source team
            agent_id: ID of the target agent
            transfer_policy: Transfer policy for the knowledge item
            
        Returns:
            knowledge_item: Converted knowledge item
        """
        # Create default transfer policy if not provided
        if transfer_policy is None:
            transfer_policy = {
                "transfer_method": self.config.default_transfer_method,
                "allowed_recipients": ["team_member"],
                "expiration": None,
                "transfer_count_limit": None
            }
        
        # Create knowledge item
        knowledge_item = KnowledgeItem(
            id=str(uuid.uuid4()),
            content=memory_item.content,
            content_type=memory_item.content_type,
            metadata={
                "source_type": "memory_item",
                "source_id": memory_item.id,
                "source_team": team_id,
                "target_agent": agent_id,
                "original_timestamp": memory_item.timestamp,
                "original_metadata": memory_item.metadata,
                "transfer_timestamp": datetime.datetime.now().isoformat()
            },
            tags=memory_item.tags,
            transfer_policy=TransferPolicy(**transfer_policy),
            timestamp=datetime.datetime.now().isoformat()
        )
        
        return knowledge_item
    
    def _check_access_permission(self, memory_item: MemoryItem, agent_id: str) -> bool:
        """
        Check if an agent has permission to access a memory item.
        
        Args:
            memory_item: Memory item to check
            agent_id: ID of the agent
            
        Returns:
            has_permission: Whether the agent has permission
        """
        if not self.config.access_control_enabled:
            return True
            
        # Get access policy
        access_policy = memory_item.access_policy
        
        # Check read permission
        if agent_id in access_policy.read:
            return True
            
        # Check if agent is a team member
        if "team_member" in access_policy.read:
            team_id = memory_item.metadata.get("team_id")
            if team_id and self._is_team_member(agent_id, team_id):
                return True
                
        # Check if agent is a team admin
        if "team_admin" in access_policy.read:
            team_id = memory_item.metadata.get("team_id")
            if team_id and self._is_team_admin(agent_id, team_id):
                return True
        
        return False
    
    def _get_team_members(self, team_id: str) -> List[str]:
        """
        Get the members of a team.
        
        Args:
            team_id: ID of the team
            
        Returns:
            members: List of team member IDs
        """
        # Check cache first
        cache_key = f"team_members_{team_id}"
        if self.config.cache_enabled and cache_key in self.cache:
            # Check if cache is still valid
            if (datetime.datetime.now().timestamp() - self.cache_timestamps[cache_key]) < self.config.cache_ttl_seconds:
                self.metrics["cache_hits"] += 1
                return self.cache[cache_key]
            else:
                # Cache expired
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Call collaboration API to get team members
            response = requests.get(
                f"{self.config.collaboration_system_api_url}/teams/{team_id}/members",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                members = response.json().get("members", [])
                
                # Cache the result
                if self.config.cache_enabled:
                    self.cache[cache_key] = members
                    self.cache_timestamps[cache_key] = datetime.datetime.now().timestamp()
                
                return members
            else:
                logger.error(f"Error getting team members: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting team members: {e}")
            return []
    
    def _is_team_member(self, agent_id: str, team_id: str) -> bool:
        """
        Check if an agent is a member of a team.
        
        Args:
            agent_id: ID of the agent
            team_id: ID of the team
            
        Returns:
            is_member: Whether the agent is a team member
        """
        members = self._get_team_members(team_id)
        return agent_id in members
    
    def _is_team_admin(self, agent_id: str, team_id: str) -> bool:
        """
        Check if an agent is an admin of a team.
        
        Args:
            agent_id: ID of the agent
            team_id: ID of the team
            
        Returns:
            is_admin: Whether the agent is a team admin
        """
        # Check cache first
        cache_key = f"team_admins_{team_id}"
        if self.config.cache_enabled and cache_key in self.cache:
            # Check if cache is still valid
            if (datetime.datetime.now().timestamp() - self.cache_timestamps[cache_key]) < self.config.cache_ttl_seconds:
                self.metrics["cache_hits"] += 1
                admins = self.cache[cache_key]
                return agent_id in admins
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Call collaboration API to get team admins
            response = requests.get(
                f"{self.config.collaboration_system_api_url}/teams/{team_id}/admins",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                admins = response.json().get("admins", [])
                
                # Cache the result
                if self.config.cache_enabled:
                    self.cache[cache_key] = admins
                    self.cache_timestamps[cache_key] = datetime.datetime.now().timestamp()
                
                return agent_id in admins
            else:
                logger.error(f"Error getting team admins: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting team admins: {e}")
            return False
    
    def _get_team_knowledge(self, team_id: str, knowledge_types: List[str] = None, max_items: int = 100) -> List[Dict[str, Any]]:
        """
        Get knowledge items for a team.
        
        Args:
            team_id: ID of the team
            knowledge_types: Types of knowledge to get (if None, all types)
            max_items: Maximum number of items to get
            
        Returns:
            knowledge_items: List of knowledge items
        """
        try:
            # Prepare query parameters
            params = {
                "team_id": team_id,
                "limit": max_items
            }
            
            if knowledge_types:
                params["types"] = ",".join(knowledge_types)
            
            # Call shared memory API to get team knowledge
            response = requests.get(
                f"{self.config.collaboration_system_api_url}/shared-memory/items",
                params=params,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json().get("items", [])
            else:
                logger.error(f"Error getting team knowledge: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting team knowledge: {e}")
            return []
    
    def _get_agent_knowledge(self, agent_id: str, knowledge_types: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get knowledge items for an agent.
        
        Args:
            agent_id: ID of the agent
            knowledge_types: Types of knowledge to get (if None, all types)
            
        Returns:
            knowledge_items: Dictionary of knowledge items by source ID
        """
        try:
            # Prepare query parameters
            params = {
                "agent_id": agent_id
            }
            
            if knowledge_types:
                params["types"] = ",".join(knowledge_types)
            
            # Call learning API to get agent knowledge
            response = requests.get(
                f"{self.config.learning_system_api_url}/knowledge/items",
                params=params,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                items = response.json().get("items", [])
                
                # Convert to dictionary by source ID
                result = {}
                for item in items:
                    source_id = item.get("metadata", {}).get("source_id")
                    if source_id:
                        result[source_id] = item
                
                return result
            else:
                logger.error(f"Error getting agent knowledge: {response.status_code} {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting agent knowledge: {e}")
            return {}
    
    def _create_transfer_policy(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Create a transfer policy for knowledge transfer.
        
        Args:
            source_id: ID of the source (agent or team)
            target_id: ID of the target (agent or team)
            
        Returns:
            policy: Transfer policy
        """
        # Create basic policy
        policy = {
            "transfer_method": self.config.default_transfer_method,
            "allowed_recipients": [target_id],
            "expiration": None,
            "transfer_count_limit": None
        }
        
        # Add source to allowed recipients if provided
        if source_id:
            policy["allowed_recipients"].append(source_id)
        
        return policy
    
    def _log_transfer(self, 
                     transfer_type: str,
                     source_id: str,
                     source_owner: str,
                     target_owner: str,
                     target_id: str):
        """
        Log a knowledge transfer.
        
        Args:
            transfer_type: Type of transfer
            source_id: ID of the source item
            source_owner: ID of the source owner
            target_owner: ID of the target owner
            target_id: ID of the target item
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "transfer_type": transfer_type,
            "source_id": source_id,
            "source_owner": source_owner,
            "target_owner": target_owner,
            "target_id": target_id
        }
        
        log_file = os.path.join(self.config.storage_path, "transfer_log.jsonl")
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Error logging transfer: {e}")


# REST API for Knowledge Transfer Integration

class KnowledgeTransferAPI:
    """
    REST API for Knowledge Transfer Integration.
    
    This class provides HTTP endpoints for the Knowledge Transfer Integration.
    """
    
    def __init__(self, integration: KnowledgeTransferIntegration = None):
        """
        Initialize the Knowledge Transfer API.
        
        Args:
            integration: Knowledge Transfer Integration instance
        """
        self.integration = integration or KnowledgeTransferIntegration()
        logger.info("Knowledge Transfer API initialized")
    
    def handle_request(self, method: str, path: str, params: Dict[str, Any] = None, body: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            params: Query parameters
            body: Request body
            
        Returns:
            response: HTTP response
        """
        # Parse path
        path_parts = path.strip("/").split("/")
        base_path = path_parts[0] if path_parts else ""
        
        # Handle request based on path and method
        if base_path == "transfer":
            if method == "POST":
                return self._handle_transfer(path_parts[1:], body)
            elif method == "GET":
                return self._handle_get_transfer(path_parts[1:], params)
        elif base_path == "metrics":
            if method == "GET":
                return self.integration.get_transfer_metrics()
        elif base_path == "cache":
            if method == "DELETE":
                return self.integration.clear_cache()
        
        # Default response for unknown path
        return {
            "status": "error",
            "message": f"Unknown path: {path}",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _handle_transfer(self, path_parts: List[str], body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a transfer request.
        
        Args:
            path_parts: Path parts after the base path
            body: Request body
            
        Returns:
            response: HTTP response
        """
        if not path_parts:
            return {
                "status": "error",
                "message": "Missing transfer type",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        transfer_type = path_parts[0]
        
        if transfer_type == "to_collaboration":
            # Transfer from agent to team
            return self.integration.transfer_knowledge_to_collaboration(
                body.get("knowledge_item_id"),
                body.get("agent_id"),
                body.get("team_id"),
                body.get("access_policy")
            )
        elif transfer_type == "from_collaboration":
            # Transfer from team to agent
            return self.integration.transfer_knowledge_from_collaboration(
                body.get("memory_item_id"),
                body.get("team_id"),
                body.get("agent_id"),
                body.get("transfer_policy")
            )
        elif transfer_type == "broadcast":
            # Broadcast from agent to team
            return self.integration.broadcast_knowledge_to_team(
                body.get("knowledge_item_id"),
                body.get("agent_id"),
                body.get("team_id"),
                body.get("access_policy")
            )
        elif transfer_type == "sync":
            # Sync agent with team
            return self.integration.sync_agent_with_team_knowledge(
                body.get("agent_id"),
                body.get("team_id"),
                body.get("knowledge_types"),
                body.get("max_items", 100)
            )
        else:
            return {
                "status": "error",
                "message": f"Unknown transfer type: {transfer_type}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _handle_get_transfer(self, path_parts: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a GET transfer request.
        
        Args:
            path_parts: Path parts after the base path
            params: Query parameters
            
        Returns:
            response: HTTP response
        """
        if not path_parts:
            return {
                "status": "error",
                "message": "Missing transfer type",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        transfer_type = path_parts[0]
        
        if transfer_type == "sync":
            # Sync agent with team
            return self.integration.sync_agent_with_team_knowledge(
                params.get("agent_id"),
                params.get("team_id"),
                params.get("knowledge_types", "").split(",") if params.get("knowledge_types") else None,
                int(params.get("max_items", 100))
            )
        else:
            return {
                "status": "error",
                "message": f"Unknown transfer type: {transfer_type}",
                "timestamp": datetime.datetime.now().isoformat()
            }


# Main function for running the API server
def main():
    """Run the Knowledge Transfer API server."""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    api = KnowledgeTransferAPI()
    
    @app.route("/api/knowledge-transfer/<path:path>", methods=["GET", "POST", "DELETE"])
    def handle_request(path):
        method = request.method
        params = request.args.to_dict()
        body = request.json if request.is_json else {}
        
        response = api.handle_request(method, path, params, body)
        return jsonify(response)
    
    app.run(host="0.0.0.0", port=8082)


if __name__ == "__main__":
    main()
