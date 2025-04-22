"""
Context module for the Advanced Memory System.

This module provides context management capabilities for the memory system,
including context tracking, analysis, and management across conversations.
"""

import logging
from typing import Dict, List, Any, Optional
import time

from memory.compression.neural_compression import ContextCompressor
from memory.vector.provider_factory import get_vector_provider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages conversation context for the memory system.
    
    This class provides capabilities for tracking, analyzing, and managing
    conversation context across user interactions.
    """
    
    def __init__(self, max_context_length: int = 10000, compression_threshold: int = 8000):
        """
        Initialize the context manager.
        
        Args:
            max_context_length: Maximum length of context to maintain
            compression_threshold: Length at which to trigger compression
        """
        self.max_context_length = max_context_length
        self.compression_threshold = compression_threshold
        self.embedding_provider = get_vector_provider()
        self.context_compressor = ContextCompressor(self.embedding_provider)
        self.user_contexts = {}  # user_id -> context_data
    
    def add_to_context(self, user_id: str, message: str, role: str = "user") -> Dict[str, Any]:
        """
        Add a message to the user's conversation context.
        
        Args:
            user_id: ID of the user
            message: Message content
            role: Role of the message sender (user or assistant)
            
        Returns:
            Updated context data
        """
        logger.info(f"Adding message to context for user {user_id}")
        
        # Initialize context data if not exists
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                "messages": [],
                "full_text": "",
                "compressed": False,
                "last_updated": time.time(),
                "turn_count": 0
            }
        
        context_data = self.user_contexts[user_id]
        
        # Add message to context
        timestamp = time.time()
        message_data = {
            "role": role,
            "content": message,
            "timestamp": timestamp,
            "turn": context_data["turn_count"]
        }
        context_data["messages"].append(message_data)
        
        # Update full text
        if context_data["full_text"]:
            context_data["full_text"] += f"\n{role.capitalize()}: {message}"
        else:
            context_data["full_text"] = f"{role.capitalize()}: {message}"
        
        # Increment turn count if user message (each user message starts a new turn)
        if role == "user":
            context_data["turn_count"] += 1
        
        # Update timestamp
        context_data["last_updated"] = timestamp
        
        # Check if compression is needed
        if len(context_data["full_text"]) > self.compression_threshold:
            self._compress_context(user_id)
        
        return context_data
    
    def get_context(self, user_id: str, max_turns: Optional[int] = None) -> Dict[str, Any]:
        """
        Get the current conversation context for a user.
        
        Args:
            user_id: ID of the user
            max_turns: Maximum number of turns to include (None for all)
            
        Returns:
            Context data
        """
        logger.info(f"Getting context for user {user_id}")
        
        if user_id not in self.user_contexts:
            return {
                "messages": [],
                "full_text": "",
                "compressed": False,
                "last_updated": time.time(),
                "turn_count": 0
            }
        
        context_data = self.user_contexts[user_id]
        
        # If max_turns specified, limit the context
        if max_turns is not None:
            current_turn = context_data["turn_count"]
            min_turn = max(0, current_turn - max_turns)
            
            filtered_messages = [
                msg for msg in context_data["messages"]
                if msg["turn"] >= min_turn
            ]
            
            # Rebuild full text from filtered messages
            full_text = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in filtered_messages
            ])
            
            return {
                "messages": filtered_messages,
                "full_text": full_text,
                "compressed": context_data["compressed"],
                "last_updated": context_data["last_updated"],
                "turn_count": context_data["turn_count"]
            }
        
        return context_data
    
    def clear_context(self, user_id: str) -> bool:
        """
        Clear the conversation context for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            True if context was cleared, False if user had no context
        """
        logger.info(f"Clearing context for user {user_id}")
        
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
            return True
        
        return False
    
    def _compress_context(self, user_id: str) -> None:
        """
        Compress the conversation context for a user.
        
        Args:
            user_id: ID of the user
        """
        logger.info(f"Compressing context for user {user_id}")
        
        if user_id not in self.user_contexts:
            return
        
        context_data = self.user_contexts[user_id]
        full_text = context_data["full_text"]
        
        # Calculate compression ratio based on current length
        current_length = len(full_text)
        target_length = self.max_context_length * 0.7  # Target 70% of max length
        compression_ratio = target_length / current_length
        
        # Compress the context
        compressed_text = self.context_compressor.compress(full_text, compression_ratio)
        
        # Update context data
        context_data["full_text"] = compressed_text
        context_data["compressed"] = True
        
        logger.info(f"Compressed context from {current_length} to {len(compressed_text)} characters")
    
    def analyze_context(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze the conversation context for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing context for user {user_id}")
        
        if user_id not in self.user_contexts:
            return {
                "length": 0,
                "turn_count": 0,
                "compressed": False,
                "key_terms": [],
                "sentiment": "neutral",
                "topics": []
            }
        
        context_data = self.user_contexts[user_id]
        full_text = context_data["full_text"]
        
        # Extract key terms (simplified implementation)
        words = full_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 terms
        key_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        key_terms = [term for term, _ in key_terms]
        
        # Simple sentiment analysis (placeholder)
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "like", "love"]
        negative_words = ["bad", "terrible", "awful", "horrible", "sad", "dislike", "hate", "poor"]
        
        positive_count = sum(words.count(word) for word in positive_words)
        negative_count = sum(words.count(word) for word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Topic extraction (simplified implementation)
        topics = []
        if "travel" in full_text.lower() or "trip" in full_text.lower() or "vacation" in full_text.lower():
            topics.append("travel")
        if "code" in full_text.lower() or "programming" in full_text.lower() or "software" in full_text.lower():
            topics.append("programming")
        if "food" in full_text.lower() or "recipe" in full_text.lower() or "cook" in full_text.lower():
            topics.append("cooking")
        
        return {
            "length": len(full_text),
            "turn_count": context_data["turn_count"],
            "compressed": context_data["compressed"],
            "key_terms": key_terms,
            "sentiment": sentiment,
            "topics": topics
        }
    
    def get_context_summary(self, user_id: str) -> str:
        """
        Get a summary of the conversation context for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Context summary
        """
        logger.info(f"Getting context summary for user {user_id}")
        
        if user_id not in self.user_contexts:
            return "No conversation history."
        
        context_data = self.user_contexts[user_id]
        full_text = context_data["full_text"]
        
        # Use the context compressor to create a summary
        summary = self.context_compressor.compress(full_text, 0.2)  # Compress to 20%
        
        return summary


# Singleton instance for global access
context_manager = ContextManager()
