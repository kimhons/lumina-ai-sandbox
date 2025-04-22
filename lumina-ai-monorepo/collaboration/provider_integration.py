"""
Integration module for connecting the Advanced Multi-Agent Collaboration system
with the Provider System.

This module provides adapters and utilities for integrating the collaboration
system with the existing provider components.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from lumina.providers.base import Provider, ProviderModel
from lumina.providers.selector import ProviderSelector
from lumina.common.interfaces import Message, MessageRole

from collaboration.integration import CollaborativeProviderAdapter, CollaborationManager

logger = logging.getLogger(__name__)

class EnhancedProviderAdapter:
    """
    Enhanced adapter for integrating the collaboration system with the provider system.
    This extends the basic CollaborativeProviderAdapter with additional functionality.
    """
    
    def __init__(
        self,
        collaboration_manager: CollaborationManager,
        provider_selector: ProviderSelector,
        collaborative_provider_adapter: CollaborativeProviderAdapter
    ):
        """
        Initialize the enhanced provider adapter.
        
        Args:
            collaboration_manager: The collaboration manager from the collaboration system
            provider_selector: The provider selector from the provider system
            collaborative_provider_adapter: The basic collaborative provider adapter
        """
        self.collaboration_manager = collaboration_manager
        self.provider_selector = provider_selector
        self.collaborative_provider_adapter = collaborative_provider_adapter
        
        # Initialize provider capability mapping
        self.provider_capability_mapping = {
            "text_generation": ["reasoning", "creative_writing", "planning"],
            "code_generation": ["code_generation", "reasoning"],
            "embedding": ["research", "reasoning"],
            "image_generation": ["visual_design", "creative_writing"],
            "function_calling": ["planning", "reasoning"],
            "chat": ["reasoning", "creative_writing", "research"],
            "classification": ["reasoning", "research"],
            "summarization": ["reasoning", "creative_writing"],
            "translation": ["language_translation"],
            "speech_to_text": ["audio_processing"],
            "text_to_speech": ["audio_generation"]
        }
        
        logger.info("Enhanced provider adapter initialized")
    
    def create_collaborative_team_for_task(
        self,
        task_name: str,
        task_description: str,
        required_capabilities: Dict[str, float],
        domain_specializations: Optional[List[str]] = None,
        min_team_size: int = 2,
        max_team_size: int = 5,
        strategy: str = "optimal_coverage"
    ) -> Dict[str, Any]:
        """
        Create a collaborative team of providers for a task with enhanced capability mapping.
        
        Args:
            task_name: Name of the task
            task_description: Description of the task
            required_capabilities: Dictionary mapping capability names to required levels
            domain_specializations: Optional list of domain specializations
            min_team_size: Minimum team size
            max_team_size: Maximum team size
            strategy: Team formation strategy
            
        Returns:
            Dictionary containing task and team information
        """
        # Map required capabilities to provider capabilities
        provider_capabilities = self._map_capabilities_to_provider_capabilities(required_capabilities)
        
        # Create task team using the basic adapter
        result = self.collaborative_provider_adapter.create_task_team(
            task_name=task_name,
            task_description=task_description,
            required_capabilities=provider_capabilities,
            domain_specializations=domain_specializations or [],
            min_team_size=min_team_size,
            max_team_size=max_team_size,
            strategy=strategy
        )
        
        # Enhance result with additional information
        if result:
            # Get team members
            team_id = result["team"]["team_id"]
            team_members = result["team"]["members"]
            
            # Get provider information for each team member
            providers_info = []
            for member_id in team_members:
                # Extract provider ID from member ID
                if member_id.startswith("provider-"):
                    provider_id = member_id[9:]  # Remove "provider-" prefix
                    provider = self.provider_selector.get_provider_by_id(provider_id)
                    if provider:
                        providers_info.append({
                            "id": provider_id,
                            "name": provider.get_name(),
                            "capabilities": provider.get_capabilities(),
                            "models": [model.name for model in provider.get_models()]
                        })
            
            # Add provider information to result
            result["providers"] = providers_info
            
            # Add negotiation information
            negotiation_id = self.collaboration_manager.initiate_task_negotiation(
                team_id=team_id,
                initiator_id=team_members[0] if team_members else None
            )
            
            if negotiation_id:
                result["negotiation"] = {
                    "id": negotiation_id,
                    "status": "initiated"
                }
            
            logger.info(f"Created enhanced collaborative team for task {task_name}")
        
        return result
    
    def _map_capabilities_to_provider_capabilities(self, capabilities: Dict[str, float]) -> Dict[str, float]:
        """
        Map general capabilities to provider-specific capabilities.
        
        Args:
            capabilities: Dictionary mapping capability names to required levels
            
        Returns:
            Dictionary mapping provider capability names to required levels
        """
        provider_capabilities = {}
        
        # Create reverse mapping from collaboration capabilities to provider capabilities
        reverse_mapping = {}
        for provider_cap, collab_caps in self.provider_capability_mapping.items():
            for collab_cap in collab_caps:
                if collab_cap not in reverse_mapping:
                    reverse_mapping[collab_cap] = []
                reverse_mapping[collab_cap].append(provider_cap)
        
        # Map each capability to provider capabilities
        for capability, level in capabilities.items():
            # Normalize capability name
            cap_name = capability.lower().replace(" ", "_")
            
            # Check if capability is in reverse mapping
            if cap_name in reverse_mapping:
                # Map to provider capabilities
                for provider_cap in reverse_mapping[cap_name]:
                    # Use the highest level if multiple capabilities map to the same provider capability
                    if provider_cap in provider_capabilities:
                        provider_capabilities[provider_cap] = max(provider_capabilities[provider_cap], level)
                    else:
                        provider_capabilities[provider_cap] = level
            else:
                # Use capability as is if no mapping exists
                provider_capabilities[cap_name] = level
        
        return provider_capabilities
    
    def execute_collaborative_task(
        self,
        team_id: str,
        task_input: Dict[str, Any],
        execution_strategy: str = "parallel"
    ) -> Dict[str, Any]:
        """
        Execute a task using a collaborative team of providers.
        
        Args:
            team_id: ID of the collaborative team
            task_input: Input data for the task
            execution_strategy: Strategy for task execution ("parallel" or "sequential")
            
        Returns:
            Dictionary containing task execution results
        """
        # Get team information
        team_info = self.collaboration_manager.get_team_info(team_id)
        if not team_info:
            logger.warning(f"Team {team_id} not found")
            return {"error": f"Team {team_id} not found"}
        
        # Get team members
        team_members = team_info.get("members", [])
        
        # Get task information
        task_id = team_info.get("task_id")
        if not task_id:
            logger.warning(f"Team {team_id} has no associated task")
            return {"error": f"Team {team_id} has no associated task"}
        
        task_info = self.collaboration_manager.get_task_info(task_id)
        if not task_info:
            logger.warning(f"Task {task_id} not found")
            return {"error": f"Task {task_id} not found"}
        
        # Create shared context for the task
        context_id = self.collaboration_manager.share_context(
            key="task_input",
            value=task_input,
            context_type="user_input",
            scope="team",
            scope_id=team_id,
            agent_id="system"
        )
        
        # Execute task based on strategy
        if execution_strategy == "parallel":
            results = self._execute_parallel(team_members, task_input, team_id, task_id)
        else:  # sequential
            results = self._execute_sequential(team_members, task_input, team_id, task_id)
        
        # Combine results
        combined_result = self._combine_results(results, team_id, task_id)
        
        # Store combined result in shared memory
        memory_id = self.collaboration_manager.store_memory(
            key="task_result",
            value=combined_result,
            memory_type="factual",
            scope="task",
            scope_id=task_id,
            agent_id="system",
            importance=0.8,
            tags=["result", task_info.get("name", "")]
        )
        
        # Record learning event
        event_id = self.collaboration_manager.record_learning_event(
            event_type="task_completion",
            agent_id="system",
            content={
                "task_id": task_id,
                "team_id": team_id,
                "result": combined_result
            },
            task_id=task_id,
            team_id=team_id
        )
        
        logger.info(f"Executed collaborative task {task_id} with team {team_id}")
        
        return {
            "task_id": task_id,
            "team_id": team_id,
            "result": combined_result,
            "individual_results": results
        }
    
    def _execute_parallel(
        self,
        team_members: List[str],
        task_input: Dict[str, Any],
        team_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Execute a task in parallel using all team members.
        
        Args:
            team_members: List of team member IDs
            task_input: Input data for the task
            team_id: ID of the collaborative team
            task_id: ID of the task
            
        Returns:
            Dictionary mapping member IDs to their results
        """
        results = {}
        
        # Execute task with each provider
        for member_id in team_members:
            # Extract provider ID from member ID
            if member_id.startswith("provider-"):
                provider_id = member_id[9:]  # Remove "provider-" prefix
                provider = self.provider_selector.get_provider_by_id(provider_id)
                if provider:
                    try:
                        # Create message for provider
                        message = Message(
                            role=MessageRole.USER,
                            content=str(task_input.get("content", "")),
                            metadata={
                                "team_id": team_id,
                                "task_id": task_id,
                                "collaborative": True
                            }
                        )
                        
                        # Get response from provider
                        response = provider.generate(message)
                        
                        # Store result
                        results[member_id] = {
                            "provider_id": provider_id,
                            "provider_name": provider.get_name(),
                            "content": response.content,
                            "metadata": response.metadata
                        }
                        
                        # Record action in learning system
                        self.collaboration_manager.record_learning_event(
                            event_type="action",
                            agent_id=member_id,
                            content={
                                "action": "generate",
                                "input": message.content,
                                "output": response.content
                            },
                            task_id=task_id,
                            team_id=team_id
                        )
                    except Exception as e:
                        logger.error(f"Error executing task with provider {provider_id}: {e}")
                        results[member_id] = {
                            "provider_id": provider_id,
                            "provider_name": provider.get_name(),
                            "error": str(e)
                        }
        
        return results
    
    def _execute_sequential(
        self,
        team_members: List[str],
        task_input: Dict[str, Any],
        team_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Execute a task sequentially, passing results from one member to the next.
        
        Args:
            team_members: List of team member IDs
            task_input: Input data for the task
            team_id: ID of the collaborative team
            task_id: ID of the task
            
        Returns:
            Dictionary mapping member IDs to their results
        """
        results = {}
        current_input = task_input
        
        # Execute task with each provider in sequence
        for member_id in team_members:
            # Extract provider ID from member ID
            if member_id.startswith("provider-"):
                provider_id = member_id[9:]  # Remove "provider-" prefix
                provider = self.provider_selector.get_provider_by_id(provider_id)
                if provider:
                    try:
                        # Create message for provider
                        message = Message(
                            role=MessageRole.USER,
                            content=str(current_input.get("content", "")),
                            metadata={
                                "team_id": team_id,
                                "task_id": task_id,
                                "collaborative": True,
                                "previous_results": results
                            }
                        )
                        
                        # Get response from provider
                        response = provider.generate(message)
                        
                        # Store result
                        results[member_id] = {
                            "provider_id": provider_id,
                            "provider_name": provider.get_name(),
                            "content": response.content,
                            "metadata": response.metadata
                        }
                        
                        # Update input for next provider
                        current_input = {
                            "content": response.content,
                            "metadata": response.metadata
                        }
                        
                        # Record action in learning system
                        self.collaboration_manager.record_learning_event(
                            event_type="action",
                            agent_id=member_id,
                            content={
                                "action": "generate",
                                "input": message.content,
                                "output": response.content
                            },
                            task_id=task_id,
                            team_id=team_id
                        )
                    except Exception as e:
                        logger.error(f"Error executing task with provider {provider_id}: {e}")
                        results[member_id] = {
                            "provider_id": provider_id,
                            "provider_name": provider.get_name(),
                            "error": str(e)
                        }
        
        return results
    
    def _combine_results(
        self,
        results: Dict[str, Any],
        team_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Combine results from multiple providers.
        
        Args:
            results: Dictionary mapping member IDs to their results
            team_id: ID of the collaborative team
            task_id: ID of the task
            
        Returns:
            Combined result
        """
        # If only one result, return it directly
        if len(results) == 1:
            return next(iter(results.values()))
        
        # If no results, return empty result
        if not results:
            return {"content": "", "metadata": {}}
        
        # Get team information
        team_info = self.collaboration_manager.get_team_info(team_id)
        if not team_info:
            logger.warning(f"Team {team_id} not found")
            return {"error": f"Team {team_id} not found"}
        
        # Get team roles
        team_roles = team_info.get("roles", {})
        
        # Determine primary role for each member
        primary_roles = {}
        for member_id, roles in team_roles.items():
            if roles:
                # Get role with highest capability level
                primary_role = max(roles, key=lambda r: team_roles[member_id][r])
                primary_roles[member_id] = primary_role
        
        # Combine results based on roles
        combined_content = ""
        combined_metadata = {}
        
        # Collect content from each provider
        for member_id, result in results.items():
            if "error" in result:
                continue
            
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Get primary role for this member
            role = primary_roles.get(member_id, "unknown")
            
            # Add content with role prefix
            combined_content += f"\n\n## {role.capitalize()} Contribution\n{content}"
            
            # Merge metadata
            for key, value in metadata.items():
                if key not in combined_metadata:
                    combined_metadata[key] = value
                elif isinstance(combined_metadata[key], list) and isinstance(value, list):
                    combined_metadata[key].extend(value)
                elif isinstance(combined_metadata[key], dict) and isinstance(value, dict):
                    combined_metadata[key].update(value)
        
        # Add team and task information to metadata
        combined_metadata["team_id"] = team_id
        combined_metadata["task_id"] = task_id
        combined_metadata["contributors"] = list(results.keys())
        
        return {
            "content": combined_content.strip(),
            "metadata": combined_metadata
        }
    
    def get_provider_agent(self, provider_id: str):
        """
        Get the collaborative agent for a provider.
        
        Args:
            provider_id: ID of the provider
            
        Returns:
            Collaborative agent for the provider
        """
        return self.collaborative_provider_adapter.get_provider_agent(provider_id)
    
    def get_team_providers(self, team_id: str) -> List[Provider]:
        """
        Get all providers in a team.
        
        Args:
            team_id: ID of the team
            
        Returns:
            List of providers in the team
        """
        return self.collaborative_provider_adapter.get_team_providers(team_id)
    
    def get_provider_context(self, provider_id: str) -> Dict[str, Any]:
        """
        Get context for a provider.
        
        Args:
            provider_id: ID of the provider
            
        Returns:
            Dictionary of context items for the provider
        """
        return self.collaborative_provider_adapter.get_provider_context(provider_id)
    
    def get_provider_memory(self, provider_id: str) -> Dict[str, Any]:
        """
        Get memory for a provider.
        
        Args:
            provider_id: ID of the provider
            
        Returns:
            Dictionary of memory items for the provider
        """
        return self.collaborative_provider_adapter.get_provider_memory(provider_id)
    
    def share_provider_context(
        self,
        provider_id: str,
        key: str,
        value: Any,
        context_type: str,
        scope: str,
        scope_id: str
    ) -> Optional[str]:
        """
        Share context from a provider.
        
        Args:
            provider_id: ID of the provider
            key: Context key
            value: Context value
            context_type: Type of context
            scope: Scope of context
            scope_id: ID of the scope
            
        Returns:
            ID of the created context item, or None if creation failed
        """
        return self.collaborative_provider_adapter.share_provider_context(
            provider_id=provider_id,
            key=key,
            value=value,
            context_type=context_type,
            scope=scope,
            scope_id=scope_id
        )


def create_enhanced_provider_adapter(
    collaboration_manager: CollaborationManager,
    provider_selector: ProviderSelector,
    collaborative_provider_adapter: CollaborativeProviderAdapter
) -> EnhancedProviderAdapter:
    """
    Create and initialize an enhanced provider adapter.
    
    Args:
        collaboration_manager: The collaboration manager from the collaboration system
        provider_selector: The provider selector from the provider system
        collaborative_provider_adapter: The basic collaborative provider adapter
        
    Returns:
        Initialized enhanced provider adapter
    """
    adapter = EnhancedProviderAdapter(
        collaboration_manager=collaboration_manager,
        provider_selector=provider_selector,
        collaborative_provider_adapter=collaborative_provider_adapter
    )
    
    return adapter
