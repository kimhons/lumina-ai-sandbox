"""
Explainable AI Module for Lumina AI Enhanced Learning System

This module provides explainability capabilities for machine learning models,
enabling transparency in how the system makes decisions and recommendations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass
import os
import json
import datetime
import logging
import matplotlib.pyplot as plt
import shap
from lime import lime_tabular, lime_text, lime_image
import eli5
from sklearn.inspection import permutation_importance
from sklearn.tree import export_graphviz, plot_tree
import graphviz
import base64
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Explanation:
    """Container for model explanation results."""
    model_id: str
    explanation_type: str
    explanation_data: Dict[str, Any]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    timestamp: str
    metadata: Dict[str, Any]


class ExplainabilityEngine:
    """
    Core engine for generating explanations for model decisions.
    
    This class provides methods for explaining model predictions using
    various explainability techniques.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the ExplainabilityEngine.
        
        Args:
            storage_path: Path to store explanation data
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # Register default explainers
        self.explainers = {
            "feature_importance": self._explain_feature_importance,
            "shap": self._explain_shap,
            "lime": self._explain_lime,
            "decision_path": self._explain_decision_path,
            "counterfactual": self._explain_counterfactual,
            "rule_extraction": self._explain_rule_extraction,
            "attention": self._explain_attention
        }
    
    def register_explainer(self, name: str, explainer_func: Callable):
        """
        Register a custom explainer function.
        
        Args:
            name: Name of the explainer
            explainer_func: Function that takes a model and data and returns an explanation
        """
        self.explainers[name] = explainer_func
    
    def explain_prediction(self, 
                          model: Any, 
                          input_data: Any,
                          output_data: Any = None,
                          explanation_type: str = "feature_importance",
                          model_id: str = None,
                          metadata: Dict[str, Any] = None) -> Explanation:
        """
        Generate an explanation for a model prediction.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction (if available)
            explanation_type: Type of explanation to generate
            model_id: ID of the model
            metadata: Additional metadata for the explanation
            
        Returns:
            explanation: The generated explanation
        """
        # Generate model ID if not provided
        if model_id is None:
            model_id = f"model_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        # Get explainer function
        explainer = self.explainers.get(explanation_type)
        if not explainer:
            raise ValueError(f"Unknown explanation type: {explanation_type}")
            
        # Generate explanation
        try:
            explanation_data = explainer(model, input_data, output_data, metadata or {})
            
            # Create explanation object
            explanation = Explanation(
                model_id=model_id,
                explanation_type=explanation_type,
                explanation_data=explanation_data,
                input_data=input_data if isinstance(input_data, dict) else None,
                output_data=output_data if isinstance(output_data, dict) else None,
                timestamp=datetime.datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            # Save explanation if storage path is provided
            if self.storage_path:
                self._save_explanation(explanation)
                
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating {explanation_type} explanation: {e}")
            raise
    
    def _save_explanation(self, explanation: Explanation):
        """
        Save an explanation to storage.
        
        Args:
            explanation: Explanation to save
        """
        # Create model directory
        model_dir = os.path.join(self.storage_path, explanation.model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # Create explanation file path
        explanation_file = os.path.join(
            model_dir, 
            f"{explanation.explanation_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )
        
        # Convert explanation to dict
        explanation_dict = {
            "model_id": explanation.model_id,
            "explanation_type": explanation.explanation_type,
            "explanation_data": explanation.explanation_data,
            "input_data": explanation.input_data,
            "output_data": explanation.output_data,
            "timestamp": explanation.timestamp,
            "metadata": explanation.metadata
        }
        
        # Save to file
        with open(explanation_file, 'w') as f:
            json.dump(explanation_dict, f, indent=2)
    
    def load_explanation(self, file_path: str) -> Explanation:
        """
        Load an explanation from a file.
        
        Args:
            file_path: Path to the explanation file
            
        Returns:
            explanation: The loaded explanation
        """
        with open(file_path, 'r') as f:
            explanation_dict = json.load(f)
            
        return Explanation(
            model_id=explanation_dict["model_id"],
            explanation_type=explanation_dict["explanation_type"],
            explanation_data=explanation_dict["explanation_data"],
            input_data=explanation_dict["input_data"],
            output_data=explanation_dict["output_data"],
            timestamp=explanation_dict["timestamp"],
            metadata=explanation_dict["metadata"]
        )
    
    def get_explanations(self, model_id: str, explanation_type: str = None) -> List[Explanation]:
        """
        Get explanations for a model.
        
        Args:
            model_id: ID of the model
            explanation_type: Type of explanation to filter by
            
        Returns:
            explanations: List of explanations
        """
        if not self.storage_path:
            return []
            
        model_dir = os.path.join(self.storage_path, model_id)
        if not os.path.exists(model_dir):
            return []
            
        explanations = []
        
        for filename in os.listdir(model_dir):
            if not filename.endswith(".json"):
                continue
                
            if explanation_type and not filename.startswith(f"{explanation_type}_"):
                continue
                
            explanation_file = os.path.join(model_dir, filename)
            
            try:
                explanation = self.load_explanation(explanation_file)
                explanations.append(explanation)
            except Exception as e:
                logger.error(f"Error loading explanation from {explanation_file}: {e}")
        
        return explanations
    
    def _explain_feature_importance(self, model, input_data, output_data, metadata):
        """
        Generate feature importance explanation.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: Feature importance explanation data
        """
        # Check if model has feature_importances_ attribute (e.g., tree-based models)
        if hasattr(model, "feature_importances_"):
            feature_importances = model.feature_importances_
            
            # Get feature names if available
            feature_names = metadata.get("feature_names")
            if feature_names is None and hasattr(model, "feature_names_in_"):
                feature_names = model.feature_names_in_
                
            if feature_names is None:
                # Create generic feature names
                if isinstance(input_data, pd.DataFrame):
                    feature_names = list(input_data.columns)
                else:
                    feature_names = [f"feature_{i}" for i in range(len(feature_importances))]
            
            # Create sorted importance data
            importance_data = sorted(
                zip(feature_names, feature_importances),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Convert to lists for JSON serialization
            features = [item[0] for item in importance_data]
            importances = [float(item[1]) for item in importance_data]
            
            return {
                "feature_names": features,
                "importance_values": importances,
                "importance_type": "built_in"
            }
            
        # If model doesn't have built-in feature importances, use permutation importance
        elif hasattr(model, "predict"):
            # Convert input data to numpy array if needed
            if isinstance(input_data, pd.DataFrame):
                X = input_data.values
                feature_names = list(input_data.columns)
            elif isinstance(input_data, dict):
                # Convert dict to DataFrame
                X = pd.DataFrame([input_data]).values
                feature_names = list(input_data.keys())
            else:
                X = input_data
                feature_names = metadata.get("feature_names", [f"feature_{i}" for i in range(X.shape[1])])
            
            # Get target if available
            y = metadata.get("target")
            
            # Calculate permutation importance
            if y is not None:
                # If we have target data, use it
                perm_importance = permutation_importance(model, X, y, n_repeats=10, random_state=42)
            else:
                # Otherwise, use a dummy target (less reliable)
                dummy_y = np.zeros(X.shape[0])
                perm_importance = permutation_importance(model, X, dummy_y, n_repeats=10, random_state=42)
            
            # Create sorted importance data
            importance_data = sorted(
                zip(feature_names, perm_importance.importances_mean),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Convert to lists for JSON serialization
            features = [item[0] for item in importance_data]
            importances = [float(item[1]) for item in importance_data]
            
            return {
                "feature_names": features,
                "importance_values": importances,
                "importance_type": "permutation"
            }
            
        else:
            raise ValueError("Model does not support feature importance explanation")
    
    def _explain_shap(self, model, input_data, output_data, metadata):
        """
        Generate SHAP explanation.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: SHAP explanation data
        """
        try:
            # Convert input data to appropriate format
            if isinstance(input_data, pd.DataFrame):
                X = input_data
                feature_names = list(X.columns)
            elif isinstance(input_data, dict):
                # Convert dict to DataFrame
                X = pd.DataFrame([input_data])
                feature_names = list(X.columns)
            else:
                X = input_data
                feature_names = metadata.get("feature_names", [f"feature_{i}" for i in range(X.shape[1])])
            
            # Create SHAP explainer based on model type
            if hasattr(model, "predict_proba"):
                # For classifiers
                explainer = shap.Explainer(model)
            else:
                # For regressors and other models
                explainer = shap.Explainer(model)
            
            # Calculate SHAP values
            shap_values = explainer(X)
            
            # Convert to serializable format
            if hasattr(shap_values, "values"):
                values = shap_values.values
            else:
                values = shap_values
                
            # Handle multi-class output
            if len(values.shape) == 3:
                # For multi-class, take the predicted class or the first class
                if output_data is not None and "class_index" in output_data:
                    class_idx = output_data["class_index"]
                    values = values[:, :, class_idx]
                else:
                    values = values[:, :, 0]
            
            # Calculate base value
            if hasattr(shap_values, "base_values"):
                base_values = shap_values.base_values
                if len(base_values.shape) > 1:
                    if output_data is not None and "class_index" in output_data:
                        class_idx = output_data["class_index"]
                        base_values = base_values[:, class_idx]
                    else:
                        base_values = base_values[:, 0]
                base_value = float(base_values[0])
            else:
                base_value = 0.0
            
            # Create explanation data
            shap_data = []
            for i in range(X.shape[0]):
                instance_values = values[i]
                
                # Sort by absolute value
                sorted_idx = np.argsort(np.abs(instance_values))[::-1]
                
                instance_data = {
                    "base_value": base_value,
                    "features": [feature_names[j] for j in sorted_idx],
                    "values": [float(instance_values[j]) for j in sorted_idx],
                    "abs_values": [float(abs(instance_values[j])) for j in sorted_idx]
                }
                
                shap_data.append(instance_data)
            
            # Generate SHAP summary plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X, show=False)
            
            # Save plot to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close()
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            
            return {
                "shap_data": shap_data,
                "summary_plot": plot_data
            }
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate SHAP explanation"
            }
    
    def _explain_lime(self, model, input_data, output_data, metadata):
        """
        Generate LIME explanation.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: LIME explanation data
        """
        try:
            # Determine data type and create appropriate explainer
            if isinstance(input_data, str) or (isinstance(input_data, dict) and "text" in input_data):
                # Text data
                text = input_data if isinstance(input_data, str) else input_data["text"]
                
                # Create text explainer
                explainer = lime_text.LimeTextExplainer(class_names=metadata.get("class_names", ["Class 0", "Class 1"]))
                
                # Create prediction function
                def predict_fn(texts):
                    if hasattr(model, "predict_proba"):
                        return model.predict_proba(texts)
                    else:
                        preds = model.predict(texts)
                        return np.column_stack((1 - preds, preds))
                
                # Generate explanation
                exp = explainer.explain_instance(text, predict_fn, num_features=10)
                
                # Extract explanation data
                explanation_list = exp.as_list()
                
                # Generate HTML
                html_exp = exp.as_html()
                
                return {
                    "type": "text",
                    "explanation": [{"feature": str(f), "weight": float(w)} for f, w in explanation_list],
                    "html": html_exp
                }
                
            elif "image" in metadata or (isinstance(input_data, np.ndarray) and len(input_data.shape) == 3):
                # Image data
                # This is a placeholder - LIME for images requires more complex setup
                return {
                    "type": "image",
                    "message": "LIME for images not implemented in this example"
                }
                
            else:
                # Tabular data
                if isinstance(input_data, pd.DataFrame):
                    X = input_data
                    feature_names = list(X.columns)
                elif isinstance(input_data, dict):
                    # Convert dict to DataFrame
                    X = pd.DataFrame([input_data])
                    feature_names = list(X.columns)
                else:
                    X = input_data
                    feature_names = metadata.get("feature_names", [f"feature_{i}" for i in range(X.shape[1])])
                
                # Get training data if available
                training_data = metadata.get("training_data", X)
                
                # Create tabular explainer
                mode = "classification" if hasattr(model, "predict_proba") else "regression"
                explainer = lime_tabular.LimeTabularExplainer(
                    training_data=training_data,
                    feature_names=feature_names,
                    class_names=metadata.get("class_names", ["Class 0", "Class 1"]),
                    mode=mode
                )
                
                # Generate explanations for each instance
                lime_data = []
                
                for i in range(X.shape[0]):
                    instance = X.iloc[i] if isinstance(X, pd.DataFrame) else X[i]
                    
                    # Generate explanation
                    if mode == "classification":
                        exp = explainer.explain_instance(
                            instance, 
                            model.predict_proba, 
                            num_features=min(10, len(feature_names))
                        )
                        
                        # Get predicted class
                        if output_data is not None and "class_index" in output_data:
                            class_idx = output_data["class_index"]
                        else:
                            class_idx = 1  # Default to positive class
                            
                        # Extract explanation data
                        explanation_list = exp.as_list(label=class_idx)
                        
                    else:
                        exp = explainer.explain_instance(
                            instance, 
                            model.predict, 
                            num_features=min(10, len(feature_names))
                        )
                        
                        # Extract explanation data
                        explanation_list = exp.as_list()
                    
                    # Add to results
                    lime_data.append({
                        "instance_index": i,
                        "explanation": [{"feature": str(f), "weight": float(w)} for f, w in explanation_list]
                    })
                
                return {
                    "type": "tabular",
                    "lime_data": lime_data
                }
                
        except Exception as e:
            logger.error(f"Error generating LIME explanation: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate LIME explanation"
            }
    
    def _explain_decision_path(self, model, input_data, output_data, metadata):
        """
        Generate decision path explanation for tree-based models.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: Decision path explanation data
        """
        # Check if model is tree-based
        if not hasattr(model, "estimators_") and not hasattr(model, "tree_"):
            return {
                "error": "Model is not tree-based",
                "message": "Decision path explanation only works for tree-based models"
            }
            
        try:
            # Convert input data to appropriate format
            if isinstance(input_data, pd.DataFrame):
                X = input_data
                feature_names = list(X.columns)
            elif isinstance(input_data, dict):
                # Convert dict to DataFrame
                X = pd.DataFrame([input_data])
                feature_names = list(X.columns)
            else:
                X = input_data
                feature_names = metadata.get("feature_names", [f"feature_{i}" for i in range(X.shape[1])])
            
            # For random forests and other ensemble models, use the first tree
            if hasattr(model, "estimators_"):
                tree = model.estimators_[0]
            else:
                tree = model
            
            # Get decision path
            decision_paths = tree.decision_path(X)
            
            # Convert to serializable format
            paths = []
            
            for i in range(X.shape[0]):
                # Get the nodes in the decision path
                node_indices = decision_paths[i].indices
                
                # Get the feature and threshold for each node
                path_features = []
                
                for node_id in node_indices:
                    # Skip leaf nodes
                    if tree.tree_.children_left[node_id] == -1:
                        continue
                        
                    # Get feature index and threshold
                    feature_idx = tree.tree_.feature[node_id]
                    threshold = tree.tree_.threshold[node_id]
                    
                    # Get feature name
                    feature_name = feature_names[feature_idx] if feature_idx >= 0 else "Unknown"
                    
                    # Get instance value
                    instance_value = X.iloc[i, feature_idx] if isinstance(X, pd.DataFrame) else X[i, feature_idx]
                    
                    # Determine direction
                    direction = "<=" if instance_value <= threshold else ">"
                    
                    path_features.append({
                        "node_id": int(node_id),
                        "feature": feature_name,
                        "threshold": float(threshold),
                        "value": float(instance_value),
                        "direction": direction
                    })
                
                paths.append({
                    "instance_index": i,
                    "path": path_features
                })
            
            # Generate tree visualization
            plt.figure(figsize=(15, 10))
            plot_tree(tree, feature_names=feature_names, filled=True, rounded=True)
            
            # Save plot to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close()
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            
            return {
                "decision_paths": paths,
                "tree_visualization": plot_data
            }
            
        except Exception as e:
            logger.error(f"Error generating decision path explanation: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate decision path explanation"
            }
    
    def _explain_counterfactual(self, model, input_data, output_data, metadata):
        """
        Generate counterfactual explanation.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: Counterfactual explanation data
        """
        try:
            # This is a simplified implementation of counterfactual explanations
            # A full implementation would use libraries like Alibi or DiCE
            
            # Convert input data to appropriate format
            if isinstance(input_data, pd.DataFrame):
                X = input_data
                feature_names = list(X.columns)
            elif isinstance(input_data, dict):
                # Convert dict to DataFrame
                X = pd.DataFrame([input_data])
                feature_names = list(X.columns)
            else:
                X = input_data
                feature_names = metadata.get("feature_names", [f"feature_{i}" for i in range(X.shape[1])])
            
            # Get feature ranges
            feature_ranges = metadata.get("feature_ranges", {})
            if not feature_ranges:
                # Create default ranges based on data
                for i, feature in enumerate(feature_names):
                    if isinstance(X, pd.DataFrame):
                        values = X[feature].values
                    else:
                        values = X[:, i]
                    
                    feature_ranges[feature] = {
                        "min": float(np.min(values)),
                        "max": float(np.max(values))
                    }
            
            # Get desired outcome
            desired_outcome = metadata.get("desired_outcome")
            if desired_outcome is None:
                # For classification, flip the predicted class
                if hasattr(model, "predict_proba"):
                    current_pred = model.predict(X)[0]
                    desired_outcome = 1 - current_pred
                else:
                    # For regression, increase/decrease by 10%
                    current_pred = model.predict(X)[0]
                    desired_outcome = current_pred * 1.1
            
            # Simple approach: perturb one feature at a time
            counterfactuals = []
            
            for i, feature in enumerate(feature_names):
                # Skip categorical features
                if feature in metadata.get("categorical_features", []):
                    continue
                
                # Get feature range
                feature_range = feature_ranges.get(feature, {"min": 0, "max": 1})
                min_val = feature_range["min"]
                max_val = feature_range["max"]
                
                # Create perturbed instances
                num_steps = 10
                step_size = (max_val - min_val) / num_steps
                
                for step in range(num_steps + 1):
                    # Create a copy of the instance
                    if isinstance(X, pd.DataFrame):
                        perturbed = X.copy()
                        original_value = float(perturbed.iloc[0, i])
                        perturbed.iloc[0, i] = min_val + step * step_size
                        perturbed_value = float(perturbed.iloc[0, i])
                    else:
                        perturbed = X.copy()
                        original_value = float(perturbed[0, i])
                        perturbed[0, i] = min_val + step * step_size
                        perturbed_value = float(perturbed[0, i])
                    
                    # Get prediction
                    if hasattr(model, "predict_proba"):
                        pred = model.predict(perturbed)[0]
                    else:
                        pred = model.predict(perturbed)[0]
                    
                    # Check if prediction matches desired outcome
                    if hasattr(model, "predict_proba"):
                        # For classification
                        if pred == desired_outcome:
                            counterfactuals.append({
                                "feature": feature,
                                "original_value": original_value,
                                "counterfactual_value": perturbed_value,
                                "prediction": float(pred)
                            })
                            break
                    else:
                        # For regression
                        if (desired_outcome > current_pred and pred > desired_outcome) or \
                           (desired_outcome < current_pred and pred < desired_outcome):
                            counterfactuals.append({
                                "feature": feature,
                                "original_value": original_value,
                                "counterfactual_value": perturbed_value,
                                "prediction": float(pred)
                            })
                            break
            
            return {
                "counterfactuals": counterfactuals,
                "desired_outcome": float(desired_outcome) if isinstance(desired_outcome, (int, float)) else desired_outcome
            }
            
        except Exception as e:
            logger.error(f"Error generating counterfactual explanation: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate counterfactual explanation"
            }
    
    def _explain_rule_extraction(self, model, input_data, output_data, metadata):
        """
        Generate rule-based explanation.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: Rule-based explanation data
        """
        try:
            # Convert input data to appropriate format
            if isinstance(input_data, pd.DataFrame):
                X = input_data
                feature_names = list(X.columns)
            elif isinstance(input_data, dict):
                # Convert dict to DataFrame
                X = pd.DataFrame([input_data])
                feature_names = list(X.columns)
            else:
                X = input_data
                feature_names = metadata.get("feature_names", [f"feature_{i}" for i in range(X.shape[1])])
            
            # For tree-based models, extract rules directly
            if hasattr(model, "estimators_") or hasattr(model, "tree_"):
                # Get the tree
                if hasattr(model, "estimators_"):
                    tree = model.estimators_[0]
                else:
                    tree = model
                
                # Get decision path
                decision_paths = tree.decision_path(X)
                
                # Extract rules
                rules = []
                
                for i in range(X.shape[0]):
                    # Get the nodes in the decision path
                    node_indices = decision_paths[i].indices
                    
                    # Build rule
                    rule_conditions = []
                    
                    for node_id in node_indices:
                        # Skip leaf nodes
                        if tree.tree_.children_left[node_id] == -1:
                            continue
                            
                        # Get feature index and threshold
                        feature_idx = tree.tree_.feature[node_id]
                        threshold = tree.tree_.threshold[node_id]
                        
                        # Get feature name
                        feature_name = feature_names[feature_idx] if feature_idx >= 0 else "Unknown"
                        
                        # Get instance value
                        instance_value = X.iloc[i, feature_idx] if isinstance(X, pd.DataFrame) else X[i, feature_idx]
                        
                        # Determine direction
                        if instance_value <= threshold:
                            condition = f"{feature_name} <= {threshold:.4f}"
                        else:
                            condition = f"{feature_name} > {threshold:.4f}"
                        
                        rule_conditions.append(condition)
                    
                    # Get prediction
                    if hasattr(model, "predict_proba"):
                        pred_proba = model.predict_proba(X[i:i+1])[0]
                        pred_class = model.predict(X[i:i+1])[0]
                        
                        prediction = {
                            "class": int(pred_class),
                            "probability": float(pred_proba[pred_class])
                        }
                    else:
                        pred = model.predict(X[i:i+1])[0]
                        prediction = float(pred)
                    
                    rules.append({
                        "instance_index": i,
                        "conditions": rule_conditions,
                        "prediction": prediction
                    })
                
                return {
                    "rules": rules,
                    "model_type": "tree"
                }
                
            else:
                # For other models, use a surrogate model
                # Train a decision tree to approximate the model
                from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
                
                # Get predictions from the original model
                if hasattr(model, "predict_proba"):
                    y_pred = model.predict(X)
                    surrogate = DecisionTreeClassifier(max_depth=5)
                else:
                    y_pred = model.predict(X)
                    surrogate = DecisionTreeRegressor(max_depth=5)
                
                # Train surrogate model
                surrogate.fit(X, y_pred)
                
                # Extract rules from surrogate model
                # This is the same code as above for tree-based models
                decision_paths = surrogate.decision_path(X)
                
                # Extract rules
                rules = []
                
                for i in range(X.shape[0]):
                    # Get the nodes in the decision path
                    node_indices = decision_paths[i].indices
                    
                    # Build rule
                    rule_conditions = []
                    
                    for node_id in node_indices:
                        # Skip leaf nodes
                        if surrogate.tree_.children_left[node_id] == -1:
                            continue
                            
                        # Get feature index and threshold
                        feature_idx = surrogate.tree_.feature[node_id]
                        threshold = surrogate.tree_.threshold[node_id]
                        
                        # Get feature name
                        feature_name = feature_names[feature_idx] if feature_idx >= 0 else "Unknown"
                        
                        # Get instance value
                        instance_value = X.iloc[i, feature_idx] if isinstance(X, pd.DataFrame) else X[i, feature_idx]
                        
                        # Determine direction
                        if instance_value <= threshold:
                            condition = f"{feature_name} <= {threshold:.4f}"
                        else:
                            condition = f"{feature_name} > {threshold:.4f}"
                        
                        rule_conditions.append(condition)
                    
                    # Get prediction
                    if hasattr(model, "predict_proba"):
                        pred_proba = model.predict_proba(X[i:i+1])[0]
                        pred_class = model.predict(X[i:i+1])[0]
                        
                        prediction = {
                            "class": int(pred_class),
                            "probability": float(pred_proba[pred_class])
                        }
                    else:
                        pred = model.predict(X[i:i+1])[0]
                        prediction = float(pred)
                    
                    rules.append({
                        "instance_index": i,
                        "conditions": rule_conditions,
                        "prediction": prediction
                    })
                
                return {
                    "rules": rules,
                    "model_type": "surrogate"
                }
                
        except Exception as e:
            logger.error(f"Error generating rule extraction explanation: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate rule extraction explanation"
            }
    
    def _explain_attention(self, model, input_data, output_data, metadata):
        """
        Generate attention-based explanation for deep learning models.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction
            metadata: Additional metadata
            
        Returns:
            explanation_data: Attention-based explanation data
        """
        # This is a placeholder for attention-based explanations
        # Implementing this properly requires access to the model's attention weights
        
        return {
            "message": "Attention-based explanation requires a model with attention mechanism",
            "attention_weights": None
        }


class ExplanationPresenter:
    """
    Presenter for model explanations.
    
    This class provides methods for formatting and presenting explanations
    in various formats (HTML, JSON, visualizations).
    """
    
    def __init__(self):
        """Initialize the ExplanationPresenter."""
        # Register default formatters
        self.formatters = {
            "feature_importance": self._format_feature_importance,
            "shap": self._format_shap,
            "lime": self._format_lime,
            "decision_path": self._format_decision_path,
            "counterfactual": self._format_counterfactual,
            "rule_extraction": self._format_rule_extraction,
            "attention": self._format_attention
        }
    
    def register_formatter(self, explanation_type: str, formatter_func: Callable):
        """
        Register a custom formatter function.
        
        Args:
            explanation_type: Type of explanation
            formatter_func: Function that takes an explanation and returns formatted output
        """
        self.formatters[explanation_type] = formatter_func
    
    def format_explanation(self, explanation: Explanation, format_type: str = "html") -> str:
        """
        Format an explanation for presentation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format ("html", "json", "text")
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        # Get formatter for this explanation type
        formatter = self.formatters.get(explanation.explanation_type)
        
        if not formatter:
            if format_type == "html":
                return f"<div class='explanation'><h3>Unknown explanation type: {explanation.explanation_type}</h3></div>"
            elif format_type == "json":
                return json.dumps(explanation.explanation_data, indent=2)
            else:
                return f"Unknown explanation type: {explanation.explanation_type}\n{explanation.explanation_data}"
        
        # Format explanation
        return formatter(explanation, format_type)
    
    def _format_feature_importance(self, explanation: Explanation, format_type: str) -> str:
        """
        Format feature importance explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            html = f"""
            <div class="explanation feature-importance">
                <h3>Feature Importance Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                <p>Importance Type: {data.get('importance_type', 'Unknown')}</p>
                
                <div class="feature-importance-chart">
                    <table class="feature-table">
                        <tr>
                            <th>Feature</th>
                            <th>Importance</th>
                            <th>Visualization</th>
                        </tr>
            """
            
            # Add rows for each feature
            max_importance = max(data.get('importance_values', [0.001]))
            
            for i, (feature, importance) in enumerate(zip(data.get('feature_names', []), data.get('importance_values', []))):
                # Calculate bar width as percentage of max
                bar_width = (importance / max_importance) * 100
                
                html += f"""
                <tr>
                    <td>{feature}</td>
                    <td>{importance:.4f}</td>
                    <td>
                        <div class="importance-bar" style="width: {bar_width}%"></div>
                    </td>
                </tr>
                """
            
            html += """
                    </table>
                </div>
            </div>
            <style>
                .feature-importance {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .feature-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .feature-table th, .feature-table td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .importance-bar {
                    background-color: #4CAF50;
                    height: 20px;
                    border-radius: 3px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"Feature Importance Explanation\n"
            text += f"Model ID: {explanation.model_id}\n"
            text += f"Importance Type: {data.get('importance_type', 'Unknown')}\n\n"
            
            text += "Features by importance:\n"
            for feature, importance in zip(data.get('feature_names', []), data.get('importance_values', [])):
                text += f"- {feature}: {importance:.4f}\n"
                
            return text
    
    def _format_shap(self, explanation: Explanation, format_type: str) -> str:
        """
        Format SHAP explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            html = f"""
            <div class="explanation shap">
                <h3>SHAP Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                
                <div class="shap-summary">
                    <h4>SHAP Summary Plot</h4>
                    <img src="data:image/png;base64,{data.get('summary_plot', '')}" alt="SHAP Summary Plot">
                </div>
                
                <div class="shap-values">
                    <h4>SHAP Values</h4>
            """
            
            # Add details for each instance
            for i, instance_data in enumerate(data.get('shap_data', [])):
                html += f"""
                <div class="instance">
                    <h5>Instance {i+1}</h5>
                    <p>Base Value: {instance_data.get('base_value', 0):.4f}</p>
                    
                    <table class="shap-table">
                        <tr>
                            <th>Feature</th>
                            <th>SHAP Value</th>
                            <th>Visualization</th>
                        </tr>
                """
                
                # Add rows for each feature
                features = instance_data.get('features', [])
                values = instance_data.get('values', [])
                abs_values = instance_data.get('abs_values', [])
                
                max_abs_value = max(abs_values) if abs_values else 1.0
                
                for feature, value, abs_value in zip(features, values, abs_values):
                    # Calculate bar width as percentage of max
                    bar_width = (abs_value / max_abs_value) * 100
                    
                    # Determine bar color based on value sign
                    bar_color = "#FF4136" if value < 0 else "#2ECC40"
                    
                    html += f"""
                    <tr>
                        <td>{feature}</td>
                        <td>{value:.4f}</td>
                        <td>
                            <div class="shap-bar" style="width: {bar_width}%; background-color: {bar_color};"></div>
                        </td>
                    </tr>
                    """
                
                html += """
                    </table>
                </div>
                """
            
            html += """
                </div>
            </div>
            <style>
                .shap {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .shap-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                .shap-table th, .shap-table td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .shap-bar {
                    height: 20px;
                    border-radius: 3px;
                }
                .instance {
                    margin-bottom: 30px;
                    padding: 10px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"SHAP Explanation\n"
            text += f"Model ID: {explanation.model_id}\n\n"
            
            for i, instance_data in enumerate(data.get('shap_data', [])):
                text += f"Instance {i+1}\n"
                text += f"Base Value: {instance_data.get('base_value', 0):.4f}\n\n"
                
                text += "Features by SHAP value:\n"
                for feature, value in zip(instance_data.get('features', []), instance_data.get('values', [])):
                    text += f"- {feature}: {value:.4f}\n"
                
                text += "\n"
                
            return text
    
    def _format_lime(self, explanation: Explanation, format_type: str) -> str:
        """
        Format LIME explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            # For text explanations, LIME provides HTML directly
            if data.get('type') == 'text' and 'html' in data:
                return data['html']
            
            # For tabular data
            html = f"""
            <div class="explanation lime">
                <h3>LIME Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                <p>Type: {data.get('type', 'Unknown')}</p>
            """
            
            if data.get('type') == 'tabular':
                html += """
                <div class="lime-values">
                """
                
                # Add details for each instance
                for instance_data in data.get('lime_data', []):
                    html += f"""
                    <div class="instance">
                        <h5>Instance {instance_data.get('instance_index', 0) + 1}</h5>
                        
                        <table class="lime-table">
                            <tr>
                                <th>Feature</th>
                                <th>Weight</th>
                                <th>Visualization</th>
                            </tr>
                    """
                    
                    # Add rows for each feature
                    explanation_list = instance_data.get('explanation', [])
                    
                    # Find max absolute weight
                    max_abs_weight = max([abs(item['weight']) for item in explanation_list]) if explanation_list else 1.0
                    
                    for item in explanation_list:
                        feature = item['feature']
                        weight = item['weight']
                        
                        # Calculate bar width as percentage of max
                        bar_width = (abs(weight) / max_abs_weight) * 100
                        
                        # Determine bar color based on weight sign
                        bar_color = "#FF4136" if weight < 0 else "#2ECC40"
                        
                        html += f"""
                        <tr>
                            <td>{feature}</td>
                            <td>{weight:.4f}</td>
                            <td>
                                <div class="lime-bar" style="width: {bar_width}%; background-color: {bar_color};"></div>
                            </td>
                        </tr>
                        """
                    
                    html += """
                        </table>
                    </div>
                    """
                
                html += """
                </div>
                """
            
            html += """
            </div>
            <style>
                .lime {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .lime-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                .lime-table th, .lime-table td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .lime-bar {
                    height: 20px;
                    border-radius: 3px;
                }
                .instance {
                    margin-bottom: 30px;
                    padding: 10px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"LIME Explanation\n"
            text += f"Model ID: {explanation.model_id}\n"
            text += f"Type: {data.get('type', 'Unknown')}\n\n"
            
            if data.get('type') == 'tabular':
                for instance_data in data.get('lime_data', []):
                    text += f"Instance {instance_data.get('instance_index', 0) + 1}\n\n"
                    
                    text += "Features by weight:\n"
                    for item in instance_data.get('explanation', []):
                        text += f"- {item['feature']}: {item['weight']:.4f}\n"
                    
                    text += "\n"
            
            return text
    
    def _format_decision_path(self, explanation: Explanation, format_type: str) -> str:
        """
        Format decision path explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            html = f"""
            <div class="explanation decision-path">
                <h3>Decision Path Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                
                <div class="tree-visualization">
                    <h4>Tree Visualization</h4>
                    <img src="data:image/png;base64,{data.get('tree_visualization', '')}" alt="Tree Visualization">
                </div>
                
                <div class="decision-paths">
                    <h4>Decision Paths</h4>
            """
            
            # Add details for each instance
            for path_data in data.get('decision_paths', []):
                html += f"""
                <div class="instance">
                    <h5>Instance {path_data.get('instance_index', 0) + 1}</h5>
                    
                    <div class="path-steps">
                        <ol>
                """
                
                # Add steps in the decision path
                for step in path_data.get('path', []):
                    feature = step['feature']
                    threshold = step['threshold']
                    value = step['value']
                    direction = step['direction']
                    
                    html += f"""
                    <li>
                        <strong>{feature}</strong> {direction} {threshold:.4f} (actual value: {value:.4f})
                    </li>
                    """
                
                html += """
                        </ol>
                    </div>
                </div>
                """
            
            html += """
                </div>
            </div>
            <style>
                .decision-path {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .instance {
                    margin-bottom: 30px;
                    padding: 10px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }
                .path-steps ol {
                    margin-top: 10px;
                }
                .path-steps li {
                    margin-bottom: 5px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"Decision Path Explanation\n"
            text += f"Model ID: {explanation.model_id}\n\n"
            
            for path_data in data.get('decision_paths', []):
                text += f"Instance {path_data.get('instance_index', 0) + 1}\n\n"
                
                text += "Decision path:\n"
                for i, step in enumerate(path_data.get('path', [])):
                    feature = step['feature']
                    threshold = step['threshold']
                    value = step['value']
                    direction = step['direction']
                    
                    text += f"{i+1}. {feature} {direction} {threshold:.4f} (actual value: {value:.4f})\n"
                
                text += "\n"
                
            return text
    
    def _format_counterfactual(self, explanation: Explanation, format_type: str) -> str:
        """
        Format counterfactual explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            html = f"""
            <div class="explanation counterfactual">
                <h3>Counterfactual Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                <p>Desired Outcome: {data.get('desired_outcome', 'Unknown')}</p>
                
                <div class="counterfactuals">
                    <h4>Counterfactual Examples</h4>
                    
                    <table class="counterfactual-table">
                        <tr>
                            <th>Feature</th>
                            <th>Original Value</th>
                            <th>Counterfactual Value</th>
                            <th>Change</th>
                            <th>Prediction</th>
                        </tr>
            """
            
            # Add rows for each counterfactual
            for cf in data.get('counterfactuals', []):
                feature = cf['feature']
                original = cf['original_value']
                counterfactual = cf['counterfactual_value']
                prediction = cf['prediction']
                
                # Calculate change
                change = counterfactual - original
                change_pct = (change / original) * 100 if original != 0 else float('inf')
                
                # Determine change direction
                change_class = "increase" if change > 0 else "decrease"
                change_symbol = "↑" if change > 0 else "↓"
                
                html += f"""
                <tr>
                    <td>{feature}</td>
                    <td>{original:.4f}</td>
                    <td>{counterfactual:.4f}</td>
                    <td class="{change_class}">{change_symbol} {abs(change):.4f} ({abs(change_pct):.1f}%)</td>
                    <td>{prediction}</td>
                </tr>
                """
            
            html += """
                    </table>
                </div>
            </div>
            <style>
                .counterfactual {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .counterfactual-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }
                .counterfactual-table th, .counterfactual-table td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .increase {
                    color: #2ECC40;
                }
                .decrease {
                    color: #FF4136;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"Counterfactual Explanation\n"
            text += f"Model ID: {explanation.model_id}\n"
            text += f"Desired Outcome: {data.get('desired_outcome', 'Unknown')}\n\n"
            
            text += "Counterfactual examples:\n"
            for cf in data.get('counterfactuals', []):
                feature = cf['feature']
                original = cf['original_value']
                counterfactual = cf['counterfactual_value']
                prediction = cf['prediction']
                
                # Calculate change
                change = counterfactual - original
                change_pct = (change / original) * 100 if original != 0 else float('inf')
                
                # Determine change direction
                change_symbol = "↑" if change > 0 else "↓"
                
                text += f"- {feature}: {original:.4f} → {counterfactual:.4f} "
                text += f"({change_symbol} {abs(change):.4f}, {abs(change_pct):.1f}%) "
                text += f"→ Prediction: {prediction}\n"
                
            return text
    
    def _format_rule_extraction(self, explanation: Explanation, format_type: str) -> str:
        """
        Format rule extraction explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            html = f"""
            <div class="explanation rule-extraction">
                <h3>Rule Extraction Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                <p>Model Type: {data.get('model_type', 'Unknown')}</p>
                
                <div class="rules">
                    <h4>Extracted Rules</h4>
            """
            
            # Add details for each instance
            for rule_data in data.get('rules', []):
                html += f"""
                <div class="instance">
                    <h5>Instance {rule_data.get('instance_index', 0) + 1}</h5>
                    
                    <div class="rule-conditions">
                        <p><strong>IF</strong></p>
                        <ul>
                """
                
                # Add conditions
                for condition in rule_data.get('conditions', []):
                    html += f"""
                    <li>{condition}</li>
                    """
                
                # Add prediction
                prediction = rule_data.get('prediction', {})
                if isinstance(prediction, dict):
                    pred_class = prediction.get('class', 'Unknown')
                    probability = prediction.get('probability', 0.0)
                    
                    html += f"""
                        </ul>
                        <p><strong>THEN</strong> Class = {pred_class} (Probability: {probability:.4f})</p>
                    </div>
                    """
                else:
                    html += f"""
                        </ul>
                        <p><strong>THEN</strong> Prediction = {prediction:.4f}</p>
                    </div>
                    """
                
                html += """
                </div>
                """
            
            html += """
                </div>
            </div>
            <style>
                .rule-extraction {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .instance {
                    margin-bottom: 30px;
                    padding: 10px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }
                .rule-conditions ul {
                    margin-top: 5px;
                    margin-bottom: 5px;
                }
                .rule-conditions li {
                    margin-bottom: 3px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"Rule Extraction Explanation\n"
            text += f"Model ID: {explanation.model_id}\n"
            text += f"Model Type: {data.get('model_type', 'Unknown')}\n\n"
            
            for rule_data in data.get('rules', []):
                text += f"Instance {rule_data.get('instance_index', 0) + 1}\n\n"
                
                text += "IF\n"
                for condition in rule_data.get('conditions', []):
                    text += f"  {condition}\n"
                
                # Add prediction
                prediction = rule_data.get('prediction', {})
                if isinstance(prediction, dict):
                    pred_class = prediction.get('class', 'Unknown')
                    probability = prediction.get('probability', 0.0)
                    
                    text += f"THEN Class = {pred_class} (Probability: {probability:.4f})\n\n"
                else:
                    text += f"THEN Prediction = {prediction:.4f}\n\n"
                
            return text
    
    def _format_attention(self, explanation: Explanation, format_type: str) -> str:
        """
        Format attention-based explanation.
        
        Args:
            explanation: Explanation to format
            format_type: Type of format
            
        Returns:
            formatted_explanation: Formatted explanation
        """
        data = explanation.explanation_data
        
        if format_type == "html":
            html = f"""
            <div class="explanation attention">
                <h3>Attention-based Explanation</h3>
                <p>Model ID: {explanation.model_id}</p>
                <p>{data.get('message', 'No attention data available')}</p>
            </div>
            <style>
                .attention {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            return json.dumps(data, indent=2)
            
        else:
            # Text format
            text = f"Attention-based Explanation\n"
            text += f"Model ID: {explanation.model_id}\n"
            text += f"{data.get('message', 'No attention data available')}\n"
            
            return text


class ExplainabilityManager:
    """
    Manager for model explainability.
    
    This class coordinates the generation, storage, and presentation of
    explanations for model decisions.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the ExplainabilityManager.
        
        Args:
            storage_path: Path to store explanation data
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # Initialize components
        self.engine = ExplainabilityEngine(storage_path=storage_path)
        self.presenter = ExplanationPresenter()
    
    def explain_prediction(self, 
                          model: Any, 
                          input_data: Any,
                          output_data: Any = None,
                          explanation_types: List[str] = None,
                          model_id: str = None,
                          metadata: Dict[str, Any] = None) -> Dict[str, Explanation]:
        """
        Generate explanations for a model prediction.
        
        Args:
            model: Model to explain
            input_data: Input data for the prediction
            output_data: Output data from the prediction (if available)
            explanation_types: Types of explanations to generate
            model_id: ID of the model
            metadata: Additional metadata for the explanation
            
        Returns:
            explanations: Dictionary of explanations by type
        """
        # Set default explanation types
        if explanation_types is None:
            explanation_types = ["feature_importance", "shap"]
            
        # Generate explanations
        explanations = {}
        
        for explanation_type in explanation_types:
            try:
                explanation = self.engine.explain_prediction(
                    model=model,
                    input_data=input_data,
                    output_data=output_data,
                    explanation_type=explanation_type,
                    model_id=model_id,
                    metadata=metadata
                )
                
                explanations[explanation_type] = explanation
                
            except Exception as e:
                logger.error(f"Error generating {explanation_type} explanation: {e}")
                # Continue with other explanation types
        
        return explanations
    
    def format_explanations(self, 
                           explanations: Dict[str, Explanation], 
                           format_type: str = "html") -> Dict[str, str]:
        """
        Format multiple explanations for presentation.
        
        Args:
            explanations: Dictionary of explanations by type
            format_type: Type of format
            
        Returns:
            formatted_explanations: Dictionary of formatted explanations by type
        """
        formatted = {}
        
        for explanation_type, explanation in explanations.items():
            formatted[explanation_type] = self.presenter.format_explanation(
                explanation=explanation,
                format_type=format_type
            )
            
        return formatted
    
    def get_explanations(self, model_id: str) -> Dict[str, List[Explanation]]:
        """
        Get all explanations for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            explanations: Dictionary of explanations by type
        """
        # Get all explanation files for the model
        if not self.storage_path:
            return {}
            
        model_dir = os.path.join(self.storage_path, model_id)
        if not os.path.exists(model_dir):
            return {}
            
        # Group explanations by type
        explanations = {}
        
        for filename in os.listdir(model_dir):
            if not filename.endswith(".json"):
                continue
                
            # Extract explanation type from filename
            explanation_type = filename.split("_")[0]
            
            # Load explanation
            explanation_file = os.path.join(model_dir, filename)
            
            try:
                explanation = self.engine.load_explanation(explanation_file)
                
                if explanation_type not in explanations:
                    explanations[explanation_type] = []
                    
                explanations[explanation_type].append(explanation)
                
            except Exception as e:
                logger.error(f"Error loading explanation from {explanation_file}: {e}")
        
        return explanations
    
    def generate_explanation_report(self, 
                                  model_id: str, 
                                  format_type: str = "html") -> str:
        """
        Generate a comprehensive explanation report for a model.
        
        Args:
            model_id: ID of the model
            format_type: Type of format
            
        Returns:
            report: Explanation report
        """
        # Get all explanations for the model
        explanations_by_type = self.get_explanations(model_id)
        
        if not explanations_by_type:
            if format_type == "html":
                return f"<div class='report'><h2>No explanations found for model {model_id}</h2></div>"
            else:
                return f"No explanations found for model {model_id}"
        
        # Format explanations
        if format_type == "html":
            html = f"""
            <div class="explanation-report">
                <h2>Explanation Report for Model {model_id}</h2>
                
                <div class="toc">
                    <h3>Table of Contents</h3>
                    <ul>
            """
            
            # Add TOC entries
            for explanation_type in explanations_by_type.keys():
                html += f"""
                <li><a href="#{explanation_type}">{explanation_type.replace('_', ' ').title()} Explanations</a></li>
                """
            
            html += """
                    </ul>
                </div>
            """
            
            # Add sections for each explanation type
            for explanation_type, explanations in explanations_by_type.items():
                html += f"""
                <div id="{explanation_type}" class="explanation-section">
                    <h3>{explanation_type.replace('_', ' ').title()} Explanations</h3>
                """
                
                # Add the most recent explanation
                latest_explanation = max(explanations, key=lambda e: e.timestamp)
                
                html += self.presenter.format_explanation(
                    explanation=latest_explanation,
                    format_type=format_type
                )
                
                html += """
                </div>
                """
            
            html += """
            </div>
            <style>
                .explanation-report {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 15px;
                }
                .toc {
                    margin-bottom: 30px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .explanation-section {
                    margin-bottom: 40px;
                }
            </style>
            """
            
            return html
            
        elif format_type == "json":
            # Create a dictionary of the latest explanation for each type
            latest_explanations = {}
            
            for explanation_type, explanations in explanations_by_type.items():
                latest_explanation = max(explanations, key=lambda e: e.timestamp)
                
                # Convert explanation to dict
                latest_explanations[explanation_type] = {
                    "model_id": latest_explanation.model_id,
                    "explanation_type": latest_explanation.explanation_type,
                    "explanation_data": latest_explanation.explanation_data,
                    "input_data": latest_explanation.input_data,
                    "output_data": latest_explanation.output_data,
                    "timestamp": latest_explanation.timestamp,
                    "metadata": latest_explanation.metadata
                }
            
            return json.dumps(latest_explanations, indent=2)
            
        else:
            # Text format
            text = f"Explanation Report for Model {model_id}\n\n"
            
            for explanation_type, explanations in explanations_by_type.items():
                text += f"{explanation_type.replace('_', ' ').title()} Explanations\n"
                text += "=" * len(f"{explanation_type.replace('_', ' ').title()} Explanations") + "\n\n"
                
                # Add the most recent explanation
                latest_explanation = max(explanations, key=lambda e: e.timestamp)
                
                text += self.presenter.format_explanation(
                    explanation=latest_explanation,
                    format_type=format_type
                )
                
                text += "\n\n"
                
            return text
