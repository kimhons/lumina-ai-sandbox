"""
User Interaction Learning Module for Lumina AI Enhanced Learning System

This module provides functionality for continuous learning from user interactions,
enabling the system to adapt and improve based on user feedback and behavior patterns.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass
import os
import json
import datetime
import uuid
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class UserInteraction:
    """Representation of a user interaction event."""
    interaction_id: str
    user_id: str
    session_id: str
    interaction_type: str  # e.g., "query", "feedback", "correction", "rating"
    content: Dict[str, Any]  # Interaction content (varies by type)
    timestamp: str
    context: Dict[str, Any]  # Additional context information
    metadata: Dict[str, Any]  # Additional metadata


@dataclass
class LearningSignal:
    """Extracted learning signal from user interactions."""
    signal_id: str
    source_interaction_ids: List[str]
    signal_type: str  # e.g., "preference", "correction", "reinforcement"
    strength: float  # 0.0 to 1.0
    content: Dict[str, Any]  # Signal content
    timestamp: str
    metadata: Dict[str, Any]  # Additional metadata


class UserInteractionCollector:
    """
    Collector for user interaction events.
    
    This class is responsible for collecting, validating, and storing user
    interaction events for later processing.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the UserInteractionCollector.
        
        Args:
            storage_path: Path to store interaction data
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # In-memory cache of recent interactions
        self.recent_interactions = []
        self.max_cache_size = 1000
    
    def record_interaction(self, 
                          user_id: str,
                          session_id: str,
                          interaction_type: str,
                          content: Dict[str, Any],
                          context: Dict[str, Any] = None,
                          metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record a user interaction event.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            interaction_type: Type of interaction
            content: Content of the interaction
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        # Generate interaction ID
        interaction_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create interaction object
        interaction = UserInteraction(
            interaction_id=interaction_id,
            user_id=user_id,
            session_id=session_id,
            interaction_type=interaction_type,
            content=content,
            timestamp=timestamp,
            context=context or {},
            metadata=metadata or {}
        )
        
        # Add to cache
        self.recent_interactions.append(interaction)
        
        # Trim cache if needed
        if len(self.recent_interactions) > self.max_cache_size:
            self.recent_interactions = self.recent_interactions[-self.max_cache_size:]
        
        # Save to storage if path is provided
        if self.storage_path:
            self._save_interaction(interaction)
        
        return interaction
    
    def _save_interaction(self, interaction: UserInteraction):
        """
        Save an interaction to storage.
        
        Args:
            interaction: Interaction to save
        """
        # Create user directory
        user_dir = os.path.join(self.storage_path, interaction.user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Create session directory
        session_dir = os.path.join(user_dir, interaction.session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save interaction to file
        interaction_file = os.path.join(session_dir, f"{interaction.interaction_id}.json")
        
        with open(interaction_file, 'w') as f:
            # Convert dataclass to dict
            interaction_dict = {
                "interaction_id": interaction.interaction_id,
                "user_id": interaction.user_id,
                "session_id": interaction.session_id,
                "interaction_type": interaction.interaction_type,
                "content": interaction.content,
                "timestamp": interaction.timestamp,
                "context": interaction.context,
                "metadata": interaction.metadata
            }
            json.dump(interaction_dict, f, indent=2)
    
    def get_recent_interactions(self, 
                              user_id: str = None, 
                              session_id: str = None,
                              interaction_type: str = None,
                              limit: int = 100) -> List[UserInteraction]:
        """
        Get recent interactions, optionally filtered.
        
        Args:
            user_id: Filter by user ID
            session_id: Filter by session ID
            interaction_type: Filter by interaction type
            limit: Maximum number of interactions to return
            
        Returns:
            interactions: List of interactions
        """
        # Filter interactions
        filtered = self.recent_interactions
        
        if user_id:
            filtered = [i for i in filtered if i.user_id == user_id]
            
        if session_id:
            filtered = [i for i in filtered if i.session_id == session_id]
            
        if interaction_type:
            filtered = [i for i in filtered if i.interaction_type == interaction_type]
        
        # Sort by timestamp (newest first) and limit
        sorted_interactions = sorted(filtered, key=lambda i: i.timestamp, reverse=True)
        return sorted_interactions[:limit]
    
    def load_interactions(self, 
                         user_id: str = None, 
                         session_id: str = None,
                         start_time: str = None,
                         end_time: str = None,
                         limit: int = 1000) -> List[UserInteraction]:
        """
        Load interactions from storage, optionally filtered.
        
        Args:
            user_id: Filter by user ID
            session_id: Filter by session ID
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            limit: Maximum number of interactions to return
            
        Returns:
            interactions: List of interactions
        """
        if not self.storage_path:
            return []
            
        interactions = []
        
        # Determine which directories to search
        if user_id and session_id:
            # Specific user and session
            session_dirs = [os.path.join(self.storage_path, user_id, session_id)]
        elif user_id:
            # All sessions for a specific user
            user_dir = os.path.join(self.storage_path, user_id)
            if os.path.exists(user_dir):
                session_dirs = [os.path.join(user_dir, d) for d in os.listdir(user_dir)]
            else:
                session_dirs = []
        else:
            # All users and sessions
            session_dirs = []
            for user in os.listdir(self.storage_path):
                user_dir = os.path.join(self.storage_path, user)
                if os.path.isdir(user_dir):
                    for session in os.listdir(user_dir):
                        session_dirs.append(os.path.join(user_dir, session))
        
        # Load interactions from each directory
        for session_dir in session_dirs:
            if not os.path.exists(session_dir) or not os.path.isdir(session_dir):
                continue
                
            for filename in os.listdir(session_dir):
                if not filename.endswith(".json"):
                    continue
                    
                interaction_file = os.path.join(session_dir, filename)
                
                try:
                    with open(interaction_file, 'r') as f:
                        interaction_dict = json.load(f)
                        
                        # Apply time filters
                        if start_time and interaction_dict["timestamp"] < start_time:
                            continue
                            
                        if end_time and interaction_dict["timestamp"] > end_time:
                            continue
                        
                        # Create interaction object
                        interaction = UserInteraction(
                            interaction_id=interaction_dict["interaction_id"],
                            user_id=interaction_dict["user_id"],
                            session_id=interaction_dict["session_id"],
                            interaction_type=interaction_dict["interaction_type"],
                            content=interaction_dict["content"],
                            timestamp=interaction_dict["timestamp"],
                            context=interaction_dict["context"],
                            metadata=interaction_dict["metadata"]
                        )
                        
                        interactions.append(interaction)
                        
                        # Check limit
                        if len(interactions) >= limit:
                            break
                except Exception as e:
                    logger.error(f"Error loading interaction from {interaction_file}: {e}")
            
            # Check limit
            if len(interactions) >= limit:
                break
        
        # Sort by timestamp (newest first)
        return sorted(interactions, key=lambda i: i.timestamp, reverse=True)


class SignalExtractor:
    """
    Extractor for learning signals from user interactions.
    
    This class is responsible for analyzing user interactions and extracting
    learning signals that can be used to improve the system.
    """
    
    def __init__(self):
        """Initialize the SignalExtractor."""
        # Register default extractors
        self.extractors = {
            "feedback": self._extract_feedback_signal,
            "correction": self._extract_correction_signal,
            "rating": self._extract_rating_signal,
            "selection": self._extract_selection_signal,
            "query": self._extract_query_signal
        }
    
    def register_extractor(self, interaction_type: str, extractor_func: Callable):
        """
        Register a custom extractor function for an interaction type.
        
        Args:
            interaction_type: Type of interaction
            extractor_func: Function that takes an interaction and returns a list of signals
        """
        self.extractors[interaction_type] = extractor_func
    
    def extract_signals(self, interactions: List[UserInteraction]) -> List[LearningSignal]:
        """
        Extract learning signals from a list of interactions.
        
        Args:
            interactions: List of user interactions
            
        Returns:
            signals: List of extracted learning signals
        """
        signals = []
        
        for interaction in interactions:
            # Get extractor for this interaction type
            extractor = self.extractors.get(interaction.interaction_type)
            
            if extractor:
                # Extract signals
                interaction_signals = extractor(interaction)
                signals.extend(interaction_signals)
            
        return signals
    
    def _extract_feedback_signal(self, interaction: UserInteraction) -> List[LearningSignal]:
        """
        Extract signals from a feedback interaction.
        
        Args:
            interaction: Feedback interaction
            
        Returns:
            signals: List of extracted signals
        """
        signals = []
        
        # Check if interaction has required fields
        if "feedback_type" not in interaction.content or "feedback_value" not in interaction.content:
            return signals
            
        feedback_type = interaction.content["feedback_type"]
        feedback_value = interaction.content["feedback_value"]
        
        # Create signal based on feedback type
        if feedback_type == "thumbs_up" or feedback_type == "thumbs_down":
            # Binary feedback
            strength = 1.0 if feedback_value == "thumbs_up" else 0.0
            
            signal = LearningSignal(
                signal_id=str(uuid.uuid4()),
                source_interaction_ids=[interaction.interaction_id],
                signal_type="preference",
                strength=strength,
                content={
                    "feedback_type": feedback_type,
                    "feedback_value": feedback_value,
                    "target": interaction.content.get("target", {})
                },
                timestamp=datetime.datetime.now().isoformat(),
                metadata={}
            )
            
            signals.append(signal)
            
        elif feedback_type == "rating":
            # Rating feedback (e.g., 1-5 stars)
            try:
                rating = float(feedback_value)
                max_rating = float(interaction.content.get("max_rating", 5.0))
                
                # Normalize to 0.0-1.0
                strength = max(0.0, min(1.0, rating / max_rating))
                
                signal = LearningSignal(
                    signal_id=str(uuid.uuid4()),
                    source_interaction_ids=[interaction.interaction_id],
                    signal_type="preference",
                    strength=strength,
                    content={
                        "feedback_type": feedback_type,
                        "feedback_value": feedback_value,
                        "max_rating": max_rating,
                        "target": interaction.content.get("target", {})
                    },
                    timestamp=datetime.datetime.now().isoformat(),
                    metadata={}
                )
                
                signals.append(signal)
            except (ValueError, TypeError):
                # Invalid rating value
                pass
                
        elif feedback_type == "text":
            # Text feedback
            # This requires NLP to extract sentiment, which is beyond the scope of this example
            # In a real implementation, we would use a sentiment analysis model here
            
            # For now, just create a neutral signal
            signal = LearningSignal(
                signal_id=str(uuid.uuid4()),
                source_interaction_ids=[interaction.interaction_id],
                signal_type="feedback",
                strength=0.5,  # Neutral
                content={
                    "feedback_type": feedback_type,
                    "feedback_value": feedback_value,
                    "target": interaction.content.get("target", {})
                },
                timestamp=datetime.datetime.now().isoformat(),
                metadata={}
            )
            
            signals.append(signal)
        
        return signals
    
    def _extract_correction_signal(self, interaction: UserInteraction) -> List[LearningSignal]:
        """
        Extract signals from a correction interaction.
        
        Args:
            interaction: Correction interaction
            
        Returns:
            signals: List of extracted signals
        """
        signals = []
        
        # Check if interaction has required fields
        if "original" not in interaction.content or "correction" not in interaction.content:
            return signals
            
        original = interaction.content["original"]
        correction = interaction.content["correction"]
        
        # Create correction signal
        signal = LearningSignal(
            signal_id=str(uuid.uuid4()),
            source_interaction_ids=[interaction.interaction_id],
            signal_type="correction",
            strength=1.0,  # Corrections are always strong signals
            content={
                "original": original,
                "correction": correction,
                "target": interaction.content.get("target", {})
            },
            timestamp=datetime.datetime.now().isoformat(),
            metadata={}
        )
        
        signals.append(signal)
        
        return signals
    
    def _extract_rating_signal(self, interaction: UserInteraction) -> List[LearningSignal]:
        """
        Extract signals from a rating interaction.
        
        Args:
            interaction: Rating interaction
            
        Returns:
            signals: List of extracted signals
        """
        signals = []
        
        # Check if interaction has required fields
        if "rating" not in interaction.content:
            return signals
            
        rating = interaction.content["rating"]
        max_rating = interaction.content.get("max_rating", 5.0)
        
        try:
            # Normalize to 0.0-1.0
            strength = max(0.0, min(1.0, float(rating) / float(max_rating)))
            
            signal = LearningSignal(
                signal_id=str(uuid.uuid4()),
                source_interaction_ids=[interaction.interaction_id],
                signal_type="preference",
                strength=strength,
                content={
                    "rating": rating,
                    "max_rating": max_rating,
                    "target": interaction.content.get("target", {})
                },
                timestamp=datetime.datetime.now().isoformat(),
                metadata={}
            )
            
            signals.append(signal)
        except (ValueError, TypeError):
            # Invalid rating value
            pass
        
        return signals
    
    def _extract_selection_signal(self, interaction: UserInteraction) -> List[LearningSignal]:
        """
        Extract signals from a selection interaction.
        
        Args:
            interaction: Selection interaction
            
        Returns:
            signals: List of extracted signals
        """
        signals = []
        
        # Check if interaction has required fields
        if "selected" not in interaction.content or "options" not in interaction.content:
            return signals
            
        selected = interaction.content["selected"]
        options = interaction.content["options"]
        
        # Create selection signal
        signal = LearningSignal(
            signal_id=str(uuid.uuid4()),
            source_interaction_ids=[interaction.interaction_id],
            signal_type="preference",
            strength=1.0,  # Selections are strong positive signals for the selected option
            content={
                "selected": selected,
                "options": options,
                "target": interaction.content.get("target", {})
            },
            timestamp=datetime.datetime.now().isoformat(),
            metadata={}
        )
        
        signals.append(signal)
        
        # Create negative signals for non-selected options
        if isinstance(options, list) and len(options) > 1:
            for option in options:
                if option != selected:
                    signal = LearningSignal(
                        signal_id=str(uuid.uuid4()),
                        source_interaction_ids=[interaction.interaction_id],
                        signal_type="preference",
                        strength=0.0,  # Non-selections are strong negative signals
                        content={
                            "selected": False,
                            "option": option,
                            "target": interaction.content.get("target", {})
                        },
                        timestamp=datetime.datetime.now().isoformat(),
                        metadata={}
                    )
                    
                    signals.append(signal)
        
        return signals
    
    def _extract_query_signal(self, interaction: UserInteraction) -> List[LearningSignal]:
        """
        Extract signals from a query interaction.
        
        Args:
            interaction: Query interaction
            
        Returns:
            signals: List of extracted signals
        """
        signals = []
        
        # Check if interaction has required fields
        if "query" not in interaction.content:
            return signals
            
        query = interaction.content["query"]
        
        # Create query signal
        signal = LearningSignal(
            signal_id=str(uuid.uuid4()),
            source_interaction_ids=[interaction.interaction_id],
            signal_type="query",
            strength=0.5,  # Neutral strength for queries
            content={
                "query": query,
                "target": interaction.content.get("target", {})
            },
            timestamp=datetime.datetime.now().isoformat(),
            metadata={}
        )
        
        signals.append(signal)
        
        return signals


class SignalProcessor:
    """
    Processor for learning signals.
    
    This class is responsible for processing learning signals and preparing
    them for use in model training and adaptation.
    """
    
    def __init__(self):
        """Initialize the SignalProcessor."""
        # Register default processors
        self.processors = {
            "preference": self._process_preference_signal,
            "correction": self._process_correction_signal,
            "query": self._process_query_signal,
            "feedback": self._process_feedback_signal
        }
    
    def register_processor(self, signal_type: str, processor_func: Callable):
        """
        Register a custom processor function for a signal type.
        
        Args:
            signal_type: Type of signal
            processor_func: Function that takes a list of signals and returns processed data
        """
        self.processors[signal_type] = processor_func
    
    def process_signals(self, signals: List[LearningSignal]) -> Dict[str, Any]:
        """
        Process a list of learning signals.
        
        Args:
            signals: List of learning signals
            
        Returns:
            processed_data: Dictionary of processed data by signal type
        """
        # Group signals by type
        signals_by_type = defaultdict(list)
        for signal in signals:
            signals_by_type[signal.signal_type].append(signal)
        
        # Process each group
        processed_data = {}
        for signal_type, type_signals in signals_by_type.items():
            processor = self.processors.get(signal_type)
            
            if processor:
                # Process signals
                processed_data[signal_type] = processor(type_signals)
            
        return processed_data
    
    def _process_preference_signal(self, signals: List[LearningSignal]) -> Dict[str, Any]:
        """
        Process preference signals.
        
        Args:
            signals: List of preference signals
            
        Returns:
            processed_data: Processed preference data
        """
        # Group by target
        preferences_by_target = defaultdict(list)
        
        for signal in signals:
            target = json.dumps(signal.content.get("target", {}))
            preferences_by_target[target].append(signal.strength)
        
        # Calculate average preference for each target
        average_preferences = {}
        for target, strengths in preferences_by_target.items():
            average_preferences[target] = sum(strengths) / len(strengths)
        
        return {
            "average_preferences": average_preferences,
            "raw_signals": signals
        }
    
    def _process_correction_signal(self, signals: List[LearningSignal]) -> Dict[str, Any]:
        """
        Process correction signals.
        
        Args:
            signals: List of correction signals
            
        Returns:
            processed_data: Processed correction data
        """
        corrections = []
        
        for signal in signals:
            corrections.append({
                "original": signal.content.get("original"),
                "correction": signal.content.get("correction"),
                "target": signal.content.get("target", {})
            })
        
        return {
            "corrections": corrections,
            "raw_signals": signals
        }
    
    def _process_query_signal(self, signals: List[LearningSignal]) -> Dict[str, Any]:
        """
        Process query signals.
        
        Args:
            signals: List of query signals
            
        Returns:
            processed_data: Processed query data
        """
        queries = []
        
        for signal in signals:
            queries.append({
                "query": signal.content.get("query"),
                "target": signal.content.get("target", {})
            })
        
        return {
            "queries": queries,
            "raw_signals": signals
        }
    
    def _process_feedback_signal(self, signals: List[LearningSignal]) -> Dict[str, Any]:
        """
        Process feedback signals.
        
        Args:
            signals: List of feedback signals
            
        Returns:
            processed_data: Processed feedback data
        """
        feedback = []
        
        for signal in signals:
            feedback.append({
                "feedback_type": signal.content.get("feedback_type"),
                "feedback_value": signal.content.get("feedback_value"),
                "strength": signal.strength,
                "target": signal.content.get("target", {})
            })
        
        return {
            "feedback": feedback,
            "raw_signals": signals
        }


class ContinuousLearningManager:
    """
    Manager for continuous learning from user interactions.
    
    This class coordinates the collection of user interactions, extraction of
    learning signals, and adaptation of models based on those signals.
    """
    
    def __init__(self, 
                storage_path: str = None,
                model_registry = None,
                feature_engineering = None,
                algorithm_factory = None,
                evaluation_framework = None,
                model_storage = None):
        """
        Initialize the ContinuousLearningManager.
        
        Args:
            storage_path: Path to store interaction and signal data
            model_registry: Model registry instance
            feature_engineering: Feature engineering instance
            algorithm_factory: Algorithm factory instance
            evaluation_framework: Evaluation framework instance
            model_storage: Model storage instance
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # Initialize components
        self.interaction_collector = UserInteractionCollector(
            storage_path=os.path.join(storage_path, "interactions") if storage_path else None
        )
        self.signal_extractor = SignalExtractor()
        self.signal_processor = SignalProcessor()
        
        # Store references to other components
        self.model_registry = model_registry
        self.feature_engineering = feature_engineering
        self.algorithm_factory = algorithm_factory
        self.evaluation_framework = evaluation_framework
        self.model_storage = model_storage
        
        # Learning configuration
        self.learning_config = {
            "min_interactions_for_learning": 100,
            "learning_interval_hours": 24,
            "learning_batch_size": 1000,
            "max_training_samples": 10000,
            "enable_automatic_learning": True
        }
        
        # Learning state
        self.last_learning_time = None
        self.learning_in_progress = False
        self.learning_stats = {
            "total_interactions_processed": 0,
            "total_signals_extracted": 0,
            "total_learning_cycles": 0,
            "total_models_updated": 0
        }
    
    def record_interaction(self, 
                          user_id: str,
                          session_id: str,
                          interaction_type: str,
                          content: Dict[str, Any],
                          context: Dict[str, Any] = None,
                          metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record a user interaction event.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            interaction_type: Type of interaction
            content: Content of the interaction
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        # Record interaction
        interaction = self.interaction_collector.record_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type=interaction_type,
            content=content,
            context=context,
            metadata=metadata
        )
        
        # Check if we should trigger learning
        if self.learning_config["enable_automatic_learning"]:
            self._check_learning_trigger()
        
        return interaction
    
    def _check_learning_trigger(self):
        """Check if learning should be triggered based on current state."""
        # Don't trigger if learning is already in progress
        if self.learning_in_progress:
            return
            
        # Check if enough time has passed since last learning
        if self.last_learning_time:
            hours_since_last_learning = (datetime.datetime.now() - self.last_learning_time).total_seconds() / 3600
            if hours_since_last_learning < self.learning_config["learning_interval_hours"]:
                return
        
        # Check if we have enough new interactions
        recent_interactions = self.interaction_collector.get_recent_interactions(limit=self.learning_config["min_interactions_for_learning"])
        if len(recent_interactions) < self.learning_config["min_interactions_for_learning"]:
            return
            
        # Trigger learning
        self.trigger_learning_cycle()
    
    def trigger_learning_cycle(self, max_interactions: int = None):
        """
        Trigger a learning cycle.
        
        Args:
            max_interactions: Maximum number of interactions to process
        """
        if self.learning_in_progress:
            logger.warning("Learning cycle already in progress")
            return
            
        self.learning_in_progress = True
        
        try:
            # Set default max interactions
            if max_interactions is None:
                max_interactions = self.learning_config["learning_batch_size"]
                
            # Load interactions
            if self.last_learning_time:
                # Load interactions since last learning time
                start_time = self.last_learning_time.isoformat()
                interactions = self.interaction_collector.load_interactions(
                    start_time=start_time,
                    limit=max_interactions
                )
            else:
                # Load recent interactions
                interactions = self.interaction_collector.load_interactions(
                    limit=max_interactions
                )
            
            # Extract signals
            signals = self.signal_extractor.extract_signals(interactions)
            
            # Process signals
            processed_data = self.signal_processor.process_signals(signals)
            
            # Update models based on processed data
            updated_models = self._update_models(processed_data)
            
            # Update learning stats
            self.learning_stats["total_interactions_processed"] += len(interactions)
            self.learning_stats["total_signals_extracted"] += len(signals)
            self.learning_stats["total_learning_cycles"] += 1
            self.learning_stats["total_models_updated"] += len(updated_models)
            
            # Update last learning time
            self.last_learning_time = datetime.datetime.now()
            
            logger.info(f"Learning cycle completed: {len(interactions)} interactions, {len(signals)} signals, {len(updated_models)} models updated")
            
            return {
                "interactions_processed": len(interactions),
                "signals_extracted": len(signals),
                "models_updated": updated_models
            }
            
        except Exception as e:
            logger.error(f"Error in learning cycle: {e}")
            raise
            
        finally:
            self.learning_in_progress = False
    
    def _update_models(self, processed_data: Dict[str, Any]) -> List[str]:
        """
        Update models based on processed signal data.
        
        Args:
            processed_data: Processed signal data
            
        Returns:
            updated_models: List of updated model IDs
        """
        updated_models = []
        
        # Check if we have the required components
        if not all([self.model_registry, self.feature_engineering, self.algorithm_factory, self.evaluation_framework, self.model_storage]):
            logger.warning("Cannot update models: missing required components")
            return updated_models
        
        # Process preference signals
        if "preference" in processed_data:
            preference_data = processed_data["preference"]
            
            # Update recommendation models
            recommendation_models = self._update_recommendation_models(preference_data)
            updated_models.extend(recommendation_models)
        
        # Process correction signals
        if "correction" in processed_data:
            correction_data = processed_data["correction"]
            
            # Update language models
            language_models = self._update_language_models(correction_data)
            updated_models.extend(language_models)
        
        # Process query signals
        if "query" in processed_data:
            query_data = processed_data["query"]
            
            # Update query understanding models
            query_models = self._update_query_models(query_data)
            updated_models.extend(query_models)
        
        return updated_models
    
    def _update_recommendation_models(self, preference_data: Dict[str, Any]) -> List[str]:
        """
        Update recommendation models based on preference data.
        
        Args:
            preference_data: Processed preference data
            
        Returns:
            updated_models: List of updated model IDs
        """
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Retrieve existing recommendation models
        # 2. Update them with new preference data
        # 3. Evaluate the updated models
        # 4. Save the updated models if they perform better
        
        logger.info("Updating recommendation models with preference data")
        
        # Return list of updated model IDs
        return ["recommendation_model_1"]
    
    def _update_language_models(self, correction_data: Dict[str, Any]) -> List[str]:
        """
        Update language models based on correction data.
        
        Args:
            correction_data: Processed correction data
            
        Returns:
            updated_models: List of updated model IDs
        """
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Retrieve existing language models
        # 2. Fine-tune them with correction data
        # 3. Evaluate the updated models
        # 4. Save the updated models if they perform better
        
        logger.info("Updating language models with correction data")
        
        # Return list of updated model IDs
        return ["language_model_1"]
    
    def _update_query_models(self, query_data: Dict[str, Any]) -> List[str]:
        """
        Update query understanding models based on query data.
        
        Args:
            query_data: Processed query data
            
        Returns:
            updated_models: List of updated model IDs
        """
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Retrieve existing query understanding models
        # 2. Update them with new query data
        # 3. Evaluate the updated models
        # 4. Save the updated models if they perform better
        
        logger.info("Updating query models with query data")
        
        # Return list of updated model IDs
        return ["query_model_1"]
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the learning process.
        
        Returns:
            stats: Learning statistics
        """
        stats = self.learning_stats.copy()
        
        # Add additional information
        stats["last_learning_time"] = self.last_learning_time.isoformat() if self.last_learning_time else None
        stats["learning_in_progress"] = self.learning_in_progress
        stats["learning_config"] = self.learning_config
        
        return stats
    
    def update_learning_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the learning configuration.
        
        Args:
            config: New configuration values
            
        Returns:
            updated_config: The updated configuration
        """
        # Update configuration
        for key, value in config.items():
            if key in self.learning_config:
                self.learning_config[key] = value
        
        return self.learning_config


class FeedbackCollector:
    """
    Specialized collector for user feedback.
    
    This class provides methods for collecting various types of user feedback
    and converting them to interaction events.
    """
    
    def __init__(self, learning_manager: ContinuousLearningManager):
        """
        Initialize the FeedbackCollector.
        
        Args:
            learning_manager: Continuous learning manager
        """
        self.learning_manager = learning_manager
    
    def record_thumbs_feedback(self, 
                              user_id: str,
                              session_id: str,
                              is_positive: bool,
                              target: Dict[str, Any] = None,
                              context: Dict[str, Any] = None,
                              metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record thumbs up/down feedback.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            is_positive: Whether the feedback is positive (thumbs up)
            target: Target of the feedback (e.g., response ID)
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        feedback_value = "thumbs_up" if is_positive else "thumbs_down"
        
        content = {
            "feedback_type": "thumbs",
            "feedback_value": feedback_value
        }
        
        if target:
            content["target"] = target
        
        return self.learning_manager.record_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="feedback",
            content=content,
            context=context,
            metadata=metadata
        )
    
    def record_rating_feedback(self, 
                              user_id: str,
                              session_id: str,
                              rating: float,
                              max_rating: float = 5.0,
                              target: Dict[str, Any] = None,
                              context: Dict[str, Any] = None,
                              metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record rating feedback.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            rating: Rating value
            max_rating: Maximum possible rating
            target: Target of the feedback (e.g., response ID)
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        content = {
            "feedback_type": "rating",
            "feedback_value": rating,
            "max_rating": max_rating
        }
        
        if target:
            content["target"] = target
        
        return self.learning_manager.record_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="feedback",
            content=content,
            context=context,
            metadata=metadata
        )
    
    def record_text_feedback(self, 
                            user_id: str,
                            session_id: str,
                            text: str,
                            target: Dict[str, Any] = None,
                            context: Dict[str, Any] = None,
                            metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record text feedback.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            text: Feedback text
            target: Target of the feedback (e.g., response ID)
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        content = {
            "feedback_type": "text",
            "feedback_value": text
        }
        
        if target:
            content["target"] = target
        
        return self.learning_manager.record_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="feedback",
            content=content,
            context=context,
            metadata=metadata
        )
    
    def record_correction(self, 
                         user_id: str,
                         session_id: str,
                         original: str,
                         correction: str,
                         target: Dict[str, Any] = None,
                         context: Dict[str, Any] = None,
                         metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record a correction.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            original: Original text
            correction: Corrected text
            target: Target of the correction (e.g., response ID)
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        content = {
            "original": original,
            "correction": correction
        }
        
        if target:
            content["target"] = target
        
        return self.learning_manager.record_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="correction",
            content=content,
            context=context,
            metadata=metadata
        )
    
    def record_selection(self, 
                        user_id: str,
                        session_id: str,
                        selected: Any,
                        options: List[Any],
                        target: Dict[str, Any] = None,
                        context: Dict[str, Any] = None,
                        metadata: Dict[str, Any] = None) -> UserInteraction:
        """
        Record a selection from options.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            selected: Selected option
            options: Available options
            target: Target of the selection (e.g., query ID)
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            interaction: The recorded interaction
        """
        content = {
            "selected": selected,
            "options": options
        }
        
        if target:
            content["target"] = target
        
        return self.learning_manager.record_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="selection",
            content=content,
            context=context,
            metadata=metadata
        )


class UserPreferenceModel:
    """
    Model for learning and predicting user preferences.
    
    This class provides methods for learning user preferences from interaction
    data and making predictions based on those preferences.
    """
    
    def __init__(self, user_id: str = None):
        """
        Initialize the UserPreferenceModel.
        
        Args:
            user_id: ID of the user (if None, model is for all users)
        """
        self.user_id = user_id
        self.preferences = {}
        self.confidence = {}
        self.last_updated = None
    
    def update_from_signals(self, signals: List[LearningSignal]) -> bool:
        """
        Update the model from learning signals.
        
        Args:
            signals: List of learning signals
            
        Returns:
            updated: Whether the model was updated
        """
        if not signals:
            return False
            
        # Filter signals for this user if user_id is specified
        if self.user_id:
            # We need to extract user_id from the source interactions
            # This is a simplification; in a real system, signals would have user_id
            user_signals = []
            for signal in signals:
                if signal.metadata.get("user_id") == self.user_id:
                    user_signals.append(signal)
            signals = user_signals
            
        if not signals:
            return False
            
        # Process preference signals
        for signal in signals:
            if signal.signal_type != "preference":
                continue
                
            # Get target
            target = json.dumps(signal.content.get("target", {}))
            
            # Update preference
            if target not in self.preferences:
                self.preferences[target] = signal.strength
                self.confidence[target] = 1.0
            else:
                # Weighted average based on confidence
                current_confidence = self.confidence[target]
                new_confidence = current_confidence + 1.0
                
                # Update preference
                current_preference = self.preferences[target]
                new_preference = (current_preference * current_confidence + signal.strength) / new_confidence
                
                self.preferences[target] = new_preference
                self.confidence[target] = new_confidence
        
        # Update timestamp
        self.last_updated = datetime.datetime.now()
        
        return True
    
    def predict_preference(self, target: Dict[str, Any]) -> Tuple[float, float]:
        """
        Predict preference for a target.
        
        Args:
            target: Target to predict preference for
            
        Returns:
            preference: Predicted preference (0.0-1.0)
            confidence: Confidence in the prediction (0.0-1.0)
        """
        target_key = json.dumps(target)
        
        if target_key in self.preferences:
            # Direct match
            return self.preferences[target_key], min(1.0, self.confidence[target_key] / 10.0)
        
        # No direct match, try to find similar targets
        # This is a simplification; in a real system, we would use embeddings or other similarity measures
        
        # Default to neutral preference with low confidence
        return 0.5, 0.1
    
    def get_top_preferences(self, n: int = 10) -> List[Tuple[Dict[str, Any], float, float]]:
        """
        Get top N preferences.
        
        Args:
            n: Number of preferences to return
            
        Returns:
            preferences: List of (target, preference, confidence) tuples
        """
        # Sort preferences by value (descending)
        sorted_preferences = sorted(
            self.preferences.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Convert to list of tuples
        result = []
        for target_key, preference in sorted_preferences[:n]:
            target = json.loads(target_key)
            confidence = min(1.0, self.confidence[target_key] / 10.0)
            result.append((target, preference, confidence))
        
        return result
    
    def save(self, filepath: str):
        """
        Save the model to a file.
        
        Args:
            filepath: Path to save the model
        """
        data = {
            "user_id": self.user_id,
            "preferences": self.preferences,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'UserPreferenceModel':
        """
        Load a model from a file.
        
        Args:
            filepath: Path to load the model from
            
        Returns:
            model: The loaded model
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        model = cls(user_id=data["user_id"])
        model.preferences = data["preferences"]
        model.confidence = data["confidence"]
        
        if data["last_updated"]:
            model.last_updated = datetime.datetime.fromisoformat(data["last_updated"])
            
        return model


class UserPreferenceManager:
    """
    Manager for user preference models.
    
    This class provides methods for creating, updating, and using user preference
    models based on interaction data.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the UserPreferenceManager.
        
        Args:
            storage_path: Path to store preference models
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # Cache of user preference models
        self.user_models = {}
        
        # Global preference model
        self.global_model = UserPreferenceModel()
    
    def get_user_model(self, user_id: str) -> UserPreferenceModel:
        """
        Get preference model for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            model: User preference model
        """
        # Check if model is in cache
        if user_id in self.user_models:
            return self.user_models[user_id]
            
        # Check if model exists on disk
        if self.storage_path:
            model_path = os.path.join(self.storage_path, f"{user_id}.json")
            if os.path.exists(model_path):
                try:
                    model = UserPreferenceModel.load(model_path)
                    self.user_models[user_id] = model
                    return model
                except Exception as e:
                    logger.error(f"Error loading preference model for user {user_id}: {e}")
        
        # Create new model
        model = UserPreferenceModel(user_id=user_id)
        self.user_models[user_id] = model
        
        return model
    
    def update_models(self, signals: List[LearningSignal]) -> Dict[str, bool]:
        """
        Update preference models from learning signals.
        
        Args:
            signals: List of learning signals
            
        Returns:
            updated: Dictionary of user IDs and whether their models were updated
        """
        # Group signals by user
        signals_by_user = defaultdict(list)
        
        for signal in signals:
            # Extract user ID from metadata
            user_id = signal.metadata.get("user_id")
            if user_id:
                signals_by_user[user_id].append(signal)
        
        # Update global model
        global_updated = self.global_model.update_from_signals(signals)
        
        # Update user models
        updated = {"global": global_updated}
        
        for user_id, user_signals in signals_by_user.items():
            model = self.get_user_model(user_id)
            updated[user_id] = model.update_from_signals(user_signals)
            
            # Save updated model
            if updated[user_id] and self.storage_path:
                model_path = os.path.join(self.storage_path, f"{user_id}.json")
                try:
                    model.save(model_path)
                except Exception as e:
                    logger.error(f"Error saving preference model for user {user_id}: {e}")
        
        # Save global model
        if global_updated and self.storage_path:
            global_path = os.path.join(self.storage_path, "global.json")
            try:
                self.global_model.save(global_path)
            except Exception as e:
                logger.error(f"Error saving global preference model: {e}")
        
        return updated
    
    def predict_preference(self, user_id: str, target: Dict[str, Any]) -> Tuple[float, float]:
        """
        Predict preference for a target.
        
        Args:
            user_id: ID of the user
            target: Target to predict preference for
            
        Returns:
            preference: Predicted preference (0.0-1.0)
            confidence: Confidence in the prediction (0.0-1.0)
        """
        # Get user model
        user_model = self.get_user_model(user_id)
        
        # Get user prediction
        user_preference, user_confidence = user_model.predict_preference(target)
        
        # Get global prediction
        global_preference, global_confidence = self.global_model.predict_preference(target)
        
        # Combine predictions based on confidence
        if user_confidence > 0.5:
            # User model is confident, use it
            return user_preference, user_confidence
        elif user_confidence > 0.1:
            # User model has some confidence, blend with global
            weight = (user_confidence - 0.1) / 0.4  # Scale from 0.1-0.5 to 0.0-1.0
            blended_preference = user_preference * weight + global_preference * (1.0 - weight)
            blended_confidence = max(user_confidence, global_confidence * 0.8)
            return blended_preference, blended_confidence
        else:
            # User model has low confidence, use global
            return global_preference, global_confidence * 0.8  # Reduce global confidence slightly
    
    def get_top_preferences(self, user_id: str, n: int = 10) -> List[Tuple[Dict[str, Any], float, float]]:
        """
        Get top N preferences for a user.
        
        Args:
            user_id: ID of the user
            n: Number of preferences to return
            
        Returns:
            preferences: List of (target, preference, confidence) tuples
        """
        # Get user model
        user_model = self.get_user_model(user_id)
        
        # Get user preferences
        return user_model.get_top_preferences(n=n)
