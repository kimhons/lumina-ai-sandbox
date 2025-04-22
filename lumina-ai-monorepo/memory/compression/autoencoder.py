"""
Autoencoder Neural Compressor for Lumina AI.

This module implements an Autoencoder-based neural compression
for efficient storage of embeddings with non-linear dimensionality reduction.
"""

import os
import json
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from .base import NeuralCompressor

try:
    import tensorflow as tf
    from tensorflow.keras.models import Model, load_model
    from tensorflow.keras.layers import Input, Dense
except ImportError:
    raise ImportError("TensorFlow package not installed. Install with 'pip install tensorflow'")

class AutoencoderCompressor(NeuralCompressor):
    """Autoencoder-based neural compressor for non-linear dimensionality reduction."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the Autoencoder compressor.
        
        Args:
            model_path: Optional path to save/load the Autoencoder model
        """
        self.model_path = model_path or "./data/compression/autoencoder_model"
        self.encoder = None
        self.decoder = None
        self.autoencoder = None
        self.original_dim = None
        self.compressed_dim = None
        self.is_fitted = False
        self.logger = logging.getLogger(__name__)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def initialize(self, **kwargs) -> bool:
        """
        Initialize the neural compressor.
        
        Args:
            **kwargs: Compressor-specific initialization parameters
                - original_dim: Original dimensionality (required)
                - compressed_dim: Compressed dimensionality (required)
                - hidden_layers: List of hidden layer sizes (optional)
                - activation: Activation function (optional, default: 'relu')
                - training_data: Optional training data for fitting the model
                - epochs: Number of training epochs (optional, default: 50)
                - batch_size: Training batch size (optional, default: 32)
            
        Returns:
            True if initialization was successful, False otherwise
        """
        # Try to load existing model
        if os.path.exists(self.model_path):
            try:
                self.autoencoder = load_model(self.model_path)
                
                # Extract encoder and decoder parts
                input_layer = self.autoencoder.layers[0].input
                encoding_layer = self.autoencoder.get_layer('encoding').output
                self.encoder = Model(inputs=input_layer, outputs=encoding_layer)
                
                encoded_input = Input(shape=(self.compressed_dim,))
                decoder_layers = []
                found_encoding = False
                
                for layer in self.autoencoder.layers:
                    if layer.name == 'encoding':
                        found_encoding = True
                        continue
                    if found_encoding:
                        decoder_layers.append(layer)
                
                x = encoded_input
                for layer in decoder_layers:
                    x = layer(x)
                
                self.decoder = Model(inputs=encoded_input, outputs=x)
                
                # Get dimensions
                self.original_dim = self.autoencoder.input_shape[1]
                self.compressed_dim = encoding_layer.shape[1]
                self.is_fitted = True
                
                self.logger.info(f"Loaded Autoencoder model from {self.model_path}")
                return True
            except Exception as e:
                self.logger.error(f"Error loading Autoencoder model: {e}")
        
        # If no existing model or loading failed, check required parameters
        original_dim = kwargs.get('original_dim')
        compressed_dim = kwargs.get('compressed_dim')
        
        if original_dim is None or compressed_dim is None:
            self.logger.error("original_dim and compressed_dim are required parameters")
            return False
        
        self.original_dim = original_dim
        self.compressed_dim = compressed_dim
        
        # Build the model
        hidden_layers = kwargs.get('hidden_layers', [])
        activation = kwargs.get('activation', 'relu')
        
        # Create the encoder
        input_layer = Input(shape=(original_dim,))
        x = input_layer
        
        # Add encoder hidden layers
        for layer_size in hidden_layers:
            x = Dense(layer_size, activation=activation)(x)
        
        # Add encoding layer
        encoding = Dense(compressed_dim, activation=activation, name='encoding')(x)
        
        # Add decoder hidden layers
        for layer_size in reversed(hidden_layers):
            encoding = Dense(layer_size, activation=activation)(encoding)
        
        # Add output layer
        output_layer = Dense(original_dim, activation='linear')(encoding)
        
        # Create the full autoencoder model
        self.autoencoder = Model(inputs=input_layer, outputs=output_layer)
        self.autoencoder.compile(optimizer='adam', loss='mse')
        
        # Create separate encoder and decoder models
        self.encoder = Model(inputs=input_layer, outputs=self.autoencoder.get_layer('encoding').output)
        
        # Create decoder model
        encoded_input = Input(shape=(compressed_dim,))
        decoder_layers = []
        found_encoding = False
        
        for layer in self.autoencoder.layers:
            if layer.name == 'encoding':
                found_encoding = True
                continue
            if found_encoding:
                decoder_layers.append(layer)
        
        x = encoded_input
        for layer in decoder_layers:
            x = layer(x)
        
        self.decoder = Model(inputs=encoded_input, outputs=x)
        
        # Train if training data is provided
        training_data = kwargs.get('training_data')
        if training_data is not None:
            epochs = kwargs.get('epochs', 50)
            batch_size = kwargs.get('batch_size', 32)
            return self._train_autoencoder(training_data, epochs, batch_size)
        
        self.logger.info(f"Initialized Autoencoder model with compression from {original_dim} to {compressed_dim} dimensions")
        return True
    
    def compress(self, data: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        """
        Compress a vector or embedding using the Autoencoder.
        
        Args:
            data: The vector or embedding to compress
            
        Returns:
            The compressed vector or embedding
        """
        if not self.is_fitted:
            raise ValueError("Autoencoder model is not fitted. Call fit() or initialize with training data first.")
        
        # Convert to numpy array if needed
        if isinstance(data, list):
            data_np = np.array(data)
        else:
            data_np = data
        
        # Ensure correct shape
        if data_np.ndim == 1:
            data_np = data_np.reshape(1, -1)
        
        # Check dimensions
        if data_np.shape[1] != self.original_dim:
            raise ValueError(f"Input dimension mismatch: expected {self.original_dim}, got {data_np.shape[1]}")
        
        # Encode data
        compressed = self.encoder.predict(data_np)
        
        # Return in the same format as input
        if isinstance(data, list):
            return compressed[0].tolist()
        else:
            return compressed[0] if data_np.shape[0] == 1 else compressed
    
    def decompress(self, compressed_data: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        """
        Decompress a compressed vector or embedding using the Autoencoder.
        
        Args:
            compressed_data: The compressed vector or embedding
            
        Returns:
            The decompressed vector or embedding (approximate reconstruction)
        """
        if not self.is_fitted:
            raise ValueError("Autoencoder model is not fitted. Call fit() or initialize with training data first.")
        
        # Convert to numpy array if needed
        if isinstance(compressed_data, list):
            compressed_np = np.array(compressed_data)
        else:
            compressed_np = compressed_data
        
        # Ensure correct shape
        if compressed_np.ndim == 1:
            compressed_np = compressed_np.reshape(1, -1)
        
        # Check dimensions
        if compressed_np.shape[1] != self.compressed_dim:
            raise ValueError(f"Input dimension mismatch: expected {self.compressed_dim}, got {compressed_np.shape[1]}")
        
        # Decode data
        decompressed = self.decoder.predict(compressed_np)
        
        # Return in the same format as input
        if isinstance(compressed_data, list):
            return decompressed[0].tolist()
        else:
            return decompressed[0] if compressed_np.shape[0] == 1 else decompressed
    
    def fit(self, training_data: Union[List[List[float]], np.ndarray], epochs: int = 50, batch_size: int = 32) -> bool:
        """
        Fit the Autoencoder model on training data.
        
        Args:
            training_data: Training data for fitting the model
            epochs: Number of training epochs
            batch_size: Training batch size
            
        Returns:
            True if fitting was successful, False otherwise
        """
        if self.autoencoder is None:
            self.logger.error("Autoencoder model not initialized. Call initialize() first.")
            return False
        
        return self._train_autoencoder(training_data, epochs, batch_size)
    
    def get_compression_ratio(self) -> float:
        """
        Get the compression ratio achieved by this compressor.
        
        Returns:
            The compression ratio (original size / compressed size)
        """
        if self.original_dim is None or self.compressed_dim is None:
            return 1.0
        
        return self.original_dim / self.compressed_dim
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the neural compressor.
        
        Returns:
            Dictionary of statistics
        """
        stats = {
            "compressor_type": "AutoencoderCompressor",
            "original_dimension": self.original_dim,
            "compressed_dimension": self.compressed_dim,
            "compression_ratio": self.get_compression_ratio(),
            "is_fitted": self.is_fitted
        }
        
        if self.is_fitted and hasattr(self.autoencoder, 'history'):
            # Add training history if available
            history = getattr(self.autoencoder, 'history', None)
            if history:
                stats["training_loss"] = history.history.get('loss', [])
                stats["validation_loss"] = history.history.get('val_loss', [])
        
        return stats
    
    def _train_autoencoder(self, training_data: Union[List[List[float]], np.ndarray], epochs: int, batch_size: int) -> bool:
        """Internal method to train the Autoencoder model."""
        try:
            # Convert to numpy array if needed
            if isinstance(training_data, list):
                training_data = np.array(training_data)
            
            # Train the model
            history = self.autoencoder.fit(
                training_data, training_data,
                epochs=epochs,
                batch_size=batch_size,
                shuffle=True,
                validation_split=0.1,
                verbose=1
            )
            
            # Save history for stats
            self.autoencoder.history = history
            
            # Save model
            self.autoencoder.save(self.model_path)
            
            self.is_fitted = True
            self.logger.info(f"Trained Autoencoder model and saved to {self.model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error training Autoencoder model: {e}")
            return False
