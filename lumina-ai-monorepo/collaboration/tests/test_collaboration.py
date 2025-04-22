"""
Tests for the Advanced Multi-Agent Collaboration system.

This module contains comprehensive tests for all components of the
Advanced Multi-Agent Collaboration system.
"""

import unittest
import time
import uuid
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional

# Import collaboration components
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
    CollaborationManager, CollaborativeAgent, CollaborativeProviderAdapter
)

# Mock Lumina AI components
class MockProvider:
    def __init__(self, provider_id, name, capabilities):
        self.provider_id = provider_id
        self.name = name
        self.capabilities = capabilities
    
    def get_id(self):
        return self.provider_id
    
    def get_name(self):
        return self.name
    
    def get_capabilities(self):
        return self.capabilities

class MockProviderSelector:
    def __init__(self, providers):
        self.providers = providers
    
    def get_all_providers(self):
        return self.providers


class TestAgentCapabilityRegistry(unittest.TestCase):
    """Tests for the AgentCapabilityRegistry class."""
    
    def setUp(self):
        self.registry = AgentCapabilityRegistry()
        
        # Create test agent profiles
        self.agent1 = AgentProfile(
            agent_id="agent1",
            name="Agent 1",
            capabilities={
                AgentCapability.REASONING: 0.9,
                AgentCapability.PLANNING: 0.8,
                AgentCapability.CODE_GENERATION: 0.7
            },
            specializations=["finance", "data analysis"]
        )
        
        self.agent2 = AgentProfile(
            agent_id="agent2",
            name="Agent 2",
            capabilities={
                AgentCapability.CREATIVE_WRITING: 0.9,
                AgentCapability.RESEARCH: 0.8,
                AgentCapability.REASONING: 0.6
            },
            specializations=["marketing", "content creation"]
        )
    
    def test_register_agent(self):
        """Test registering agents with the registry."""
        # Register agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        
        # Check if agents are registered
        self.assertIn("agent1", self.registry.agents)
        self.assertIn("agent2", self.registry.agents)
        
        # Check if capabilities are indexed correctly
        self.assertIn("agent1", self.registry.capability_index[AgentCapability.REASONING])
        self.assertIn("agent2", self.registry.capability_index[AgentCapability.REASONING])
        self.assertIn("agent1", self.registry.capability_index[AgentCapability.PLANNING])
        self.assertIn("agent2", self.registry.capability_index[AgentCapability.CREATIVE_WRITING])
        
        # Check if specializations are indexed correctly
        self.assertIn("agent1", self.registry.specialization_index["finance"])
        self.assertIn("agent2", self.registry.specialization_index["marketing"])
    
    def test_unregister_agent(self):
        """Test unregistering agents from the registry."""
        # Register agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        
        # Unregister agent1
        result = self.registry.unregister_agent("agent1")
        self.assertTrue(result)
        
        # Check if agent1 is unregistered
        self.assertNotIn("agent1", self.registry.agents)
        
        # Check if capabilities are updated correctly
        self.assertNotIn("agent1", self.registry.capability_index[AgentCapability.REASONING])
        self.assertIn("agent2", self.registry.capability_index[AgentCapability.REASONING])
        self.assertNotIn("agent1", self.registry.capability_index[AgentCapability.PLANNING])
        
        # Check if specializations are updated correctly
        self.assertNotIn("agent1", self.registry.specialization_index["finance"])
        self.assertIn("agent2", self.registry.specialization_index["marketing"])
        
        # Try unregistering non-existent agent
        result = self.registry.unregister_agent("agent3")
        self.assertFalse(result)
    
    def test_find_agents_by_capability(self):
        """Test finding agents by capability."""
        # Register agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        
        # Find agents with REASONING capability
        agents = self.registry.find_agents_by_capability(AgentCapability.REASONING)
        self.assertEqual(len(agents), 2)
        self.assertIn("agent1", agents)
        self.assertIn("agent2", agents)
        
        # Find agents with PLANNING capability
        agents = self.registry.find_agents_by_capability(AgentCapability.PLANNING)
        self.assertEqual(len(agents), 1)
        self.assertIn("agent1", agents)
        
        # Find agents with non-existent capability
        agents = self.registry.find_agents_by_capability(AgentCapability.VISUAL_DESIGN)
        self.assertEqual(len(agents), 0)
    
    def test_find_agents_by_specialization(self):
        """Test finding agents by specialization."""
        # Register agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        
        # Find agents with finance specialization
        agents = self.registry.find_agents_by_specialization("finance")
        self.assertEqual(len(agents), 1)
        self.assertIn("agent1", agents)
        
        # Find agents with marketing specialization
        agents = self.registry.find_agents_by_specialization("marketing")
        self.assertEqual(len(agents), 1)
        self.assertIn("agent2", agents)
        
        # Find agents with non-existent specialization
        agents = self.registry.find_agents_by_specialization("healthcare")
        self.assertEqual(len(agents), 0)
    
    def test_get_agent_profile(self):
        """Test getting agent profiles."""
        # Register agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        
        # Get agent1 profile
        profile = self.registry.get_agent_profile("agent1")
        self.assertEqual(profile.agent_id, "agent1")
        self.assertEqual(profile.name, "Agent 1")
        self.assertEqual(profile.capabilities[AgentCapability.REASONING], 0.9)
        
        # Get non-existent agent profile
        profile = self.registry.get_agent_profile("agent3")
        self.assertIsNone(profile)


class TestTeamFormationManager(unittest.TestCase):
    """Tests for the TeamFormationManager class."""
    
    def setUp(self):
        self.registry = AgentCapabilityRegistry()
        self.performance_monitor = TeamPerformanceMonitor()
        self.manager = TeamFormationManager(self.registry, self.performance_monitor)
        
        # Create test agent profiles
        self.agent1 = AgentProfile(
            agent_id="agent1",
            name="Agent 1",
            capabilities={
                AgentCapability.REASONING: 0.9,
                AgentCapability.PLANNING: 0.8,
                AgentCapability.CODE_GENERATION: 0.7
            },
            specializations=["finance", "data analysis"]
        )
        
        self.agent2 = AgentProfile(
            agent_id="agent2",
            name="Agent 2",
            capabilities={
                AgentCapability.CREATIVE_WRITING: 0.9,
                AgentCapability.RESEARCH: 0.8,
                AgentCapability.REASONING: 0.6
            },
            specializations=["marketing", "content creation"]
        )
        
        self.agent3 = AgentProfile(
            agent_id="agent3",
            name="Agent 3",
            capabilities={
                AgentCapability.VISUAL_DESIGN: 0.9,
                AgentCapability.CREATIVE_WRITING: 0.7,
                AgentCapability.RESEARCH: 0.6
            },
            specializations=["design", "marketing"]
        )
        
        # Register agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        self.registry.register_agent(self.agent3)
        
        # Create test task
        self.task = TaskRequirement(
            task_id="task1",
            name="Test Task",
            description="A test task for team formation",
            required_capabilities={
                AgentCapability.REASONING: 0.7,
                AgentCapability.CREATIVE_WRITING: 0.7,
                AgentCapability.RESEARCH: 0.6
            },
            domain_specializations=["marketing", "data analysis"],
            priority=7,
            estimated_duration=2.0,
            complexity=6,
            min_team_size=2,
            max_team_size=3
        )
    
    def test_create_team_optimal_coverage(self):
        """Test creating a team with optimal coverage strategy."""
        # Create team
        team = self.manager.create_team(self.task, "optimal_coverage")
        
        # Check if team is created
        self.assertIsNotNone(team)
        self.assertEqual(team.task_id, "task1")
        
        # Check if team has the right members
        self.assertEqual(team.get_size(), 2)
        self.assertIn("agent1", team.members)
        self.assertIn("agent2", team.members)
        
        # Check if team has the right roles
        self.assertIn(AgentCapability.REASONING, team.roles["agent1"])
        self.assertIn(AgentCapability.CREATIVE_WRITING, team.roles["agent2"])
        self.assertIn(AgentCapability.RESEARCH, team.roles["agent2"])
    
    def test_create_team_balanced_workload(self):
        """Test creating a team with balanced workload strategy."""
        # Create team
        team = self.manager.create_team(self.task, "balanced_workload")
        
        # Check if team is created
        self.assertIsNotNone(team)
        self.assertEqual(team.task_id, "task1")
        
        # Check if team has the right members
        self.assertEqual(team.get_size(), 3)
        self.assertIn("agent1", team.members)
        self.assertIn("agent2", team.members)
        self.assertIn("agent3", team.members)
    
    def test_create_team_minimal_size(self):
        """Test creating a team with minimal size strategy."""
        # Create team
        team = self.manager.create_team(self.task, "minimal_size")
        
        # Check if team is created
        self.assertIsNotNone(team)
        self.assertEqual(team.task_id, "task1")
        
        # Check if team has the right members
        self.assertEqual(team.get_size(), 2)
    
    def test_create_team_specialized_domain(self):
        """Test creating a team with specialized domain strategy."""
        # Create team
        team = self.manager.create_team(self.task, "specialized_domain")
        
        # Check if team is created
        self.assertIsNotNone(team)
        self.assertEqual(team.task_id, "task1")
        
        # Check if team has the right members
        self.assertIn("agent1", team.members)  # Has data analysis specialization
        self.assertIn("agent2", team.members)  # Has marketing specialization
    
    def test_disband_team(self):
        """Test disbanding a team."""
        # Create team
        team = self.manager.create_team(self.task, "optimal_coverage")
        team_id = team.team_id
        
        # Check if team is created
        self.assertIsNotNone(team)
        self.assertIn(team_id, self.manager.teams)
        
        # Disband team
        result = self.manager.disband_team(team_id)
        self.assertTrue(result)
        
        # Check if team is disbanded
        self.assertNotIn(team_id, self.manager.teams)
        
        # Try disbanding non-existent team
        result = self.manager.disband_team("non-existent-team")
        self.assertFalse(result)


class TestCollaborativeContextService(unittest.TestCase):
    """Tests for the CollaborativeContextService class."""
    
    def setUp(self):
        self.context_service = CollaborativeContextService()
        
        # Create test context items
        self.context1 = {
            "key": "test_context_1",
            "value": {"data": "test data 1"},
            "context_type": ContextType.USER_INPUT,
            "scope": ContextScope.AGENT,
            "scope_id": "agent1",
            "agent_id": "agent1",
            "timestamp": time.time()
        }
        
        self.context2 = {
            "key": "test_context_2",
            "value": {"data": "test data 2"},
            "context_type": ContextType.SYSTEM_STATE,
            "scope": ContextScope.TEAM,
            "scope_id": "team1",
            "agent_id": "agent2",
            "timestamp": time.time()
        }
        
        self.context3 = {
            "key": "test_context_3",
            "value": {"data": "test data 3"},
            "context_type": ContextType.TASK_DEFINITION,
            "scope": ContextScope.TASK,
            "scope_id": "task1",
            "agent_id": "agent1",
            "timestamp": time.time()
        }
    
    def test_create_context(self):
        """Test creating context items."""
        # Create context items
        context_id1 = self.context_service.create_context(
            key=self.context1["key"],
            value=self.context1["value"],
            context_type=self.context1["context_type"],
            scope=self.context1["scope"],
            scope_id=self.context1["scope_id"],
            agent_id=self.context1["agent_id"]
        )
        
        context_id2 = self.context_service.create_context(
            key=self.context2["key"],
            value=self.context2["value"],
            context_type=self.context2["context_type"],
            scope=self.context2["scope"],
            scope_id=self.context2["scope_id"],
            agent_id=self.context2["agent_id"]
        )
        
        # Check if context items are created
        self.assertIsNotNone(context_id1)
        self.assertIsNotNone(context_id2)
        self.assertIn(context_id1, self.context_service.contexts)
        self.assertIn(context_id2, self.context_service.contexts)
    
    def test_get_context(self):
        """Test getting context items."""
        # Create context items
        context_id1 = self.context_service.create_context(
            key=self.context1["key"],
            value=self.context1["value"],
            context_type=self.context1["context_type"],
            scope=self.context1["scope"],
            scope_id=self.context1["scope_id"],
            agent_id=self.context1["agent_id"]
        )
        
        # Get context item
        context = self.context_service.get_context(context_id1)
        
        # Check if context item is retrieved correctly
        self.assertIsNotNone(context)
        self.assertEqual(context.key, self.context1["key"])
        self.assertEqual(context.value, self.context1["value"])
        self.assertEqual(context.context_type, self.context1["context_type"])
        self.assertEqual(context.scope, self.context1["scope"])
        self.assertEqual(context.scope_id, self.context1["scope_id"])
        self.assertEqual(context.agent_id, self.context1["agent_id"])
        
        # Try getting non-existent context item
        context = self.context_service.get_context("non-existent-context")
        self.assertIsNone(context)
    
    def test_update_context(self):
        """Test updating context items."""
        # Create context item
        context_id = self.context_service.create_context(
            key=self.context1["key"],
            value=self.context1["value"],
            context_type=self.context1["context_type"],
            scope=self.context1["scope"],
            scope_id=self.context1["scope_id"],
            agent_id=self.context1["agent_id"]
        )
        
        # Update context item
        new_value = {"data": "updated test data"}
        result = self.context_service.update_context(
            context_id=context_id,
            value=new_value
        )
        
        # Check if update was successful
        self.assertTrue(result)
        
        # Get updated context item
        context = self.context_service.get_context(context_id)
        
        # Check if context item is updated correctly
        self.assertEqual(context.value, new_value)
        
        # Try updating non-existent context item
        result = self.context_service.update_context(
            context_id="non-existent-context",
            value=new_value
        )
        self.assertFalse(result)
    
    def test_delete_context(self):
        """Test deleting context items."""
        # Create context item
        context_id = self.context_service.create_context(
            key=self.context1["key"],
            value=self.context1["value"],
            context_type=self.context1["context_type"],
            scope=self.context1["scope"],
            scope_id=self.context1["scope_id"],
            agent_id=self.context1["agent_id"]
        )
        
        # Delete context item
        result = self.context_service.delete_context(context_id)
        
        # Check if deletion was successful
        self.assertTrue(result)
        self.assertNotIn(context_id, self.context_service.contexts)
        
        # Try deleting non-existent context item
        result = self.context_service.delete_context("non-existent-context")
        self.assertFalse(result)
    
    def test_get_agent_context(self):
        """Test getting context for an agent."""
        # Create context items
        self.context_service.create_context(
            key=self.context1["key"],
            value=self.context1["value"],
            context_type=self.context1["context_type"],
            scope=self.context1["scope"],
            scope_id=self.context1["scope_id"],
            agent_id=self.context1["agent_id"]
        )
        
        self.context_service.create_context(
            key=self.context2["key"],
            value=self.context2["value"],
            context_type=self.context2["context_type"],
            scope=self.context2["scope"],
            scope_id=self.context2["scope_id"],
            agent_id=self.context2["agent_id"]
        )
        
        self.context_service.create_context(
            key=self.context3["key"],
            value=self.context3["value"],
            context_type=self.context3["context_type"],
            scope=self.context3["scope"],
            scope_id=self.context3["scope_id"],
            agent_id=self.context3["agent_id"]
        )
        
        # Register agent-team and agent-task relationships
        self.context_service.register_agent_team("agent1", "team1")
        self.context_service.register_agent_task("agent1", "task1")
        
        # Get context for agent1
        agent_context = self.context_service.get_agent_context("agent1")
        
        # Check if agent context is retrieved correctly
        self.assertEqual(len(agent_context), 3)
        self.assertEqual(agent_context[self.context1["key"]], self.context1["value"])
        self.assertEqual(agent_context[self.context2["key"]], self.context2["value"])
        self.assertEqual(agent_context[self.context3["key"]], self.context3["value"])
        
        # Get context for agent2
        agent_context = self.context_service.get_agent_context("agent2")
        
        # Check if agent context is retrieved correctly
        self.assertEqual(len(agent_context), 1)
        self.assertEqual(agent_context[self.context2["key"]], self.context2["value"])
        
        # Get context for agent1 with specific context type
        agent_context = self.context_service.get_agent_context(
            agent_id="agent1",
            context_types=[ContextType.USER_INPUT]
        )
        
        # Check if filtered agent context is retrieved correctly
        self.assertEqual(len(agent_context), 1)
        self.assertEqual(agent_context[self.context1["key"]], self.context1["value"])


class TestNegotiationService(unittest.TestCase):
    """Tests for the NegotiationService class."""
    
    def setUp(self):
        self.negotiation_service = NegotiationService()
        
        # Create test task details
        self.task1 = TaskDetails(
            task_id="task1",
            name="Task 1",
            description="Test task 1",
            estimated_duration=1.0,
            complexity=5,
            priority=7,
            dependencies=[],
            required_resources={}
        )
        
        self.task2 = TaskDetails(
            task_id="task2",
            name="Task 2",
            description="Test task 2",
            estimated_duration=2.0,
            complexity=6,
            priority=8,
            dependencies=["task1"],
            required_resources={}
        )
        
        # Create test agents
        self.agent_ids = ["agent1", "agent2", "agent3"]
    
    def test_initiate_task_allocation_negotiation(self):
        """Test initiating a task allocation negotiation."""
        # Initiate negotiation
        negotiation_id = self.negotiation_service.initiate_task_allocation_negotiation(
            initiator_id="agent1",
            participants=self.agent_ids,
            tasks=[self.task1, self.task2],
            deadline=time.time() + 300
        )
        
        # Check if negotiation is created
        self.assertIsNotNone(negotiation_id)
        self.assertIn(negotiation_id, self.negotiation_service.negotiations)
        
        # Get negotiation
        negotiation = self.negotiation_service.negotiations[negotiation_id]
        
        # Check negotiation properties
        self.assertEqual(negotiation.negotiation_type, NegotiationType.TASK_ALLOCATION)
        self.assertEqual(negotiation.initiator_id, "agent1")
        self.assertEqual(negotiation.participants, self.agent_ids)
        self.assertEqual(len(negotiation.tasks), 2)
        self.assertEqual(negotiation.tasks[0].task_id, "task1")
        self.assertEqual(negotiation.tasks[1].task_id, "task2")
        self.assertEqual(negotiation.status, "active")
    
    def test_propose_task_allocation(self):
        """Test proposing a task allocation."""
        # Initiate negotiation
        negotiation_id = self.negotiation_service.initiate_task_allocation_negotiation(
            initiator_id="agent1",
            participants=self.agent_ids,
            tasks=[self.task1, self.task2],
            deadline=time.time() + 300
        )
        
        # Create allocation
        allocation = {
            "agent1": ["task1"],
            "agent2": ["task2"],
            "agent3": []
        }
        
        # Propose allocation
        proposal_id = self.negotiation_service.propose_task_allocation(
            negotiation_id=negotiation_id,
            proposer_id="agent1",
            allocation=allocation
        )
        
        # Check if proposal is created
        self.assertIsNotNone(proposal_id)
        
        # Get negotiation
        negotiation = self.negotiation_service.negotiations[negotiation_id]
        
        # Check if proposal is added to negotiation
        self.assertIn(proposal_id, negotiation.proposals)
        
        # Get proposal
        proposal = negotiation.proposals[proposal_id]
        
        # Check proposal properties
        self.assertEqual(proposal.proposer_id, "agent1")
        self.assertEqual(proposal.allocation, allocation)
        self.assertEqual(proposal.status, "proposed")
    
    def test_respond_to_proposal(self):
        """Test responding to a proposal."""
        # Initiate negotiation
        negotiation_id = self.negotiation_service.initiate_task_allocation_negotiation(
            initiator_id="agent1",
            participants=self.agent_ids,
            tasks=[self.task1, self.task2],
            deadline=time.time() + 300
        )
        
        # Create allocation
        allocation = {
            "agent1": ["task1"],
            "agent2": ["task2"],
            "agent3": []
        }
        
        # Propose allocation
        proposal_id = self.negotiation_service.propose_task_allocation(
            negotiation_id=negotiation_id,
            proposer_id="agent1",
            allocation=allocation
        )
        
        # Respond to proposal
        result = self.negotiation_service.respond_to_proposal(
            negotiation_id=negotiation_id,
            proposal_id=proposal_id,
            agent_id="agent2",
            response="accept"
        )
        
        # Check if response is recorded
        self.assertTrue(result)
        
        # Get negotiation
        negotiation = self.negotiation_service.negotiations[negotiation_id]
        
        # Get proposal
        proposal = negotiation.proposals[proposal_id]
        
        # Check if response is added to proposal
        self.assertIn("agent2", proposal.responses)
        self.assertEqual(proposal.responses["agent2"], "accept")
        
        # Respond with all agents accepting
        self.negotiation_service.respond_to_proposal(
            negotiation_id=negotiation_id,
            proposal_id=proposal_id,
            agent_id="agent3",
            response="accept"
        )
        
        # Check if proposal is accepted
        self.assertEqual(proposal.status, "accepted")
        
        # Check if negotiation is completed
        self.assertEqual(negotiation.status, "completed")
        self.assertEqual(negotiation.outcome["status"], "agreement")
        self.assertEqual(negotiation.outcome["proposal_id"], proposal_id)
    
    def test_get_negotiation_status(self):
        """Test getting negotiation status."""
        # Initiate negotiation
        negotiation_id = self.negotiation_service.initiate_task_allocation_negotiation(
            initiator_id="agent1",
            participants=self.agent_ids,
            tasks=[self.task1, self.task2],
            deadline=time.time() + 300
        )
        
        # Get negotiation status
        status = self.negotiation_service.get_negotiation_status(negotiation_id)
        
        # Check status properties
        self.assertEqual(status["negotiation_id"], negotiation_id)
        self.assertEqual(status["negotiation_type"], "task_allocation")
        self.assertEqual(status["initiator_id"], "agent1")
        self.assertEqual(status["participants"], self.agent_ids)
        self.assertEqual(status["status"], "active")
        self.assertEqual(len(status["tasks"]), 2)
        self.assertEqual(status["tasks"][0]["task_id"], "task1")
        self.assertEqual(status["tasks"][1]["task_id"], "task2")
        self.assertEqual(len(status["proposals"]), 0)
        
        # Try getting status for non-existent negotiation
        status = self.negotiation_service.get_negotiation_status("non-existent-negotiation")
        self.assertIsNone(status)


class TestSharedMemoryService(unittest.TestCase):
    """Tests for the SharedMemoryService class."""
    
    def setUp(self):
        self.memory_service = SharedMemoryService()
        
        # Create test memory items
        self.memory1 = {
            "key": "test_memory_1",
            "value": {"data": "test data 1"},
            "memory_type": MemoryType.FACTUAL,
            "scope": MemoryScope.AGENT,
            "scope_id": "agent1",
            "agent_id": "agent1",
            "importance": 0.8,
            "tags": ["test", "agent1"]
        }
        
        self.memory2 = {
            "key": "test_memory_2",
            "value": {"data": "test data 2"},
            "memory_type": MemoryType.PROCEDURAL,
            "scope": MemoryScope.TEAM,
            "scope_id": "team1",
            "agent_id": "agent2",
            "importance": 0.7,
            "tags": ["test", "team1"]
        }
        
        self.memory3 = {
            "key": "test_memory_3",
            "value": {"data": "test data 3"},
            "memory_type": MemoryType.EPISODIC,
            "scope": MemoryScope.TASK,
            "scope_id": "task1",
            "agent_id": "agent1",
            "importance": 0.9,
            "tags": ["test", "task1"]
        }
    
    def test_create_memory(self):
        """Test creating memory items."""
        # Create memory items
        memory_id1 = self.memory_service.create_memory(
            key=self.memory1["key"],
            value=self.memory1["value"],
            memory_type=self.memory1["memory_type"],
            scope=self.memory1["scope"],
            scope_id=self.memory1["scope_id"],
            agent_id=self.memory1["agent_id"],
            importance=self.memory1["importance"],
            tags=self.memory1["tags"]
        )
        
        memory_id2 = self.memory_service.create_memory(
            key=self.memory2["key"],
            value=self.memory2["value"],
            memory_type=self.memory2["memory_type"],
            scope=self.memory2["scope"],
            scope_id=self.memory2["scope_id"],
            agent_id=self.memory2["agent_id"],
            importance=self.memory2["importance"],
            tags=self.memory2["tags"]
        )
        
        # Check if memory items are created
        self.assertIsNotNone(memory_id1)
        self.assertIsNotNone(memory_id2)
        self.assertIn(memory_id1, self.memory_service.memories)
        self.assertIn(memory_id2, self.memory_service.memories)
    
    def test_get_memory(self):
        """Test getting memory items."""
        # Create memory item
        memory_id = self.memory_service.create_memory(
            key=self.memory1["key"],
            value=self.memory1["value"],
            memory_type=self.memory1["memory_type"],
            scope=self.memory1["scope"],
            scope_id=self.memory1["scope_id"],
            agent_id=self.memory1["agent_id"],
            importance=self.memory1["importance"],
            tags=self.memory1["tags"]
        )
        
        # Get memory item
        memory = self.memory_service.get_memory(memory_id)
        
        # Check if memory item is retrieved correctly
        self.assertIsNotNone(memory)
        self.assertEqual(memory.key, self.memory1["key"])
        self.assertEqual(memory.value, self.memory1["value"])
        self.assertEqual(memory.memory_type, self.memory1["memory_type"])
        self.assertEqual(memory.scope, self.memory1["scope"])
        self.assertEqual(memory.scope_id, self.memory1["scope_id"])
        self.assertEqual(memory.agent_id, self.memory1["agent_id"])
        self.assertEqual(memory.importance, self.memory1["importance"])
        self.assertEqual(memory.tags, self.memory1["tags"])
        
        # Try getting non-existent memory item
        memory = self.memory_service.get_memory("non-existent-memory")
        self.assertIsNone(memory)
    
    def test_update_memory(self):
        """Test updating memory items."""
        # Create memory item
        memory_id = self.memory_service.create_memory(
            key=self.memory1["key"],
            value=self.memory1["value"],
            memory_type=self.memory1["memory_type"],
            scope=self.memory1["scope"],
            scope_id=self.memory1["scope_id"],
            agent_id=self.memory1["agent_id"],
            importance=self.memory1["importance"],
            tags=self.memory1["tags"]
        )
        
        # Update memory item
        new_value = {"data": "updated test data"}
        new_importance = 0.9
        new_tags = ["test", "agent1", "updated"]
        
        result = self.memory_service.update_memory(
            memory_id=memory_id,
            value=new_value,
            importance=new_importance,
            tags=new_tags
        )
        
        # Check if update was successful
        self.assertTrue(result)
        
        # Get updated memory item
        memory = self.memory_service.get_memory(memory_id)
        
        # Check if memory item is updated correctly
        self.assertEqual(memory.value, new_value)
        self.assertEqual(memory.importance, new_importance)
        self.assertEqual(memory.tags, new_tags)
        
        # Try updating non-existent memory item
        result = self.memory_service.update_memory(
            memory_id="non-existent-memory",
            value=new_value
        )
        self.assertFalse(result)
    
    def test_delete_memory(self):
        """Test deleting memory items."""
        # Create memory item
        memory_id = self.memory_service.create_memory(
            key=self.memory1["key"],
            value=self.memory1["value"],
            memory_type=self.memory1["memory_type"],
            scope=self.memory1["scope"],
            scope_id=self.memory1["scope_id"],
            agent_id=self.memory1["agent_id"],
            importance=self.memory1["importance"],
            tags=self.memory1["tags"]
        )
        
        # Delete memory item
        result = self.memory_service.delete_memory(memory_id)
        
        # Check if deletion was successful
        self.assertTrue(result)
        self.assertNotIn(memory_id, self.memory_service.memories)
        
        # Try deleting non-existent memory item
        result = self.memory_service.delete_memory("non-existent-memory")
        self.assertFalse(result)
    
    def test_get_agent_memory(self):
        """Test getting memory for an agent."""
        # Create memory items
        self.memory_service.create_memory(
            key=self.memory1["key"],
            value=self.memory1["value"],
            memory_type=self.memory1["memory_type"],
            scope=self.memory1["scope"],
            scope_id=self.memory1["scope_id"],
            agent_id=self.memory1["agent_id"],
            importance=self.memory1["importance"],
            tags=self.memory1["tags"]
        )
        
        self.memory_service.create_memory(
            key=self.memory2["key"],
            value=self.memory2["value"],
            memory_type=self.memory2["memory_type"],
            scope=self.memory2["scope"],
            scope_id=self.memory2["scope_id"],
            agent_id=self.memory2["agent_id"],
            importance=self.memory2["importance"],
            tags=self.memory2["tags"]
        )
        
        self.memory_service.create_memory(
            key=self.memory3["key"],
            value=self.memory3["value"],
            memory_type=self.memory3["memory_type"],
            scope=self.memory3["scope"],
            scope_id=self.memory3["scope_id"],
            agent_id=self.memory3["agent_id"],
            importance=self.memory3["importance"],
            tags=self.memory3["tags"]
        )
        
        # Register agent-team and agent-task relationships
        self.memory_service.register_agent_team("agent1", "team1")
        self.memory_service.register_agent_task("agent1", "task1")
        
        # Get memory for agent1
        agent_memory = self.memory_service.get_agent_memory("agent1")
        
        # Check if agent memory is retrieved correctly
        self.assertEqual(len(agent_memory), 3)
        self.assertEqual(agent_memory[self.memory1["key"]], self.memory1["value"])
        self.assertEqual(agent_memory[self.memory2["key"]], self.memory2["value"])
        self.assertEqual(agent_memory[self.memory3["key"]], self.memory3["value"])
        
        # Get memory for agent2
        agent_memory = self.memory_service.get_agent_memory("agent2")
        
        # Check if agent memory is retrieved correctly
        self.assertEqual(len(agent_memory), 1)
        self.assertEqual(agent_memory[self.memory2["key"]], self.memory2["value"])
        
        # Get memory for agent1 with specific memory type
        agent_memory = self.memory_service.get_agent_memory(
            agent_id="agent1",
            memory_types=[MemoryType.FACTUAL]
        )
        
        # Check if filtered agent memory is retrieved correctly
        self.assertEqual(len(agent_memory), 1)
        self.assertEqual(agent_memory[self.memory1["key"]], self.memory1["value"])
        
        # Get memory for agent1 with minimum importance
        agent_memory = self.memory_service.get_agent_memory(
            agent_id="agent1",
            min_importance=0.9
        )
        
        # Check if filtered agent memory is retrieved correctly
        self.assertEqual(len(agent_memory), 1)
        self.assertEqual(agent_memory[self.memory3["key"]], self.memory3["value"])


class TestCollaborativeLearningService(unittest.TestCase):
    """Tests for the CollaborativeLearningService class."""
    
    def setUp(self):
        self.learning_service = CollaborativeLearningService()
        
        # Create test agents
        self.agent_ids = ["agent1", "agent2", "agent3"]
        
        # Create test team and task
        self.team_id = "team1"
        self.task_id = "task1"
    
    def test_record_event(self):
        """Test recording learning events."""
        # Record observation event
        observation_id = self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent1",
            content={"observation": "test observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        # Check if event is recorded
        self.assertIsNotNone(observation_id)
        self.assertIn(observation_id, self.learning_service.event_store.events)
        
        # Get event
        event = self.learning_service.event_store.get_event(observation_id)
        
        # Check event properties
        self.assertEqual(event.event_type, LearningEventType.OBSERVATION)
        self.assertEqual(event.agent_id, "agent1")
        self.assertEqual(event.content, {"observation": "test observation"})
        self.assertEqual(event.task_id, self.task_id)
        self.assertEqual(event.team_id, self.team_id)
        
        # Record action event
        action_id = self.learning_service.record_event(
            event_type=LearningEventType.ACTION,
            agent_id="agent1",
            content={"action": "test action"},
            task_id=self.task_id,
            team_id=self.team_id,
            related_events=[observation_id]
        )
        
        # Check if event is recorded
        self.assertIsNotNone(action_id)
        self.assertIn(action_id, self.learning_service.event_store.events)
        
        # Get event
        event = self.learning_service.event_store.get_event(action_id)
        
        # Check event properties
        self.assertEqual(event.event_type, LearningEventType.ACTION)
        self.assertEqual(event.agent_id, "agent1")
        self.assertEqual(event.content, {"action": "test action"})
        self.assertEqual(event.task_id, self.task_id)
        self.assertEqual(event.team_id, self.team_id)
        self.assertEqual(event.related_events, [observation_id])
    
    def test_get_agent_history(self):
        """Test getting agent history."""
        # Record events for agent1
        observation_id = self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent1",
            content={"observation": "test observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        action_id = self.learning_service.record_event(
            event_type=LearningEventType.ACTION,
            agent_id="agent1",
            content={"action": "test action"},
            task_id=self.task_id,
            team_id=self.team_id,
            related_events=[observation_id]
        )
        
        # Record event for agent2
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent2",
            content={"observation": "agent2 observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        # Get history for agent1
        history = self.learning_service.get_agent_history("agent1")
        
        # Check if history is retrieved correctly
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["event_type"], "action")
        self.assertEqual(history[0]["agent_id"], "agent1")
        self.assertEqual(history[0]["content"], {"action": "test action"})
        self.assertEqual(history[1]["event_type"], "observation")
        self.assertEqual(history[1]["agent_id"], "agent1")
        self.assertEqual(history[1]["content"], {"observation": "test observation"})
        
        # Get history for agent1 with specific event type
        history = self.learning_service.get_agent_history(
            agent_id="agent1",
            event_types=[LearningEventType.OBSERVATION]
        )
        
        # Check if filtered history is retrieved correctly
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["event_type"], "observation")
        self.assertEqual(history[0]["agent_id"], "agent1")
        self.assertEqual(history[0]["content"], {"observation": "test observation"})
    
    def test_get_team_history(self):
        """Test getting team history."""
        # Record events for team1
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent1",
            content={"observation": "agent1 observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent2",
            content={"observation": "agent2 observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        # Record event for another team
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent3",
            content={"observation": "agent3 observation"},
            task_id="task2",
            team_id="team2"
        )
        
        # Get history for team1
        history = self.learning_service.get_team_history(self.team_id)
        
        # Check if history is retrieved correctly
        self.assertEqual(len(history), 2)
        self.assertTrue(any(h["agent_id"] == "agent1" for h in history))
        self.assertTrue(any(h["agent_id"] == "agent2" for h in history))
    
    def test_get_task_history(self):
        """Test getting task history."""
        # Record events for task1
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent1",
            content={"observation": "agent1 observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent2",
            content={"observation": "agent2 observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        
        # Record event for another task
        self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent3",
            content={"observation": "agent3 observation"},
            task_id="task2",
            team_id="team2"
        )
        
        # Get history for task1
        history = self.learning_service.get_task_history(self.task_id)
        
        # Check if history is retrieved correctly
        self.assertEqual(len(history), 2)
        self.assertTrue(any(h["agent_id"] == "agent1" for h in history))
        self.assertTrue(any(h["agent_id"] == "agent2" for h in history))
    
    def test_analyze_events(self):
        """Test analyzing events."""
        # Record a sequence of events
        event_ids = []
        
        observation_id = self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent1",
            content={"observation": "test observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        event_ids.append(observation_id)
        
        action_id = self.learning_service.record_event(
            event_type=LearningEventType.ACTION,
            agent_id="agent1",
            content={"action": "test action"},
            task_id=self.task_id,
            team_id=self.team_id,
            related_events=[observation_id]
        )
        event_ids.append(action_id)
        
        feedback_id = self.learning_service.record_event(
            event_type=LearningEventType.FEEDBACK,
            agent_id="agent2",
            content={"feedback": "test feedback", "rating": 4},
            task_id=self.task_id,
            team_id=self.team_id,
            related_events=[action_id]
        )
        event_ids.append(feedback_id)
        
        # Analyze events
        results = self.learning_service.analyze_events(event_ids)
        
        # Check analysis results
        self.assertEqual(results["events_analyzed"], 3)
        self.assertIn("patterns_detected", results)
        self.assertIn("matching_patterns", results)
        self.assertIn("insights_generated", results)
    
    def test_get_insights(self):
        """Test getting insights."""
        # Record a sequence of events and generate insights
        event_ids = []
        
        observation_id = self.learning_service.record_event(
            event_type=LearningEventType.OBSERVATION,
            agent_id="agent1",
            content={"observation": "test observation"},
            task_id=self.task_id,
            team_id=self.team_id
        )
        event_ids.append(observation_id)
        
        action_id = self.learning_service.record_event(
            event_type=LearningEventType.ACTION,
            agent_id="agent1",
            content={"action": "test action"},
            task_id=self.task_id,
            team_id=self.team_id,
            related_events=[observation_id]
        )
        event_ids.append(action_id)
        
        feedback_id = self.learning_service.record_event(
            event_type=LearningEventType.FEEDBACK,
            agent_id="agent2",
            content={"feedback": "test feedback", "rating": 4},
            task_id=self.task_id,
            team_id=self.team_id,
            related_events=[action_id]
        )
        event_ids.append(feedback_id)
        
        # Analyze events to generate insights
        self.learning_service.analyze_events(event_ids)
        
        # Get insights
        insights = self.learning_service.get_insights()
        
        # Check if insights are retrieved
        self.assertIsInstance(insights, list)


class TestCollaborationManager(unittest.TestCase):
    """Tests for the CollaborationManager class."""
    
    def setUp(self):
        self.collaboration_manager = CollaborationManager()
        
        # Create test agents
        self.agent1_id = "agent1"
        self.agent2_id = "agent2"
        self.agent3_id = "agent3"
        
        # Register agents
        self.collaboration_manager.register_agent(
            agent_id=self.agent1_id,
            name="Agent 1",
            capabilities={
                "reasoning": 0.9,
                "planning": 0.8,
                "code_generation": 0.7
            },
            specializations=["finance", "data analysis"]
        )
        
        self.collaboration_manager.register_agent(
            agent_id=self.agent2_id,
            name="Agent 2",
            capabilities={
                "creative_writing": 0.9,
                "research": 0.8,
                "reasoning": 0.6
            },
            specializations=["marketing", "content creation"]
        )
        
        self.collaboration_manager.register_agent(
            agent_id=self.agent3_id,
            name="Agent 3",
            capabilities={
                "visual_design": 0.9,
                "creative_writing": 0.7,
                "research": 0.6
            },
            specializations=["design", "marketing"]
        )
    
    def test_create_task(self):
        """Test creating a task."""
        # Create task
        task_id = self.collaboration_manager.create_task(
            name="Test Task",
            description="A test task for collaboration",
            required_capabilities={
                "reasoning": 0.7,
                "creative_writing": 0.7,
                "research": 0.6
            },
            domain_specializations=["marketing", "data analysis"],
            priority=7,
            estimated_duration=2.0,
            complexity=6,
            min_team_size=2,
            max_team_size=3
        )
        
        # Check if task is created
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.collaboration_manager.active_tasks)
        
        # Get task info
        task_info = self.collaboration_manager.get_task_info(task_id)
        
        # Check task properties
        self.assertEqual(task_info["name"], "Test Task")
        self.assertEqual(task_info["description"], "A test task for collaboration")
        self.assertEqual(task_info["required_capabilities"]["reasoning"], 0.7)
        self.assertEqual(task_info["required_capabilities"]["creative_writing"], 0.7)
        self.assertEqual(task_info["required_capabilities"]["research"], 0.6)
        self.assertEqual(task_info["domain_specializations"], ["marketing", "data analysis"])
        self.assertEqual(task_info["priority"], 7)
        self.assertEqual(task_info["estimated_duration"], 2.0)
        self.assertEqual(task_info["complexity"], 6)
        self.assertEqual(task_info["min_team_size"], 2)
        self.assertEqual(task_info["max_team_size"], 3)
    
    def test_form_team(self):
        """Test forming a team for a task."""
        # Create task
        task_id = self.collaboration_manager.create_task(
            name="Test Task",
            description="A test task for collaboration",
            required_capabilities={
                "reasoning": 0.7,
                "creative_writing": 0.7,
                "research": 0.6
            },
            domain_specializations=["marketing", "data analysis"],
            priority=7,
            estimated_duration=2.0,
            complexity=6,
            min_team_size=2,
            max_team_size=3
        )
        
        # Form team
        team_id = self.collaboration_manager.form_team(task_id)
        
        # Check if team is formed
        self.assertIsNotNone(team_id)
        self.assertIn(team_id, self.collaboration_manager.active_teams)
        
        # Get team info
        team_info = self.collaboration_manager.get_team_info(team_id)
        
        # Check team properties
        self.assertEqual(team_info["task_id"], task_id)
        self.assertEqual(len(team_info["members"]), 2)
        self.assertIn(self.agent1_id, team_info["members"])
        self.assertIn(self.agent2_id, team_info["members"])
    
    def test_disband_team(self):
        """Test disbanding a team."""
        # Create task
        task_id = self.collaboration_manager.create_task(
            name="Test Task",
            description="A test task for collaboration",
            required_capabilities={
                "reasoning": 0.7,
                "creative_writing": 0.7,
                "research": 0.6
            },
            domain_specializations=["marketing", "data analysis"],
            priority=7,
            estimated_duration=2.0,
            complexity=6,
            min_team_size=2,
            max_team_size=3
        )
        
        # Form team
        team_id = self.collaboration_manager.form_team(task_id)
        
        # Check if team is formed
        self.assertIsNotNone(team_id)
        self.assertIn(team_id, self.collaboration_manager.active_teams)
        
        # Disband team
        result = self.collaboration_manager.disband_team(team_id)
        
        # Check if team is disbanded
        self.assertTrue(result)
        self.assertNotIn(team_id, self.collaboration_manager.active_teams)
    
    def test_initiate_task_negotiation(self):
        """Test initiating a task negotiation."""
        # Create task
        task_id = self.collaboration_manager.create_task(
            name="Test Task",
            description="A test task for collaboration",
            required_capabilities={
                "reasoning": 0.7,
                "creative_writing": 0.7,
                "research": 0.6
            },
            domain_specializations=["marketing", "data analysis"],
            priority=7,
            estimated_duration=2.0,
            complexity=6,
            min_team_size=2,
            max_team_size=3
        )
        
        # Form team
        team_id = self.collaboration_manager.form_team(task_id)
        
        # Initiate negotiation
        negotiation_id = self.collaboration_manager.initiate_task_negotiation(
            team_id=team_id,
            initiator_id=self.agent1_id
        )
        
        # Check if negotiation is initiated
        self.assertIsNotNone(negotiation_id)
        
        # Get negotiation status
        status = self.collaboration_manager.get_negotiation_status(negotiation_id)
        
        # Check negotiation properties
        self.assertEqual(status["negotiation_type"], "task_allocation")
        self.assertEqual(status["initiator_id"], self.agent1_id)
        self.assertIn(self.agent1_id, status["participants"])
        self.assertIn(self.agent2_id, status["participants"])
        self.assertEqual(status["status"], "active")
    
    def test_share_context(self):
        """Test sharing context."""
        # Share context
        context_id = self.collaboration_manager.share_context(
            key="test_context",
            value={"data": "test data"},
            context_type="user_input",
            scope="agent",
            scope_id=self.agent1_id,
            agent_id=self.agent1_id
        )
        
        # Check if context is shared
        self.assertIsNotNone(context_id)
        
        # Get agent context
        agent_context = self.collaboration_manager.get_agent_context(self.agent1_id)
        
        # Check if context is accessible
        self.assertIn("test_context", agent_context)
        self.assertEqual(agent_context["test_context"], {"data": "test data"})
    
    def test_store_memory(self):
        """Test storing memory."""
        # Store memory
        memory_id = self.collaboration_manager.store_memory(
            key="test_memory",
            value={"data": "test data"},
            memory_type="factual",
            scope="agent",
            scope_id=self.agent1_id,
            agent_id=self.agent1_id,
            importance=0.8,
            tags=["test", "agent1"]
        )
        
        # Check if memory is stored
        self.assertIsNotNone(memory_id)
        
        # Get agent memory
        agent_memory = self.collaboration_manager.get_agent_memory(self.agent1_id)
        
        # Check if memory is accessible
        self.assertIn("test_memory", agent_memory)
        self.assertEqual(agent_memory["test_memory"], {"data": "test data"})
    
    def test_record_learning_event(self):
        """Test recording learning events."""
        # Record learning event
        event_id = self.collaboration_manager.record_learning_event(
            event_type="observation",
            agent_id=self.agent1_id,
            content={"observation": "test observation"},
            task_id="task1",
            team_id="team1"
        )
        
        # Check if event is recorded
        self.assertIsNotNone(event_id)
        
        # Get agent learning history
        history = self.collaboration_manager.get_agent_learning_history(self.agent1_id)
        
        # Check if event is in history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["event_type"], "observation")
        self.assertEqual(history[0]["agent_id"], self.agent1_id)
        self.assertEqual(history[0]["content"], {"observation": "test observation"})
    
    def test_unregister_agent(self):
        """Test unregistering an agent."""
        # Unregister agent
        result = self.collaboration_manager.unregister_agent(self.agent3_id)
        
        # Check if agent is unregistered
        self.assertTrue(result)
        
        # Try to get agent profile
        profile = self.collaboration_manager.capability_registry.get_agent_profile(self.agent3_id)
        
        # Check if profile is removed
        self.assertIsNone(profile)


class TestCollaborativeAgent(unittest.TestCase):
    """Tests for the CollaborativeAgent class."""
    
    def setUp(self):
        self.collaboration_manager = CollaborationManager()
        
        # Create collaborative agent
        self.agent = CollaborativeAgent(
            agent_id="agent1",
            name="Agent 1",
            capabilities={
                "reasoning": 0.9,
                "planning": 0.8,
                "code_generation": 0.7
            },
            specializations=["finance", "data analysis"],
            collaboration_manager=self.collaboration_manager
        )
    
    def test_share_context(self):
        """Test sharing context."""
        # Share context
        context_id = self.agent.share_context(
            key="test_context",
            value={"data": "test data"},
            context_type="user_input",
            scope="agent",
            scope_id="agent1"
        )
        
        # Check if context is shared
        self.assertIsNotNone(context_id)
        
        # Get agent context
        agent_context = self.agent.get_context()
        
        # Check if context is accessible
        self.assertIn("test_context", agent_context)
        self.assertEqual(agent_context["test_context"], {"data": "test data"})
    
    def test_store_memory(self):
        """Test storing memory."""
        # Store memory
        memory_id = self.agent.store_memory(
            key="test_memory",
            value={"data": "test data"},
            memory_type="factual",
            scope="agent",
            scope_id="agent1",
            importance=0.8,
            tags=["test", "agent1"]
        )
        
        # Check if memory is stored
        self.assertIsNotNone(memory_id)
        
        # Get agent memory
        agent_memory = self.agent.get_memory()
        
        # Check if memory is accessible
        self.assertIn("test_memory", agent_memory)
        self.assertEqual(agent_memory["test_memory"], {"data": "test data"})
    
    def test_record_observation(self):
        """Test recording observations."""
        # Record observation
        event_id = self.agent.record_observation(
            content={"observation": "test observation"},
            task_id="task1",
            team_id="team1"
        )
        
        # Check if observation is recorded
        self.assertIsNotNone(event_id)
        
        # Get agent learning history
        history = self.agent.get_learning_history()
        
        # Check if observation is in history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["event_type"], "observation")
        self.assertEqual(history[0]["agent_id"], "agent1")
        self.assertEqual(history[0]["content"], {"observation": "test observation"})
    
    def test_record_action(self):
        """Test recording actions."""
        # Record action
        event_id = self.agent.record_action(
            content={"action": "test action"},
            task_id="task1",
            team_id="team1"
        )
        
        # Check if action is recorded
        self.assertIsNotNone(event_id)
        
        # Get agent learning history
        history = self.agent.get_learning_history()
        
        # Check if action is in history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["event_type"], "action")
        self.assertEqual(history[0]["agent_id"], "agent1")
        self.assertEqual(history[0]["content"], {"action": "test action"})
    
    def test_record_insight(self):
        """Test recording insights."""
        # Record insight
        event_id = self.agent.record_insight(
            content={"insight": "test insight"},
            task_id="task1",
            team_id="team1"
        )
        
        # Check if insight is recorded
        self.assertIsNotNone(event_id)
        
        # Get agent learning history
        history = self.agent.get_learning_history()
        
        # Check if insight is in history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["event_type"], "insight")
        self.assertEqual(history[0]["agent_id"], "agent1")
        self.assertEqual(history[0]["content"], {"insight": "test insight"})


class TestCollaborativeProviderAdapter(unittest.TestCase):
    """Tests for the CollaborativeProviderAdapter class."""
    
    def setUp(self):
        # Create mock providers
        self.providers = [
            MockProvider("provider1", "Provider 1", ["text_generation", "code_generation"]),
            MockProvider("provider2", "Provider 2", ["text_generation", "embedding"]),
            MockProvider("provider3", "Provider 3", ["image_generation", "function_calling"])
        ]
        
        # Create mock provider selector
        self.provider_selector = MockProviderSelector(self.providers)
        
        # Create collaboration manager
        self.collaboration_manager = CollaborationManager()
        
        # Create provider adapter
        self.provider_adapter = CollaborativeProviderAdapter(
            collaboration_manager=self.collaboration_manager,
            provider_selector=self.provider_selector
        )
    
    def test_register_providers(self):
        """Test registering providers as collaborative agents."""
        # Check if providers are registered
        self.assertEqual(len(self.provider_adapter.collaborative_agents), 3)
        self.assertIn("provider-provider1", self.provider_adapter.collaborative_agents)
        self.assertIn("provider-provider2", self.provider_adapter.collaborative_agents)
        self.assertIn("provider-provider3", self.provider_adapter.collaborative_agents)
    
    def test_create_task_team(self):
        """Test creating a task and forming a team of providers."""
        # Create task team
        result = self.provider_adapter.create_task_team(
            task_name="Test Task",
            task_description="A test task for provider collaboration",
            required_capabilities={
                "reasoning": 0.7,
                "code_generation": 0.7
            },
            min_team_size=2,
            max_team_size=3
        )
        
        # Check if task team is created
        self.assertIsNotNone(result)
        self.assertIn("task", result)
        self.assertIn("team", result)
        
        # Check task properties
        self.assertEqual(result["task"]["name"], "Test Task")
        self.assertEqual(result["task"]["description"], "A test task for provider collaboration")
        
        # Check team properties
        self.assertEqual(len(result["team"]["members"]), 2)
    
    def test_get_provider_agent(self):
        """Test getting the collaborative agent for a provider."""
        # Get provider agent
        agent = self.provider_adapter.get_provider_agent("provider1")
        
        # Check if agent is retrieved
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_id, "provider-provider1")
        self.assertEqual(agent.name, "Provider 1")
    
    def test_get_team_providers(self):
        """Test getting all providers in a team."""
        # Create task team
        result = self.provider_adapter.create_task_team(
            task_name="Test Task",
            task_description="A test task for provider collaboration",
            required_capabilities={
                "reasoning": 0.7,
                "code_generation": 0.7
            },
            min_team_size=2,
            max_team_size=3
        )
        
        # Get team ID
        team_id = result["team"]["team_id"]
        
        # Get team providers
        providers = self.provider_adapter.get_team_providers(team_id)
        
        # Check if providers are retrieved
        self.assertEqual(len(providers), 2)
    
    def test_share_provider_context(self):
        """Test sharing context from a provider."""
        # Share context
        context_id = self.provider_adapter.share_provider_context(
            provider_id="provider1",
            key="test_context",
            value={"data": "test data"},
            context_type="user_input",
            scope="agent",
            scope_id="provider-provider1"
        )
        
        # Check if context is shared
        self.assertIsNotNone(context_id)
        
        # Get provider context
        provider_context = self.provider_adapter.get_provider_context("provider1")
        
        # Check if context is accessible
        self.assertIn("test_context", provider_context)
        self.assertEqual(provider_context["test_context"], {"data": "test data"})
    
    def test_get_provider_memory(self):
        """Test getting memory for a provider."""
        # Get provider agent
        agent = self.provider_adapter.get_provider_agent("provider1")
        
        # Store memory
        memory_id = agent.store_memory(
            key="test_memory",
            value={"data": "test data"},
            memory_type="factual",
            scope="agent",
            scope_id="provider-provider1",
            importance=0.8,
            tags=["test", "provider1"]
        )
        
        # Check if memory is stored
        self.assertIsNotNone(memory_id)
        
        # Get provider memory
        provider_memory = self.provider_adapter.get_provider_memory("provider1")
        
        # Check if memory is accessible
        self.assertIn("test_memory", provider_memory)
        self.assertEqual(provider_memory["test_memory"], {"data": "test data"})


if __name__ == "__main__":
    unittest.main()
