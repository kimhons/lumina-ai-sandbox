import logging
import asyncio
import os
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import threading
import time

from .interfaces import (
    LearningEvent, FeedbackEvent, InteractionEvent, ErrorEvent, PerformanceEvent,
    LearningModel, LearningEventStore, LearningStrategy
)
from .event_store import EventStoreFactory
from .models import ModelFactory
from .strategies import StrategyFactory

logger = logging.getLogger(__name__)


class AdaptiveLearningSystem:
    """Main class for the adaptive learning system."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize a new adaptive learning system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.event_store = None
        self.models = {}
        self.strategy = None
        self.initialized = False
        self._running = False
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "event_store": {
                "type": "memory"
            },
            "models": {
                "feedback_classifier": {
                    "enabled": True
                },
                "response_quality": {
                    "enabled": True
                },
                "user_preference": {
                    "enabled": True
                }
            },
            "strategy": {
                "type": "basic",
                "training_interval": 3600,
                "min_events_for_training": 10
            },
            "model_storage": {
                "directory": "/tmp/lumina-ai/models"
            }
        }
        
        if not config_path:
            logger.info("No configuration file provided, using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Merge with default config
            merged_config = default_config.copy()
            for section, values in config.items():
                if section in merged_config:
                    if isinstance(merged_config[section], dict) and isinstance(values, dict):
                        merged_config[section].update(values)
                    else:
                        merged_config[section] = values
                else:
                    merged_config[section] = values
            
            logger.info(f"Loaded configuration from {config_path}")
            return merged_config
        
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return default_config
    
    async def initialize(self):
        """Initialize the adaptive learning system."""
        if self.initialized:
            logger.warning("Adaptive learning system already initialized")
            return
        
        try:
            # Create event store
            store_config = self.config["event_store"]
            self.event_store = EventStoreFactory.create_event_store(**store_config)
            
            # Create models
            for model_name, model_config in self.config["models"].items():
                if model_config.get("enabled", True):
                    model = ModelFactory.create_model(model_name)
                    self.models[model_name] = model
                    
                    # Load model if it exists
                    model_path = os.path.join(
                        self.config["model_storage"]["directory"],
                        f"{model_name}.model"
                    )
                    
                    if os.path.exists(model_path):
                        logger.info(f"Loading model from {model_path}")
                        await model.load(model_path)
            
            # Create strategy
            strategy_config = self.config["strategy"]
            strategy_type = strategy_config.pop("type")
            self.strategy = StrategyFactory.create_strategy(
                strategy_type,
                self.event_store,
                self.models,
                **strategy_config
            )
            
            # Start scheduled strategy if applicable
            if hasattr(self.strategy, 'start_scheduler'):
                self.strategy.start_scheduler()
            
            self.initialized = True
            logger.info("Adaptive learning system initialized")
        
        except Exception as e:
            logger.error(f"Error initializing adaptive learning system: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the adaptive learning system."""
        if not self.initialized:
            logger.warning("Adaptive learning system not initialized")
            return
        
        try:
            # Stop scheduled strategy if applicable
            if hasattr(self.strategy, 'stop_scheduler'):
                self.strategy.stop_scheduler()
            
            # Save models
            for model_name, model in self.models.items():
                model_path = os.path.join(
                    self.config["model_storage"]["directory"],
                    f"{model_name}.model"
                )
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                
                logger.info(f"Saving model to {model_path}")
                await model.save(model_path)
            
            self.initialized = False
            logger.info("Adaptive learning system shutdown")
        
        except Exception as e:
            logger.error(f"Error shutting down adaptive learning system: {e}")
            raise
    
    async def process_event(self, event: LearningEvent) -> bool:
        """
        Process a learning event.
        
        Args:
            event: Learning event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        if not self.initialized:
            logger.warning("Adaptive learning system not initialized")
            return False
        
        return await self.strategy.process_event(event)
    
    async def create_feedback_event(
        self,
        user_id: str,
        agent_id: str,
        conversation_id: str,
        rating: int,
        feedback_text: str = None,
        feedback_type: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create and process a feedback event.
        
        Args:
            user_id: ID of the user
            agent_id: ID of the agent
            conversation_id: ID of the conversation
            rating: Numerical rating (e.g., 1-5)
            feedback_text: Textual feedback
            feedback_type: Type of feedback (e.g., "response_quality", "helpfulness")
            metadata: Additional metadata
            
        Returns:
            ID of the created event if successful, None otherwise
        """
        event = FeedbackEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            rating=rating,
            feedback_text=feedback_text,
            feedback_type=feedback_type,
            metadata=metadata or {}
        )
        
        success = await self.process_event(event)
        return event.event_id if success else None
    
    async def create_interaction_event(
        self,
        user_id: str,
        agent_id: str,
        conversation_id: str,
        interaction_type: str,
        content: str,
        duration: float = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create and process an interaction event.
        
        Args:
            user_id: ID of the user
            agent_id: ID of the agent
            conversation_id: ID of the conversation
            interaction_type: Type of interaction (e.g., "message", "command")
            content: Content of the interaction
            duration: Duration of the interaction in seconds
            metadata: Additional metadata
            
        Returns:
            ID of the created event if successful, None otherwise
        """
        event = InteractionEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            interaction_type=interaction_type,
            content=content,
            duration=duration,
            metadata=metadata or {}
        )
        
        success = await self.process_event(event)
        return event.event_id if success else None
    
    async def create_error_event(
        self,
        user_id: str = None,
        agent_id: str = None,
        conversation_id: str = None,
        error_type: str = None,
        error_message: str = None,
        stack_trace: str = None,
        severity: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create and process an error event.
        
        Args:
            user_id: ID of the user
            agent_id: ID of the agent
            conversation_id: ID of the conversation
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace
            severity: Severity of the error (e.g., "info", "warning", "error", "critical")
            metadata: Additional metadata
            
        Returns:
            ID of the created event if successful, None otherwise
        """
        event = ErrorEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            severity=severity,
            metadata=metadata or {}
        )
        
        success = await self.process_event(event)
        return event.event_id if success else None
    
    async def create_performance_event(
        self,
        user_id: str = None,
        agent_id: str = None,
        conversation_id: str = None,
        metric_name: str = None,
        metric_value: float = None,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create and process a performance event.
        
        Args:
            user_id: ID of the user
            agent_id: ID of the agent
            conversation_id: ID of the conversation
            metric_name: Name of the performance metric
            metric_value: Value of the performance metric
            context: Context in which the metric was measured
            metadata: Additional metadata
            
        Returns:
            ID of the created event if successful, None otherwise
        """
        event = PerformanceEvent(
            user_id=user_id,
            agent_id=agent_id,
            conversation_id=conversation_id,
            metric_name=metric_name,
            metric_value=metric_value,
            context=context,
            metadata=metadata or {}
        )
        
        success = await self.process_event(event)
        return event.event_id if success else None
    
    async def apply_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learning to a context.
        
        Args:
            context: Context to apply learning to
            
        Returns:
            Modified context
        """
        if not self.initialized:
            logger.warning("Adaptive learning system not initialized")
            return context
        
        return await self.strategy.apply_learning(context)
    
    async def train_models(self) -> bool:
        """
        Manually trigger model training.
        
        Returns:
            True if training was successful, False otherwise
        """
        if not self.initialized:
            logger.warning("Adaptive learning system not initialized")
            return False
        
        return await self.strategy.train_models()
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the models.
        
        Returns:
            Dictionary with model information
        """
        if not self.initialized:
            logger.warning("Adaptive learning system not initialized")
            return {}
        
        result = {}
        for model_name, model in self.models.items():
            result[model_name] = model.metadata
        
        return result


class AdaptiveLearningService:
    """Service for running the adaptive learning system."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize a new adaptive learning service.
        
        Args:
            config_path: Path to configuration file
        """
        self.learning_system = AdaptiveLearningSystem(config_path)
        self._running = False
    
    async def start(self):
        """Start the adaptive learning service."""
        if self._running:
            logger.warning("Adaptive learning service already running")
            return
        
        await self.learning_system.initialize()
        self._running = True
        logger.info("Adaptive learning service started")
    
    async def stop(self):
        """Stop the adaptive learning service."""
        if not self._running:
            logger.warning("Adaptive learning service not running")
            return
        
        await self.learning_system.shutdown()
        self._running = False
        logger.info("Adaptive learning service stopped")
    
    async def run_forever(self):
        """Run the service indefinitely."""
        await self.start()
        
        try:
            # Keep the service running
            while self._running:
                await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            logger.info("Service execution cancelled")
        
        except Exception as e:
            logger.error(f"Error in service execution: {e}")
        
        finally:
            await self.stop()


def run_service(config_path: str = None):
    """
    Run the adaptive learning service.
    
    Args:
        config_path: Path to configuration file
    """
    service = AdaptiveLearningService(config_path)
    
    async def main():
        await service.run_forever()
    
    try:
        asyncio.run(main())
    
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    
    except Exception as e:
        logger.error(f"Error running service: {e}")


if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Get configuration path from command line arguments
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the service
    run_service(config_path)
