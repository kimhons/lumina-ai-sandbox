# GitHub Setup Instructions for Lumina AI

This document provides step-by-step instructions for setting up the GitHub organization and repositories for Lumina AI development.

## 1. Create GitHub Organization

1. Log in to your GitHub account
2. Click on your profile picture in the top-right corner
3. Select "Your organizations"
4. Click "New organization"
5. Select "Free" plan
6. Enter "LuminaAI" as the organization name
7. Enter your email address for billing
8. Select "My personal account" for organization ownership
9. Click "Create organization"

## 2. Configure Organization Settings

1. Go to the LuminaAI organization page
2. Click "Settings" in the top navigation bar
3. Under "Access", set the base permissions to "Write"
4. Enable "Allow forking of private repositories"
5. Under "Repository creation", select "Members can create repositories"
6. Under "Member privileges", enable "Allow members to create teams"
7. Save changes

## 3. Create Core Repositories

Execute the following commands to create the core repositories:

```bash
# Create a working directory for Lumina AI
mkdir -p ~/lumina-ai
cd ~/lumina-ai

# Initialize lumina-core repository
mkdir -p lumina-core
cd lumina-core
git init
echo "# Lumina Core" > README.md
echo "Central orchestration and core services for Lumina AI" >> README.md
echo "" >> README.md
echo "## Overview" >> README.md
echo "This repository contains the central orchestration service and core components of Lumina AI." >> README.md
echo "" >> README.md
echo "## Installation" >> README.md
echo "\`\`\`bash" >> README.md
echo "pip install -e ." >> README.md
echo "\`\`\`" >> README.md

# Create .gitignore file
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
EOL

# Create initial package structure
mkdir -p lumina/orchestration
mkdir -p lumina/api
mkdir -p tests

# Create __init__.py files
touch lumina/__init__.py
touch lumina/orchestration/__init__.py
touch lumina/api/__init__.py
touch tests/__init__.py

# Copy the orchestration service code
cat > lumina/orchestration/service.py << EOL
from typing import Dict, List, Optional, Any
import uuid

class OrchestrationService:
    """
    Central orchestration service for Lumina AI.
    Coordinates between all components and manages execution flow.
    """
    
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.providers = {}
        self.tools = {}
        self.memory = None
        self.security = None
    
    def register_provider(self, provider_id: str, provider: Any) -> None:
        """Register an AI provider with the orchestration service."""
        self.providers[provider_id] = provider
    
    def register_tool(self, tool_id: str, tool: Any) -> None:
        """Register a tool with the orchestration service."""
        self.tools[tool_id] = tool
    
    def set_memory(self, memory: Any) -> None:
        """Set the memory system for the orchestration service."""
        self.memory = memory
    
    def set_security(self, security: Any) -> None:
        """Set the security system for the orchestration service."""
        self.security = security
    
    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: The user message to process
            user_id: The ID of the user sending the message
            
        Returns:
            A dictionary containing the response and metadata
        """
        # Validate user permissions
        if self.security and not self.security.validate_user(user_id):
            return {"error": "Unauthorized"}
        
        # Store message in memory
        if self.memory:
            self.memory.store_message("user", message, user_id)
        
        # Determine task complexity and select provider
        provider = self._select_provider(message)
        if not provider:
            return {"error": "No suitable provider available"}
        
        # Process message with selected provider
        response = provider.process_message(message)
        
        # Store response in memory
        if self.memory:
            self.memory.store_message("assistant", response["content"], user_id)
        
        return response
    
    def _select_provider(self, message: str) -> Optional[Any]:
        """
        Select the most appropriate provider for the given message.
        
        Args:
            message: The user message to process
            
        Returns:
            The selected provider or None if no suitable provider is available
        """
        # Simple implementation - use first available provider
        # Will be enhanced with sophisticated selection logic
        if not self.providers:
            return None
        
        return next(iter(self.providers.values()))
EOL

# Create setup.py
cat > setup.py << EOL
from setuptools import setup, find_packages

setup(
    name="lumina-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
    ],
    author="Lumina AI Team",
    author_email="team@luminaai.com",
    description="Central orchestration and core services for Lumina AI",
    keywords="ai, agent, orchestration",
    python_requires=">=3.10",
)
EOL

# Create test file
cat > tests/test_orchestration.py << EOL
import pytest
from lumina.orchestration.service import OrchestrationService

class MockProvider:
    def process_message(self, message):
        return {"content": f"Processed: {message}", "provider": "mock"}
    
    def get_capabilities(self):
        return {"provider": "mock", "capabilities": {"text_generation": True}}
    
    def get_cost_estimate(self, message):
        return 0.0

class MockMemory:
    def __init__(self):
        self.messages = []
    
    def store_message(self, role, content, user_id):
        self.messages.append({"role": role, "content": content, "user_id": user_id})

class MockSecurity:
    def validate_user(self, user_id):
        return user_id == "valid_user"

def test_orchestration_service_initialization():
    service = OrchestrationService()
    assert service.conversation_id is not None
    assert service.providers == {}
    assert service.tools == {}
    assert service.memory is None
    assert service.security is None

def test_register_provider():
    service = OrchestrationService()
    provider = MockProvider()
    service.register_provider("mock", provider)
    assert "mock" in service.providers
    assert service.providers["mock"] == provider

def test_process_message():
    service = OrchestrationService()
    provider = MockProvider()
    service.register_provider("mock", provider)
    
    memory = MockMemory()
    service.set_memory(memory)
    
    security = MockSecurity()
    service.set_security(security)
    
    # Test with valid user
    response = service.process_message("Hello", "valid_user")
    assert response["content"] == "Processed: Hello"
    assert response["provider"] == "mock"
    assert len(memory.messages) == 2
    assert memory.messages[0]["role"] == "user"
    assert memory.messages[0]["content"] == "Hello"
    assert memory.messages[1]["role"] == "assistant"
    assert memory.messages[1]["content"] == "Processed: Hello"
    
    # Test with invalid user
    response = service.process_message("Hello", "invalid_user")
    assert "error" in response
    assert response["error"] == "Unauthorized"
EOL

# Create GitHub workflow for CI
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << EOL
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov flake8
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install -e .
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - name: Test with pytest
      run: |
        pytest --cov=./ --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
EOL

# Commit and push to GitHub
git add .
git commit -m "Initial commit for lumina-core"
git branch -M main

# Note: You'll need to create the repository on GitHub first
echo "Now create the 'lumina-core' repository on GitHub under the LuminaAI organization"
echo "Then run: git remote add origin https://github.com/LuminaAI/lumina-core.git"
echo "And: git push -u origin main"

# Return to the main directory
cd ..

# Repeat similar steps for other repositories (lumina-providers, lumina-memory, lumina-security)
# For brevity, only showing the first repository setup in detail
```

## 4. Create Provider Integration Repository

```bash
cd ~/lumina-ai

# Initialize lumina-providers repository
mkdir -p lumina-providers
cd lumina-providers
git init
echo "# Lumina Providers" > README.md
echo "AI provider integration for Lumina AI" >> README.md

# Create .gitignore file (same as for lumina-core)
# Create initial package structure
mkdir -p lumina/providers
touch lumina/__init__.py
touch lumina/providers/__init__.py
mkdir -p tests

# Create base provider interface
cat > lumina/providers/base.py << EOL
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProvider(ABC):
    """
    Base class for AI provider integration.
    All provider implementations must inherit from this class.
    """
    
    @abstractmethod
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: The user message to process
            
        Returns:
            A dictionary containing the response and metadata
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this provider.
        
        Returns:
            A dictionary describing the provider's capabilities
        """
        pass
    
    @abstractmethod
    def get_cost_estimate(self, message: str) -> float:
        """
        Estimate the cost of processing a message with this provider.
        
        Args:
            message: The user message to process
            
        Returns:
            The estimated cost in USD
        """
        pass
EOL

# Create OpenAI provider implementation
cat > lumina/providers/openai.py << EOL
import os
from typing import Dict, Any
import openai
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    """
    OpenAI provider integration for Lumina AI.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: OpenAI model to use (defaults to gpt-4o)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message using OpenAI and return a response.
        
        Args:
            message: The user message to process
            
        Returns:
            A dictionary containing the response and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Lumina AI, a versatile general AI solution that seamlessly connects thoughts and actions."},
                    {"role": "user", "content": message}
                ]
            )
            
            return {
                "content": response.choices[0].message.content,
                "provider": "openai",
                "model": self.model,
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the OpenAI provider.
        
        Returns:
            A dictionary describing the provider's capabilities
        """
        return {
            "provider": "openai",
            "model": self.model,
            "capabilities": {
                "text_generation": True,
                "code_generation": True,
                "reasoning": True,
                "tool_use": True,
                "image_understanding": self.model in ["gpt-4o", "gpt-4-vision"]
            }
        }
    
    def get_cost_estimate(self, message: str) -> float:
        """
        Estimate the cost of processing a message with OpenAI.
        
        Args:
            message: The user message to process
            
        Returns:
            The estimated cost in USD
        """
        # Rough token count estimation (4 chars = 1 token)
        estimated_tokens = len(message) / 4
        
        # GPT-4o pricing (as of 2025)
        input_cost_per_1k = 0.01
        output_cost_per_1k = 0.03
        
        # Assume output is roughly the same length as input
        estimated_cost = (estimated_tokens / 1000 * input_cost_per_1k) + (estimated_tokens / 1000 * output_cost_per_1k)
        
        return estimated_cost
EOL

# Create setup.py
cat > setup.py << EOL
from setuptools import setup, find_packages

setup(
    name="lumina-providers",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "google-generativeai>=0.3.0",
        "pydantic>=2.0.0",
    ],
    author="Lumina AI Team",
    author_email="team@luminaai.com",
    description="AI provider integration for Lumina AI",
    keywords="ai, provider, integration",
    python_requires=">=3.10",
)
EOL

# Commit and push to GitHub
git add .
git commit -m "Initial commit for lumina-providers"
git branch -M main

echo "Now create the 'lumina-providers' repository on GitHub under the LuminaAI organization"
echo "Then run: git remote add origin https://github.com/LuminaAI/lumina-providers.git"
echo "And: git push -u origin main"
```

## 5. Set Up Development Environment

```bash
# Create a virtual environment
cd ~/lumina-ai
python -m venv venv
source venv/bin/activate

# Install the packages in development mode
cd lumina-core
pip install -e .
cd ../lumina-providers
pip install -e .

# Create a .env file for API keys
cd ~/lumina-ai
cat > .env << EOL
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
EOL

# Create a simple test script
cat > test_lumina.py << EOL
import os
from dotenv import load_dotenv
from lumina.orchestration.service import OrchestrationService
from lumina.providers.openai import OpenAIProvider

# Load environment variables
load_dotenv()

# Initialize orchestration service
service = OrchestrationService()

# Register OpenAI provider
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY environment variable not set")
    exit(1)

openai_provider = OpenAIProvider(api_key=openai_api_key)
service.register_provider("openai", openai_provider)

# Test the service
message = "Hello, I'm testing Lumina AI. What can you do?"
response = service.process_message(message, "test_user")

print(f"User: {message}")
print(f"Lumina AI: {response['content']}")
print(f"Provider: {response.get('provider')}")
print(f"Model: {response.get('model')}")
EOL

# Run the test script
python test_lumina.py
```

## 6. Branching Strategy

Follow this branching strategy for all repositories:

1. **main**: Production-ready code
2. **develop**: Integration branch for features
3. **feature/xxx**: Individual feature branches
4. **release/x.y.z**: Release preparation
5. **hotfix/xxx**: Emergency fixes

### Workflow:

1. Create feature branch from develop:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/new-feature
   ```

2. Implement and test feature:
   ```bash
   # Make changes
   git add .
   git commit -m "Implement new feature"
   ```

3. Create pull request to develop:
   - Push feature branch to GitHub
   ```bash
   git push -u origin feature/new-feature
   ```
   - Create pull request on GitHub

4. After code review and automated testing, merge to develop:
   ```bash
   git checkout develop
   git pull
   git merge --no-ff feature/new-feature
   git push
   ```

5. Create release branch when ready:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/0.1.0
   ```

6. Final testing and version bumping:
   ```bash
   # Update version in setup.py
   git add setup.py
   git commit -m "Bump version to 0.1.0"
   ```

7. Merge to main and tag release:
   ```bash
   git checkout main
   git pull
   git merge --no-ff release/0.1.0
   git tag -a v0.1.0 -m "Version 0.1.0"
   git push --tags
   ```

## 7. GitHub Actions Setup

Create a GitHub Actions workflow file in each repository to automate testing and deployment:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov flake8
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install -e .
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - name: Test with pytest
      run: |
        pytest --cov=./ --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 8. Next Steps

After setting up the GitHub repositories:

1. Implement the remaining core components:
   - Memory system
   - Security framework
   - API gateway

2. Expand provider integration:
   - Claude integration
   - Gemini integration
   - DeepSeek integration
   - Grok integration

3. Begin implementing computer control capabilities:
   - Screen understanding
   - Action execution
   - Browser automation

4. Start developing the user interface:
   - Web application
   - Desktop applications
   - Mobile applications

These GitHub setup instructions provide a comprehensive guide for establishing the development infrastructure for Lumina AI. Following these steps will create a solid foundation for collaborative development and ensure consistent code quality across all repositories.
