"""
Base provider implementation for Lumina AI.

This module provides a base implementation of the BaseProvider interface
that can be extended by specific provider implementations.
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List
import logging
import time

from lumina.common.interfaces import BaseProvider
from lumina.common.utils import timestamp, count_tokens, format_error

logger = logging.getLogger(__name__)

class Provider(BaseProvider):
    """
    Base implementation of the BaseProvider interface.
    
    This class provides common functionality for all provider implementations
    and should be extended by specific provider classes.
    """
    
    def __init__(self, provider_id: str, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the provider.
        
        Args:
            provider_id: Unique identifier for the provider
            api_key: API key for authentication
            config: Optional configuration dictionary
        """
        self.provider_id = provider_id
        self.api_key = api_key
        self.config = config or {}
        self.models = {}
        logger.info(f"Initialized {provider_id} provider")
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: The user message to process
            context: Optional context information
            
        Returns:
            A dictionary containing the response and metadata
        """
        start_time = time.time()
        context = context or {}
        
        try:
            # Select the appropriate model based on context
            model = self._select_model(message, context)
            
            # Prepare the prompt
            prompt = self._prepare_prompt(message, context)
            
            # Count tokens
            prompt_tokens = self._count_prompt_tokens(prompt)
            
            # Generate completion
            completion = self._generate_completion(prompt, model)
            
            # Count completion tokens
            completion_tokens = self._count_completion_tokens(completion)
            
            # Process the completion
            processed_completion = self._process_completion(completion)
            
            # Calculate cost
            cost = self._calculate_cost(prompt_tokens, completion_tokens, model)
            
            # Prepare response
            response = {
                "content": processed_completion,
                "provider": self.provider_id,
                "model": model,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": prompt_tokens + completion_tokens
                },
                "cost": cost,
                "latency": time.time() - start_time,
                "timestamp": timestamp()
            }
            
            logger.info(f"{self.provider_id} processed message: {prompt_tokens} prompt tokens, {completion_tokens} completion tokens")
            return response
        
        except Exception as e:
            logger.error(f"Error processing message with {self.provider_id}: {str(e)}")
            return {
                "error": str(e),
                "provider": self.provider_id,
                "timestamp": timestamp(),
                "latency": time.time() - start_time
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this provider.
        
        Returns:
            A dictionary describing the provider's capabilities
        """
        return {
            "provider": self.provider_id,
            "models": list(self.models.keys()),
            "capabilities": self._get_provider_capabilities()
        }
    
    def get_cost_estimate(self, message: str) -> float:
        """
        Estimate the cost of processing a message with this provider.
        
        Args:
            message: The user message to process
            
        Returns:
            The estimated cost in USD
        """
        model = self._select_model(message, {})
        prompt_tokens = count_tokens(message)
        # Assume completion is roughly the same length as prompt for estimation
        completion_tokens = prompt_tokens
        return self._calculate_cost(prompt_tokens, completion_tokens, model)
    
    @abstractmethod
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Generate a completion for the given prompt using the specified model.
        
        Args:
            prompt: The prompt to generate a completion for
            model: The model to use
            
        Returns:
            The generated completion
        """
        pass
    
    @abstractmethod
    def _get_provider_capabilities(self) -> Dict[str, bool]:
        """
        Get the capabilities specific to this provider.
        
        Returns:
            A dictionary of capability names and boolean values
        """
        pass
    
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
        
        # Default to the first available model
        if self.models:
            return next(iter(self.models.keys()))
        
        # If no models are available, raise an exception
        raise ValueError(f"No models available for {self.provider_id}")
    
    def _prepare_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """
        Prepare the prompt for the model.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            The prepared prompt
        """
        # Simple implementation that just returns the message
        # Subclasses should override this to implement more sophisticated prompt preparation
        return message
    
    def _process_completion(self, completion: str) -> str:
        """
        Process the completion from the model.
        
        Args:
            completion: The raw completion from the model
            
        Returns:
            The processed completion
        """
        # Simple implementation that just returns the completion
        # Subclasses should override this to implement more sophisticated completion processing
        return completion
    
    def _count_prompt_tokens(self, prompt: str) -> int:
        """
        Count the number of tokens in the prompt.
        
        Args:
            prompt: The prompt to count tokens for
            
        Returns:
            The number of tokens
        """
        # Simple implementation using the utility function
        # Subclasses should override this to use provider-specific tokenizers
        return count_tokens(prompt)
    
    def _count_completion_tokens(self, completion: str) -> int:
        """
        Count the number of tokens in the completion.
        
        Args:
            completion: The completion to count tokens for
            
        Returns:
            The number of tokens
        """
        # Simple implementation using the utility function
        # Subclasses should override this to use provider-specific tokenizers
        return count_tokens(completion)
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Calculate the cost of the request.
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            model: The model used
            
        Returns:
            The cost in USD
        """
        # Default implementation that assumes zero cost
        # Subclasses should override this to implement provider-specific cost calculations
        return 0.0
