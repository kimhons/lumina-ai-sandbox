"""
Collaborative Problem Solving capabilities for Lumina AI.

This module implements collaborative problem solving capabilities that integrate
the Enhanced Learning System with the Multi-Agent Collaboration System.
"""

import os
import logging
import datetime
import json
import uuid
import time
import random
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
import requests
from dataclasses import dataclass, field

# Import Enhanced Learning System components
from lumina_ai_monorepo.learning.core.algorithm_factory import AlgorithmFactory
from lumina_ai_monorepo.learning.core.model_registry import ModelRegistry
from lumina_ai_monorepo.learning.explainable.explainability import ExplainabilityEngine

# Import Multi-Agent Collaboration System components
from lumina_ai_monorepo.collaboration.team_formation import TeamFormationSystem
from lumina_ai_monorepo.collaboration.context_manager import ContextManager
from lumina_ai_monorepo.collaboration.negotiation import NegotiationSystem

# Import Integration components
from lumina_ai_monorepo.learning.integration.knowledge_transfer_integration import KnowledgeTransferIntegration
from lumina_ai_monorepo.learning.integration.collaborative_learning import CollaborativeLearningMechanisms

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProblemSolvingConfig:
    """Configuration for collaborative problem solving."""
    
    # General settings
    enabled: bool = True
    storage_path: str = "/tmp/lumina_problem_solving"
    
    # Problem decomposition settings
    max_decomposition_depth: int = 3
    min_subtask_size: int = 1
    max_subtasks_per_agent: int = 5
    
    # Team settings
    dynamic_team_formation: bool = True
    expertise_based_assignment: bool = True
    
    # Solution settings
    solution_aggregation_method: str = "weighted_consensus"  # "weighted_consensus", "voting", "hierarchical"
    solution_verification: bool = True
    
    # Learning settings
    learn_from_solutions: bool = True
    solution_feedback_enabled: bool = True
    
    # Performance settings
    parallel_solving: bool = True
    timeout_seconds: int = 300
    
    # Integration settings
    learning_system_api_url: str = "http://localhost:8080/api/learning"
    collaboration_system_api_url: str = "http://localhost:8081/api/collaboration"
    knowledge_transfer_api_url: str = "http://localhost:8082/api/knowledge-transfer"
    collaborative_learning_api_url: str = "http://localhost:8083/api/collaborative-learning"


class ProblemSolvingCapabilities:
    """
    Collaborative Problem Solving Capabilities for Lumina AI.
    
    This class provides capabilities for collaborative problem solving between agents,
    enabling them to tackle complex problems through coordinated efforts.
    """
    
    def __init__(self, config: ProblemSolvingConfig = None,
                 knowledge_transfer: KnowledgeTransferIntegration = None,
                 collaborative_learning: CollaborativeLearningMechanisms = None):
        """
        Initialize the Collaborative Problem Solving Capabilities.
        
        Args:
            config: Configuration for problem solving
            knowledge_transfer: Knowledge Transfer Integration instance
            collaborative_learning: Collaborative Learning Mechanisms instance
        """
        # Load configuration
        self.config = config or ProblemSolvingConfig()
        
        # Create storage directory
        os.makedirs(self.config.storage_path, exist_ok=True)
        
        # Initialize integration components
        self.knowledge_transfer = knowledge_transfer or KnowledgeTransferIntegration()
        self.collaborative_learning = collaborative_learning or CollaborativeLearningMechanisms()
        
        # Initialize learning components
        self.algorithm_factory = AlgorithmFactory()
        self.model_registry = ModelRegistry()
        self.explainability_engine = ExplainabilityEngine()
        
        # Initialize collaboration components
        self.team_formation = TeamFormationSystem()
        self.context_manager = ContextManager()
        self.negotiation_system = NegotiationSystem()
        
        # Initialize metrics
        self.metrics = {
            "problems_solved": 0,
            "solution_success_rate": 0.0,
            "average_solution_time": 0.0,
            "knowledge_items_created": 0,
            "last_activity_timestamp": None
        }
        
        logger.info("Collaborative Problem Solving Capabilities initialized")
    
    def analyze_problem(self, problem_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a problem to determine solution approach and requirements.
        
        Args:
            problem_spec: Specification of the problem to solve
            
        Returns:
            result: Problem analysis result
        """
        try:
            # Extract problem details
            problem_id = problem_spec.get("problem_id", str(uuid.uuid4()))
            problem_type = problem_spec.get("problem_type", "unknown")
            problem_domain = problem_spec.get("domain", "general")
            problem_description = problem_spec.get("description", "")
            problem_constraints = problem_spec.get("constraints", [])
            
            # Initialize analysis result
            analysis_result = {
                "problem_id": problem_id,
                "problem_type": problem_type,
                "domain": problem_domain,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Determine if problem is suitable for collaborative solving
            is_collaborative = self._is_collaborative_problem(problem_spec)
            analysis_result["is_collaborative"] = is_collaborative
            
            if not is_collaborative:
                analysis_result["recommendation"] = "single_agent_solving"
                analysis_result["reason"] = "Problem is not complex enough to warrant collaborative solving"
                return analysis_result
            
            # Identify required capabilities
            required_capabilities = self._identify_required_capabilities(problem_spec)
            analysis_result["required_capabilities"] = required_capabilities
            
            # Determine decomposition approach
            decomposition_approach = self._determine_decomposition_approach(problem_spec)
            analysis_result["decomposition_approach"] = decomposition_approach
            
            # Estimate resource requirements
            resource_requirements = self._estimate_resource_requirements(problem_spec)
            analysis_result["resource_requirements"] = resource_requirements
            
            # Identify relevant knowledge and models
            relevant_knowledge = self._identify_relevant_knowledge(problem_spec)
            analysis_result["relevant_knowledge"] = relevant_knowledge
            
            # Determine solution verification approach
            verification_approach = self._determine_verification_approach(problem_spec)
            analysis_result["verification_approach"] = verification_approach
            
            # Provide overall recommendation
            analysis_result["recommendation"] = "collaborative_solving"
            analysis_result["approach"] = self._determine_solving_approach(problem_spec, required_capabilities)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing problem: {e}")
            return {
                "status": "error",
                "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def decompose_problem(self, 
                         problem_spec: Dict[str, Any],
                         analysis_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Decompose a complex problem into subtasks.
        
        Args:
            problem_spec: Specification of the problem to decompose
            analysis_result: Result of problem analysis (if already performed)
            
        Returns:
            result: Problem decomposition result
        """
        try:
            # Get or perform problem analysis
            if analysis_result is None:
                analysis_result = self.analyze_problem(problem_spec)
            
            # Extract problem details
            problem_id = problem_spec.get("problem_id", str(uuid.uuid4()))
            problem_type = problem_spec.get("problem_type", "unknown")
            
            # Check if problem is suitable for decomposition
            if not analysis_result.get("is_collaborative", False):
                return {
                    "status": "warning",
                    "problem_id": problem_id,
                    "message": "Problem is not suitable for decomposition",
                    "subtasks": [],
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Get decomposition approach
            decomposition_approach = analysis_result.get("decomposition_approach", {})
            approach_type = decomposition_approach.get("type", "functional")
            
            # Initialize subtasks list
            subtasks = []
            
            # Decompose problem based on approach type
            if approach_type == "functional":
                # Functional decomposition - break down by function/operation
                functions = decomposition_approach.get("functions", [])
                
                for i, function in enumerate(functions):
                    subtask = {
                        "subtask_id": f"{problem_id}_subtask_{i}",
                        "type": "functional",
                        "function": function.get("name"),
                        "description": function.get("description"),
                        "inputs": function.get("inputs", []),
                        "outputs": function.get("outputs", []),
                        "dependencies": function.get("dependencies", []),
                        "required_capabilities": function.get("required_capabilities", []),
                        "priority": function.get("priority", "medium")
                    }
                    subtasks.append(subtask)
                
            elif approach_type == "domain":
                # Domain decomposition - break down by knowledge domain
                domains = decomposition_approach.get("domains", [])
                
                for i, domain in enumerate(domains):
                    subtask = {
                        "subtask_id": f"{problem_id}_subtask_{i}",
                        "type": "domain",
                        "domain": domain.get("name"),
                        "description": domain.get("description"),
                        "inputs": domain.get("inputs", []),
                        "outputs": domain.get("outputs", []),
                        "dependencies": domain.get("dependencies", []),
                        "required_capabilities": domain.get("required_capabilities", []),
                        "priority": domain.get("priority", "medium")
                    }
                    subtasks.append(subtask)
                
            elif approach_type == "data":
                # Data decomposition - break down by data partitions
                partitions = decomposition_approach.get("partitions", [])
                
                for i, partition in enumerate(partitions):
                    subtask = {
                        "subtask_id": f"{problem_id}_subtask_{i}",
                        "type": "data",
                        "partition": partition.get("name"),
                        "description": partition.get("description"),
                        "data_filter": partition.get("filter"),
                        "inputs": partition.get("inputs", []),
                        "outputs": partition.get("outputs", []),
                        "dependencies": partition.get("dependencies", []),
                        "required_capabilities": partition.get("required_capabilities", []),
                        "priority": partition.get("priority", "medium")
                    }
                    subtasks.append(subtask)
                
            elif approach_type == "hierarchical":
                # Hierarchical decomposition - break down by levels
                levels = decomposition_approach.get("levels", [])
                
                # Process each level
                for level_idx, level in enumerate(levels):
                    level_subtasks = level.get("subtasks", [])
                    
                    for i, level_subtask in enumerate(level_subtasks):
                        subtask = {
                            "subtask_id": f"{problem_id}_level_{level_idx}_subtask_{i}",
                            "type": "hierarchical",
                            "level": level_idx,
                            "description": level_subtask.get("description"),
                            "inputs": level_subtask.get("inputs", []),
                            "outputs": level_subtask.get("outputs", []),
                            "dependencies": level_subtask.get("dependencies", []),
                            "required_capabilities": level_subtask.get("required_capabilities", []),
                            "priority": level_subtask.get("priority", "medium")
                        }
                        subtasks.append(subtask)
            
            # Add integration subtask if needed
            if len(subtasks) > 1:
                integration_subtask = {
                    "subtask_id": f"{problem_id}_integration",
                    "type": "integration",
                    "description": "Integrate solutions from all subtasks",
                    "inputs": [subtask["subtask_id"] for subtask in subtasks],
                    "outputs": ["integrated_solution"],
                    "dependencies": [subtask["subtask_id"] for subtask in subtasks],
                    "required_capabilities": ["solution_integration", "verification"],
                    "priority": "high"
                }
                subtasks.append(integration_subtask)
            
            # Create dependency graph
            dependency_graph = self._create_dependency_graph(subtasks)
            
            # Return decomposition result
            return {
                "status": "success",
                "problem_id": problem_id,
                "subtasks": subtasks,
                "dependency_graph": dependency_graph,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error decomposing problem: {e}")
            return {
                "status": "error",
                "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def form_problem_solving_team(self,
                                 problem_spec: Dict[str, Any],
                                 decomposition_result: Dict[str, Any],
                                 available_agents: List[str] = None) -> Dict[str, Any]:
        """
        Form a team of agents for collaborative problem solving.
        
        Args:
            problem_spec: Specification of the problem to solve
            decomposition_result: Result of problem decomposition
            available_agents: List of available agent IDs (if None, all agents are considered)
            
        Returns:
            result: Team formation result
        """
        try:
            # Extract problem details
            problem_id = problem_spec.get("problem_id", str(uuid.uuid4()))
            
            # Extract subtasks and their required capabilities
            subtasks = decomposition_result.get("subtasks", [])
            
            if not subtasks:
                return {
                    "status": "error",
                    "problem_id": problem_id,
                    "message": "No subtasks found in decomposition result",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Collect all required capabilities
            all_capabilities = set()
            for subtask in subtasks:
                capabilities = subtask.get("required_capabilities", [])
                all_capabilities.update(capabilities)
            
            # Create team formation request
            formation_request = {
                "task_type": "problem_solving",
                "required_capabilities": list(all_capabilities),
                "team_size": min(len(subtasks) + 1, len(available_agents or [])),
                "available_agents": available_agents,
                "task_metadata": {
                    "problem_id": problem_id,
                    "problem_type": problem_spec.get("problem_type", "unknown"),
                    "domain": problem_spec.get("domain", "general"),
                    "priority": problem_spec.get("priority", "medium")
                }
            }
            
            # Call team formation API
            response = requests.post(
                f"{self.config.collaboration_system_api_url}/teams/form",
                json=formation_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error forming problem solving team: {response.status_code} {response.text}")
                return {
                    "status": "error",
                    "problem_id": problem_id,
                    "message": f"Error forming team: {response.text}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            team_result = response.json()
            
            # Create agent-subtask assignments
            assignments = self._assign_subtasks_to_agents(
                subtasks, 
                team_result.get("members", []),
                team_result.get("capabilities_coverage", {})
            )
            
            # Log the team formation
            logger.info(f"Formed problem solving team: {team_result.get('team_id')} with {len(team_result.get('members', []))} members")
            
            # Return team formation result
            return {
                "status": "success",
                "problem_id": problem_id,
                "team_id": team_result.get("team_id"),
                "members": team_result.get("members", []),
                "capabilities_coverage": team_result.get("capabilities_coverage", {}),
                "assignments": assignments,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error forming problem solving team: {e}")
            return {
                "status": "error",
                "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def create_problem_solving_context(self,
                                     problem_spec: Dict[str, Any],
                                     team_result: Dict[str, Any],
                                     decomposition_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a shared context for collaborative problem solving.
        
        Args:
            problem_spec: Specification of the problem to solve
            team_result: Result of team formation
            decomposition_result: Result of problem decomposition
            
        Returns:
            result: Context creation result
        """
        try:
            # Extract details
            problem_id = problem_spec.get("problem_id", str(uuid.uuid4()))
            team_id = team_result.get("team_id")
            
            if not team_id:
                return {
                    "status": "error",
                    "problem_id": problem_id,
                    "message": "No team ID found in team formation result",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Create initial context data
            initial_data = {
                "problem": problem_spec,
                "decomposition": decomposition_result,
                "team": team_result,
                "status": "initialized",
                "progress": {
                    "completed_subtasks": 0,
                    "total_subtasks": len(decomposition_result.get("subtasks", [])),
                    "status_by_subtask": {}
                },
                "solutions": {},
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Create context request
            context_request = {
                "team_id": team_id,
                "context_type": "problem_solving",
                "task_id": problem_id,
                "metadata": {
                    "problem_id": problem_id,
                    "problem_type": problem_spec.get("problem_type", "unknown"),
                    "domain": problem_spec.get("domain", "general"),
                    "created_at": datetime.datetime.now().isoformat()
                },
                "initial_data": initial_data
            }
            
            # Call context manager API
            response = requests.post(
                f"{self.config.collaboration_system_api_url}/contexts",
                json=context_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error creating problem solving context: {response.status_code} {response.text}")
                return {
                    "status": "error",
                    "problem_id": problem_id,
                    "message": f"Error creating context: {response.text}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            context_result = response.json()
            
            # Log the context creation
            logger.info(f"Created problem solving context: {context_result.get('context_id')} for team {team_id}")
            
            # Return context creation result
            return {
                "status": "success",
                "problem_id": problem_id,
                "team_id": team_id,
                "context_id": context_result.get("context_id"),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating problem solving context: {e}")
            return {
                "status": "error",
                "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def coordinate_problem_solving(self,
                                 problem_spec: Dict[str, Any],
                                 team_result: Dict[str, Any],
                                 context_result: Dict[str, Any],
                                 decomposition_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate the collaborative problem solving process.
        
        Args:
            problem_spec: Specification of the problem to solve
            team_result: Result of team formation
            context_result: Result of context creation
            decomposition_result: Result of problem decomposition
            
        Returns:
            result: Problem solving result
        """
        try:
            # Extract details
            problem_id = problem_spec.get("problem_id", str(uuid.uuid4()))
            team_id = team_result.get("team_id")
            context_id = context_result.get("context_id")
            subtasks = decomposition_result.get("subtasks", [])
            assignments = team_result.get("assignments", {})
            
            if not team_id or not context_id:
                return {
                    "status": "error",
                    "problem_id": problem_id,
                    "message": "Missing team ID or context ID",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Initialize solving session
            session_id = str(uuid.uuid4())
            
            # Update context with session start
            self._update_problem_context(context_id, {
                "solving_session": {
                    "session_id": session_id,
                    "status": "started",
                    "start_time": datetime.datetime.now().isoformat()
                }
            })
            
            # Distribute knowledge and resources to team members
            self._distribute_knowledge_to_team(team_id, problem_spec, decomposition_result)
            
            # Create execution plan based on dependency graph
            execution_plan = self._create_execution_plan(
                subtasks, 
                decomposition_result.get("dependency_graph", {})
            )
            
            # Update context with execution plan
            self._update_problem_context(context_id, {
                "solving_session": {
                    "session_id": session_id,
                    "execution_plan": execution_plan,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            })
            
            # Execute subtasks according to plan
            subtask_results = {}
            
            for phase_idx, phase in enumerate(execution_plan):
                # Update context with phase start
                self._update_problem_context(context_id, {
                    "solving_session": {
                        "session_id": session_id,
                        "status": f"executing_phase_{phase_idx}",
                        "current_phase": phase_idx,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                })
                
                # Execute all subtasks in this phase (can be done in parallel)
                phase_results = {}
                
                for subtask_id in phase:
                    # Find subtask details
                    subtask = next((s for s in subtasks if s["subtask_id"] == subtask_id), None)
                    
                    if not subtask:
                        logger.warning(f"Subtask {subtask_id} not found in decomposition result")
                        continue
                    
                    # Find assigned agent
                    agent_id = None
                    for a_id, assigned_subtasks in assignments.items():
                        if subtask_id in assigned_subtasks:
                            agent_id = a_id
                            break
                    
                    if not agent_id:
                        logger.warning(f"No agent assigned to subtask {subtask_id}")
                        continue
                    
                    # Prepare subtask inputs
                    subtask_inputs = {}
                    
                    for dependency in subtask.get("dependencies", []):
                        if dependency in subtask_results:
                            subtask_inputs[dependency] = subtask_results[dependency].get("outputs", {})
                    
                    # Execute subtask
                    subtask_result = self._execute_subtask(
                        agent_id,
                        team_id,
                        context_id,
                        subtask,
                        subtask_inputs,
                        problem_spec
                    )
                    
                    # Store result
                    phase_results[subtask_id] = subtask_result
                    subtask_results[subtask_id] = subtask_result
                    
                    # Update context with subtask completion
                    self._update_problem_context(context_id, {
                        "progress": {
                            "status_by_subtask": {
                                subtask_id: {
                                    "status": "completed",
                                    "agent_id": agent_id,
                                    "timestamp": datetime.datetime.now().isoformat()
                                }
                            }
                        }
                    })
                
                # Update context with phase completion
                self._update_problem_context(context_id, {
                    "solving_session": {
                        "session_id": session_id,
                        "status": f"completed_phase_{phase_idx}",
                        "phase_results": phase_results,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                })
            
            # Check if we have an integration subtask
            integration_subtask = next((s for s in subtasks if s["type"] == "integration"), None)
            
            final_solution = None
            
            if integration_subtask:
                # Find assigned agent
                agent_id = None
                for a_id, assigned_subtasks in assignments.items():
                    if integration_subtask["subtask_id"] in assigned_subtasks:
                        agent_id = a_id
                        break
                
                if agent_id:
                    # Prepare integration inputs
                    integration_inputs = {}
                    
                    for dependency in integration_subtask.get("dependencies", []):
                        if dependency in subtask_results:
                            integration_inputs[dependency] = subtask_results[dependency].get("outputs", {})
                    
                    # Execute integration subtask
                    integration_result = self._execute_subtask(
                        agent_id,
                        team_id,
                        context_id,
                        integration_subtask,
                        integration_inputs,
                        problem_spec
                    )
                    
                    # Store result
                    subtask_results[integration_subtask["subtask_id"]] = integration_result
                    final_solution = integration_result.get("outputs", {}).get("integrated_solution")
                    
                    # Update context with integration completion
                    self._update_problem_context(context_id, {
                        "progress": {
                            "status_by_subtask": {
                                integration_subtask["subtask_id"]: {
                                    "status": "completed",
                                    "agent_id": agent_id,
                                    "timestamp": datetime.datetime.now().isoformat()
                                }
                            }
                        }
                    })
            else:
                # If no integration subtask, use the result of the last subtask
                last_subtask_id = subtasks[-1]["subtask_id"]
                if last_subtask_id in subtask_results:
                    final_solution = subtask_results[last_subtask_id].get("outputs", {})
            
            # Verify solution if enabled
            verification_result = None
            
            if self.config.solution_verification and final_solution:
                verification_result = self._verify_solution(
                    problem_spec,
                    final_solution,
                    team_id,
                    context_id
                )
                
                # Update context with verification result
                self._update_problem_context(context_id, {
                    "solving_session": {
                        "session_id": session_id,
                        "verification_result": verification_result,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                })
            
            # Learn from solution if enabled
            if self.config.learn_from_solutions and final_solution:
                self._learn_from_solution(
                    problem_spec,
                    final_solution,
                    verification_result,
                    team_id,
                    context_id
                )
            
            # Update context with session completion
            self._update_problem_context(context_id, {
                "solving_session": {
                    "session_id": session_id,
                    "status": "completed",
                    "end_time": datetime.datetime.now().isoformat()
                },
                "status": "completed",
                "solutions": {
                    "final_solution": final_solution,
                    "verification_result": verification_result,
                    "subtask_results": subtask_results
                }
            })
            
            # Update metrics
            self.metrics["problems_solved"] += 1
            
            if verification_result and verification_result.get("is_valid", False):
                self.metrics["solution_success_rate"] = (
                    (self.metrics["solution_success_rate"] * (self.metrics["problems_solved"] - 1) + 1) / 
                    self.metrics["problems_solved"]
                )
            else:
                self.metrics["solution_success_rate"] = (
                    (self.metrics["solution_success_rate"] * (self.metrics["problems_solved"] - 1)) / 
                    self.metrics["problems_solved"]
                )
            
            self.metrics["last_activity_timestamp"] = datetime.datetime.now().isoformat()
            
            # Return final result
            return {
                "status": "success",
                "problem_id": problem_id,
                "team_id": team_id,
                "context_id": context_id,
                "session_id": session_id,
                "solution": final_solution,
                "verification_result": verification_result,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error coordinating problem solving: {e}")
            return {
                "status": "error",
                "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def solve_problem(self, problem_spec: Dict[str, Any], available_agents: List[str] = None) -> Dict[str, Any]:
        """
        Solve a problem using collaborative problem solving.
        
        This is a high-level method that combines all the steps of the problem solving process.
        
        Args:
            problem_spec: Specification of the problem to solve
            available_agents: List of available agent IDs (if None, all agents are considered)
            
        Returns:
            result: Problem solving result
        """
        try:
            # Step 1: Analyze problem
            analysis_result = self.analyze_problem(problem_spec)
            
            if analysis_result.get("status") == "error":
                return analysis_result
            
            # Check if problem is suitable for collaborative solving
            if not analysis_result.get("is_collaborative", False):
                return {
                    "status": "warning",
                    "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                    "message": "Problem is not suitable for collaborative solving",
                    "recommendation": "single_agent_solving",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Step 2: Decompose problem
            decomposition_result = self.decompose_problem(problem_spec, analysis_result)
            
            if decomposition_result.get("status") == "error":
                return decomposition_result
            
            # Step 3: Form problem solving team
            team_result = self.form_problem_solving_team(
                problem_spec,
                decomposition_result,
                available_agents
            )
            
            if team_result.get("status") == "error":
                return team_result
            
            # Step 4: Create problem solving context
            context_result = self.create_problem_solving_context(
                problem_spec,
                team_result,
                decomposition_result
            )
            
            if context_result.get("status") == "error":
                return context_result
            
            # Step 5: Coordinate problem solving
            solving_result = self.coordinate_problem_solving(
                problem_spec,
                team_result,
                context_result,
                decomposition_result
            )
            
            return solving_result
            
        except Exception as e:
            logger.error(f"Error solving problem: {e}")
            return {
                "status": "error",
                "problem_id": problem_spec.get("problem_id", str(uuid.uuid4())),
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def get_problem_solving_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for problem solving.
        
        Returns:
            metrics: Problem solving metrics
        """
        return {
            **self.metrics,
            "current_timestamp": datetime.datetime.now().isoformat()
        }
    
    def _is_collaborative_problem(self, problem_spec: Dict[str, Any]) -> bool:
        """
        Determine if a problem is suitable for collaborative solving.
        
        Args:
            problem_spec: Specification of the problem
            
        Returns:
            is_collaborative: Whether the problem is suitable for collaborative solving
        """
        # Check complexity indicators
        complexity_indicators = [
            len(problem_spec.get("constraints", [])) > 2,
            len(problem_spec.get("requirements", [])) > 3,
            problem_spec.get("complexity", "low") in ["medium", "high"],
            len(problem_spec.get("domains", [])) > 1,
            problem_spec.get("estimated_time", 0) > 60  # minutes
        ]
        
        # Count how many indicators suggest complexity
        complexity_score = sum(1 for indicator in complexity_indicators if indicator)
        
        # Problem is collaborative if majority of indicators suggest complexity
        return complexity_score >= len(complexity_indicators) / 2
    
    def _identify_required_capabilities(self, problem_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify capabilities required to solve a problem.
        
        Args:
            problem_spec: Specification of the problem
            
        Returns:
            capabilities: List of required capabilities
        """
        # Extract relevant information
        problem_type = problem_spec.get("problem_type", "unknown")
        domains = problem_spec.get("domains", [])
        
        # Initialize capabilities list
        capabilities = []
        
        # Add capabilities based on problem type
        if problem_type == "classification":
            capabilities.append({
                "name": "classification",
                "importance": "high",
                "description": "Ability to classify data into categories"
            })
        elif problem_type == "regression":
            capabilities.append({
                "name": "regression",
                "importance": "high",
                "description": "Ability to predict continuous values"
            })
        elif problem_type == "clustering":
            capabilities.append({
                "name": "clustering",
                "importance": "high",
                "description": "Ability to group similar data points"
            })
        elif problem_type == "optimization":
            capabilities.append({
                "name": "optimization",
                "importance": "high",
                "description": "Ability to find optimal solutions"
            })
        elif problem_type == "recommendation":
            capabilities.append({
                "name": "recommendation",
                "importance": "high",
                "description": "Ability to recommend items or actions"
            })
        elif problem_type == "natural_language":
            capabilities.append({
                "name": "natural_language_processing",
                "importance": "high",
                "description": "Ability to process and understand natural language"
            })
        elif problem_type == "computer_vision":
            capabilities.append({
                "name": "computer_vision",
                "importance": "high",
                "description": "Ability to process and understand visual data"
            })
        
        # Add capabilities based on domains
        for domain in domains:
            capabilities.append({
                "name": f"domain_{domain}",
                "importance": "medium",
                "description": f"Knowledge of {domain} domain"
            })
        
        # Add general capabilities
        capabilities.extend([
            {
                "name": "data_analysis",
                "importance": "medium",
                "description": "Ability to analyze and interpret data"
            },
            {
                "name": "problem_decomposition",
                "importance": "medium",
                "description": "Ability to break down complex problems"
            },
            {
                "name": "solution_integration",
                "importance": "medium",
                "description": "Ability to integrate partial solutions"
            },
            {
                "name": "verification",
                "importance": "medium",
                "description": "Ability to verify solutions"
            }
        ])
        
        return capabilities
    
    def _determine_decomposition_approach(self, problem_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine the approach for decomposing a problem.
        
        Args:
            problem_spec: Specification of the problem
            
        Returns:
            approach: Decomposition approach
        """
        # Extract relevant information
        problem_type = problem_spec.get("problem_type", "unknown")
        domains = problem_spec.get("domains", [])
        
        # Initialize approach
        approach = {
            "type": "functional",  # default
            "functions": []
        }
        
        # Determine approach type based on problem characteristics
        if len(domains) > 1:
            # Multiple domains suggest domain decomposition
            approach["type"] = "domain"
            approach["domains"] = []
            
            for domain in domains:
                approach["domains"].append({
                    "name": domain,
                    "description": f"Solve aspects related to {domain}",
                    "inputs": [],
                    "outputs": [],
                    "dependencies": [],
                    "required_capabilities": [f"domain_{domain}"]
                })
                
        elif problem_type in ["classification", "regression", "clustering"] and problem_spec.get("data_size", 0) > 1000:
            # Large data problems suggest data decomposition
            approach["type"] = "data"
            approach["partitions"] = []
            
            # Create partitions (example: by feature groups)
            feature_groups = problem_spec.get("feature_groups", ["group1", "group2"])
            
            for group in feature_groups:
                approach["partitions"].append({
                    "name": group,
                    "description": f"Process features in {group}",
                    "filter": f"features.group == '{group}'",
                    "inputs": [],
                    "outputs": [],
                    "dependencies": [],
                    "required_capabilities": ["data_analysis"]
                })
                
        elif problem_spec.get("complexity", "low") == "high":
            # High complexity suggests hierarchical decomposition
            approach["type"] = "hierarchical"
            approach["levels"] = []
            
            # Create levels (example: 3 levels)
            for i in range(3):
                level_subtasks = []
                
                # Create subtasks for this level
                for j in range(2):  # 2 subtasks per level
                    level_subtasks.append({
                        "description": f"Level {i} subtask {j}",
                        "inputs": [],
                        "outputs": [],
                        "dependencies": [],
                        "required_capabilities": []
                    })
                
                approach["levels"].append({
                    "level": i,
                    "subtasks": level_subtasks
                })
                
        else:
            # Default to functional decomposition
            # Create functions based on problem type
            if problem_type == "classification":
                approach["functions"] = [
                    {
                        "name": "data_preprocessing",
                        "description": "Preprocess and clean data",
                        "inputs": ["raw_data"],
                        "outputs": ["preprocessed_data"],
                        "dependencies": [],
                        "required_capabilities": ["data_analysis"]
                    },
                    {
                        "name": "feature_engineering",
                        "description": "Engineer features for classification",
                        "inputs": ["preprocessed_data"],
                        "outputs": ["engineered_features"],
                        "dependencies": ["data_preprocessing"],
                        "required_capabilities": ["feature_engineering"]
                    },
                    {
                        "name": "model_training",
                        "description": "Train classification model",
                        "inputs": ["engineered_features"],
                        "outputs": ["trained_model"],
                        "dependencies": ["feature_engineering"],
                        "required_capabilities": ["classification"]
                    },
                    {
                        "name": "model_evaluation",
                        "description": "Evaluate classification model",
                        "inputs": ["trained_model", "engineered_features"],
                        "outputs": ["evaluation_results"],
                        "dependencies": ["model_training"],
                        "required_capabilities": ["model_evaluation"]
                    }
                ]
            elif problem_type == "optimization":
                approach["functions"] = [
                    {
                        "name": "problem_formulation",
                        "description": "Formulate optimization problem",
                        "inputs": ["problem_description"],
                        "outputs": ["formulated_problem"],
                        "dependencies": [],
                        "required_capabilities": ["optimization"]
                    },
                    {
                        "name": "constraint_analysis",
                        "description": "Analyze constraints",
                        "inputs": ["formulated_problem"],
                        "outputs": ["analyzed_constraints"],
                        "dependencies": ["problem_formulation"],
                        "required_capabilities": ["constraint_analysis"]
                    },
                    {
                        "name": "algorithm_selection",
                        "description": "Select optimization algorithm",
                        "inputs": ["formulated_problem", "analyzed_constraints"],
                        "outputs": ["selected_algorithm"],
                        "dependencies": ["constraint_analysis"],
                        "required_capabilities": ["algorithm_selection"]
                    },
                    {
                        "name": "solution_computation",
                        "description": "Compute optimal solution",
                        "inputs": ["formulated_problem", "selected_algorithm"],
                        "outputs": ["computed_solution"],
                        "dependencies": ["algorithm_selection"],
                        "required_capabilities": ["optimization"]
                    }
                ]
            else:
                # Generic functional decomposition
                approach["functions"] = [
                    {
                        "name": "problem_analysis",
                        "description": "Analyze problem requirements",
                        "inputs": ["problem_description"],
                        "outputs": ["analyzed_problem"],
                        "dependencies": [],
                        "required_capabilities": ["problem_analysis"]
                    },
                    {
                        "name": "solution_design",
                        "description": "Design solution approach",
                        "inputs": ["analyzed_problem"],
                        "outputs": ["solution_design"],
                        "dependencies": ["problem_analysis"],
                        "required_capabilities": ["solution_design"]
                    },
                    {
                        "name": "solution_implementation",
                        "description": "Implement designed solution",
                        "inputs": ["solution_design"],
                        "outputs": ["implemented_solution"],
                        "dependencies": ["solution_design"],
                        "required_capabilities": ["implementation"]
                    },
                    {
                        "name": "solution_testing",
                        "description": "Test implemented solution",
                        "inputs": ["implemented_solution"],
                        "outputs": ["tested_solution"],
                        "dependencies": ["solution_implementation"],
                        "required_capabilities": ["testing"]
                    }
                ]
        
        return approach
    
    def _estimate_resource_requirements(self, problem_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate resources required to solve a problem.
        
        Args:
            problem_spec: Specification of the problem
            
        Returns:
            requirements: Resource requirements
        """
        # Extract relevant information
        complexity = problem_spec.get("complexity", "low")
        data_size = problem_spec.get("data_size", 0)
        
        # Initialize requirements
        requirements = {
            "computation": "low",
            "memory": "low",
            "time": "low",
            "agents": 2
        }
        
        # Adjust based on complexity
        if complexity == "medium":
            requirements["computation"] = "medium"
            requirements["memory"] = "medium"
            requirements["time"] = "medium"
            requirements["agents"] = 3
        elif complexity == "high":
            requirements["computation"] = "high"
            requirements["memory"] = "high"
            requirements["time"] = "high"
            requirements["agents"] = 5
        
        # Adjust based on data size
        if data_size > 1000:
            requirements["memory"] = "medium"
        if data_size > 10000:
            requirements["memory"] = "high"
            requirements["computation"] = "high"
        
        # Add specific estimates
        requirements["estimated_time_minutes"] = {
            "low": 30,
            "medium": 120,
            "high": 360
        }[requirements["time"]]
        
        requirements["estimated_memory_mb"] = {
            "low": 512,
            "medium": 2048,
            "high": 8192
        }[requirements["memory"]]
        
        return requirements
    
    def _identify_relevant_knowledge(self, problem_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify knowledge relevant to solving a problem.
        
        Args:
            problem_spec: Specification of the problem
            
        Returns:
            knowledge: List of relevant knowledge items
        """
        # Extract relevant information
        problem_type = problem_spec.get("problem_type", "unknown")
        domains = problem_spec.get("domains", [])
        
        # Initialize knowledge list
        knowledge = []
        
        # Add knowledge based on problem type
        if problem_type == "classification":
            knowledge.append({
                "type": "model",
                "name": "classification_models",
                "description": "Models for classification tasks",
                "relevance": "high"
            })
        elif problem_type == "regression":
            knowledge.append({
                "type": "model",
                "name": "regression_models",
                "description": "Models for regression tasks",
                "relevance": "high"
            })
        elif problem_type == "clustering":
            knowledge.append({
                "type": "model",
                "name": "clustering_models",
                "description": "Models for clustering tasks",
                "relevance": "high"
            })
        elif problem_type == "optimization":
            knowledge.append({
                "type": "algorithm",
                "name": "optimization_algorithms",
                "description": "Algorithms for optimization problems",
                "relevance": "high"
            })
        
        # Add knowledge based on domains
        for domain in domains:
            knowledge.append({
                "type": "domain",
                "name": f"{domain}_knowledge",
                "description": f"Knowledge about {domain}",
                "relevance": "medium"
            })
        
        # Add general knowledge
        knowledge.append({
            "type": "methodology",
            "name": "problem_solving_methodology",
            "description": "Methodologies for solving complex problems",
            "relevance": "medium"
        })
        
        return knowledge
    
    def _determine_verification_approach(self, problem_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine the approach for verifying a solution.
        
        Args:
            problem_spec: Specification of the problem
            
        Returns:
            approach: Verification approach
        """
        # Extract relevant information
        problem_type = problem_spec.get("problem_type", "unknown")
        
        # Initialize approach
        approach = {
            "method": "testing",
            "metrics": [],
            "thresholds": {}
        }
        
        # Determine verification method based on problem type
        if problem_type == "classification":
            approach["method"] = "performance_metrics"
            approach["metrics"] = ["accuracy", "precision", "recall", "f1"]
            approach["thresholds"] = {
                "accuracy": 0.8,
                "precision": 0.8,
                "recall": 0.8,
                "f1": 0.8
            }
        elif problem_type == "regression":
            approach["method"] = "performance_metrics"
            approach["metrics"] = ["mse", "mae", "r2"]
            approach["thresholds"] = {
                "mse": 0.2,
                "mae": 0.3,
                "r2": 0.7
            }
        elif problem_type == "clustering":
            approach["method"] = "performance_metrics"
            approach["metrics"] = ["silhouette", "davies_bouldin", "calinski_harabasz"]
            approach["thresholds"] = {
                "silhouette": 0.6,
                "davies_bouldin": 0.5,
                "calinski_harabasz": 10
            }
        elif problem_type == "optimization":
            approach["method"] = "constraint_satisfaction"
            approach["metrics"] = ["objective_value", "constraint_violation"]
            approach["thresholds"] = {
                "constraint_violation": 0.001
            }
        else:
            # Default to testing
            approach["method"] = "testing"
            approach["metrics"] = ["test_coverage", "test_success_rate"]
            approach["thresholds"] = {
                "test_coverage": 0.9,
                "test_success_rate": 0.95
            }
        
        return approach
    
    def _determine_solving_approach(self, problem_spec: Dict[str, Any], required_capabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Determine the overall approach for solving a problem.
        
        Args:
            problem_spec: Specification of the problem
            required_capabilities: List of required capabilities
            
        Returns:
            approach: Solving approach
        """
        # Extract relevant information
        problem_type = problem_spec.get("problem_type", "unknown")
        complexity = problem_spec.get("complexity", "low")
        
        # Initialize approach
        approach = {
            "strategy": "divide_and_conquer",
            "coordination": "centralized",
            "learning_integration": "federated"
        }
        
        # Determine strategy based on problem type and complexity
        if complexity == "high":
            approach["strategy"] = "divide_and_conquer"
        elif problem_type in ["classification", "regression", "clustering"]:
            approach["strategy"] = "model_ensemble"
        elif problem_type == "optimization":
            approach["strategy"] = "constraint_decomposition"
        else:
            approach["strategy"] = "functional_decomposition"
        
        # Determine coordination approach
        if len(required_capabilities) > 5:
            approach["coordination"] = "hierarchical"
        else:
            approach["coordination"] = "centralized"
        
        # Determine learning integration approach
        if problem_type in ["classification", "regression", "clustering"]:
            approach["learning_integration"] = "federated"
        else:
            approach["learning_integration"] = "knowledge_sharing"
        
        return approach
    
    def _create_dependency_graph(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Create a dependency graph for subtasks.
        
        Args:
            subtasks: List of subtasks
            
        Returns:
            graph: Dependency graph
        """
        # Initialize graph
        graph = {}
        
        # Create nodes for all subtasks
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            graph[subtask_id] = []
        
        # Add edges based on dependencies
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            dependencies = subtask.get("dependencies", [])
            
            for dependency in dependencies:
                if dependency in graph:
                    graph[dependency].append(subtask_id)
        
        return graph
    
    def _assign_subtasks_to_agents(self, 
                                 subtasks: List[Dict[str, Any]], 
                                 agents: List[str],
                                 capabilities_coverage: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Assign subtasks to agents based on capabilities.
        
        Args:
            subtasks: List of subtasks
            agents: List of agent IDs
            capabilities_coverage: Map of capabilities to agents
            
        Returns:
            assignments: Map of agent IDs to assigned subtask IDs
        """
        # Initialize assignments
        assignments = {agent_id: [] for agent_id in agents}
        
        # Track assigned subtasks
        assigned_subtasks = set()
        
        # First pass: assign based on capabilities
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            required_capabilities = subtask.get("required_capabilities", [])
            
            # Find best agent for this subtask
            best_agent = None
            best_score = -1
            
            for agent_id in agents:
                # Skip agents with too many subtasks
                if len(assignments[agent_id]) >= self.config.max_subtasks_per_agent:
                    continue
                
                # Calculate capability match score
                score = 0
                for capability in required_capabilities:
                    if capability in capabilities_coverage and agent_id in capabilities_coverage[capability]:
                        score += 1
                
                # Adjust score based on current workload
                score = score / (1 + len(assignments[agent_id]))
                
                if score > best_score:
                    best_score = score
                    best_agent = agent_id
            
            # Assign subtask to best agent
            if best_agent:
                assignments[best_agent].append(subtask_id)
                assigned_subtasks.add(subtask_id)
        
        # Second pass: assign remaining subtasks
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            
            if subtask_id not in assigned_subtasks:
                # Find agent with fewest assignments
                best_agent = min(agents, key=lambda a: len(assignments[a]))
                
                # Assign subtask
                assignments[best_agent].append(subtask_id)
                assigned_subtasks.add(subtask_id)
        
        return assignments
    
    def _distribute_knowledge_to_team(self, 
                                    team_id: str, 
                                    problem_spec: Dict[str, Any],
                                    decomposition_result: Dict[str, Any]) -> bool:
        """
        Distribute relevant knowledge to team members.
        
        Args:
            team_id: ID of the team
            problem_spec: Specification of the problem
            decomposition_result: Result of problem decomposition
            
        Returns:
            success: Whether knowledge distribution was successful
        """
        try:
            # Identify relevant knowledge
            relevant_knowledge = self._identify_relevant_knowledge(problem_spec)
            
            # Get team members
            team_response = requests.get(
                f"{self.config.collaboration_system_api_url}/teams/{team_id}",
                headers={"Content-Type": "application/json"}
            )
            
            if team_response.status_code != 200:
                logger.error(f"Error getting team: {team_response.status_code} {team_response.text}")
                return False
            
            team_data = team_response.json()
            members = team_data.get("members", [])
            
            if not members:
                logger.error(f"No members found for team {team_id}")
                return False
            
            # Distribute knowledge to all team members
            for knowledge_item in relevant_knowledge:
                # Create knowledge item in shared memory
                knowledge_request = {
                    "type": knowledge_item["type"],
                    "name": knowledge_item["name"],
                    "description": knowledge_item["description"],
                    "content": {
                        "relevance": knowledge_item["relevance"],
                        "problem_id": problem_spec.get("problem_id"),
                        "created_at": datetime.datetime.now().isoformat()
                    },
                    "metadata": {
                        "source": "problem_solving",
                        "problem_id": problem_spec.get("problem_id")
                    }
                }
                
                # Call knowledge API to create item
                knowledge_response = requests.post(
                    f"{self.config.learning_system_api_url}/knowledge/items",
                    json=knowledge_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if knowledge_response.status_code != 200:
                    logger.warning(f"Error creating knowledge item: {knowledge_response.status_code} {knowledge_response.text}")
                    continue
                
                knowledge_result = knowledge_response.json()
                knowledge_id = knowledge_result.get("item_id")
                
                # Broadcast knowledge to team
                self.knowledge_transfer.broadcast_knowledge_to_team(
                    knowledge_id,
                    members[0],  # Use first member as source
                    team_id,
                    {
                        "read": ["team_member"],
                        "write": ["team_admin"],
                        "delete": ["team_admin"],
                        "share": ["team_member"]
                    }
                )
            
            # Update metrics
            self.metrics["knowledge_items_created"] += len(relevant_knowledge)
            
            return True
            
        except Exception as e:
            logger.error(f"Error distributing knowledge to team: {e}")
            return False
    
    def _create_execution_plan(self, 
                             subtasks: List[Dict[str, Any]], 
                             dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Create an execution plan for subtasks based on dependencies.
        
        Args:
            subtasks: List of subtasks
            dependency_graph: Dependency graph
            
        Returns:
            plan: Execution plan as list of phases, each containing subtask IDs
        """
        # Create reverse dependency graph
        reverse_graph = {}
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            reverse_graph[subtask_id] = []
        
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            dependencies = subtask.get("dependencies", [])
            
            for dependency in dependencies:
                if dependency in reverse_graph:
                    reverse_graph[dependency].append(subtask_id)
        
        # Calculate in-degree for each subtask
        in_degree = {}
        for subtask in subtasks:
            subtask_id = subtask["subtask_id"]
            in_degree[subtask_id] = len(subtask.get("dependencies", []))
        
        # Create execution plan
        plan = []
        remaining = set(s["subtask_id"] for s in subtasks)
        
        while remaining:
            # Find subtasks with no dependencies
            current_phase = []
            
            for subtask_id in list(remaining):
                if in_degree[subtask_id] == 0:
                    current_phase.append(subtask_id)
                    remaining.remove(subtask_id)
            
            if not current_phase:
                # Circular dependency detected
                logger.warning("Circular dependency detected in subtasks")
                # Break the cycle by selecting a random subtask
                subtask_id = next(iter(remaining))
                current_phase.append(subtask_id)
                remaining.remove(subtask_id)
            
            # Add phase to plan
            plan.append(current_phase)
            
            # Update in-degree for remaining subtasks
            for subtask_id in current_phase:
                for dependent in reverse_graph.get(subtask_id, []):
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
        
        return plan
    
    def _execute_subtask(self,
                       agent_id: str,
                       team_id: str,
                       context_id: str,
                       subtask: Dict[str, Any],
                       inputs: Dict[str, Any],
                       problem_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a subtask using an agent.
        
        Args:
            agent_id: ID of the agent
            team_id: ID of the team
            context_id: ID of the context
            subtask: Subtask specification
            inputs: Inputs for the subtask
            problem_spec: Original problem specification
            
        Returns:
            result: Subtask execution result
        """
        try:
            # Create execution request
            execution_request = {
                "agent_id": agent_id,
                "team_id": team_id,
                "context_id": context_id,
                "subtask_id": subtask["subtask_id"],
                "subtask_type": subtask.get("type", "unknown"),
                "description": subtask.get("description", ""),
                "inputs": inputs,
                "problem_spec": problem_spec,
                "timeout_seconds": self.config.timeout_seconds
            }
            
            # Call agent execution API
            execution_response = requests.post(
                f"{self.config.collaboration_system_api_url}/agents/{agent_id}/execute",
                json=execution_request,
                headers={"Content-Type": "application/json"}
            )
            
            if execution_response.status_code != 200:
                logger.error(f"Error executing subtask: {execution_response.status_code} {execution_response.text}")
                return {
                    "status": "error",
                    "subtask_id": subtask["subtask_id"],
                    "message": f"Error executing subtask: {execution_response.text}",
                    "outputs": {},
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            execution_result = execution_response.json()
            
            # Return execution result
            return {
                "status": execution_result.get("status", "unknown"),
                "subtask_id": subtask["subtask_id"],
                "agent_id": agent_id,
                "outputs": execution_result.get("outputs", {}),
                "metrics": execution_result.get("metrics", {}),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing subtask: {e}")
            return {
                "status": "error",
                "subtask_id": subtask["subtask_id"],
                "message": str(e),
                "outputs": {},
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _verify_solution(self,
                       problem_spec: Dict[str, Any],
                       solution: Dict[str, Any],
                       team_id: str,
                       context_id: str) -> Dict[str, Any]:
        """
        Verify a solution to a problem.
        
        Args:
            problem_spec: Specification of the problem
            solution: Solution to verify
            team_id: ID of the team
            context_id: ID of the context
            
        Returns:
            result: Verification result
        """
        try:
            # Determine verification approach
            verification_approach = self._determine_verification_approach(problem_spec)
            
            # Create verification request
            verification_request = {
                "problem_spec": problem_spec,
                "solution": solution,
                "verification_approach": verification_approach,
                "team_id": team_id,
                "context_id": context_id
            }
            
            # Call verification API
            verification_response = requests.post(
                f"{self.config.learning_system_api_url}/verification/verify",
                json=verification_request,
                headers={"Content-Type": "application/json"}
            )
            
            if verification_response.status_code != 200:
                logger.error(f"Error verifying solution: {verification_response.status_code} {verification_response.text}")
                return {
                    "is_valid": False,
                    "confidence": 0.0,
                    "message": f"Error verifying solution: {verification_response.text}",
                    "metrics": {},
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            verification_result = verification_response.json()
            
            # Return verification result
            return {
                "is_valid": verification_result.get("is_valid", False),
                "confidence": verification_result.get("confidence", 0.0),
                "message": verification_result.get("message", ""),
                "metrics": verification_result.get("metrics", {}),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error verifying solution: {e}")
            return {
                "is_valid": False,
                "confidence": 0.0,
                "message": str(e),
                "metrics": {},
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _learn_from_solution(self,
                          problem_spec: Dict[str, Any],
                          solution: Dict[str, Any],
                          verification_result: Dict[str, Any],
                          team_id: str,
                          context_id: str) -> bool:
        """
        Learn from a solution to improve future problem solving.
        
        Args:
            problem_spec: Specification of the problem
            solution: Solution to learn from
            verification_result: Result of solution verification
            team_id: ID of the team
            context_id: ID of the context
            
        Returns:
            success: Whether learning was successful
        """
        try:
            # Only learn from valid solutions
            if not verification_result or not verification_result.get("is_valid", False):
                return False
            
            # Create learning request
            learning_request = {
                "problem_spec": problem_spec,
                "solution": solution,
                "verification_result": verification_result,
                "team_id": team_id,
                "context_id": context_id,
                "learning_type": "solution_pattern"
            }
            
            # Call learning API
            learning_response = requests.post(
                f"{self.config.learning_system_api_url}/learning/from-solution",
                json=learning_request,
                headers={"Content-Type": "application/json"}
            )
            
            if learning_response.status_code != 200:
                logger.error(f"Error learning from solution: {learning_response.status_code} {learning_response.text}")
                return False
            
            # Create knowledge item for the solution
            knowledge_request = {
                "type": "solution",
                "name": f"solution_{problem_spec.get('problem_id')}",
                "description": f"Solution for {problem_spec.get('problem_type')} problem",
                "content": {
                    "problem": problem_spec,
                    "solution": solution,
                    "verification": verification_result
                },
                "metadata": {
                    "source": "problem_solving",
                    "problem_id": problem_spec.get("problem_id"),
                    "team_id": team_id,
                    "context_id": context_id
                }
            }
            
            # Call knowledge API to create item
            knowledge_response = requests.post(
                f"{self.config.learning_system_api_url}/knowledge/items",
                json=knowledge_request,
                headers={"Content-Type": "application/json"}
            )
            
            if knowledge_response.status_code != 200:
                logger.warning(f"Error creating knowledge item for solution: {knowledge_response.status_code} {knowledge_response.text}")
            else:
                # Update metrics
                self.metrics["knowledge_items_created"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error learning from solution: {e}")
            return False
    
    def _update_problem_context(self, context_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update the problem solving context with new data.
        
        Args:
            context_id: ID of the context to update
            update_data: Data to update in the context
            
        Returns:
            success: Whether the update was successful
        """
        try:
            # Create update request
            update_request = {
                "context_id": context_id,
                "update_data": update_data,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Call context manager API
            response = requests.patch(
                f"{self.config.collaboration_system_api_url}/contexts/{context_id}",
                json=update_request,
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error updating problem context: {e}")
            return False


# REST API for Problem Solving Capabilities

class ProblemSolvingAPI:
    """
    REST API for Problem Solving Capabilities.
    
    This class provides HTTP endpoints for the Problem Solving Capabilities.
    """
    
    def __init__(self, capabilities: ProblemSolvingCapabilities = None):
        """
        Initialize the Problem Solving API.
        
        Args:
            capabilities: Problem Solving Capabilities instance
        """
        self.capabilities = capabilities or ProblemSolvingCapabilities()
        logger.info("Problem Solving API initialized")
    
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
        if base_path == "analyze":
            if method == "POST":
                return self.capabilities.analyze_problem(body)
        elif base_path == "decompose":
            if method == "POST":
                return self.capabilities.decompose_problem(
                    body.get("problem_spec"),
                    body.get("analysis_result")
                )
        elif base_path == "teams":
            if method == "POST" and len(path_parts) > 1 and path_parts[1] == "form":
                return self.capabilities.form_problem_solving_team(
                    body.get("problem_spec"),
                    body.get("decomposition_result"),
                    body.get("available_agents")
                )
        elif base_path == "contexts":
            if method == "POST":
                return self.capabilities.create_problem_solving_context(
                    body.get("problem_spec"),
                    body.get("team_result"),
                    body.get("decomposition_result")
                )
        elif base_path == "coordinate":
            if method == "POST":
                return self.capabilities.coordinate_problem_solving(
                    body.get("problem_spec"),
                    body.get("team_result"),
                    body.get("context_result"),
                    body.get("decomposition_result")
                )
        elif base_path == "solve":
            if method == "POST":
                return self.capabilities.solve_problem(
                    body,
                    body.get("available_agents")
                )
        elif base_path == "metrics":
            if method == "GET":
                return self.capabilities.get_problem_solving_metrics()
        
        # Default response for unknown path
        return {
            "status": "error",
            "message": f"Unknown path: {path}",
            "timestamp": datetime.datetime.now().isoformat()
        }


# Main function for running the API server
def main():
    """Run the Problem Solving API server."""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    api = ProblemSolvingAPI()
    
    @app.route("/api/problem-solving/<path:path>", methods=["GET", "POST", "PATCH", "DELETE"])
    def handle_request(path):
        method = request.method
        params = request.args.to_dict()
        body = request.json if request.is_json else {}
        
        response = api.handle_request(method, path, params, body)
        return jsonify(response)
    
    app.run(host="0.0.0.0", port=8084)


if __name__ == "__main__":
    main()
