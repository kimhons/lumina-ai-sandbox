"""
Learning Algorithm Factory for Lumina AI Enhanced Learning System

This module provides a factory for creating and configuring various learning algorithms,
including meta-learning, transfer learning, reinforcement learning, and more.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Type
from dataclasses import dataclass
import os
import joblib
from abc import ABC, abstractmethod


@dataclass
class AlgorithmConfig:
    """Configuration for a learning algorithm."""
    algorithm_type: str
    parameters: Dict[str, Any]
    input_shape: Optional[Tuple] = None
    output_shape: Optional[Tuple] = None


class LearningAlgorithm(ABC):
    """
    Abstract base class for all learning algorithms.
    
    This class defines the interface that all learning algorithms must implement.
    """
    
    @abstractmethod
    def fit(self, X, y=None, **kwargs):
        """
        Fit the algorithm to the data.
        
        Args:
            X: Input features
            y: Target values (optional)
            **kwargs: Additional parameters for fitting
        """
        pass
    
    @abstractmethod
    def predict(self, X, **kwargs):
        """
        Make predictions using the fitted algorithm.
        
        Args:
            X: Input features
            **kwargs: Additional parameters for prediction
            
        Returns:
            predictions: Predicted values
        """
        pass
    
    @abstractmethod
    def save(self, filepath: str):
        """
        Save the algorithm to a file.
        
        Args:
            filepath: Path to save the algorithm
        """
        pass
    
    @classmethod
    @abstractmethod
    def load(cls, filepath: str) -> 'LearningAlgorithm':
        """
        Load an algorithm from a file.
        
        Args:
            filepath: Path to load the algorithm from
            
        Returns:
            algorithm: The loaded algorithm
        """
        pass


class ClassicalAlgorithm(LearningAlgorithm):
    """
    Wrapper for classical machine learning algorithms from scikit-learn.
    
    This class provides a common interface for various scikit-learn algorithms.
    """
    
    def __init__(self, algorithm_type: str, **kwargs):
        """
        Initialize the ClassicalAlgorithm.
        
        Args:
            algorithm_type: Type of algorithm to create
            **kwargs: Parameters for the algorithm
        """
        self.algorithm_type = algorithm_type
        self.params = kwargs
        self.model = self._create_model()
        
    def _create_model(self):
        """
        Create the underlying scikit-learn model.
        
        Returns:
            model: The created model
        """
        if self.algorithm_type == "random_forest":
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            if self.params.get("task") == "regression":
                # Remove task parameter as it's not used by scikit-learn
                params = {k: v for k, v in self.params.items() if k != "task"}
                return RandomForestRegressor(**params)
            else:
                # Remove task parameter as it's not used by scikit-learn
                params = {k: v for k, v in self.params.items() if k != "task"}
                return RandomForestClassifier(**params)
        elif self.algorithm_type == "gradient_boosting":
            from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
            if self.params.get("task") == "regression":
                params = {k: v for k, v in self.params.items() if k != "task"}
                return GradientBoostingRegressor(**params)
            else:
                params = {k: v for k, v in self.params.items() if k != "task"}
                return GradientBoostingClassifier(**params)
        elif self.algorithm_type == "svm":
            from sklearn.svm import SVC, SVR
            if self.params.get("task") == "regression":
                params = {k: v for k, v in self.params.items() if k != "task"}
                return SVR(**params)
            else:
                params = {k: v for k, v in self.params.items() if k != "task"}
                return SVC(**params)
        elif self.algorithm_type == "logistic_regression":
            from sklearn.linear_model import LogisticRegression
            params = {k: v for k, v in self.params.items() if k != "task"}
            return LogisticRegression(**params)
        elif self.algorithm_type == "linear_regression":
            from sklearn.linear_model import LinearRegression
            params = {k: v for k, v in self.params.items() if k != "task"}
            return LinearRegression(**params)
        elif self.algorithm_type == "knn":
            from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
            if self.params.get("task") == "regression":
                params = {k: v for k, v in self.params.items() if k != "task"}
                return KNeighborsRegressor(**params)
            else:
                params = {k: v for k, v in self.params.items() if k != "task"}
                return KNeighborsClassifier(**params)
        else:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
    
    def fit(self, X, y=None, **kwargs):
        """
        Fit the algorithm to the data.
        
        Args:
            X: Input features
            y: Target values
            **kwargs: Additional parameters for fitting
        """
        return self.model.fit(X, y, **kwargs)
    
    def predict(self, X, **kwargs):
        """
        Make predictions using the fitted algorithm.
        
        Args:
            X: Input features
            **kwargs: Additional parameters for prediction
            
        Returns:
            predictions: Predicted values
        """
        return self.model.predict(X, **kwargs)
    
    def predict_proba(self, X, **kwargs):
        """
        Predict class probabilities for X.
        
        Args:
            X: Input features
            **kwargs: Additional parameters for prediction
            
        Returns:
            probabilities: Class probabilities
        """
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X, **kwargs)
        else:
            raise AttributeError(f"{self.algorithm_type} does not support predict_proba")
    
    def save(self, filepath: str):
        """
        Save the algorithm to a file.
        
        Args:
            filepath: Path to save the algorithm
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model and metadata
        joblib.dump({
            "algorithm_type": self.algorithm_type,
            "params": self.params,
            "model": self.model
        }, filepath)
    
    @classmethod
    def load(cls, filepath: str) -> 'ClassicalAlgorithm':
        """
        Load an algorithm from a file.
        
        Args:
            filepath: Path to load the algorithm from
            
        Returns:
            algorithm: The loaded algorithm
        """
        data = joblib.load(filepath)
        
        algorithm = cls(algorithm_type=data["algorithm_type"], **data["params"])
        algorithm.model = data["model"]
        
        return algorithm


class DeepLearningAlgorithm(LearningAlgorithm):
    """
    Wrapper for deep learning algorithms using TensorFlow/Keras.
    
    This class provides a common interface for various deep learning architectures.
    """
    
    def __init__(self, algorithm_type: str, input_shape: Tuple = None, output_shape: Tuple = None, **kwargs):
        """
        Initialize the DeepLearningAlgorithm.
        
        Args:
            algorithm_type: Type of algorithm to create
            input_shape: Shape of the input data
            output_shape: Shape of the output data
            **kwargs: Parameters for the algorithm
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError("TensorFlow is required for deep learning algorithms")
            
        self.algorithm_type = algorithm_type
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.params = kwargs
        self.model = None
        
        # Only create model if shapes are provided
        if input_shape is not None and output_shape is not None:
            self.model = self._create_model()
    
    def _create_model(self):
        """
        Create the underlying TensorFlow/Keras model.
        
        Returns:
            model: The created model
        """
        import tensorflow as tf
        from tensorflow.keras.models import Sequential, Model
        from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, LSTM, Dropout, Input
        
        if self.algorithm_type == "mlp":
            # Multi-layer perceptron
            model = Sequential()
            model.add(Input(shape=self.input_shape))
            
            # Add hidden layers
            hidden_layers = self.params.get("hidden_layers", [64, 32])
            activation = self.params.get("activation", "relu")
            dropout_rate = self.params.get("dropout_rate", 0.0)
            
            for units in hidden_layers:
                model.add(Dense(units, activation=activation))
                if dropout_rate > 0:
                    model.add(Dropout(dropout_rate))
            
            # Add output layer
            output_units = self.output_shape[0] if isinstance(self.output_shape, tuple) else self.output_shape
            output_activation = self.params.get("output_activation", "softmax")
            model.add(Dense(output_units, activation=output_activation))
            
        elif self.algorithm_type == "cnn":
            # Convolutional neural network
            model = Sequential()
            
            # Add convolutional layers
            filters = self.params.get("filters", [32, 64])
            kernel_size = self.params.get("kernel_size", (3, 3))
            pool_size = self.params.get("pool_size", (2, 2))
            activation = self.params.get("activation", "relu")
            
            model.add(Input(shape=self.input_shape))
            
            for filter_count in filters:
                model.add(Conv2D(filter_count, kernel_size, activation=activation))
                model.add(MaxPooling2D(pool_size=pool_size))
            
            model.add(Flatten())
            
            # Add dense layers
            dense_layers = self.params.get("dense_layers", [128])
            dropout_rate = self.params.get("dropout_rate", 0.0)
            
            for units in dense_layers:
                model.add(Dense(units, activation=activation))
                if dropout_rate > 0:
                    model.add(Dropout(dropout_rate))
            
            # Add output layer
            output_units = self.output_shape[0] if isinstance(self.output_shape, tuple) else self.output_shape
            output_activation = self.params.get("output_activation", "softmax")
            model.add(Dense(output_units, activation=output_activation))
            
        elif self.algorithm_type == "rnn":
            # Recurrent neural network
            model = Sequential()
            
            # Add LSTM layers
            lstm_units = self.params.get("lstm_units", [64, 32])
            dropout_rate = self.params.get("dropout_rate", 0.0)
            recurrent_dropout = self.params.get("recurrent_dropout", 0.0)
            
            model.add(Input(shape=self.input_shape))
            
            for i, units in enumerate(lstm_units):
                return_sequences = i < len(lstm_units) - 1  # Return sequences for all but the last layer
                model.add(LSTM(units, return_sequences=return_sequences, 
                              dropout=dropout_rate, recurrent_dropout=recurrent_dropout))
            
            # Add dense layers
            dense_layers = self.params.get("dense_layers", [32])
            activation = self.params.get("activation", "relu")
            
            for units in dense_layers:
                model.add(Dense(units, activation=activation))
                if dropout_rate > 0:
                    model.add(Dropout(dropout_rate))
            
            # Add output layer
            output_units = self.output_shape[0] if isinstance(self.output_shape, tuple) else self.output_shape
            output_activation = self.params.get("output_activation", "softmax")
            model.add(Dense(output_units, activation=output_activation))
            
        else:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
        
        # Compile the model
        loss = self.params.get("loss", "categorical_crossentropy")
        optimizer_name = self.params.get("optimizer", "adam")
        learning_rate = self.params.get("learning_rate", 0.001)
        
        if optimizer_name == "adam":
            optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        elif optimizer_name == "sgd":
            optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
        elif optimizer_name == "rmsprop":
            optimizer = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
        else:
            optimizer = optimizer_name
            
        metrics = self.params.get("metrics", ["accuracy"])
        
        model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
        
        return model
    
    def fit(self, X, y=None, **kwargs):
        """
        Fit the algorithm to the data.
        
        Args:
            X: Input features
            y: Target values
            **kwargs: Additional parameters for fitting
        """
        if self.model is None:
            if self.input_shape is None:
                # Infer input shape from data
                if isinstance(X, np.ndarray):
                    self.input_shape = X.shape[1:]
                else:
                    raise ValueError("Cannot infer input shape from data")
                    
            if self.output_shape is None and y is not None:
                # Infer output shape from targets
                if isinstance(y, np.ndarray):
                    if len(y.shape) == 1:
                        # For binary classification or regression
                        self.output_shape = 1
                    else:
                        # For multi-class classification
                        self.output_shape = y.shape[1]
                else:
                    raise ValueError("Cannot infer output shape from targets")
            
            # Create model with inferred shapes
            self.model = self._create_model()
        
        # Set default values for training
        epochs = kwargs.pop("epochs", 10)
        batch_size = kwargs.pop("batch_size", 32)
        validation_split = kwargs.pop("validation_split", 0.0)
        validation_data = kwargs.pop("validation_data", None)
        
        return self.model.fit(
            X, y, 
            epochs=epochs, 
            batch_size=batch_size, 
            validation_split=validation_split,
            validation_data=validation_data,
            **kwargs
        )
    
    def predict(self, X, **kwargs):
        """
        Make predictions using the fitted algorithm.
        
        Args:
            X: Input features
            **kwargs: Additional parameters for prediction
            
        Returns:
            predictions: Predicted values
        """
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
            
        return self.model.predict(X, **kwargs)
    
    def save(self, filepath: str):
        """
        Save the algorithm to a file.
        
        Args:
            filepath: Path to save the algorithm
        """
        if self.model is None:
            raise ValueError("Model must be created before saving")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model architecture and weights
        model_path = filepath + ".keras"
        self.model.save(model_path)
        
        # Save metadata
        metadata_path = filepath + ".json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump({
                "algorithm_type": self.algorithm_type,
                "input_shape": self.input_shape,
                "output_shape": self.output_shape,
                "params": {k: v for k, v in self.params.items() if isinstance(v, (str, int, float, bool, list, dict))}
            }, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'DeepLearningAlgorithm':
        """
        Load an algorithm from a file.
        
        Args:
            filepath: Path to load the algorithm from
            
        Returns:
            algorithm: The loaded algorithm
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError("TensorFlow is required for deep learning algorithms")
            
        # Load metadata
        metadata_path = filepath + ".json"
        import json
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        # Create algorithm instance
        algorithm = cls(
            algorithm_type=metadata["algorithm_type"],
            input_shape=metadata["input_shape"],
            output_shape=metadata["output_shape"],
            **metadata["params"]
        )
        
        # Load model
        model_path = filepath + ".keras"
        algorithm.model = tf.keras.models.load_model(model_path)
        
        return algorithm


class TransferLearningAlgorithm(DeepLearningAlgorithm):
    """
    Implementation of transfer learning algorithms using pre-trained models.
    
    This class extends DeepLearningAlgorithm to support transfer learning.
    """
    
    def __init__(self, base_model: str, input_shape: Tuple = None, output_shape: Tuple = None, **kwargs):
        """
        Initialize the TransferLearningAlgorithm.
        
        Args:
            base_model: Name of the pre-trained model to use
            input_shape: Shape of the input data
            output_shape: Shape of the output data
            **kwargs: Parameters for the algorithm
        """
        self.base_model = base_model
        super().__init__("transfer", input_shape, output_shape, **kwargs)
    
    def _create_model(self):
        """
        Create a transfer learning model using a pre-trained base model.
        
        Returns:
            model: The created model
        """
        import tensorflow as tf
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Dropout
        
        # Load pre-trained model
        if self.base_model == "resnet50":
            from tensorflow.keras.applications import ResNet50
            base = ResNet50(weights='imagenet', include_top=False, input_shape=self.input_shape)
        elif self.base_model == "vgg16":
            from tensorflow.keras.applications import VGG16
            base = VGG16(weights='imagenet', include_top=False, input_shape=self.input_shape)
        elif self.base_model == "mobilenet":
            from tensorflow.keras.applications import MobileNetV2
            base = MobileNetV2(weights='imagenet', include_top=False, input_shape=self.input_shape)
        elif self.base_model == "inception":
            from tensorflow.keras.applications import InceptionV3
            base = InceptionV3(weights='imagenet', include_top=False, input_shape=self.input_shape)
        else:
            raise ValueError(f"Unknown base model: {self.base_model}")
        
        # Freeze base model layers
        trainable_layers = self.params.get("trainable_layers", 0)
        if trainable_layers > 0:
            # Make the last N layers trainable
            for layer in base.layers[:-trainable_layers]:
                layer.trainable = False
            for layer in base.layers[-trainable_layers:]:
                layer.trainable = True
        else:
            # Freeze all layers
            base.trainable = False
        
        # Add custom layers on top
        x = base.output
        x = GlobalAveragePooling2D()(x)
        
        # Add dense layers
        dense_layers = self.params.get("dense_layers", [1024, 512])
        activation = self.params.get("activation", "relu")
        dropout_rate = self.params.get("dropout_rate", 0.0)
        
        for units in dense_layers:
            x = Dense(units, activation=activation)(x)
            if dropout_rate > 0:
                x = Dropout(dropout_rate)(x)
        
        # Add output layer
        output_units = self.output_shape[0] if isinstance(self.output_shape, tuple) else self.output_shape
        output_activation = self.params.get("output_activation", "softmax")
        predictions = Dense(output_units, activation=output_activation)(x)
        
        # Create model
        model = Model(inputs=base.input, outputs=predictions)
        
        # Compile model
        loss = self.params.get("loss", "categorical_crossentropy")
        optimizer_name = self.params.get("optimizer", "adam")
        learning_rate = self.params.get("learning_rate", 0.001)
        
        if optimizer_name == "adam":
            optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        elif optimizer_name == "sgd":
            optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
        elif optimizer_name == "rmsprop":
            optimizer = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
        else:
            optimizer = optimizer_name
            
        metrics = self.params.get("metrics", ["accuracy"])
        
        model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
        
        return model
    
    def save(self, filepath: str):
        """
        Save the algorithm to a file.
        
        Args:
            filepath: Path to save the algorithm
        """
        if self.model is None:
            raise ValueError("Model must be created before saving")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model architecture and weights
        model_path = filepath + ".keras"
        self.model.save(model_path)
        
        # Save metadata
        metadata_path = filepath + ".json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump({
                "algorithm_type": "transfer",
                "base_model": self.base_model,
                "input_shape": self.input_shape,
                "output_shape": self.output_shape,
                "params": {k: v for k, v in self.params.items() if isinstance(v, (str, int, float, bool, list, dict))}
            }, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'TransferLearningAlgorithm':
        """
        Load an algorithm from a file.
        
        Args:
            filepath: Path to load the algorithm from
            
        Returns:
            algorithm: The loaded algorithm
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError("TensorFlow is required for transfer learning algorithms")
            
        # Load metadata
        metadata_path = filepath + ".json"
        import json
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        # Create algorithm instance
        algorithm = cls(
            base_model=metadata["base_model"],
            input_shape=metadata["input_shape"],
            output_shape=metadata["output_shape"],
            **metadata["params"]
        )
        
        # Load model
        model_path = filepath + ".keras"
        algorithm.model = tf.keras.models.load_model(model_path)
        
        return algorithm


class ReinforcementLearningAlgorithm(LearningAlgorithm):
    """
    Implementation of reinforcement learning algorithms.
    
    This class provides a common interface for various reinforcement learning algorithms.
    """
    
    def __init__(self, algorithm_type: str, state_shape: Tuple, action_shape: Tuple, **kwargs):
        """
        Initialize the ReinforcementLearningAlgorithm.
        
        Args:
            algorithm_type: Type of algorithm to create
            state_shape: Shape of the state space
            action_shape: Shape of the action space
            **kwargs: Parameters for the algorithm
        """
        self.algorithm_type = algorithm_type
        self.state_shape = state_shape
        self.action_shape = action_shape
        self.params = kwargs
        self.model = None
        
        # Initialize the algorithm
        self._initialize_algorithm()
    
    def _initialize_algorithm(self):
        """Initialize the reinforcement learning algorithm."""
        if self.algorithm_type == "dqn":
            try:
                from stable_baselines3 import DQN
                
                # Create environment wrapper for the algorithm
                from gym import spaces
                import numpy as np
                
                class EnvWrapper:
                    def __init__(self, state_shape, action_shape):
                        self.observation_space = spaces.Box(
                            low=-np.inf, high=np.inf, shape=state_shape, dtype=np.float32
                        )
                        if len(action_shape) == 1:
                            self.action_space = spaces.Discrete(action_shape[0])
                        else:
                            self.action_space = spaces.Box(
                                low=-np.inf, high=np.inf, shape=action_shape, dtype=np.float32
                            )
                
                env = EnvWrapper(self.state_shape, self.action_shape)
                
                # Create DQN model
                self.model = DQN(
                    "MlpPolicy",
                    env,
                    learning_rate=self.params.get("learning_rate", 0.001),
                    buffer_size=self.params.get("buffer_size", 10000),
                    learning_starts=self.params.get("learning_starts", 1000),
                    batch_size=self.params.get("batch_size", 64),
                    tau=self.params.get("tau", 1.0),
                    gamma=self.params.get("gamma", 0.99),
                    train_freq=self.params.get("train_freq", 4),
                    gradient_steps=self.params.get("gradient_steps", 1),
                    target_update_interval=self.params.get("target_update_interval", 1000),
                    exploration_fraction=self.params.get("exploration_fraction", 0.1),
                    exploration_initial_eps=self.params.get("exploration_initial_eps", 1.0),
                    exploration_final_eps=self.params.get("exploration_final_eps", 0.05),
                    max_grad_norm=self.params.get("max_grad_norm", 10),
                    verbose=self.params.get("verbose", 0)
                )
            except ImportError:
                raise ImportError("stable-baselines3 is required for DQN algorithm")
        elif self.algorithm_type == "ppo":
            try:
                from stable_baselines3 import PPO
                
                # Create environment wrapper for the algorithm
                from gym import spaces
                import numpy as np
                
                class EnvWrapper:
                    def __init__(self, state_shape, action_shape):
                        self.observation_space = spaces.Box(
                            low=-np.inf, high=np.inf, shape=state_shape, dtype=np.float32
                        )
                        if len(action_shape) == 1:
                            self.action_space = spaces.Discrete(action_shape[0])
                        else:
                            self.action_space = spaces.Box(
                                low=-np.inf, high=np.inf, shape=action_shape, dtype=np.float32
                            )
                
                env = EnvWrapper(self.state_shape, self.action_shape)
                
                # Create PPO model
                self.model = PPO(
                    "MlpPolicy",
                    env,
                    learning_rate=self.params.get("learning_rate", 0.0003),
                    n_steps=self.params.get("n_steps", 2048),
                    batch_size=self.params.get("batch_size", 64),
                    n_epochs=self.params.get("n_epochs", 10),
                    gamma=self.params.get("gamma", 0.99),
                    gae_lambda=self.params.get("gae_lambda", 0.95),
                    clip_range=self.params.get("clip_range", 0.2),
                    clip_range_vf=self.params.get("clip_range_vf", None),
                    ent_coef=self.params.get("ent_coef", 0.0),
                    vf_coef=self.params.get("vf_coef", 0.5),
                    max_grad_norm=self.params.get("max_grad_norm", 0.5),
                    use_sde=self.params.get("use_sde", False),
                    sde_sample_freq=self.params.get("sde_sample_freq", -1),
                    target_kl=self.params.get("target_kl", None),
                    verbose=self.params.get("verbose", 0)
                )
            except ImportError:
                raise ImportError("stable-baselines3 is required for PPO algorithm")
        else:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
    
    def fit(self, X, y=None, **kwargs):
        """
        Train the reinforcement learning algorithm.
        
        For RL algorithms, X should be a list of (state, action, reward, next_state, done) tuples,
        or a function that generates these tuples.
        
        Args:
            X: Training data or environment
            y: Not used
            **kwargs: Additional parameters for training
        """
        if self.model is None:
            raise ValueError("Algorithm must be initialized before training")
            
        # For RL algorithms, we typically train for a number of timesteps
        total_timesteps = kwargs.get("total_timesteps", 10000)
        
        if callable(X):
            # X is a function that generates training data
            # This is not directly supported by stable-baselines3, so we'd need custom logic
            raise NotImplementedError("Training with a data generation function is not implemented")
        elif isinstance(X, list) and len(X) > 0 and isinstance(X[0], tuple):
            # X is a list of (state, action, reward, next_state, done) tuples
            # This is not directly supported by stable-baselines3, so we'd need custom logic
            raise NotImplementedError("Training with a list of tuples is not implemented")
        else:
            # Assume X is a gym environment
            self.model.learn(total_timesteps=total_timesteps, **kwargs)
    
    def predict(self, X, **kwargs):
        """
        Make predictions (actions) using the trained algorithm.
        
        Args:
            X: States to predict actions for
            **kwargs: Additional parameters for prediction
            
        Returns:
            actions: Predicted actions
        """
        if self.model is None:
            raise ValueError("Algorithm must be trained before prediction")
            
        # For RL algorithms, X should be a state or batch of states
        deterministic = kwargs.get("deterministic", True)
        
        if isinstance(X, list) or isinstance(X, np.ndarray) and len(X.shape) > 1:
            # Batch of states
            actions = []
            for state in X:
                action, _ = self.model.predict(state, deterministic=deterministic)
                actions.append(action)
            return np.array(actions)
        else:
            # Single state
            action, _ = self.model.predict(X, deterministic=deterministic)
            return action
    
    def save(self, filepath: str):
        """
        Save the algorithm to a file.
        
        Args:
            filepath: Path to save the algorithm
        """
        if self.model is None:
            raise ValueError("Algorithm must be initialized before saving")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        self.model.save(filepath)
        
        # Save metadata
        metadata_path = filepath + ".json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump({
                "algorithm_type": self.algorithm_type,
                "state_shape": self.state_shape,
                "action_shape": self.action_shape,
                "params": {k: v for k, v in self.params.items() if isinstance(v, (str, int, float, bool, list, dict))}
            }, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'ReinforcementLearningAlgorithm':
        """
        Load an algorithm from a file.
        
        Args:
            filepath: Path to load the algorithm from
            
        Returns:
            algorithm: The loaded algorithm
        """
        # Load metadata
        metadata_path = filepath + ".json"
        import json
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        # Create algorithm instance
        algorithm = cls(
            algorithm_type=metadata["algorithm_type"],
            state_shape=metadata["state_shape"],
            action_shape=metadata["action_shape"],
            **metadata["params"]
        )
        
        # Load model
        if algorithm.algorithm_type == "dqn":
            from stable_baselines3 import DQN
            algorithm.model = DQN.load(filepath)
        elif algorithm.algorithm_type == "ppo":
            from stable_baselines3 import PPO
            algorithm.model = PPO.load(filepath)
        
        return algorithm


class BayesianAlgorithm(LearningAlgorithm):
    """
    Implementation of Bayesian learning algorithms.
    
    This class provides a common interface for various Bayesian learning algorithms.
    """
    
    def __init__(self, algorithm_type: str, **kwargs):
        """
        Initialize the BayesianAlgorithm.
        
        Args:
            algorithm_type: Type of algorithm to create
            **kwargs: Parameters for the algorithm
        """
        self.algorithm_type = algorithm_type
        self.params = kwargs
        self.model = self._create_model()
    
    def _create_model(self):
        """
        Create the underlying Bayesian model.
        
        Returns:
            model: The created model
        """
        if self.algorithm_type == "gaussian_process":
            from sklearn.gaussian_process import GaussianProcessRegressor, GaussianProcessClassifier
            from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
            
            # Create kernel
            kernel_type = self.params.get("kernel", "rbf")
            if kernel_type == "rbf":
                length_scale = self.params.get("length_scale", 1.0)
                kernel = RBF(length_scale=length_scale)
            elif kernel_type == "constant_rbf":
                constant = self.params.get("constant", 1.0)
                length_scale = self.params.get("length_scale", 1.0)
                kernel = C(constant) * RBF(length_scale=length_scale)
            else:
                raise ValueError(f"Unknown kernel type: {kernel_type}")
            
            # Create model
            task = self.params.get("task", "regression")
            if task == "regression":
                alpha = self.params.get("alpha", 1e-10)
                normalize_y = self.params.get("normalize_y", False)
                n_restarts_optimizer = self.params.get("n_restarts_optimizer", 0)
                
                return GaussianProcessRegressor(
                    kernel=kernel,
                    alpha=alpha,
                    normalize_y=normalize_y,
                    n_restarts_optimizer=n_restarts_optimizer
                )
            else:
                n_restarts_optimizer = self.params.get("n_restarts_optimizer", 0)
                max_iter_predict = self.params.get("max_iter_predict", 100)
                
                return GaussianProcessClassifier(
                    kernel=kernel,
                    n_restarts_optimizer=n_restarts_optimizer,
                    max_iter_predict=max_iter_predict
                )
        elif self.algorithm_type == "bayesian_ridge":
            from sklearn.linear_model import BayesianRidge
            
            n_iter = self.params.get("n_iter", 300)
            tol = self.params.get("tol", 1e-3)
            alpha_1 = self.params.get("alpha_1", 1e-6)
            alpha_2 = self.params.get("alpha_2", 1e-6)
            lambda_1 = self.params.get("lambda_1", 1e-6)
            lambda_2 = self.params.get("lambda_2", 1e-6)
            
            return BayesianRidge(
                n_iter=n_iter,
                tol=tol,
                alpha_1=alpha_1,
                alpha_2=alpha_2,
                lambda_1=lambda_1,
                lambda_2=lambda_2
            )
        elif self.algorithm_type == "bayesian_neural_network":
            try:
                import tensorflow as tf
                import tensorflow_probability as tfp
                
                # Create a Bayesian neural network using TensorFlow Probability
                input_shape = self.params.get("input_shape")
                if input_shape is None:
                    raise ValueError("input_shape must be provided for Bayesian neural network")
                    
                output_shape = self.params.get("output_shape")
                if output_shape is None:
                    raise ValueError("output_shape must be provided for Bayesian neural network")
                
                hidden_layers = self.params.get("hidden_layers", [64, 32])
                activation = self.params.get("activation", "relu")
                
                # Define the model
                model = tf.keras.Sequential()
                model.add(tf.keras.layers.Input(shape=input_shape))
                
                # Add hidden layers with Bayesian weights
                for units in hidden_layers:
                    kernel_divergence_fn = tfp.layers.default_mean_field_normal_fn(
                        loc_initializer=tf.keras.initializers.he_normal(),
                        untransformed_scale_initializer=tf.keras.initializers.random_normal(mean=-3.0, stddev=0.1),
                        loc_regularizer=None,
                        untransformed_scale_regularizer=None
                    )
                    
                    bias_divergence_fn = tfp.layers.default_mean_field_normal_fn(
                        loc_initializer=tf.keras.initializers.he_normal(),
                        untransformed_scale_initializer=tf.keras.initializers.random_normal(mean=-3.0, stddev=0.1),
                        loc_regularizer=None,
                        untransformed_scale_regularizer=None
                    )
                    
                    model.add(tfp.layers.DenseVariational(
                        units=units,
                        make_posterior_fn=kernel_divergence_fn,
                        make_prior_fn=tfp.layers.default_multivariate_normal_fn,
                        bias_posterior_fn=bias_divergence_fn,
                        bias_prior_fn=tfp.layers.default_multivariate_normal_fn,
                        activation=activation
                    ))
                
                # Add output layer
                model.add(tfp.layers.DenseVariational(
                    units=output_shape,
                    make_posterior_fn=kernel_divergence_fn,
                    make_prior_fn=tfp.layers.default_multivariate_normal_fn,
                    bias_posterior_fn=bias_divergence_fn,
                    bias_prior_fn=tfp.layers.default_multivariate_normal_fn,
                    activation=self.params.get("output_activation", "linear")
                ))
                
                # Compile the model
                loss = self.params.get("loss", "mse")
                optimizer_name = self.params.get("optimizer", "adam")
                learning_rate = self.params.get("learning_rate", 0.001)
                
                if optimizer_name == "adam":
                    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
                elif optimizer_name == "sgd":
                    optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
                elif optimizer_name == "rmsprop":
                    optimizer = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
                else:
                    optimizer = optimizer_name
                    
                metrics = self.params.get("metrics", ["mse"])
                
                model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
                
                return model
            except ImportError:
                raise ImportError("TensorFlow and TensorFlow Probability are required for Bayesian neural networks")
        else:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
    
    def fit(self, X, y=None, **kwargs):
        """
        Fit the algorithm to the data.
        
        Args:
            X: Input features
            y: Target values
            **kwargs: Additional parameters for fitting
        """
        if self.algorithm_type == "bayesian_neural_network":
            # For Bayesian neural networks, we use Keras fit method
            epochs = kwargs.pop("epochs", 10)
            batch_size = kwargs.pop("batch_size", 32)
            validation_split = kwargs.pop("validation_split", 0.0)
            validation_data = kwargs.pop("validation_data", None)
            
            return self.model.fit(
                X, y, 
                epochs=epochs, 
                batch_size=batch_size, 
                validation_split=validation_split,
                validation_data=validation_data,
                **kwargs
            )
        else:
            # For scikit-learn models
            return self.model.fit(X, y, **kwargs)
    
    def predict(self, X, **kwargs):
        """
        Make predictions using the fitted algorithm.
        
        Args:
            X: Input features
            **kwargs: Additional parameters for prediction
            
        Returns:
            predictions: Predicted values
        """
        return self.model.predict(X, **kwargs)
    
    def predict_with_uncertainty(self, X, **kwargs):
        """
        Make predictions with uncertainty estimates.
        
        Args:
            X: Input features
            **kwargs: Additional parameters for prediction
            
        Returns:
            predictions: Predicted values
            uncertainty: Uncertainty estimates
        """
        if self.algorithm_type == "gaussian_process":
            # Gaussian processes provide uncertainty estimates
            if hasattr(self.model, "predict_proba"):
                # For classification
                proba = self.model.predict_proba(X)
                predictions = np.argmax(proba, axis=1)
                # Use entropy as uncertainty measure
                uncertainty = -np.sum(proba * np.log(proba + 1e-10), axis=1)
                return predictions, uncertainty
            else:
                # For regression
                predictions, std = self.model.predict(X, return_std=True)
                return predictions, std
        elif self.algorithm_type == "bayesian_neural_network":
            # For Bayesian neural networks, we need to perform multiple forward passes
            n_samples = kwargs.get("n_samples", 100)
            
            # Collect predictions from multiple forward passes
            predictions = []
            for _ in range(n_samples):
                pred = self.model.predict(X)
                predictions.append(pred)
                
            # Calculate mean and standard deviation
            predictions = np.array(predictions)
            mean_prediction = np.mean(predictions, axis=0)
            uncertainty = np.std(predictions, axis=0)
            
            return mean_prediction, uncertainty
        else:
            # For other models, we don't have built-in uncertainty estimates
            predictions = self.model.predict(X)
            # Return zeros as uncertainty (not meaningful)
            uncertainty = np.zeros_like(predictions)
            return predictions, uncertainty
    
    def save(self, filepath: str):
        """
        Save the algorithm to a file.
        
        Args:
            filepath: Path to save the algorithm
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if self.algorithm_type == "bayesian_neural_network":
            # Save Keras model
            model_path = filepath + ".keras"
            self.model.save(model_path)
            
            # Save metadata
            metadata_path = filepath + ".json"
            import json
            with open(metadata_path, 'w') as f:
                json.dump({
                    "algorithm_type": self.algorithm_type,
                    "params": {k: v for k, v in self.params.items() if isinstance(v, (str, int, float, bool, list, dict))}
                }, f)
        else:
            # Save scikit-learn model
            joblib.dump({
                "algorithm_type": self.algorithm_type,
                "params": self.params,
                "model": self.model
            }, filepath)
    
    @classmethod
    def load(cls, filepath: str) -> 'BayesianAlgorithm':
        """
        Load an algorithm from a file.
        
        Args:
            filepath: Path to load the algorithm from
            
        Returns:
            algorithm: The loaded algorithm
        """
        if filepath.endswith(".keras") or os.path.exists(filepath + ".keras"):
            # Load Keras model
            import tensorflow as tf
            
            # Load metadata
            metadata_path = filepath + ".json" if not filepath.endswith(".keras") else filepath.replace(".keras", ".json")
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
            # Create algorithm instance
            algorithm = cls(algorithm_type=metadata["algorithm_type"], **metadata["params"])
            
            # Load model
            model_path = filepath if filepath.endswith(".keras") else filepath + ".keras"
            algorithm.model = tf.keras.models.load_model(model_path)
            
            return algorithm
        else:
            # Load scikit-learn model
            data = joblib.load(filepath)
            
            algorithm = cls(algorithm_type=data["algorithm_type"], **data["params"])
            algorithm.model = data["model"]
            
            return algorithm


class LearningAlgorithmFactory:
    """
    Factory for creating and configuring various learning algorithms.
    
    This class provides methods for creating different types of learning algorithms,
    including classical, deep learning, transfer learning, reinforcement learning,
    and Bayesian algorithms.
    """
    
    @staticmethod
    def create_algorithm(config: AlgorithmConfig) -> LearningAlgorithm:
        """
        Create a learning algorithm based on configuration.
        
        Args:
            config: Configuration for the algorithm
            
        Returns:
            algorithm: The created learning algorithm
        """
        algorithm_type = config.algorithm_type
        params = config.parameters
        
        # Classical machine learning algorithms
        if algorithm_type in ["random_forest", "gradient_boosting", "svm", 
                             "logistic_regression", "linear_regression", "knn"]:
            return ClassicalAlgorithm(algorithm_type, **params)
            
        # Deep learning algorithms
        elif algorithm_type in ["mlp", "cnn", "rnn"]:
            return DeepLearningAlgorithm(algorithm_type, 
                                        input_shape=config.input_shape, 
                                        output_shape=config.output_shape, 
                                        **params)
            
        # Transfer learning algorithms
        elif algorithm_type == "transfer":
            base_model = params.pop("base_model", "resnet50")
            return TransferLearningAlgorithm(base_model, 
                                           input_shape=config.input_shape, 
                                           output_shape=config.output_shape, 
                                           **params)
            
        # Reinforcement learning algorithms
        elif algorithm_type in ["dqn", "ppo"]:
            state_shape = config.input_shape
            action_shape = config.output_shape
            return ReinforcementLearningAlgorithm(algorithm_type, 
                                                state_shape=state_shape, 
                                                action_shape=action_shape, 
                                                **params)
            
        # Bayesian learning algorithms
        elif algorithm_type in ["gaussian_process", "bayesian_ridge", "bayesian_neural_network"]:
            if algorithm_type == "bayesian_neural_network":
                # Add shapes to params for Bayesian neural network
                params["input_shape"] = config.input_shape
                params["output_shape"] = config.output_shape
            return BayesianAlgorithm(algorithm_type, **params)
            
        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
    
    @staticmethod
    def get_algorithm_types() -> Dict[str, List[str]]:
        """
        Get a dictionary of available algorithm types grouped by category.
        
        Returns:
            algorithm_types: Dictionary of algorithm types by category
        """
        return {
            "classical": [
                "random_forest",
                "gradient_boosting",
                "svm",
                "logistic_regression",
                "linear_regression",
                "knn"
            ],
            "deep_learning": [
                "mlp",
                "cnn",
                "rnn"
            ],
            "transfer_learning": [
                "transfer"
            ],
            "reinforcement_learning": [
                "dqn",
                "ppo"
            ],
            "bayesian": [
                "gaussian_process",
                "bayesian_ridge",
                "bayesian_neural_network"
            ]
        }
    
    @staticmethod
    def get_default_parameters(algorithm_type: str) -> Dict[str, Any]:
        """
        Get default parameters for a specific algorithm type.
        
        Args:
            algorithm_type: Type of algorithm
            
        Returns:
            parameters: Default parameters for the algorithm
        """
        # Classical algorithms
        if algorithm_type == "random_forest":
            return {
                "n_estimators": 100,
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "task": "classification"
            }
        elif algorithm_type == "gradient_boosting":
            return {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 3,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "task": "classification"
            }
        elif algorithm_type == "svm":
            return {
                "C": 1.0,
                "kernel": "rbf",
                "gamma": "scale",
                "task": "classification"
            }
        elif algorithm_type == "logistic_regression":
            return {
                "C": 1.0,
                "penalty": "l2",
                "solver": "lbfgs",
                "max_iter": 100
            }
        elif algorithm_type == "linear_regression":
            return {
                "fit_intercept": True,
                "normalize": False
            }
        elif algorithm_type == "knn":
            return {
                "n_neighbors": 5,
                "weights": "uniform",
                "algorithm": "auto",
                "task": "classification"
            }
            
        # Deep learning algorithms
        elif algorithm_type == "mlp":
            return {
                "hidden_layers": [64, 32],
                "activation": "relu",
                "dropout_rate": 0.2,
                "output_activation": "softmax",
                "loss": "categorical_crossentropy",
                "optimizer": "adam",
                "learning_rate": 0.001,
                "metrics": ["accuracy"]
            }
        elif algorithm_type == "cnn":
            return {
                "filters": [32, 64],
                "kernel_size": (3, 3),
                "pool_size": (2, 2),
                "activation": "relu",
                "dense_layers": [128],
                "dropout_rate": 0.2,
                "output_activation": "softmax",
                "loss": "categorical_crossentropy",
                "optimizer": "adam",
                "learning_rate": 0.001,
                "metrics": ["accuracy"]
            }
        elif algorithm_type == "rnn":
            return {
                "lstm_units": [64, 32],
                "dropout_rate": 0.2,
                "recurrent_dropout": 0.2,
                "dense_layers": [32],
                "activation": "relu",
                "output_activation": "softmax",
                "loss": "categorical_crossentropy",
                "optimizer": "adam",
                "learning_rate": 0.001,
                "metrics": ["accuracy"]
            }
            
        # Transfer learning algorithms
        elif algorithm_type == "transfer":
            return {
                "base_model": "resnet50",
                "trainable_layers": 0,
                "dense_layers": [1024, 512],
                "activation": "relu",
                "dropout_rate": 0.5,
                "output_activation": "softmax",
                "loss": "categorical_crossentropy",
                "optimizer": "adam",
                "learning_rate": 0.0001,
                "metrics": ["accuracy"]
            }
            
        # Reinforcement learning algorithms
        elif algorithm_type == "dqn":
            return {
                "learning_rate": 0.001,
                "buffer_size": 10000,
                "learning_starts": 1000,
                "batch_size": 64,
                "tau": 1.0,
                "gamma": 0.99,
                "train_freq": 4,
                "gradient_steps": 1,
                "target_update_interval": 1000,
                "exploration_fraction": 0.1,
                "exploration_initial_eps": 1.0,
                "exploration_final_eps": 0.05,
                "max_grad_norm": 10,
                "verbose": 0
            }
        elif algorithm_type == "ppo":
            return {
                "learning_rate": 0.0003,
                "n_steps": 2048,
                "batch_size": 64,
                "n_epochs": 10,
                "gamma": 0.99,
                "gae_lambda": 0.95,
                "clip_range": 0.2,
                "clip_range_vf": None,
                "ent_coef": 0.0,
                "vf_coef": 0.5,
                "max_grad_norm": 0.5,
                "use_sde": False,
                "sde_sample_freq": -1,
                "target_kl": None,
                "verbose": 0
            }
            
        # Bayesian algorithms
        elif algorithm_type == "gaussian_process":
            return {
                "kernel": "rbf",
                "length_scale": 1.0,
                "alpha": 1e-10,
                "normalize_y": False,
                "n_restarts_optimizer": 0,
                "task": "regression"
            }
        elif algorithm_type == "bayesian_ridge":
            return {
                "n_iter": 300,
                "tol": 1e-3,
                "alpha_1": 1e-6,
                "alpha_2": 1e-6,
                "lambda_1": 1e-6,
                "lambda_2": 1e-6
            }
        elif algorithm_type == "bayesian_neural_network":
            return {
                "hidden_layers": [64, 32],
                "activation": "relu",
                "output_activation": "linear",
                "loss": "mse",
                "optimizer": "adam",
                "learning_rate": 0.001,
                "metrics": ["mse"]
            }
        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
