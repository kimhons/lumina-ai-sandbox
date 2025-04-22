"""
Utility functions for Lumina AI.

This module provides utility functions that are used across
different components of the Lumina AI system.
"""

import time
import uuid
import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

def timestamp() -> int:
    """
    Get the current timestamp in milliseconds.
    
    Returns:
        The current timestamp in milliseconds
    """
    return int(time.time() * 1000)

def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique ID string
    """
    return f"{prefix}{uuid.uuid4().hex}"

def count_tokens(text: str) -> int:
    """
    Count the approximate number of tokens in a text.
    
    This is a simple approximation that assumes 4 characters per token
    on average. For accurate token counting, use provider-specific
    tokenizers.
    
    Args:
        text: The text to count tokens for
        
    Returns:
        The approximate number of tokens
    """
    return len(text) // 4 + 1

def format_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception as a dictionary.
    
    Args:
        error: The exception to format
        
    Returns:
        A dictionary containing error information
    """
    return {
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "timestamp": timestamp()
    }

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: The maximum length
        
    Returns:
        The truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text.
    
    Args:
        text: The text to extract JSON from
        
    Returns:
        The extracted JSON as a dictionary, or None if no JSON was found
    """
    import json
    
    # Find JSON-like patterns
    json_pattern = r'(\{.*\}|\[.*\])'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries.
    
    Args:
        dict1: The first dictionary
        dict2: The second dictionary
        
    Returns:
        The merged dictionary
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def safe_get(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Safely get a value from a nested dictionary.
    
    Args:
        obj: The dictionary to get the value from
        path: The path to the value, using dot notation
        default: The default value to return if the path doesn't exist
        
    Returns:
        The value at the path, or the default value if the path doesn't exist
    """
    keys = path.split('.')
    result = obj
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    
    return result
