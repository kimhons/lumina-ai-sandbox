import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
import json
import os
import sys

from .interfaces import (
    Agent, AgentType, AgentRole, AgentStatus, AgentCapability,
    Message, Task, Conversation, OrchestrationInterface
)
from .manager import OrchestrationManager
from .agents import AgentFactory, AIAgent, HumanAgent, ToolAgent
from .orchestrator import MultiAgentOrchestrator, TeamDefinition, Workflow, WorkflowStep
from .api import OrchestrationAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class OrchestrationService:
    """
    Service for running the multi-agent orchestration system.
    This class provides a high-level service that can be run as a standalone application.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize a new orchestration service.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.orchestrator = MultiAgentOrchestrator()
        self.api = OrchestrationAPI(self.orchestrator)
        self._running = False
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "service": {
                "name": "Lumina AI Orchestration Service",
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False,
                "log_level": "INFO"
            },
            "database": {
                "type": "memory",
                "connection_string": None
            },
            "security": {
                "enabled": True,
                "auth_service_url": "http://localhost:8081/auth"
            },
            "providers": {
                "openai": {
                    "enabled": True,
                    "api_key_env": "OPENAI_API_KEY"
                },
                "claude": {
                    "enabled": True,
                    "api_key_env": "ANTHROPIC_API_KEY"
                },
                "gemini": {
                    "enabled": True,
                    "api_key_env": "GOOGLE_API_KEY"
                },
                "deepseek": {
                    "enabled": False,
                    "api_key_env": "DEEPSEEK_API_KEY"
                },
                "grok": {
                    "enabled": False,
                    "api_key_env": "GROK_API_KEY"
                }
            },
            "memory": {
                "vector_store": {
                    "type": "inmemory",
                    "connection_string": None
                },
                "compression": {
                    "enabled": True,
                    "method": "pca"
                }
            },
            "tools": {
                "enabled": True,
                "tool_registry_url": "http://localhost:8082/tools"
            }
        }
        
        if not config_path:
            logger.info("No configuration file provided, using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Merge with default config
            merged_config = default_config.copy()
            for section, values in config.items():
                if section in merged_config:
                    if isinstance(merged_config[section], dict) and isinstance(values, dict):
                        merged_config[section].update(values)
                    else:
                        merged_config[section] = values
                else:
                    merged_config[section] = values
            
            logger.info(f"Loaded configuration from {config_path}")
            return merged_config
        
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return default_config
    
    async def start(self):
        """Start the orchestration service."""
        if self._running:
            logger.warning("Orchestration service already running")
            return
        
        self._running = True
        
        # Configure logging
        log_level = getattr(logging, self.config["service"]["log_level"])
        logging.getLogger().setLevel(log_level)
        
        # Start the orchestrator
        await self.orchestrator.start()
        
        # Create default agents if configured
        await self._create_default_agents()
        
        logger.info(f"Orchestration service started: {self.config['service']['name']}")
    
    async def stop(self):
        """Stop the orchestration service."""
        if not self._running:
            logger.warning("Orchestration service not running")
            return
        
        self._running = False
        
        # Stop the orchestrator
        await self.orchestrator.stop()
        
        logger.info("Orchestration service stopped")
    
    async def _create_default_agents(self):
        """Create default agents based on configuration."""
        # Create a default AI agent for each enabled provider
        for provider_name, provider_config in self.config["providers"].items():
            if provider_config["enabled"]:
                # Check if API key is available
                api_key_env = provider_config["api_key_env"]
                if api_key_env not in os.environ:
                    logger.warning(f"API key environment variable {api_key_env} not set for provider {provider_name}")
                    continue
                
                # Determine default model for provider
                default_model = self._get_default_model(provider_name)
                
                # Create the agent
                try:
                    agent_id = await self.orchestrator.create_agent(
                        agent_type=AgentType.AI,
                        name=f"{provider_name.capitalize()} Assistant",
                        role=AgentRole.ASSISTANT,
                        provider_name=provider_name,
                        model_name=default_model,
                        system_prompt="You are a helpful AI assistant.",
                        metadata={
                            "default": True,
                            "provider": provider_name
                        }
                    )
                    
                    logger.info(f"Created default AI agent for provider {provider_name} with ID {agent_id}")
                
                except Exception as e:
                    logger.error(f"Error creating default AI agent for provider {provider_name}: {e}")
    
    def _get_default_model(self, provider_name: str) -> str:
        """
        Get the default model for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Name of the default model
        """
        provider_models = {
            "openai": "gpt-4o",
            "claude": "claude-3-opus-20240229",
            "gemini": "gemini-pro",
            "deepseek": "deepseek-chat",
            "grok": "grok-1"
        }
        
        return provider_models.get(provider_name, "default")
    
    async def run_forever(self):
        """Run the service indefinitely."""
        await self.start()
        
        try:
            # Keep the service running
            while self._running:
                await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            logger.info("Service execution cancelled")
        
        except Exception as e:
            logger.error(f"Error in service execution: {e}")
        
        finally:
            await self.stop()


def run_service(config_path: str = None):
    """
    Run the orchestration service.
    
    Args:
        config_path: Path to configuration file
    """
    service = OrchestrationService(config_path)
    
    async def main():
        await service.run_forever()
    
    try:
        asyncio.run(main())
    
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    
    except Exception as e:
        logger.error(f"Error running service: {e}")


if __name__ == "__main__":
    # Get configuration path from command line arguments
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the service
    run_service(config_path)
