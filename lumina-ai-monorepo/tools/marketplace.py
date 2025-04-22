"""
Marketplace module for Lumina AI's Expanded Tool Ecosystem.

This module provides functionality for discovering, distributing, and managing
third-party tools and integrations.
"""

import datetime
import hashlib
import json
import os
import re
import uuid
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import logging
from enum import Enum

from .registry import ToolRegistry, ToolMetadata
from .interface import ToolInterface
from .execution import ToolExecutionEngine
from .monitoring import ToolMonitoring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolVerificationStatus(Enum):
    """Status of tool verification."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ToolPublishStatus(Enum):
    """Status of tool publication."""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    REMOVED = "removed"

class ToolCategory(Enum):
    """Categories for marketplace tools."""
    DATA_PROCESSING = "data_processing"
    COMMUNICATION = "communication"
    FILE_MANAGEMENT = "file_management"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    SECURITY = "security"
    AI_ML = "ai_ml"
    UTILITY = "utility"
    VISUALIZATION = "visualization"
    PRODUCTIVITY = "productivity"
    COLLABORATION = "collaboration"
    OTHER = "other"

class ToolRating:
    """Rating for a marketplace tool."""
    
    def __init__(
        self,
        user_id: str,
        tool_id: str,
        rating: int,
        review: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None
    ):
        """
        Initialize tool rating.
        
        Args:
            user_id: User identifier
            tool_id: Tool identifier
            rating: Rating value (1-5)
            review: Optional review text
            timestamp: Rating timestamp
        """
        self.user_id = user_id
        self.tool_id = tool_id
        self.rating = max(1, min(5, rating))  # Ensure rating is between 1 and 5
        self.review = review
        self.timestamp = timestamp or datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rating to dictionary."""
        return {
            "user_id": self.user_id,
            "tool_id": self.tool_id,
            "rating": self.rating,
            "review": self.review,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolRating':
        """Create rating from dictionary."""
        return cls(
            user_id=data["user_id"],
            tool_id=data["tool_id"],
            rating=data["rating"],
            review=data.get("review"),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"])
        )

class ToolDeveloper:
    """Developer information for marketplace tools."""
    
    def __init__(
        self,
        developer_id: str,
        name: str,
        email: str,
        organization: Optional[str] = None,
        website: Optional[str] = None,
        verified: bool = False
    ):
        """
        Initialize tool developer.
        
        Args:
            developer_id: Developer identifier
            name: Developer name
            email: Developer email
            organization: Optional organization name
            website: Optional website URL
            verified: Whether developer is verified
        """
        self.developer_id = developer_id
        self.name = name
        self.email = email
        self.organization = organization
        self.website = website
        self.verified = verified
        self.created_at = datetime.datetime.now()
        self.tools: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert developer to dictionary."""
        return {
            "developer_id": self.developer_id,
            "name": self.name,
            "email": self.email,
            "organization": self.organization,
            "website": self.website,
            "verified": self.verified,
            "created_at": self.created_at.isoformat(),
            "tools": self.tools
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolDeveloper':
        """Create developer from dictionary."""
        developer = cls(
            developer_id=data["developer_id"],
            name=data["name"],
            email=data["email"],
            organization=data.get("organization"),
            website=data.get("website"),
            verified=data.get("verified", False)
        )
        developer.created_at = datetime.datetime.fromisoformat(data["created_at"])
        developer.tools = data.get("tools", [])
        return developer

class MarketplaceTool:
    """Tool in the marketplace."""
    
    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        version: str,
        developer_id: str,
        categories: List[ToolCategory],
        tags: List[str],
        parameters: Dict[str, Dict[str, Any]],
        implementation_type: str,
        implementation: Any,
        documentation_url: Optional[str] = None,
        icon_url: Optional[str] = None,
        screenshots: Optional[List[str]] = None,
        pricing_model: Optional[str] = None,
        pricing_details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize marketplace tool.
        
        Args:
            tool_id: Tool identifier
            name: Tool name
            description: Tool description
            version: Tool version
            developer_id: Developer identifier
            categories: Tool categories
            tags: Tool tags
            parameters: Tool parameters
            implementation_type: Implementation type (python, javascript, etc.)
            implementation: Tool implementation
            documentation_url: Optional documentation URL
            icon_url: Optional icon URL
            screenshots: Optional screenshot URLs
            pricing_model: Optional pricing model (free, paid, subscription)
            pricing_details: Optional pricing details
        """
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.version = version
        self.developer_id = developer_id
        self.categories = categories
        self.tags = tags
        self.parameters = parameters
        self.implementation_type = implementation_type
        self.implementation = implementation
        self.documentation_url = documentation_url
        self.icon_url = icon_url
        self.screenshots = screenshots or []
        self.pricing_model = pricing_model or "free"
        self.pricing_details = pricing_details or {}
        
        # Metadata
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.verification_status = ToolVerificationStatus.PENDING
        self.publish_status = ToolPublishStatus.DRAFT
        self.downloads = 0
        self.ratings: List[ToolRating] = []
        self.average_rating = 0.0
    
    def update_average_rating(self) -> None:
        """Update the average rating based on all ratings."""
        if not self.ratings:
            self.average_rating = 0.0
            return
        
        total = sum(rating.rating for rating in self.ratings)
        self.average_rating = total / len(self.ratings)
    
    def add_rating(self, rating: ToolRating) -> None:
        """
        Add a rating to the tool.
        
        Args:
            rating: Tool rating
        """
        # Check if user has already rated
        for i, existing_rating in enumerate(self.ratings):
            if existing_rating.user_id == rating.user_id:
                # Update existing rating
                self.ratings[i] = rating
                self.update_average_rating()
                return
        
        # Add new rating
        self.ratings.append(rating)
        self.update_average_rating()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert marketplace tool to dictionary."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "developer_id": self.developer_id,
            "categories": [category.value for category in self.categories],
            "tags": self.tags,
            "parameters": self.parameters,
            "implementation_type": self.implementation_type,
            "implementation": self.implementation,
            "documentation_url": self.documentation_url,
            "icon_url": self.icon_url,
            "screenshots": self.screenshots,
            "pricing_model": self.pricing_model,
            "pricing_details": self.pricing_details,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "verification_status": self.verification_status.value,
            "publish_status": self.publish_status.value,
            "downloads": self.downloads,
            "ratings": [rating.to_dict() for rating in self.ratings],
            "average_rating": self.average_rating
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketplaceTool':
        """Create marketplace tool from dictionary."""
        tool = cls(
            tool_id=data["tool_id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            developer_id=data["developer_id"],
            categories=[ToolCategory(category) for category in data["categories"]],
            tags=data["tags"],
            parameters=data["parameters"],
            implementation_type=data["implementation_type"],
            implementation=data["implementation"],
            documentation_url=data.get("documentation_url"),
            icon_url=data.get("icon_url"),
            screenshots=data.get("screenshots", []),
            pricing_model=data.get("pricing_model", "free"),
            pricing_details=data.get("pricing_details", {})
        )
        
        tool.created_at = datetime.datetime.fromisoformat(data["created_at"])
        tool.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        tool.verification_status = ToolVerificationStatus(data["verification_status"])
        tool.publish_status = ToolPublishStatus(data["publish_status"])
        tool.downloads = data["downloads"]
        tool.ratings = [ToolRating.from_dict(rating) for rating in data.get("ratings", [])]
        tool.average_rating = data.get("average_rating", 0.0)
        
        return tool

class ToolVerifier:
    """Verifies third-party tools for security and quality."""
    
    def __init__(self):
        """Initialize tool verifier."""
        self.security_checks = [
            self._check_code_injection,
            self._check_data_leakage,
            self._check_resource_usage,
            self._check_network_access,
            self._check_file_access
        ]
        
        self.quality_checks = [
            self._check_documentation,
            self._check_error_handling,
            self._check_parameter_validation,
            self._check_performance
        ]
    
    def verify_tool(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """
        Verify a tool for security and quality.
        
        Args:
            tool: Tool to verify
            
        Returns:
            Tuple of (passed, issues)
        """
        issues = []
        
        # Run security checks
        for check in self.security_checks:
            result, check_issues = check(tool)
            if not result:
                issues.extend(check_issues)
        
        # Run quality checks
        for check in self.quality_checks:
            result, check_issues = check(tool)
            if not result:
                issues.extend(check_issues)
        
        # Tool passes if no issues found
        passed = len(issues) == 0
        
        return passed, issues
    
    def _check_code_injection(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for potential code injection vulnerabilities."""
        issues = []
        
        # Check implementation for eval, exec, etc.
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                if "eval(" in code or "exec(" in code:
                    issues.append("Tool uses potentially unsafe eval() or exec() functions")
                
                if "__import__(" in code:
                    issues.append("Tool uses potentially unsafe __import__() function")
                
                if "subprocess" in code and any(func in code for func in ["call", "Popen", "run"]):
                    issues.append("Tool uses subprocess module which may be unsafe")
                
                if "os.system" in code:
                    issues.append("Tool uses potentially unsafe os.system() function")
        
        return len(issues) == 0, issues
    
    def _check_data_leakage(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for potential data leakage."""
        issues = []
        
        # Check for hardcoded credentials
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                # Check for API keys, tokens, etc.
                api_key_pattern = r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']'
                token_pattern = r'token["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']'
                password_pattern = r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']'
                
                if re.search(api_key_pattern, code):
                    issues.append("Tool contains hardcoded API key")
                
                if re.search(token_pattern, code):
                    issues.append("Tool contains hardcoded token")
                
                if re.search(password_pattern, code):
                    issues.append("Tool contains hardcoded password")
                
                # Check for external data transmission
                if "requests." in code and "post(" in code:
                    issues.append("Tool sends data to external services, review carefully")
        
        return len(issues) == 0, issues
    
    def _check_resource_usage(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for excessive resource usage."""
        issues = []
        
        # Check for potential resource-intensive operations
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                # Check for infinite loops
                if "while True" in code:
                    issues.append("Tool contains potentially infinite loop (while True)")
                
                # Check for large memory usage
                if "numpy" in code and "zeros" in code:
                    large_array_pattern = r'zeros\(\s*\(\s*\d{4,}'
                    if re.search(large_array_pattern, code):
                        issues.append("Tool may allocate very large arrays")
        
        return len(issues) == 0, issues
    
    def _check_network_access(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for unauthorized network access."""
        issues = []
        
        # Check for network access
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                if "socket." in code:
                    issues.append("Tool uses socket module for direct network access")
                
                if "requests." in code:
                    # Extract URLs
                    url_pattern = r'requests\.[a-z]+\(\s*[\'"]([^\'"]+)[\'"]'
                    urls = re.findall(url_pattern, code)
                    
                    for url in urls:
                        if not url.startswith(("https://api.", "https://www.")):
                            issues.append(f"Tool accesses potentially unsafe URL: {url}")
        
        return len(issues) == 0, issues
    
    def _check_file_access(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for unauthorized file access."""
        issues = []
        
        # Check for file access
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                if "open(" in code:
                    issues.append("Tool uses file operations, review file access patterns")
                
                if "os.path" in code:
                    issues.append("Tool uses os.path module, review file access patterns")
                
                if "shutil" in code:
                    issues.append("Tool uses shutil module which can modify files and directories")
        
        return len(issues) == 0, issues
    
    def _check_documentation(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for adequate documentation."""
        issues = []
        
        # Check description length
        if len(tool.description) < 50:
            issues.append("Tool description is too short (minimum 50 characters)")
        
        # Check parameter documentation
        for param_name, param_info in tool.parameters.items():
            if "description" not in param_info or len(param_info["description"]) < 10:
                issues.append(f"Parameter '{param_name}' has insufficient description")
        
        # Check for documentation URL
        if not tool.documentation_url:
            issues.append("Tool is missing documentation URL")
        
        return len(issues) == 0, issues
    
    def _check_error_handling(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for proper error handling."""
        issues = []
        
        # Check for try/except blocks
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                if "try:" not in code:
                    issues.append("Tool does not use exception handling (try/except)")
        
        return len(issues) == 0, issues
    
    def _check_parameter_validation(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for parameter validation."""
        issues = []
        
        # Check if parameters are validated
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                for param_name in tool.parameters:
                    # Simple check for parameter validation
                    validation_patterns = [
                        f"if\\s+{param_name}\\s+is\\s+None",
                        f"if\\s+not\\s+{param_name}",
                        f"isinstance\\({param_name},\\s*"
                    ]
                    
                    if not any(re.search(pattern, code) for pattern in validation_patterns):
                        issues.append(f"Parameter '{param_name}' may not be properly validated")
        
        return len(issues) == 0, issues
    
    def _check_performance(self, tool: MarketplaceTool) -> Tuple[bool, List[str]]:
        """Check for performance issues."""
        issues = []
        
        # Check for potential performance issues
        if tool.implementation_type == "python":
            code = tool.implementation
            if isinstance(code, str):
                # Check for nested loops
                if re.search(r'for\s+.+:\s+.*for\s+.+:\s+.*for\s+.+:', code):
                    issues.append("Tool contains triple-nested loops which may cause performance issues")
                
                # Check for inefficient list operations
                if re.search(r'for\s+.+\s+in\s+.+:\s+.*\.append', code):
                    if "list comprehension" not in code:
                        issues.append("Tool uses inefficient list building instead of list comprehension")
        
        return len(issues) == 0, issues

class ToolMarketplace:
    """
    Marketplace for third-party tools and integrations.
    
    Provides functionality for:
    - Publishing tools to the marketplace
    - Discovering tools in the marketplace
    - Installing tools from the marketplace
    - Rating and reviewing tools
    - Managing tool versions and updates
    """
    
    def __init__(
        self,
        registry: ToolRegistry,
        execution_engine: ToolExecutionEngine,
        storage_dir: Optional[str] = None
    ):
        """
        Initialize tool marketplace.
        
        Args:
            registry: Tool registry
            execution_engine: Tool execution engine
            storage_dir: Directory for storing marketplace data
        """
        self.registry = registry
        self.execution_engine = execution_engine
        self.storage_dir = storage_dir or os.path.expanduser("~/.lumina/marketplace")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize data structures
        self.tools: Dict[str, MarketplaceTool] = {}
        self.developers: Dict[str, ToolDeveloper] = {}
        self.verifier = ToolVerifier()
        
        # Load data from storage
        self._load_data()
    
    def publish_tool(
        self,
        name: str,
        description: str,
        version: str,
        developer_id: str,
        categories: List[Union[ToolCategory, str]],
        tags: List[str],
        parameters: Dict[str, Dict[str, Any]],
        implementation_type: str,
        implementation: Any,
        documentation_url: Optional[str] = None,
        icon_url: Optional[str] = None,
        screenshots: Optional[List[str]] = None,
        pricing_model: Optional[str] = None,
        pricing_details: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        """
        Publish a tool to the marketplace.
        
        Args:
            name: Tool name
            description: Tool description
            version: Tool version
            developer_id: Developer identifier
            categories: Tool categories
            tags: Tool tags
            parameters: Tool parameters
            implementation_type: Implementation type (python, javascript, etc.)
            implementation: Tool implementation
            documentation_url: Optional documentation URL
            icon_url: Optional icon URL
            screenshots: Optional screenshot URLs
            pricing_model: Optional pricing model (free, paid, subscription)
            pricing_details: Optional pricing details
            
        Returns:
            Tuple of (tool_id, issues)
        """
        # Check if developer exists
        if developer_id not in self.developers:
            raise ValueError(f"Developer with ID {developer_id} does not exist")
        
        # Generate tool ID
        tool_id = f"{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}"
        
        # Convert string categories to enum
        enum_categories = []
        for category in categories:
            if isinstance(category, str):
                try:
                    enum_categories.append(ToolCategory(category))
                except ValueError:
                    enum_categories.append(ToolCategory.OTHER)
            else:
                enum_categories.append(category)
        
        # Create marketplace tool
        tool = MarketplaceTool(
            tool_id=tool_id,
            name=name,
            description=description,
            version=version,
            developer_id=developer_id,
            categories=enum_categories,
            tags=tags,
            parameters=parameters,
            implementation_type=implementation_type,
            implementation=implementation,
            documentation_url=documentation_url,
            icon_url=icon_url,
            screenshots=screenshots,
            pricing_model=pricing_model,
            pricing_details=pricing_details
        )
        
        # Verify tool
        passed, issues = self.verifier.verify_tool(tool)
        
        # Set verification status
        if passed:
            tool.verification_status = ToolVerificationStatus.APPROVED
        else:
            tool.verification_status = ToolVerificationStatus.PENDING
        
        # Add tool to marketplace
        self.tools[tool_id] = tool
        
        # Add tool to developer's tools
        self.developers[developer_id].tools.append(tool_id)
        
        # Save data
        self._save_data()
        
        return tool_id, issues
    
    def update_tool(
        self,
        tool_id: str,
        developer_id: str,
        **kwargs
    ) -> Tuple[bool, List[str]]:
        """
        Update a tool in the marketplace.
        
        Args:
            tool_id: Tool identifier
            developer_id: Developer identifier
            **kwargs: Tool properties to update
            
        Returns:
            Tuple of (success, issues)
        """
        # Check if tool exists
        if tool_id not in self.tools:
            return False, ["Tool does not exist"]
        
        # Check if developer owns the tool
        tool = self.tools[tool_id]
        if tool.developer_id != developer_id:
            return False, ["Developer does not own this tool"]
        
        # Update tool properties
        for key, value in kwargs.items():
            if hasattr(tool, key) and key not in ["tool_id", "developer_id", "created_at"]:
                # Handle special case for categories
                if key == "categories" and value:
                    # Convert string categories to enum
                    enum_categories = []
                    for category in value:
                        if isinstance(category, str):
                            try:
                                enum_categories.append(ToolCategory(category))
                            except ValueError:
                                enum_categories.append(ToolCategory.OTHER)
                        else:
                            enum_categories.append(category)
                    setattr(tool, key, enum_categories)
                else:
                    setattr(tool, key, value)
        
        # Update timestamp
        tool.updated_at = datetime.datetime.now()
        
        # Re-verify tool
        passed, issues = self.verifier.verify_tool(tool)
        
        # Set verification status
        if passed:
            tool.verification_status = ToolVerificationStatus.APPROVED
        else:
            tool.verification_status = ToolVerificationStatus.PENDING
        
        # Save data
        self._save_data()
        
        return True, issues
    
    def publish_tool_version(
        self,
        tool_id: str,
        developer_id: str,
        version: str,
        implementation: Any,
        **kwargs
    ) -> Tuple[bool, List[str]]:
        """
        Publish a new version of a tool.
        
        Args:
            tool_id: Tool identifier
            developer_id: Developer identifier
            version: New version
            implementation: New implementation
            **kwargs: Additional properties to update
            
        Returns:
            Tuple of (success, issues)
        """
        # Check if tool exists
        if tool_id not in self.tools:
            return False, ["Tool does not exist"]
        
        # Check if developer owns the tool
        tool = self.tools[tool_id]
        if tool.developer_id != developer_id:
            return False, ["Developer does not own this tool"]
        
        # Create a copy of the tool with the new version
        new_tool_id = f"{tool_id}-{version}"
        
        # Create new tool based on existing tool
        new_tool = MarketplaceTool(
            tool_id=new_tool_id,
            name=tool.name,
            description=tool.description,
            version=version,
            developer_id=developer_id,
            categories=tool.categories,
            tags=tool.tags,
            parameters=tool.parameters,
            implementation_type=tool.implementation_type,
            implementation=implementation,
            documentation_url=tool.documentation_url,
            icon_url=tool.icon_url,
            screenshots=tool.screenshots,
            pricing_model=tool.pricing_model,
            pricing_details=tool.pricing_details
        )
        
        # Update additional properties
        for key, value in kwargs.items():
            if hasattr(new_tool, key) and key not in ["tool_id", "developer_id", "created_at"]:
                setattr(new_tool, key, value)
        
        # Verify new tool
        passed, issues = self.verifier.verify_tool(new_tool)
        
        # Set verification status
        if passed:
            new_tool.verification_status = ToolVerificationStatus.APPROVED
        else:
            new_tool.verification_status = ToolVerificationStatus.PENDING
        
        # Add new tool to marketplace
        self.tools[new_tool_id] = new_tool
        
        # Add tool to developer's tools
        self.developers[developer_id].tools.append(new_tool_id)
        
        # Save data
        self._save_data()
        
        return True, issues
    
    def register_developer(
        self,
        name: str,
        email: str,
        organization: Optional[str] = None,
        website: Optional[str] = None
    ) -> str:
        """
        Register a new developer.
        
        Args:
            name: Developer name
            email: Developer email
            organization: Optional organization name
            website: Optional website URL
            
        Returns:
            Developer identifier
        """
        # Check if developer with this email already exists
        for developer in self.developers.values():
            if developer.email == email:
                return developer.developer_id
        
        # Generate developer ID
        developer_id = f"dev-{uuid.uuid4().hex[:8]}"
        
        # Create developer
        developer = ToolDeveloper(
            developer_id=developer_id,
            name=name,
            email=email,
            organization=organization,
            website=website
        )
        
        # Add developer to marketplace
        self.developers[developer_id] = developer
        
        # Save data
        self._save_data()
        
        return developer_id
    
    def verify_developer(self, developer_id: str) -> bool:
        """
        Verify a developer.
        
        Args:
            developer_id: Developer identifier
            
        Returns:
            Success flag
        """
        # Check if developer exists
        if developer_id not in self.developers:
            return False
        
        # Set verified flag
        self.developers[developer_id].verified = True
        
        # Save data
        self._save_data()
        
        return True
    
    def search_tools(
        self,
        query: Optional[str] = None,
        categories: Optional[List[Union[ToolCategory, str]]] = None,
        tags: Optional[List[str]] = None,
        developer_id: Optional[str] = None,
        min_rating: Optional[float] = None,
        pricing_model: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for tools in the marketplace.
        
        Args:
            query: Search query
            categories: Filter by categories
            tags: Filter by tags
            developer_id: Filter by developer
            min_rating: Filter by minimum rating
            pricing_model: Filter by pricing model
            verified_only: Only include verified tools
            limit: Maximum number of results
            offset: Result offset
            
        Returns:
            List of matching tools
        """
        # Convert string categories to enum
        enum_categories = None
        if categories:
            enum_categories = []
            for category in categories:
                if isinstance(category, str):
                    try:
                        enum_categories.append(ToolCategory(category))
                    except ValueError:
                        enum_categories.append(ToolCategory.OTHER)
                else:
                    enum_categories.append(category)
        
        # Filter tools
        results = []
        
        for tool in self.tools.values():
            # Skip tools that are not published
            if tool.publish_status != ToolPublishStatus.PUBLISHED:
                continue
            
            # Skip tools that are not verified if verified_only is True
            if verified_only and tool.verification_status != ToolVerificationStatus.APPROVED:
                continue
            
            # Filter by query
            if query and not (
                query.lower() in tool.name.lower() or
                query.lower() in tool.description.lower() or
                any(query.lower() in tag.lower() for tag in tool.tags)
            ):
                continue
            
            # Filter by categories
            if enum_categories and not any(category in tool.categories for category in enum_categories):
                continue
            
            # Filter by tags
            if tags and not any(tag.lower() in [t.lower() for t in tool.tags] for tag in tags):
                continue
            
            # Filter by developer
            if developer_id and tool.developer_id != developer_id:
                continue
            
            # Filter by rating
            if min_rating is not None and tool.average_rating < min_rating:
                continue
            
            # Filter by pricing model
            if pricing_model and tool.pricing_model != pricing_model:
                continue
            
            # Add to results
            results.append(self._format_tool_result(tool))
        
        # Sort by rating (descending)
        results.sort(key=lambda x: x["average_rating"], reverse=True)
        
        # Apply limit and offset
        return results[offset:offset+limit]
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool from the marketplace.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool details or None if not found
        """
        if tool_id not in self.tools:
            return None
        
        tool = self.tools[tool_id]
        
        # Format tool details
        return self._format_tool_result(tool, include_implementation=False)
    
    def install_tool(self, tool_id: str) -> bool:
        """
        Install a tool from the marketplace.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Success flag
        """
        # Check if tool exists
        if tool_id not in self.tools:
            return False
        
        tool = self.tools[tool_id]
        
        # Check if tool is published and verified
        if tool.publish_status != ToolPublishStatus.PUBLISHED:
            return False
        
        if tool.verification_status != ToolVerificationStatus.APPROVED:
            return False
        
        # Convert marketplace tool to registry tool
        registry_tool = ToolMetadata(
            id=tool.tool_id,
            name=tool.name,
            description=tool.description,
            version=tool.version,
            categories=[category.value for category in tool.categories],
            tags=tool.tags,
            parameters=tool.parameters,
            implementation_type=tool.implementation_type,
            implementation=tool.implementation
        )
        
        # Register tool
        self.registry.register_tool(registry_tool)
        
        # Increment download count
        tool.downloads += 1
        
        # Save data
        self._save_data()
        
        return True
    
    def rate_tool(
        self,
        tool_id: str,
        user_id: str,
        rating: int,
        review: Optional[str] = None
    ) -> bool:
        """
        Rate a tool in the marketplace.
        
        Args:
            tool_id: Tool identifier
            user_id: User identifier
            rating: Rating value (1-5)
            review: Optional review text
            
        Returns:
            Success flag
        """
        # Check if tool exists
        if tool_id not in self.tools:
            return False
        
        tool = self.tools[tool_id]
        
        # Create rating
        tool_rating = ToolRating(
            user_id=user_id,
            tool_id=tool_id,
            rating=rating,
            review=review
        )
        
        # Add rating to tool
        tool.add_rating(tool_rating)
        
        # Save data
        self._save_data()
        
        return True
    
    def get_developer(self, developer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a developer from the marketplace.
        
        Args:
            developer_id: Developer identifier
            
        Returns:
            Developer details or None if not found
        """
        if developer_id not in self.developers:
            return None
        
        developer = self.developers[developer_id]
        
        # Format developer details
        return {
            "developer_id": developer.developer_id,
            "name": developer.name,
            "organization": developer.organization,
            "website": developer.website,
            "verified": developer.verified,
            "tools": [self._format_tool_result(self.tools[tool_id], include_implementation=False)
                     for tool_id in developer.tools if tool_id in self.tools],
            "tool_count": len(developer.tools)
        }
    
    def get_categories(self) -> List[Dict[str, str]]:
        """
        Get all available categories.
        
        Returns:
            List of categories
        """
        return [{"id": category.value, "name": category.name.replace("_", " ").title()}
                for category in ToolCategory]
    
    def get_popular_tools(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular tools from the marketplace.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of popular tools
        """
        # Filter published and verified tools
        published_tools = [
            tool for tool in self.tools.values()
            if tool.publish_status == ToolPublishStatus.PUBLISHED and
               tool.verification_status == ToolVerificationStatus.APPROVED
        ]
        
        # Sort by downloads (descending)
        published_tools.sort(key=lambda x: x.downloads, reverse=True)
        
        # Format results
        return [self._format_tool_result(tool) for tool in published_tools[:limit]]
    
    def get_top_rated_tools(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top-rated tools from the marketplace.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of top-rated tools
        """
        # Filter published and verified tools with at least one rating
        rated_tools = [
            tool for tool in self.tools.values()
            if tool.publish_status == ToolPublishStatus.PUBLISHED and
               tool.verification_status == ToolVerificationStatus.APPROVED and
               len(tool.ratings) > 0
        ]
        
        # Sort by average rating (descending)
        rated_tools.sort(key=lambda x: x.average_rating, reverse=True)
        
        # Format results
        return [self._format_tool_result(tool) for tool in rated_tools[:limit]]
    
    def get_new_tools(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get new tools from the marketplace.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of new tools
        """
        # Filter published and verified tools
        published_tools = [
            tool for tool in self.tools.values()
            if tool.publish_status == ToolPublishStatus.PUBLISHED and
               tool.verification_status == ToolVerificationStatus.APPROVED
        ]
        
        # Sort by creation date (descending)
        published_tools.sort(key=lambda x: x.created_at, reverse=True)
        
        # Format results
        return [self._format_tool_result(tool) for tool in published_tools[:limit]]
    
    def _format_tool_result(
        self,
        tool: MarketplaceTool,
        include_implementation: bool = False
    ) -> Dict[str, Any]:
        """
        Format a tool for API responses.
        
        Args:
            tool: Tool to format
            include_implementation: Whether to include implementation
            
        Returns:
            Formatted tool
        """
        result = {
            "tool_id": tool.tool_id,
            "name": tool.name,
            "description": tool.description,
            "version": tool.version,
            "developer_id": tool.developer_id,
            "developer_name": self.developers[tool.developer_id].name if tool.developer_id in self.developers else "Unknown",
            "categories": [{"id": category.value, "name": category.name.replace("_", " ").title()} for category in tool.categories],
            "tags": tool.tags,
            "parameters": tool.parameters,
            "documentation_url": tool.documentation_url,
            "icon_url": tool.icon_url,
            "screenshots": tool.screenshots,
            "pricing_model": tool.pricing_model,
            "pricing_details": tool.pricing_details,
            "created_at": tool.created_at.isoformat(),
            "updated_at": tool.updated_at.isoformat(),
            "verification_status": tool.verification_status.value,
            "publish_status": tool.publish_status.value,
            "downloads": tool.downloads,
            "average_rating": tool.average_rating,
            "rating_count": len(tool.ratings)
        }
        
        # Include implementation if requested
        if include_implementation:
            result["implementation_type"] = tool.implementation_type
            result["implementation"] = tool.implementation
        
        return result
    
    def _save_data(self) -> None:
        """Save marketplace data to storage."""
        # Save tools
        tools_data = {
            tool_id: tool.to_dict()
            for tool_id, tool in self.tools.items()
        }
        
        tools_file = os.path.join(self.storage_dir, "tools.json")
        with open(tools_file, "w") as f:
            json.dump(tools_data, f, indent=2)
        
        # Save developers
        developers_data = {
            developer_id: developer.to_dict()
            for developer_id, developer in self.developers.items()
        }
        
        developers_file = os.path.join(self.storage_dir, "developers.json")
        with open(developers_file, "w") as f:
            json.dump(developers_data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load marketplace data from storage."""
        # Load tools
        tools_file = os.path.join(self.storage_dir, "tools.json")
        if os.path.exists(tools_file):
            try:
                with open(tools_file, "r") as f:
                    tools_data = json.load(f)
                
                for tool_id, tool_data in tools_data.items():
                    self.tools[tool_id] = MarketplaceTool.from_dict(tool_data)
            except Exception as e:
                logger.error(f"Error loading tools data: {e}")
        
        # Load developers
        developers_file = os.path.join(self.storage_dir, "developers.json")
        if os.path.exists(developers_file):
            try:
                with open(developers_file, "r") as f:
                    developers_data = json.load(f)
                
                for developer_id, developer_data in developers_data.items():
                    self.developers[developer_id] = ToolDeveloper.from_dict(developer_data)
            except Exception as e:
                logger.error(f"Error loading developers data: {e}")
