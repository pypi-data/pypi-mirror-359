"""
Log data sanitization utilities for hiding sensitive information.
"""

from typing import Any, Dict, Union
import re


def sanitize_log_data(data: Union[Dict[str, Any], list, str, Any]) -> Union[Dict[str, Any], list, str, Any]:
    """
    Recursively sanitize sensitive data from log entries.
    
    Args:
        data: The data to sanitize
        
    Returns:
        Sanitized data with sensitive fields masked
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if _is_sensitive_field(key):
                sanitized[key] = _mask_value(value)
            else:
                sanitized[key] = sanitize_log_data(value)
        return sanitized
    
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    
    elif isinstance(data, str):
        return _sanitize_string(data)
    
    else:
        return data


def _is_sensitive_field(field_name: str) -> bool:
    """Check if a field name contains sensitive information."""
    sensitive_patterns = [
        'api_key', 'password', 'token', 'secret', 'auth', 'key',
        'credential', 'private', 'confidential', 'user_id'
    ]
    
    field_lower = field_name.lower()
    return any(pattern in field_lower for pattern in sensitive_patterns)


def _mask_value(value: Any) -> str:
    """Mask a sensitive value."""
    if not value:
        return "***"
    
    value_str = str(value)
    if len(value_str) <= 4:
        return "***"
    
    # Show first 2 and last 2 characters, mask the middle
    return f"{value_str[:2]}***{value_str[-2:]}"


def _sanitize_string(text: str) -> str:
    """
    Sanitize strings that might contain sensitive data patterns.
    """
    # Pattern for API keys (common formats)
    api_key_patterns = [
        r'sk-[A-Za-z0-9\-_]{10,}',  # OpenAI style keys
        r'[A-Za-z0-9]{32,}',  # Long hex strings
        r'Bearer\s+[A-Za-z0-9\-_\.]+',  # Bearer tokens
    ]
    
    sanitized_text = text
    for pattern in api_key_patterns:
        sanitized_text = re.sub(pattern, '***REDACTED***', sanitized_text, flags=re.IGNORECASE)
    
    return sanitized_text 