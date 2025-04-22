"""
Integration module for neural context compression in the Advanced Memory System.

This module connects the neural compression components to the main memory system
and provides a unified interface for context compression operations.
"""

import logging
from typing import Dict, Any, Optional

from ..compression.neural_compression import (
    NeuralSummarizer,
    ImportanceScorer,
    AdaptiveCompressor,
    CompressionEvaluator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompressionModule:
    """
    Integration module for neural context compression.
    
    This class provides a unified interface for context compression operations
    and integrates with the main memory system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the compression module with the provided configuration.
        
        Args:
            config: Configuration dictionary for the compression module
        """
        self.config = config or {}
        logger.info("Initializing Compression Module")
        
        # Initialize compression components
        model_name = self.config.get("model_name", "facebook/bart-large-cnn")
        self.summarizer = NeuralSummarizer(model_name=model_name)
        self.importance_scorer = ImportanceScorer()
        self.compressor = AdaptiveCompressor(self.summarizer, self.importance_scorer)
        self.evaluator = CompressionEvaluator(tokenizer=self.summarizer.tokenizer)
        
        # Configure compression parameters
        self.target_ratio = self.config.get("target_ratio", 0.5)
        self.importance_threshold = self.config.get("importance_threshold", 0.7)
        self.min_length_for_compression = self.config.get("min_length_for_compression", 500)
        
        logger.info("Compression Module initialized successfully")
    
    def compress(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compress content using neural compression techniques.
        
        Args:
            content: The content to compress
            metadata: Optional metadata about the content
            
        Returns:
            Dictionary containing compressed content and metadata
        """
        logger.info(f"Compressing content of length {len(content)}")
        metadata = metadata or {}
        
        # Skip compression for short content
        if len(content) < self.min_length_for_compression:
            logger.info("Content too short for compression, returning original")
            return {
                "original_content": content,
                "compressed_content": content,
                "compression_ratio": 1.0,
                "original_token_count": len(content.split()),
                "compressed_token_count": len(content.split()),
                "compression_method": "none",
                "metadata": metadata
            }
        
        # Perform adaptive compression
        compressed_content = self.compressor.compress(
            content, 
            target_ratio=self.target_ratio,
            importance_threshold=self.importance_threshold
        )
        
        # Evaluate compression quality
        evaluation = self.evaluator.evaluate(content, compressed_content)
        
        # Prepare result
        result = {
            "original_content": content,
            "compressed_content": compressed_content,
            "compression_ratio": evaluation.get("compression_ratio_chars", 0),
            "token_compression_ratio": evaluation.get("compression_ratio_tokens", 0),
            "information_retention": evaluation.get("information_retention", 0),
            "original_token_count": len(content.split()),  # Approximation
            "compressed_token_count": len(compressed_content.split()),  # Approximation
            "compression_method": "adaptive_neural",
            "metadata": metadata
        }
        
        logger.info(f"Compression complete. Ratio: {result['compression_ratio']:.2f}, "
                   f"Information retention: {result['information_retention']:.2f}")
        
        return result
    
    def get_summary(self, content: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate a summary of the content.
        
        Args:
            content: The content to summarize
            max_length: Maximum length of the summary in tokens
            min_length: Minimum length of the summary in tokens
            
        Returns:
            Summarized content
        """
        logger.info(f"Generating summary for content of length {len(content)}")
        return self.summarizer.summarize(content, max_length=max_length, min_length=min_length)
    
    def score_importance(self, content: str) -> float:
        """
        Score the overall importance of content.
        
        Args:
            content: The content to score
            
        Returns:
            Importance score between 0 and 1
        """
        logger.info(f"Scoring importance of content of length {len(content)}")
        scored_sentences = self.importance_scorer.score_sentences(content)
        if not scored_sentences:
            return 0.5
        
        # Calculate average importance score
        total_score = sum(score for _, score in scored_sentences)
        return total_score / len(scored_sentences)
