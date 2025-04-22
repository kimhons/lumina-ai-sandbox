"""
Neural context compression module for the Advanced Memory System.

This module provides functionality for compressing conversation contexts
using neural summarization techniques to optimize token usage while
preserving important information.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NeuralSummarizer:
    """
    Neural summarization model for compressing conversation contexts.
    
    This class uses transformer-based models to generate concise summaries
    of conversation contexts, optimizing token usage while preserving
    important information.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the neural summarizer with the specified model.
        
        Args:
            model_name: Name of the pre-trained model to use for summarization
        """
        logger.info(f"Initializing NeuralSummarizer with model: {model_name}")
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        
        logger.info("NeuralSummarizer initialized successfully")
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate a summary of the input text.
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of the summary in tokens
            min_length: Minimum length of the summary in tokens
            
        Returns:
            Summarized text
        """
        logger.info(f"Summarizing text of length {len(text)}")
        
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True).to(self.device)
        
        # Generate summary
        summary_ids = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        
        # Decode the summary
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        logger.info(f"Generated summary of length {len(summary)}")
        return summary
    
    def get_compression_ratio(self, original_text: str, summary: str) -> float:
        """
        Calculate the compression ratio between the original text and the summary.
        
        Args:
            original_text: Original input text
            summary: Summarized text
            
        Returns:
            Compression ratio (summary length / original length)
        """
        original_tokens = len(self.tokenizer.encode(original_text))
        summary_tokens = len(self.tokenizer.encode(summary))
        
        compression_ratio = summary_tokens / original_tokens
        logger.info(f"Compression ratio: {compression_ratio:.2f} ({summary_tokens}/{original_tokens} tokens)")
        
        return compression_ratio


class ImportanceScorer:
    """
    Scores the importance of text segments for selective compression.
    
    This class analyzes text to identify and score important segments
    that should be preserved during compression.
    """
    
    def __init__(self):
        """Initialize the importance scorer."""
        logger.info("Initializing ImportanceScorer")
    
    def score_sentences(self, text: str) -> List[Tuple[str, float]]:
        """
        Split text into sentences and score each sentence by importance.
        
        Args:
            text: Input text to score
            
        Returns:
            List of (sentence, score) tuples
        """
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        scored_sentences = []
        for sentence in sentences:
            # Calculate a simple importance score based on heuristics
            score = self._calculate_importance_score(sentence)
            scored_sentences.append((sentence, score))
        
        # Sort by importance score in descending order
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        return scored_sentences
    
    def _calculate_importance_score(self, sentence: str) -> float:
        """
        Calculate an importance score for a sentence based on heuristics.
        
        Args:
            sentence: Input sentence to score
            
        Returns:
            Importance score between 0 and 1
        """
        # This is a simple heuristic-based scoring function
        # In a production system, this would use more sophisticated NLP techniques
        
        # Initialize base score
        score = 0.5
        
        # Length factor (longer sentences often contain more information)
        words = sentence.split()
        length_factor = min(len(words) / 20, 1.0)  # Cap at 1.0
        score += length_factor * 0.1
        
        # Presence of important keywords
        important_keywords = [
            "important", "critical", "essential", "key", "significant",
            "must", "should", "will", "can", "need", "require",
            "first", "second", "third", "finally", "conclusion",
            "result", "therefore", "thus", "because", "since"
        ]
        
        keyword_count = sum(1 for word in words if word.lower() in important_keywords)
        keyword_factor = min(keyword_count / 3, 1.0)  # Cap at 1.0
        score += keyword_factor * 0.2
        
        # Presence of named entities (simple approximation)
        capitalized_words = sum(1 for word in words if word and word[0].isupper())
        entity_factor = min(capitalized_words / 3, 1.0)  # Cap at 1.0
        score += entity_factor * 0.1
        
        # Presence of numbers (often important facts)
        has_numbers = any(char.isdigit() for char in sentence)
        if has_numbers:
            score += 0.1
        
        # Cap the final score at 1.0
        return min(score, 1.0)


class AdaptiveCompressor:
    """
    Adaptively compresses text based on content type and importance.
    
    This class combines different compression strategies and applies them
    selectively based on the content type and importance of different
    parts of the text.
    """
    
    def __init__(self, summarizer: NeuralSummarizer, importance_scorer: ImportanceScorer):
        """
        Initialize the adaptive compressor.
        
        Args:
            summarizer: Neural summarizer for text compression
            importance_scorer: Scorer for determining text importance
        """
        logger.info("Initializing AdaptiveCompressor")
        self.summarizer = summarizer
        self.importance_scorer = importance_scorer
    
    def compress(self, text: str, target_ratio: float = 0.5, importance_threshold: float = 0.7) -> str:
        """
        Compress text adaptively based on content type and importance.
        
        Args:
            text: Input text to compress
            target_ratio: Target compression ratio (compressed/original)
            importance_threshold: Threshold for preserving important content
            
        Returns:
            Compressed text
        """
        logger.info(f"Adaptively compressing text of length {len(text)}")
        
        # If text is short, don't compress
        if len(text) < 500:
            logger.info("Text too short for compression, returning original")
            return text
        
        # Score sentences by importance
        scored_sentences = self.importance_scorer.score_sentences(text)
        
        # Separate important and less important content
        important_sentences = []
        compressible_sentences = []
        
        for sentence, score in scored_sentences:
            if score >= importance_threshold:
                important_sentences.append(sentence)
            else:
                compressible_sentences.append(sentence)
        
        # If most content is important, use neural summarization
        if len(important_sentences) > 0.7 * len(scored_sentences):
            logger.info("Most content is important, using neural summarization")
            return self.summarizer.summarize(text)
        
        # Otherwise, preserve important sentences and compress the rest
        logger.info(f"Preserving {len(important_sentences)} important sentences and compressing the rest")
        
        # Join compressible sentences for summarization
        compressible_text = " ".join(compressible_sentences)
        
        # Determine target length for compressed content
        original_length = len(text)
        important_length = sum(len(s) for s in important_sentences)
        target_compressed_length = int(target_ratio * original_length) - important_length
        
        # Compress the compressible content if it's substantial
        if len(compressible_text) > 500:
            # Calculate appropriate max_length for the summarizer
            max_tokens = max(50, int(target_compressed_length / 4))  # Rough approximation
            compressed_text = self.summarizer.summarize(compressible_text, max_length=max_tokens)
        else:
            compressed_text = compressible_text
        
        # Combine important sentences with compressed content
        result = " ".join(important_sentences) + " " + compressed_text
        
        logger.info(f"Compressed text from {len(text)} to {len(result)} characters")
        return result


class CompressionEvaluator:
    """
    Evaluates the quality of compressed text.
    
    This class provides metrics for assessing how well the compressed text
    preserves the important information from the original text.
    """
    
    def __init__(self, tokenizer=None):
        """
        Initialize the compression evaluator.
        
        Args:
            tokenizer: Optional tokenizer for token-based metrics
        """
        logger.info("Initializing CompressionEvaluator")
        self.tokenizer = tokenizer
    
    def evaluate(self, original_text: str, compressed_text: str) -> Dict[str, float]:
        """
        Evaluate the quality of compression.
        
        Args:
            original_text: Original input text
            compressed_text: Compressed version of the text
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating compression quality")
        
        metrics = {}
        
        # Compression ratio (character-based)
        char_ratio = len(compressed_text) / len(original_text)
        metrics["compression_ratio_chars"] = char_ratio
        
        # Compression ratio (token-based, if tokenizer is available)
        if self.tokenizer:
            original_tokens = len(self.tokenizer.encode(original_text))
            compressed_tokens = len(self.tokenizer.encode(compressed_text))
            token_ratio = compressed_tokens / original_tokens
            metrics["compression_ratio_tokens"] = token_ratio
        
        # Information retention score (simple approximation)
        # In a production system, this would use more sophisticated NLP techniques
        original_keywords = self._extract_keywords(original_text)
        compressed_keywords = self._extract_keywords(compressed_text)
        
        if original_keywords:
            retention_score = len(set(compressed_keywords) & set(original_keywords)) / len(original_keywords)
            metrics["information_retention"] = retention_score
        else:
            metrics["information_retention"] = 1.0
        
        logger.info(f"Compression evaluation metrics: {metrics}")
        return metrics
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        # This is a simple keyword extraction method
        # In a production system, this would use more sophisticated NLP techniques
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            "the", "and", "is", "in", "it", "to", "that", "of", "for", "with",
            "as", "was", "on", "are", "be", "this", "have", "from", "or", "an",
            "by", "not", "but", "what", "all", "when", "can", "they", "their"
        }
        
        keywords = [word for word in words if word not in stop_words]
        
        # Count word frequencies
        word_counts = {}
        for word in keywords:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:min(20, len(sorted_words))]]
