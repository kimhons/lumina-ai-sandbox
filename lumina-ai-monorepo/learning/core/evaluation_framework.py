"""
Evaluation Framework for Lumina AI Enhanced Learning System

This module provides a comprehensive framework for evaluating the performance
of machine learning models in the Enhanced Learning System.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass
import os
import json
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)
from sklearn.model_selection import (
    cross_val_score, KFold, StratifiedKFold, 
    train_test_split, GridSearchCV, RandomizedSearchCV
)
import matplotlib.pyplot as plt
from datetime import datetime


@dataclass
class EvaluationResult:
    """Results of a model evaluation."""
    model_id: str
    dataset_id: str
    metrics: Dict[str, float]
    detailed_metrics: Dict[str, Any]
    timestamp: str
    parameters: Dict[str, Any]
    evaluation_type: str  # "train", "validation", "test", "cross_validation"


class EvaluationFramework:
    """
    Framework for evaluating machine learning models.
    
    The EvaluationFramework handles:
    - Metric definition and calculation
    - Cross-validation implementation
    - A/B testing framework
    - Performance monitoring and alerting
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the EvaluationFramework.
        
        Args:
            storage_path: Path to store evaluation results
        """
        self.storage_path = storage_path
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
        
        # Default metrics for different tasks
        self.classification_metrics = {
            "accuracy": accuracy_score,
            "precision": lambda y_true, y_pred: precision_score(y_true, y_pred, average='weighted'),
            "recall": lambda y_true, y_pred: recall_score(y_true, y_pred, average='weighted'),
            "f1": lambda y_true, y_pred: f1_score(y_true, y_pred, average='weighted')
        }
        
        self.regression_metrics = {
            "mse": mean_squared_error,
            "rmse": lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
            "mae": mean_absolute_error,
            "r2": r2_score
        }
        
        # Custom metrics registry
        self.custom_metrics = {}
    
    def add_custom_metric(self, name: str, metric_func: Callable):
        """
        Add a custom metric to the framework.
        
        Args:
            name: Name of the metric
            metric_func: Function that takes y_true and y_pred and returns a score
        """
        self.custom_metrics[name] = metric_func
    
    def evaluate_model(self, 
                      model: Any, 
                      X: np.ndarray, 
                      y: np.ndarray, 
                      task_type: str = "classification",
                      metrics: List[str] = None,
                      model_id: str = None,
                      dataset_id: str = None,
                      parameters: Dict[str, Any] = None,
                      evaluation_type: str = "test") -> EvaluationResult:
        """
        Evaluate a model on a dataset.
        
        Args:
            model: Model to evaluate (must have a predict method)
            X: Input features
            y: Target values
            task_type: Type of task ("classification" or "regression")
            metrics: List of metric names to calculate
            model_id: ID of the model
            dataset_id: ID of the dataset
            parameters: Additional parameters for the evaluation
            evaluation_type: Type of evaluation
            
        Returns:
            result: Evaluation result
        """
        # Generate IDs if not provided
        if model_id is None:
            model_id = f"model_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if dataset_id is None:
            dataset_id = f"dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get predictions
        y_pred = model.predict(X)
        
        # Select metrics based on task type
        if metrics is None:
            if task_type == "classification":
                metrics = list(self.classification_metrics.keys())
            else:
                metrics = list(self.regression_metrics.keys())
        
        # Calculate metrics
        metric_results = {}
        detailed_metrics = {}
        
        for metric_name in metrics:
            if metric_name in self.classification_metrics and task_type == "classification":
                metric_func = self.classification_metrics[metric_name]
                metric_results[metric_name] = metric_func(y, y_pred)
            elif metric_name in self.regression_metrics and task_type == "regression":
                metric_func = self.regression_metrics[metric_name]
                metric_results[metric_name] = metric_func(y, y_pred)
            elif metric_name in self.custom_metrics:
                metric_func = self.custom_metrics[metric_name]
                metric_results[metric_name] = metric_func(y, y_pred)
            else:
                raise ValueError(f"Unknown metric: {metric_name} for task type: {task_type}")
        
        # Calculate detailed metrics
        if task_type == "classification":
            # Check if model has predict_proba method for ROC AUC
            if hasattr(model, "predict_proba"):
                try:
                    y_prob = model.predict_proba(X)
                    # For binary classification
                    if y_prob.shape[1] == 2:
                        fpr, tpr, _ = roc_curve(y, y_prob[:, 1])
                        detailed_metrics["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
                        detailed_metrics["roc_auc"] = roc_auc_score(y, y_prob[:, 1])
                        
                        precision, recall, _ = precision_recall_curve(y, y_prob[:, 1])
                        detailed_metrics["pr_curve"] = {"precision": precision.tolist(), "recall": recall.tolist()}
                except:
                    pass
            
            # Confusion matrix
            cm = confusion_matrix(y, y_pred)
            detailed_metrics["confusion_matrix"] = cm.tolist()
            
            # Classification report
            try:
                report = classification_report(y, y_pred, output_dict=True)
                detailed_metrics["classification_report"] = report
            except:
                pass
        
        elif task_type == "regression":
            # Residuals
            residuals = y - y_pred
            detailed_metrics["residuals"] = {
                "mean": float(np.mean(residuals)),
                "std": float(np.std(residuals)),
                "min": float(np.min(residuals)),
                "max": float(np.max(residuals))
            }
            
            # R-squared
            detailed_metrics["r2"] = float(r2_score(y, y_pred))
            
            # Explained variance
            from sklearn.metrics import explained_variance_score
            detailed_metrics["explained_variance"] = float(explained_variance_score(y, y_pred))
        
        # Create evaluation result
        result = EvaluationResult(
            model_id=model_id,
            dataset_id=dataset_id,
            metrics=metric_results,
            detailed_metrics=detailed_metrics,
            timestamp=datetime.now().isoformat(),
            parameters=parameters or {},
            evaluation_type=evaluation_type
        )
        
        # Save result if storage path is provided
        if self.storage_path:
            self._save_result(result)
        
        return result
    
    def cross_validate(self,
                      model: Any,
                      X: np.ndarray,
                      y: np.ndarray,
                      task_type: str = "classification",
                      metrics: List[str] = None,
                      cv: int = 5,
                      stratified: bool = True,
                      model_id: str = None,
                      dataset_id: str = None,
                      parameters: Dict[str, Any] = None) -> EvaluationResult:
        """
        Perform cross-validation on a model.
        
        Args:
            model: Model to evaluate (must have a fit and predict method)
            X: Input features
            y: Target values
            task_type: Type of task ("classification" or "regression")
            metrics: List of metric names to calculate
            cv: Number of cross-validation folds
            stratified: Whether to use stratified folds for classification
            model_id: ID of the model
            dataset_id: ID of the dataset
            parameters: Additional parameters for the evaluation
            
        Returns:
            result: Evaluation result with cross-validation metrics
        """
        # Generate IDs if not provided
        if model_id is None:
            model_id = f"model_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if dataset_id is None:
            dataset_id = f"dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Select metrics based on task type
        if metrics is None:
            if task_type == "classification":
                metrics = list(self.classification_metrics.keys())
            else:
                metrics = list(self.regression_metrics.keys())
        
        # Create cross-validation splitter
        if task_type == "classification" and stratified:
            cv_splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        else:
            cv_splitter = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Perform cross-validation
        fold_results = []
        for fold, (train_idx, test_idx) in enumerate(cv_splitter.split(X, y)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Clone the model to avoid fitting the same model multiple times
            from sklearn.base import clone
            fold_model = clone(model)
            
            # Fit and evaluate the model
            fold_model.fit(X_train, y_train)
            fold_result = self.evaluate_model(
                model=fold_model,
                X=X_test,
                y=y_test,
                task_type=task_type,
                metrics=metrics,
                model_id=f"{model_id}_fold{fold}",
                dataset_id=dataset_id,
                parameters=parameters,
                evaluation_type=f"cv_fold{fold}"
            )
            
            fold_results.append(fold_result)
        
        # Aggregate results across folds
        aggregated_metrics = {}
        for metric in metrics:
            values = [result.metrics[metric] for result in fold_results]
            aggregated_metrics[metric] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "values": values
            }
        
        # Create overall result
        result = EvaluationResult(
            model_id=model_id,
            dataset_id=dataset_id,
            metrics={k: v["mean"] for k, v in aggregated_metrics.items()},
            detailed_metrics={
                "cross_validation": aggregated_metrics,
                "folds": [
                    {
                        "fold": i,
                        "metrics": r.metrics,
                        "detailed_metrics": r.detailed_metrics
                    } for i, r in enumerate(fold_results)
                ]
            },
            timestamp=datetime.now().isoformat(),
            parameters=parameters or {},
            evaluation_type="cross_validation"
        )
        
        # Save result if storage path is provided
        if self.storage_path:
            self._save_result(result)
        
        return result
    
    def hyperparameter_search(self,
                             model_class: Any,
                             param_grid: Dict[str, List[Any]],
                             X: np.ndarray,
                             y: np.ndarray,
                             task_type: str = "classification",
                             metrics: List[str] = None,
                             cv: int = 5,
                             stratified: bool = True,
                             n_jobs: int = -1,
                             randomized: bool = False,
                             n_iter: int = 10,
                             model_id: str = None,
                             dataset_id: str = None) -> Tuple[Any, EvaluationResult]:
        """
        Perform hyperparameter search for a model.
        
        Args:
            model_class: Model class to evaluate
            param_grid: Grid of parameters to search
            X: Input features
            y: Target values
            task_type: Type of task ("classification" or "regression")
            metrics: List of metric names to calculate
            cv: Number of cross-validation folds
            stratified: Whether to use stratified folds for classification
            n_jobs: Number of parallel jobs
            randomized: Whether to use randomized search instead of grid search
            n_iter: Number of iterations for randomized search
            model_id: ID of the model
            dataset_id: ID of the dataset
            
        Returns:
            best_model: Best model found
            result: Evaluation result for the best model
        """
        # Generate IDs if not provided
        if model_id is None:
            model_id = f"model_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if dataset_id is None:
            dataset_id = f"dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Select primary metric based on task type
        if metrics is None:
            if task_type == "classification":
                primary_metric = "accuracy"
                metrics = list(self.classification_metrics.keys())
            else:
                primary_metric = "r2"
                metrics = list(self.regression_metrics.keys())
        else:
            primary_metric = metrics[0]
        
        # Create cross-validation splitter
        if task_type == "classification" and stratified:
            cv_splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        else:
            cv_splitter = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Create base model
        base_model = model_class()
        
        # Create search object
        if randomized:
            search = RandomizedSearchCV(
                base_model,
                param_distributions=param_grid,
                n_iter=n_iter,
                scoring=primary_metric,
                cv=cv_splitter,
                n_jobs=n_jobs,
                verbose=1,
                return_train_score=True
            )
        else:
            search = GridSearchCV(
                base_model,
                param_grid=param_grid,
                scoring=primary_metric,
                cv=cv_splitter,
                n_jobs=n_jobs,
                verbose=1,
                return_train_score=True
            )
        
        # Perform search
        search.fit(X, y)
        
        # Get best model
        best_model = search.best_estimator_
        
        # Evaluate best model
        result = self.cross_validate(
            model=best_model,
            X=X,
            y=y,
            task_type=task_type,
            metrics=metrics,
            cv=cv,
            stratified=stratified,
            model_id=model_id,
            dataset_id=dataset_id,
            parameters={
                "best_params": search.best_params_,
                "search_results": {
                    "best_score": search.best_score_,
                    "best_index": search.best_index_,
                    "best_params": search.best_params_,
                    "cv_results": {
                        k: v.tolist() if isinstance(v, np.ndarray) else v
                        for k, v in search.cv_results_.items()
                    }
                }
            }
        )
        
        return best_model, result
    
    def ab_test(self,
               model_a: Any,
               model_b: Any,
               X: np.ndarray,
               y: np.ndarray,
               task_type: str = "classification",
               metrics: List[str] = None,
               n_trials: int = 100,
               test_size: float = 0.3,
               model_a_id: str = None,
               model_b_id: str = None,
               dataset_id: str = None) -> Dict[str, Any]:
        """
        Perform A/B testing between two models.
        
        Args:
            model_a: First model to evaluate
            model_b: Second model to evaluate
            X: Input features
            y: Target values
            task_type: Type of task ("classification" or "regression")
            metrics: List of metric names to calculate
            n_trials: Number of trials for the test
            test_size: Size of the test set for each trial
            model_a_id: ID of the first model
            model_b_id: ID of the second model
            dataset_id: ID of the dataset
            
        Returns:
            result: A/B test results
        """
        # Generate IDs if not provided
        if model_a_id is None:
            model_a_id = f"model_a_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if model_b_id is None:
            model_b_id = f"model_b_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if dataset_id is None:
            dataset_id = f"dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Select metrics based on task type
        if metrics is None:
            if task_type == "classification":
                metrics = list(self.classification_metrics.keys())
            else:
                metrics = list(self.regression_metrics.keys())
        
        # Perform trials
        results_a = []
        results_b = []
        
        for trial in range(n_trials):
            # Split data for this trial
            if task_type == "classification":
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, stratify=y, random_state=trial
                )
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=trial
                )
            
            # Evaluate model A
            result_a = self.evaluate_model(
                model=model_a,
                X=X_test,
                y=y_test,
                task_type=task_type,
                metrics=metrics,
                model_id=f"{model_a_id}_trial{trial}",
                dataset_id=dataset_id,
                parameters={"trial": trial},
                evaluation_type=f"ab_test_a_trial{trial}"
            )
            
            # Evaluate model B
            result_b = self.evaluate_model(
                model=model_b,
                X=X_test,
                y=y_test,
                task_type=task_type,
                metrics=metrics,
                model_id=f"{model_b_id}_trial{trial}",
                dataset_id=dataset_id,
                parameters={"trial": trial},
                evaluation_type=f"ab_test_b_trial{trial}"
            )
            
            results_a.append(result_a)
            results_b.append(result_b)
        
        # Analyze results
        comparison = {}
        for metric in metrics:
            values_a = [r.metrics[metric] for r in results_a]
            values_b = [r.metrics[metric] for r in results_b]
            
            # Perform t-test
            from scipy import stats
            t_stat, p_value = stats.ttest_ind(values_a, values_b)
            
            # Determine winner
            mean_a = np.mean(values_a)
            mean_b = np.mean(values_b)
            
            if p_value < 0.05:
                if mean_a > mean_b:
                    winner = "A"
                else:
                    winner = "B"
            else:
                winner = "Tie"
            
            comparison[metric] = {
                "model_a": {
                    "mean": float(mean_a),
                    "std": float(np.std(values_a)),
                    "values": values_a
                },
                "model_b": {
                    "mean": float(mean_b),
                    "std": float(np.std(values_b)),
                    "values": values_b
                },
                "t_test": {
                    "t_stat": float(t_stat),
                    "p_value": float(p_value)
                },
                "winner": winner
            }
        
        # Create overall result
        result = {
            "model_a_id": model_a_id,
            "model_b_id": model_b_id,
            "dataset_id": dataset_id,
            "metrics": comparison,
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "n_trials": n_trials,
                "test_size": test_size,
                "task_type": task_type
            },
            "evaluation_type": "ab_test"
        }
        
        # Save result if storage path is provided
        if self.storage_path:
            ab_test_path = os.path.join(self.storage_path, f"ab_test_{model_a_id}_{model_b_id}.json")
            with open(ab_test_path, 'w') as f:
                json.dump(result, f, indent=2)
        
        return result
    
    def _save_result(self, result: EvaluationResult):
        """
        Save evaluation result to storage.
        
        Args:
            result: Evaluation result to save
        """
        if not self.storage_path:
            return
            
        # Create result directory
        result_dir = os.path.join(self.storage_path, result.model_id)
        os.makedirs(result_dir, exist_ok=True)
        
        # Save result as JSON
        result_path = os.path.join(
            result_dir, 
            f"{result.evaluation_type}_{result.dataset_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )
        
        with open(result_path, 'w') as f:
            # Convert dataclass to dict
            result_dict = {
                "model_id": result.model_id,
                "dataset_id": result.dataset_id,
                "metrics": result.metrics,
                "detailed_metrics": result.detailed_metrics,
                "timestamp": result.timestamp,
                "parameters": result.parameters,
                "evaluation_type": result.evaluation_type
            }
            json.dump(result_dict, f, indent=2)
    
    def load_result(self, result_path: str) -> EvaluationResult:
        """
        Load evaluation result from file.
        
        Args:
            result_path: Path to the result file
            
        Returns:
            result: Loaded evaluation result
        """
        with open(result_path, 'r') as f:
            result_dict = json.load(f)
            
        return EvaluationResult(
            model_id=result_dict["model_id"],
            dataset_id=result_dict["dataset_id"],
            metrics=result_dict["metrics"],
            detailed_metrics=result_dict["detailed_metrics"],
            timestamp=result_dict["timestamp"],
            parameters=result_dict["parameters"],
            evaluation_type=result_dict["evaluation_type"]
        )
    
    def get_results_for_model(self, model_id: str) -> List[EvaluationResult]:
        """
        Get all evaluation results for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            results: List of evaluation results
        """
        if not self.storage_path:
            return []
            
        result_dir = os.path.join(self.storage_path, model_id)
        if not os.path.exists(result_dir):
            return []
            
        results = []
        for filename in os.listdir(result_dir):
            if filename.endswith(".json"):
                result_path = os.path.join(result_dir, filename)
                results.append(self.load_result(result_path))
                
        return results
    
    def plot_metrics(self, results: List[EvaluationResult], metrics: List[str] = None, 
                    title: str = None, figsize: Tuple[int, int] = (10, 6)):
        """
        Plot metrics from evaluation results.
        
        Args:
            results: List of evaluation results
            metrics: List of metrics to plot (if None, plot all metrics)
            title: Title for the plot
            figsize: Figure size
            
        Returns:
            fig: Matplotlib figure
        """
        if not results:
            raise ValueError("No results to plot")
            
        # Get all metrics if not specified
        if metrics is None:
            metrics = set()
            for result in results:
                metrics.update(result.metrics.keys())
            metrics = list(metrics)
        
        # Create figure
        fig, axes = plt.subplots(len(metrics), 1, figsize=figsize)
        if len(metrics) == 1:
            axes = [axes]
        
        # Plot each metric
        for i, metric in enumerate(metrics):
            ax = axes[i]
            
            # Collect values and labels
            values = []
            labels = []
            
            for result in results:
                if metric in result.metrics:
                    values.append(result.metrics[metric])
                    labels.append(f"{result.model_id} ({result.evaluation_type})")
            
            # Plot values
            ax.bar(range(len(values)), values)
            ax.set_xticks(range(len(values)))
            ax.set_xticklabels(labels, rotation=45, ha="right")
            ax.set_ylabel(metric)
            ax.set_title(f"{metric} comparison")
            
            # Add values on top of bars
            for j, v in enumerate(values):
                ax.text(j, v, f"{v:.4f}", ha="center", va="bottom")
        
        # Set overall title
        if title:
            fig.suptitle(title)
            
        fig.tight_layout()
        
        return fig
    
    def plot_confusion_matrix(self, result: EvaluationResult, class_names: List[str] = None,
                             figsize: Tuple[int, int] = (8, 6), title: str = None):
        """
        Plot confusion matrix from evaluation result.
        
        Args:
            result: Evaluation result
            class_names: Names of the classes
            figsize: Figure size
            title: Title for the plot
            
        Returns:
            fig: Matplotlib figure
        """
        if "confusion_matrix" not in result.detailed_metrics:
            raise ValueError("Evaluation result does not contain confusion matrix")
            
        cm = np.array(result.detailed_metrics["confusion_matrix"])
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot confusion matrix
        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax)
        
        # Set labels
        if class_names:
            ax.set_xticks(np.arange(len(class_names)))
            ax.set_yticks(np.arange(len(class_names)))
            ax.set_xticklabels(class_names)
            ax.set_yticklabels(class_names)
        else:
            ax.set_xticks(np.arange(cm.shape[1]))
            ax.set_yticks(np.arange(cm.shape[0]))
            ax.set_xticklabels(np.arange(cm.shape[1]))
            ax.set_yticklabels(np.arange(cm.shape[0]))
        
        # Rotate tick labels and set alignment
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Loop over data dimensions and create text annotations
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black")
        
        # Set title and labels
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Confusion Matrix for {result.model_id}")
        ax.set_ylabel('True label')
        ax.set_xlabel('Predicted label')
        
        fig.tight_layout()
        
        return fig
    
    def plot_roc_curve(self, result: EvaluationResult, figsize: Tuple[int, int] = (8, 6), title: str = None):
        """
        Plot ROC curve from evaluation result.
        
        Args:
            result: Evaluation result
            figsize: Figure size
            title: Title for the plot
            
        Returns:
            fig: Matplotlib figure
        """
        if "roc_curve" not in result.detailed_metrics:
            raise ValueError("Evaluation result does not contain ROC curve data")
            
        fpr = np.array(result.detailed_metrics["roc_curve"]["fpr"])
        tpr = np.array(result.detailed_metrics["roc_curve"]["tpr"])
        roc_auc = result.detailed_metrics["roc_auc"]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot ROC curve
        ax.plot(fpr, tpr, lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], 'k--', lw=2)
        
        # Set labels and title
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'ROC Curve for {result.model_id}')
        ax.legend(loc="lower right")
        
        fig.tight_layout()
        
        return fig
    
    def plot_precision_recall_curve(self, result: EvaluationResult, figsize: Tuple[int, int] = (8, 6), title: str = None):
        """
        Plot precision-recall curve from evaluation result.
        
        Args:
            result: Evaluation result
            figsize: Figure size
            title: Title for the plot
            
        Returns:
            fig: Matplotlib figure
        """
        if "pr_curve" not in result.detailed_metrics:
            raise ValueError("Evaluation result does not contain precision-recall curve data")
            
        precision = np.array(result.detailed_metrics["pr_curve"]["precision"])
        recall = np.array(result.detailed_metrics["pr_curve"]["recall"])
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot precision-recall curve
        ax.plot(recall, precision, lw=2)
        
        # Set labels and title
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'Precision-Recall Curve for {result.model_id}')
        
        fig.tight_layout()
        
        return fig
    
    def plot_residuals(self, result: EvaluationResult, figsize: Tuple[int, int] = (8, 6), title: str = None):
        """
        Plot residuals from evaluation result.
        
        Args:
            result: Evaluation result
            figsize: Figure size
            title: Title for the plot
            
        Returns:
            fig: Matplotlib figure
        """
        if "residuals" not in result.detailed_metrics:
            raise ValueError("Evaluation result does not contain residuals data")
            
        residuals = result.detailed_metrics["residuals"]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot residuals statistics
        labels = ["Mean", "Std", "Min", "Max"]
        values = [residuals["mean"], residuals["std"], residuals["min"], residuals["max"]]
        
        ax.bar(labels, values)
        
        # Add values on top of bars
        for i, v in enumerate(values):
            ax.text(i, v, f"{v:.4f}", ha="center", va="bottom" if v >= 0 else "top")
        
        # Set labels and title
        ax.set_ylabel('Value')
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f'Residuals Statistics for {result.model_id}')
        
        fig.tight_layout()
        
        return fig
    
    def generate_report(self, result: EvaluationResult, output_path: str = None):
        """
        Generate a comprehensive evaluation report.
        
        Args:
            result: Evaluation result
            output_path: Path to save the report (if None, return HTML string)
            
        Returns:
            report: HTML report string (if output_path is None)
        """
        try:
            import pandas as pd
            from IPython.display import HTML
        except ImportError:
            raise ImportError("pandas and IPython are required for report generation")
        
        # Create report HTML
        html = f"""
        <html>
        <head>
            <title>Model Evaluation Report: {result.model_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .metric-good {{ color: green; }}
                .metric-bad {{ color: red; }}
                .container {{ margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <h1>Model Evaluation Report</h1>
            
            <div class="container">
                <h2>Overview</h2>
                <table>
                    <tr><th>Model ID</th><td>{result.model_id}</td></tr>
                    <tr><th>Dataset ID</th><td>{result.dataset_id}</td></tr>
                    <tr><th>Evaluation Type</th><td>{result.evaluation_type}</td></tr>
                    <tr><th>Timestamp</th><td>{result.timestamp}</td></tr>
                </table>
            </div>
            
            <div class="container">
                <h2>Performance Metrics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
        """
        
        # Add metrics
        for metric, value in result.metrics.items():
            html += f"<tr><td>{metric}</td><td>{value:.4f}</td></tr>"
        
        html += """
                </table>
            </div>
        """
        
        # Add detailed metrics based on evaluation type
        if result.evaluation_type == "cross_validation":
            html += """
            <div class="container">
                <h2>Cross-Validation Results</h2>
                <table>
                    <tr><th>Metric</th><th>Mean</th><th>Std</th><th>Min</th><th>Max</th></tr>
            """
            
            for metric, values in result.detailed_metrics["cross_validation"].items():
                html += f"""
                <tr>
                    <td>{metric}</td>
                    <td>{values["mean"]:.4f}</td>
                    <td>{values["std"]:.4f}</td>
                    <td>{values["min"]:.4f}</td>
                    <td>{values["max"]:.4f}</td>
                </tr>
                """
            
            html += """
                </table>
            </div>
            """
        
        # Add confusion matrix for classification
        if "confusion_matrix" in result.detailed_metrics:
            cm = np.array(result.detailed_metrics["confusion_matrix"])
            
            html += """
            <div class="container">
                <h2>Confusion Matrix</h2>
                <table>
            """
            
            # Add header row
            html += "<tr><th></th>"
            for i in range(cm.shape[1]):
                html += f"<th>Predicted {i}</th>"
            html += "</tr>"
            
            # Add data rows
            for i in range(cm.shape[0]):
                html += f"<tr><th>Actual {i}</th>"
                for j in range(cm.shape[1]):
                    html += f"<td>{cm[i, j]}</td>"
                html += "</tr>"
            
            html += """
                </table>
            </div>
            """
        
        # Add classification report
        if "classification_report" in result.detailed_metrics:
            report = result.detailed_metrics["classification_report"]
            
            html += """
            <div class="container">
                <h2>Classification Report</h2>
                <table>
                    <tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1-score</th><th>Support</th></tr>
            """
            
            for class_name, metrics in report.items():
                if class_name in ["accuracy", "macro avg", "weighted avg"]:
                    continue
                
                html += f"""
                <tr>
                    <td>{class_name}</td>
                    <td>{metrics["precision"]:.4f}</td>
                    <td>{metrics["recall"]:.4f}</td>
                    <td>{metrics["f1-score"]:.4f}</td>
                    <td>{metrics["support"]}</td>
                </tr>
                """
            
            # Add summary rows
            for avg_type in ["macro avg", "weighted avg"]:
                if avg_type in report:
                    html += f"""
                    <tr>
                        <th>{avg_type}</th>
                        <td>{report[avg_type]["precision"]:.4f}</td>
                        <td>{report[avg_type]["recall"]:.4f}</td>
                        <td>{report[avg_type]["f1-score"]:.4f}</td>
                        <td>{report[avg_type]["support"]}</td>
                    </tr>
                    """
            
            # Add accuracy
            if "accuracy" in report:
                html += f"""
                <tr>
                    <th>Accuracy</th>
                    <td colspan="3">{report["accuracy"]:.4f}</td>
                    <td>{report["macro avg"]["support"] if "macro avg" in report else ""}</td>
                </tr>
                """
            
            html += """
                </table>
            </div>
            """
        
        # Add residuals for regression
        if "residuals" in result.detailed_metrics:
            residuals = result.detailed_metrics["residuals"]
            
            html += """
            <div class="container">
                <h2>Residuals Statistics</h2>
                <table>
                    <tr><th>Statistic</th><th>Value</th></tr>
            """
            
            for stat, value in residuals.items():
                html += f"<tr><td>{stat.capitalize()}</td><td>{value:.4f}</td></tr>"
            
            html += """
                </table>
            </div>
            """
        
        # Add parameters
        if result.parameters:
            html += """
            <div class="container">
                <h2>Parameters</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th></tr>
            """
            
            for param, value in result.parameters.items():
                if isinstance(value, dict) and len(value) > 10:
                    # For large nested dictionaries, just show a summary
                    html += f"<tr><td>{param}</td><td>{len(value)} items</td></tr>"
                else:
                    html += f"<tr><td>{param}</td><td>{value}</td></tr>"
            
            html += """
                </table>
            </div>
            """
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        # Save or return HTML
        if output_path:
            with open(output_path, 'w') as f:
                f.write(html)
        else:
            return html
