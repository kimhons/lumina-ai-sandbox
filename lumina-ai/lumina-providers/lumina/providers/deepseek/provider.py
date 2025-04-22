"""
DeepSeek provider implementation for Lumina AI.

This module implements the DeepSeek provider for Lumina AI, providing
integration with DeepSeek's models like DeepSeek-Coder and DeepSeek-Chat.
"""

import os
from typing import Dict, Any, Optional, List
import logging
import json
import time
import requests

from lumina.providers.base import Provider
from lumina.common.utils import timestamp, format_error

logger = logging.getLogger(__name__)

class DeepSeekProvider(Provider):
    """
    DeepSeek provider implementation.
    
    This class implements the Provider interface for DeepSeek,
    providing access to models like DeepSeek-Coder and DeepSeek-Chat.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DeepSeek provider.
        
        Args:
            api_key: DeepSeek API key
            config: Optional configuration dictionary
        """
        super().__init__("deepseek", api_key, config)
        
        # Set API endpoint
        self.api_endpoint = config.get("api_endpoint", "https://api.deepseek.com/v1")
        
        # Define available models and their capabilities
        self.models = {
            "deepseek-chat": {
                "context_window": 32768,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": False
                },
                "pricing": {
                    "prompt": 0.0000025,  # per token
                    "completion": 0.0000025  # per token
                }
            },
            "deepseek-coder": {
                "context_window": 32768,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": False
                },
                "pricing": {
                    "prompt": 0.0000025,  # per token
                    "completion": 0.0000025  # per token
                }
            }
        }
        
        # Set default model
        self.default_model = config.get("default_model", "deepseek-chat")
        if self.default_model not in self.models:
            logger.warning(f"Default model {self.default_model} not available, using first available model")
            self.default_model = next(iter(self.models.keys()))
        
        logger.info(f"DeepSeek provider initialized with {len(self.models)} models")
    
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Generate a completion using DeepSeek's API.
        
        Args:
            prompt: The prompt to generate a completion for
            model: The model to use
            
        Returns:
            The generated completion
        """
        try:
            # Create messages from prompt
            messages = self._create_messages(prompt)
            
            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1000),
                "top_p": self.config.get("top_p", 1.0),
                "frequency_penalty": self.config.get("frequency_penalty", 0.0),
                "presence_penalty": self.config.get("presence_penalty", 0.0)
            }
            
            # Add system prompt if provided
            if self.config.get("system_prompt"):
                data["system"] = self.config.get("system_prompt")
            
            # Call DeepSeek API
            response = requests.post(
                f"{self.api_endpoint}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                raise Exception(f"DeepSeek API error: {response.status_code}")
            
            # Parse response
            response_data = response.json()
            
            # Extract and return the completion text
            if "choices" in response_data and len(response_data["choices"]) > 0:
                if "message" in response_data["choices"][0] and "content" in response_data["choices"][0]["message"]:
                    return response_data["choices"][0]["message"]["content"]
            
            logger.warning("DeepSeek API returned empty response")
            return ""
        
        except Exception as e:
            logger.error(f"Error generating completion with DeepSeek: {str(e)}")
            raise
    
    def _create_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create messages array from prompt.
        
        Args:
            prompt: The prompt text
            
        Returns:
            List of message dictionaries for DeepSeek API
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
        Get the capabilities of the DeepSeek provider.
        
        Returns:
            A dictionary of capability names and boolean values
        """
        return {
            "text_generation": True,
            "code_generation": True,
            "reasoning": True,
            "tool_use": True,
            "multimodal": False,
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
        
        # Check if message requires code generation
        requires_code = self._requires_code(message, context)
        
        # Select model based on requirements
        if requires_code:
            return "deepseek-coder" if "deepseek-coder" in self.models else self.default_model
        else:
            return self.default_model
    
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
            "implement", "develop", "create a function", "write a program",
            "class", "method", "api", "endpoint", "database query",
            "sql", "html", "css", "react", "node", "express"
        ]
        
        return any(indicator in message.lower() for indicator in code_indicators)
    
    def _count_prompt_tokens(self, prompt: str) -> int:
        """
        Count the number of tokens in the prompt.
        
        Args:
            prompt: The prompt to count tokens for
            
        Returns:
            The number of tokens
        """
        # DeepSeek doesn't provide a token counting API, so we use the utility function
        return super()._count_prompt_tokens(prompt)
    
    def _count_completion_tokens(self, completion: str) -> int:
        """
        Count the number of tokens in the completion.
        
        Args:
            completion: The completion to count tokens for
            
        Returns:
            The number of tokens
        """
        # DeepSeek doesn't provide a token counting API, so we use the utility function
        return super()._count_completion_tokens(completion)
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Calculate the cost of the request based on DeepSeek's pricing.
        
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
