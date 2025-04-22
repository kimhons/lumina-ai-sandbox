"""
Grok provider implementation for Lumina AI.

This module implements the Grok provider for Lumina AI, providing
integration with xAI's Grok models.
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

class GrokProvider(Provider):
    """
    Grok provider implementation.
    
    This class implements the Provider interface for xAI's Grok,
    providing access to models like Grok-1.5 and Grok-1.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Grok provider.
        
        Args:
            api_key: xAI API key
            config: Optional configuration dictionary
        """
        super().__init__("grok", api_key, config)
        
        # Set API endpoint
        self.api_endpoint = config.get("api_endpoint", "https://api.grok.x.ai/v1")
        
        # Define available models and their capabilities
        self.models = {
            "grok-1.5": {
                "context_window": 128000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.0000025,  # per token
                    "completion": 0.0000075  # per token
                }
            },
            "grok-1": {
                "context_window": 8192,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": False,
                    "multimodal": False
                },
                "pricing": {
                    "prompt": 0.0000015,  # per token
                    "completion": 0.0000045  # per token
                }
            }
        }
        
        # Set default model
        self.default_model = config.get("default_model", "grok-1.5")
        if self.default_model not in self.models:
            logger.warning(f"Default model {self.default_model} not available, using first available model")
            self.default_model = next(iter(self.models.keys()))
        
        logger.info(f"Grok provider initialized with {len(self.models)} models")
    
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Generate a completion using Grok's API.
        
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
                "top_p": self.config.get("top_p", 1.0)
            }
            
            # Call Grok API
            response = requests.post(
                f"{self.api_endpoint}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                raise Exception(f"Grok API error: {response.status_code}")
            
            # Parse response
            response_data = response.json()
            
            # Extract and return the completion text
            if "choices" in response_data and len(response_data["choices"]) > 0:
                if "message" in response_data["choices"][0] and "content" in response_data["choices"][0]["message"]:
                    return response_data["choices"][0]["message"]["content"]
            
            logger.warning("Grok API returned empty response")
            return ""
        
        except Exception as e:
            logger.error(f"Error generating completion with Grok: {str(e)}")
            raise
    
    def _create_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create messages array from prompt.
        
        Args:
            prompt: The prompt text
            
        Returns:
            List of message dictionaries for Grok API
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
        Get the capabilities of the Grok provider.
        
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
            "function_calling": True,
            "real_time_knowledge": True
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
        requires_tool_use = self._requires_tool_use(message, context)
        requires_long_context = self._requires_long_context(message, context)
        
        # Select model based on requirements
        if requires_multimodal or requires_tool_use or requires_long_context:
            return "grok-1.5" if "grok-1.5" in self.models else self.default_model
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
        
        # Check for indicators of image processing
        image_indicators = [
            "image", "picture", "photo", "diagram", "chart", "graph",
            "analyze this image", "look at this picture", "what's in this photo"
        ]
        
        return any(indicator in message.lower() for indicator in image_indicators)
    
    def _requires_tool_use(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires tool use capabilities.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if tool use capabilities are required, False otherwise
        """
        # Check if context explicitly requests tool use
        if context.get("tools") or context.get("require_tools"):
            return True
        
        # Check for indicators of tool use
        tool_indicators = [
            "use tool", "search for", "calculate", "find information",
            "look up", "query", "fetch data", "api call", "execute"
        ]
        
        return any(indicator in message.lower() for indicator in tool_indicators)
    
    def _requires_long_context(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires long context capabilities.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if long context capabilities are required, False otherwise
        """
        # Check if context contains a lot of history
        if context.get("history") and len(context["history"]) > 10:
            return True
        
        # Check if message is very long
        if len(message) > 2000:
            return True
        
        # Check if context contains large documents
        if context.get("documents") and len(context["documents"]) > 0:
            return True
        
        return False
    
    def _count_prompt_tokens(self, prompt: str) -> int:
        """
        Count the number of tokens in the prompt.
        
        Args:
            prompt: The prompt to count tokens for
            
        Returns:
            The number of tokens
        """
        # Grok doesn't provide a token counting API, so we use the utility function
        return super()._count_prompt_tokens(prompt)
    
    def _count_completion_tokens(self, completion: str) -> int:
        """
        Count the number of tokens in the completion.
        
        Args:
            completion: The completion to count tokens for
            
        Returns:
            The number of tokens
        """
        # Grok doesn't provide a token counting API, so we use the utility function
        return super()._count_completion_tokens(completion)
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Calculate the cost of the request based on Grok's pricing.
        
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
