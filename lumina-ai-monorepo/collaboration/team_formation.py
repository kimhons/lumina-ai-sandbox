"""
Agent Team Formation Service for Advanced Multi-Agent Collaboration.

This module implements the Agent Team Formation Service, which is responsible for
creating and managing teams of agents based on task requirements and agent capabilities.
"""

from typing import Dict, List, Optional, Set, Tuple
import uuid
import time
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Enum representing different agent capabilities."""
    REASONING = "reasoning"
    RESEARCH = "research"
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE_WRITING = "creative_writing"
    PLANNING = "planning"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    MATH = "math"
    DOMAIN_EXPERT = "domain_expert"


@dataclass
class AgentProfile:
    """Represents an agent's profile with capabilities and performance metrics."""
    agent_id: str
    name: str
    capabilities: Dict[AgentCapability, float] = field(default_factory=dict)
    specializations: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    availability: float = 1.0  # 0.0 to 1.0, representing percentage of availability
    current_load: float = 0.0  # 0.0 to 1.0, representing current workload
    
    def can_handle(self, required_capability: AgentCapability, min_proficiency: float = 0.5) -> bool:
        """Check if agent can handle a required capability with minimum proficiency."""
        return required_capability in self.capabilities and self.capabilities[required_capability] >= min_proficiency
    
    def has_specialization(self, domain: str) -> bool:
        """Check if agent has specialization in a specific domain."""
        return domain in self.specializations
    
    def is_available(self, required_availability: float = 0.2) -> bool:
        """Check if agent has enough availability."""
        return self.availability >= required_availability and self.current_load < 0.8
    
    def get_capability_score(self, capability: AgentCapability) -> float:
        """Get the agent's proficiency score for a capability."""
        return self.capabilities.get(capability, 0.0)
    
    def update_load(self, load_delta: float) -> None:
        """Update the agent's current load."""
        self.current_load = max(0.0, min(1.0, self.current_load + load_delta))


@dataclass
class TaskRequirement:
    """Represents requirements for a task."""
    task_id: str
    name: str
    description: str
    required_capabilities: Dict[AgentCapability, float] = field(default_factory=dict)
    domain_specializations: List[str] = field(default_factory=list)
    priority: int = 1  # 1 to 10, with 10 being highest priority
    estimated_duration: float = 1.0  # in hours
    complexity: int = 5  # 1 to 10, with 10 being most complex
    min_team_size: int = 1
    max_team_size: int = 5


@dataclass
class AgentTeam:
    """Represents a team of agents formed for a specific task."""
    team_id: str
    task_id: str
    members: Dict[str, AgentProfile] = field(default_factory=dict)
    roles: Dict[str, List[AgentCapability]] = field(default_factory=dict)
    formation_time: float = field(default_factory=time.time)
    performance_score: float = 0.0
    status: str = "forming"  # forming, active, completed, disbanded
    
    def add_member(self, agent: AgentProfile, roles: List[AgentCapability]) -> None:
        """Add a member to the team with specified roles."""
        self.members[agent.agent_id] = agent
        self.roles[agent.agent_id] = roles
        
    def remove_member(self, agent_id: str) -> bool:
        """Remove a member from the team."""
        if agent_id in self.members:
            del self.members[agent_id]
            del self.roles[agent_id]
            return True
        return False
    
    def get_capability_coverage(self) -> Dict[AgentCapability, float]:
        """Get the team's coverage of capabilities."""
        coverage = {}
        for agent_id, roles in self.roles.items():
            agent = self.members[agent_id]
            for capability in roles:
                current_score = coverage.get(capability, 0.0)
                agent_score = agent.get_capability_score(capability)
                coverage[capability] = max(current_score, agent_score)
        return coverage
    
    def get_size(self) -> int:
        """Get the team size."""
        return len(self.members)
    
    def update_status(self, status: str) -> None:
        """Update the team status."""
        self.status = status
        
    def update_performance_score(self, score: float) -> None:
        """Update the team performance score."""
        self.performance_score = score


class AgentCapabilityRegistry:
    """Registry for agent capabilities and profiles."""
    
    def __init__(self):
        self.agents: Dict[str, AgentProfile] = {}
        
    def register_agent(self, agent: AgentProfile) -> None:
        """Register an agent in the registry."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent {agent.name} with ID {agent.agent_id}")
        
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            logger.info(f"Unregistered agent {agent.name} with ID {agent_id}")
            return True
        return False
        
    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def find_agents_by_capability(self, capability: AgentCapability, min_proficiency: float = 0.5) -> List[AgentProfile]:
        """Find agents with a specific capability."""
        return [
            agent for agent in self.agents.values() 
            if agent.can_handle(capability, min_proficiency)
        ]
    
    def find_agents_by_specialization(self, domain: str) -> List[AgentProfile]:
        """Find agents with a specific domain specialization."""
        return [
            agent for agent in self.agents.values() 
            if agent.has_specialization(domain)
        ]
    
    def find_available_agents(self, required_availability: float = 0.2) -> List[AgentProfile]:
        """Find agents that are currently available."""
        return [
            agent for agent in self.agents.values() 
            if agent.is_available(required_availability)
        ]
    
    def update_agent_metrics(self, agent_id: str, metrics: Dict[str, float]) -> bool:
        """Update an agent's performance metrics."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.performance_metrics.update(metrics)
            return True
        return False
    
    def update_agent_load(self, agent_id: str, load_delta: float) -> bool:
        """Update an agent's current load."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.update_load(load_delta)
            return True
        return False


class TeamPerformanceMonitor:
    """Monitors and evaluates team performance."""
    
    def __init__(self):
        self.team_metrics: Dict[str, Dict[str, float]] = {}
        
    def record_metric(self, team_id: str, metric_name: str, value: float) -> None:
        """Record a performance metric for a team."""
        if team_id not in self.team_metrics:
            self.team_metrics[team_id] = {}
        self.team_metrics[team_id][metric_name] = value
        
    def get_team_metrics(self, team_id: str) -> Dict[str, float]:
        """Get all metrics for a team."""
        return self.team_metrics.get(team_id, {})
    
    def calculate_performance_score(self, team_id: str) -> float:
        """Calculate an overall performance score for a team."""
        metrics = self.get_team_metrics(team_id)
        if not metrics:
            return 0.0
        
        # Example scoring algorithm - can be customized
        score = 0.0
        weights = {
            "task_completion_rate": 0.4,
            "quality_score": 0.3,
            "efficiency_score": 0.2,
            "collaboration_score": 0.1
        }
        
        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
                
        return score
    
    def compare_teams(self, team_ids: List[str]) -> Dict[str, float]:
        """Compare performance scores of multiple teams."""
        return {
            team_id: self.calculate_performance_score(team_id)
            for team_id in team_ids
        }


class TeamFormationStrategy:
    """Base class for team formation strategies."""
    
    def form_team(
        self, 
        task: TaskRequirement, 
        available_agents: List[AgentProfile]
    ) -> AgentTeam:
        """Form a team for a task from available agents."""
        raise NotImplementedError("Subclasses must implement form_team method")


class OptimalCoverageStrategy(TeamFormationStrategy):
    """Strategy that optimizes for capability coverage."""
    
    def form_team(
        self, 
        task: TaskRequirement, 
        available_agents: List[AgentProfile]
    ) -> AgentTeam:
        """Form a team optimizing for capability coverage."""
        team = AgentTeam(
            team_id=f"team-{uuid.uuid4()}",
            task_id=task.task_id
        )
        
        # Sort agents by their capability scores for required capabilities
        scored_agents = []
        for agent in available_agents:
            total_score = 0.0
            covered_capabilities = set()
            for capability, min_proficiency in task.required_capabilities.items():
                if agent.can_handle(capability, min_proficiency):
                    score = agent.get_capability_score(capability)
                    total_score += score
                    covered_capabilities.add(capability)
            
            # Add domain specialization bonus
            for domain in task.domain_specializations:
                if agent.has_specialization(domain):
                    total_score += 2.0
            
            scored_agents.append((agent, total_score, covered_capabilities))
        
        # Sort by score in descending order
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        # Track which capabilities we've covered
        covered_capabilities: Set[AgentCapability] = set()
        
        # Add agents until we've covered all capabilities or reached max team size
        for agent, score, agent_capabilities in scored_agents:
            if team.get_size() >= task.max_team_size:
                break
                
            # If we've covered all capabilities and reached min team size, we're done
            if (covered_capabilities == set(task.required_capabilities.keys()) and 
                team.get_size() >= task.min_team_size):
                break
                
            # Determine which capabilities this agent should handle
            assigned_capabilities = [
                capability for capability in agent_capabilities
                if capability not in covered_capabilities or 
                agent.get_capability_score(capability) > 0.8  # High proficiency specialists can double up
            ]
            
            if assigned_capabilities:
                team.add_member(agent, assigned_capabilities)
                covered_capabilities.update(agent_capabilities)
        
        # Check if we've formed a valid team
        if team.get_size() < task.min_team_size:
            logger.warning(f"Could not form team with minimum size {task.min_team_size} for task {task.task_id}")
            
        coverage = team.get_capability_coverage()
        missing_capabilities = set(task.required_capabilities.keys()) - set(coverage.keys())
        if missing_capabilities:
            logger.warning(f"Team missing capabilities {missing_capabilities} for task {task.task_id}")
            
        return team


class BalancedWorkloadStrategy(TeamFormationStrategy):
    """Strategy that balances workload across agents."""
    
    def form_team(
        self, 
        task: TaskRequirement, 
        available_agents: List[AgentProfile]
    ) -> AgentTeam:
        """Form a team balancing workload across agents."""
        team = AgentTeam(
            team_id=f"team-{uuid.uuid4()}",
            task_id=task.task_id
        )
        
        # Filter agents that can handle at least one required capability
        qualified_agents = []
        for agent in available_agents:
            for capability, min_proficiency in task.required_capabilities.items():
                if agent.can_handle(capability, min_proficiency):
                    qualified_agents.append(agent)
                    break
        
        # Sort by current load in ascending order (least loaded first)
        qualified_agents.sort(key=lambda x: x.current_load)
        
        # Track which capabilities we've covered
        covered_capabilities: Set[AgentCapability] = set()
        
        # Add agents until we've covered all capabilities or reached max team size
        for agent in qualified_agents:
            if team.get_size() >= task.max_team_size:
                break
                
            # If we've covered all capabilities and reached min team size, we're done
            if (covered_capabilities == set(task.required_capabilities.keys()) and 
                team.get_size() >= task.min_team_size):
                break
                
            # Determine which capabilities this agent should handle
            assigned_capabilities = []
            for capability, min_proficiency in task.required_capabilities.items():
                if agent.can_handle(capability, min_proficiency):
                    if capability not in covered_capabilities:
                        assigned_capabilities.append(capability)
                        covered_capabilities.add(capability)
            
            if assigned_capabilities:
                team.add_member(agent, assigned_capabilities)
        
        # Check if we've formed a valid team
        if team.get_size() < task.min_team_size:
            logger.warning(f"Could not form team with minimum size {task.min_team_size} for task {task.task_id}")
            
        coverage = team.get_capability_coverage()
        missing_capabilities = set(task.required_capabilities.keys()) - set(coverage.keys())
        if missing_capabilities:
            logger.warning(f"Team missing capabilities {missing_capabilities} for task {task.task_id}")
            
        return team


class TeamFormationManager:
    """Main manager for team formation and management."""
    
    def __init__(
        self, 
        capability_registry: AgentCapabilityRegistry,
        performance_monitor: TeamPerformanceMonitor
    ):
        self.capability_registry = capability_registry
        self.performance_monitor = performance_monitor
        self.teams: Dict[str, AgentTeam] = {}
        self.strategies: Dict[str, TeamFormationStrategy] = {
            "optimal_coverage": OptimalCoverageStrategy(),
            "balanced_workload": BalancedWorkloadStrategy()
        }
        
    def create_team(
        self, 
        task: TaskRequirement, 
        strategy_name: str = "optimal_coverage"
    ) -> Optional[AgentTeam]:
        """Create a team for a task using the specified strategy."""
        if strategy_name not in self.strategies:
            logger.error(f"Unknown team formation strategy: {strategy_name}")
            return None
            
        strategy = self.strategies[strategy_name]
        
        # Get available agents
        available_agents = self.capability_registry.find_available_agents()
        
        # Form the team
        team = strategy.form_team(task, available_agents)
        
        # Update agent loads
        for agent_id, agent in team.members.items():
            # Estimate load based on task complexity and duration
            load_increase = (task.complexity / 10.0) * (task.estimated_duration / 8.0)
            self.capability_registry.update_agent_load(agent_id, load_increase)
        
        # Store the team
        self.teams[team.team_id] = team
        logger.info(f"Created team {team.team_id} for task {task.task_id} with {team.get_size()} members")
        
        return team
    
    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        """Get a team by ID."""
        return self.teams.get(team_id)
    
    def get_teams_for_task(self, task_id: str) -> List[AgentTeam]:
        """Get all teams for a specific task."""
        return [team for team in self.teams.values() if team.task_id == task_id]
    
    def disband_team(self, team_id: str) -> bool:
        """Disband a team and release its members."""
        if team_id not in self.teams:
            return False
            
        team = self.teams[team_id]
        
        # Update agent loads
        for agent_id in team.members:
            self.capability_registry.update_agent_load(agent_id, -0.2)  # Reduce load
            
        # Update team status
        team.update_status("disbanded")
        
        # Remove from active teams
        del self.teams[team_id]
        
        logger.info(f"Disbanded team {team_id}")
        return True
    
    def update_team_performance(self, team_id: str, metrics: Dict[str, float]) -> bool:
        """Update performance metrics for a team."""
        if team_id not in self.teams:
            return False
            
        for metric_name, value in metrics.items():
            self.performance_monitor.record_metric(team_id, metric_name, value)
            
        score = self.performance_monitor.calculate_performance_score(team_id)
        self.teams[team_id].update_performance_score(score)
        
        return True
    
    def adjust_team_composition(self, team_id: str) -> bool:
        """Adjust team composition based on performance."""
        if team_id not in self.teams:
            return False
            
        team = self.teams[team_id]
        
        # If team is performing well, no need to adjust
        if team.performance_score >= 0.7:
            return True
            
        # Get task requirements
        # In a real implementation, this would retrieve the task from a task repository
        # For now, we'll just use a placeholder
        task = TaskRequirement(
            task_id=team.task_id,
            name="Placeholder Task",
            description="Placeholder task for team adjustment",
            required_capabilities={
                capability: 0.6 for capability in 
                set().union(*[set(roles) for roles in team.roles.values()])
            }
        )
        
        # Get available agents not already in the team
        available_agents = [
            agent for agent in self.capability_registry.find_available_agents()
            if agent.agent_id not in team.members
        ]
        
        # Check team coverage
        coverage = team.get_capability_coverage()
        missing_capabilities = set(task.required_capabilities.keys()) - set(coverage.keys())
        weak_capabilities = [
            capability for capability, score in coverage.items()
            if score < task.required_capabilities.get(capability, 0.0)
        ]
        
        # If no issues, no need to adjust
        if not missing_capabilities and not weak_capabilities:
            return True
            
        # Try to find agents to cover missing or weak capabilities
        for capability in list(missing_capabilities) + weak_capabilities:
            if team.get_size() >= task.max_team_size:
                break
                
            candidates = [
                agent for agent in available_agents
                if agent.can_handle(capability, task.required_capabilities.get(capability, 0.5))
            ]
            
            if candidates:
                # Sort by proficiency
                candidates.sort(
                    key=lambda x: x.get_capability_score(capability),
                    reverse=True
                )
                
                # Add the best candidate
                best_agent = candidates[0]
                team.add_member(best_agent, [capability])
                
                # Update agent load
                load_increase = (task.complexity / 10.0) * (task.estimated_duration / 8.0)
                self.capability_registry.update_agent_load(best_agent.agent_id, load_increase)
                
                logger.info(f"Added agent {best_agent.agent_id} to team {team_id} for capability {capability}")
        
        return True
    
    def register_strategy(self, name: str, strategy: TeamFormationStrategy) -> None:
        """Register a new team formation strategy."""
        self.strategies[name] = strategy
        logger.info(f"Registered team formation strategy: {name}")
