import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
import os
import json
import time
import threading
from datetime import datetime, timedelta

from .interfaces import (
    LearningEvent, FeedbackEvent, InteractionEvent, ErrorEvent, PerformanceEvent,
    LearningModel, LearningEventStore, LearningStrategy
)
from .event_store import EventStoreFactory
from .models import ModelFactory

logger = logging.getLogger(__name__)


class BasicLearningStrategy(LearningStrategy):
    """Basic implementation of a learning strategy."""
    
    def __init__(
        self,
        event_store: LearningEventStore,
        models: Dict[str, LearningModel],
        training_interval: int = 3600,  # 1 hour
        min_events_for_training: int = 10
    ):
        """
        Initialize a new basic learning strategy.
        
        Args:
            event_store: Event store to use
            models: Dictionary of models to use
            training_interval: Interval between training runs in seconds
            min_events_for_training: Minimum number of events required for training
        """
        self.event_store = event_store
        self.models = models
        self.training_interval = training_interval
        self.min_events_for_training = min_events_for_training
        self.last_training_time = 0
        self.pending_events = 0
    
    async def process_event(self, event: LearningEvent) -> bool:
        """
        Process a learning event.
        
        Args:
            event: Learning event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Store the event
            success = await self.event_store.store_event(event)
            
            if success:
                self.pending_events += 1
                
                # Check if we should train models
                current_time = time.time()
                if (current_time - self.last_training_time > self.training_interval and 
                    self.pending_events >= self.min_events_for_training):
                    await self.train_models()
            
            return success
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False
    
    async def train_models(self) -> bool:
        """
        Train models based on collected events.
        
        Returns:
            True if training was successful, False otherwise
        """
        try:
            # Get all events
            events = await self.event_store.query_events()
            
            if len(events) < self.min_events_for_training:
                logger.info(f"Not enough events for training: {len(events)} < {self.min_events_for_training}")
                return False
            
            # Train each model
            success = True
            for model_name, model in self.models.items():
                logger.info(f"Training model: {model_name}")
                model_success = await model.train(events)
                
                if not model_success:
                    logger.warning(f"Failed to train model: {model_name}")
                    success = False
            
            # Update training time and reset pending events
            self.last_training_time = time.time()
            self.pending_events = 0
            
            return success
        
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    async def apply_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learning to a context.
        
        Args:
            context: Context to apply learning to
            
        Returns:
            Modified context
        """
        try:
            result = context.copy()
            
            # Apply each model
            for model_name, model in self.models.items():
                logger.debug(f"Applying model: {model_name}")
                prediction = await model.predict(context)
                
                # Add prediction to result
                result[model_name] = prediction
            
            return result
        
        except Exception as e:
            logger.error(f"Error applying learning: {e}")
            return context


class ScheduledLearningStrategy(LearningStrategy):
    """Learning strategy with scheduled training."""
    
    def __init__(
        self,
        event_store: LearningEventStore,
        models: Dict[str, LearningModel],
        schedule: Dict[str, List[str]] = None,
        min_events_for_training: int = 10
    ):
        """
        Initialize a new scheduled learning strategy.
        
        Args:
            event_store: Event store to use
            models: Dictionary of models to use
            schedule: Dictionary mapping days of week to hours for training
            min_events_for_training: Minimum number of events required for training
        """
        self.event_store = event_store
        self.models = models
        self.min_events_for_training = min_events_for_training
        
        # Default schedule: train every day at midnight
        self.schedule = schedule or {
            "monday": ["00:00"],
            "tuesday": ["00:00"],
            "wednesday": ["00:00"],
            "thursday": ["00:00"],
            "friday": ["00:00"],
            "saturday": ["00:00"],
            "sunday": ["00:00"]
        }
        
        self.last_training_time = datetime.now() - timedelta(days=1)
        self.pending_events = 0
        self.scheduler_thread = None
        self.running = False
    
    def start_scheduler(self):
        """Start the scheduler thread."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the scheduler thread."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1.0)
    
    def _scheduler_loop(self):
        """Scheduler loop that runs in a separate thread."""
        while self.running:
            now = datetime.now()
            day_of_week = now.strftime("%A").lower()
            time_str = now.strftime("%H:%M")
            
            # Check if we should train now
            if day_of_week in self.schedule and time_str in self.schedule[day_of_week]:
                # Check if we've already trained at this time
                if (now - self.last_training_time).total_seconds() > 3600:  # At least 1 hour since last training
                    # Create an event loop for the thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Train models
                    loop.run_until_complete(self.train_models())
                    
                    # Close the loop
                    loop.close()
            
            # Sleep for 1 minute
            time.sleep(60)
    
    async def process_event(self, event: LearningEvent) -> bool:
        """
        Process a learning event.
        
        Args:
            event: Learning event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Store the event
            success = await self.event_store.store_event(event)
            
            if success:
                self.pending_events += 1
            
            return success
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False
    
    async def train_models(self) -> bool:
        """
        Train models based on collected events.
        
        Returns:
            True if training was successful, False otherwise
        """
        try:
            # Get all events
            events = await self.event_store.query_events()
            
            if len(events) < self.min_events_for_training:
                logger.info(f"Not enough events for training: {len(events)} < {self.min_events_for_training}")
                return False
            
            # Train each model
            success = True
            for model_name, model in self.models.items():
                logger.info(f"Training model: {model_name}")
                model_success = await model.train(events)
                
                if not model_success:
                    logger.warning(f"Failed to train model: {model_name}")
                    success = False
            
            # Update training time and reset pending events
            self.last_training_time = datetime.now()
            self.pending_events = 0
            
            return success
        
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    async def apply_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learning to a context.
        
        Args:
            context: Context to apply learning to
            
        Returns:
            Modified context
        """
        try:
            result = context.copy()
            
            # Apply each model
            for model_name, model in self.models.items():
                logger.debug(f"Applying model: {model_name}")
                prediction = await model.predict(context)
                
                # Add prediction to result
                result[model_name] = prediction
            
            return result
        
        except Exception as e:
            logger.error(f"Error applying learning: {e}")
            return context


class StrategyFactory:
    """Factory for creating learning strategies."""
    
    @staticmethod
    def create_strategy(
        strategy_type: str,
        event_store: LearningEventStore,
        models: Dict[str, LearningModel],
        **kwargs
    ) -> LearningStrategy:
        """
        Create a learning strategy.
        
        Args:
            strategy_type: Type of strategy to create
            event_store: Event store to use
            models: Dictionary of models to use
            **kwargs: Additional arguments for the strategy
            
        Returns:
            The created strategy
            
        Raises:
            ValueError: If the strategy type is not supported
        """
        if strategy_type == "basic":
            training_interval = kwargs.get("training_interval", 3600)
            min_events = kwargs.get("min_events_for_training", 10)
            return BasicLearningStrategy(event_store, models, training_interval, min_events)
        elif strategy_type == "scheduled":
            schedule = kwargs.get("schedule")
            min_events = kwargs.get("min_events_for_training", 10)
            return ScheduledLearningStrategy(event_store, models, schedule, min_events)
        else:
            raise ValueError(f"Unsupported strategy type: {strategy_type}")
