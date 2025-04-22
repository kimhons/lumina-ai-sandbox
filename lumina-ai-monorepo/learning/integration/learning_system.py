"""
Integration module for the Enhanced Learning System.

This module provides functionality to integrate all components of the
Enhanced Learning System, including the Learning Core, Continuous Learning,
Explainable AI, Knowledge Transfer, and Privacy Layer.
"""

import os
import logging
import datetime
import json
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd

# Import core components
from ..core.model_registry import ModelRegistry
from ..core.feature_engineering import FeatureEngineeringPipeline
from ..core.algorithm_factory import LearningAlgorithmFactory
from ..core.evaluation_framework import EvaluationFramework
from ..core.model_storage import ModelStorage

# Import continuous learning components
from ..continuous.user_interaction import UserInteractionLearning

# Import explainable AI components
from ..explainable.explainability import ExplainabilityEngine

# Import knowledge transfer components
from ..transfer.knowledge_transfer import KnowledgeTransferSystem

# Import privacy components
from ..privacy.privacy_layer import PrivacyManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedLearningSystem:
    """
    Main class for the Enhanced Learning System.
    
    This class integrates all components of the Enhanced Learning System and
    provides a unified interface for learning from user interactions.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Enhanced Learning System.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self._initialize_components()
        
        # System state
        self.is_initialized = True
        self.start_time = datetime.datetime.now()
        self.last_activity = self.start_time
        
        logger.info("Enhanced Learning System initialized")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            config: Configuration dictionary
        """
        # Default configuration
        default_config = {
            "system": {
                "name": "Lumina AI Enhanced Learning System",
                "version": "1.0.0",
                "storage_path": "/tmp/lumina_learning"
            },
            "core": {
                "model_registry": {
                    "enabled": True,
                    "default_model_type": "neural_network"
                },
                "feature_engineering": {
                    "enabled": True,
                    "auto_feature_selection": True
                },
                "algorithm_factory": {
                    "enabled": True,
                    "default_algorithm": "adaptive_ensemble"
                },
                "evaluation": {
                    "enabled": True,
                    "metrics": ["accuracy", "precision", "recall", "f1"]
                },
                "storage": {
                    "enabled": True,
                    "compression": True,
                    "versioning": True
                }
            },
            "continuous_learning": {
                "enabled": True,
                "learning_rate": 0.01,
                "batch_size": 32,
                "update_frequency": "real_time"
            },
            "explainable_ai": {
                "enabled": True,
                "methods": ["shap", "lime", "counterfactual"],
                "verbosity": "medium"
            },
            "knowledge_transfer": {
                "enabled": True,
                "transfer_method": "adaptive",
                "knowledge_retention": 0.8
            },
            "privacy": {
                "enabled": True,
                "differential_privacy": {
                    "enabled": True,
                    "epsilon": 1.0,
                    "delta": 1e-5
                },
                "federated_learning": {
                    "enabled": True,
                    "aggregation_method": "fedavg"
                },
                "secure_aggregation": {
                    "enabled": True,
                    "threshold": 3
                },
                "data_transformation": {
                    "enabled": True
                }
            }
        }
        
        # Load configuration from file if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Merge configurations
                self._merge_configs(default_config, file_config)
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {e}")
                logger.info("Using default configuration")
        else:
            logger.info("No configuration file provided, using default configuration")
        
        # Create storage directory
        storage_path = default_config["system"]["storage_path"]
        os.makedirs(storage_path, exist_ok=True)
        
        return default_config
    
    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]):
        """
        Merge override configuration into base configuration.
        
        Args:
            base_config: Base configuration to update
            override_config: Override configuration
        """
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value
    
    def _initialize_components(self):
        """Initialize all components of the Enhanced Learning System."""
        # Get storage path
        storage_path = self.config["system"]["storage_path"]
        
        # Initialize core components
        if self.config["core"]["model_registry"]["enabled"]:
            self.model_registry = ModelRegistry(
                default_model_type=self.config["core"]["model_registry"]["default_model_type"]
            )
            logger.info("Model Registry initialized")
        else:
            self.model_registry = None
            logger.info("Model Registry disabled")
        
        if self.config["core"]["feature_engineering"]["enabled"]:
            self.feature_engineering = FeatureEngineeringPipeline(
                auto_feature_selection=self.config["core"]["feature_engineering"]["auto_feature_selection"]
            )
            logger.info("Feature Engineering Pipeline initialized")
        else:
            self.feature_engineering = None
            logger.info("Feature Engineering Pipeline disabled")
        
        if self.config["core"]["algorithm_factory"]["enabled"]:
            self.algorithm_factory = LearningAlgorithmFactory(
                default_algorithm=self.config["core"]["algorithm_factory"]["default_algorithm"]
            )
            logger.info("Learning Algorithm Factory initialized")
        else:
            self.algorithm_factory = None
            logger.info("Learning Algorithm Factory disabled")
        
        if self.config["core"]["evaluation"]["enabled"]:
            self.evaluation_framework = EvaluationFramework(
                metrics=self.config["core"]["evaluation"]["metrics"]
            )
            logger.info("Evaluation Framework initialized")
        else:
            self.evaluation_framework = None
            logger.info("Evaluation Framework disabled")
        
        if self.config["core"]["storage"]["enabled"]:
            self.model_storage = ModelStorage(
                storage_path=os.path.join(storage_path, "models"),
                compression=self.config["core"]["storage"]["compression"],
                versioning=self.config["core"]["storage"]["versioning"]
            )
            logger.info("Model Storage initialized")
        else:
            self.model_storage = None
            logger.info("Model Storage disabled")
        
        # Initialize continuous learning components
        if self.config["continuous_learning"]["enabled"]:
            self.user_interaction_learning = UserInteractionLearning(
                learning_rate=self.config["continuous_learning"]["learning_rate"],
                batch_size=self.config["continuous_learning"]["batch_size"],
                update_frequency=self.config["continuous_learning"]["update_frequency"]
            )
            logger.info("User Interaction Learning initialized")
        else:
            self.user_interaction_learning = None
            logger.info("User Interaction Learning disabled")
        
        # Initialize explainable AI components
        if self.config["explainable_ai"]["enabled"]:
            self.explainability_engine = ExplainabilityEngine(
                methods=self.config["explainable_ai"]["methods"],
                verbosity=self.config["explainable_ai"]["verbosity"]
            )
            logger.info("Explainability Engine initialized")
        else:
            self.explainability_engine = None
            logger.info("Explainability Engine disabled")
        
        # Initialize knowledge transfer components
        if self.config["knowledge_transfer"]["enabled"]:
            self.knowledge_transfer = KnowledgeTransferSystem(
                transfer_method=self.config["knowledge_transfer"]["transfer_method"],
                knowledge_retention=self.config["knowledge_transfer"]["knowledge_retention"]
            )
            logger.info("Knowledge Transfer System initialized")
        else:
            self.knowledge_transfer = None
            logger.info("Knowledge Transfer System disabled")
        
        # Initialize privacy components
        if self.config["privacy"]["enabled"]:
            self.privacy_manager = PrivacyManager(
                storage_path=os.path.join(storage_path, "privacy")
            )
            
            # Update privacy settings
            self.privacy_manager.update_settings(self.config["privacy"])
            logger.info("Privacy Manager initialized")
        else:
            self.privacy_manager = None
            logger.info("Privacy Manager disabled")
    
    def train_model(self, 
                   model_id: str, 
                   data: Union[pd.DataFrame, np.ndarray], 
                   target: Union[pd.Series, np.ndarray],
                   model_type: str = None,
                   algorithm: str = None,
                   hyperparameters: Dict[str, Any] = None,
                   privacy_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Train a model with the Enhanced Learning System.
        
        Args:
            model_id: ID for the model
            data: Training data
            target: Target values
            model_type: Type of model to train
            algorithm: Learning algorithm to use
            hyperparameters: Hyperparameters for the algorithm
            privacy_settings: Privacy settings for training
            
        Returns:
            result: Training result
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Apply privacy transformations if enabled
        if self.privacy_manager and privacy_settings:
            # Update privacy settings if provided
            if privacy_settings:
                self.privacy_manager.update_settings(privacy_settings)
            
            # Apply privacy transformations to data
            if isinstance(data, pd.DataFrame):
                # For DataFrame, use anonymization
                identifiers = privacy_settings.get("identifiers", [])
                quasi_identifiers = privacy_settings.get("quasi_identifiers", [])
                sensitive_attributes = privacy_settings.get("sensitive_attributes", [])
                
                data = self.privacy_manager.privatize_data(
                    data,
                    method="anonymize",
                    identifiers=identifiers,
                    quasi_identifiers=quasi_identifiers,
                    sensitive_attributes=sensitive_attributes
                )
            else:
                # For arrays, use differential privacy
                sensitivity = privacy_settings.get("sensitivity", 1.0)
                
                data = self.privacy_manager.privatize_data(
                    data,
                    method="differential_privacy",
                    sensitivity=sensitivity
                )
        
        # Apply feature engineering if enabled
        if self.feature_engineering:
            data = self.feature_engineering.transform(data)
        
        # Get model type from registry if enabled
        if self.model_registry:
            if model_type:
                model_spec = self.model_registry.get_model_spec(model_type)
            else:
                model_spec = self.model_registry.get_default_model_spec()
        else:
            model_spec = {"type": model_type or "default"}
        
        # Get algorithm from factory if enabled
        if self.algorithm_factory:
            if algorithm:
                learning_algorithm = self.algorithm_factory.create_algorithm(algorithm, hyperparameters)
            else:
                learning_algorithm = self.algorithm_factory.create_default_algorithm(hyperparameters)
        else:
            # Simple fallback if factory is disabled
            from sklearn.ensemble import RandomForestClassifier
            learning_algorithm = RandomForestClassifier(**(hyperparameters or {}))
        
        # Train the model
        logger.info(f"Training model {model_id} with {learning_algorithm.__class__.__name__}")
        learning_algorithm.fit(data, target)
        
        # Evaluate the model if framework is enabled
        if self.evaluation_framework:
            evaluation_result = self.evaluation_framework.evaluate(learning_algorithm, data, target)
            logger.info(f"Model {model_id} evaluation: {evaluation_result}")
        else:
            evaluation_result = {}
        
        # Store the model if storage is enabled
        if self.model_storage:
            storage_result = self.model_storage.save_model(model_id, learning_algorithm, metadata={
                "model_type": model_spec.get("type"),
                "algorithm": algorithm,
                "hyperparameters": hyperparameters,
                "evaluation": evaluation_result,
                "timestamp": datetime.datetime.now().isoformat()
            })
            logger.info(f"Model {model_id} stored: {storage_result}")
        else:
            storage_result = {}
        
        # Return result
        return {
            "model_id": model_id,
            "model_type": model_spec.get("type"),
            "algorithm": algorithm or (learning_algorithm.__class__.__name__ if learning_algorithm else None),
            "evaluation": evaluation_result,
            "storage": storage_result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def predict(self, 
               model_id: str, 
               data: Union[pd.DataFrame, np.ndarray],
               explain: bool = False,
               privacy_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make predictions with a trained model.
        
        Args:
            model_id: ID of the model to use
            data: Data to make predictions on
            explain: Whether to generate explanations
            privacy_settings: Privacy settings for prediction
            
        Returns:
            result: Prediction result
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Apply privacy transformations if enabled
        if self.privacy_manager and privacy_settings:
            # Update privacy settings if provided
            if privacy_settings:
                self.privacy_manager.update_settings(privacy_settings)
            
            # Apply privacy transformations to data
            if isinstance(data, pd.DataFrame):
                # For DataFrame, use anonymization
                identifiers = privacy_settings.get("identifiers", [])
                quasi_identifiers = privacy_settings.get("quasi_identifiers", [])
                sensitive_attributes = privacy_settings.get("sensitive_attributes", [])
                
                data = self.privacy_manager.privatize_data(
                    data,
                    method="anonymize",
                    identifiers=identifiers,
                    quasi_identifiers=quasi_identifiers,
                    sensitive_attributes=sensitive_attributes
                )
            else:
                # For arrays, use differential privacy
                sensitivity = privacy_settings.get("sensitivity", 1.0)
                
                data = self.privacy_manager.privatize_data(
                    data,
                    method="differential_privacy",
                    sensitivity=sensitivity
                )
        
        # Apply feature engineering if enabled
        if self.feature_engineering:
            data = self.feature_engineering.transform(data)
        
        # Load the model if storage is enabled
        if self.model_storage:
            model, metadata = self.model_storage.load_model(model_id)
            logger.info(f"Model {model_id} loaded")
        else:
            raise ValueError(f"Model {model_id} not found (storage disabled)")
        
        # Make predictions
        predictions = model.predict(data)
        
        # Generate explanations if requested and engine is enabled
        explanations = None
        if explain and self.explainability_engine:
            explanations = self.explainability_engine.explain(model, data, predictions)
            logger.info(f"Generated explanations for model {model_id}")
        
        # Return result
        result = {
            "model_id": model_id,
            "predictions": predictions,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if explanations:
            result["explanations"] = explanations
        
        return result
    
    def update_from_feedback(self, 
                            model_id: str, 
                            data: Union[pd.DataFrame, np.ndarray],
                            target: Union[pd.Series, np.ndarray],
                            feedback_type: str = "explicit",
                            privacy_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update a model from user feedback.
        
        Args:
            model_id: ID of the model to update
            data: New data from feedback
            target: New target values from feedback
            feedback_type: Type of feedback ("explicit" or "implicit")
            privacy_settings: Privacy settings for update
            
        Returns:
            result: Update result
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Check if continuous learning is enabled
        if not self.user_interaction_learning:
            logger.warning("Continuous learning is disabled")
            return {"status": "error", "message": "Continuous learning is disabled"}
        
        # Apply privacy transformations if enabled
        if self.privacy_manager and privacy_settings:
            # Update privacy settings if provided
            if privacy_settings:
                self.privacy_manager.update_settings(privacy_settings)
            
            # Apply privacy transformations to data
            if isinstance(data, pd.DataFrame):
                # For DataFrame, use anonymization
                identifiers = privacy_settings.get("identifiers", [])
                quasi_identifiers = privacy_settings.get("quasi_identifiers", [])
                sensitive_attributes = privacy_settings.get("sensitive_attributes", [])
                
                data = self.privacy_manager.privatize_data(
                    data,
                    method="anonymize",
                    identifiers=identifiers,
                    quasi_identifiers=quasi_identifiers,
                    sensitive_attributes=sensitive_attributes
                )
            else:
                # For arrays, use differential privacy
                sensitivity = privacy_settings.get("sensitivity", 1.0)
                
                data = self.privacy_manager.privatize_data(
                    data,
                    method="differential_privacy",
                    sensitivity=sensitivity
                )
        
        # Apply feature engineering if enabled
        if self.feature_engineering:
            data = self.feature_engineering.transform(data)
        
        # Load the model if storage is enabled
        if self.model_storage:
            model, metadata = self.model_storage.load_model(model_id)
            logger.info(f"Model {model_id} loaded for update")
        else:
            raise ValueError(f"Model {model_id} not found (storage disabled)")
        
        # Update the model
        update_result = self.user_interaction_learning.update_model(
            model, data, target, feedback_type=feedback_type
        )
        
        # Evaluate the updated model if framework is enabled
        if self.evaluation_framework:
            evaluation_result = self.evaluation_framework.evaluate(model, data, target)
            logger.info(f"Updated model {model_id} evaluation: {evaluation_result}")
        else:
            evaluation_result = {}
        
        # Store the updated model if storage is enabled
        if self.model_storage:
            # Update metadata
            metadata.update({
                "last_update": datetime.datetime.now().isoformat(),
                "update_type": "feedback",
                "feedback_type": feedback_type,
                "evaluation": evaluation_result
            })
            
            storage_result = self.model_storage.save_model(model_id, model, metadata=metadata)
            logger.info(f"Updated model {model_id} stored: {storage_result}")
        else:
            storage_result = {}
        
        # Return result
        return {
            "model_id": model_id,
            "update_type": "feedback",
            "feedback_type": feedback_type,
            "evaluation": evaluation_result,
            "storage": storage_result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def transfer_knowledge(self, 
                          source_model_id: str, 
                          target_model_id: str,
                          transfer_type: str = "full",
                          knowledge_items: List[str] = None) -> Dict[str, Any]:
        """
        Transfer knowledge between models.
        
        Args:
            source_model_id: ID of the source model
            target_model_id: ID of the target model
            transfer_type: Type of transfer ("full", "partial", "selective")
            knowledge_items: Specific knowledge items to transfer (for selective)
            
        Returns:
            result: Transfer result
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Check if knowledge transfer is enabled
        if not self.knowledge_transfer:
            logger.warning("Knowledge transfer is disabled")
            return {"status": "error", "message": "Knowledge transfer is disabled"}
        
        # Load the models if storage is enabled
        if self.model_storage:
            source_model, source_metadata = self.model_storage.load_model(source_model_id)
            logger.info(f"Source model {source_model_id} loaded")
            
            target_model, target_metadata = self.model_storage.load_model(target_model_id)
            logger.info(f"Target model {target_model_id} loaded")
        else:
            raise ValueError("Models not found (storage disabled)")
        
        # Transfer knowledge
        transfer_result = self.knowledge_transfer.transfer(
            source_model, target_model, 
            transfer_type=transfer_type,
            knowledge_items=knowledge_items
        )
        
        # Store the updated target model if storage is enabled
        if self.model_storage:
            # Update metadata
            target_metadata.update({
                "last_update": datetime.datetime.now().isoformat(),
                "update_type": "knowledge_transfer",
                "source_model_id": source_model_id,
                "transfer_type": transfer_type,
                "transfer_result": transfer_result
            })
            
            storage_result = self.model_storage.save_model(target_model_id, target_model, metadata=target_metadata)
            logger.info(f"Updated target model {target_model_id} stored: {storage_result}")
        else:
            storage_result = {}
        
        # Return result
        return {
            "source_model_id": source_model_id,
            "target_model_id": target_model_id,
            "transfer_type": transfer_type,
            "transfer_result": transfer_result,
            "storage": storage_result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def setup_federated_learning(self, 
                                model_id: str,
                                client_ids: List[str]) -> Dict[str, Any]:
        """
        Set up federated learning for a model.
        
        Args:
            model_id: ID of the model to use
            client_ids: IDs of participating clients
            
        Returns:
            result: Setup result
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Check if privacy manager is enabled
        if not self.privacy_manager:
            logger.warning("Privacy manager is disabled")
            return {"status": "error", "message": "Privacy manager is disabled"}
        
        # Load the model if storage is enabled
        if self.model_storage:
            model, metadata = self.model_storage.load_model(model_id)
            logger.info(f"Model {model_id} loaded for federated learning")
        else:
            raise ValueError(f"Model {model_id} not found (storage disabled)")
        
        # Set up federated learning
        setup_result = self.privacy_manager.setup_federated_learning(model)
        
        # Register clients
        for client_id in client_ids:
            self.privacy_manager.register_federated_client(client_id)
        
        # Return result
        return {
            "model_id": model_id,
            "client_ids": client_ids,
            "setup_result": setup_result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def aggregate_federated_updates(self, model_id: str) -> Dict[str, Any]:
        """
        Aggregate updates in federated learning.
        
        Args:
            model_id: ID of the model
            
        Returns:
            result: Aggregation result
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Check if privacy manager is enabled
        if not self.privacy_manager:
            logger.warning("Privacy manager is disabled")
            return {"status": "error", "message": "Privacy manager is disabled"}
        
        # Aggregate models
        aggregation_result = self.privacy_manager.aggregate_federated_models()
        
        # Get the updated global model
        global_model = self.privacy_manager.federated_learning.get_global_model()
        
        # Store the updated model if storage is enabled
        if self.model_storage:
            # Load existing metadata
            _, metadata = self.model_storage.load_model(model_id)
            
            # Update metadata
            metadata.update({
                "last_update": datetime.datetime.now().isoformat(),
                "update_type": "federated_learning",
                "aggregation_result": aggregation_result
            })
            
            storage_result = self.model_storage.save_model(model_id, global_model, metadata=metadata)
            logger.info(f"Updated model {model_id} stored: {storage_result}")
        else:
            storage_result = {}
        
        # Return result
        return {
            "model_id": model_id,
            "aggregation_result": aggregation_result,
            "storage": storage_result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """
        Get a privacy report.
        
        Returns:
            report: Privacy report
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Check if privacy manager is enabled
        if not self.privacy_manager:
            logger.warning("Privacy manager is disabled")
            return {"status": "error", "message": "Privacy manager is disabled"}
        
        # Get privacy report
        report = self.privacy_manager.get_privacy_report()
        
        return report
    
    def get_explainability_report(self, 
                                 model_id: str, 
                                 data: Union[pd.DataFrame, np.ndarray],
                                 target: Union[pd.Series, np.ndarray] = None) -> Dict[str, Any]:
        """
        Get an explainability report for a model.
        
        Args:
            model_id: ID of the model
            data: Data to explain
            target: Target values (optional)
            
        Returns:
            report: Explainability report
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Check if explainability engine is enabled
        if not self.explainability_engine:
            logger.warning("Explainability engine is disabled")
            return {"status": "error", "message": "Explainability engine is disabled"}
        
        # Load the model if storage is enabled
        if self.model_storage:
            model, metadata = self.model_storage.load_model(model_id)
            logger.info(f"Model {model_id} loaded for explainability report")
        else:
            raise ValueError(f"Model {model_id} not found (storage disabled)")
        
        # Apply feature engineering if enabled
        if self.feature_engineering:
            data = self.feature_engineering.transform(data)
        
        # Make predictions
        predictions = model.predict(data)
        
        # Generate explanations
        explanations = self.explainability_engine.explain(model, data, predictions)
        
        # Generate report
        report = self.explainability_engine.generate_report(model, data, predictions, target, explanations)
        
        return {
            "model_id": model_id,
            "explanations": explanations,
            "report": report,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the status of the Enhanced Learning System.
        
        Returns:
            status: System status
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Get component statuses
        components = {
            "model_registry": self.model_registry is not None,
            "feature_engineering": self.feature_engineering is not None,
            "algorithm_factory": self.algorithm_factory is not None,
            "evaluation_framework": self.evaluation_framework is not None,
            "model_storage": self.model_storage is not None,
            "user_interaction_learning": self.user_interaction_learning is not None,
            "explainability_engine": self.explainability_engine is not None,
            "knowledge_transfer": self.knowledge_transfer is not None,
            "privacy_manager": self.privacy_manager is not None
        }
        
        # Get model count if storage is enabled
        model_count = 0
        if self.model_storage:
            model_count = len(self.model_storage.list_models())
        
        # Get privacy metrics if manager is enabled
        privacy_metrics = {}
        if self.privacy_manager:
            privacy_metrics = self.privacy_manager.get_metrics()
        
        # Calculate uptime
        uptime = datetime.datetime.now() - self.start_time
        uptime_seconds = uptime.total_seconds()
        
        # Calculate time since last activity
        idle_time = datetime.datetime.now() - self.last_activity
        idle_seconds = idle_time.total_seconds()
        
        return {
            "system": {
                "name": self.config["system"]["name"],
                "version": self.config["system"]["version"],
                "initialized": self.is_initialized,
                "uptime_seconds": uptime_seconds,
                "idle_seconds": idle_seconds,
                "start_time": self.start_time.isoformat(),
                "last_activity": self.last_activity.isoformat()
            },
            "components": components,
            "models": {
                "count": model_count
            },
            "privacy": privacy_metrics,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def save_system_state(self) -> Dict[str, Any]:
        """
        Save the current state of the Enhanced Learning System.
        
        Returns:
            save_info: Information about the saved state
        """
        # Update last activity
        self.last_activity = datetime.datetime.now()
        
        # Get storage path
        storage_path = self.config["system"]["storage_path"]
        
        try:
            # Create state dictionary
            state = {
                "system": {
                    "name": self.config["system"]["name"],
                    "version": self.config["system"]["version"],
                    "config": self.config,
                    "start_time": self.start_time.isoformat(),
                    "last_activity": self.last_activity.isoformat()
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save privacy state if manager is enabled
            if self.privacy_manager:
                self.privacy_manager.save_state()
            
            # Save to file
            state_file = os.path.join(storage_path, "system_state.json")
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            return {
                "status": "success",
                "file": state_file,
                "timestamp": state["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error saving system state: {e}")
            return {"status": "error", "message": str(e)}
    
    def load_system_state(self) -> Dict[str, Any]:
        """
        Load the saved state of the Enhanced Learning System.
        
        Returns:
            load_info: Information about the loaded state
        """
        # Get storage path
        storage_path = self.config["system"]["storage_path"]
        
        try:
            # Load from file
            state_file = os.path.join(storage_path, "system_state.json")
            
            if not os.path.exists(state_file):
                logger.warning("No saved system state found")
                return {"status": "error", "message": "No saved system state found"}
                
            with open(state_file, 'r') as f:
                state = json.load(f)
                
            # Restore system state
            if "system" in state and "config" in state["system"]:
                self.config = state["system"]["config"]
                
                # Re-initialize components with loaded config
                self._initialize_components()
                
                # Load privacy state if manager is enabled
                if self.privacy_manager:
                    self.privacy_manager.load_state()
                
                # Update timestamps
                if "start_time" in state["system"]:
                    self.start_time = datetime.datetime.fromisoformat(state["system"]["start_time"])
                
                if "last_activity" in state["system"]:
                    self.last_activity = datetime.datetime.fromisoformat(state["system"]["last_activity"])
                
                return {
                    "status": "success",
                    "file": state_file,
                    "timestamp": state.get("timestamp")
                }
            else:
                logger.error("Invalid system state file")
                return {"status": "error", "message": "Invalid system state file"}
            
        except Exception as e:
            logger.error(f"Error loading system state: {e}")
            return {"status": "error", "message": str(e)}
