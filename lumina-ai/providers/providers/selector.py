"""
Provider selection logic for Lumina AI.

This module implements the logic for selecting the optimal AI provider
for different types of requests based on task requirements, provider
capabilities, and cost considerations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import re

from lumina.common.utils import count_tokens
from lumina.providers.base import Provider

logger = logging.getLogger(__name__)

class ProviderSelector:
    """
    Provider selector for Lumina AI.
    
    This class implements the logic for selecting the optimal AI provider
    for different types of requests.
    """
    
    def __init__(self, providers: Dict[str, Provider], config: Optional[Dict[str, Any]] = None):
        """
        Initialize the provider selector.
        
        Args:
            providers: Dictionary of provider instances keyed by provider ID
            config: Optional configuration dictionary
        """
        self.providers = providers
        self.config = config or {}
        
        # Default provider priorities
        self.default_priorities = self.config.get("default_priorities", [
            "openai",
            "claude",
            "gemini",
            "deepseek",
            "grok"
        ])
        
        # Task type to provider mapping
        self.task_provider_mapping = self.config.get("task_provider_mapping", {
            "general": ["openai", "claude", "gemini", "grok", "deepseek"],
            "creative_writing": ["claude", "openai", "gemini", "grok", "deepseek"],
            "code_generation": ["openai", "deepseek", "claude", "gemini", "grok"],
            "data_analysis": ["gemini", "openai", "claude", "grok", "deepseek"],
            "reasoning": ["claude", "openai", "gemini", "grok", "deepseek"],
            "research": ["claude", "openai", "gemini", "grok", "deepseek"],
            "math": ["deepseek", "openai", "gemini", "claude", "grok"],
            "real_time_knowledge": ["grok", "gemini", "openai", "claude", "deepseek"]
        })
        
        # Initialize provider capabilities cache
        self.provider_capabilities = {}
        for provider_id, provider in self.providers.items():
            try:
                self.provider_capabilities[provider_id] = provider.get_capabilities()
            except Exception as e:
                logger.warning(f"Failed to get capabilities for provider {provider_id}: {str(e)}")
                self.provider_capabilities[provider_id] = {}
        
        logger.info(f"Provider selector initialized with {len(providers)} providers")
    
    def select_provider(self, message: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Select the optimal provider for a message.
        
        Args:
            message: The user message
            context: Optional context information
            
        Returns:
            A tuple of (provider_id, selection_metadata)
        """
        context = context or {}
        
        # If provider is explicitly specified in context, use it
        if context.get("provider") and context["provider"] in self.providers:
            provider_id = context["provider"]
            return provider_id, {
                "reason": "explicitly_specified",
                "score": 1.0,
                "alternatives": []
            }
        
        # Determine task type
        task_type = self._determine_task_type(message, context)
        
        # Get provider priorities for this task type
        provider_priorities = self.task_provider_mapping.get(task_type, self.default_priorities)
        
        # Check required capabilities
        required_capabilities = self._determine_required_capabilities(message, context)
        
        # Calculate scores for each provider
        provider_scores = []
        for provider_id in provider_priorities:
            if provider_id not in self.providers:
                continue
            
            # Check if provider has all required capabilities
            provider_capabilities = self.provider_capabilities.get(provider_id, {})
            has_required_capabilities = all(
                capability in provider_capabilities and provider_capabilities[capability]
                for capability in required_capabilities
            )
            
            if not has_required_capabilities:
                continue
            
            # Calculate base score based on priority
            priority_score = 1.0 - (provider_priorities.index(provider_id) / len(provider_priorities))
            
            # Adjust score based on cost if cost optimization is enabled
            cost_score = 1.0
            if self.config.get("optimize_for_cost", False):
                try:
                    cost = self.providers[provider_id].get_cost_estimate(message)
                    # Normalize cost score (lower cost = higher score)
                    max_cost = 0.01  # Assume $0.01 is the maximum reasonable cost
                    cost_score = max(0.0, 1.0 - (cost / max_cost))
                except Exception as e:
                    logger.warning(f"Failed to get cost estimate for provider {provider_id}: {str(e)}")
            
            # Adjust score based on latency if speed optimization is enabled
            speed_score = 1.0
            if self.config.get("optimize_for_speed", False):
                # Simple heuristic: OpenAI and Gemini tend to be faster
                if provider_id == "openai" or provider_id == "gemini":
                    speed_score = 1.0
                elif provider_id == "grok":
                    speed_score = 0.9
                elif provider_id == "claude":
                    speed_score = 0.8
                elif provider_id == "deepseek":
                    speed_score = 0.7
            
            # Calculate final score
            # Weights can be adjusted based on configuration
            priority_weight = self.config.get("priority_weight", 0.5)
            cost_weight = self.config.get("cost_weight", 0.3) if self.config.get("optimize_for_cost", False) else 0.0
            speed_weight = self.config.get("speed_weight", 0.2) if self.config.get("optimize_for_speed", False) else 0.0
            
            # Normalize weights
            total_weight = priority_weight + cost_weight + speed_weight
            if total_weight > 0:
                priority_weight /= total_weight
                cost_weight /= total_weight
                speed_weight /= total_weight
            
            final_score = (
                priority_score * priority_weight +
                cost_score * cost_weight +
                speed_score * speed_weight
            )
            
            provider_scores.append((provider_id, final_score))
        
        # Sort providers by score
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        
        # If no provider is suitable, use the first available provider
        if not provider_scores:
            default_provider_id = next(iter(self.providers.keys()))
            return default_provider_id, {
                "reason": "fallback_to_default",
                "score": 0.0,
                "alternatives": []
            }
        
        # Select the provider with the highest score
        selected_provider_id, selected_score = provider_scores[0]
        
        # Prepare alternatives for metadata
        alternatives = [
            {"provider": provider_id, "score": score}
            for provider_id, score in provider_scores[1:3]  # Include top 2 alternatives
        ]
        
        return selected_provider_id, {
            "reason": f"optimal_for_{task_type}",
            "task_type": task_type,
            "required_capabilities": required_capabilities,
            "score": selected_score,
            "alternatives": alternatives
        }
    
    def _determine_task_type(self, message: str, context: Dict[str, Any]) -> str:
        """
        Determine the type of task based on the message and context.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            The task type
        """
        # If task type is explicitly specified in context, use it
        if context.get("task_type") and context["task_type"] in self.task_provider_mapping:
            return context["task_type"]
        
        # Check for code generation
        code_indicators = [
            "code", "function", "program", "script", "algorithm",
            "python", "javascript", "java", "c++", "typescript",
            "implement", "develop", "create a function", "write a program"
        ]
        if any(indicator in message.lower() for indicator in code_indicators):
            return "code_generation"
        
        # Check for creative writing
        creative_indicators = [
            "write a story", "creative", "poem", "novel", "fiction",
            "narrative", "character", "plot", "setting", "dialogue",
            "write an article", "blog post", "essay"
        ]
        if any(indicator in message.lower() for indicator in creative_indicators):
            return "creative_writing"
        
        # Check for data analysis
        data_indicators = [
            "data", "analysis", "statistics", "graph", "chart",
            "dataset", "correlation", "regression", "predict",
            "analyze these numbers", "data science", "visualization"
        ]
        if any(indicator in message.lower() for indicator in data_indicators):
            return "data_analysis"
        
        # Check for reasoning
        reasoning_indicators = [
            "explain", "why", "how", "reason", "logic",
            "analyze", "evaluate", "assess", "critique",
            "implications", "consequences", "philosophy"
        ]
        if any(indicator in message.lower() for indicator in reasoning_indicators):
            return "reasoning"
        
        # Check for research
        research_indicators = [
            "research", "information", "find", "search",
            "literature", "paper", "study", "investigation",
            "background", "history", "overview", "summary"
        ]
        if any(indicator in message.lower() for indicator in research_indicators):
            return "research"
        
        # Check for math
        math_indicators = [
            "math", "equation", "calculation", "formula", "solve",
            "calculus", "algebra", "geometry", "statistics",
            "probability", "theorem", "proof", "numerical"
        ]
        if any(indicator in message.lower() for indicator in math_indicators):
            return "math"
        
        # Check for real-time knowledge
        realtime_indicators = [
            "current", "latest", "recent", "news", "today",
            "update", "happening now", "real-time", "live",
            "this week", "this month", "this year"
        ]
        if any(indicator in message.lower() for indicator in realtime_indicators):
            return "real_time_knowledge"
        
        # Default to general
        return "general"
    
    def _determine_required_capabilities(self, message: str, context: Dict[str, Any]) -> List[str]:
        """
        Determine the required capabilities based on the message and context.
        
        Args:
            message: The user message
            context: Context information
            
        Returns:
            List of required capability names
        """
        required_capabilities = []
        
        # Check for multimodal requirements
        if context.get("images") or context.get("attachments"):
            required_capabilities.append("multimodal")
        
        multimodal_indicators = [
            "image", "picture", "photo", "diagram", "chart", "graph",
            "analyze this image", "look at this picture", "what's in this photo"
        ]
        if any(indicator in message.lower() for indicator in multimodal_indicators):
            required_capabilities.append("multimodal")
        
        # Check for tool use requirements
        if context.get("tools") or context.get("require_tools"):
            required_capabilities.append("tool_use")
        
        tool_indicators = [
            "use tool", "search for", "calculate", "find information",
            "look up", "query", "fetch data", "api call", "execute"
        ]
        if any(indicator in message.lower() for indicator in tool_indicators):
            required_capabilities.append("tool_use")
        
        # Check for long context requirements
        if context.get("history") and len(context["history"]) > 10:
            required_capabilities.append("long_context")
        
        if len(message) > 2000:
            required_capabilities.append("long_context")
        
        if context.get("documents") and len(context["documents"]) > 0:
            required_capabilities.append("long_context")
        
        # Check for code generation requirements
        code_indicators = [
            "code", "function", "program", "script", "algorithm",
            "python", "javascript", "java", "c++", "typescript",
            "implement", "develop", "create a function", "write a program"
        ]
        if any(indicator in message.lower() for indicator in code_indicators):
            required_capabilities.append("code_generation")
        
        # Check for streaming requirements
        if context.get("streaming", False):
            required_capabilities.append("streaming")
        
        # Check for function calling requirements
        if context.get("functions") or context.get("require_function_calling"):
            required_capabilities.append("function_calling")
        
        return list(set(required_capabilities))  # Remove duplicates
