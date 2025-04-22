"""
Negotiation Protocol Module for Advanced Multi-Agent Collaboration System
This module provides enhanced negotiation capabilities for Lumina AI, enabling
efficient task allocation and resource management between agents with sophisticated
conflict resolution mechanisms and resource optimization.
"""
import logging
from typing import List, Dict, Set, Optional, Tuple, Any, Union
import numpy as np
from dataclasses import dataclass, field
import json
import time
import uuid
from enum import Enum
import copy
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NegotiationStatus(Enum):
    """Status of a negotiation process."""
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CONFLICT_RESOLUTION = "CONFLICT_RESOLUTION"

class MessageType(Enum):
    """Types of negotiation messages."""
    PROPOSAL = "PROPOSAL"
    COUNTER_PROPOSAL = "COUNTER_PROPOSAL"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    QUERY = "QUERY"
    INFORM = "INFORM"
    CONFIRM = "CONFIRM"
    CONCESSION = "CONCESSION"
    DEMAND = "DEMAND"
    COMPROMISE = "COMPROMISE"
    RESOLUTION = "RESOLUTION"

class ResourceType(Enum):
    """Types of resources that can be negotiated."""
    COMPUTATION = "COMPUTATION"
    MEMORY = "MEMORY"
    TIME = "TIME"
    API_CALLS = "API_CALLS"
    TOKENS = "TOKENS"
    SPECIALIZED_CAPABILITY = "SPECIALIZED_CAPABILITY"
    DATA_ACCESS = "DATA_ACCESS"
    PRIORITY = "PRIORITY"
    BUDGET = "BUDGET"

class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts in negotiations."""
    PRIORITY_BASED = "PRIORITY_BASED"
    COMPROMISE = "COMPROMISE"
    VOTING = "VOTING"
    OPTIMIZATION = "OPTIMIZATION"
    FAIR_DIVISION = "FAIR_DIVISION"
    PARETO_OPTIMAL = "PARETO_OPTIMAL"
    NASH_BARGAINING = "NASH_BARGAINING"

@dataclass
class NegotiationParticipant:
    """Represents a participant in a negotiation."""
    id: str
    name: str
    priority: int = 1
    preferences: Dict[str, float] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    utility_function: Optional[callable] = None
    
    def calculate_utility(self, proposal: Dict[str, Any]) -> float:
        """Calculate the utility of a proposal for this participant."""
        if self.utility_function:
            return self.utility_function(proposal)
        
        # Default utility calculation based on preferences
        utility = 0.0
        for key, value in proposal.items():
            if key in self.preferences:
                preference = self.preferences[key]
                
                # Handle different types of values
                if isinstance(value, (int, float)) and isinstance(preference, (int, float)):
                    # For numeric values, utility is higher when closer to preference
                    utility += 1.0 - min(1.0, abs(value - preference) / max(1.0, abs(preference)))
                elif value == preference:
                    # For exact matches
                    utility += 1.0
                else:
                    # For non-matches
                    utility += 0.0
        
        # Normalize by number of preferences
        return utility / max(1, len(self.preferences))
    
    def satisfies_constraints(self, proposal: Dict[str, Any]) -> bool:
        """Check if a proposal satisfies this participant's constraints."""
        for key, constraint in self.constraints.items():
            if key not in proposal:
                continue
                
            value = proposal[key]
            
            if isinstance(constraint, dict):
                if 'min' in constraint and value < constraint['min']:
                    return False
                if 'max' in constraint and value > constraint['max']:
                    return False
            elif value != constraint:
                return False
        
        return True

@dataclass
class NegotiationMessage:
    """Represents a message in a negotiation."""
    sender_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"Message({self.message_type.value} from {self.sender_id})"

@dataclass
class Negotiation:
    """Represents a negotiation process between multiple agents."""
    id: str
    subject: str
    initiator_id: str
    participant_ids: Set[str]
    resources: Dict[str, Any]
    status: NegotiationStatus = NegotiationStatus.INITIATED
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    current_round: int = 1
    max_rounds: int = 10
    timeout_ms: int = 30000
    messages: List[NegotiationMessage] = field(default_factory=list)
    proposals: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.COMPROMISE
    
    def add_message(self, message: NegotiationMessage) -> None:
        """Add a message to the negotiation."""
        self.messages.append(message)
        
        # Update proposals if it's a proposal or counter-proposal
        if message.message_type in [MessageType.PROPOSAL, MessageType.COUNTER_PROPOSAL]:
            self.proposals[message.sender_id] = message.content
            self.state["current_proposal"] = message.content
    
    def is_timed_out(self) -> bool:
        """Check if the negotiation has timed out."""
        elapsed_ms = (time.time() - self.start_time) * 1000
        return elapsed_ms > self.timeout_ms
    
    def all_participants_responded(self) -> bool:
        """Check if all participants have responded in the current round."""
        all_participants = set(self.participant_ids)
        all_participants.add(self.initiator_id)
        
        # Get all agents who have submitted proposals
        responded_agents = set(self.proposals.keys())
        
        return responded_agents.issuperset(all_participants)
    
    def all_participants_accepted(self) -> bool:
        """Check if all participants have accepted the current proposal."""
        acceptances = self.state.get("acceptances", {})
        
        all_participants = set(self.participant_ids)
        all_participants.add(self.initiator_id)
        
        # Check if all participants have accepted
        for participant_id in all_participants:
            if not acceptances.get(participant_id, False):
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"Negotiation(id={self.id}, subject={self.subject}, status={self.status.value}, round={self.current_round}/{self.max_rounds})"

class NegotiationProtocol:
    """
    Enhanced negotiation protocol that provides sophisticated negotiation capabilities
    for efficient task allocation and resource management between agents.
    """
    
    def __init__(self, 
                 default_max_rounds: int = 10,
                 default_timeout_ms: int = 30000,
                 default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.COMPROMISE):
        """
        Initialize the negotiation protocol.
        
        Args:
            default_max_rounds: Default maximum number of negotiation rounds
            default_timeout_ms: Default timeout in milliseconds
            default_strategy: Default conflict resolution strategy
        """
        self.default_max_rounds = default_max_rounds
        self.default_timeout_ms = default_timeout_ms
        self.default_strategy = default_strategy
        self.negotiations: Dict[str, Negotiation] = {}
        self.participants: Dict[str, NegotiationParticipant] = {}
        
    def register_participant(self, participant: NegotiationParticipant) -> None:
        """Register a participant with the negotiation protocol."""
        self.participants[participant.id] = participant
        logger.info(f"Registered negotiation participant: {participant.name}")
    
    def initiate_negotiation(self, 
                           initiator_id: str, 
                           participant_ids: List[str], 
                           subject: str, 
                           resources: Dict[str, Any],
                           initial_proposal: Dict[str, Any],
                           max_rounds: Optional[int] = None,
                           timeout_ms: Optional[int] = None,
                           strategy: Optional[ConflictResolutionStrategy] = None) -> Negotiation:
        """
        Initiate a new negotiation process.
        
        Args:
            initiator_id: ID of the agent initiating the negotiation
            participant_ids: IDs of the participating agents
            subject: Subject of the negotiation
            resources: Resources being negotiated
            initial_proposal: Initial proposal from the initiator
            max_rounds: Maximum number of negotiation rounds
            timeout_ms: Timeout in milliseconds
            strategy: Conflict resolution strategy
            
        Returns:
            The created negotiation
        """
        # Validate participants
        if initiator_id not in self.participants:
            raise ValueError(f"Initiator {initiator_id} is not registered")
        
        for participant_id in participant_ids:
            if participant_id not in self.participants:
                raise ValueError(f"Participant {participant_id} is not registered")
        
        # Create negotiation
        negotiation_id = str(uuid.uuid4())
        negotiation = Negotiation(
            id=negotiation_id,
            subject=subject,
            initiator_id=initiator_id,
            participant_ids=set(participant_ids),
            resources=resources,
            status=NegotiationStatus.INITIATED,
            start_time=time.time(),
            current_round=1,
            max_rounds=max_rounds or self.default_max_rounds,
            timeout_ms=timeout_ms or self.default_timeout_ms,
            conflict_resolution_strategy=strategy or self.default_strategy
        )
        
        # Add initial proposal
        initial_message = NegotiationMessage(
            sender_id=initiator_id,
            message_type=MessageType.PROPOSAL,
            content=initial_proposal
        )
        negotiation.add_message(initial_message)
        
        # Initialize state
        negotiation.state["current_proposal"] = initial_proposal
        negotiation.state["acceptances"] = {}
        
        # Store negotiation
        self.negotiations[negotiation_id] = negotiation
        
        logger.info(f"Initiated negotiation: {negotiation_id} on subject: {subject}")
        return negotiation
    
    def submit_response(self, 
                      negotiation_id: str, 
                      participant_id: str, 
                      response_type: MessageType, 
                      content: Dict[str, Any] = None) -> Negotiation:
        """
        Submit a response to an ongoing negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            participant_id: ID of the participant submitting the response
            response_type: Type of response
            content: Content of the response
            
        Returns:
            The updated negotiation
        """
        # Validate negotiation
        if negotiation_id not in self.negotiations:
            raise ValueError(f"Negotiation {negotiation_id} not found")
        
        negotiation = self.negotiations[negotiation_id]
        
        # Validate participant
        if participant_id not in negotiation.participant_ids and participant_id != negotiation.initiator_id:
            raise ValueError(f"Participant {participant_id} is not part of this negotiation")
        
        # Validate negotiation is still active
        if negotiation.status not in [NegotiationStatus.INITIATED, NegotiationStatus.IN_PROGRESS]:
            raise ValueError(f"Negotiation is no longer active: {negotiation.status.value}")
        
        # Check for timeout
        if negotiation.is_timed_out():
            negotiation.status = NegotiationStatus.TIMEOUT
            negotiation.end_time = time.time()
            self._resolve_negotiation(negotiation)
            return negotiation
        
        # Update negotiation status if it was just initiated
        if negotiation.status == NegotiationStatus.INITIATED:
            negotiation.status = NegotiationStatus.IN_PROGRESS
        
        # Create message
        message = NegotiationMessage(
            sender_id=participant_id,
            message_type=response_type,
            content=content or {}
        )
        negotiation.add_message(message)
        
        # Process response based on type
        if response_type == MessageType.COUNTER_PROPOSAL:
            self._process_counter_proposal(negotiation, participant_id, content)
        elif response_type == MessageType.ACCEPT:
            self._process_acceptance(negotiation, participant_id)
        elif response_type == MessageType.REJECT:
            self._process_rejection(negotiation, participant_id)
        elif response_type == MessageType.CONCESSION:
            self._process_concession(negotiation, participant_id, content)
        elif response_type == MessageType.DEMAND:
            self._process_demand(negotiation, participant_id, content)
        elif response_type == MessageType.COMPROMISE:
            self._process_compromise(negotiation, participant_id, content)
        
        return negotiation
    
    def _process_counter_proposal(self, negotiation: Negotiation, participant_id: str, content: Dict[str, Any]) -> None:
        """Process a counter-proposal response."""
        # Increment round if all participants have responded
        if negotiation.all_participants_responded():
            negotiation.current_round += 1
            
            # Reset acceptances for the new round
            negotiation.state["acceptances"] = {}
            
            # Check if max rounds reached
            if negotiation.current_round > negotiation.max_rounds:
                negotiation.status = NegotiationStatus.CONFLICT_RESOLUTION
                self._resolve_negotiation(negotiation)
    
    def _process_acceptance(self, negotiation: Negotiation, participant_id: str) -> None:
        """Process an acceptance response."""
        # Mark this participant as accepting the current proposal
        acceptances = negotiation.state.get("acceptances", {})
        acceptances[participant_id] = True
        negotiation.state["acceptances"] = acceptances
        
        # Check if all participants have accepted
        if negotiation.all_participants_accepted():
            negotiation.status = NegotiationStatus.SUCCESSFUL
            negotiation.end_time = time.time()
            negotiation.state["final_agreement"] = negotiation.state.get("current_proposal")
    
    def _process_rejection(self, negotiation: Negotiation, participant_id: str) -> None:
        """Process a rejection response."""
        # If any participant rejects and no further negotiation is possible, fail the negotiation
        if negotiation.current_round >= negotiation.max_rounds:
            negotiation.status = NegotiationStatus.FAILED
            negotiation.end_time = time.time()
    
    def _process_concession(self, negotiation: Negotiation, participant_id: str, content: Dict[str, Any]) -> None:
        """Process a concession response."""
        # A concession is a modified proposal that gives up some demands
        current_proposal = negotiation.state.get("current_proposal", {})
        
        # Update the participant's proposal
        negotiation.proposals[participant_id] = content
        
        # Check if this concession leads to agreement
        all_satisfied = True
        for pid in negotiation.participant_ids:
            if pid == participant_id:
                continue
                
            participant = self.participants.get(pid)
            if participant and not participant.satisfies_constraints(content):
                all_satisfied = False
                break
        
        if all_satisfied:
            # If all participants would be satisfied with this concession, make it the current proposal
            negotiation.state["current_proposal"] = content
            
            # Send an inform message to all participants
            inform_message = NegotiationMessage(
                sender_id="SYSTEM",
                message_type=MessageType.INFORM,
                content={"message": "A concession has been made that may satisfy all participants"}
            )
            negotiation.add_message(inform_message)
    
    def _process_demand(self, negotiation: Negotiation, participant_id: str, content: Dict[str, Any]) -> None:
        """Process a demand response."""
        # A demand is a statement of requirements that must be met
        # Update the participant's constraints
        participant = self.participants.get(participant_id)
        if participant:
            for key, value in content.items():
                participant.constraints[key] = value
    
    def _process_compromise(self, negotiation: Negotiation, participant_id: str, content: Dict[str, Any]) -> None:
        """Process a compromise response."""
        # A compromise is a middle-ground proposal
        # Similar to counter-proposal but signals willingness to meet in the middle
        self._process_counter_proposal(negotiation, participant_id, content)
        
        # Check if this compromise could lead to resolution
        if self._could_lead_to_resolution(negotiation, content):
            # Suggest this compromise as a potential resolution
            suggestion_message = NegotiationMessage(
                sender_id="SYSTEM",
                message_type=MessageType.INFORM,
                content={"message": "This compromise could lead to resolution", "proposal": content}
            )
            negotiation.add_message(suggestion_message)
    
    def _could_lead_to_resolution(self, negotiation: Negotiation, proposal: Dict[str, Any]) -> bool:
        """Check if a proposal could lead to resolution based on participant preferences."""
        # Calculate utility for all participants
        utilities = {}
        for pid in negotiation.participant_ids:
            participant = self.participants.get(pid)
            if participant:
                utilities[pid] = participant.calculate_utility(proposal)
        
        # If average utility is high, this could lead to resolution
        avg_utility = sum(utilities.values()) / max(1, len(utilities))
        return avg_utility > 0.7  # Threshold for "good enough" compromise
    
    def _resolve_negotiation(self, negotiation: Negotiation) -> None:
        """Resolve a negotiation using the configured conflict resolution strategy."""
        logger.info(f"Resolving negotiation {negotiation.id} using strategy: {negotiation.conflict_resolution_strategy.value}")
        
        resolved_proposal = None
        
        if negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            resolved_proposal = self._resolve_priority_based(negotiation)
        elif negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.COMPROMISE:
            resolved_proposal = self._resolve_compromise(negotiation)
        elif negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.VOTING:
            resolved_proposal = self._resolve_voting(negotiation)
        elif negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.OPTIMIZATION:
            resolved_proposal = self._resolve_optimization(negotiation)
        elif negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.FAIR_DIVISION:
            resolved_proposal = self._resolve_fair_division(negotiation)
        elif negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.PARETO_OPTIMAL:
            resolved_proposal = self._resolve_pareto_optimal(negotiation)
        elif negotiation.conflict_resolution_strategy == ConflictResolutionStrategy.NASH_BARGAINING:
            resolved_proposal = self._resolve_nash_bargaining(negotiation)
        else:
            # Default to compromise
            resolved_proposal = self._resolve_compromise(negotiation)
        
        if resolved_proposal:
            # Update negotiation with resolved proposal
            negotiation.state["final_agreement"] = resolved_proposal
            negotiation.status = NegotiationStatus.SUCCESSFUL
            if not negotiation.end_time:
                negotiation.end_time = time.time()
            
            # Add resolution message
            resolution_message = NegotiationMessage(
                sender_id="SYSTEM",
                message_type=MessageType.RESOLUTION,
                content=resolved_proposal
            )
            negotiation.add_message(resolution_message)
        else:
            # If resolution failed
            negotiation.status = NegotiationStatus.FAILED
            if not negotiation.end_time:
                negotiation.end_time = time.time()
    
    def _resolve_priority_based(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation using priority-based conflict resolution."""
        # Get participant priorities
        participant_priorities = {}
        for pid in negotiation.participant_ids:
            participant = self.participants.get(pid)
            if participant:
                participant_priorities[pid] = participant.priority
        
        # Include initiator
        initiator = self.participants.get(negotiation.initiator_id)
        if initiator:
            participant_priorities[negotiation.initiator_id] = initiator.priority
        
        # Find the participant with highest priority
        highest_priority_id = max(participant_priorities.items(), key=lambda x: x[1])[0]
        
        # Use the proposal from the highest priority participant
        return negotiation.proposals.get(highest_priority_id, negotiation.state.get("current_proposal", {}))
    
    def _resolve_compromise(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation using compromise-based conflict resolution."""
        # Create a new proposal that combines elements from all proposals
        compromise_proposal = {}
        
        # Get all resource keys from all proposals
        all_keys = set()
        for proposal in negotiation.proposals.values():
            all_keys.update(proposal.keys())
        
        # For each resource, find a compromise value
        for key in all_keys:
            values = []
            for proposal in negotiation.proposals.values():
                if key in proposal:
                    values.append(proposal[key])
            
            if not values:
                continue
                
            # Determine compromise value based on type
            first_value = values[0]
            if isinstance(first_value, (int, float)):
                # For numbers, use average
                compromise_proposal[key] = sum(values) / len(values)
            elif isinstance(first_value, bool):
                # For booleans, use majority vote
                true_count = sum(1 for v in values if v)
                compromise_proposal[key] = true_count > len(values) / 2
            else:
                # For strings or other objects, use most frequent value
                value_counts = {}
                for value in values:
                    value_counts[value] = value_counts.get(value, 0) + 1
                
                most_frequent = max(value_counts.items(), key=lambda x: x[1])[0]
                compromise_proposal[key] = most_frequent
        
        return compromise_proposal
    
    def _resolve_voting(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation using voting-based conflict resolution."""
        # Count votes for each proposal
        proposal_votes = {}
        
        for proposal_id, proposal in negotiation.proposals.items():
            # Convert proposal to immutable key
            proposal_key = json.dumps(proposal, sort_keys=True)
            proposal_votes[proposal_key] = proposal_votes.get(proposal_key, 0) + 1
        
        # Find proposal with most votes
        if not proposal_votes:
            return negotiation.state.get("current_proposal", {})
            
        winning_proposal_key = max(proposal_votes.items(), key=lambda x: x[1])[0]
        return json.loads(winning_proposal_key)
    
    def _resolve_optimization(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation using optimization-based conflict resolution."""
        # This would implement a more sophisticated optimization algorithm
        # For now, we'll use a simplified approach that maximizes overall utility
        
        optimized_proposal = {}
        all_keys = set()
        
        # Collect all keys from all proposals
        for proposal in negotiation.proposals.values():
            all_keys.update(proposal.keys())
        
        # For each key, choose the value that maximizes overall utility
        for key in all_keys:
            best_value = None
            best_utility = float('-inf')
            
            # Collect all proposed values for this key
            values = set()
            for proposal in negotiation.proposals.values():
                if key in proposal:
                    values.add(proposal[key])
            
            # For each possible value, calculate total utility across all participants
            for value in values:
                total_utility = 0
                
                # Create a test proposal with just this key-value pair
                test_proposal = {key: value}
                
                # Calculate utility for all participants
                for pid in negotiation.participant_ids:
                    participant = self.participants.get(pid)
                    if participant:
                        # For simplicity, we'll just check if this matches their preference
                        if key in participant.preferences and participant.preferences[key] == value:
                            total_utility += 1
                
                if total_utility > best_utility:
                    best_utility = total_utility
                    best_value = value
            
            if best_value is not None:
                optimized_proposal[key] = best_value
        
        return optimized_proposal
    
    def _resolve_fair_division(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation using fair division algorithms."""
        # Simplified implementation of fair division
        # In a real implementation, this would use more sophisticated algorithms
        
        fair_proposal = {}
        all_keys = set()
        
        # Collect all keys from all proposals
        for proposal in negotiation.proposals.values():
            all_keys.update(proposal.keys())
        
        # For each key, allocate based on participant preferences
        for key in all_keys:
            # Collect preferences for this key
            preferences = {}
            for pid in negotiation.participant_ids:
                participant = self.participants.get(pid)
                if participant and key in participant.preferences:
                    preferences[pid] = participant.preferences[key]
            
            if not preferences:
                # If no preferences, use compromise
                values = [proposal[key] for proposal in negotiation.proposals.values() if key in proposal]
                if values:
                    if isinstance(values[0], (int, float)):
                        fair_proposal[key] = sum(values) / len(values)
                    else:
                        fair_proposal[key] = values[0]
            else:
                # Allocate based on strongest preference
                strongest_preference = max(preferences.items(), key=lambda x: abs(x[1]))[0]
                participant = self.participants.get(strongest_preference)
                if participant:
                    fair_proposal[key] = participant.preferences[key]
        
        return fair_proposal
    
    def _resolve_pareto_optimal(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation by finding a Pareto optimal solution."""
        # A Pareto optimal solution is one where no participant can be made better off
        # without making at least one participant worse off
        
        # Start with all proposals
        candidate_proposals = list(negotiation.proposals.values())
        if not candidate_proposals:
            return negotiation.state.get("current_proposal", {})
        
        # Calculate utilities for all participants for all proposals
        proposal_utilities = []
        
        for proposal in candidate_proposals:
            utilities = {}
            for pid in negotiation.participant_ids:
                participant = self.participants.get(pid)
                if participant:
                    utilities[pid] = participant.calculate_utility(proposal)
            
            proposal_utilities.append((proposal, utilities))
        
        # Find Pareto optimal proposals
        pareto_optimal = []
        
        for i, (proposal1, utilities1) in enumerate(proposal_utilities):
            is_dominated = False
            
            for j, (proposal2, utilities2) in enumerate(proposal_utilities):
                if i == j:
                    continue
                
                # Check if proposal2 dominates proposal1
                dominates = True
                for pid, utility1 in utilities1.items():
                    utility2 = utilities2.get(pid, 0)
                    if utility2 < utility1:
                        dominates = False
                        break
                
                # If at least one utility is strictly better in proposal2
                strictly_better = False
                for pid, utility2 in utilities2.items():
                    utility1 = utilities1.get(pid, 0)
                    if utility2 > utility1:
                        strictly_better = True
                        break
                
                if dominates and strictly_better:
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_optimal.append(proposal1)
        
        if not pareto_optimal:
            # If no Pareto optimal solutions found, use compromise
            return self._resolve_compromise(negotiation)
        
        # Choose the Pareto optimal proposal with highest average utility
        best_proposal = None
        best_avg_utility = float('-inf')
        
        for proposal in pareto_optimal:
            total_utility = 0
            count = 0
            
            for pid in negotiation.participant_ids:
                participant = self.participants.get(pid)
                if participant:
                    total_utility += participant.calculate_utility(proposal)
                    count += 1
            
            avg_utility = total_utility / max(1, count)
            
            if avg_utility > best_avg_utility:
                best_avg_utility = avg_utility
                best_proposal = proposal
        
        return best_proposal or pareto_optimal[0]
    
    def _resolve_nash_bargaining(self, negotiation: Negotiation) -> Dict[str, Any]:
        """Resolve a negotiation using the Nash bargaining solution."""
        # The Nash bargaining solution maximizes the product of utility gains
        
        # Calculate utilities for all participants for all proposals
        proposal_utilities = []
        
        # Include all proposals and the compromise proposal
        candidate_proposals = list(negotiation.proposals.values())
        compromise_proposal = self._resolve_compromise(negotiation)
        candidate_proposals.append(compromise_proposal)
        
        # Calculate disagreement point (utilities if negotiation fails)
        disagreement_utilities = {}
        for pid in negotiation.participant_ids:
            participant = self.participants.get(pid)
            if participant:
                disagreement_utilities[pid] = 0.0  # Assume zero utility if negotiation fails
        
        # Calculate Nash product for each proposal
        best_proposal = None
        best_nash_product = float('-inf')
        
        for proposal in candidate_proposals:
            nash_product = 1.0
            
            for pid in negotiation.participant_ids:
                participant = self.participants.get(pid)
                if participant:
                    utility = participant.calculate_utility(proposal)
                    utility_gain = max(0, utility - disagreement_utilities.get(pid, 0))
                    nash_product *= utility_gain
            
            if nash_product > best_nash_product:
                best_nash_product = nash_product
                best_proposal = proposal
        
        return best_proposal or compromise_proposal
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Negotiation]:
        """Get a negotiation by ID."""
        return self.negotiations.get(negotiation_id)
    
    def analyze_negotiation(self, negotiation_id: str) -> Dict[str, Any]:
        """
        Analyze a completed negotiation to extract insights and patterns.
        
        Args:
            negotiation_id: ID of the negotiation to analyze
            
        Returns:
            A dictionary of analysis results
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")
        
        # Ensure negotiation is completed
        if negotiation.status in [NegotiationStatus.INITIATED, NegotiationStatus.IN_PROGRESS]:
            raise ValueError("Cannot analyze an ongoing negotiation")
        
        analysis = {}
        
        # Basic statistics
        analysis["status"] = negotiation.status.value
        analysis["duration_ms"] = int((negotiation.end_time - negotiation.start_time) * 1000)
        analysis["rounds"] = negotiation.current_round
        analysis["participant_count"] = len(negotiation.participant_ids) + 1  # +1 for initiator
        
        # Message analysis
        message_type_count = {}
        agent_message_count = {}
        
        for message in negotiation.messages:
            message_type = message.message_type.value
            sender_id = message.sender_id
            
            message_type_count[message_type] = message_type_count.get(message_type, 0) + 1
            agent_message_count[sender_id] = agent_message_count.get(sender_id, 0) + 1
        
        analysis["message_type_count"] = message_type_count
        analysis["agent_message_count"] = agent_message_count
        
        # Proposal evolution analysis
        if negotiation.status == NegotiationStatus.SUCCESSFUL:
            initial_proposal = negotiation.messages[0].content
            final_agreement = negotiation.state.get("final_agreement", {})
            
            changed_keys = set()
            for key in set(initial_proposal.keys()).union(final_agreement.keys()):
                if key not in initial_proposal or key not in final_agreement:
                    changed_keys.add(key)
                elif initial_proposal[key] != final_agreement[key]:
                    changed_keys.add(key)
            
            proposal_evolution = {
                "initial_proposal": initial_proposal,
                "final_agreement": final_agreement,
                "changed_keys": list(changed_keys)
            }
            
            analysis["proposal_evolution"] = proposal_evolution
        
        # Utility analysis
        if negotiation.status == NegotiationStatus.SUCCESSFUL:
            final_agreement = negotiation.state.get("final_agreement", {})
            utilities = {}
            
            for pid in negotiation.participant_ids:
                participant = self.participants.get(pid)
                if participant:
                    utilities[pid] = participant.calculate_utility(final_agreement)
            
            # Include initiator
            initiator = self.participants.get(negotiation.initiator_id)
            if initiator:
                utilities[negotiation.initiator_id] = initiator.calculate_utility(final_agreement)
            
            analysis["utilities"] = utilities
            analysis["avg_utility"] = sum(utilities.values()) / max(1, len(utilities))
        
        return analysis
    
    def suggest_concession(self, negotiation_id: str, participant_id: str) -> Dict[str, Any]:
        """
        Suggest a concession that could move the negotiation forward.
        
        Args:
            negotiation_id: ID of the negotiation
            participant_id: ID of the participant for whom to suggest a concession
            
        Returns:
            A suggested concession proposal
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")
        
        participant = self.participants.get(participant_id)
        if not participant:
            raise ValueError(f"Participant {participant_id} not found")
        
        # Get current proposal and participant's last proposal
        current_proposal = negotiation.state.get("current_proposal", {})
        participant_proposal = negotiation.proposals.get(participant_id, {})
        
        # Start with participant's proposal
        concession = copy.deepcopy(participant_proposal)
        
        # Identify points of disagreement
        disagreements = []
        
        for key, value in current_proposal.items():
            if key not in participant_proposal or participant_proposal[key] != value:
                disagreements.append(key)
        
        # If no disagreements, no concession needed
        if not disagreements:
            return participant_proposal
        
        # Choose one disagreement point to concede on
        if disagreements:
            key_to_concede = disagreements[0]  # Simple strategy: concede on first disagreement
            
            # If the key exists in current proposal, adopt that value
            if key_to_concede in current_proposal:
                concession[key_to_concede] = current_proposal[key_to_concede]
        
        return concession
    
    def calculate_fairness(self, negotiation_id: str) -> float:
        """
        Calculate the fairness of a negotiation outcome.
        
        Args:
            negotiation_id: ID of the negotiation
            
        Returns:
            A fairness score between 0 and 1
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")
        
        if negotiation.status != NegotiationStatus.SUCCESSFUL:
            return 0.0
        
        final_agreement = negotiation.state.get("final_agreement", {})
        utilities = {}
        
        # Calculate utilities for all participants
        for pid in negotiation.participant_ids:
            participant = self.participants.get(pid)
            if participant:
                utilities[pid] = participant.calculate_utility(final_agreement)
        
        # Include initiator
        initiator = self.participants.get(negotiation.initiator_id)
        if initiator:
            utilities[negotiation.initiator_id] = initiator.calculate_utility(final_agreement)
        
        if not utilities:
            return 0.0
        
        # Calculate fairness metrics
        min_utility = min(utilities.values())
        max_utility = max(utilities.values())
        avg_utility = sum(utilities.values()) / len(utilities)
        
        # Jain's fairness index
        sum_utilities = sum(utilities.values())
        sum_squared_utilities = sum(u * u for u in utilities.values())
        jains_index = (sum_utilities * sum_utilities) / (len(utilities) * sum_squared_utilities)
        
        # Combine metrics (equal weight)
        fairness = (min_utility / max(0.001, max_utility) + jains_index) / 2
        
        return fairness
    
    def predict_negotiation_success(self, negotiation_id: str) -> float:
        """
        Predict the likelihood of a negotiation succeeding.
        
        Args:
            negotiation_id: ID of the negotiation
            
        Returns:
            A probability between 0 and 1
        """
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")
        
        # If negotiation is already completed, return actual outcome
        if negotiation.status == NegotiationStatus.SUCCESSFUL:
            return 1.0
        elif negotiation.status in [NegotiationStatus.FAILED, NegotiationStatus.TIMEOUT]:
            return 0.0
        
        # Calculate features that predict success
        
        # 1. Progress through rounds
        round_progress = negotiation.current_round / negotiation.max_rounds
        
        # 2. Time remaining
        elapsed_ms = (time.time() - negotiation.start_time) * 1000
        time_remaining = max(0, 1 - elapsed_ms / negotiation.timeout_ms)
        
        # 3. Message sentiment (simplified)
        positive_message_types = [MessageType.ACCEPT, MessageType.COMPROMISE, MessageType.CONCESSION]
        negative_message_types = [MessageType.REJECT, MessageType.DEMAND]
        
        positive_count = sum(1 for m in negotiation.messages if m.message_type in positive_message_types)
        negative_count = sum(1 for m in negotiation.messages if m.message_type in negative_message_types)
        
        message_sentiment = 0.5  # Neutral by default
        if positive_count + negative_count > 0:
            message_sentiment = positive_count / (positive_count + negative_count)
        
        # 4. Utility convergence
        utilities_by_participant = {}
        
        for pid in negotiation.participant_ids:
            participant = self.participants.get(pid)
            if participant:
                utilities = []
                for proposal_id, proposal in negotiation.proposals.items():
                    utilities.append(participant.calculate_utility(proposal))
                
                if utilities:
                    utilities_by_participant[pid] = utilities
        
        utility_convergence = 0.5  # Neutral by default
        if utilities_by_participant:
            # Calculate standard deviation of utilities for each participant
            std_devs = []
            for utilities in utilities_by_participant.values():
                if len(utilities) > 1:
                    mean = sum(utilities) / len(utilities)
                    variance = sum((u - mean) ** 2 for u in utilities) / len(utilities)
                    std_devs.append(math.sqrt(variance))
            
            if std_devs:
                # Lower standard deviation means more convergence
                avg_std_dev = sum(std_devs) / len(std_devs)
                utility_convergence = 1.0 - min(1.0, avg_std_dev)
        
        # Combine features with weights
        success_probability = (
            0.2 * (1 - round_progress) +  # Earlier rounds have more potential for success
            0.2 * time_remaining +        # More time means more chance to succeed
            0.3 * message_sentiment +     # Positive messages indicate progress
            0.3 * utility_convergence     # Converging utilities suggest agreement is near
        )
        
        return max(0.0, min(1.0, success_probability))
