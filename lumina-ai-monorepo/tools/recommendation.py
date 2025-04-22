"""
Tool Recommendation module for Lumina AI's Expanded Tool Ecosystem.

This module provides functionality for recommending tools based on context,
user preferences, and historical usage patterns.
"""

import datetime
import math
import json
import re
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import logging
from collections import Counter, defaultdict

from .registry import ToolRegistry, ToolMetadata
from .execution import ToolExecutionEngine, ToolExecutionResult
from .monitoring import ToolMonitoring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextFeature:
    """Represents a feature extracted from context for tool recommendation."""
    
    def __init__(self, name: str, value: Any, weight: float = 1.0):
        """
        Initialize context feature.
        
        Args:
            name: Feature name
            value: Feature value
            weight: Feature weight for recommendation
        """
        self.name = name
        self.value = value
        self.weight = weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feature to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "weight": self.weight
        }

class ToolRecommendationContext:
    """Context information for tool recommendation."""
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        task_description: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        current_tools: Optional[List[str]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize recommendation context.
        
        Args:
            user_id: User identifier
            task_description: Description of the current task
            input_data: Available input data
            current_tools: Currently selected tools
            user_preferences: User preferences
        """
        self.user_id = user_id
        self.task_description = task_description
        self.input_data = input_data or {}
        self.current_tools = current_tools or []
        self.user_preferences = user_preferences or {}
        self.features: Dict[str, ContextFeature] = {}
        self.timestamp = datetime.datetime.now()
    
    def add_feature(self, name: str, value: Any, weight: float = 1.0) -> None:
        """
        Add a context feature.
        
        Args:
            name: Feature name
            value: Feature value
            weight: Feature weight
        """
        self.features[name] = ContextFeature(name, value, weight)
    
    def get_feature(self, name: str) -> Optional[ContextFeature]:
        """
        Get a context feature.
        
        Args:
            name: Feature name
            
        Returns:
            Feature or None if not found
        """
        return self.features.get(name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "user_id": self.user_id,
            "task_description": self.task_description,
            "input_data": self.input_data,
            "current_tools": self.current_tools,
            "user_preferences": self.user_preferences,
            "features": {
                name: feature.to_dict()
                for name, feature in self.features.items()
            },
            "timestamp": self.timestamp.isoformat()
        }

class ToolRecommendation:
    """Recommendation for a tool."""
    
    def __init__(
        self,
        tool_id: str,
        score: float,
        reasons: List[str] = None,
        parameters: Dict[str, Any] = None
    ):
        """
        Initialize tool recommendation.
        
        Args:
            tool_id: Tool ID
            score: Recommendation score
            reasons: Reasons for recommendation
            parameters: Suggested parameter values
        """
        self.tool_id = tool_id
        self.score = score
        self.reasons = reasons or []
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "tool_id": self.tool_id,
            "score": self.score,
            "reasons": self.reasons,
            "parameters": self.parameters
        }

class CompositionRecommendation:
    """Recommendation for a tool composition."""
    
    def __init__(
        self,
        composition_id: str,
        score: float,
        reasons: List[str] = None,
        parameters: Dict[str, Any] = None
    ):
        """
        Initialize composition recommendation.
        
        Args:
            composition_id: Composition ID
            score: Recommendation score
            reasons: Reasons for recommendation
            parameters: Suggested parameter values
        """
        self.composition_id = composition_id
        self.score = score
        self.reasons = reasons or []
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "composition_id": self.composition_id,
            "score": self.score,
            "reasons": self.reasons,
            "parameters": self.parameters
        }

class ToolUsageHistory:
    """History of tool usage for a user."""
    
    def __init__(self, user_id: str):
        """
        Initialize tool usage history.
        
        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.tool_usage: Dict[str, List[datetime.datetime]] = defaultdict(list)
        self.tool_success: Dict[str, int] = Counter()
        self.tool_failure: Dict[str, int] = Counter()
        self.tool_contexts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.tool_sequences: List[List[str]] = []
        self.current_sequence: List[str] = []
    
    def record_usage(
        self,
        tool_id: str,
        success: bool,
        context: Optional[ToolRecommendationContext] = None
    ) -> None:
        """
        Record tool usage.
        
        Args:
            tool_id: Tool ID
            success: Whether usage was successful
            context: Usage context
        """
        timestamp = datetime.datetime.now()
        
        # Record usage time
        self.tool_usage[tool_id].append(timestamp)
        
        # Record success/failure
        if success:
            self.tool_success[tool_id] += 1
        else:
            self.tool_failure[tool_id] += 1
        
        # Record context
        if context:
            self.tool_contexts[tool_id].append(context.to_dict())
        
        # Update current sequence
        self.current_sequence.append(tool_id)
        
        # If sequence gets too long, start a new one
        if len(self.current_sequence) >= 10:
            self.tool_sequences.append(self.current_sequence)
            self.current_sequence = []
    
    def end_sequence(self) -> None:
        """End the current tool sequence."""
        if self.current_sequence:
            self.tool_sequences.append(self.current_sequence)
            self.current_sequence = []
    
    def get_usage_count(self, tool_id: str) -> int:
        """
        Get the number of times a tool has been used.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Usage count
        """
        return len(self.tool_usage.get(tool_id, []))
    
    def get_success_rate(self, tool_id: str) -> float:
        """
        Get the success rate for a tool.
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Success rate (0-1)
        """
        success = self.tool_success.get(tool_id, 0)
        failure = self.tool_failure.get(tool_id, 0)
        total = success + failure
        
        if total == 0:
            return 0.0
        
        return success / total
    
    def get_recent_usage(self, tool_id: str, days: int = 30) -> int:
        """
        Get the number of times a tool has been used recently.
        
        Args:
            tool_id: Tool ID
            days: Number of days to consider
            
        Returns:
            Recent usage count
        """
        if tool_id not in self.tool_usage:
            return 0
        
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        return sum(1 for timestamp in self.tool_usage[tool_id] if timestamp >= cutoff)
    
    def get_common_sequences(self, min_length: int = 2, max_sequences: int = 5) -> List[List[str]]:
        """
        Get common tool sequences.
        
        Args:
            min_length: Minimum sequence length
            max_sequences: Maximum number of sequences to return
            
        Returns:
            List of common sequences
        """
        # Extract all subsequences
        subsequences = []
        for sequence in self.tool_sequences:
            for i in range(len(sequence) - min_length + 1):
                for j in range(i + min_length, min(i + 6, len(sequence) + 1)):
                    subsequences.append(tuple(sequence[i:j]))
        
        # Count subsequences
        sequence_counts = Counter(subsequences)
        
        # Get most common
        common_sequences = sequence_counts.most_common(max_sequences)
        
        return [list(seq) for seq, count in common_sequences]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary."""
        return {
            "user_id": self.user_id,
            "tool_usage": {
                tool_id: [timestamp.isoformat() for timestamp in timestamps]
                for tool_id, timestamps in self.tool_usage.items()
            },
            "tool_success": dict(self.tool_success),
            "tool_failure": dict(self.tool_failure),
            "tool_contexts": dict(self.tool_contexts),
            "tool_sequences": self.tool_sequences,
            "current_sequence": self.current_sequence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolUsageHistory':
        """Create history from dictionary."""
        history = cls(data["user_id"])
        
        # Load tool usage
        for tool_id, timestamps in data.get("tool_usage", {}).items():
            history.tool_usage[tool_id] = [
                datetime.datetime.fromisoformat(timestamp)
                for timestamp in timestamps
            ]
        
        # Load success/failure counts
        history.tool_success = Counter(data.get("tool_success", {}))
        history.tool_failure = Counter(data.get("tool_failure", {}))
        
        # Load contexts
        history.tool_contexts = defaultdict(list)
        for tool_id, contexts in data.get("tool_contexts", {}).items():
            history.tool_contexts[tool_id] = contexts
        
        # Load sequences
        history.tool_sequences = data.get("tool_sequences", [])
        history.current_sequence = data.get("current_sequence", [])
        
        return history

class FeatureExtractor:
    """
    Extracts features from context for tool recommendation.
    
    Provides functionality for:
    - Extracting keywords from text
    - Identifying data types and formats
    - Recognizing patterns in input data
    - Extracting semantic meaning from task descriptions
    """
    
    def __init__(self):
        """Initialize feature extractor."""
        # Common keywords for different tool categories
        self.category_keywords = {
            "data_processing": [
                "process", "transform", "convert", "format", "parse", "extract",
                "filter", "sort", "group", "aggregate", "join", "merge", "split",
                "clean", "normalize", "standardize", "validate", "csv", "json",
                "xml", "excel", "database", "sql", "query", "data"
            ],
            "communication": [
                "send", "receive", "message", "email", "chat", "notify", "alert",
                "communicate", "broadcast", "publish", "subscribe", "webhook",
                "api", "http", "request", "response", "post", "get", "slack",
                "teams", "discord", "telegram", "sms", "push", "notification"
            ],
            "file_management": [
                "file", "folder", "directory", "path", "create", "read", "write",
                "delete", "copy", "move", "rename", "list", "search", "find",
                "upload", "download", "compress", "decompress", "zip", "unzip",
                "archive", "backup", "restore", "sync", "share", "permission"
            ],
            "analysis": [
                "analyze", "calculate", "compute", "statistics", "metrics",
                "measure", "evaluate", "assess", "compare", "correlate",
                "predict", "forecast", "trend", "pattern", "insight",
                "visualization", "chart", "graph", "plot", "dashboard",
                "report", "summary", "kpi", "indicator", "performance"
            ],
            "automation": [
                "automate", "schedule", "trigger", "workflow", "pipeline",
                "process", "sequence", "batch", "job", "task", "cron",
                "periodic", "recurring", "event", "condition", "rule",
                "action", "reaction", "if", "then", "when", "repeat"
            ],
            "integration": [
                "integrate", "connect", "bridge", "link", "sync", "interface",
                "api", "webhook", "callback", "event", "trigger", "subscribe",
                "publish", "push", "pull", "import", "export", "exchange",
                "transfer", "system", "service", "platform", "application"
            ],
            "security": [
                "secure", "protect", "encrypt", "decrypt", "hash", "sign",
                "verify", "authenticate", "authorize", "permission", "access",
                "control", "role", "user", "password", "token", "certificate",
                "key", "secret", "credential", "identity", "privacy", "compliance"
            ],
            "ai_ml": [
                "predict", "classify", "cluster", "recognize", "detect",
                "identify", "generate", "create", "train", "learn", "model",
                "algorithm", "feature", "label", "dataset", "neural", "deep",
                "machine", "learning", "artificial", "intelligence", "nlp",
                "vision", "speech", "language", "image", "video", "audio"
            ]
        }
    
    def extract_features(self, context: ToolRecommendationContext) -> None:
        """
        Extract features from context.
        
        Args:
            context: Recommendation context to update with features
        """
        # Extract features from task description
        if context.task_description:
            self._extract_text_features(context, context.task_description)
        
        # Extract features from input data
        if context.input_data:
            self._extract_data_features(context, context.input_data)
        
        # Extract features from user preferences
        if context.user_preferences:
            self._extract_preference_features(context, context.user_preferences)
        
        # Extract features from current tools
        if context.current_tools:
            self._extract_tool_features(context, context.current_tools)
    
    def _extract_text_features(self, context: ToolRecommendationContext, text: str) -> None:
        """
        Extract features from text.
        
        Args:
            context: Recommendation context
            text: Text to analyze
        """
        # Extract keywords
        keywords = self._extract_keywords(text)
        context.add_feature("keywords", keywords, weight=1.5)
        
        # Extract categories
        categories = self._categorize_text(text)
        context.add_feature("categories", categories, weight=2.0)
        
        # Extract entities
        entities = self._extract_entities(text)
        context.add_feature("entities", entities, weight=1.2)
        
        # Extract actions
        actions = self._extract_actions(text)
        context.add_feature("actions", actions, weight=1.8)
        
        # Extract complexity
        complexity = self._assess_complexity(text)
        context.add_feature("complexity", complexity, weight=1.0)
    
    def _extract_data_features(self, context: ToolRecommendationContext, data: Dict[str, Any]) -> None:
        """
        Extract features from input data.
        
        Args:
            context: Recommendation context
            data: Input data
        """
        # Extract data types
        data_types = self._extract_data_types(data)
        context.add_feature("data_types", data_types, weight=1.5)
        
        # Extract data formats
        data_formats = self._extract_data_formats(data)
        context.add_feature("data_formats", data_formats, weight=1.3)
        
        # Extract data size
        data_size = self._assess_data_size(data)
        context.add_feature("data_size", data_size, weight=1.0)
        
        # Extract data structure
        data_structure = self._assess_data_structure(data)
        context.add_feature("data_structure", data_structure, weight=1.2)
    
    def _extract_preference_features(self, context: ToolRecommendationContext, preferences: Dict[str, Any]) -> None:
        """
        Extract features from user preferences.
        
        Args:
            context: Recommendation context
            preferences: User preferences
        """
        # Extract preferred categories
        if "preferred_categories" in preferences:
            context.add_feature("preferred_categories", preferences["preferred_categories"], weight=1.5)
        
        # Extract preferred tools
        if "preferred_tools" in preferences:
            context.add_feature("preferred_tools", preferences["preferred_tools"], weight=1.8)
        
        # Extract avoided tools
        if "avoided_tools" in preferences:
            context.add_feature("avoided_tools", preferences["avoided_tools"], weight=2.0)
        
        # Extract expertise level
        if "expertise_level" in preferences:
            context.add_feature("expertise_level", preferences["expertise_level"], weight=1.2)
    
    def _extract_tool_features(self, context: ToolRecommendationContext, tools: List[str]) -> None:
        """
        Extract features from current tools.
        
        Args:
            context: Recommendation context
            tools: Current tools
        """
        # Add current tools as a feature
        context.add_feature("current_tools", tools, weight=1.5)
        
        # Extract tool categories
        # This would require access to the tool registry, which we don't have here
        # In a real implementation, we would look up the categories for each tool
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction based on word frequency
        # In a real implementation, this would use more sophisticated NLP techniques
        
        # Normalize text
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
            "at", "by", "for", "with", "about", "against", "between", "into",
            "through", "during", "before", "after", "above", "below", "to",
            "from", "up", "down", "in", "out", "on", "off", "over", "under",
            "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "any", "both", "each", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "s", "t", "can", "will", "just", "don",
            "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren",
            "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma",
            "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won",
            "wouldn", "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
            "you", "your", "yours", "yourself", "yourselves", "he", "him", "his",
            "himself", "she", "her", "hers", "herself", "it", "its", "itself",
            "they", "them", "their", "theirs", "themselves", "what", "which", "who",
            "whom", "this", "that", "these", "those", "am", "is", "are", "was",
            "were", "be", "been", "being", "have", "has", "had", "having", "do",
            "does", "did", "doing", "would", "should", "could", "ought", "i'm",
            "you're", "he's", "she's", "it's", "we're", "they're", "i've", "you've",
            "we've", "they've", "i'd", "you'd", "he'd", "she'd", "we'd", "they'd",
            "i'll", "you'll", "he'll", "she'll", "we'll", "they'll", "isn't",
            "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't", "doesn't",
            "don't", "didn't", "won't", "wouldn't", "shan't", "shouldn't", "can't",
            "cannot", "couldn't", "mustn't", "let's", "that's", "who's", "what's",
            "here's", "there's", "when's", "where's", "why's", "how's"
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Get most common words
        common_words = [word for word, count in word_counts.most_common(10)]
        
        return common_words
    
    def _categorize_text(self, text: str) -> Dict[str, float]:
        """
        Categorize text based on keyword matching.
        
        Args:
            text: Text to categorize
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        text = text.lower()
        categories = {}
        
        for category, keywords in self.category_keywords.items():
            # Count keyword occurrences
            count = sum(1 for keyword in keywords if keyword in text)
            
            # Calculate confidence score
            if count > 0:
                confidence = min(1.0, count / 5)  # Cap at 1.0
                categories[category] = confidence
        
        return categories
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of entities
        """
        # Simple entity extraction based on capitalization and patterns
        # In a real implementation, this would use more sophisticated NLP techniques
        
        entities = []
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            entities.extend(emails)
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls:
            entities.extend(urls)
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        if dates:
            entities.extend(dates)
        
        # Extract file paths
        file_pattern = r'\b(?:[a-zA-Z]:\\|/)[^\s:*?"<>|]+'
        files = re.findall(file_pattern, text)
        if files:
            entities.extend(files)
        
        return entities
    
    def _extract_actions(self, text: str) -> List[str]:
        """
        Extract action verbs from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of action verbs
        """
        # Simple action extraction based on common verbs
        # In a real implementation, this would use more sophisticated NLP techniques
        
        common_actions = [
            "create", "read", "update", "delete", "send", "receive", "process",
            "analyze", "calculate", "compute", "transform", "convert", "extract",
            "filter", "sort", "group", "join", "merge", "split", "clean",
            "validate", "generate", "predict", "classify", "detect", "identify",
            "search", "find", "list", "upload", "download", "connect", "integrate",
            "automate", "schedule", "trigger", "monitor", "alert", "notify"
        ]
        
        text = text.lower()
        actions = []
        
        for action in common_actions:
            if action in text:
                actions.append(action)
        
        return actions
    
    def _assess_complexity(self, text: str) -> str:
        """
        Assess the complexity of a task description.
        
        Args:
            text: Text to analyze
            
        Returns:
            Complexity level (simple, moderate, complex)
        """
        # Simple complexity assessment based on text length and sentence structure
        # In a real implementation, this would use more sophisticated NLP techniques
        
        # Count words
        word_count = len(text.split())
        
        # Count sentences
        sentence_count = len(re.split(r'[.!?]+', text))
        
        # Calculate average words per sentence
        if sentence_count > 0:
            avg_words_per_sentence = word_count / sentence_count
        else:
            avg_words_per_sentence = word_count
        
        # Assess complexity
        if word_count < 20:
            return "simple"
        elif word_count < 50 and avg_words_per_sentence < 15:
            return "moderate"
        else:
            return "complex"
    
    def _extract_data_types(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract data types from input data.
        
        Args:
            data: Input data
            
        Returns:
            Dictionary mapping field names to data types
        """
        data_types = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                data_types[key] = "string"
            elif isinstance(value, int):
                data_types[key] = "integer"
            elif isinstance(value, float):
                data_types[key] = "float"
            elif isinstance(value, bool):
                data_types[key] = "boolean"
            elif isinstance(value, list):
                data_types[key] = "array"
            elif isinstance(value, dict):
                data_types[key] = "object"
            elif value is None:
                data_types[key] = "null"
            else:
                data_types[key] = "unknown"
        
        return data_types
    
    def _extract_data_formats(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract data formats from input data.
        
        Args:
            data: Input data
            
        Returns:
            Dictionary mapping field names to data formats
        """
        data_formats = {}
        
        for key, value in data.items():
            if not isinstance(value, str):
                continue
            
            # Check for common formats
            if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', value):
                data_formats[key] = "email"
            elif re.match(r'https?://[^\s]+', value):
                data_formats[key] = "url"
            elif re.match(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', value):
                data_formats[key] = "date"
            elif re.match(r'\b\d{1,2}:\d{2}(:\d{2})?\b', value):
                data_formats[key] = "time"
            elif re.match(r'\b(?:[a-zA-Z]:\\|/)[^\s:*?"<>|]+', value):
                data_formats[key] = "file_path"
            elif re.match(r'^[A-Fa-f0-9]{6}$', value):
                data_formats[key] = "color_hex"
            elif re.match(r'^\d{3}-\d{2}-\d{4}$', value):
                data_formats[key] = "ssn"
            elif re.match(r'^\d{5}(-\d{4})?$', value):
                data_formats[key] = "zipcode"
            elif re.match(r'^\d{10}$', value) or re.match(r'^\d{3}-\d{3}-\d{4}$', value):
                data_formats[key] = "phone"
            elif re.match(r'^[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$', value):
                data_formats[key] = "uuid"
            elif re.match(r'^[A-Fa-f0-9]{40}$', value):
                data_formats[key] = "sha1"
            elif re.match(r'^[A-Fa-f0-9]{64}$', value):
                data_formats[key] = "sha256"
            elif value.startswith("{") and value.endswith("}"):
                try:
                    json.loads(value)
                    data_formats[key] = "json"
                except:
                    pass
            elif value.startswith("<") and value.endswith(">"):
                data_formats[key] = "xml"
            elif "," in value and len(value.split(",")) > 1:
                data_formats[key] = "csv"
        
        return data_formats
    
    def _assess_data_size(self, data: Dict[str, Any]) -> str:
        """
        Assess the size of input data.
        
        Args:
            data: Input data
            
        Returns:
            Size assessment (small, medium, large)
        """
        # Simple size assessment based on number of fields and data volume
        # In a real implementation, this would use more sophisticated techniques
        
        # Count fields
        field_count = len(data)
        
        # Estimate data volume
        data_volume = len(json.dumps(data))
        
        # Assess size
        if field_count < 5 and data_volume < 1000:
            return "small"
        elif field_count < 20 and data_volume < 10000:
            return "medium"
        else:
            return "large"
    
    def _assess_data_structure(self, data: Dict[str, Any]) -> str:
        """
        Assess the structure of input data.
        
        Args:
            data: Input data
            
        Returns:
            Structure assessment (flat, nested, complex)
        """
        # Simple structure assessment based on nesting level
        # In a real implementation, this would use more sophisticated techniques
        
        def get_nesting_level(obj, level=0):
            if isinstance(obj, dict):
                if not obj:
                    return level
                return max(get_nesting_level(v, level + 1) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return level
                return max(get_nesting_level(v, level + 1) for v in obj)
            else:
                return level
        
        nesting_level = get_nesting_level(data)
        
        # Assess structure
        if nesting_level <= 1:
            return "flat"
        elif nesting_level <= 3:
            return "nested"
        else:
            return "complex"

class RecommendationEngine:
    """
    Engine for recommending tools based on context.
    
    Provides functionality for:
    - Recommending individual tools
    - Recommending tool compositions
    - Explaining recommendations
    - Learning from user feedback
    """
    
    def __init__(
        self,
        registry: ToolRegistry,
        execution_engine: ToolExecutionEngine,
        monitoring: Optional[ToolMonitoring] = None
    ):
        """
        Initialize recommendation engine.
        
        Args:
            registry: Tool registry
            execution_engine: Tool execution engine
            monitoring: Tool monitoring service
        """
        self.registry = registry
        self.execution_engine = execution_engine
        self.monitoring = monitoring
        self.feature_extractor = FeatureExtractor()
        self.user_history: Dict[str, ToolUsageHistory] = {}
        self.composition_engine = None  # Will be set later
    
    def set_composition_engine(self, composition_engine: Any) -> None:
        """
        Set the composition engine.
        
        Args:
            composition_engine: Composition engine
        """
        self.composition_engine = composition_engine
    
    def recommend_tools(
        self,
        context: ToolRecommendationContext,
        max_recommendations: int = 5
    ) -> List[ToolRecommendation]:
        """
        Recommend tools based on context.
        
        Args:
            context: Recommendation context
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of tool recommendations
        """
        # Extract features from context
        self.feature_extractor.extract_features(context)
        
        # Score all tools
        tool_scores = []
        
        for tool_id, tool in self.registry.tools.items():
            score, reasons = self._score_tool(tool, context)
            
            if score > 0:
                # Get suggested parameters
                parameters = self._suggest_parameters(tool, context)
                
                # Create recommendation
                recommendation = ToolRecommendation(
                    tool_id=tool_id,
                    score=score,
                    reasons=reasons,
                    parameters=parameters
                )
                
                tool_scores.append((score, recommendation))
        
        # Sort by score (descending)
        tool_scores.sort(reverse=True)
        
        # Return top recommendations
        return [recommendation for _, recommendation in tool_scores[:max_recommendations]]
    
    def recommend_compositions(
        self,
        context: ToolRecommendationContext,
        max_recommendations: int = 3
    ) -> List[CompositionRecommendation]:
        """
        Recommend tool compositions based on context.
        
        Args:
            context: Recommendation context
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of composition recommendations
        """
        if not self.composition_engine:
            return []
        
        # Extract features from context
        self.feature_extractor.extract_features(context)
        
        # Score all compositions
        composition_scores = []
        
        for composition_id, composition in self.composition_engine.compositions.items():
            score, reasons = self._score_composition(composition, context)
            
            if score > 0:
                # Get suggested parameters
                parameters = self._suggest_composition_parameters(composition, context)
                
                # Create recommendation
                recommendation = CompositionRecommendation(
                    composition_id=composition_id,
                    score=score,
                    reasons=reasons,
                    parameters=parameters
                )
                
                composition_scores.append((score, recommendation))
        
        # Sort by score (descending)
        composition_scores.sort(reverse=True)
        
        # Return top recommendations
        return [recommendation for _, recommendation in composition_scores[:max_recommendations]]
    
    def recommend_next_tool(
        self,
        context: ToolRecommendationContext
    ) -> Optional[ToolRecommendation]:
        """
        Recommend the next tool to use based on context.
        
        Args:
            context: Recommendation context
            
        Returns:
            Tool recommendation or None
        """
        # Check if we have user history
        user_id = context.user_id
        
        if not user_id or user_id not in self.user_history:
            # Fall back to regular recommendation
            recommendations = self.recommend_tools(context, max_recommendations=1)
            return recommendations[0] if recommendations else None
        
        # Get user history
        history = self.user_history[user_id]
        
        # Get current tool sequence
        current_sequence = history.current_sequence
        
        if not current_sequence:
            # Fall back to regular recommendation
            recommendations = self.recommend_tools(context, max_recommendations=1)
            return recommendations[0] if recommendations else None
        
        # Find common next tools
        next_tools = self._find_common_next_tools(history, current_sequence)
        
        if not next_tools:
            # Fall back to regular recommendation
            recommendations = self.recommend_tools(context, max_recommendations=1)
            return recommendations[0] if recommendations else None
        
        # Get the most common next tool
        tool_id, count = next_tools[0]
        
        # Create recommendation
        tool = self.registry.get_tool(tool_id)
        
        if not tool:
            # Fall back to regular recommendation
            recommendations = self.recommend_tools(context, max_recommendations=1)
            return recommendations[0] if recommendations else None
        
        # Get suggested parameters
        parameters = self._suggest_parameters(tool, context)
        
        # Create recommendation
        recommendation = ToolRecommendation(
            tool_id=tool_id,
            score=0.9,  # High score for sequence-based recommendation
            reasons=[f"Commonly used after {', '.join(current_sequence[-3:])}"],
            parameters=parameters
        )
        
        return recommendation
    
    def record_tool_usage(
        self,
        user_id: str,
        tool_id: str,
        success: bool,
        context: Optional[ToolRecommendationContext] = None
    ) -> None:
        """
        Record tool usage for a user.
        
        Args:
            user_id: User identifier
            tool_id: Tool ID
            success: Whether usage was successful
            context: Usage context
        """
        # Get or create user history
        if user_id not in self.user_history:
            self.user_history[user_id] = ToolUsageHistory(user_id)
        
        history = self.user_history[user_id]
        
        # Record usage
        history.record_usage(tool_id, success, context)
    
    def end_tool_sequence(self, user_id: str) -> None:
        """
        End the current tool sequence for a user.
        
        Args:
            user_id: User identifier
        """
        if user_id in self.user_history:
            self.user_history[user_id].end_sequence()
    
    def _score_tool(
        self,
        tool: ToolMetadata,
        context: ToolRecommendationContext
    ) -> Tuple[float, List[str]]:
        """
        Score a tool based on context.
        
        Args:
            tool: Tool metadata
            context: Recommendation context
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []
        
        # Check if tool is in avoided tools
        avoided_tools = context.get_feature("avoided_tools")
        if avoided_tools and tool.id in avoided_tools.value:
            return 0.0, []
        
        # Check if tool is in preferred tools
        preferred_tools = context.get_feature("preferred_tools")
        if preferred_tools and tool.id in preferred_tools.value:
            score += 0.3
            reasons.append("User preferred tool")
        
        # Check categories
        categories_feature = context.get_feature("categories")
        if categories_feature:
            categories = categories_feature.value
            for category, confidence in categories.items():
                if category in tool.categories:
                    category_score = confidence * 0.2
                    score += category_score
                    if category_score > 0.1:
                        reasons.append(f"Matches {category} category")
        
        # Check keywords
        keywords_feature = context.get_feature("keywords")
        if keywords_feature:
            keywords = keywords_feature.value
            keyword_matches = []
            
            # Check against tool name
            for keyword in keywords:
                if keyword.lower() in tool.name.lower():
                    keyword_matches.append(keyword)
            
            # Check against tool description
            for keyword in keywords:
                if keyword.lower() in tool.description.lower():
                    keyword_matches.append(keyword)
            
            # Check against tool tags
            for keyword in keywords:
                if keyword.lower() in [tag.lower() for tag in tool.tags]:
                    keyword_matches.append(keyword)
            
            # Add score for keyword matches
            unique_matches = set(keyword_matches)
            if unique_matches:
                keyword_score = min(0.4, len(unique_matches) * 0.1)
                score += keyword_score
                reasons.append(f"Matches keywords: {', '.join(unique_matches)}")
        
        # Check actions
        actions_feature = context.get_feature("actions")
        if actions_feature:
            actions = actions_feature.value
            action_matches = []
            
            for action in actions:
                if action.lower() in tool.name.lower() or action.lower() in tool.description.lower():
                    action_matches.append(action)
            
            if action_matches:
                action_score = min(0.3, len(action_matches) * 0.1)
                score += action_score
                reasons.append(f"Matches actions: {', '.join(action_matches)}")
        
        # Check data types and formats
        data_types_feature = context.get_feature("data_types")
        data_formats_feature = context.get_feature("data_formats")
        
        if data_types_feature or data_formats_feature:
            # This would require more detailed tool metadata
            # In a real implementation, we would match input/output data types
            pass
        
        # Check user history if available
        user_id = context.user_id
        if user_id and user_id in self.user_history:
            history = self.user_history[user_id]
            
            # Check usage count
            usage_count = history.get_usage_count(tool.id)
            if usage_count > 0:
                usage_score = min(0.2, usage_count * 0.02)
                score += usage_score
                if usage_score > 0.05:
                    reasons.append(f"Used {usage_count} times before")
            
            # Check success rate
            success_rate = history.get_success_rate(tool.id)
            if usage_count > 3 and success_rate > 0.7:
                success_score = success_rate * 0.2
                score += success_score
                if success_score > 0.1:
                    reasons.append(f"Success rate: {success_rate:.0%}")
            
            # Check recent usage
            recent_usage = history.get_recent_usage(tool.id, days=7)
            if recent_usage > 0:
                recent_score = min(0.1, recent_usage * 0.02)
                score += recent_score
                if recent_score > 0.05:
                    reasons.append(f"Used {recent_usage} times recently")
        
        # Check monitoring data if available
        if self.monitoring:
            try:
                # Get tool metrics
                metrics = self.monitoring.get_tool_metrics(tool.id)
                
                # Check success rate
                if "success_rate" in metrics:
                    success_rate = metrics["success_rate"]["average"]
                    if success_rate is not None and success_rate > 70:
                        success_score = (success_rate - 70) / 100 * 0.2
                        score += success_score
                        if success_score > 0.05:
                            reasons.append(f"High overall success rate: {success_rate:.0f}%")
            except:
                # Ignore errors in monitoring data
                pass
        
        return score, reasons
    
    def _score_composition(
        self,
        composition: Any,
        context: ToolRecommendationContext
    ) -> Tuple[float, List[str]]:
        """
        Score a composition based on context.
        
        Args:
            composition: Tool composition
            context: Recommendation context
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []
        
        # Extract tool IDs from composition
        tool_ids = []
        for node_id, node in composition.nodes.items():
            if node.type.value == "tool" and "tool_id" in node.config:
                tool_ids.append(node.config["tool_id"])
        
        # Check categories
        categories_feature = context.get_feature("categories")
        if categories_feature:
            categories = categories_feature.value
            matched_categories = set()
            
            for tool_id in tool_ids:
                if tool_id in self.registry.tools:
                    tool = self.registry.tools[tool_id]
                    for category in tool.categories:
                        if category in categories:
                            matched_categories.add(category)
            
            if matched_categories:
                category_score = min(0.3, len(matched_categories) * 0.1)
                score += category_score
                reasons.append(f"Matches categories: {', '.join(matched_categories)}")
        
        # Check keywords
        keywords_feature = context.get_feature("keywords")
        if keywords_feature:
            keywords = keywords_feature.value
            keyword_matches = []
            
            # Check against composition name and description
            for keyword in keywords:
                if keyword.lower() in composition.name.lower() or keyword.lower() in composition.description.lower():
                    keyword_matches.append(keyword)
            
            # Add score for keyword matches
            unique_matches = set(keyword_matches)
            if unique_matches:
                keyword_score = min(0.3, len(unique_matches) * 0.1)
                score += keyword_score
                reasons.append(f"Matches keywords: {', '.join(unique_matches)}")
        
        # Check complexity
        complexity_feature = context.get_feature("complexity")
        if complexity_feature:
            complexity = complexity_feature.value
            
            # Assess composition complexity
            composition_complexity = "simple"
            if len(composition.nodes) > 5:
                composition_complexity = "moderate"
            if len(composition.nodes) > 10:
                composition_complexity = "complex"
            
            # Match complexity
            if complexity == composition_complexity:
                score += 0.2
                reasons.append(f"Matches task complexity: {complexity}")
            elif (complexity == "complex" and composition_complexity == "moderate") or (complexity == "moderate" and composition_complexity == "complex"):
                score += 0.1
                reasons.append(f"Similar to task complexity: {complexity}")
        
        # Check user history if available
        user_id = context.user_id
        if user_id and user_id in self.user_history:
            history = self.user_history[user_id]
            
            # Check for common tool sequences
            common_sequences = history.get_common_sequences()
            
            for sequence in common_sequences:
                # Check if composition contains this sequence
                if self._is_subsequence(sequence, tool_ids):
                    score += 0.2
                    reasons.append(f"Contains commonly used tool sequence")
                    break
        
        return score, reasons
    
    def _suggest_parameters(
        self,
        tool: ToolMetadata,
        context: ToolRecommendationContext
    ) -> Dict[str, Any]:
        """
        Suggest parameter values for a tool.
        
        Args:
            tool: Tool metadata
            context: Recommendation context
            
        Returns:
            Dictionary of suggested parameters
        """
        parameters = {}
        
        # Extract entities from context
        entities_feature = context.get_feature("entities")
        entities = entities_feature.value if entities_feature else []
        
        # Extract data from context
        input_data = context.input_data
        
        # Simple parameter matching based on name and type
        # In a real implementation, this would use more sophisticated techniques
        
        # This is a simplified implementation
        # In a real system, we would have more detailed parameter metadata
        
        # For now, just copy matching fields from input data
        for param_name in tool.parameters:
            if param_name in input_data:
                parameters[param_name] = input_data[param_name]
        
        # Try to match entities to parameters
        for entity in entities:
            # Email parameter
            if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', entity):
                for param_name in tool.parameters:
                    if "email" in param_name.lower() and param_name not in parameters:
                        parameters[param_name] = entity
                        break
            
            # URL parameter
            elif re.match(r'https?://[^\s]+', entity):
                for param_name in tool.parameters:
                    if any(term in param_name.lower() for term in ["url", "link", "website"]) and param_name not in parameters:
                        parameters[param_name] = entity
                        break
            
            # File path parameter
            elif re.match(r'\b(?:[a-zA-Z]:\\|/)[^\s:*?"<>|]+', entity):
                for param_name in tool.parameters:
                    if any(term in param_name.lower() for term in ["file", "path", "location"]) and param_name not in parameters:
                        parameters[param_name] = entity
                        break
        
        return parameters
    
    def _suggest_composition_parameters(
        self,
        composition: Any,
        context: ToolRecommendationContext
    ) -> Dict[str, Any]:
        """
        Suggest parameter values for a composition.
        
        Args:
            composition: Tool composition
            context: Recommendation context
            
        Returns:
            Dictionary of suggested parameters
        """
        # For compositions, we need to suggest parameters for the start node
        # This is a simplified implementation
        
        # Extract input data from context
        input_data = context.input_data
        
        # Just return the input data as parameters
        return dict(input_data)
    
    def _find_common_next_tools(
        self,
        history: ToolUsageHistory,
        current_sequence: List[str]
    ) -> List[Tuple[str, int]]:
        """
        Find tools commonly used after the current sequence.
        
        Args:
            history: Tool usage history
            current_sequence: Current tool sequence
            
        Returns:
            List of (tool_id, count) tuples
        """
        # Look for the current sequence in historical sequences
        next_tools = Counter()
        
        for sequence in history.tool_sequences:
            for i in range(len(sequence) - len(current_sequence)):
                if sequence[i:i+len(current_sequence)] == current_sequence and i+len(current_sequence) < len(sequence):
                    next_tool = sequence[i+len(current_sequence)]
                    next_tools[next_tool] += 1
        
        # Return most common next tools
        return next_tools.most_common(3)
    
    def _is_subsequence(self, subseq: List[str], seq: List[str]) -> bool:
        """
        Check if subseq is a subsequence of seq.
        
        Args:
            subseq: Subsequence to check
            seq: Main sequence
            
        Returns:
            True if subseq is a subsequence of seq
        """
        if len(subseq) > len(seq):
            return False
        
        for i in range(len(seq) - len(subseq) + 1):
            if seq[i:i+len(subseq)] == subseq:
                return True
        
        return False
