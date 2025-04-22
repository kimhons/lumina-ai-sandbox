"""
Claude provider implementation for Lumina AI.

This module implements the Claude provider for Lumina AI, providing
integration with Anthropic's Claude models like Claude 3.5 Sonnet, Claude 3 Opus, and Claude 3 Haiku.
"""

import os
from typing import Dict, Any, Optional, List
import logging
import json
import time
import anthropic
from anthropic import Anthropic

from lumina.providers.base import Provider
from lumina.common.utils import timestamp, format_error

logger = logging.getLogger(__name__)

class ClaudeProvider(Provider):
    """
    Claude provider implementation.
    
    This class implements the Provider interface for Anthropic's Claude,
    providing access to models like Claude 3.5 Sonnet, Claude 3 Opus, and Claude 3 Haiku.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Claude provider.
        
        Args:
            api_key: Anthropic API key
            config: Optional configuration dictionary
        """
        super().__init__("claude", api_key, config)
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key)
        
        # Define available models and their capabilities
        self.models = {
            "claude-3-5-sonnet-20240620": {
                "context_window": 200000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.000003,  # per token
                    "completion": 0.000015  # per token
                }
            },
            "claude-3-opus-20240229": {
                "context_window": 200000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.00003,  # per token
                    "completion": 0.00015  # per token
                }
            },
            "claude-3-sonnet-20240229": {
                "context_window": 200000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.000003,  # per token
                    "completion": 0.000015  # per token
                }
            },
            "claude-3-haiku-20240307": {
                "context_window": 200000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.00000025,  # per token
                    "completion": 0.00000125  # per token
                }
            }
        }
        
        # Set default model
        self.default_model = config.get("default_model", "claude-3-5-sonnet-20240620")
        if self.default_model not in self.models:
            logger.warning(f"Default model {self.default_model} not available, using first available model")
            self.default_model = next(iter(self.models.keys()))
        
        logger.info(f"Claude provider initialized with {len(self.models)} models")
    
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Generate a completion using Claude's API.
        
        Args:
            prompt: The prompt to generate a completion for
            model: The model to use
            
        Returns:
            The generated completion
        """
        try:
            # Create messages from prompt
            messages = self._create_messages(prompt)
            
            # Call Claude API
            response = self.client.messages.create(
                model=model,
                messages=messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000),
                top_p=self.config.get("top_p", 1.0),
                system=self.config.get("system_prompt", "")
            )
            
            # Extract and return the completion text
            if response.content and len(response.content) > 0:
                # Get text content from the response
                text_content = [block.text for block in response.content if hasattr(block, 'text')]
                return "\n".join(text_content)
            else:
                logger.warning("Claude API returned empty response")
                return ""
        
        except Exception as e:
            logger.error(f"Error generating completion with Claude: {str(e)}")
            raise
    
    def _create_messages(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Create messages array from prompt.
        
        Args:
            prompt: The prompt text
            
        Returns:
            List of message dictionaries for Claude API
        """
        # Check if prompt is already in JSON format for messages
        if prompt.startswith('[') and prompt.endswith(']'):
            try:
                messages = json.loads(prompt)
                if isinstance(messages, list) and all(isinstance(m, dict) and 'role' in m and 'content' in m for m in messages):
                    # Convert to Claude message format
                    return [
                        {
                            "role": m["role"],
                            "content": m["content"]
                        }
                        for m in messages
                    ]
            except:
                pass
        
        # If not, create a simple user message
        return [{"role": "user", "content": prompt}]
    
    def _get_provider_capabilities(self) -> Dict[str, bool]:
        """
        Get the capabilities of the Claude provider.
        
        Returns:
            A dictionary of capability names and boolean values
        """
        return {
            "text_generation": True,
            "code_generation": True,
            "reasoning": True,
            "tool_use": True,
            "multimodal": True,
            "streaming": True,
            "function_calling": True
        }
    
    def _select_model(self, message: str, context: Dict[str, Any]) -> str:
        """
        Select the appropriate model based on the message and context.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            The selected model identifier
        """
        # Use explicitly specified model if provided in context
        if context.get("model") and context["model"] in self.models:
            return context["model"]
        
        # Check if message requires specific capabilities
        requires_complex_reasoning = self._requires_complex_reasoning(message, context)
        requires_code = self._requires_code(message, context)
        
        # Select model based on requirements
        if requires_complex_reasoning:
            return "claude-3-opus-20240229" if "claude-3-opus-20240229" in self.models else self.default_model
        elif requires_code:
            return "claude-3-5-sonnet-20240620" if "claude-3-5-sonnet-20240620" in self.models else self.default_model
        elif len(message) < 100 and not self._requires_detailed_response(message, context):
            return "claude-3-haiku-20240307" if "claude-3-haiku-20240307" in self.models else self.default_model
        else:
            return self.default_model
    
    def _requires_complex_reasoning(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires complex reasoning capabilities.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if complex reasoning capabilities are required, False otherwise
        """
        # Simple heuristic based on message length and complexity indicators
        if len(message) > 1000:
            return True
        
        complexity_indicators = [
            "explain in detail", "analyze deeply", "compare and contrast", "evaluate thoroughly", 
            "synthesize", "philosophical", "theoretical", "implications", "complex system",
            "step by step analysis", "nuanced", "multifaceted", "comprehensive"
        ]
        
        return any(indicator in message.lower() for indicator in complexity_indicators)
    
    def _requires_code(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires code generation capabilities.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if code generation capabilities are required, False otherwise
        """
        code_indicators = [
            "code", "function", "program", "script", "algorithm",
            "python", "javascript", "java", "c++", "typescript",
            "implement", "develop", "create a function", "write a program"
        ]
        
        return any(indicator in message.lower() for indicator in code_indicators)
    
    def _requires_detailed_response(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires a detailed response.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if a detailed response is required, False otherwise
        """
        detail_indicators = [
            "detailed", "explain", "elaborate", "comprehensive", "thorough",
            "in-depth", "step by step", "guide", "tutorial", "how to"
        ]
        
        return any(indicator in message.lower() for indicator in detail_indicators)
    
    def _count_prompt_tokens(self, prompt: str) -> int:
        """
        Count the number of tokens in the prompt using Claude's tokenizer.
        
        Args:
            prompt: The prompt to count tokens for
            
        Returns:
            The number of tokens
        """
        try:
            # Use Anthropic's token counting API
            token_count = self.client.count_tokens(prompt)
            return token_count.token_count
        except Exception as e:
            logger.warning(f"Error counting tokens with Claude API: {str(e)}")
            # Fall back to the utility function
            return super()._count_prompt_tokens(prompt)
    
    def _count_completion_tokens(self, completion: str) -> int:
        """
        Count the number of tokens in the completion using Claude's tokenizer.
        
        Args:
            completion: The completion to count tokens for
            
        Returns:
            The number of tokens
        """
        try:
            # Use Anthropic's token counting API
            token_count = self.client.count_tokens(completion)
            return token_count.token_count
        except Exception as e:
            logger.warning(f"Error counting tokens with Claude API: {str(e)}")
            # Fall back to the utility function
            return super()._count_completion_tokens(completion)
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Calculate the cost of the request based on Claude's pricing.
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            model: The model used
            
        Returns:
            The cost in USD
        """
        if model in self.models and "pricing" in self.models[model]:
            pricing = self.models[model]["pricing"]
            prompt_cost = prompt_tokens * pricing["prompt"]
            completion_cost = completion_tokens * pricing["completion"]
            return prompt_cost + completion_cost
        else:
            # If pricing information is not available, return 0
            return 0.0
