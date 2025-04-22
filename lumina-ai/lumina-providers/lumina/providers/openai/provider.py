"""
OpenAI provider implementation for Lumina AI.

This module implements the OpenAI provider for Lumina AI, providing
integration with OpenAI's models like GPT-4o, GPT-4, and GPT-3.5.
"""

import os
from typing import Dict, Any, Optional, List
import logging
import json
import time
import openai
from openai import OpenAI
import tiktoken

from lumina.providers.base import Provider
from lumina.common.utils import timestamp, format_error

logger = logging.getLogger(__name__)

class OpenAIProvider(Provider):
    """
    OpenAI provider implementation.
    
    This class implements the Provider interface for OpenAI,
    providing access to models like GPT-4o, GPT-4, and GPT-3.5.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            config: Optional configuration dictionary
        """
        super().__init__("openai", api_key, config)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        
        # Define available models and their capabilities
        self.models = {
            "gpt-4o": {
                "context_window": 128000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.00005,  # per token
                    "completion": 0.00015  # per token
                }
            },
            "gpt-4": {
                "context_window": 8192,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": False
                },
                "pricing": {
                    "prompt": 0.00003,  # per token
                    "completion": 0.00006  # per token
                }
            },
            "gpt-3.5-turbo": {
                "context_window": 16385,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": False
                },
                "pricing": {
                    "prompt": 0.000005,  # per token
                    "completion": 0.000015  # per token
                }
            }
        }
        
        # Set default model
        self.default_model = config.get("default_model", "gpt-4o")
        if self.default_model not in self.models:
            logger.warning(f"Default model {self.default_model} not available, using first available model")
            self.default_model = next(iter(self.models.keys()))
        
        # Initialize tokenizers
        self.tokenizers = {}
        for model in self.models:
            try:
                if "gpt-4" in model:
                    self.tokenizers[model] = tiktoken.encoding_for_model("gpt-4")
                elif "gpt-3.5" in model:
                    self.tokenizers[model] = tiktoken.encoding_for_model("gpt-3.5-turbo")
                else:
                    self.tokenizers[model] = tiktoken.encoding_for_model(model)
            except Exception as e:
                logger.warning(f"Failed to load tokenizer for {model}: {str(e)}")
                self.tokenizers[model] = None
        
        logger.info(f"OpenAI provider initialized with {len(self.models)} models")
    
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Generate a completion using OpenAI's API.
        
        Args:
            prompt: The prompt to generate a completion for
            model: The model to use
            
        Returns:
            The generated completion
        """
        try:
            # Create messages from prompt
            messages = self._create_messages(prompt)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000),
                top_p=self.config.get("top_p", 1.0),
                frequency_penalty=self.config.get("frequency_penalty", 0.0),
                presence_penalty=self.config.get("presence_penalty", 0.0)
            )
            
            # Extract and return the completion text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            else:
                logger.warning("OpenAI API returned empty response")
                return ""
        
        except Exception as e:
            logger.error(f"Error generating completion with OpenAI: {str(e)}")
            raise
    
    def _create_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create messages array from prompt.
        
        Args:
            prompt: The prompt text
            
        Returns:
            List of message dictionaries for OpenAI API
        """
        # Check if prompt is already in JSON format for messages
        if prompt.startswith('[') and prompt.endswith(']'):
            try:
                messages = json.loads(prompt)
                if isinstance(messages, list) and all(isinstance(m, dict) and 'role' in m and 'content' in m for m in messages):
                    return messages
            except:
                pass
        
        # If not, create a simple user message
        return [{"role": "user", "content": prompt}]
    
    def _get_provider_capabilities(self) -> Dict[str, bool]:
        """
        Get the capabilities of the OpenAI provider.
        
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
        requires_multimodal = self._requires_multimodal(message, context)
        requires_complex_reasoning = self._requires_complex_reasoning(message, context)
        requires_code = self._requires_code(message, context)
        
        # Select model based on requirements
        if requires_multimodal:
            return "gpt-4o"
        elif requires_complex_reasoning or requires_code:
            return "gpt-4o" if "gpt-4o" in self.models else "gpt-4"
        else:
            return self.default_model
    
    def _requires_multimodal(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires multimodal capabilities.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if multimodal capabilities are required, False otherwise
        """
        # Check if context contains image data
        if context.get("images") or context.get("attachments"):
            return True
        
        return False
    
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
        if len(message) > 500:
            return True
        
        complexity_indicators = [
            "explain", "analyze", "compare", "evaluate", "synthesize",
            "why", "how", "what if", "implications", "consequences"
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
    
    def _count_prompt_tokens(self, prompt: str) -> int:
        """
        Count the number of tokens in the prompt using OpenAI's tokenizer.
        
        Args:
            prompt: The prompt to count tokens for
            
        Returns:
            The number of tokens
        """
        model = self.default_model
        tokenizer = self.tokenizers.get(model)
        
        if tokenizer:
            # If prompt is a JSON string of messages, parse it
            if prompt.startswith('[') and prompt.endswith(']'):
                try:
                    messages = json.loads(prompt)
                    if isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
                        # Count tokens for each message
                        total = 0
                        for message in messages:
                            if isinstance(message, dict) and 'content' in message:
                                total += len(tokenizer.encode(message['content']))
                        return total
                except:
                    pass
            
            # Otherwise, encode the prompt directly
            return len(tokenizer.encode(prompt))
        else:
            # Fall back to the utility function if tokenizer is not available
            return super()._count_prompt_tokens(prompt)
    
    def _count_completion_tokens(self, completion: str) -> int:
        """
        Count the number of tokens in the completion using OpenAI's tokenizer.
        
        Args:
            completion: The completion to count tokens for
            
        Returns:
            The number of tokens
        """
        model = self.default_model
        tokenizer = self.tokenizers.get(model)
        
        if tokenizer:
            return len(tokenizer.encode(completion))
        else:
            # Fall back to the utility function if tokenizer is not available
            return super()._count_completion_tokens(completion)
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Calculate the cost of the request based on OpenAI's pricing.
        
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
