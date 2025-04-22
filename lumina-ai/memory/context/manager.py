"""
Context Management for Lumina AI.

This module provides context compression and management capabilities,
allowing for efficient use of context windows in LLM interactions.
"""

import json
import time
from typing import List, Dict, Any, Optional, Tuple
import logging

class ContextManager:
    """Manages conversation context with compression and prioritization."""
    
    def __init__(self, max_tokens: int = 8000):
        """
        Initialize the context manager.
        
        Args:
            max_tokens: Maximum number of tokens to maintain in context
        """
        self.max_tokens = max_tokens
        self.messages = []
        self.token_count = 0
        self.logger = logging.getLogger(__name__)
        
    def add_message(self, role: str, content: str, token_count: Optional[int] = None) -> None:
        """
        Add a message to the context.
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The message content
            token_count: Optional pre-computed token count
        """
        # Estimate token count if not provided
        if token_count is None:
            # Simple estimation: ~4 chars per token
            token_count = len(content) // 4 + 1
        
        message = {
            "role": role,
            "content": content,
            "token_count": token_count,
            "timestamp": time.time(),
            "importance": 1.0  # Default importance
        }
        
        self.messages.append(message)
        self.token_count += token_count
        
        # Compress context if it exceeds max tokens
        if self.token_count > self.max_tokens:
            self._compress_context()
    
    def get_context(self, max_tokens: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the current context messages.
        
        Args:
            max_tokens: Optional maximum token limit for returned context
            
        Returns:
            List of context messages
        """
        if max_tokens is None or max_tokens >= self.token_count:
            return [{"role": m["role"], "content": m["content"]} for m in self.messages]
        
        # If we need to limit tokens, prioritize messages
        return self._get_prioritized_context(max_tokens)
    
    def get_token_count(self) -> int:
        """Get the current token count of the context."""
        return self.token_count
    
    def get_context_utilization(self) -> float:
        """Get the current context utilization as a percentage."""
        return (self.token_count / self.max_tokens) * 100
    
    def clear_context(self) -> None:
        """Clear all context messages."""
        self.messages = []
        self.token_count = 0
    
    def set_message_importance(self, index: int, importance: float) -> bool:
        """
        Set the importance of a message for prioritization.
        
        Args:
            index: Index of the message
            importance: Importance score (0.0 to 2.0)
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= index < len(self.messages):
            self.messages[index]["importance"] = max(0.0, min(2.0, importance))
            return True
        return False
    
    def summarize_context(self) -> str:
        """
        Generate a summary of the current context.
        
        Returns:
            Summary text
        """
        # In a real implementation, this would use an LLM to generate a summary
        # For this implementation, we'll just return a placeholder
        
        user_messages = [m for m in self.messages if m["role"] == "user"]
        assistant_messages = [m for m in self.messages if m["role"] == "assistant"]
        
        summary = (
            f"Context contains {len(self.messages)} messages "
            f"({len(user_messages)} from user, {len(assistant_messages)} from assistant) "
            f"with approximately {self.token_count} tokens."
        )
        
        return summary
    
    def _compress_context(self) -> None:
        """Compress the context to fit within max_tokens."""
        # Strategy 1: Remove oldest, least important messages first
        if len(self.messages) <= 3:  # Keep at least 3 messages if possible
            return
        
        # Sort messages by importance and recency
        # We'll use a score that combines both
        for i, msg in enumerate(self.messages):
            # Skip the first (system) and last two messages
            if i == 0 or i >= len(self.messages) - 2:
                msg["compression_score"] = float('inf')
            else:
                # Recency factor: newer messages have higher scores
                recency = (msg["timestamp"] - self.messages[0]["timestamp"]) / (
                    self.messages[-1]["timestamp"] - self.messages[0]["timestamp"] + 1e-10
                )
                
                # Combine importance and recency
                msg["compression_score"] = msg["importance"] * (0.3 + 0.7 * recency)
        
        # Sort by compression score (ascending)
        sorted_messages = sorted(self.messages, key=lambda m: m.get("compression_score", 0))
        
        # Remove messages until we're under the limit
        removed_count = 0
        for msg in sorted_messages:
            if self.token_count <= self.max_tokens * 0.8:  # Target 80% of max to avoid frequent compression
                break
                
            if msg.get("compression_score", 0) == float('inf'):
                continue  # Skip protected messages
                
            self.token_count -= msg["token_count"]
            self.messages.remove(msg)
            removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Compressed context by removing {removed_count} messages")
    
    def _get_prioritized_context(self, max_tokens: int) -> List[Dict[str, str]]:
        """
        Get a prioritized subset of context messages within token limit.
        
        Args:
            max_tokens: Maximum token limit
            
        Returns:
            List of prioritized context messages
        """
        # Always include the first message (usually system) and the last two messages
        must_include = []
        if self.messages:
            must_include.append(0)  # First message
        
        if len(self.messages) >= 2:
            must_include.extend([len(self.messages) - 2, len(self.messages) - 1])  # Last two messages
        
        # Calculate scores for other messages
        scored_messages = []
        for i, msg in enumerate(self.messages):
            if i in must_include:
                continue
                
            # Similar scoring as in _compress_context
            recency = (msg["timestamp"] - self.messages[0]["timestamp"]) / (
                self.messages[-1]["timestamp"] - self.messages[0]["timestamp"] + 1e-10
            )
            
            score = msg["importance"] * (0.3 + 0.7 * recency)
            scored_messages.append((i, score))
        
        # Sort by score (descending)
        scored_messages.sort(key=lambda x: x[1], reverse=True)
        
        # Build prioritized indices
        prioritized_indices = must_include.copy()
        remaining_tokens = max_tokens - sum(self.messages[i]["token_count"] for i in must_include)
        
        for idx, _ in scored_messages:
            token_count = self.messages[idx]["token_count"]
            if token_count <= remaining_tokens:
                prioritized_indices.append(idx)
                remaining_tokens -= token_count
            
            if remaining_tokens <= 0:
                break
        
        # Sort indices to maintain original order
        prioritized_indices.sort()
        
        # Return prioritized messages
        return [{"role": self.messages[i]["role"], "content": self.messages[i]["content"]} 
                for i in prioritized_indices]
