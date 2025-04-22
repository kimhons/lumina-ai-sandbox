"""
Compression Factory for Lumina AI.

This module provides a factory for creating neural compressors,
allowing for easy switching between different compression techniques.
"""

import logging
from typing import Dict, Any, Optional

from .base import NeuralCompressor
from .pca import PCACompressor
from .autoencoder import AutoencoderCompressor

class CompressionFactory:
    """Factory for creating neural compressors."""
    
    @staticmethod
    def create_compressor(compressor_type: str, **kwargs) -> NeuralCompressor:
        """
        Create a neural compressor of the specified type.
        
        Args:
            compressor_type: Type of compressor to create ('pca', 'autoencoder')
            **kwargs: Compressor-specific initialization parameters
            
        Returns:
            An initialized neural compressor
            
        Raises:
            ValueError: If the compressor type is not supported
        """
        logger = logging.getLogger(__name__)
        
        if compressor_type.lower() == 'pca':
            model_path = kwargs.get('model_path')
            return PCACompressor(model_path=model_path)
        
        elif compressor_type.lower() == 'autoencoder':
            model_path = kwargs.get('model_path')
            return AutoencoderCompressor(model_path=model_path)
        
        else:
            logger.error(f"Unsupported compressor type: {compressor_type}")
            raise ValueError(f"Unsupported compressor type: {compressor_type}")
    
    @staticmethod
    def get_available_compressors() -> Dict[str, str]:
        """
        Get a dictionary of available compressor types and their descriptions.
        
        Returns:
            Dictionary mapping compressor types to descriptions
        """
        return {
            'pca': 'PCA-based linear dimensionality reduction',
            'autoencoder': 'Autoencoder-based non-linear dimensionality reduction'
        }
