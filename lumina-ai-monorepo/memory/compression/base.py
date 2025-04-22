"""
Neural Compression Interface for Lumina AI.

This module defines the interface for neural compression techniques,
allowing for efficient storage and retrieval of memory data.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

class NeuralCompressor(ABC):
    """Abstract base class for neural compression techniques."""
    
    @abstractmethod
    def initialize(self, **kwargs) -> bool:
        """
        Initialize the neural compressor.
        
        Args:
            **kwargs: Compressor-specific initialization parameters
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def compress(self, data: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        """
        Compress a vector or embedding.
        
        Args:
            data: The vector or embedding to compress
            
        Returns:
            The compressed vector or embedding
        """
        pass
    
    @abstractmethod
    def decompress(self, compressed_data: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        """
        Decompress a compressed vector or embedding.
        
        Args:
            compressed_data: The compressed vector or embedding
            
        Returns:
            The decompressed vector or embedding
        """
        pass
    
    @abstractmethod
    def get_compression_ratio(self) -> float:
        """
        Get the compression ratio achieved by this compressor.
        
        Returns:
            The compression ratio (original size / compressed size)
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the neural compressor.
        
        Returns:
            Dictionary of statistics
        """
        pass
