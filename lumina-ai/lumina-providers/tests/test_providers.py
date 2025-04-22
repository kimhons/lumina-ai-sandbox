"""
Test script for Lumina AI provider integration.

This script tests the provider integration layer, including individual
provider adapters and the provider selection logic.
"""

import os
import sys
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import lumina modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lumina.providers.openai.provider import OpenAIProvider
from lumina.providers.claude.provider import ClaudeProvider
from lumina.providers.gemini.provider import GeminiProvider
from lumina.providers.deepseek.provider import DeepSeekProvider
from lumina.providers.grok.provider import GrokProvider
from lumina.providers.selector import ProviderSelector

def test_provider_initialization():
    """Test provider initialization."""
    logger.info("Testing provider initialization...")
    
    # Load API keys from environment variables or config file
    api_keys = {}
    try:
        # Try to load from environment variables
        api_keys = {
            "openai": os.environ.get("OPENAI_API_KEY", "dummy_key_for_testing"),
            "claude": os.environ.get("ANTHROPIC_API_KEY", "dummy_key_for_testing"),
            "gemini": os.environ.get("GOOGLE_API_KEY", "dummy_key_for_testing"),
            "deepseek": os.environ.get("DEEPSEEK_API_KEY", "dummy_key_for_testing"),
            "grok": os.environ.get("GROK_API_KEY", "dummy_key_for_testing")
        }
    except Exception as e:
        logger.warning(f"Failed to load API keys from environment variables: {str(e)}")
    
    # Initialize providers
    providers = {}
    provider_classes = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
        "deepseek": DeepSeekProvider,
        "grok": GrokProvider
    }
    
    for provider_id, provider_class in provider_classes.items():
        try:
            api_key = api_keys.get(provider_id, "dummy_key_for_testing")
            providers[provider_id] = provider_class(api_key)
            logger.info(f"Successfully initialized {provider_id} provider")
        except Exception as e:
            logger.error(f"Failed to initialize {provider_id} provider: {str(e)}")
    
    return providers

def test_provider_capabilities(providers):
    """Test provider capabilities."""
    logger.info("Testing provider capabilities...")
    
    for provider_id, provider in providers.items():
        try:
            capabilities = provider.get_capabilities()
            logger.info(f"{provider_id} capabilities: {json.dumps(capabilities, indent=2)}")
        except Exception as e:
            logger.error(f"Failed to get capabilities for {provider_id}: {str(e)}")

def test_provider_selection(providers):
    """Test provider selection logic."""
    logger.info("Testing provider selection logic...")
    
    # Initialize provider selector
    selector = ProviderSelector(providers)
    
    # Test cases
    test_cases = [
        {
            "name": "General query",
            "message": "What is the capital of France?",
            "context": {}
        },
        {
            "name": "Code generation",
            "message": "Write a Python function to calculate the Fibonacci sequence.",
            "context": {}
        },
        {
            "name": "Creative writing",
            "message": "Write a short story about a robot that becomes sentient.",
            "context": {}
        },
        {
            "name": "Data analysis",
            "message": "Analyze this dataset and tell me the key trends.",
            "context": {"documents": ["data.csv"]}
        },
        {
            "name": "Reasoning",
            "message": "Explain the philosophical implications of artificial general intelligence.",
            "context": {}
        },
        {
            "name": "Research",
            "message": "Provide a comprehensive overview of quantum computing.",
            "context": {}
        },
        {
            "name": "Math",
            "message": "Solve this differential equation: dy/dx = 2x + y",
            "context": {}
        },
        {
            "name": "Real-time knowledge",
            "message": "What are the latest developments in AI research this year?",
            "context": {}
        },
        {
            "name": "Multimodal",
            "message": "What's in this image?",
            "context": {"images": ["image.jpg"]}
        },
        {
            "name": "Long context",
            "message": "Summarize this long document.",
            "context": {"documents": ["long_document.txt"], "history": ["message1", "message2", "message3", "message4", "message5", "message6", "message7", "message8", "message9", "message10", "message11"]}
        },
        {
            "name": "Explicit provider selection",
            "message": "Tell me a joke.",
            "context": {"provider": "claude"}
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        try:
            provider_id, metadata = selector.select_provider(test_case["message"], test_case["context"])
            logger.info(f"Test case: {test_case['name']}")
            logger.info(f"Selected provider: {provider_id}")
            logger.info(f"Selection metadata: {json.dumps(metadata, indent=2)}")
            logger.info("---")
        except Exception as e:
            logger.error(f"Failed to select provider for test case {test_case['name']}: {str(e)}")

def test_model_selection(providers):
    """Test model selection within providers."""
    logger.info("Testing model selection within providers...")
    
    test_cases = [
        {
            "name": "Simple query",
            "message": "What is the weather like today?",
            "context": {}
        },
        {
            "name": "Complex reasoning",
            "message": "Explain the implications of quantum mechanics on our understanding of reality, including the many-worlds interpretation and the Copenhagen interpretation.",
            "context": {}
        },
        {
            "name": "Code generation",
            "message": "Write a Python function to implement a neural network from scratch.",
            "context": {}
        },
        {
            "name": "Multimodal",
            "message": "Describe what's in this image.",
            "context": {"images": ["image.jpg"]}
        }
    ]
    
    for provider_id, provider in providers.items():
        logger.info(f"Testing model selection for {provider_id}...")
        
        for test_case in test_cases:
            try:
                # Use the provider's internal model selection logic
                model = provider._select_model(test_case["message"], test_case["context"])
                logger.info(f"Test case: {test_case['name']}")
                logger.info(f"Selected model: {model}")
                logger.info("---")
            except Exception as e:
                logger.error(f"Failed to select model for test case {test_case['name']}: {str(e)}")

def main():
    """Main function."""
    logger.info("Starting provider integration tests...")
    
    # Test provider initialization
    providers = test_provider_initialization()
    
    # Test provider capabilities
    test_provider_capabilities(providers)
    
    # Test provider selection
    test_provider_selection(providers)
    
    # Test model selection
    test_model_selection(providers)
    
    logger.info("Provider integration tests completed.")

if __name__ == "__main__":
    main()
