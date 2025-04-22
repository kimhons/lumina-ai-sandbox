"""
Dynamic Team Formation Module for Advanced Multi-Agent Collaboration System
This module provides enhanced dynamic team formation capabilities for Lumina AI, enabling
the system to automatically assemble specialized agent teams based on task requirements.
"""
import logging
from typing import List, Dict, Set, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass, field
import json
import time
import uuid
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TeamFormationStrategy(Enum):
    """Strategy for team formation."""
    CAPABILITY_BASED = "CAPABILITY_BASED"
    PERFORMANCE_BASED = "PERFORMANCE_BASED"
    SPECIALIZATION_BASED = "SPECIALIZATION_BASED"
    BALANCED = "BALANCED"
    COST_OPTIMIZED = "COST_OPTIMIZED"
    HYBRID = "HYBRID"

@dataclass
class Agent:
    """Represents an AI agent with specific capabilities and performance metrics."""
    id: str
    name: str
    provider_id: str
    model_id: str
    capabilities: Set[str] = field(default_factory=set)
    performance_rating: float = 0.0
    available: bool = True
    specialization: str = ""
    context_window_size: int = 8192
    cost_per_token: float = 0.0
    historical_performance: Dict[str, float] = field(default_factory=dict)
    collaboration_score: float = 0.0
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    def has_all_capabilities(self, capabilities: Set[str]) -> bool:
        """Check if agent has all specified capabilities."""
        return capabilities.issubset(self.capabilities)
    
    def capability_match_score(self, required_capabilities: Set[str]) -> float:
        """Calculate how well the agent's capabilities match the requirements."""
        if not required_capabilities:
            return 1.0
        
        matches = len(required_capabilities.intersection(self.capabilities))
        return matches / len(required_capabilities)
    
    def get_performance_for_task_type(self, task_type: str) -> float:
        """Get the agent's performance rating for a specific task type."""
        return self.historical_performance.get(task_type, self.performance_rating)
    
    def __str__(self) -> str:
        return f"Agent(id={self.id}, name={self.name}, capabilities={len(self.capabilities)}, rating={self.performance_rating:.2f})"

@dataclass
class Role:
    """Represents a role that an agent can fulfill in a team."""
    id: str
    name: str
    description: str
    required_capabilities: Set[str] = field(default_factory=set)
    preferred_capabilities: Set[str] = field(default_factory=set)
    min_performance_rating: float = 0.0
    priority: int = 1
    categories: Set[str] = field(default_factory=set)
    
    def __str__(self) -> str:
        return f"Role(id={self.id}, name={self.name}, required_capabilities={len(self.required_capabilities)})"

@dataclass
class Task:
    """Represents a task that requires a team of agents to complete."""
    id: str
    name: str
    description: str
    required_capabilities: Set[str] = field(default_factory=set)
    preferred_capabilities: Set[str] = field(default_factory=set)
    required_roles: List[Role] = field(default_factory=list)
    priority: int = 1
    deadline: Optional[float] = None
    complexity: int = 1
    task_type: str = "general"
    
    def __str__(self) -> str:
        return f"Task(id={self.id}, name={self.name}, required_roles={len(self.required_roles)})"

@dataclass
class Team:
    """Represents a team of agents assembled for a specific task."""
    id: str
    name: str
    agents: List[Agent] = field(default_factory=list)
    task: Optional[Task] = None
    created_at: float = field(default_factory=time.time)
    status: str = "FORMING"
    role_assignments: Dict[str, str] = field(default_factory=dict)  # role_id -> agent_id
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def get_agent_for_role(self, role_id: str) -> Optional[Agent]:
        """Get the agent assigned to a specific role."""
        agent_id = self.role_assignments.get(role_id)
        if not agent_id:
            return None
        
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        
        return None
    
    def is_complete(self) -> bool:
        """Check if the team has all required roles filled."""
        if not self.task:
            return False
        
        return len(self.role_assignments) == len(self.task.required_roles)
    
    def calculate_team_performance(self) -> float:
        """Calculate the overall performance rating of the team."""
        if not self.agents:
            return 0.0
        
        # Base performance is the average of all agent performance ratings
        base_performance = sum(agent.performance_rating for agent in self.agents) / len(self.agents)
        
        # Adjust for role coverage
        role_coverage = len(self.role_assignments) / len(self.task.required_roles) if self.task else 0.0
        
        # Adjust for collaboration score
        collaboration_factor = sum(agent.collaboration_score for agent in self.agents) / len(self.agents)
        
        return base_performance * 0.6 + role_coverage * 0.3 + collaboration_factor * 0.1
    
    def __str__(self) -> str:
        return f"Team(id={self.id}, name={self.name}, agents={len(self.agents)}, status={self.status})"

class DynamicTeamFormation:
    """
    Enhanced dynamic team formation system that assembles specialized agent teams
    based on task requirements, agent capabilities, and performance metrics.
    """
    
    def __init__(self, 
                 capability_match_threshold: float = 0.75,
                 performance_weight: float = 0.6,
                 specialization_weight: float = 0.4,
                 collaboration_weight: float = 0.3,
                 cost_weight: float = 0.2):
        """
        Initialize the dynamic team formation system.
        
        Args:
            capability_match_threshold: Minimum capability match score required for agent selection
            performance_weight: Weight given to agent performance in scoring
            specialization_weight: Weight given to agent specialization in scoring
            collaboration_weight: Weight given to agent collaboration history in scoring
            cost_weight: Weight given to agent cost in scoring
        """
        self.capability_match_threshold = capability_match_threshold
        self.performance_weight = performance_weight
        self.specialization_weight = specialization_weight
        self.collaboration_weight = collaboration_weight
        self.cost_weight = cost_weight
        self.agent_registry: Dict[str, Agent] = {}
        self.role_registry: Dict[str, Role] = {}
        self.team_history: List[Team] = []
        
    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the team formation system."""
        self.agent_registry[agent.id] = agent
        logger.info(f"Registered agent: {agent.name} with {len(agent.capabilities)} capabilities")
        
    def register_role(self, role: Role) -> None:
        """Register a role with the team formation system."""
        self.role_registry[role.id] = role
        logger.info(f"Registered role: {role.name} requiring {len(role.required_capabilities)} capabilities")
        
    def get_available_agents(self) -> List[Agent]:
        """Get all available agents."""
        return [agent for agent in self.agent_registry.values() if agent.available]
    
    def form_team_for_task(self, task: Task, strategy: TeamFormationStrategy = TeamFormationStrategy.BALANCED) -> Team:
        """
        Form a team for a specific task using the specified strategy.
        
        Args:
            task: The task for which to form a team
            strategy: The team formation strategy to use
            
        Returns:
            A team of agents assembled for the task
        """
        logger.info(f"Forming team for task: {task.name} using strategy: {strategy.value}")
        
        # Create a new team
        team = Team(
            id=str(uuid.uuid4()),
            name=f"Team for {task.name}",
            task=task
        )
        
        # Get available agents
        available_agents = self.get_available_agents()
        if not available_agents:
            logger.warning("No available agents for team formation")
            team.status = "FAILED"
            return team
        
        # Form team based on strategy
        if strategy == TeamFormationStrategy.CAPABILITY_BASED:
            self._form_team_capability_based(team, available_agents)
        elif strategy == TeamFormationStrategy.PERFORMANCE_BASED:
            self._form_team_performance_based(team, available_agents)
        elif strategy == TeamFormationStrategy.SPECIALIZATION_BASED:
            self._form_team_specialization_based(team, available_agents)
        elif strategy == TeamFormationStrategy.COST_OPTIMIZED:
            self._form_team_cost_optimized(team, available_agents)
        elif strategy == TeamFormationStrategy.HYBRID:
            self._form_team_hybrid(team, available_agents)
        else:  # Default to BALANCED
            self._form_team_balanced(team, available_agents)
        
        # Update team status
        if team.is_complete():
            team.status = "COMPLETE"
        else:
            team.status = "PARTIAL"
        
        # Calculate team performance metrics
        team.performance_metrics["overall"] = team.calculate_team_performance()
        team.performance_metrics["capability_coverage"] = self._calculate_capability_coverage(team)
        team.performance_metrics["role_coverage"] = len(team.role_assignments) / len(task.required_roles) if task.required_roles else 1.0
        
        # Add to team history
        self.team_history.append(team)
        
        logger.info(f"Team formation complete: {team.status} with {len(team.agents)} agents")
        return team
    
    def _form_team_capability_based(self, team: Team, available_agents: List[Agent]) -> None:
        """Form a team based primarily on capability matching."""
        task = team.task
        if not task:
            return
        
        # For each required role, find the agent with the best capability match
        for role in task.required_roles:
            best_agent = None
            best_score = 0.0
            
            for agent in available_agents:
                if agent in team.agents:
                    continue  # Skip agents already in the team
                
                # Calculate capability match score
                capability_score = agent.capability_match_score(role.required_capabilities)
                
                # Skip agents that don't meet the minimum capability threshold
                if capability_score < self.capability_match_threshold:
                    continue
                
                if capability_score > best_score:
                    best_score = capability_score
                    best_agent = agent
            
            if best_agent:
                team.agents.append(best_agent)
                team.role_assignments[role.id] = best_agent.id
                available_agents.remove(best_agent)  # Remove from available pool
    
    def _form_team_performance_based(self, team: Team, available_agents: List[Agent]) -> None:
        """Form a team based primarily on agent performance ratings."""
        task = team.task
        if not task:
            return
        
        # For each required role, find the agent with the best performance
        for role in task.required_roles:
            best_agent = None
            best_score = 0.0
            
            for agent in available_agents:
                if agent in team.agents:
                    continue  # Skip agents already in the team
                
                # Calculate capability match score
                capability_score = agent.capability_match_score(role.required_capabilities)
                
                # Skip agents that don't meet the minimum capability threshold
                if capability_score < self.capability_match_threshold:
                    continue
                
                # Calculate performance score for this task type
                performance_score = agent.get_performance_for_task_type(task.task_type)
                
                # Combined score with heavy weight on performance
                combined_score = capability_score * 0.3 + performance_score * 0.7
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_agent = agent
            
            if best_agent:
                team.agents.append(best_agent)
                team.role_assignments[role.id] = best_agent.id
                available_agents.remove(best_agent)  # Remove from available pool
    
    def _form_team_specialization_based(self, team: Team, available_agents: List[Agent]) -> None:
        """Form a team based primarily on agent specialization for roles."""
        task = team.task
        if not task:
            return
        
        # For each required role, find the agent with the best specialization match
        for role in task.required_roles:
            best_agent = None
            best_score = 0.0
            
            for agent in available_agents:
                if agent in team.agents:
                    continue  # Skip agents already in the team
                
                # Calculate capability match score
                capability_score = agent.capability_match_score(role.required_capabilities)
                
                # Skip agents that don't meet the minimum capability threshold
                if capability_score < self.capability_match_threshold:
                    continue
                
                # Calculate specialization score
                specialization_score = 1.0 if agent.specialization == role.name else 0.2
                
                # Combined score with heavy weight on specialization
                combined_score = capability_score * 0.3 + specialization_score * 0.7
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_agent = agent
            
            if best_agent:
                team.agents.append(best_agent)
                team.role_assignments[role.id] = best_agent.id
                available_agents.remove(best_agent)  # Remove from available pool
    
    def _form_team_cost_optimized(self, team: Team, available_agents: List[Agent]) -> None:
        """Form a team optimized for cost efficiency."""
        task = team.task
        if not task:
            return
        
        # For each required role, find the agent with the best cost-performance ratio
        for role in task.required_roles:
            best_agent = None
            best_score = 0.0
            
            for agent in available_agents:
                if agent in team.agents:
                    continue  # Skip agents already in the team
                
                # Calculate capability match score
                capability_score = agent.capability_match_score(role.required_capabilities)
                
                # Skip agents that don't meet the minimum capability threshold
                if capability_score < self.capability_match_threshold:
                    continue
                
                # Calculate performance score
                performance_score = agent.get_performance_for_task_type(task.task_type)
                
                # Calculate cost efficiency (higher is better)
                cost_efficiency = performance_score / (agent.cost_per_token + 0.0001)  # Avoid division by zero
                
                # Combined score with heavy weight on cost efficiency
                combined_score = capability_score * 0.3 + cost_efficiency * 0.7
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_agent = agent
            
            if best_agent:
                team.agents.append(best_agent)
                team.role_assignments[role.id] = best_agent.id
                available_agents.remove(best_agent)  # Remove from available pool
    
    def _form_team_balanced(self, team: Team, available_agents: List[Agent]) -> None:
        """Form a team with a balanced approach considering all factors."""
        task = team.task
        if not task:
            return
        
        # For each required role, find the agent with the best overall score
        for role in task.required_roles:
            best_agent = None
            best_score = 0.0
            
            for agent in available_agents:
                if agent in team.agents:
                    continue  # Skip agents already in the team
                
                # Calculate capability match score
                capability_score = agent.capability_match_score(role.required_capabilities)
                
                # Skip agents that don't meet the minimum capability threshold
                if capability_score < self.capability_match_threshold:
                    continue
                
                # Calculate performance score
                performance_score = agent.get_performance_for_task_type(task.task_type) / 10.0  # Normalize to 0-1
                
                # Calculate specialization score
                specialization_score = 1.0 if agent.specialization == role.name else 0.2
                
                # Calculate collaboration score
                collaboration_score = agent.collaboration_score
                
                # Calculate cost efficiency
                cost_efficiency = 1.0 - min(1.0, agent.cost_per_token / 0.01)  # Normalize to 0-1, higher is better
                
                # Combined score with balanced weights
                combined_score = (
                    capability_score * 0.3 +
                    performance_score * self.performance_weight +
                    specialization_score * self.specialization_weight +
                    collaboration_score * self.collaboration_weight +
                    cost_efficiency * self.cost_weight
                )
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_agent = agent
            
            if best_agent:
                team.agents.append(best_agent)
                team.role_assignments[role.id] = best_agent.id
                available_agents.remove(best_agent)  # Remove from available pool
    
    def _form_team_hybrid(self, team: Team, available_agents: List[Agent]) -> None:
        """
        Form a team using a hybrid approach that adapts based on task characteristics.
        This strategy dynamically adjusts weights based on task complexity, deadline, and type.
        """
        task = team.task
        if not task:
            return
        
        # Adjust weights based on task characteristics
        adjusted_performance_weight = self.performance_weight
        adjusted_specialization_weight = self.specialization_weight
        adjusted_collaboration_weight = self.collaboration_weight
        adjusted_cost_weight = self.cost_weight
        
        # Adjust for task complexity
        if task.complexity > 7:  # High complexity
            adjusted_performance_weight *= 1.5
            adjusted_specialization_weight *= 1.2
        elif task.complexity < 3:  # Low complexity
            adjusted_cost_weight *= 1.5
        
        # Adjust for deadline pressure
        if task.deadline and (task.deadline - time.time()) < 3600:  # Less than 1 hour
            adjusted_performance_weight *= 1.5
            adjusted_cost_weight *= 0.5  # Cost less important under time pressure
        
        # Adjust for task type
        if task.task_type == "creative":
            adjusted_specialization_weight *= 1.3
        elif task.task_type == "analytical":
            adjusted_performance_weight *= 1.3
        
        # Normalize weights
        total_weight = (adjusted_performance_weight + adjusted_specialization_weight + 
                        adjusted_collaboration_weight + adjusted_cost_weight)
        
        adjusted_performance_weight /= total_weight
        adjusted_specialization_weight /= total_weight
        adjusted_collaboration_weight /= total_weight
        adjusted_cost_weight /= total_weight
        
        # For each required role, find the agent with the best score using adjusted weights
        for role in task.required_roles:
            best_agent = None
            best_score = 0.0
            
            for agent in available_agents:
                if agent in team.agents:
                    continue  # Skip agents already in the team
                
                # Calculate capability match score
                capability_score = agent.capability_match_score(role.required_capabilities)
                
                # Skip agents that don't meet the minimum capability threshold
                if capability_score < self.capability_match_threshold:
                    continue
                
                # Calculate performance score
                performance_score = agent.get_performance_for_task_type(task.task_type) / 10.0  # Normalize to 0-1
                
                # Calculate specialization score
                specialization_score = 1.0 if agent.specialization == role.name else 0.2
                
                # Calculate collaboration score
                collaboration_score = agent.collaboration_score
                
                # Calculate cost efficiency
                cost_efficiency = 1.0 - min(1.0, agent.cost_per_token / 0.01)  # Normalize to 0-1, higher is better
                
                # Combined score with adjusted weights
                combined_score = (
                    capability_score * 0.3 +  # Capability always has fixed weight
                    performance_score * adjusted_performance_weight +
                    specialization_score * adjusted_specialization_weight +
                    collaboration_score * adjusted_collaboration_weight +
                    cost_efficiency * adjusted_cost_weight
                )
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_agent = agent
            
            if best_agent:
                team.agents.append(best_agent)
                team.role_assignments[role.id] = best_agent.id
                available_agents.remove(best_agent)  # Remove from available pool
    
    def _calculate_capability_coverage(self, team: Team) -> float:
        """Calculate how well the team covers the required capabilities for the task."""
        task = team.task
        if not task or not task.required_capabilities:
            return 1.0
        
        # Collect all capabilities from team members
        team_capabilities = set()
        for agent in team.agents:
            team_capabilities.update(agent.capabilities)
        
        # Calculate coverage
        covered_capabilities = team_capabilities.intersection(task.required_capabilities)
        return len(covered_capabilities) / len(task.required_capabilities)
    
    def optimize_team(self, team: Team) -> Team:
        """
        Optimize an existing team by suggesting agent replacements that could improve
        overall team performance.
        
        Args:
            team: The team to optimize
            
        Returns:
            The optimized team
        """
        logger.info(f"Optimizing team: {team.name}")
        
        if not team.task:
            logger.warning("Cannot optimize team without associated task")
            return team
        
        # Get all available agents not currently in the team
        available_agents = [agent for agent in self.get_available_agents() if agent not in team.agents]
        
        # For each role in the team, check if there's a better agent available
        team_improved = False
        
        for role_id, current_agent_id in team.role_assignments.items():
            role = self.role_registry.get(role_id)
            if not role:
                continue
            
            current_agent = None
            for agent in team.agents:
                if agent.id == current_agent_id:
                    current_agent = agent
                    break
            
            if not current_agent:
                continue
            
            # Calculate current agent's score
            current_score = self._calculate_agent_role_score(current_agent, role, team.task)
            
            # Find potential replacement with better score
            best_replacement = None
            best_replacement_score = current_score
            
            for candidate in available_agents:
                candidate_score = self._calculate_agent_role_score(candidate, role, team.task)
                if candidate_score > best_replacement_score:
                    best_replacement = candidate
                    best_replacement_score = candidate_score
            
            # Replace agent if better candidate found
            if best_replacement:
                # Update team
                team.agents.remove(current_agent)
                team.agents.append(best_replacement)
                team.role_assignments[role_id] = best_replacement.id
                
                # Update available agents
                available_agents.remove(best_replacement)
                available_agents.append(current_agent)
                
                team_improved = True
                logger.info(f"Optimized team by replacing {current_agent.name} with {best_replacement.name} for role {role.name}")
        
        if team_improved:
            # Recalculate team performance metrics
            team.performance_metrics["overall"] = team.calculate_team_performance()
            team.performance_metrics["capability_coverage"] = self._calculate_capability_coverage(team)
        
        return team
    
    def _calculate_agent_role_score(self, agent: Agent, role: Role, task: Task) -> float:
        """Calculate a comprehensive score for an agent's suitability for a role."""
        # Calculate capability match score
        capability_score = agent.capability_match_score(role.required_capabilities)
        
        # Calculate performance score
        performance_score = agent.get_performance_for_task_type(task.task_type) / 10.0  # Normalize to 0-1
        
        # Calculate specialization score
        specialization_score = 1.0 if agent.specialization == role.name else 0.2
        
        # Calculate collaboration score
        collaboration_score = agent.collaboration_score
        
        # Calculate cost efficiency
        cost_efficiency = 1.0 - min(1.0, agent.cost_per_token / 0.01)  # Normalize to 0-1, higher is better
        
        # Combined score with balanced weights
        return (
            capability_score * 0.3 +
            performance_score * self.performance_weight +
            specialization_score * self.specialization_weight +
            collaboration_score * self.collaboration_weight +
            cost_efficiency * self.cost_weight
        )
    
    def analyze_team_formation_history(self) -> Dict[str, Any]:
        """
        Analyze team formation history to extract insights and patterns.
        
        Returns:
            A dictionary of analysis results
        """
        if not self.team_history:
            return {"status": "No team formation history available"}
        
        analysis = {}
        
        # Basic statistics
        analysis["total_teams_formed"] = len(self.team_history)
        analysis["complete_teams"] = sum(1 for team in self.team_history if team.status == "COMPLETE")
        analysis["partial_teams"] = sum(1 for team in self.team_history if team.status == "PARTIAL")
        analysis["failed_teams"] = sum(1 for team in self.team_history if team.status == "FAILED")
        
        # Performance metrics
        if analysis["total_teams_formed"] > 0:
            analysis["avg_team_performance"] = sum(team.performance_metrics.get("overall", 0) 
                                                for team in self.team_history) / analysis["total_teams_formed"]
            
            analysis["avg_capability_coverage"] = sum(team.performance_metrics.get("capability_coverage", 0) 
                                                   for team in self.team_history) / analysis["total_teams_formed"]
            
            analysis["avg_role_coverage"] = sum(team.performance_metrics.get("role_coverage", 0) 
                                             for team in self.team_history) / analysis["total_teams_formed"]
        
        # Agent utilization
        agent_utilization = {}
        for team in self.team_history:
            for agent in team.agents:
                agent_utilization[agent.id] = agent_utilization.get(agent.id, 0) + 1
        
        analysis["agent_utilization"] = agent_utilization
        
        # Most utilized agents
        if agent_utilization:
            analysis["most_utilized_agents"] = sorted(agent_utilization.items(), 
                                                    key=lambda x: x[1], reverse=True)[:5]
        
        # Role difficulty (how often roles couldn't be filled)
        role_difficulty = {}
        for team in self.team_history:
            if team.task:
                for role in team.task.required_roles:
                    if role.id not in team.role_assignments:
                        role_difficulty[role.id] = role_difficulty.get(role.id, 0) + 1
        
        analysis["role_difficulty"] = role_difficulty
        
        return analysis
    
    def get_team_recommendations(self, task: Task, count: int = 3) -> List[Team]:
        """
        Generate multiple team recommendations for a task using different strategies.
        
        Args:
            task: The task for which to generate team recommendations
            count: The number of recommendations to generate
            
        Returns:
            A list of recommended teams
        """
        recommendations = []
        
        # Generate recommendations using different strategies
        strategies = list(TeamFormationStrategy)
        
        # Ensure we don't try to generate more recommendations than we have strategies
        count = min(count, len(strategies))
        
        for i in range(count):
            strategy = strategies[i % len(strategies)]
            team = self.form_team_for_task(task, strategy)
            recommendations.append(team)
        
        # Sort recommendations by performance
        recommendations.sort(key=lambda t: t.performance_metrics.get("overall", 0), reverse=True)
        
        return recommendations
    
    def update_agent_collaboration_scores(self, team: Team, success_rating: float) -> None:
        """
        Update collaboration scores for agents based on team performance.
        
        Args:
            team: The team whose agents' collaboration scores should be updated
            success_rating: A rating of how successful the team was (0.0 to 1.0)
        """
        if not team.agents:
            return
        
        # Update collaboration scores for all agents in the team
        for agent in team.agents:
            if agent.id in self.agent_registry:
                stored_agent = self.agent_registry[agent.id]
                
                # Update collaboration score with exponential moving average
                alpha = 0.3  # Weight for new observation
                old_score = stored_agent.collaboration_score
                new_score = alpha * success_rating + (1 - alpha) * old_score
                stored_agent.collaboration_score = new_score
                
                logger.info(f"Updated collaboration score for {stored_agent.name}: {old_score:.2f} -> {new_score:.2f}")
