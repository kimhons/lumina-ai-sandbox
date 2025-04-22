"""
Collaborative Learning Module for Advanced Multi-Agent Collaboration.

This module implements the Collaborative Learning Module, which enables agents to learn
from each other's experiences and improve their collective performance.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
import uuid
import time
import json
import logging
import copy
import threading
import random
import math
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class LearningEventType(Enum):
    """Enum representing different learning event types."""
    OBSERVATION = "observation"       # Agent observation
    ACTION = "action"                 # Agent action
    FEEDBACK = "feedback"             # Feedback on agent performance
    ERROR = "error"                   # Error encountered by agent
    INSIGHT = "insight"               # Agent insight
    KNOWLEDGE = "knowledge"           # Knowledge acquired by agent
    SKILL = "skill"                   # Skill demonstrated by agent
    INTERACTION = "interaction"       # Interaction between agents


@dataclass
class LearningEvent:
    """Represents a learning event."""
    event_id: str
    event_type: LearningEventType
    agent_id: str
    content: Any
    timestamp: float = field(default_factory=time.time)
    task_id: Optional[str] = None
    team_id: Optional[str] = None
    related_events: List[str] = field(default_factory=list)  # IDs of related events
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningPattern:
    """Represents a pattern identified in learning events."""
    pattern_id: str
    name: str
    description: str
    event_sequence: List[Dict[str, Any]]  # Sequence of event patterns
    confidence: float = 0.5  # 0.0 to 1.0
    frequency: int = 0  # Number of times pattern has been observed
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningInsight:
    """Represents an insight derived from learning events."""
    insight_id: str
    title: str
    description: str
    source_events: List[str]  # IDs of events that led to this insight
    source_patterns: List[str] = field(default_factory=list)  # IDs of patterns that led to this insight
    confidence: float = 0.5  # 0.0 to 1.0
    created_at: float = field(default_factory=time.time)
    created_by: Optional[str] = None  # Agent ID or "system"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillModel:
    """Represents a skill model that can be learned and shared."""
    model_id: str
    name: str
    description: str
    skill_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    created_by: Optional[str] = None  # Agent ID or "system"
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    training_events: List[str] = field(default_factory=list)  # IDs of events used for training
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventStore:
    """Stores and retrieves learning events."""
    
    def __init__(self):
        self.events: Dict[str, LearningEvent] = {}
        self.lock = threading.RLock()
        
    def add_event(self, event: LearningEvent) -> str:
        """
        Add a learning event to the store.
        
        Args:
            event: The learning event to add
            
        Returns:
            The ID of the added event
        """
        with self.lock:
            self.events[event.event_id] = event
            logger.info(f"Added learning event {event.event_id} of type {event.event_type}")
            return event.event_id
    
    def get_event(self, event_id: str) -> Optional[LearningEvent]:
        """Get a learning event by ID."""
        with self.lock:
            return self.events.get(event_id)
    
    def query_events(
        self,
        event_type: Optional[LearningEventType] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        related_to: Optional[str] = None
    ) -> List[LearningEvent]:
        """
        Query learning events based on various criteria.
        
        Args:
            event_type: Filter by event type
            agent_id: Filter by agent ID
            task_id: Filter by task ID
            team_id: Filter by team ID
            start_time: Filter by start time
            end_time: Filter by end time
            related_to: Filter by related event ID
            
        Returns:
            List of matching learning events
        """
        with self.lock:
            results = []
            
            for event in self.events.values():
                # Apply filters
                if event_type and event.event_type != event_type:
                    continue
                    
                if agent_id and event.agent_id != agent_id:
                    continue
                    
                if task_id and event.task_id != task_id:
                    continue
                    
                if team_id and event.team_id != team_id:
                    continue
                    
                if start_time and event.timestamp < start_time:
                    continue
                    
                if end_time and event.timestamp > end_time:
                    continue
                    
                if related_to and related_to not in event.related_events:
                    continue
                    
                results.append(event)
                
            return results
    
    def get_agent_events(
        self,
        agent_id: str,
        limit: int = 100,
        event_types: Optional[List[LearningEventType]] = None
    ) -> List[LearningEvent]:
        """
        Get recent events for a specific agent.
        
        Args:
            agent_id: The ID of the agent
            limit: Maximum number of events to return
            event_types: Optional list of event types to include
            
        Returns:
            List of learning events
        """
        with self.lock:
            # Get all events for the agent
            agent_events = [
                event for event in self.events.values()
                if event.agent_id == agent_id and
                (event_types is None or event.event_type in event_types)
            ]
            
            # Sort by timestamp (newest first)
            agent_events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Return up to the limit
            return agent_events[:limit]
    
    def get_team_events(
        self,
        team_id: str,
        limit: int = 100,
        event_types: Optional[List[LearningEventType]] = None
    ) -> List[LearningEvent]:
        """
        Get recent events for a specific team.
        
        Args:
            team_id: The ID of the team
            limit: Maximum number of events to return
            event_types: Optional list of event types to include
            
        Returns:
            List of learning events
        """
        with self.lock:
            # Get all events for the team
            team_events = [
                event for event in self.events.values()
                if event.team_id == team_id and
                (event_types is None or event.event_type in event_types)
            ]
            
            # Sort by timestamp (newest first)
            team_events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Return up to the limit
            return team_events[:limit]
    
    def get_task_events(
        self,
        task_id: str,
        limit: int = 100,
        event_types: Optional[List[LearningEventType]] = None
    ) -> List[LearningEvent]:
        """
        Get recent events for a specific task.
        
        Args:
            task_id: The ID of the task
            limit: Maximum number of events to return
            event_types: Optional list of event types to include
            
        Returns:
            List of learning events
        """
        with self.lock:
            # Get all events for the task
            task_events = [
                event for event in self.events.values()
                if event.task_id == task_id and
                (event_types is None or event.event_type in event_types)
            ]
            
            # Sort by timestamp (newest first)
            task_events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Return up to the limit
            return task_events[:limit]
    
    def get_event_sequence(
        self,
        event_ids: List[str]
    ) -> List[LearningEvent]:
        """
        Get a sequence of events by their IDs.
        
        Args:
            event_ids: List of event IDs
            
        Returns:
            List of learning events in the same order as the IDs
        """
        with self.lock:
            return [
                self.events.get(event_id)
                for event_id in event_ids
                if event_id in self.events
            ]


class PatternRecognizer:
    """Recognizes patterns in learning events."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.patterns: Dict[str, LearningPattern] = {}
        self.lock = threading.RLock()
        
    def add_pattern(self, pattern: LearningPattern) -> str:
        """
        Add a learning pattern.
        
        Args:
            pattern: The learning pattern to add
            
        Returns:
            The ID of the added pattern
        """
        with self.lock:
            self.patterns[pattern.pattern_id] = pattern
            logger.info(f"Added learning pattern {pattern.pattern_id}: {pattern.name}")
            return pattern.pattern_id
    
    def get_pattern(self, pattern_id: str) -> Optional[LearningPattern]:
        """Get a learning pattern by ID."""
        with self.lock:
            return self.patterns.get(pattern_id)
    
    def update_pattern(
        self,
        pattern_id: str,
        frequency_delta: int = 0,
        confidence_delta: float = 0.0
    ) -> bool:
        """
        Update a learning pattern.
        
        Args:
            pattern_id: The ID of the pattern to update
            frequency_delta: Change in frequency
            confidence_delta: Change in confidence
            
        Returns:
            True if the update was successful, False otherwise
        """
        with self.lock:
            pattern = self.patterns.get(pattern_id)
            if not pattern:
                logger.warning(f"Pattern {pattern_id} not found")
                return False
                
            pattern.frequency += frequency_delta
            pattern.confidence = max(0.0, min(1.0, pattern.confidence + confidence_delta))
            pattern.updated_at = time.time()
            
            logger.info(f"Updated pattern {pattern_id}: frequency={pattern.frequency}, confidence={pattern.confidence}")
            return True
    
    def find_matching_patterns(
        self,
        events: List[LearningEvent],
        min_confidence: float = 0.0
    ) -> List[Tuple[LearningPattern, float]]:
        """
        Find patterns that match a sequence of events.
        
        Args:
            events: The sequence of events to match
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of tuples (pattern, match_score)
        """
        with self.lock:
            results = []
            
            for pattern in self.patterns.values():
                if pattern.confidence < min_confidence:
                    continue
                    
                match_score = self._calculate_match_score(pattern, events)
                if match_score > 0.0:
                    results.append((pattern, match_score))
                    
            # Sort by match score (highest first)
            results.sort(key=lambda x: x[1], reverse=True)
            return results
    
    def detect_patterns(
        self,
        events: List[LearningEvent],
        min_pattern_length: int = 2,
        max_pattern_length: int = 5,
        min_frequency: int = 2
    ) -> List[LearningPattern]:
        """
        Detect new patterns in a sequence of events.
        
        Args:
            events: The sequence of events to analyze
            min_pattern_length: Minimum length of patterns to detect
            max_pattern_length: Maximum length of patterns to detect
            min_frequency: Minimum frequency threshold
            
        Returns:
            List of detected patterns
        """
        with self.lock:
            # Sort events by timestamp
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            
            # Extract event features for pattern matching
            event_features = [self._extract_event_features(event) for event in sorted_events]
            
            # Find repeated subsequences
            patterns = []
            
            for length in range(min_pattern_length, min(max_pattern_length + 1, len(event_features) + 1)):
                subsequences = {}
                
                for i in range(len(event_features) - length + 1):
                    # Create a hashable representation of the subsequence
                    subsequence = tuple(json.dumps(event_features[i + j], sort_keys=True) for j in range(length))
                    
                    if subsequence not in subsequences:
                        subsequences[subsequence] = []
                        
                    subsequences[subsequence].append(i)
                
                # Filter subsequences that appear at least min_frequency times
                for subsequence, occurrences in subsequences.items():
                    if len(occurrences) >= min_frequency:
                        # Create a pattern
                        pattern_id = f"pattern-{uuid.uuid4()}"
                        pattern = LearningPattern(
                            pattern_id=pattern_id,
                            name=f"Pattern of {length} events",
                            description=f"Automatically detected pattern of {length} events",
                            event_sequence=[json.loads(event_json) for event_json in subsequence],
                            confidence=0.5,  # Initial confidence
                            frequency=len(occurrences)
                        )
                        
                        patterns.append(pattern)
            
            return patterns
    
    def _extract_event_features(self, event: LearningEvent) -> Dict[str, Any]:
        """Extract features from an event for pattern matching."""
        return {
            "event_type": event.event_type.value,
            "agent_id": event.agent_id,
            "content_type": type(event.content).__name__,
            "task_id": event.task_id,
            "team_id": event.team_id
        }
    
    def _calculate_match_score(
        self,
        pattern: LearningPattern,
        events: List[LearningEvent]
    ) -> float:
        """
        Calculate how well a pattern matches a sequence of events.
        
        Args:
            pattern: The pattern to match
            events: The sequence of events
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if len(events) < len(pattern.event_sequence):
            return 0.0
            
        max_score = 0.0
        
        # Try matching the pattern at each position in the event sequence
        for i in range(len(events) - len(pattern.event_sequence) + 1):
            score = 0.0
            
            for j in range(len(pattern.event_sequence)):
                event = events[i + j]
                pattern_event = pattern.event_sequence[j]
                
                # Calculate similarity between event and pattern event
                similarity = self._calculate_event_similarity(event, pattern_event)
                score += similarity
                
            # Normalize score
            score /= len(pattern.event_sequence)
            
            # Update max score
            max_score = max(max_score, score)
            
        return max_score
    
    def _calculate_event_similarity(
        self,
        event: LearningEvent,
        pattern_event: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between an event and a pattern event.
        
        Args:
            event: The event
            pattern_event: The pattern event
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        score = 0.0
        total_weight = 0.0
        
        # Check event type
        if "event_type" in pattern_event:
            weight = 0.4
            if event.event_type.value == pattern_event["event_type"]:
                score += weight
            total_weight += weight
            
        # Check agent ID
        if "agent_id" in pattern_event:
            weight = 0.2
            if event.agent_id == pattern_event["agent_id"]:
                score += weight
            total_weight += weight
            
        # Check content type
        if "content_type" in pattern_event:
            weight = 0.1
            if type(event.content).__name__ == pattern_event["content_type"]:
                score += weight
            total_weight += weight
            
        # Check task ID
        if "task_id" in pattern_event:
            weight = 0.15
            if event.task_id == pattern_event["task_id"]:
                score += weight
            total_weight += weight
            
        # Check team ID
        if "team_id" in pattern_event:
            weight = 0.15
            if event.team_id == pattern_event["team_id"]:
                score += weight
            total_weight += weight
            
        # Normalize score
        if total_weight > 0.0:
            return score / total_weight
        else:
            return 0.0


class InsightGenerator:
    """Generates insights from learning events and patterns."""
    
    def __init__(
        self,
        event_store: EventStore,
        pattern_recognizer: PatternRecognizer
    ):
        self.event_store = event_store
        self.pattern_recognizer = pattern_recognizer
        self.insights: Dict[str, LearningInsight] = {}
        self.lock = threading.RLock()
        
    def add_insight(self, insight: LearningInsight) -> str:
        """
        Add a learning insight.
        
        Args:
            insight: The learning insight to add
            
        Returns:
            The ID of the added insight
        """
        with self.lock:
            self.insights[insight.insight_id] = insight
            logger.info(f"Added learning insight {insight.insight_id}: {insight.title}")
            return insight.insight_id
    
    def get_insight(self, insight_id: str) -> Optional[LearningInsight]:
        """Get a learning insight by ID."""
        with self.lock:
            return self.insights.get(insight_id)
    
    def query_insights(
        self,
        tags: Optional[List[str]] = None,
        min_confidence: Optional[float] = None,
        created_by: Optional[str] = None,
        created_after: Optional[float] = None,
        related_to_event: Optional[str] = None,
        related_to_pattern: Optional[str] = None
    ) -> List[LearningInsight]:
        """
        Query learning insights based on various criteria.
        
        Args:
            tags: Filter by tags (insights must have all specified tags)
            min_confidence: Filter by minimum confidence
            created_by: Filter by creator
            created_after: Filter by creation time
            related_to_event: Filter by related event ID
            related_to_pattern: Filter by related pattern ID
            
        Returns:
            List of matching learning insights
        """
        with self.lock:
            results = []
            
            for insight in self.insights.values():
                # Apply filters
                if tags and not all(tag in insight.tags for tag in tags):
                    continue
                    
                if min_confidence is not None and insight.confidence < min_confidence:
                    continue
                    
                if created_by and insight.created_by != created_by:
                    continue
                    
                if created_after and insight.created_at <= created_after:
                    continue
                    
                if related_to_event and related_to_event not in insight.source_events:
                    continue
                    
                if related_to_pattern and related_to_pattern not in insight.source_patterns:
                    continue
                    
                results.append(insight)
                
            return results
    
    def generate_insights_from_events(
        self,
        events: List[LearningEvent],
        min_confidence: float = 0.5
    ) -> List[LearningInsight]:
        """
        Generate insights from a sequence of events.
        
        Args:
            events: The sequence of events to analyze
            min_confidence: Minimum confidence threshold for insights
            
        Returns:
            List of generated insights
        """
        with self.lock:
            insights = []
            
            # Find patterns in the events
            patterns = self.pattern_recognizer.detect_patterns(events)
            
            # Add new patterns
            for pattern in patterns:
                self.pattern_recognizer.add_pattern(pattern)
            
            # Find matching existing patterns
            matching_patterns = self.pattern_recognizer.find_matching_patterns(
                events,
                min_confidence=min_confidence
            )
            
            # Generate insights from patterns
            for pattern, match_score in matching_patterns:
                # Update pattern frequency
                self.pattern_recognizer.update_pattern(
                    pattern_id=pattern.pattern_id,
                    frequency_delta=1
                )
                
                # Generate insight
                insight_id = f"insight-{uuid.uuid4()}"
                insight = LearningInsight(
                    insight_id=insight_id,
                    title=f"Pattern-based insight: {pattern.name}",
                    description=f"Insight based on pattern {pattern.name}: {pattern.description}",
                    source_events=[event.event_id for event in events],
                    source_patterns=[pattern.pattern_id],
                    confidence=match_score * pattern.confidence,
                    created_by="system",
                    tags=["pattern-based", pattern.name]
                )
                
                insights.append(insight)
                self.add_insight(insight)
            
            # Generate insights from event sequences
            if len(events) >= 2:
                # Analyze event sequences for cause-effect relationships
                for i in range(len(events) - 1):
                    for j in range(i + 1, min(i + 3, len(events))):
                        cause_event = events[i]
                        effect_event = events[j]
                        
                        # Check if there's a potential cause-effect relationship
                        if self._check_cause_effect(cause_event, effect_event):
                            # Generate insight
                            insight_id = f"insight-{uuid.uuid4()}"
                            insight = LearningInsight(
                                insight_id=insight_id,
                                title=f"Cause-effect insight",
                                description=f"Potential cause-effect relationship detected between events {cause_event.event_id} and {effect_event.event_id}",
                                source_events=[cause_event.event_id, effect_event.event_id],
                                confidence=0.6,  # Initial confidence
                                created_by="system",
                                tags=["cause-effect"]
                            )
                            
                            insights.append(insight)
                            self.add_insight(insight)
            
            return insights
    
    def generate_insights_from_patterns(
        self,
        min_frequency: int = 3,
        min_confidence: float = 0.7
    ) -> List[LearningInsight]:
        """
        Generate insights from frequently occurring patterns.
        
        Args:
            min_frequency: Minimum pattern frequency
            min_confidence: Minimum pattern confidence
            
        Returns:
            List of generated insights
        """
        with self.lock:
            insights = []
            
            # Find frequent patterns
            frequent_patterns = [
                pattern for pattern in self.pattern_recognizer.patterns.values()
                if pattern.frequency >= min_frequency and pattern.confidence >= min_confidence
            ]
            
            for pattern in frequent_patterns:
                # Check if we already have an insight for this pattern
                existing_insights = self.query_insights(
                    related_to_pattern=pattern.pattern_id
                )
                
                if not existing_insights:
                    # Generate insight
                    insight_id = f"insight-{uuid.uuid4()}"
                    insight = LearningInsight(
                        insight_id=insight_id,
                        title=f"Frequent pattern insight: {pattern.name}",
                        description=f"Insight based on frequently occurring pattern {pattern.name}: {pattern.description}",
                        source_events=[],  # No specific events
                        source_patterns=[pattern.pattern_id],
                        confidence=pattern.confidence,
                        created_by="system",
                        tags=["frequent-pattern", pattern.name]
                    )
                    
                    insights.append(insight)
                    self.add_insight(insight)
            
            return insights
    
    def _check_cause_effect(
        self,
        cause_event: LearningEvent,
        effect_event: LearningEvent
    ) -> bool:
        """
        Check if there's a potential cause-effect relationship between two events.
        
        Args:
            cause_event: The potential cause event
            effect_event: The potential effect event
            
        Returns:
            True if there's a potential cause-effect relationship, False otherwise
        """
        # Check if the events are close in time
        time_diff = effect_event.timestamp - cause_event.timestamp
        if time_diff <= 0 or time_diff > 60:  # Within 60 seconds
            return False
            
        # Check if the events are related
        if (effect_event.task_id and effect_event.task_id == cause_event.task_id) or \
           (effect_event.team_id and effect_event.team_id == cause_event.team_id) or \
           cause_event.event_id in effect_event.related_events or \
           effect_event.event_id in cause_event.related_events:
            return True
            
        return False


class SkillModelManager:
    """Manages skill models that can be learned and shared."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.models: Dict[str, SkillModel] = {}
        self.lock = threading.RLock()
        
    def add_model(self, model: SkillModel) -> str:
        """
        Add a skill model.
        
        Args:
            model: The skill model to add
            
        Returns:
            The ID of the added model
        """
        with self.lock:
            self.models[model.model_id] = model
            logger.info(f"Added skill model {model.model_id}: {model.name}")
            return model.model_id
    
    def get_model(self, model_id: str) -> Optional[SkillModel]:
        """Get a skill model by ID."""
        with self.lock:
            return self.models.get(model_id)
    
    def update_model(
        self,
        model_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        training_events: Optional[List[str]] = None
    ) -> bool:
        """
        Update a skill model.
        
        Args:
            model_id: The ID of the model to update
            parameters: Optional new parameters
            performance_metrics: Optional new performance metrics
            training_events: Optional new training events
            
        Returns:
            True if the update was successful, False otherwise
        """
        with self.lock:
            model = self.models.get(model_id)
            if not model:
                logger.warning(f"Model {model_id} not found")
                return False
                
            if parameters:
                model.parameters.update(parameters)
                
            if performance_metrics:
                model.performance_metrics.update(performance_metrics)
                
            if training_events:
                for event_id in training_events:
                    if event_id not in model.training_events:
                        model.training_events.append(event_id)
                        
            model.version += 1
            model.updated_at = time.time()
            
            logger.info(f"Updated skill model {model_id} to version {model.version}")
            return True
    
    def query_models(
        self,
        skill_type: Optional[str] = None,
        created_by: Optional[str] = None,
        min_performance: Optional[Dict[str, float]] = None
    ) -> List[SkillModel]:
        """
        Query skill models based on various criteria.
        
        Args:
            skill_type: Filter by skill type
            created_by: Filter by creator
            min_performance: Filter by minimum performance metrics
            
        Returns:
            List of matching skill models
        """
        with self.lock:
            results = []
            
            for model in self.models.values():
                # Apply filters
                if skill_type and model.skill_type != skill_type:
                    continue
                    
                if created_by and model.created_by != created_by:
                    continue
                    
                if min_performance:
                    meets_performance = True
                    for metric, min_value in min_performance.items():
                        if metric not in model.performance_metrics or model.performance_metrics[metric] < min_value:
                            meets_performance = False
                            break
                            
                    if not meets_performance:
                        continue
                        
                results.append(model)
                
            return results
    
    def train_model(
        self,
        model_id: str,
        training_events: List[str],
        training_function: Callable[[SkillModel, List[LearningEvent]], Dict[str, Any]]
    ) -> bool:
        """
        Train a skill model using learning events.
        
        Args:
            model_id: The ID of the model to train
            training_events: List of event IDs to use for training
            training_function: Function that trains the model and returns new parameters
            
        Returns:
            True if training was successful, False otherwise
        """
        with self.lock:
            model = self.models.get(model_id)
            if not model:
                logger.warning(f"Model {model_id} not found")
                return False
                
            # Get the events
            events = self.event_store.get_event_sequence(training_events)
            if not events:
                logger.warning(f"No events found for training model {model_id}")
                return False
                
            try:
                # Train the model
                new_parameters = training_function(model, events)
                
                # Update the model
                return self.update_model(
                    model_id=model_id,
                    parameters=new_parameters,
                    training_events=training_events
                )
            except Exception as e:
                logger.error(f"Error training model {model_id}: {e}")
                return False
    
    def evaluate_model(
        self,
        model_id: str,
        evaluation_events: List[str],
        evaluation_function: Callable[[SkillModel, List[LearningEvent]], Dict[str, float]]
    ) -> Optional[Dict[str, float]]:
        """
        Evaluate a skill model using learning events.
        
        Args:
            model_id: The ID of the model to evaluate
            evaluation_events: List of event IDs to use for evaluation
            evaluation_function: Function that evaluates the model and returns performance metrics
            
        Returns:
            Dictionary of performance metrics, or None if evaluation failed
        """
        with self.lock:
            model = self.models.get(model_id)
            if not model:
                logger.warning(f"Model {model_id} not found")
                return None
                
            # Get the events
            events = self.event_store.get_event_sequence(evaluation_events)
            if not events:
                logger.warning(f"No events found for evaluating model {model_id}")
                return None
                
            try:
                # Evaluate the model
                performance_metrics = evaluation_function(model, events)
                
                # Update the model
                self.update_model(
                    model_id=model_id,
                    performance_metrics=performance_metrics
                )
                
                return performance_metrics
            except Exception as e:
                logger.error(f"Error evaluating model {model_id}: {e}")
                return None


class CollaborativeLearningService:
    """Service for collaborative learning between agents."""
    
    def __init__(
        self,
        event_store: Optional[EventStore] = None,
        pattern_recognizer: Optional[PatternRecognizer] = None,
        insight_generator: Optional[InsightGenerator] = None,
        skill_model_manager: Optional[SkillModelManager] = None
    ):
        self.event_store = event_store or EventStore()
        self.pattern_recognizer = pattern_recognizer or PatternRecognizer(self.event_store)
        self.insight_generator = insight_generator or InsightGenerator(self.event_store, self.pattern_recognizer)
        self.skill_model_manager = skill_model_manager or SkillModelManager(self.event_store)
        
    def record_observation(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an observation event.
        
        Args:
            agent_id: The ID of the agent making the observation
            content: The observation content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.OBSERVATION,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_action(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an action event.
        
        Args:
            agent_id: The ID of the agent performing the action
            content: The action content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.ACTION,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_feedback(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a feedback event.
        
        Args:
            agent_id: The ID of the agent receiving the feedback
            content: The feedback content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.FEEDBACK,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_error(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an error event.
        
        Args:
            agent_id: The ID of the agent encountering the error
            content: The error content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.ERROR,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_insight(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an insight event.
        
        Args:
            agent_id: The ID of the agent generating the insight
            content: The insight content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.INSIGHT,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_knowledge(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a knowledge event.
        
        Args:
            agent_id: The ID of the agent acquiring the knowledge
            content: The knowledge content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.KNOWLEDGE,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_skill(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a skill event.
        
        Args:
            agent_id: The ID of the agent demonstrating the skill
            content: The skill content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.SKILL,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def record_interaction(
        self,
        agent_id: str,
        content: Any,
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an interaction event.
        
        Args:
            agent_id: The ID of the agent involved in the interaction
            content: The interaction content
            task_id: Optional task ID
            team_id: Optional team ID
            related_events: Optional list of related event IDs
            metadata: Optional additional metadata
            
        Returns:
            The ID of the created event
        """
        event_id = f"event-{uuid.uuid4()}"
        event = LearningEvent(
            event_id=event_id,
            event_type=LearningEventType.INTERACTION,
            agent_id=agent_id,
            content=content,
            task_id=task_id,
            team_id=team_id,
            related_events=related_events or [],
            metadata=metadata or {}
        )
        
        return self.event_store.add_event(event)
    
    def get_agent_history(
        self,
        agent_id: str,
        limit: int = 100,
        event_types: Optional[List[LearningEventType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent events for a specific agent.
        
        Args:
            agent_id: The ID of the agent
            limit: Maximum number of events to return
            event_types: Optional list of event types to include
            
        Returns:
            List of dictionaries with event information
        """
        events = self.event_store.get_agent_events(
            agent_id=agent_id,
            limit=limit,
            event_types=event_types
        )
        
        return [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "agent_id": event.agent_id,
                "content": event.content,
                "timestamp": event.timestamp,
                "task_id": event.task_id,
                "team_id": event.team_id
            }
            for event in events
        ]
    
    def get_team_history(
        self,
        team_id: str,
        limit: int = 100,
        event_types: Optional[List[LearningEventType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent events for a specific team.
        
        Args:
            team_id: The ID of the team
            limit: Maximum number of events to return
            event_types: Optional list of event types to include
            
        Returns:
            List of dictionaries with event information
        """
        events = self.event_store.get_team_events(
            team_id=team_id,
            limit=limit,
            event_types=event_types
        )
        
        return [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "agent_id": event.agent_id,
                "content": event.content,
                "timestamp": event.timestamp,
                "task_id": event.task_id,
                "team_id": event.team_id
            }
            for event in events
        ]
    
    def get_task_history(
        self,
        task_id: str,
        limit: int = 100,
        event_types: Optional[List[LearningEventType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent events for a specific task.
        
        Args:
            task_id: The ID of the task
            limit: Maximum number of events to return
            event_types: Optional list of event types to include
            
        Returns:
            List of dictionaries with event information
        """
        events = self.event_store.get_task_events(
            task_id=task_id,
            limit=limit,
            event_types=event_types
        )
        
        return [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "agent_id": event.agent_id,
                "content": event.content,
                "timestamp": event.timestamp,
                "task_id": event.task_id,
                "team_id": event.team_id
            }
            for event in events
        ]
    
    def analyze_events(
        self,
        event_ids: List[str],
        generate_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a sequence of events.
        
        Args:
            event_ids: List of event IDs to analyze
            generate_insights: Whether to generate insights
            
        Returns:
            Dictionary with analysis results
        """
        # Get the events
        events = self.event_store.get_event_sequence(event_ids)
        if not events:
            return {"error": "No events found"}
            
        # Find patterns
        patterns = self.pattern_recognizer.detect_patterns(events)
        
        # Add new patterns
        for pattern in patterns:
            self.pattern_recognizer.add_pattern(pattern)
            
        # Find matching existing patterns
        matching_patterns = self.pattern_recognizer.find_matching_patterns(events)
        
        # Generate insights if requested
        insights = []
        if generate_insights:
            insights = self.insight_generator.generate_insights_from_events(events)
            
        # Prepare results
        results = {
            "events_analyzed": len(events),
            "patterns_detected": [
                {
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "description": pattern.description,
                    "frequency": pattern.frequency,
                    "confidence": pattern.confidence
                }
                for pattern in patterns
            ],
            "matching_patterns": [
                {
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "description": pattern.description,
                    "match_score": match_score
                }
                for pattern, match_score in matching_patterns
            ],
            "insights_generated": [
                {
                    "insight_id": insight.insight_id,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence
                }
                for insight in insights
            ]
        }
        
        return results
    
    def get_insights(
        self,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get insights based on various criteria.
        
        Args:
            tags: Optional list of tags to filter by
            min_confidence: Minimum confidence threshold
            limit: Maximum number of insights to return
            
        Returns:
            List of dictionaries with insight information
        """
        insights = self.insight_generator.query_insights(
            tags=tags,
            min_confidence=min_confidence
        )
        
        # Sort by confidence (highest first)
        insights.sort(key=lambda x: x.confidence, reverse=True)
        
        # Return up to the limit
        return [
            {
                "insight_id": insight.insight_id,
                "title": insight.title,
                "description": insight.description,
                "confidence": insight.confidence,
                "created_at": insight.created_at,
                "created_by": insight.created_by,
                "tags": insight.tags
            }
            for insight in insights[:limit]
        ]
    
    def create_skill_model(
        self,
        name: str,
        description: str,
        skill_type: str,
        parameters: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> str:
        """
        Create a new skill model.
        
        Args:
            name: The name of the model
            description: The description of the model
            skill_type: The type of skill
            parameters: The model parameters
            created_by: Optional creator ID
            
        Returns:
            The ID of the created model
        """
        model_id = f"model-{uuid.uuid4()}"
        model = SkillModel(
            model_id=model_id,
            name=name,
            description=description,
            skill_type=skill_type,
            parameters=parameters,
            created_by=created_by
        )
        
        return self.skill_model_manager.add_model(model)
    
    def get_skill_models(
        self,
        skill_type: Optional[str] = None,
        created_by: Optional[str] = None,
        min_performance: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get skill models based on various criteria.
        
        Args:
            skill_type: Optional skill type to filter by
            created_by: Optional creator ID to filter by
            min_performance: Optional minimum performance metrics
            
        Returns:
            List of dictionaries with model information
        """
        models = self.skill_model_manager.query_models(
            skill_type=skill_type,
            created_by=created_by,
            min_performance=min_performance
        )
        
        return [
            {
                "model_id": model.model_id,
                "name": model.name,
                "description": model.description,
                "skill_type": model.skill_type,
                "version": model.version,
                "created_at": model.created_at,
                "updated_at": model.updated_at,
                "created_by": model.created_by,
                "performance_metrics": model.performance_metrics
            }
            for model in models
        ]
    
    def share_knowledge(
        self,
        source_agent_id: str,
        target_agent_id: str,
        knowledge_content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Share knowledge between agents.
        
        Args:
            source_agent_id: The ID of the source agent
            target_agent_id: The ID of the target agent
            knowledge_content: The knowledge content to share
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (source_event_id, target_event_id)
        """
        # Record knowledge event for source agent
        source_event_id = self.record_knowledge(
            agent_id=source_agent_id,
            content=knowledge_content,
            metadata=metadata
        )
        
        # Record knowledge event for target agent
        target_event_id = self.record_knowledge(
            agent_id=target_agent_id,
            content=knowledge_content,
            related_events=[source_event_id],
            metadata=metadata
        )
        
        # Record interaction event
        self.record_interaction(
            agent_id=source_agent_id,
            content={
                "type": "knowledge_sharing",
                "target_agent_id": target_agent_id,
                "knowledge_summary": str(knowledge_content)[:100] + "..." if len(str(knowledge_content)) > 100 else str(knowledge_content)
            },
            related_events=[source_event_id, target_event_id],
            metadata=metadata
        )
        
        return (source_event_id, target_event_id)
    
    def share_skill_model(
        self,
        model_id: str,
        source_agent_id: str,
        target_agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Share a skill model between agents.
        
        Args:
            model_id: The ID of the model to share
            source_agent_id: The ID of the source agent
            target_agent_id: The ID of the target agent
            metadata: Optional additional metadata
            
        Returns:
            The ID of the interaction event, or None if sharing failed
        """
        # Get the model
        model = self.skill_model_manager.get_model(model_id)
        if not model:
            logger.warning(f"Model {model_id} not found")
            return None
            
        # Record interaction event
        interaction_id = self.record_interaction(
            agent_id=source_agent_id,
            content={
                "type": "skill_model_sharing",
                "target_agent_id": target_agent_id,
                "model_id": model_id,
                "model_name": model.name,
                "skill_type": model.skill_type
            },
            metadata=metadata
        )
        
        # Record skill event for target agent
        self.record_skill(
            agent_id=target_agent_id,
            content={
                "type": "received_skill_model",
                "model_id": model_id,
                "model_name": model.name,
                "skill_type": model.skill_type,
                "source_agent_id": source_agent_id
            },
            related_events=[interaction_id],
            metadata=metadata
        )
        
        return interaction_id
    
    def collaborative_learning_session(
        self,
        agent_ids: List[str],
        task_id: Optional[str] = None,
        team_id: Optional[str] = None,
        session_duration: float = 300,  # 5 minutes
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a collaborative learning session between multiple agents.
        
        Args:
            agent_ids: List of agent IDs participating in the session
            task_id: Optional task ID
            team_id: Optional team ID
            session_duration: Duration of the session in seconds
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with session results
        """
        if len(agent_ids) < 2:
            return {"error": "At least two agents are required for a collaborative learning session"}
            
        session_id = f"session-{uuid.uuid4()}"
        session_start = time.time()
        session_end = session_start + session_duration
        
        # Record session start
        session_events = []
        for agent_id in agent_ids:
            event_id = self.record_interaction(
                agent_id=agent_id,
                content={
                    "type": "session_start",
                    "session_id": session_id,
                    "participants": agent_ids
                },
                task_id=task_id,
                team_id=team_id,
                metadata=metadata
            )
            session_events.append(event_id)
            
        # Simulate knowledge sharing
        knowledge_sharing_events = []
        for i in range(len(agent_ids)):
            for j in range(len(agent_ids)):
                if i != j:
                    # Agent i shares knowledge with agent j
                    source_id, target_id = self.share_knowledge(
                        source_agent_id=agent_ids[i],
                        target_agent_id=agent_ids[j],
                        knowledge_content={
                            "type": "session_knowledge",
                            "session_id": session_id,
                            "content": f"Knowledge shared from {agent_ids[i]} to {agent_ids[j]}"
                        },
                        metadata={
                            "session_id": session_id
                        }
                    )
                    knowledge_sharing_events.extend([source_id, target_id])
                    
        # Generate insights from session events
        all_events = session_events + knowledge_sharing_events
        insights = self.insight_generator.generate_insights_from_events(
            self.event_store.get_event_sequence(all_events)
        )
        
        # Record session end
        for agent_id in agent_ids:
            self.record_interaction(
                agent_id=agent_id,
                content={
                    "type": "session_end",
                    "session_id": session_id,
                    "participants": agent_ids,
                    "insights_generated": len(insights)
                },
                task_id=task_id,
                team_id=team_id,
                related_events=all_events,
                metadata=metadata
            )
            
        # Prepare results
        results = {
            "session_id": session_id,
            "participants": agent_ids,
            "duration": time.time() - session_start,
            "events_generated": len(all_events),
            "insights_generated": [
                {
                    "insight_id": insight.insight_id,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence
                }
                for insight in insights
            ]
        }
        
        return results
