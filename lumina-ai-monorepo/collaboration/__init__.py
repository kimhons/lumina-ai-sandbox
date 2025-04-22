"""
__init__.py for the collaboration package.

This file initializes the Advanced Multi-Agent Collaboration system and
exports the main classes and functions.
"""

from collaboration.team_formation import (
    AgentCapability, AgentProfile, TaskRequirement, AgentTeam,
    AgentCapabilityRegistry, TeamPerformanceMonitor, TeamFormationManager
)
from collaboration.context_manager import (
    ContextScope, ContextType, ContextItem, CollaborativeContextService
)
from collaboration.negotiation import (
    NegotiationType, TaskDetails, NegotiationService
)
from collaboration.shared_memory import (
    MemoryScope, MemoryType, SharedMemoryService
)
from collaboration.learning import (
    LearningEventType, CollaborativeLearningService
)
from collaboration.integration import (
    CollaborationManager, CollaborativeAgent, CollaborativeProviderAdapter,
    initialize_collaboration_system
)

__all__ = [
    # Team Formation
    'AgentCapability', 'AgentProfile', 'TaskRequirement', 'AgentTeam',
    'AgentCapabilityRegistry', 'TeamPerformanceMonitor', 'TeamFormationManager',
    
    # Context Manager
    'ContextScope', 'ContextType', 'ContextItem', 'CollaborativeContextService',
    
    # Negotiation
    'NegotiationType', 'TaskDetails', 'NegotiationService',
    
    # Shared Memory
    'MemoryScope', 'MemoryType', 'SharedMemoryService',
    
    # Learning
    'LearningEventType', 'CollaborativeLearningService',
    
    # Integration
    'CollaborationManager', 'CollaborativeAgent', 'CollaborativeProviderAdapter',
    'initialize_collaboration_system'
]
