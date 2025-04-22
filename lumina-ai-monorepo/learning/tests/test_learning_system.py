"""
Test module for the Enhanced Learning System.

This module provides comprehensive tests for all components of the
Enhanced Learning System, including the Learning Core, Continuous Learning,
Explainable AI, Knowledge Transfer, and Privacy Layer.
"""

import os
import unittest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
import tempfile
import shutil
import logging
import json
from typing import Dict, List, Any, Tuple

# Import the Enhanced Learning System
from ..integration.learning_system import EnhancedLearningSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestEnhancedLearningSystem(unittest.TestCase):
    """Test case for the Enhanced Learning System."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are reused across tests."""
        # Create a temporary directory for storage
        cls.temp_dir = tempfile.mkdtemp()
        
        # Create test configuration
        cls.config = {
            "system": {
                "name": "Lumina AI Enhanced Learning System Test",
                "version": "1.0.0",
                "storage_path": os.path.join(cls.temp_dir, "lumina_learning")
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
                    "default_algorithm": "random_forest"
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
        
        # Save configuration to file
        config_path = os.path.join(cls.temp_dir, "test_config.json")
        with open(config_path, 'w') as f:
            json.dump(cls.config, f, indent=2)
        
        # Create test datasets
        # Classification dataset
        X_cls, y_cls = make_classification(
            n_samples=1000,
            n_features=20,
            n_informative=10,
            n_redundant=5,
            n_classes=2,
            random_state=42
        )
        cls.X_cls_train, cls.X_cls_test, cls.y_cls_train, cls.y_cls_test = train_test_split(
            X_cls, y_cls, test_size=0.2, random_state=42
        )
        
        # Regression dataset
        X_reg, y_reg = make_regression(
            n_samples=1000,
            n_features=20,
            n_informative=10,
            noise=0.1,
            random_state=42
        )
        cls.X_reg_train, cls.X_reg_test, cls.y_reg_train, cls.y_reg_test = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42
        )
        
        # Create DataFrame versions of the datasets
        cls.df_cls_train = pd.DataFrame(cls.X_cls_train, columns=[f"feature_{i}" for i in range(20)])
        cls.df_cls_train["target"] = cls.y_cls_train
        cls.df_cls_test = pd.DataFrame(cls.X_cls_test, columns=[f"feature_{i}" for i in range(20)])
        cls.df_cls_test["target"] = cls.y_cls_test
        
        cls.df_reg_train = pd.DataFrame(cls.X_reg_train, columns=[f"feature_{i}" for i in range(20)])
        cls.df_reg_train["target"] = cls.y_reg_train
        cls.df_reg_test = pd.DataFrame(cls.X_reg_test, columns=[f"feature_{i}" for i in range(20)])
        cls.df_reg_test["target"] = cls.y_reg_test
        
        # Initialize the Enhanced Learning System
        cls.learning_system = EnhancedLearningSystem(config_path=config_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures after tests."""
        # Remove temporary directory
        shutil.rmtree(cls.temp_dir)
    
    def test_system_initialization(self):
        """Test that the system initializes correctly."""
        # Check that the system is initialized
        self.assertTrue(self.learning_system.is_initialized)
        
        # Check that all components are initialized
        status = self.learning_system.get_system_status()
        components = status["components"]
        
        self.assertTrue(components["model_registry"])
        self.assertTrue(components["feature_engineering"])
        self.assertTrue(components["algorithm_factory"])
        self.assertTrue(components["evaluation_framework"])
        self.assertTrue(components["model_storage"])
        self.assertTrue(components["user_interaction_learning"])
        self.assertTrue(components["explainability_engine"])
        self.assertTrue(components["knowledge_transfer"])
        self.assertTrue(components["privacy_manager"])
    
    def test_train_classification_model(self):
        """Test training a classification model."""
        # Train a classification model
        result = self.learning_system.train_model(
            model_id="test_classification",
            data=self.X_cls_train,
            target=self.y_cls_train,
            model_type="classification",
            algorithm="random_forest",
            hyperparameters={"n_estimators": 100, "max_depth": 10}
        )
        
        # Check that the model was trained successfully
        self.assertEqual(result["model_id"], "test_classification")
        self.assertEqual(result["model_type"], "classification")
        self.assertEqual(result["algorithm"], "random_forest")
        
        # Check that the model was evaluated
        self.assertIn("evaluation", result)
        evaluation = result["evaluation"]
        self.assertIn("accuracy", evaluation)
        self.assertIn("precision", evaluation)
        self.assertIn("recall", evaluation)
        self.assertIn("f1", evaluation)
        
        # Check that the model was stored
        self.assertIn("storage", result)
        storage = result["storage"]
        self.assertEqual(storage.get("status"), "success")
    
    def test_train_regression_model(self):
        """Test training a regression model."""
        # Train a regression model
        result = self.learning_system.train_model(
            model_id="test_regression",
            data=self.X_reg_train,
            target=self.y_reg_train,
            model_type="regression",
            algorithm="gradient_boosting",
            hyperparameters={"n_estimators": 100, "max_depth": 5}
        )
        
        # Check that the model was trained successfully
        self.assertEqual(result["model_id"], "test_regression")
        self.assertEqual(result["model_type"], "regression")
        self.assertEqual(result["algorithm"], "gradient_boosting")
        
        # Check that the model was evaluated
        self.assertIn("evaluation", result)
        
        # Check that the model was stored
        self.assertIn("storage", result)
        storage = result["storage"]
        self.assertEqual(storage.get("status"), "success")
    
    def test_predict_classification(self):
        """Test making predictions with a classification model."""
        # First, ensure we have a trained model
        self.test_train_classification_model()
        
        # Make predictions
        result = self.learning_system.predict(
            model_id="test_classification",
            data=self.X_cls_test,
            explain=True
        )
        
        # Check that predictions were made
        self.assertEqual(result["model_id"], "test_classification")
        self.assertIn("predictions", result)
        predictions = result["predictions"]
        self.assertEqual(len(predictions), len(self.X_cls_test))
        
        # Check that explanations were generated
        self.assertIn("explanations", result)
    
    def test_predict_regression(self):
        """Test making predictions with a regression model."""
        # First, ensure we have a trained model
        self.test_train_regression_model()
        
        # Make predictions
        result = self.learning_system.predict(
            model_id="test_regression",
            data=self.X_reg_test,
            explain=True
        )
        
        # Check that predictions were made
        self.assertEqual(result["model_id"], "test_regression")
        self.assertIn("predictions", result)
        predictions = result["predictions"]
        self.assertEqual(len(predictions), len(self.X_reg_test))
        
        # Check that explanations were generated
        self.assertIn("explanations", result)
    
    def test_update_from_feedback(self):
        """Test updating a model from user feedback."""
        # First, ensure we have a trained model
        self.test_train_classification_model()
        
        # Create some feedback data
        X_feedback = self.X_cls_test[:10]
        y_feedback = self.y_cls_test[:10]
        
        # Update the model
        result = self.learning_system.update_from_feedback(
            model_id="test_classification",
            data=X_feedback,
            target=y_feedback,
            feedback_type="explicit"
        )
        
        # Check that the model was updated successfully
        self.assertEqual(result["model_id"], "test_classification")
        self.assertEqual(result["update_type"], "feedback")
        self.assertEqual(result["feedback_type"], "explicit")
        
        # Check that the model was evaluated
        self.assertIn("evaluation", result)
        
        # Check that the model was stored
        self.assertIn("storage", result)
        storage = result["storage"]
        self.assertEqual(storage.get("status"), "success")
    
    def test_transfer_knowledge(self):
        """Test transferring knowledge between models."""
        # First, ensure we have trained models
        self.test_train_classification_model()
        self.test_train_regression_model()
        
        # Transfer knowledge
        result = self.learning_system.transfer_knowledge(
            source_model_id="test_classification",
            target_model_id="test_regression",
            transfer_type="partial"
        )
        
        # Check that knowledge was transferred successfully
        self.assertEqual(result["source_model_id"], "test_classification")
        self.assertEqual(result["target_model_id"], "test_regression")
        self.assertEqual(result["transfer_type"], "partial")
        
        # Check that transfer result is available
        self.assertIn("transfer_result", result)
        
        # Check that the model was stored
        self.assertIn("storage", result)
        storage = result["storage"]
        self.assertEqual(storage.get("status"), "success")
    
    def test_federated_learning(self):
        """Test federated learning setup and aggregation."""
        # First, ensure we have a trained model
        self.test_train_classification_model()
        
        # Set up federated learning
        setup_result = self.learning_system.setup_federated_learning(
            model_id="test_classification",
            client_ids=["client1", "client2", "client3"]
        )
        
        # Check that federated learning was set up successfully
        self.assertEqual(setup_result["model_id"], "test_classification")
        self.assertEqual(len(setup_result["client_ids"]), 3)
        
        # Simulate client updates (in a real system, clients would train locally)
        # For testing, we'll just aggregate without actual client updates
        
        # Aggregate updates
        aggregation_result = self.learning_system.aggregate_federated_updates(
            model_id="test_classification"
        )
        
        # Check that aggregation was performed
        self.assertEqual(aggregation_result["model_id"], "test_classification")
        self.assertIn("aggregation_result", aggregation_result)
        
        # Check that the model was stored
        self.assertIn("storage", aggregation_result)
        storage = aggregation_result["storage"]
        self.assertEqual(storage.get("status"), "success")
    
    def test_privacy_report(self):
        """Test generating a privacy report."""
        # Generate privacy report
        report = self.learning_system.get_privacy_report()
        
        # Check that the report was generated
        self.assertIsInstance(report, dict)
        self.assertIn("differential_privacy", report)
        self.assertIn("federated_learning", report)
        self.assertIn("secure_aggregation", report)
        self.assertIn("data_transformation", report)
    
    def test_explainability_report(self):
        """Test generating an explainability report."""
        # First, ensure we have a trained model
        self.test_train_classification_model()
        
        # Generate explainability report
        report = self.learning_system.get_explainability_report(
            model_id="test_classification",
            data=self.X_cls_test[:5],
            target=self.y_cls_test[:5]
        )
        
        # Check that the report was generated
        self.assertEqual(report["model_id"], "test_classification")
        self.assertIn("explanations", report)
        self.assertIn("report", report)
    
    def test_system_status(self):
        """Test getting system status."""
        # Get system status
        status = self.learning_system.get_system_status()
        
        # Check that status was generated
        self.assertIn("system", status)
        self.assertIn("components", status)
        self.assertIn("models", status)
        self.assertIn("privacy", status)
        
        # Check system info
        system = status["system"]
        self.assertEqual(system["name"], "Lumina AI Enhanced Learning System Test")
        self.assertEqual(system["version"], "1.0.0")
        self.assertTrue(system["initialized"])
    
    def test_save_load_system_state(self):
        """Test saving and loading system state."""
        # First, ensure we have some trained models
        self.test_train_classification_model()
        self.test_train_regression_model()
        
        # Save system state
        save_result = self.learning_system.save_system_state()
        
        # Check that state was saved successfully
        self.assertEqual(save_result["status"], "success")
        self.assertIn("file", save_result)
        
        # Create a new learning system instance
        new_system = EnhancedLearningSystem(config_path=os.path.join(self.temp_dir, "test_config.json"))
        
        # Load system state
        load_result = new_system.load_system_state()
        
        # Check that state was loaded successfully
        self.assertEqual(load_result["status"], "success")
        
        # Check that models are available in the new system
        # Make predictions with the loaded system
        result = new_system.predict(
            model_id="test_classification",
            data=self.X_cls_test,
            explain=False
        )
        
        # Check that predictions were made
        self.assertEqual(result["model_id"], "test_classification")
        self.assertIn("predictions", result)
    
    def test_privacy_preserving_training(self):
        """Test training with privacy-preserving features."""
        # Train a model with privacy settings
        privacy_settings = {
            "differential_privacy": {
                "enabled": True,
                "epsilon": 0.5  # More privacy
            },
            "data_transformation": {
                "enabled": True
            }
        }
        
        result = self.learning_system.train_model(
            model_id="private_classification",
            data=self.df_cls_train.drop("target", axis=1),
            target=self.df_cls_train["target"],
            model_type="classification",
            algorithm="random_forest",
            hyperparameters={"n_estimators": 100, "max_depth": 10},
            privacy_settings=privacy_settings
        )
        
        # Check that the model was trained successfully
        self.assertEqual(result["model_id"], "private_classification")
        self.assertEqual(result["model_type"], "classification")
        self.assertEqual(result["algorithm"], "random_forest")
        
        # Check that the model was evaluated
        self.assertIn("evaluation", result)
        
        # Check that the model was stored
        self.assertIn("storage", result)
        storage = result["storage"]
        self.assertEqual(storage.get("status"), "success")
        
        # Make predictions with the private model
        predict_result = self.learning_system.predict(
            model_id="private_classification",
            data=self.df_cls_test.drop("target", axis=1),
            explain=True,
            privacy_settings=privacy_settings
        )
        
        # Check that predictions were made
        self.assertEqual(predict_result["model_id"], "private_classification")
        self.assertIn("predictions", predict_result)
    
    def test_train_with_dataframe(self):
        """Test training with pandas DataFrame input."""
        # Train a model with DataFrame input
        result = self.learning_system.train_model(
            model_id="dataframe_classification",
            data=self.df_cls_train.drop("target", axis=1),
            target=self.df_cls_train["target"],
            model_type="classification",
            algorithm="random_forest",
            hyperparameters={"n_estimators": 100, "max_depth": 10}
        )
        
        # Check that the model was trained successfully
        self.assertEqual(result["model_id"], "dataframe_classification")
        self.assertEqual(result["model_type"], "classification")
        self.assertEqual(result["algorithm"], "random_forest")
        
        # Check that the model was evaluated
        self.assertIn("evaluation", result)
        
        # Check that the model was stored
        self.assertIn("storage", result)
        storage = result["storage"]
        self.assertEqual(storage.get("status"), "success")
        
        # Make predictions
        predict_result = self.learning_system.predict(
            model_id="dataframe_classification",
            data=self.df_cls_test.drop("target", axis=1),
            explain=True
        )
        
        # Check that predictions were made
        self.assertEqual(predict_result["model_id"], "dataframe_classification")
        self.assertIn("predictions", predict_result)


if __name__ == "__main__":
    unittest.main()
