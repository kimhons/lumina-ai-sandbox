"""
Task Negotiation Protocol for Advanced Multi-Agent Collaboration.

This module implements the Task Negotiation Protocol, which enables agents to negotiate
task allocation, priorities, and resource usage.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, Union
import uuid
import time
import logging
import copy
import random
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class NegotiationStatus(Enum):
    """Enum representing different negotiation statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class NegotiationType(Enum):
    """Enum representing different negotiation types."""
    TASK_ALLOCATION = "task_allocation"
    RESOURCE_ALLOCATION = "resource_allocation"
    PRIORITY_SETTING = "priority_setting"
    CONFLICT_RESOLUTION = "conflict_resolution"
    TASK_REASSIGNMENT = "task_reassignment"


class ProposalStatus(Enum):
    """Enum representing different proposal statuses."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    WITHDRAWN = "withdrawn"


@dataclass
class TaskDetails:
    """Represents details of a task for negotiation."""
    task_id: str
    name: str
    description: str
    estimated_duration: float  # in hours
    complexity: int  # 1-10
    priority: int  # 1-10
    dependencies: List[str] = field(default_factory=list)  # list of task_ids
    required_resources: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NegotiationProposal:
    """Represents a proposal in a negotiation."""
    proposal_id: str
    negotiation_id: str
    proposer_id: str
    proposal_type: NegotiationType
    content: Dict[str, Any]
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    responses: Dict[str, str] = field(default_factory=dict)  # agent_id -> response
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Negotiation:
    """Represents a negotiation between agents."""
    negotiation_id: str
    negotiation_type: NegotiationType
    initiator_id: str
    participants: List[str]
    status: NegotiationStatus = NegotiationStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)
    proposals: List[NegotiationProposal] = field(default_factory=list)
    outcome: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskAllocationStrategy:
    """Base class for task allocation strategies."""
    
    def allocate_tasks(
        self, 
        tasks: List[TaskDetails], 
        agents: List[str],
        agent_capabilities: Optional[Dict[str, Dict[str, float]]] = None,
        agent_workloads: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[str]]:
        """
        Allocate tasks to agents.
        
        Args:
            tasks: List of tasks to allocate
            agents: List of agent IDs
            agent_capabilities: Optional dict mapping agent IDs to capability scores
            agent_workloads: Optional dict mapping agent IDs to current workloads
            
        Returns:
            Dict mapping agent IDs to lists of task IDs
        """
        raise NotImplementedError("Subclasses must implement allocate_tasks method")


class RoundRobinAllocationStrategy(TaskAllocationStrategy):
    """Strategy that allocates tasks in a round-robin fashion."""
    
    def allocate_tasks(
        self, 
        tasks: List[TaskDetails], 
        agents: List[str],
        agent_capabilities: Optional[Dict[str, Dict[str, float]]] = None,
        agent_workloads: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[str]]:
        """Allocate tasks in a round-robin fashion."""
        allocation = {agent_id: [] for agent_id in agents}
        
        # Sort tasks by priority (highest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        # Allocate tasks in round-robin fashion
        for i, task in enumerate(sorted_tasks):
            agent_id = agents[i % len(agents)]
            allocation[agent_id].append(task.task_id)
            
        return allocation


class WorkloadBalancingStrategy(TaskAllocationStrategy):
    """Strategy that balances workload across agents."""
    
    def allocate_tasks(
        self, 
        tasks: List[TaskDetails], 
        agents: List[str],
        agent_capabilities: Optional[Dict[str, Dict[str, float]]] = None,
        agent_workloads: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[str]]:
        """Allocate tasks to balance workload."""
        allocation = {agent_id: [] for agent_id in agents}
        
        # Initialize workloads if not provided
        if agent_workloads is None:
            agent_workloads = {agent_id: 0.0 for agent_id in agents}
        else:
            # Make a copy to avoid modifying the original
            agent_workloads = copy.deepcopy(agent_workloads)
            
        # Sort tasks by estimated duration (longest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.estimated_duration, reverse=True)
        
        # Allocate tasks to the agent with the lowest workload
        for task in sorted_tasks:
            # Find agent with lowest workload
            agent_id = min(agent_workloads.keys(), key=lambda a: agent_workloads[a])
            
            # Allocate task
            allocation[agent_id].append(task.task_id)
            
            # Update workload
            agent_workloads[agent_id] += task.estimated_duration
            
        return allocation


class CapabilityMatchingStrategy(TaskAllocationStrategy):
    """Strategy that matches tasks to agents based on capabilities."""
    
    def allocate_tasks(
        self, 
        tasks: List[TaskDetails], 
        agents: List[str],
        agent_capabilities: Optional[Dict[str, Dict[str, float]]] = None,
        agent_workloads: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[str]]:
        """Allocate tasks based on capability matching."""
        allocation = {agent_id: [] for agent_id in agents}
        
        # If no capabilities provided, fall back to round-robin
        if agent_capabilities is None:
            return RoundRobinAllocationStrategy().allocate_tasks(tasks, agents)
            
        # Initialize workloads if not provided
        if agent_workloads is None:
            agent_workloads = {agent_id: 0.0 for agent_id in agents}
        else:
            # Make a copy to avoid modifying the original
            agent_workloads = copy.deepcopy(agent_workloads)
            
        # For each task, find the best agent
        for task in tasks:
            best_agent = None
            best_score = -1.0
            
            # Extract required capabilities from task metadata
            required_capabilities = task.metadata.get("required_capabilities", {})
            
            for agent_id in agents:
                # Calculate capability match score
                score = 0.0
                agent_caps = agent_capabilities.get(agent_id, {})
                
                if required_capabilities:
                    # If specific capabilities are required, match against them
                    for cap, weight in required_capabilities.items():
                        score += agent_caps.get(cap, 0.0) * weight
                else:
                    # Otherwise, use average of all capabilities
                    if agent_caps:
                        score = sum(agent_caps.values()) / len(agent_caps)
                
                # Adjust score based on workload (lower workload is better)
                workload_factor = 1.0 - min(agent_workloads.get(agent_id, 0.0) / 10.0, 0.9)
                score *= workload_factor
                
                if score > best_score:
                    best_score = score
                    best_agent = agent_id
            
            # Allocate task to best agent
            if best_agent:
                allocation[best_agent].append(task.task_id)
                agent_workloads[best_agent] += task.estimated_duration
            else:
                # Fallback if no suitable agent found
                agent_id = min(agent_workloads.keys(), key=lambda a: agent_workloads[a])
                allocation[agent_id].append(task.task_id)
                agent_workloads[agent_id] += task.estimated_duration
            
        return allocation


class ConflictResolutionService:
    """Service for resolving conflicts in negotiations."""
    
    def resolve_conflict(
        self, 
        negotiation: Negotiation,
        proposals: List[NegotiationProposal]
    ) -> Optional[NegotiationProposal]:
        """
        Resolve a conflict between multiple proposals.
        
        Args:
            negotiation: The negotiation context
            proposals: List of conflicting proposals
            
        Returns:
            The resolved proposal, or None if resolution failed
        """
        if not proposals:
            return None
            
        # Default to the proposal with the most acceptances
        best_proposal = None
        best_acceptance_count = -1
        
        for proposal in proposals:
            acceptance_count = sum(1 for response in proposal.responses.values() if response == "accept")
            if acceptance_count > best_acceptance_count:
                best_acceptance_count = acceptance_count
                best_proposal = proposal
                
        return best_proposal
    
    def suggest_compromise(
        self, 
        negotiation: Negotiation,
        proposals: List[NegotiationProposal]
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest a compromise between conflicting proposals.
        
        Args:
            negotiation: The negotiation context
            proposals: List of conflicting proposals
            
        Returns:
            A compromise proposal content, or None if compromise is not possible
        """
        if not proposals or len(proposals) < 2:
            return None
            
        # The compromise strategy depends on the negotiation type
        if negotiation.negotiation_type == NegotiationType.TASK_ALLOCATION:
            return self._compromise_task_allocation(proposals)
        elif negotiation.negotiation_type == NegotiationType.RESOURCE_ALLOCATION:
            return self._compromise_resource_allocation(proposals)
        elif negotiation.negotiation_type == NegotiationType.PRIORITY_SETTING:
            return self._compromise_priority_setting(proposals)
        else:
            # For other types, no specific compromise strategy
            return None
    
    def _compromise_task_allocation(
        self, 
        proposals: List[NegotiationProposal]
    ) -> Optional[Dict[str, Any]]:
        """Suggest a compromise for task allocation."""
        # Combine all allocations, giving preference to agents who specifically requested tasks
        combined_allocation = {}
        
        # First pass: collect all agent-task preferences
        agent_preferences = {}
        for proposal in proposals:
            allocation = proposal.content.get("allocation", {})
            for agent_id, task_ids in allocation.items():
                if agent_id not in agent_preferences:
                    agent_preferences[agent_id] = set()
                agent_preferences[agent_id].update(task_ids)
        
        # Second pass: resolve conflicts
        all_tasks = set()
        for preferences in agent_preferences.values():
            all_tasks.update(preferences)
            
        # For each task, assign to the agent who requested it
        # If multiple agents requested it, assign to the one with fewer tasks
        task_assignments = {}
        for task_id in all_tasks:
            candidates = [
                agent_id for agent_id, tasks in agent_preferences.items()
                if task_id in tasks
            ]
            
            if not candidates:
                continue
                
            # Assign to agent with fewest tasks so far
            agent_task_counts = {
                agent_id: len([t for t, a in task_assignments.items() if a == agent_id])
                for agent_id in candidates
            }
            
            best_agent = min(agent_task_counts.keys(), key=lambda a: agent_task_counts[a])
            task_assignments[task_id] = best_agent
        
        # Convert to the expected format
        compromise = {"allocation": {}}
        for task_id, agent_id in task_assignments.items():
            if agent_id not in compromise["allocation"]:
                compromise["allocation"][agent_id] = []
            compromise["allocation"][agent_id].append(task_id)
            
        return compromise
    
    def _compromise_resource_allocation(
        self, 
        proposals: List[NegotiationProposal]
    ) -> Optional[Dict[str, Any]]:
        """Suggest a compromise for resource allocation."""
        # Average the requested resources
        all_resources = set()
        for proposal in proposals:
            resources = proposal.content.get("resources", {})
            all_resources.update(resources.keys())
            
        compromise_resources = {}
        for resource in all_resources:
            # Calculate average requested amount
            values = [
                proposal.content.get("resources", {}).get(resource, 0.0)
                for proposal in proposals
            ]
            non_zero_values = [v for v in values if v > 0]
            if non_zero_values:
                compromise_resources[resource] = sum(non_zero_values) / len(non_zero_values)
            
        return {"resources": compromise_resources}
    
    def _compromise_priority_setting(
        self, 
        proposals: List[NegotiationProposal]
    ) -> Optional[Dict[str, Any]]:
        """Suggest a compromise for priority setting."""
        # Average the requested priorities
        all_tasks = set()
        for proposal in proposals:
            priorities = proposal.content.get("priorities", {})
            all_tasks.update(priorities.keys())
            
        compromise_priorities = {}
        for task_id in all_tasks:
            # Calculate average priority
            values = [
                proposal.content.get("priorities", {}).get(task_id, 0)
                for proposal in proposals
            ]
            non_zero_values = [v for v in values if v > 0]
            if non_zero_values:
                compromise_priorities[task_id] = round(sum(non_zero_values) / len(non_zero_values))
            
        return {"priorities": compromise_priorities}


class NegotiationManager:
    """Main interface for negotiation operations."""
    
    def __init__(
        self,
        conflict_resolver: ConflictResolutionService = None,
        allocation_strategies: Dict[str, TaskAllocationStrategy] = None
    ):
        self.negotiations: Dict[str, Negotiation] = {}
        self.conflict_resolver = conflict_resolver or ConflictResolutionService()
        
        # Initialize allocation strategies
        self.allocation_strategies = allocation_strategies or {
            "round_robin": RoundRobinAllocationStrategy(),
            "workload_balancing": WorkloadBalancingStrategy(),
            "capability_matching": CapabilityMatchingStrategy()
        }
    
    def create_negotiation(
        self,
        negotiation_type: NegotiationType,
        initiator_id: str,
        participants: List[str],
        context: Dict[str, Any] = None,
        deadline: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create a new negotiation.
        
        Args:
            negotiation_type: The type of negotiation
            initiator_id: The ID of the initiating agent
            participants: List of participating agent IDs
            context: Optional context for the negotiation
            deadline: Optional deadline for the negotiation
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created negotiation
        """
        negotiation_id = f"neg-{uuid.uuid4()}"
        
        negotiation = Negotiation(
            negotiation_id=negotiation_id,
            negotiation_type=negotiation_type,
            initiator_id=initiator_id,
            participants=participants,
            status=NegotiationStatus.PENDING,
            deadline=deadline,
            context=context or {},
            metadata=metadata or {}
        )
        
        self.negotiations[negotiation_id] = negotiation
        
        logger.info(f"Created negotiation {negotiation_id} of type {negotiation_type}")
        return negotiation_id
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Negotiation]:
        """Get a negotiation by ID."""
        return self.negotiations.get(negotiation_id)
    
    def start_negotiation(self, negotiation_id: str) -> bool:
        """
        Start a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation to start
            
        Returns:
            True if the negotiation was started, False otherwise
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to start non-existent negotiation {negotiation_id}")
            return False
            
        if negotiation.status != NegotiationStatus.PENDING:
            logger.warning(f"Attempted to start negotiation {negotiation_id} with status {negotiation.status}")
            return False
            
        negotiation.status = NegotiationStatus.ACTIVE
        negotiation.updated_at = time.time()
        
        logger.info(f"Started negotiation {negotiation_id}")
        return True
    
    def cancel_negotiation(self, negotiation_id: str) -> bool:
        """
        Cancel a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation to cancel
            
        Returns:
            True if the negotiation was cancelled, False otherwise
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to cancel non-existent negotiation {negotiation_id}")
            return False
            
        if negotiation.status not in [NegotiationStatus.PENDING, NegotiationStatus.ACTIVE]:
            logger.warning(f"Attempted to cancel negotiation {negotiation_id} with status {negotiation.status}")
            return False
            
        negotiation.status = NegotiationStatus.CANCELLED
        negotiation.updated_at = time.time()
        
        logger.info(f"Cancelled negotiation {negotiation_id}")
        return True
    
    def submit_proposal(
        self,
        negotiation_id: str,
        proposer_id: str,
        proposal_type: NegotiationType,
        content: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Submit a proposal to a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposer_id: The ID of the proposing agent
            proposal_type: The type of proposal
            content: The proposal content
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created proposal, or None if submission failed
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to submit proposal to non-existent negotiation {negotiation_id}")
            return None
            
        if negotiation.status != NegotiationStatus.ACTIVE:
            logger.warning(f"Attempted to submit proposal to negotiation {negotiation_id} with status {negotiation.status}")
            return None
            
        if proposer_id not in negotiation.participants and proposer_id != negotiation.initiator_id:
            logger.warning(f"Agent {proposer_id} is not a participant in negotiation {negotiation_id}")
            return None
            
        proposal_id = f"prop-{uuid.uuid4()}"
        
        proposal = NegotiationProposal(
            proposal_id=proposal_id,
            negotiation_id=negotiation_id,
            proposer_id=proposer_id,
            proposal_type=proposal_type,
            content=content,
            status=ProposalStatus.PENDING,
            metadata=metadata or {}
        )
        
        negotiation.proposals.append(proposal)
        negotiation.updated_at = time.time()
        
        logger.info(f"Submitted proposal {proposal_id} to negotiation {negotiation_id}")
        return proposal_id
    
    def respond_to_proposal(
        self,
        negotiation_id: str,
        proposal_id: str,
        agent_id: str,
        response: str  # "accept", "reject", "counter"
    ) -> bool:
        """
        Respond to a proposal.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposal_id: The ID of the proposal
            agent_id: The ID of the responding agent
            response: The response ("accept", "reject", "counter")
            
        Returns:
            True if the response was recorded, False otherwise
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to respond to proposal in non-existent negotiation {negotiation_id}")
            return False
            
        if negotiation.status != NegotiationStatus.ACTIVE:
            logger.warning(f"Attempted to respond to proposal in negotiation {negotiation_id} with status {negotiation.status}")
            return False
            
        if agent_id not in negotiation.participants and agent_id != negotiation.initiator_id:
            logger.warning(f"Agent {agent_id} is not a participant in negotiation {negotiation_id}")
            return False
            
        # Find the proposal
        proposal = None
        for p in negotiation.proposals:
            if p.proposal_id == proposal_id:
                proposal = p
                break
                
        if not proposal:
            logger.warning(f"Proposal {proposal_id} not found in negotiation {negotiation_id}")
            return False
            
        if proposal.status != ProposalStatus.PENDING:
            logger.warning(f"Attempted to respond to proposal {proposal_id} with status {proposal.status}")
            return False
            
        # Record the response
        proposal.responses[agent_id] = response
        proposal.updated_at = time.time()
        negotiation.updated_at = time.time()
        
        logger.info(f"Agent {agent_id} responded {response} to proposal {proposal_id}")
        
        # Check if all participants have responded
        all_participants = set(negotiation.participants)
        if negotiation.initiator_id not in all_participants:
            all_participants.add(negotiation.initiator_id)
            
        responded_participants = set(proposal.responses.keys())
        
        # Don't count the proposer as needing to respond
        all_participants.discard(proposal.proposer_id)
        
        if responded_participants >= all_participants:
            # All participants have responded, update proposal status
            accept_count = sum(1 for r in proposal.responses.values() if r == "accept")
            reject_count = sum(1 for r in proposal.responses.values() if r == "reject")
            counter_count = sum(1 for r in proposal.responses.values() if r == "counter")
            
            if accept_count == len(all_participants):
                # All accepted
                proposal.status = ProposalStatus.ACCEPTED
                
                # Update negotiation status and outcome
                negotiation.status = NegotiationStatus.SUCCESSFUL
                negotiation.outcome = proposal.content
                
                logger.info(f"Proposal {proposal_id} accepted by all participants")
            elif reject_count > 0:
                # At least one rejection
                proposal.status = ProposalStatus.REJECTED
                
                # If all proposals are rejected, the negotiation fails
                if all(p.status in [ProposalStatus.REJECTED, ProposalStatus.WITHDRAWN] for p in negotiation.proposals):
                    negotiation.status = NegotiationStatus.FAILED
                    
                logger.info(f"Proposal {proposal_id} rejected")
            elif counter_count > 0:
                # At least one counter-proposal requested
                proposal.status = ProposalStatus.COUNTERED
                
                logger.info(f"Counter-proposal requested for proposal {proposal_id}")
        
        return True
    
    def withdraw_proposal(
        self,
        negotiation_id: str,
        proposal_id: str,
        agent_id: str
    ) -> bool:
        """
        Withdraw a proposal.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposal_id: The ID of the proposal
            agent_id: The ID of the agent withdrawing the proposal
            
        Returns:
            True if the proposal was withdrawn, False otherwise
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to withdraw proposal from non-existent negotiation {negotiation_id}")
            return False
            
        if negotiation.status != NegotiationStatus.ACTIVE:
            logger.warning(f"Attempted to withdraw proposal from negotiation {negotiation_id} with status {negotiation.status}")
            return False
            
        # Find the proposal
        proposal = None
        for p in negotiation.proposals:
            if p.proposal_id == proposal_id:
                proposal = p
                break
                
        if not proposal:
            logger.warning(f"Proposal {proposal_id} not found in negotiation {negotiation_id}")
            return False
            
        if proposal.proposer_id != agent_id:
            logger.warning(f"Agent {agent_id} is not the proposer of proposal {proposal_id}")
            return False
            
        if proposal.status != ProposalStatus.PENDING:
            logger.warning(f"Attempted to withdraw proposal {proposal_id} with status {proposal.status}")
            return False
            
        # Update proposal status
        proposal.status = ProposalStatus.WITHDRAWN
        proposal.updated_at = time.time()
        negotiation.updated_at = time.time()
        
        logger.info(f"Proposal {proposal_id} withdrawn by agent {agent_id}")
        
        # If all proposals are withdrawn or rejected, the negotiation fails
        if all(p.status in [ProposalStatus.REJECTED, ProposalStatus.WITHDRAWN] for p in negotiation.proposals):
            negotiation.status = NegotiationStatus.FAILED
            
        return True
    
    def check_negotiation_timeout(self, negotiation_id: str) -> bool:
        """
        Check if a negotiation has timed out.
        
        Args:
            negotiation_id: The ID of the negotiation
            
        Returns:
            True if the negotiation has timed out, False otherwise
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to check timeout for non-existent negotiation {negotiation_id}")
            return False
            
        if negotiation.status != NegotiationStatus.ACTIVE:
            return False
            
        if negotiation.deadline and time.time() > negotiation.deadline:
            negotiation.status = NegotiationStatus.TIMEOUT
            negotiation.updated_at = time.time()
            
            logger.info(f"Negotiation {negotiation_id} timed out")
            return True
            
        return False
    
    def suggest_compromise(
        self,
        negotiation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest a compromise for a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation
            
        Returns:
            A compromise proposal content, or None if compromise is not possible
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            logger.warning(f"Attempted to suggest compromise for non-existent negotiation {negotiation_id}")
            return None
            
        if negotiation.status != NegotiationStatus.ACTIVE:
            logger.warning(f"Attempted to suggest compromise for negotiation {negotiation_id} with status {negotiation.status}")
            return None
            
        # Get all pending and countered proposals
        active_proposals = [
            p for p in negotiation.proposals
            if p.status in [ProposalStatus.PENDING, ProposalStatus.COUNTERED]
        ]
        
        if not active_proposals:
            logger.warning(f"No active proposals found in negotiation {negotiation_id}")
            return None
            
        # Suggest a compromise
        return self.conflict_resolver.suggest_compromise(negotiation, active_proposals)
    
    def allocate_tasks(
        self,
        tasks: List[TaskDetails],
        agents: List[str],
        strategy_name: str = "capability_matching",
        agent_capabilities: Optional[Dict[str, Dict[str, float]]] = None,
        agent_workloads: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[str]]:
        """
        Allocate tasks to agents using a specified strategy.
        
        Args:
            tasks: List of tasks to allocate
            agents: List of agent IDs
            strategy_name: Name of the allocation strategy to use
            agent_capabilities: Optional dict mapping agent IDs to capability scores
            agent_workloads: Optional dict mapping agent IDs to current workloads
            
        Returns:
            Dict mapping agent IDs to lists of task IDs
        """
        if strategy_name not in self.allocation_strategies:
            logger.warning(f"Unknown allocation strategy: {strategy_name}")
            strategy_name = "round_robin"
            
        strategy = self.allocation_strategies[strategy_name]
        
        return strategy.allocate_tasks(
            tasks=tasks,
            agents=agents,
            agent_capabilities=agent_capabilities,
            agent_workloads=agent_workloads
        )
    
    def register_allocation_strategy(
        self,
        name: str,
        strategy: TaskAllocationStrategy
    ) -> None:
        """Register a new task allocation strategy."""
        self.allocation_strategies[name] = strategy
        logger.info(f"Registered task allocation strategy: {name}")


class NegotiationService:
    """Service for managing negotiations between agents."""
    
    def __init__(
        self,
        negotiation_manager: NegotiationManager = None
    ):
        self.negotiation_manager = negotiation_manager or NegotiationManager()
        
    def initiate_task_allocation_negotiation(
        self,
        initiator_id: str,
        participants: List[str],
        tasks: List[TaskDetails],
        deadline: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Initiate a task allocation negotiation.
        
        Args:
            initiator_id: The ID of the initiating agent
            participants: List of participating agent IDs
            tasks: List of tasks to allocate
            deadline: Optional deadline for the negotiation
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created negotiation, or None if creation failed
        """
        # Create context with tasks
        context = {
            "tasks": {task.task_id: {
                "name": task.name,
                "description": task.description,
                "estimated_duration": task.estimated_duration,
                "complexity": task.complexity,
                "priority": task.priority,
                "dependencies": task.dependencies,
                "required_resources": task.required_resources,
                "metadata": task.metadata
            } for task in tasks}
        }
        
        # Create negotiation
        negotiation_id = self.negotiation_manager.create_negotiation(
            negotiation_type=NegotiationType.TASK_ALLOCATION,
            initiator_id=initiator_id,
            participants=participants,
            context=context,
            deadline=deadline,
            metadata=metadata
        )
        
        # Start negotiation
        if not self.negotiation_manager.start_negotiation(negotiation_id):
            logger.error(f"Failed to start negotiation {negotiation_id}")
            return None
            
        return negotiation_id
    
    def initiate_resource_allocation_negotiation(
        self,
        initiator_id: str,
        participants: List[str],
        resources: Dict[str, float],
        deadline: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Initiate a resource allocation negotiation.
        
        Args:
            initiator_id: The ID of the initiating agent
            participants: List of participating agent IDs
            resources: Dict mapping resource names to available amounts
            deadline: Optional deadline for the negotiation
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created negotiation, or None if creation failed
        """
        # Create context with resources
        context = {
            "resources": resources
        }
        
        # Create negotiation
        negotiation_id = self.negotiation_manager.create_negotiation(
            negotiation_type=NegotiationType.RESOURCE_ALLOCATION,
            initiator_id=initiator_id,
            participants=participants,
            context=context,
            deadline=deadline,
            metadata=metadata
        )
        
        # Start negotiation
        if not self.negotiation_manager.start_negotiation(negotiation_id):
            logger.error(f"Failed to start negotiation {negotiation_id}")
            return None
            
        return negotiation_id
    
    def initiate_priority_setting_negotiation(
        self,
        initiator_id: str,
        participants: List[str],
        tasks: List[TaskDetails],
        deadline: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Initiate a priority setting negotiation.
        
        Args:
            initiator_id: The ID of the initiating agent
            participants: List of participating agent IDs
            tasks: List of tasks to set priorities for
            deadline: Optional deadline for the negotiation
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created negotiation, or None if creation failed
        """
        # Create context with tasks
        context = {
            "tasks": {task.task_id: {
                "name": task.name,
                "description": task.description,
                "current_priority": task.priority,
                "metadata": task.metadata
            } for task in tasks}
        }
        
        # Create negotiation
        negotiation_id = self.negotiation_manager.create_negotiation(
            negotiation_type=NegotiationType.PRIORITY_SETTING,
            initiator_id=initiator_id,
            participants=participants,
            context=context,
            deadline=deadline,
            metadata=metadata
        )
        
        # Start negotiation
        if not self.negotiation_manager.start_negotiation(negotiation_id):
            logger.error(f"Failed to start negotiation {negotiation_id}")
            return None
            
        return negotiation_id
    
    def propose_task_allocation(
        self,
        negotiation_id: str,
        proposer_id: str,
        allocation: Dict[str, List[str]],
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Propose a task allocation.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposer_id: The ID of the proposing agent
            allocation: Dict mapping agent IDs to lists of task IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created proposal, or None if submission failed
        """
        content = {
            "allocation": allocation
        }
        
        return self.negotiation_manager.submit_proposal(
            negotiation_id=negotiation_id,
            proposer_id=proposer_id,
            proposal_type=NegotiationType.TASK_ALLOCATION,
            content=content,
            metadata=metadata
        )
    
    def propose_resource_allocation(
        self,
        negotiation_id: str,
        proposer_id: str,
        resources: Dict[str, Dict[str, float]],
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Propose a resource allocation.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposer_id: The ID of the proposing agent
            resources: Dict mapping agent IDs to dicts mapping resource names to amounts
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created proposal, or None if submission failed
        """
        content = {
            "resources": resources
        }
        
        return self.negotiation_manager.submit_proposal(
            negotiation_id=negotiation_id,
            proposer_id=proposer_id,
            proposal_type=NegotiationType.RESOURCE_ALLOCATION,
            content=content,
            metadata=metadata
        )
    
    def propose_priority_setting(
        self,
        negotiation_id: str,
        proposer_id: str,
        priorities: Dict[str, int],
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Propose task priorities.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposer_id: The ID of the proposing agent
            priorities: Dict mapping task IDs to priority values
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created proposal, or None if submission failed
        """
        content = {
            "priorities": priorities
        }
        
        return self.negotiation_manager.submit_proposal(
            negotiation_id=negotiation_id,
            proposer_id=proposer_id,
            proposal_type=NegotiationType.PRIORITY_SETTING,
            content=content,
            metadata=metadata
        )
    
    def respond_to_proposal(
        self,
        negotiation_id: str,
        proposal_id: str,
        agent_id: str,
        response: str  # "accept", "reject", "counter"
    ) -> bool:
        """
        Respond to a proposal.
        
        Args:
            negotiation_id: The ID of the negotiation
            proposal_id: The ID of the proposal
            agent_id: The ID of the responding agent
            response: The response ("accept", "reject", "counter")
            
        Returns:
            True if the response was recorded, False otherwise
        """
        return self.negotiation_manager.respond_to_proposal(
            negotiation_id=negotiation_id,
            proposal_id=proposal_id,
            agent_id=agent_id,
            response=response
        )
    
    def get_negotiation_status(
        self,
        negotiation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the status of a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation
            
        Returns:
            Dict with negotiation status information, or None if not found
        """
        negotiation = self.negotiation_manager.get_negotiation(negotiation_id)
        if not negotiation:
            return None
            
        # Check for timeout
        self.negotiation_manager.check_negotiation_timeout(negotiation_id)
        
        # Build status information
        status_info = {
            "negotiation_id": negotiation.negotiation_id,
            "negotiation_type": negotiation.negotiation_type.value,
            "status": negotiation.status.value,
            "initiator_id": negotiation.initiator_id,
            "participants": negotiation.participants,
            "created_at": negotiation.created_at,
            "updated_at": negotiation.updated_at,
            "deadline": negotiation.deadline,
            "proposals": [
                {
                    "proposal_id": p.proposal_id,
                    "proposer_id": p.proposer_id,
                    "status": p.status.value,
                    "responses": p.responses
                }
                for p in negotiation.proposals
            ],
            "outcome": negotiation.outcome
        }
        
        return status_info
    
    def suggest_compromise(
        self,
        negotiation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest a compromise for a negotiation.
        
        Args:
            negotiation_id: The ID of the negotiation
            
        Returns:
            A compromise proposal content, or None if compromise is not possible
        """
        return self.negotiation_manager.suggest_compromise(negotiation_id)
    
    def allocate_tasks(
        self,
        tasks: List[TaskDetails],
        agents: List[str],
        strategy_name: str = "capability_matching",
        agent_capabilities: Optional[Dict[str, Dict[str, float]]] = None,
        agent_workloads: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[str]]:
        """
        Allocate tasks to agents using a specified strategy.
        
        Args:
            tasks: List of tasks to allocate
            agents: List of agent IDs
            strategy_name: Name of the allocation strategy to use
            agent_capabilities: Optional dict mapping agent IDs to capability scores
            agent_workloads: Optional dict mapping agent IDs to current workloads
            
        Returns:
            Dict mapping agent IDs to lists of task IDs
        """
        return self.negotiation_manager.allocate_tasks(
            tasks=tasks,
            agents=agents,
            strategy_name=strategy_name,
            agent_capabilities=agent_capabilities,
            agent_workloads=agent_workloads
        )
