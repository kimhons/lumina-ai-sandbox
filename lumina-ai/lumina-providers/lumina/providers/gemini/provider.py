"""
Gemini provider implementation for Lumina AI.

This module implements the Gemini provider for Lumina AI, providing
integration with Google's Gemini models like Gemini 1.5 Pro and Gemini 1.5 Flash.
"""

import os
from typing import Dict, Any, Optional, List
import logging
import json
import time
import google.generativeai as genai

from lumina.providers.base import Provider
from lumina.common.utils import timestamp, format_error

logger = logging.getLogger(__name__)

class GeminiProvider(Provider):
    """
    Gemini provider implementation.
    
    This class implements the Provider interface for Google's Gemini,
    providing access to models like Gemini 1.5 Pro and Gemini 1.5 Flash.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Google API key
            config: Optional configuration dictionary
        """
        super().__init__("gemini", api_key, config)
        
        # Initialize Gemini client
        genai.configure(api_key=api_key)
        
        # Define available models and their capabilities
        self.models = {
            "gemini-1.5-pro": {
                "context_window": 1000000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.00000035,  # per token
                    "completion": 0.00000105  # per token
                }
            },
            "gemini-1.5-flash": {
                "context_window": 1000000,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.000000175,  # per token
                    "completion": 0.000000525  # per token
                }
            },
            "gemini-1.0-pro": {
                "context_window": 32768,
                "capabilities": {
                    "text_generation": True,
                    "code_generation": True,
                    "reasoning": True,
                    "tool_use": True,
                    "multimodal": True
                },
                "pricing": {
                    "prompt": 0.0000005,  # per token
                    "completion": 0.0000015  # per token
                }
            }
        }
        
        # Set default model
        self.default_model = config.get("default_model", "gemini-1.5-pro")
        if self.default_model not in self.models:
            logger.warning(f"Default model {self.default_model} not available, using first available model")
            self.default_model = next(iter(self.models.keys()))
        
        # Initialize model instances
        self.model_instances = {}
        for model_name in self.models:
            try:
                self.model_instances[model_name] = genai.GenerativeModel(model_name)
            except Exception as e:
                logger.warning(f"Failed to initialize model {model_name}: {str(e)}")
        
        logger.info(f"Gemini provider initialized with {len(self.models)} models")
    
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Generate a completion using Gemini's API.
        
        Args:
            prompt: The prompt to generate a completion for
            model: The model to use
            
        Returns:
            The generated completion
        """
        try:
            # Get model instance
            model_instance = self.model_instances.get(model)
            if not model_instance:
                raise ValueError(f"Model {model} not initialized")
            
            # Create messages from prompt
            messages = self._create_messages(prompt)
            
            # Call Gemini API
            generation_config = {
                "temperature": self.config.get("temperature", 0.7),
                "top_p": self.config.get("top_p", 1.0),
                "top_k": self.config.get("top_k", 40),
                "max_output_tokens": self.config.get("max_tokens", 1000),
            }
            
            if len(messages) > 1:
                # Use chat mode
                chat = model_instance.start_chat(history=[])
                for msg in messages:
                    if msg["role"] == "user":
                        chat.send_message(msg["content"], generation_config=generation_config)
                    # Note: system messages are handled differently in Gemini
                
                # Get the last response
                if chat.history:
                    last_response = chat.history[-1]
                    if hasattr(last_response, 'parts') and last_response.parts:
                        return str(last_response.parts[0])
                    else:
                        return ""
                else:
                    return ""
            else:
                # Use completion mode for single messages
                content = messages[0]["content"] if messages else prompt
                response = model_instance.generate_content(
                    content,
                    generation_config=generation_config
                )
                
                if response and hasattr(response, 'text'):
                    return response.text
                else:
                    logger.warning("Gemini API returned empty response")
                    return ""
        
        except Exception as e:
            logger.error(f"Error generating completion with Gemini: {str(e)}")
            raise
    
    def _create_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create messages array from prompt.
        
        Args:
            prompt: The prompt text
            
        Returns:
            List of message dictionaries for Gemini API
        """
        # Check if prompt is already in JSON format for messages
        if prompt.startswith('[') and prompt.endswith(']'):
            try:
                messages = json.loads(prompt)
                if isinstance(messages, list) and all(isinstance(m, dict) and 'role' in m and 'content' in m for m in messages):
                    # Convert to Gemini message format
                    return [
                        {
                            "role": "model" if m["role"] == "assistant" else m["role"],
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
        Get the capabilities of the Gemini provider.
        
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
            "long_context": True
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
        requires_long_context = self._requires_long_context(message, context)
        requires_fast_response = self._requires_fast_response(message, context)
        
        # Select model based on requirements
        if requires_long_context or requires_complex_reasoning:
            return "gemini-1.5-pro" if "gemini-1.5-pro" in self.models else self.default_model
        elif requires_fast_response:
            return "gemini-1.5-flash" if "gemini-1.5-flash" in self.models else self.default_model
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
        if len(message) > 800:
            return True
        
        complexity_indicators = [
            "explain", "analyze", "compare", "evaluate", "synthesize",
            "why", "how", "what if", "implications", "consequences",
            "complex", "detailed", "thorough", "comprehensive"
        ]
        
        return any(indicator in message.lower() for indicator in complexity_indicators)
    
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
    
    def _requires_fast_response(self, message: str, context: Dict[str, Any]) -> bool:
        """
        Check if the message requires a fast response.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            True if a fast response is required, False otherwise
        """
        # Check if context explicitly requests fast response
        if context.get("priority") == "speed":
            return True
        
        # Check if message is short and simple
        if len(message) < 100 and not self._requires_complex_reasoning(message, context):
            return True
        
        # Check for indicators of urgency
        urgency_indicators = [
            "quick", "fast", "urgent", "immediately", "asap",
            "hurry", "rush", "emergency", "now", "soon"
        ]
        
        return any(indicator in message.lower() for indicator in urgency_indicators)
    
    def _count_prompt_tokens(self, prompt: str) -> int:
        """
        Count the number of tokens in the prompt.
        
        Args:
            prompt: The prompt to count tokens for
            
        Returns:
            The number of tokens
        """
        try:
            # Use Gemini's token counting
            result = genai.count_tokens(model=self.default_model, prompt=prompt)
            return result.total_tokens
        except Exception as e:
            logger.warning(f"Error counting tokens with Gemini API: {str(e)}")
            # Fall back to the utility function
            return super()._count_prompt_tokens(prompt)
    
    def _count_completion_tokens(self, completion: str) -> int:
        """
        Count the number of tokens in the completion.
        
        Args:
            completion: The completion to count tokens for
            
        Returns:
            The number of tokens
        """
        try:
            # Use Gemini's token counting
            result = genai.count_tokens(model=self.default_model, prompt=completion)
            return result.total_tokens
        except Exception as e:
            logger.warning(f"Error counting tokens with Gemini API: {str(e)}")
            # Fall back to the utility function
            return super()._count_completion_tokens(completion)
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Calculate the cost of the request based on Gemini's pricing.
        
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
