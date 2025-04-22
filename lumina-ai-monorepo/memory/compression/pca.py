"""
PCA Neural Compressor for Lumina AI.

This module implements Principal Component Analysis (PCA) based
neural compression for efficient storage of embeddings.
"""

import os
import pickle
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from .base import NeuralCompressor

try:
    from sklearn.decomposition import PCA
except ImportError:
    raise ImportError("scikit-learn package not installed. Install with 'pip install scikit-learn'")

class PCACompressor(NeuralCompressor):
    """PCA-based neural compressor for dimensionality reduction."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the PCA compressor.
        
        Args:
            model_path: Optional path to save/load the PCA model
        """
        self.model_path = model_path or "./data/compression/pca_model.pkl"
        self.pca = None
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
                - n_components: Number of components to keep (required if training)
                - original_dim: Original dimensionality (required if training)
                - training_data: Optional training data for fitting the PCA model
            
        Returns:
            True if initialization was successful, False otherwise
        """
        # Try to load existing model
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.pca = pickle.load(f)
                self.original_dim = self.pca.n_features_in_
                self.compressed_dim = self.pca.n_components_
                self.is_fitted = True
                self.logger.info(f"Loaded PCA model from {self.model_path}")
                return True
            except Exception as e:
                self.logger.error(f"Error loading PCA model: {e}")
        
        # If no existing model or loading failed, check if we have training data
        training_data = kwargs.get('training_data')
        n_components = kwargs.get('n_components')
        original_dim = kwargs.get('original_dim')
        
        if training_data is not None and n_components is not None:
            return self._fit_pca(training_data, n_components)
        elif n_components is not None and original_dim is not None:
            # Initialize without fitting
            self.pca = PCA(n_components=n_components)
            self.original_dim = original_dim
            self.compressed_dim = n_components
            self.is_fitted = False
            self.logger.info(f"Initialized PCA model with {n_components} components (not fitted)")
            return True
        else:
            self.logger.error("Either training_data and n_components, or n_components and original_dim must be provided")
            return False
    
    def compress(self, data: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        """
        Compress a vector or embedding using PCA.
        
        Args:
            data: The vector or embedding to compress
            
        Returns:
            The compressed vector or embedding
        """
        if not self.is_fitted:
            raise ValueError("PCA model is not fitted. Call fit() or initialize with training data first.")
        
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
        
        # Transform data
        compressed = self.pca.transform(data_np)
        
        # Return in the same format as input
        if isinstance(data, list):
            return compressed[0].tolist()
        else:
            return compressed[0] if data_np.shape[0] == 1 else compressed
    
    def decompress(self, compressed_data: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        """
        Decompress a compressed vector or embedding using PCA.
        
        Args:
            compressed_data: The compressed vector or embedding
            
        Returns:
            The decompressed vector or embedding (approximate reconstruction)
        """
        if not self.is_fitted:
            raise ValueError("PCA model is not fitted. Call fit() or initialize with training data first.")
        
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
        
        # Inverse transform data
        decompressed = self.pca.inverse_transform(compressed_np)
        
        # Return in the same format as input
        if isinstance(compressed_data, list):
            return decompressed[0].tolist()
        else:
            return decompressed[0] if compressed_np.shape[0] == 1 else decompressed
    
    def fit(self, training_data: Union[List[List[float]], np.ndarray]) -> bool:
        """
        Fit the PCA model on training data.
        
        Args:
            training_data: Training data for fitting the PCA model
            
        Returns:
            True if fitting was successful, False otherwise
        """
        if self.pca is None:
            self.logger.error("PCA model not initialized. Call initialize() first.")
            return False
        
        return self._fit_pca(training_data, self.compressed_dim)
    
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
            "compressor_type": "PCACompressor",
            "original_dimension": self.original_dim,
            "compressed_dimension": self.compressed_dim,
            "compression_ratio": self.get_compression_ratio(),
            "is_fitted": self.is_fitted
        }
        
        if self.is_fitted:
            # Add explained variance information
            explained_variance_ratio = self.pca.explained_variance_ratio_
            stats["explained_variance_ratio"] = explained_variance_ratio.tolist()
            stats["cumulative_explained_variance"] = np.cumsum(explained_variance_ratio).tolist()
        
        return stats
    
    def _fit_pca(self, training_data: Union[List[List[float]], np.ndarray], n_components: int) -> bool:
        """Internal method to fit the PCA model."""
        try:
            # Convert to numpy array if needed
            if isinstance(training_data, list):
                training_data = np.array(training_data)
            
            # Initialize PCA
            self.pca = PCA(n_components=n_components)
            
            # Fit PCA
            self.pca.fit(training_data)
            
            # Store dimensions
            self.original_dim = training_data.shape[1]
            self.compressed_dim = n_components
            self.is_fitted = True
            
            # Save model
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pca, f)
            
            self.logger.info(f"Fitted PCA model with {n_components} components and saved to {self.model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error fitting PCA model: {e}")
            return False
