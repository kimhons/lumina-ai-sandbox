"""
Privacy Layer for Lumina AI Enhanced Learning System

This module provides privacy-preserving features to protect user data during
the learning process, including differential privacy, federated learning,
secure aggregation, and privacy-preserving data transformations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
import os
import json
import datetime
import uuid
import logging
import hashlib
import pickle
import base64
import random
import math
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import io

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DifferentialPrivacy:
    """
    Implementation of differential privacy techniques.
    
    This class provides methods for adding noise to data and queries to
    protect individual privacy while allowing useful aggregate analysis.
    """
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Initialize the DifferentialPrivacy module.
        
        Args:
            epsilon: Privacy parameter (smaller = more privacy)
            delta: Probability of privacy failure
        """
        self.epsilon = epsilon
        self.delta = delta
        
        # Track privacy budget usage
        self.budget_used = 0.0
        self.queries = []
    
    def add_laplace_noise(self, data: Union[float, np.ndarray], sensitivity: float) -> Union[float, np.ndarray]:
        """
        Add Laplace noise to numeric data.
        
        Args:
            data: Original data (scalar or array)
            sensitivity: Maximum change in function output when one record changes
            
        Returns:
            noisy_data: Data with Laplace noise added
        """
        # Calculate scale parameter
        scale = sensitivity / self.epsilon
        
        # Generate noise
        if isinstance(data, np.ndarray):
            noise = np.random.laplace(0, scale, data.shape)
        else:
            noise = np.random.laplace(0, scale)
        
        # Add noise to data
        noisy_data = data + noise
        
        # Track budget usage
        self.budget_used += 1.0
        self.queries.append({
            "type": "laplace",
            "sensitivity": sensitivity,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return noisy_data
    
    def add_gaussian_noise(self, data: Union[float, np.ndarray], sensitivity: float) -> Union[float, np.ndarray]:
        """
        Add Gaussian noise to numeric data.
        
        Args:
            data: Original data (scalar or array)
            sensitivity: Maximum change in function output when one record changes
            
        Returns:
            noisy_data: Data with Gaussian noise added
        """
        # Calculate standard deviation
        c = np.sqrt(2 * np.log(1.25 / self.delta))
        sigma = c * sensitivity / self.epsilon
        
        # Generate noise
        if isinstance(data, np.ndarray):
            noise = np.random.normal(0, sigma, data.shape)
        else:
            noise = np.random.normal(0, sigma)
        
        # Add noise to data
        noisy_data = data + noise
        
        # Track budget usage
        self.budget_used += 1.0
        self.queries.append({
            "type": "gaussian",
            "sensitivity": sensitivity,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return noisy_data
    
    def privatize_histogram(self, data: List[Any], bins: List[Any] = None) -> Dict[Any, int]:
        """
        Create a differentially private histogram.
        
        Args:
            data: List of categorical or binned data
            bins: Possible values or bins (if None, inferred from data)
            
        Returns:
            histogram: Differentially private histogram
        """
        # Determine bins if not provided
        if bins is None:
            bins = list(set(data))
        
        # Create histogram
        counts = {}
        for bin_value in bins:
            counts[bin_value] = data.count(bin_value)
        
        # Add noise to each count
        noisy_counts = {}
        for bin_value, count in counts.items():
            # Sensitivity is 1 for histograms (one person can only change count by 1)
            noisy_counts[bin_value] = max(0, int(round(self.add_laplace_noise(count, 1.0))))
        
        return noisy_counts
    
    def privatize_mean(self, data: List[float], bounds: Tuple[float, float] = None) -> float:
        """
        Calculate a differentially private mean.
        
        Args:
            data: List of numeric values
            bounds: (min, max) bounds for the data (if None, estimated from data)
            
        Returns:
            mean: Differentially private mean
        """
        if not data:
            return 0.0
            
        # Determine bounds if not provided
        if bounds is None:
            min_val = min(data)
            max_val = max(data)
            # Add some padding to avoid underestimation
            range_padding = (max_val - min_val) * 0.1
            bounds = (min_val - range_padding, max_val + range_padding)
        
        # Clip data to bounds
        clipped_data = [max(bounds[0], min(x, bounds[1])) for x in data]
        
        # Calculate mean
        mean = sum(clipped_data) / len(clipped_data)
        
        # Sensitivity is (bounds[1] - bounds[0]) / n
        sensitivity = (bounds[1] - bounds[0]) / len(data)
        
        # Add noise
        noisy_mean = self.add_laplace_noise(mean, sensitivity)
        
        return noisy_mean
    
    def privatize_quantile(self, data: List[float], quantile: float, bounds: Tuple[float, float] = None) -> float:
        """
        Calculate a differentially private quantile.
        
        Args:
            data: List of numeric values
            quantile: Quantile to compute (0.0 to 1.0)
            bounds: (min, max) bounds for the data (if None, estimated from data)
            
        Returns:
            quantile_value: Differentially private quantile
        """
        if not data:
            return 0.0
            
        # Determine bounds if not provided
        if bounds is None:
            min_val = min(data)
            max_val = max(data)
            # Add some padding to avoid underestimation
            range_padding = (max_val - min_val) * 0.1
            bounds = (min_val - range_padding, max_val + range_padding)
        
        # Clip data to bounds
        clipped_data = [max(bounds[0], min(x, bounds[1])) for x in data]
        
        # Sort data
        sorted_data = sorted(clipped_data)
        
        # Calculate quantile
        index = int(quantile * (len(sorted_data) - 1))
        quantile_value = sorted_data[index]
        
        # Sensitivity is (bounds[1] - bounds[0]) / n
        sensitivity = (bounds[1] - bounds[0]) / len(data)
        
        # Add noise
        noisy_quantile = self.add_laplace_noise(quantile_value, sensitivity)
        
        # Ensure result is within bounds
        noisy_quantile = max(bounds[0], min(noisy_quantile, bounds[1]))
        
        return noisy_quantile
    
    def privatize_count(self, count: int) -> int:
        """
        Create a differentially private count.
        
        Args:
            count: Original count
            
        Returns:
            noisy_count: Differentially private count
        """
        # Sensitivity is 1 for counts (one person can only change count by 1)
        noisy_count = self.add_laplace_noise(count, 1.0)
        
        # Ensure count is non-negative and integer
        return max(0, int(round(noisy_count)))
    
    def privatize_sum(self, data: List[float], bounds: Tuple[float, float] = None) -> float:
        """
        Calculate a differentially private sum.
        
        Args:
            data: List of numeric values
            bounds: (min, max) bounds for individual values (if None, estimated from data)
            
        Returns:
            sum: Differentially private sum
        """
        if not data:
            return 0.0
            
        # Determine bounds if not provided
        if bounds is None:
            min_val = min(data)
            max_val = max(data)
            # Add some padding to avoid underestimation
            range_padding = (max_val - min_val) * 0.1
            bounds = (min_val - range_padding, max_val + range_padding)
        
        # Clip data to bounds
        clipped_data = [max(bounds[0], min(x, bounds[1])) for x in data]
        
        # Calculate sum
        total = sum(clipped_data)
        
        # Sensitivity is the maximum possible contribution of one record
        sensitivity = bounds[1] - bounds[0]
        
        # Add noise
        noisy_sum = self.add_laplace_noise(total, sensitivity)
        
        return noisy_sum
    
    def get_remaining_budget(self) -> float:
        """
        Get the remaining privacy budget.
        
        Returns:
            remaining_budget: Remaining privacy budget (1.0 - used)
        """
        return max(0.0, 1.0 - self.budget_used)
    
    def reset_budget(self):
        """Reset the privacy budget tracking."""
        self.budget_used = 0.0
        self.queries = []
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """
        Generate a report on privacy budget usage.
        
        Returns:
            report: Privacy budget usage report
        """
        return {
            "epsilon": self.epsilon,
            "delta": self.delta,
            "budget_used": self.budget_used,
            "remaining_budget": self.get_remaining_budget(),
            "query_count": len(self.queries),
            "queries": self.queries
        }


class FederatedLearning:
    """
    Implementation of federated learning techniques.
    
    This class provides methods for training models across multiple clients
    without sharing raw data, only model updates.
    """
    
    def __init__(self, aggregation_method: str = "fedavg"):
        """
        Initialize the FederatedLearning module.
        
        Args:
            aggregation_method: Method for aggregating model updates
                ("fedavg", "fedsgd", "fedprox")
        """
        self.aggregation_method = aggregation_method
        self.global_model = None
        self.client_models = {}
        self.round = 0
        self.history = []
    
    def initialize_global_model(self, model: Any):
        """
        Initialize the global model.
        
        Args:
            model: Initial global model
        """
        self.global_model = self._serialize_model(model)
        self.round = 0
    
    def get_global_model(self) -> Any:
        """
        Get the current global model.
        
        Returns:
            model: Current global model
        """
        return self._deserialize_model(self.global_model)
    
    def register_client(self, client_id: str, model: Any = None):
        """
        Register a client for federated learning.
        
        Args:
            client_id: ID of the client
            model: Initial client model (if None, copy of global model)
        """
        if model is None:
            if self.global_model is None:
                raise ValueError("Global model must be initialized first")
            self.client_models[client_id] = self.global_model
        else:
            self.client_models[client_id] = self._serialize_model(model)
    
    def get_client_model(self, client_id: str) -> Any:
        """
        Get the current model for a client.
        
        Args:
            client_id: ID of the client
            
        Returns:
            model: Current client model
        """
        if client_id not in self.client_models:
            raise ValueError(f"Client {client_id} not registered")
            
        return self._deserialize_model(self.client_models[client_id])
    
    def submit_model_update(self, client_id: str, model: Any, metrics: Dict[str, float] = None, weight: float = 1.0):
        """
        Submit a model update from a client.
        
        Args:
            client_id: ID of the client
            model: Updated client model
            metrics: Performance metrics for the model
            weight: Weight for this client's update (e.g., based on data size)
        """
        if client_id not in self.client_models:
            raise ValueError(f"Client {client_id} not registered")
            
        # Store updated model
        self.client_models[client_id] = {
            "model": self._serialize_model(model),
            "metrics": metrics or {},
            "weight": weight,
            "round": self.round,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def aggregate_models(self) -> Any:
        """
        Aggregate client models to update the global model.
        
        Returns:
            model: Updated global model
        """
        # Get client updates for current round
        updates = {}
        total_weight = 0.0
        
        for client_id, client_data in self.client_models.items():
            if isinstance(client_data, dict) and client_data.get("round") == self.round:
                updates[client_id] = client_data
                total_weight += client_data.get("weight", 1.0)
        
        if not updates:
            logger.warning("No client updates for current round")
            return self.get_global_model()
            
        # Perform aggregation based on method
        if self.aggregation_method == "fedavg":
            global_model = self._fedavg_aggregate(updates, total_weight)
        elif self.aggregation_method == "fedsgd":
            global_model = self._fedsgd_aggregate(updates, total_weight)
        elif self.aggregation_method == "fedprox":
            global_model = self._fedprox_aggregate(updates, total_weight)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")
            
        # Update global model
        self.global_model = self._serialize_model(global_model)
        
        # Record history
        self.history.append({
            "round": self.round,
            "clients": list(updates.keys()),
            "client_count": len(updates),
            "total_weight": total_weight,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Increment round
        self.round += 1
        
        return global_model
    
    def _fedavg_aggregate(self, updates: Dict[str, Dict[str, Any]], total_weight: float) -> Any:
        """
        Aggregate models using FedAvg algorithm.
        
        Args:
            updates: Client updates
            total_weight: Total weight of updates
            
        Returns:
            model: Aggregated model
        """
        # This is a simplified implementation
        # In a real system, we would need to handle different model architectures
        
        # Get global model as starting point
        global_model = self.get_global_model()
        
        # Check if model has weights attribute (e.g., for neural networks)
        if hasattr(global_model, "get_weights") and hasattr(global_model, "set_weights"):
            # Neural network model
            
            # Get global weights
            global_weights = global_model.get_weights()
            
            # Initialize weighted sum of weights
            weighted_sum = [np.zeros_like(w) for w in global_weights]
            
            # Add weighted client updates
            for client_id, client_data in updates.items():
                client_model = self._deserialize_model(client_data["model"])
                client_weights = client_model.get_weights()
                client_weight = client_data.get("weight", 1.0) / total_weight
                
                for i, w in enumerate(client_weights):
                    weighted_sum[i] += w * client_weight
            
            # Set global model weights
            global_model.set_weights(weighted_sum)
            
        elif hasattr(global_model, "coef_") and hasattr(global_model, "intercept_"):
            # Linear model
            
            # Initialize weighted sum of coefficients and intercept
            weighted_coef = np.zeros_like(global_model.coef_)
            weighted_intercept = np.zeros_like(global_model.intercept_)
            
            # Add weighted client updates
            for client_id, client_data in updates.items():
                client_model = self._deserialize_model(client_data["model"])
                client_weight = client_data.get("weight", 1.0) / total_weight
                
                weighted_coef += client_model.coef_ * client_weight
                weighted_intercept += client_model.intercept_ * client_weight
            
            # Set global model coefficients and intercept
            global_model.coef_ = weighted_coef
            global_model.intercept_ = weighted_intercept
            
        else:
            # Generic model
            logger.warning("Model type not supported for FedAvg, returning global model")
        
        return global_model
    
    def _fedsgd_aggregate(self, updates: Dict[str, Dict[str, Any]], total_weight: float) -> Any:
        """
        Aggregate models using FedSGD algorithm.
        
        Args:
            updates: Client updates
            total_weight: Total weight of updates
            
        Returns:
            model: Aggregated model
        """
        # FedSGD is similar to FedAvg but with a learning rate
        # This is a simplified implementation
        
        # Get global model as starting point
        global_model = self.get_global_model()
        learning_rate = 0.01  # Could be a parameter
        
        # Check if model has weights attribute (e.g., for neural networks)
        if hasattr(global_model, "get_weights") and hasattr(global_model, "set_weights"):
            # Neural network model
            
            # Get global weights
            global_weights = global_model.get_weights()
            
            # Initialize weighted sum of gradients
            weighted_gradients = [np.zeros_like(w) for w in global_weights]
            
            # Add weighted client gradients
            for client_id, client_data in updates.items():
                client_model = self._deserialize_model(client_data["model"])
                client_weights = client_model.get_weights()
                client_weight = client_data.get("weight", 1.0) / total_weight
                
                for i, w in enumerate(client_weights):
                    # Calculate gradient (difference from global weights)
                    gradient = w - global_weights[i]
                    weighted_gradients[i] += gradient * client_weight
            
            # Update global weights with gradients
            updated_weights = []
            for i, w in enumerate(global_weights):
                updated_weights.append(w + learning_rate * weighted_gradients[i])
            
            # Set global model weights
            global_model.set_weights(updated_weights)
            
        elif hasattr(global_model, "coef_") and hasattr(global_model, "intercept_"):
            # Linear model
            
            # Initialize weighted sum of gradients
            weighted_coef_gradient = np.zeros_like(global_model.coef_)
            weighted_intercept_gradient = np.zeros_like(global_model.intercept_)
            
            # Add weighted client gradients
            for client_id, client_data in updates.items():
                client_model = self._deserialize_model(client_data["model"])
                client_weight = client_data.get("weight", 1.0) / total_weight
                
                # Calculate gradients
                coef_gradient = client_model.coef_ - global_model.coef_
                intercept_gradient = client_model.intercept_ - global_model.intercept_
                
                weighted_coef_gradient += coef_gradient * client_weight
                weighted_intercept_gradient += intercept_gradient * client_weight
            
            # Update global model coefficients and intercept
            global_model.coef_ = global_model.coef_ + learning_rate * weighted_coef_gradient
            global_model.intercept_ = global_model.intercept_ + learning_rate * weighted_intercept_gradient
            
        else:
            # Generic model
            logger.warning("Model type not supported for FedSGD, returning global model")
        
        return global_model
    
    def _fedprox_aggregate(self, updates: Dict[str, Dict[str, Any]], total_weight: float) -> Any:
        """
        Aggregate models using FedProx algorithm.
        
        Args:
            updates: Client updates
            total_weight: Total weight of updates
            
        Returns:
            model: Aggregated model
        """
        # FedProx is similar to FedAvg but with a proximal term
        # This is a simplified implementation
        
        # Get global model as starting point
        global_model = self.get_global_model()
        mu = 0.01  # Proximal term weight, could be a parameter
        
        # Check if model has weights attribute (e.g., for neural networks)
        if hasattr(global_model, "get_weights") and hasattr(global_model, "set_weights"):
            # Neural network model
            
            # Get global weights
            global_weights = global_model.get_weights()
            
            # Initialize weighted sum of weights
            weighted_sum = [np.zeros_like(w) for w in global_weights]
            
            # Add weighted client updates with proximal term
            for client_id, client_data in updates.items():
                client_model = self._deserialize_model(client_data["model"])
                client_weights = client_model.get_weights()
                client_weight = client_data.get("weight", 1.0) / total_weight
                
                for i, w in enumerate(client_weights):
                    # Add proximal term (penalize deviation from global model)
                    proximal_weights = w + mu * (global_weights[i] - w)
                    weighted_sum[i] += proximal_weights * client_weight
            
            # Set global model weights
            global_model.set_weights(weighted_sum)
            
        elif hasattr(global_model, "coef_") and hasattr(global_model, "intercept_"):
            # Linear model
            
            # Initialize weighted sum of coefficients and intercept
            weighted_coef = np.zeros_like(global_model.coef_)
            weighted_intercept = np.zeros_like(global_model.intercept_)
            
            # Add weighted client updates with proximal term
            for client_id, client_data in updates.items():
                client_model = self._deserialize_model(client_data["model"])
                client_weight = client_data.get("weight", 1.0) / total_weight
                
                # Add proximal term
                proximal_coef = client_model.coef_ + mu * (global_model.coef_ - client_model.coef_)
                proximal_intercept = client_model.intercept_ + mu * (global_model.intercept_ - client_model.intercept_)
                
                weighted_coef += proximal_coef * client_weight
                weighted_intercept += proximal_intercept * client_weight
            
            # Set global model coefficients and intercept
            global_model.coef_ = weighted_coef
            global_model.intercept_ = weighted_intercept
            
        else:
            # Generic model
            logger.warning("Model type not supported for FedProx, returning global model")
        
        return global_model
    
    def _serialize_model(self, model: Any) -> bytes:
        """
        Serialize a model to bytes.
        
        Args:
            model: Model to serialize
            
        Returns:
            serialized: Serialized model
        """
        # This is a simplified implementation
        # In a real system, we would need to handle different model types
        
        try:
            return pickle.dumps(model)
        except Exception as e:
            logger.error(f"Error serializing model: {e}")
            raise
    
    def _deserialize_model(self, serialized: bytes) -> Any:
        """
        Deserialize a model from bytes.
        
        Args:
            serialized: Serialized model
            
        Returns:
            model: Deserialized model
        """
        try:
            return pickle.loads(serialized)
        except Exception as e:
            logger.error(f"Error deserializing model: {e}")
            raise
    
    def get_training_history(self) -> List[Dict[str, Any]]:
        """
        Get the training history.
        
        Returns:
            history: List of training rounds
        """
        return self.history
    
    def get_client_performance(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance metrics for all clients.
        
        Returns:
            performance: Dictionary of client performance metrics
        """
        performance = {}
        
        for client_id, client_data in self.client_models.items():
            if isinstance(client_data, dict) and "metrics" in client_data:
                performance[client_id] = client_data["metrics"]
        
        return performance


class SecureAggregation:
    """
    Implementation of secure aggregation for federated learning.
    
    This class provides methods for aggregating model updates without
    revealing individual updates, using cryptographic techniques.
    """
    
    def __init__(self, threshold: int = 3):
        """
        Initialize the SecureAggregation module.
        
        Args:
            threshold: Minimum number of clients required for aggregation
        """
        self.threshold = threshold
        self.clients = {}
        self.round = 0
        self.shared_keys = {}
        self.masked_updates = {}
        self.unmasking_shares = {}
    
    def register_client(self, client_id: str):
        """
        Register a client for secure aggregation.
        
        Args:
            client_id: ID of the client
        """
        self.clients[client_id] = {
            "registered_at": datetime.datetime.now().isoformat(),
            "active": True
        }
    
    def setup_round(self, client_ids: List[str]) -> Dict[str, Any]:
        """
        Set up a new aggregation round.
        
        Args:
            client_ids: IDs of participating clients
            
        Returns:
            round_info: Information about the round
        """
        # Increment round
        self.round += 1
        
        # Reset round data
        self.shared_keys = {}
        self.masked_updates = {}
        self.unmasking_shares = {}
        
        # Check if we have enough clients
        active_clients = [cid for cid in client_ids if cid in self.clients and self.clients[cid]["active"]]
        
        if len(active_clients) < self.threshold:
            raise ValueError(f"Not enough active clients: {len(active_clients)} < {self.threshold}")
            
        # Generate round information
        round_info = {
            "round": self.round,
            "clients": active_clients,
            "threshold": self.threshold,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return round_info
    
    def generate_key_shares(self, client_id: str, client_ids: List[str]) -> Dict[str, bytes]:
        """
        Generate key shares for a client.
        
        Args:
            client_id: ID of the client
            client_ids: IDs of all participating clients
            
        Returns:
            key_shares: Key shares for other clients
        """
        if client_id not in self.clients or not self.clients[client_id]["active"]:
            raise ValueError(f"Client {client_id} not registered or not active")
            
        # Generate random key for this client
        key = os.urandom(32)
        
        # Generate shares for each other client
        shares = {}
        for other_id in client_ids:
            if other_id != client_id:
                # In a real implementation, we would use Shamir's Secret Sharing
                # For simplicity, we just generate random shares
                shares[other_id] = os.urandom(32)
        
        # Store key and shares
        self.shared_keys[client_id] = {
            "key": key,
            "shares": shares,
            "round": self.round
        }
        
        return shares
    
    def receive_key_shares(self, client_id: str, shares: Dict[str, bytes]):
        """
        Receive key shares from other clients.
        
        Args:
            client_id: ID of the receiving client
            shares: Key shares from other clients
        """
        if client_id not in self.clients or not self.clients[client_id]["active"]:
            raise ValueError(f"Client {client_id} not registered or not active")
            
        # Store received shares
        if client_id not in self.shared_keys:
            self.shared_keys[client_id] = {
                "received_shares": shares,
                "round": self.round
            }
        else:
            self.shared_keys[client_id]["received_shares"] = shares
    
    def mask_update(self, client_id: str, update: np.ndarray) -> np.ndarray:
        """
        Mask a model update with random noise.
        
        Args:
            client_id: ID of the client
            update: Model update to mask
            
        Returns:
            masked_update: Masked model update
        """
        if client_id not in self.clients or not self.clients[client_id]["active"]:
            raise ValueError(f"Client {client_id} not registered or not active")
            
        if client_id not in self.shared_keys:
            raise ValueError(f"Client {client_id} has not set up keys for round {self.round}")
            
        # Get key and received shares
        client_data = self.shared_keys[client_id]
        key = client_data.get("key")
        received_shares = client_data.get("received_shares", {})
        
        if key is None:
            raise ValueError(f"Client {client_id} has no key for round {self.round}")
            
        # Generate pseudorandom noise from key and received shares
        noise = np.zeros_like(update)
        
        # Add noise from own key
        noise_from_key = self._generate_noise(key, update.shape)
        noise += noise_from_key
        
        # Add noise from received shares
        for other_id, share in received_shares.items():
            noise_from_share = self._generate_noise(share, update.shape)
            # Add or subtract based on client IDs (consistent pairwise)
            if client_id < other_id:
                noise += noise_from_share
            else:
                noise -= noise_from_share
        
        # Mask update with noise
        masked_update = update + noise
        
        # Store masked update
        self.masked_updates[client_id] = {
            "masked_update": masked_update,
            "round": self.round
        }
        
        return masked_update
    
    def submit_masked_update(self, client_id: str, masked_update: np.ndarray):
        """
        Submit a masked model update.
        
        Args:
            client_id: ID of the client
            masked_update: Masked model update
        """
        if client_id not in self.clients or not self.clients[client_id]["active"]:
            raise ValueError(f"Client {client_id} not registered or not active")
            
        # Store masked update
        self.masked_updates[client_id] = {
            "masked_update": masked_update,
            "round": self.round,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def generate_unmasking_shares(self, client_id: str, surviving_clients: List[str]) -> Dict[str, bytes]:
        """
        Generate shares for unmasking when some clients drop out.
        
        Args:
            client_id: ID of the client
            surviving_clients: IDs of clients that are still active
            
        Returns:
            unmasking_shares: Shares for unmasking
        """
        if client_id not in self.clients or not self.clients[client_id]["active"]:
            raise ValueError(f"Client {client_id} not registered or not active")
            
        if client_id not in self.shared_keys:
            raise ValueError(f"Client {client_id} has not set up keys for round {self.round}")
            
        # Get key and shares
        client_data = self.shared_keys[client_id]
        key = client_data.get("key")
        shares = client_data.get("shares", {})
        
        if key is None:
            raise ValueError(f"Client {client_id} has no key for round {self.round}")
            
        # Generate unmasking shares for surviving clients
        unmasking_shares = {}
        
        # Share own key with all surviving clients
        for other_id in surviving_clients:
            if other_id != client_id:
                unmasking_shares[other_id] = key
        
        # Share received shares from dropped clients with surviving clients
        dropped_clients = [cid for cid in shares.keys() if cid not in surviving_clients]
        
        for dropped_id in dropped_clients:
            if dropped_id in shares:
                for other_id in surviving_clients:
                    if other_id != client_id:
                        # In a real implementation, we would use a more secure approach
                        # For simplicity, we just share the dropped client's share
                        if other_id not in unmasking_shares:
                            unmasking_shares[other_id] = shares[dropped_id]
                        else:
                            # XOR the shares (simplified)
                            unmasking_shares[other_id] = bytes(a ^ b for a, b in zip(unmasking_shares[other_id], shares[dropped_id]))
        
        # Store unmasking shares
        self.unmasking_shares[client_id] = {
            "shares": unmasking_shares,
            "round": self.round,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return unmasking_shares
    
    def receive_unmasking_shares(self, client_id: str, shares: Dict[str, bytes]):
        """
        Receive unmasking shares from other clients.
        
        Args:
            client_id: ID of the receiving client
            shares: Unmasking shares from other clients
        """
        if client_id not in self.clients or not self.clients[client_id]["active"]:
            raise ValueError(f"Client {client_id} not registered or not active")
            
        # Store received unmasking shares
        self.unmasking_shares[client_id] = {
            "received_shares": shares,
            "round": self.round,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def aggregate_masked_updates(self, surviving_clients: List[str]) -> np.ndarray:
        """
        Aggregate masked updates from surviving clients.
        
        Args:
            surviving_clients: IDs of clients that are still active
            
        Returns:
            aggregated_update: Aggregated model update
        """
        # Check if we have enough clients
        if len(surviving_clients) < self.threshold:
            raise ValueError(f"Not enough surviving clients: {len(surviving_clients)} < {self.threshold}")
            
        # Check if we have masked updates from all surviving clients
        for client_id in surviving_clients:
            if client_id not in self.masked_updates:
                raise ValueError(f"Missing masked update from client {client_id}")
                
        # Sum masked updates
        updates = [self.masked_updates[client_id]["masked_update"] for client_id in surviving_clients]
        aggregated_update = sum(updates)
        
        # The noise cancels out in the sum (in a complete implementation)
        # In a real system, we would need to handle dropped clients properly
        
        return aggregated_update
    
    def _generate_noise(self, seed: bytes, shape: Tuple[int, ...]) -> np.ndarray:
        """
        Generate pseudorandom noise from a seed.
        
        Args:
            seed: Seed for the random number generator
            shape: Shape of the noise array
            
        Returns:
            noise: Pseudorandom noise
        """
        # Create a random number generator with the seed
        rng = np.random.RandomState(int.from_bytes(seed[:4], byteorder="big"))
        
        # Generate noise
        noise = rng.normal(0, 1, shape)
        
        return noise


class PrivacyPreservingDataTransformation:
    """
    Implementation of privacy-preserving data transformations.
    
    This class provides methods for transforming data to protect privacy,
    including anonymization, pseudonymization, and k-anonymity.
    """
    
    def __init__(self):
        """Initialize the PrivacyPreservingDataTransformation module."""
        self.transformations = {}
        self.encryption_keys = {}
    
    def anonymize_dataframe(self, 
                           df: pd.DataFrame, 
                           identifiers: List[str],
                           quasi_identifiers: List[str],
                           sensitive_attributes: List[str]) -> pd.DataFrame:
        """
        Anonymize a pandas DataFrame.
        
        Args:
            df: DataFrame to anonymize
            identifiers: Direct identifier columns to remove
            quasi_identifiers: Quasi-identifier columns to transform
            sensitive_attributes: Sensitive columns to protect
            
        Returns:
            anonymized_df: Anonymized DataFrame
        """
        # Create a copy of the DataFrame
        anonymized_df = df.copy()
        
        # Remove direct identifiers
        anonymized_df = anonymized_df.drop(columns=identifiers)
        
        # Transform quasi-identifiers
        for column in quasi_identifiers:
            if column in anonymized_df.columns:
                # Check column type and apply appropriate transformation
                if pd.api.types.is_numeric_dtype(anonymized_df[column]):
                    # For numeric columns, apply binning
                    anonymized_df[column] = self._bin_numeric_column(anonymized_df[column])
                elif pd.api.types.is_datetime64_dtype(anonymized_df[column]):
                    # For date columns, reduce precision
                    anonymized_df[column] = self._reduce_date_precision(anonymized_df[column])
                else:
                    # For categorical columns, apply generalization
                    anonymized_df[column] = self._generalize_categorical_column(anonymized_df[column])
        
        # Protect sensitive attributes
        for column in sensitive_attributes:
            if column in anonymized_df.columns:
                # Apply differential privacy to sensitive columns
                dp = DifferentialPrivacy(epsilon=1.0)
                
                if pd.api.types.is_numeric_dtype(anonymized_df[column]):
                    # For numeric columns, add noise
                    values = anonymized_df[column].values
                    min_val = values.min()
                    max_val = values.max()
                    sensitivity = (max_val - min_val) * 0.01  # Small fraction of range
                    
                    noisy_values = dp.add_laplace_noise(values, sensitivity)
                    anonymized_df[column] = noisy_values
                elif pd.api.types.is_categorical_dtype(anonymized_df[column]) or anonymized_df[column].dtype == object:
                    # For categorical columns, apply randomized response
                    anonymized_df[column] = self._randomized_response(anonymized_df[column])
        
        # Store transformation metadata
        transformation_id = str(uuid.uuid4())
        self.transformations[transformation_id] = {
            "type": "anonymization",
            "identifiers": identifiers,
            "quasi_identifiers": quasi_identifiers,
            "sensitive_attributes": sensitive_attributes,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add transformation ID as metadata
        anonymized_df.attrs["transformation_id"] = transformation_id
        
        return anonymized_df
    
    def pseudonymize_dataframe(self, 
                              df: pd.DataFrame, 
                              identifiers: List[str],
                              salt: str = None) -> Tuple[pd.DataFrame, Dict[str, Dict[str, str]]]:
        """
        Pseudonymize a pandas DataFrame.
        
        Args:
            df: DataFrame to pseudonymize
            identifiers: Identifier columns to pseudonymize
            salt: Salt for hashing (if None, random salt is generated)
            
        Returns:
            pseudonymized_df: Pseudonymized DataFrame
            mapping: Mapping from pseudonyms to original values
        """
        # Create a copy of the DataFrame
        pseudonymized_df = df.copy()
        
        # Generate salt if not provided
        if salt is None:
            salt = base64.b64encode(os.urandom(16)).decode("utf-8")
            
        # Initialize mapping
        mapping = {}
        
        # Pseudonymize identifiers
        for column in identifiers:
            if column in pseudonymized_df.columns:
                column_mapping = {}
                
                # Get unique values
                unique_values = pseudonymized_df[column].unique()
                
                # Create pseudonyms for each unique value
                for value in unique_values:
                    if pd.isna(value):
                        # Skip NaN values
                        continue
                        
                    # Convert value to string
                    value_str = str(value)
                    
                    # Create pseudonym using hash
                    pseudonym = self._create_pseudonym(value_str, salt)
                    
                    # Store in mapping
                    column_mapping[pseudonym] = value_str
                    
                    # Replace in DataFrame
                    pseudonymized_df.loc[pseudonymized_df[column] == value, column] = pseudonym
                
                # Store column mapping
                mapping[column] = column_mapping
        
        # Store transformation metadata
        transformation_id = str(uuid.uuid4())
        self.transformations[transformation_id] = {
            "type": "pseudonymization",
            "identifiers": identifiers,
            "salt": salt,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add transformation ID as metadata
        pseudonymized_df.attrs["transformation_id"] = transformation_id
        
        return pseudonymized_df, mapping
    
    def apply_k_anonymity(self, 
                         df: pd.DataFrame, 
                         quasi_identifiers: List[str],
                         k: int = 5) -> pd.DataFrame:
        """
        Apply k-anonymity to a pandas DataFrame.
        
        Args:
            df: DataFrame to anonymize
            quasi_identifiers: Quasi-identifier columns to consider
            k: Minimum group size
            
        Returns:
            anonymized_df: k-anonymized DataFrame
        """
        # Create a copy of the DataFrame
        anonymized_df = df.copy()
        
        # Check if we have quasi-identifiers
        if not quasi_identifiers or not all(col in anonymized_df.columns for col in quasi_identifiers):
            raise ValueError("Invalid quasi-identifiers")
            
        # Group by quasi-identifiers
        grouped = anonymized_df.groupby(quasi_identifiers).size().reset_index(name="count")
        
        # Identify groups smaller than k
        small_groups = grouped[grouped["count"] < k]
        
        if small_groups.empty:
            # Already k-anonymous
            logger.info("DataFrame is already k-anonymous")
            return anonymized_df
            
        # Generalize quasi-identifiers until k-anonymity is achieved
        while not small_groups.empty:
            # Choose a quasi-identifier to generalize
            # In a real implementation, we would use a more sophisticated approach
            column_to_generalize = quasi_identifiers[0]
            
            # Generalize the column
            if pd.api.types.is_numeric_dtype(anonymized_df[column_to_generalize]):
                # For numeric columns, apply binning
                anonymized_df[column_to_generalize] = self._bin_numeric_column(
                    anonymized_df[column_to_generalize], 
                    n_bins=max(2, anonymized_df[column_to_generalize].nunique() // 2)
                )
            elif pd.api.types.is_datetime64_dtype(anonymized_df[column_to_generalize]):
                # For date columns, reduce precision
                anonymized_df[column_to_generalize] = self._reduce_date_precision(
                    anonymized_df[column_to_generalize],
                    level="month"  # Increase generalization level
                )
            else:
                # For categorical columns, apply generalization
                anonymized_df[column_to_generalize] = self._generalize_categorical_column(
                    anonymized_df[column_to_generalize]
                )
            
            # Check if k-anonymity is achieved
            grouped = anonymized_df.groupby(quasi_identifiers).size().reset_index(name="count")
            small_groups = grouped[grouped["count"] < k]
            
            # Rotate quasi-identifiers to generalize different columns
            quasi_identifiers = quasi_identifiers[1:] + quasi_identifiers[:1]
            
            # Safety check to avoid infinite loop
            if all(col in anonymized_df.columns and anonymized_df[col].nunique() <= 1 for col in quasi_identifiers):
                logger.warning("Cannot achieve k-anonymity with current quasi-identifiers")
                break
        
        # Store transformation metadata
        transformation_id = str(uuid.uuid4())
        self.transformations[transformation_id] = {
            "type": "k_anonymity",
            "quasi_identifiers": quasi_identifiers,
            "k": k,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add transformation ID as metadata
        anonymized_df.attrs["transformation_id"] = transformation_id
        
        return anonymized_df
    
    def encrypt_column(self, 
                      df: pd.DataFrame, 
                      column: str,
                      key: bytes = None) -> pd.DataFrame:
        """
        Encrypt a column in a pandas DataFrame.
        
        Args:
            df: DataFrame containing the column
            column: Column to encrypt
            key: Encryption key (if None, a new key is generated)
            
        Returns:
            df_with_encrypted: DataFrame with encrypted column
        """
        # Create a copy of the DataFrame
        df_with_encrypted = df.copy()
        
        # Generate key if not provided
        if key is None:
            key = Fernet.generate_key()
            
        # Create cipher
        cipher = Fernet(key)
        
        # Encrypt column values
        encrypted_values = []
        
        for value in df_with_encrypted[column]:
            if pd.isna(value):
                # Keep NaN values as is
                encrypted_values.append(value)
            else:
                # Convert to string and encrypt
                value_str = str(value).encode("utf-8")
                encrypted = cipher.encrypt(value_str)
                encrypted_values.append(encrypted.decode("utf-8"))
        
        # Replace column with encrypted values
        df_with_encrypted[column] = encrypted_values
        
        # Store encryption key
        key_id = str(uuid.uuid4())
        self.encryption_keys[key_id] = {
            "key": key,
            "column": column,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add key ID as metadata
        df_with_encrypted.attrs["encryption_key_id"] = key_id
        
        return df_with_encrypted
    
    def decrypt_column(self, 
                      df: pd.DataFrame, 
                      column: str,
                      key: bytes) -> pd.DataFrame:
        """
        Decrypt a column in a pandas DataFrame.
        
        Args:
            df: DataFrame containing the encrypted column
            column: Column to decrypt
            key: Decryption key
            
        Returns:
            df_with_decrypted: DataFrame with decrypted column
        """
        # Create a copy of the DataFrame
        df_with_decrypted = df.copy()
        
        # Create cipher
        cipher = Fernet(key)
        
        # Decrypt column values
        decrypted_values = []
        
        for value in df_with_decrypted[column]:
            if pd.isna(value):
                # Keep NaN values as is
                decrypted_values.append(value)
            else:
                try:
                    # Decrypt
                    encrypted = value.encode("utf-8")
                    decrypted = cipher.decrypt(encrypted)
                    decrypted_values.append(decrypted.decode("utf-8"))
                except Exception as e:
                    logger.error(f"Error decrypting value: {e}")
                    decrypted_values.append(None)
        
        # Replace column with decrypted values
        df_with_decrypted[column] = decrypted_values
        
        return df_with_decrypted
    
    def _bin_numeric_column(self, column: pd.Series, n_bins: int = 10) -> pd.Series:
        """
        Bin a numeric column into categories.
        
        Args:
            column: Numeric column to bin
            n_bins: Number of bins
            
        Returns:
            binned: Binned column
        """
        # Create bins
        bins = pd.cut(column, n_bins)
        
        # Convert to string representation
        binned = bins.astype(str)
        
        return binned
    
    def _reduce_date_precision(self, column: pd.Series, level: str = "year") -> pd.Series:
        """
        Reduce precision of a date column.
        
        Args:
            column: Date column to transform
            level: Level of precision ("year", "month", "day")
            
        Returns:
            reduced: Date column with reduced precision
        """
        if level == "year":
            # Keep only year
            reduced = column.dt.strftime("%Y-01-01")
        elif level == "month":
            # Keep year and month
            reduced = column.dt.strftime("%Y-%m-01")
        elif level == "day":
            # Keep year, month, and day
            reduced = column.dt.strftime("%Y-%m-%d")
        else:
            raise ValueError(f"Invalid precision level: {level}")
            
        return reduced
    
    def _generalize_categorical_column(self, column: pd.Series) -> pd.Series:
        """
        Generalize a categorical column.
        
        Args:
            column: Categorical column to generalize
            
        Returns:
            generalized: Generalized column
        """
        # This is a simplified implementation
        # In a real system, we would use a domain hierarchy
        
        # Get value counts
        value_counts = column.value_counts()
        
        # Identify rare categories (less than 5% of data)
        total_count = len(column)
        rare_categories = value_counts[value_counts / total_count < 0.05].index.tolist()
        
        # Replace rare categories with "Other"
        generalized = column.copy()
        generalized[generalized.isin(rare_categories)] = "Other"
        
        return generalized
    
    def _randomized_response(self, column: pd.Series, p: float = 0.7) -> pd.Series:
        """
        Apply randomized response to a categorical column.
        
        Args:
            column: Categorical column to transform
            p: Probability of keeping original value
            
        Returns:
            randomized: Column with randomized response
        """
        # Get unique values
        unique_values = column.unique()
        
        # Apply randomized response
        randomized = column.copy()
        
        for i in range(len(randomized)):
            if random.random() > p:
                # Replace with random value
                randomized.iloc[i] = random.choice(unique_values)
        
        return randomized
    
    def _create_pseudonym(self, value: str, salt: str) -> str:
        """
        Create a pseudonym for a value using hashing.
        
        Args:
            value: Value to pseudonymize
            salt: Salt for hashing
            
        Returns:
            pseudonym: Pseudonym for the value
        """
        # Create hash
        hash_obj = hashlib.sha256((value + salt).encode("utf-8"))
        hash_hex = hash_obj.hexdigest()
        
        # Use first 16 characters as pseudonym
        pseudonym = hash_hex[:16]
        
        return pseudonym
    
    def get_transformation_metadata(self, transformation_id: str) -> Dict[str, Any]:
        """
        Get metadata for a transformation.
        
        Args:
            transformation_id: ID of the transformation
            
        Returns:
            metadata: Transformation metadata
        """
        return self.transformations.get(transformation_id, {})
    
    def get_encryption_key(self, key_id: str) -> bytes:
        """
        Get an encryption key.
        
        Args:
            key_id: ID of the encryption key
            
        Returns:
            key: Encryption key
        """
        key_data = self.encryption_keys.get(key_id, {})
        return key_data.get("key")


class PrivacyManager:
    """
    Manager for privacy-preserving features.
    
    This class integrates all privacy-preserving components and provides
    a unified interface for protecting user data during the learning process.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the PrivacyManager.
        
        Args:
            storage_path: Path to store privacy-related data
        """
        # Create storage directory
        if storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
        # Initialize components
        self.differential_privacy = DifferentialPrivacy()
        self.federated_learning = FederatedLearning()
        self.secure_aggregation = SecureAggregation()
        self.data_transformation = PrivacyPreservingDataTransformation()
        
        # Privacy settings
        self.settings = {
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
        
        # Privacy metrics
        self.metrics = {
            "differential_privacy": {
                "queries": 0,
                "budget_used": 0.0
            },
            "federated_learning": {
                "rounds": 0,
                "clients": 0
            },
            "secure_aggregation": {
                "rounds": 0,
                "clients": 0
            },
            "data_transformation": {
                "transformations": 0
            }
        }
        
        # Storage path
        self.storage_path = storage_path
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update privacy settings.
        
        Args:
            settings: New settings
            
        Returns:
            updated_settings: Updated settings
        """
        # Update differential privacy settings
        if "differential_privacy" in settings:
            dp_settings = settings["differential_privacy"]
            
            if "enabled" in dp_settings:
                self.settings["differential_privacy"]["enabled"] = dp_settings["enabled"]
                
            if "epsilon" in dp_settings:
                epsilon = dp_settings["epsilon"]
                if epsilon > 0:
                    self.settings["differential_privacy"]["epsilon"] = epsilon
                    self.differential_privacy.epsilon = epsilon
                    
            if "delta" in dp_settings:
                delta = dp_settings["delta"]
                if 0 < delta < 1:
                    self.settings["differential_privacy"]["delta"] = delta
                    self.differential_privacy.delta = delta
        
        # Update federated learning settings
        if "federated_learning" in settings:
            fl_settings = settings["federated_learning"]
            
            if "enabled" in fl_settings:
                self.settings["federated_learning"]["enabled"] = fl_settings["enabled"]
                
            if "aggregation_method" in fl_settings:
                method = fl_settings["aggregation_method"]
                if method in ["fedavg", "fedsgd", "fedprox"]:
                    self.settings["federated_learning"]["aggregation_method"] = method
                    self.federated_learning.aggregation_method = method
        
        # Update secure aggregation settings
        if "secure_aggregation" in settings:
            sa_settings = settings["secure_aggregation"]
            
            if "enabled" in sa_settings:
                self.settings["secure_aggregation"]["enabled"] = sa_settings["enabled"]
                
            if "threshold" in sa_settings:
                threshold = sa_settings["threshold"]
                if threshold >= 2:
                    self.settings["secure_aggregation"]["threshold"] = threshold
                    self.secure_aggregation.threshold = threshold
        
        # Update data transformation settings
        if "data_transformation" in settings:
            dt_settings = settings["data_transformation"]
            
            if "enabled" in dt_settings:
                self.settings["data_transformation"]["enabled"] = dt_settings["enabled"]
        
        return self.settings
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current privacy settings.
        
        Returns:
            settings: Current privacy settings
        """
        return self.settings
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get privacy metrics.
        
        Returns:
            metrics: Privacy metrics
        """
        # Update metrics from components
        
        # Differential privacy metrics
        dp_report = self.differential_privacy.get_privacy_report()
        self.metrics["differential_privacy"]["queries"] = len(dp_report["queries"])
        self.metrics["differential_privacy"]["budget_used"] = dp_report["budget_used"]
        
        # Federated learning metrics
        fl_history = self.federated_learning.get_training_history()
        self.metrics["federated_learning"]["rounds"] = len(fl_history)
        
        if fl_history:
            clients = set()
            for round_data in fl_history:
                clients.update(round_data.get("clients", []))
            self.metrics["federated_learning"]["clients"] = len(clients)
        
        # Secure aggregation metrics
        self.metrics["secure_aggregation"]["rounds"] = self.secure_aggregation.round
        self.metrics["secure_aggregation"]["clients"] = len(self.secure_aggregation.clients)
        
        # Data transformation metrics
        self.metrics["data_transformation"]["transformations"] = len(self.data_transformation.transformations)
        
        return self.metrics
    
    def privatize_data(self, 
                      data: Union[pd.DataFrame, np.ndarray, List[Any]],
                      method: str = "auto",
                      **kwargs) -> Union[pd.DataFrame, np.ndarray, List[Any]]:
        """
        Apply privacy-preserving transformations to data.
        
        Args:
            data: Data to privatize
            method: Privacy method to use
            **kwargs: Additional arguments for the method
            
        Returns:
            private_data: Privatized data
        """
        # Check if data transformation is enabled
        if not self.settings["data_transformation"]["enabled"]:
            logger.warning("Data transformation is disabled")
            return data
            
        # Determine method based on data type if auto
        if method == "auto":
            if isinstance(data, pd.DataFrame):
                method = "anonymize"
            elif isinstance(data, np.ndarray):
                method = "differential_privacy"
            else:
                method = "differential_privacy"
        
        # Apply appropriate method
        if method == "anonymize" and isinstance(data, pd.DataFrame):
            # Get parameters
            identifiers = kwargs.get("identifiers", [])
            quasi_identifiers = kwargs.get("quasi_identifiers", [])
            sensitive_attributes = kwargs.get("sensitive_attributes", [])
            
            # Apply anonymization
            private_data = self.data_transformation.anonymize_dataframe(
                data, identifiers, quasi_identifiers, sensitive_attributes
            )
            
            # Update metrics
            self.metrics["data_transformation"]["transformations"] += 1
            
        elif method == "pseudonymize" and isinstance(data, pd.DataFrame):
            # Get parameters
            identifiers = kwargs.get("identifiers", [])
            salt = kwargs.get("salt")
            
            # Apply pseudonymization
            private_data, mapping = self.data_transformation.pseudonymize_dataframe(
                data, identifiers, salt
            )
            
            # Update metrics
            self.metrics["data_transformation"]["transformations"] += 1
            
        elif method == "k_anonymity" and isinstance(data, pd.DataFrame):
            # Get parameters
            quasi_identifiers = kwargs.get("quasi_identifiers", [])
            k = kwargs.get("k", 5)
            
            # Apply k-anonymity
            private_data = self.data_transformation.apply_k_anonymity(
                data, quasi_identifiers, k
            )
            
            # Update metrics
            self.metrics["data_transformation"]["transformations"] += 1
            
        elif method == "differential_privacy":
            # Get parameters
            sensitivity = kwargs.get("sensitivity", 1.0)
            noise_type = kwargs.get("noise_type", "laplace")
            
            # Apply differential privacy
            if noise_type == "laplace":
                private_data = self.differential_privacy.add_laplace_noise(data, sensitivity)
            else:
                private_data = self.differential_privacy.add_gaussian_noise(data, sensitivity)
                
            # Update metrics
            self.metrics["differential_privacy"]["queries"] += 1
            self.metrics["differential_privacy"]["budget_used"] = self.differential_privacy.budget_used
            
        elif method == "encrypt" and isinstance(data, pd.DataFrame):
            # Get parameters
            column = kwargs.get("column")
            key = kwargs.get("key")
            
            if column is None:
                raise ValueError("Column must be specified for encryption")
                
            # Apply encryption
            private_data = self.data_transformation.encrypt_column(
                data, column, key
            )
            
            # Update metrics
            self.metrics["data_transformation"]["transformations"] += 1
            
        else:
            raise ValueError(f"Invalid privacy method: {method}")
            
        return private_data
    
    def setup_federated_learning(self, model: Any) -> Dict[str, Any]:
        """
        Set up federated learning with a global model.
        
        Args:
            model: Initial global model
            
        Returns:
            setup_info: Setup information
        """
        # Check if federated learning is enabled
        if not self.settings["federated_learning"]["enabled"]:
            logger.warning("Federated learning is disabled")
            return {"status": "disabled"}
            
        # Initialize global model
        self.federated_learning.initialize_global_model(model)
        
        # Update metrics
        self.metrics["federated_learning"]["rounds"] = 0
        
        return {
            "status": "success",
            "aggregation_method": self.federated_learning.aggregation_method,
            "round": self.federated_learning.round
        }
    
    def register_federated_client(self, client_id: str, model: Any = None) -> Dict[str, Any]:
        """
        Register a client for federated learning.
        
        Args:
            client_id: ID of the client
            model: Initial client model (if None, copy of global model)
            
        Returns:
            client_info: Client registration information
        """
        # Check if federated learning is enabled
        if not self.settings["federated_learning"]["enabled"]:
            logger.warning("Federated learning is disabled")
            return {"status": "disabled"}
            
        # Register client
        self.federated_learning.register_client(client_id, model)
        
        # Update metrics
        self.metrics["federated_learning"]["clients"] = len(self.federated_learning.client_models)
        
        return {
            "status": "success",
            "client_id": client_id,
            "round": self.federated_learning.round
        }
    
    def submit_federated_update(self, 
                               client_id: str, 
                               model: Any, 
                               metrics: Dict[str, float] = None,
                               weight: float = 1.0) -> Dict[str, Any]:
        """
        Submit a model update for federated learning.
        
        Args:
            client_id: ID of the client
            model: Updated client model
            metrics: Performance metrics for the model
            weight: Weight for this client's update
            
        Returns:
            submission_info: Submission information
        """
        # Check if federated learning is enabled
        if not self.settings["federated_learning"]["enabled"]:
            logger.warning("Federated learning is disabled")
            return {"status": "disabled"}
            
        # Submit update
        self.federated_learning.submit_model_update(client_id, model, metrics, weight)
        
        return {
            "status": "success",
            "client_id": client_id,
            "round": self.federated_learning.round
        }
    
    def aggregate_federated_models(self) -> Dict[str, Any]:
        """
        Aggregate client models in federated learning.
        
        Returns:
            aggregation_info: Aggregation information
        """
        # Check if federated learning is enabled
        if not self.settings["federated_learning"]["enabled"]:
            logger.warning("Federated learning is disabled")
            return {"status": "disabled"}
            
        # Aggregate models
        global_model = self.federated_learning.aggregate_models()
        
        # Update metrics
        self.metrics["federated_learning"]["rounds"] = self.federated_learning.round
        
        return {
            "status": "success",
            "round": self.federated_learning.round - 1,
            "client_count": len(self.federated_learning.history[-1]["clients"]) if self.federated_learning.history else 0
        }
    
    def setup_secure_aggregation(self, client_ids: List[str]) -> Dict[str, Any]:
        """
        Set up secure aggregation for a round.
        
        Args:
            client_ids: IDs of participating clients
            
        Returns:
            round_info: Information about the round
        """
        # Check if secure aggregation is enabled
        if not self.settings["secure_aggregation"]["enabled"]:
            logger.warning("Secure aggregation is disabled")
            return {"status": "disabled"}
            
        # Set up round
        round_info = self.secure_aggregation.setup_round(client_ids)
        
        # Update metrics
        self.metrics["secure_aggregation"]["rounds"] = self.secure_aggregation.round
        
        return {
            "status": "success",
            **round_info
        }
    
    def generate_key_shares(self, client_id: str, client_ids: List[str]) -> Dict[str, Any]:
        """
        Generate key shares for secure aggregation.
        
        Args:
            client_id: ID of the client
            client_ids: IDs of all participating clients
            
        Returns:
            shares_info: Information about the generated shares
        """
        # Check if secure aggregation is enabled
        if not self.settings["secure_aggregation"]["enabled"]:
            logger.warning("Secure aggregation is disabled")
            return {"status": "disabled"}
            
        # Generate key shares
        shares = self.secure_aggregation.generate_key_shares(client_id, client_ids)
        
        return {
            "status": "success",
            "client_id": client_id,
            "round": self.secure_aggregation.round,
            "share_count": len(shares)
        }
    
    def mask_model_update(self, client_id: str, update: np.ndarray) -> Dict[str, Any]:
        """
        Mask a model update for secure aggregation.
        
        Args:
            client_id: ID of the client
            update: Model update to mask
            
        Returns:
            masking_info: Information about the masking
        """
        # Check if secure aggregation is enabled
        if not self.settings["secure_aggregation"]["enabled"]:
            logger.warning("Secure aggregation is disabled")
            return {"status": "disabled"}
            
        # Mask update
        masked_update = self.secure_aggregation.mask_update(client_id, update)
        
        return {
            "status": "success",
            "client_id": client_id,
            "round": self.secure_aggregation.round,
            "masked_update": masked_update
        }
    
    def aggregate_secure_updates(self, surviving_clients: List[str]) -> Dict[str, Any]:
        """
        Aggregate masked updates in secure aggregation.
        
        Args:
            surviving_clients: IDs of clients that are still active
            
        Returns:
            aggregation_info: Aggregation information
        """
        # Check if secure aggregation is enabled
        if not self.settings["secure_aggregation"]["enabled"]:
            logger.warning("Secure aggregation is disabled")
            return {"status": "disabled"}
            
        # Aggregate updates
        aggregated_update = self.secure_aggregation.aggregate_masked_updates(surviving_clients)
        
        return {
            "status": "success",
            "round": self.secure_aggregation.round,
            "client_count": len(surviving_clients),
            "aggregated_update": aggregated_update
        }
    
    def save_state(self) -> Dict[str, Any]:
        """
        Save the current state of the privacy manager.
        
        Returns:
            save_info: Information about the saved state
        """
        if not self.storage_path:
            logger.warning("No storage path specified")
            return {"status": "error", "message": "No storage path specified"}
            
        try:
            # Create state dictionary
            state = {
                "settings": self.settings,
                "metrics": self.metrics,
                "differential_privacy": {
                    "epsilon": self.differential_privacy.epsilon,
                    "delta": self.differential_privacy.delta,
                    "budget_used": self.differential_privacy.budget_used,
                    "queries": self.differential_privacy.queries
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save to file
            state_file = os.path.join(self.storage_path, "privacy_state.json")
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            return {
                "status": "success",
                "file": state_file,
                "timestamp": state["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            return {"status": "error", "message": str(e)}
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load the saved state of the privacy manager.
        
        Returns:
            load_info: Information about the loaded state
        """
        if not self.storage_path:
            logger.warning("No storage path specified")
            return {"status": "error", "message": "No storage path specified"}
            
        try:
            # Load from file
            state_file = os.path.join(self.storage_path, "privacy_state.json")
            
            if not os.path.exists(state_file):
                logger.warning("No saved state found")
                return {"status": "error", "message": "No saved state found"}
                
            with open(state_file, 'r') as f:
                state = json.load(f)
                
            # Restore settings
            if "settings" in state:
                self.settings = state["settings"]
                
            # Restore metrics
            if "metrics" in state:
                self.metrics = state["metrics"]
                
            # Restore differential privacy state
            if "differential_privacy" in state:
                dp_state = state["differential_privacy"]
                self.differential_privacy.epsilon = dp_state.get("epsilon", 1.0)
                self.differential_privacy.delta = dp_state.get("delta", 1e-5)
                self.differential_privacy.budget_used = dp_state.get("budget_used", 0.0)
                self.differential_privacy.queries = dp_state.get("queries", [])
                
            return {
                "status": "success",
                "file": state_file,
                "timestamp": state.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive privacy report.
        
        Returns:
            report: Privacy report
        """
        # Get current settings and metrics
        settings = self.get_settings()
        metrics = self.get_metrics()
        
        # Get differential privacy report
        dp_report = self.differential_privacy.get_privacy_report()
        
        # Get federated learning history
        fl_history = self.federated_learning.get_training_history()
        fl_performance = self.federated_learning.get_client_performance()
        
        # Create report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "settings": settings,
            "metrics": metrics,
            "differential_privacy": dp_report,
            "federated_learning": {
                "rounds": len(fl_history),
                "history": fl_history,
                "performance": fl_performance
            },
            "secure_aggregation": {
                "rounds": self.secure_aggregation.round,
                "clients": len(self.secure_aggregation.clients)
            },
            "data_transformation": {
                "transformations": len(self.data_transformation.transformations)
            }
        }
        
        return report
