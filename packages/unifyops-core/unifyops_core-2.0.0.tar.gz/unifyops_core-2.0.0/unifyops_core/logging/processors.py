"""
Logging processors module for UnifyOps Core.

This module provides log record processors for enhanced logging functionality.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

import structlog

# Define sensitive keys that should be redacted
SENSITIVE_KEYS: Set[str] = {
    # Authentication & Secrets
    "password",
    "passwd",
    "pwd",
    "token",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "auth_token",
    "secret",
    "secret_key",
    "private_key",
    "client_secret",
    
    # Personal Information
    "ssn",
    "social_security_number",
    "credit_card",
    "card_number",
    "cvv",
    "pin",
    
    # Database & Connection Strings
    "database_url",
    "db_password",
    "connection_string",
    
    # Session & Cookies
    "session_id",
    "cookie",
    "csrf_token",
    
    # Other Sensitive Data
    "authorization",
    "x-api-key",
    "x-auth-token",
}


def format_timestamp(
    logger: Optional[Any], method_name: Optional[str], event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add an ISO8601 timestamp with UTC timezone to the event dictionary.
    
    This processor adds a "timestamp" field to every log entry with the current
    time in ISO8601 format. The timestamp uses UTC timezone and replaces the
    "+00:00" suffix with "Z" for better compatibility with log aggregation systems.
    
    Args:
        logger: The logger instance (unused in this processor but required by structlog)
        method_name: The name of the method being called (unused but required by structlog)
        event_dict: The event dictionary to process. This contains all the log data.
        
    Returns:
        Dict[str, Any]: The event dictionary with added "timestamp" field in format:
                       "2024-01-01T12:00:00.123456Z"
    
    Example:
        >>> event = {"event": "user_login", "user_id": 123}
        >>> processed = format_timestamp(None, None, event)
        >>> print(processed)
        {
            "event": "user_login",
            "user_id": 123,
            "timestamp": "2024-01-01T12:00:00.123456Z"
        }
    
    Note:
        - Always uses UTC timezone for consistency across deployments
        - Microsecond precision is included
        - This processor should typically be one of the first in the chain
    """
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return event_dict


def add_service_info(
    logger: Optional[Any], method_name: Optional[str], event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add service information from structlog configuration to the event dictionary.
    
    This processor extracts service metadata (service_name, service_version, and 
    environment) from structlog's contextvars and adds them to every log entry.
    It also includes any additional context variables like request_id that may
    have been bound by middleware or application code.
    
    Args:
        logger: The logger instance (unused in this processor but required by structlog)
        method_name: The name of the method being called (unused but required by structlog)
        event_dict: The event dictionary to process. This contains all the log data.
        
    Returns:
        Dict[str, Any]: The event dictionary with added service information:
                       - service: The service name (from service_name context)
                       - service_version: The service version
                       - environment: The deployment environment
                       - Any additional context variables (e.g., request_id)
    
    Example:
        >>> # Assuming context has been set up
        >>> import structlog
        >>> structlog.contextvars.bind_contextvars(
        ...     service_name="auth-api",
        ...     service_version="1.0.0",
        ...     environment="production",
        ...     request_id="abc-123"
        ... )
        >>> event = {"event": "login_attempt", "user_id": 456}
        >>> processed = add_service_info(None, None, event)
        >>> print(processed)
        {
            "event": "login_attempt",
            "user_id": 456,
            "service": "auth-api",
            "service_version": "1.0.0",
            "environment": "production",
            "request_id": "abc-123"
        }
    
    Note:
        - Service metadata is set during configure() and stored in contextvars
        - Additional context from middleware (like request_id) is automatically included
        - If contextvars retrieval fails, the event_dict is returned unmodified
        - The "service_name" key is renamed to "service" in the output for brevity
    """
    # Try to get context from structlog contextvars
    try:
        bound_context = structlog.contextvars.get_contextvars()
        if bound_context:
            if "service_name" in bound_context:
                event_dict["service"] = bound_context["service_name"]
            if "service_version" in bound_context:
                event_dict["service_version"] = bound_context["service_version"]
            if "environment" in bound_context:
                event_dict["environment"] = bound_context["environment"]
            
            # Also add any other context (like request_id from middleware)
            for key, value in bound_context.items():
                if key not in ["service_name", "service_version", "environment"] and key not in event_dict:
                    event_dict[key] = value
    except Exception:
        # If contextvars fails, just return the event_dict as is
        pass
    
    return event_dict


def redact_sensitive(
    logger: Optional[Any], method_name: Optional[str], event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Redact sensitive information from the event dictionary.
    
    This processor searches for keys that might contain sensitive information
    (passwords, tokens, API keys, etc.) and replaces their values with "***".
    It performs case-insensitive matching and handles nested dictionaries and
    lists containing dictionaries recursively.
    
    Args:
        logger: The logger instance (unused in this processor but required by structlog)
        method_name: The name of the method being called (unused but required by structlog)
        event_dict: The event dictionary to process. This contains all the log data.
        
    Returns:
        Dict[str, Any]: A new event dictionary with sensitive values replaced by "***".
                       The original dictionary is not modified.
    
    Example:
        >>> event = {
        ...     "event": "api_call",
        ...     "username": "john",
        ...     "password": "secret123",
        ...     "api_key": "sk-1234567890",
        ...     "data": {
        ...         "token": "bearer-abc123",
        ...         "public_id": "user-456"
        ...     }
        ... }
        >>> processed = redact_sensitive(None, None, event)
        >>> print(processed)
        {
            "event": "api_call",
            "username": "john",
            "password": "***",
            "api_key": "***",
            "data": {
                "token": "***",
                "public_id": "user-456"
            }
        }
    
    Note:
        - Uses the SENSITIVE_KEYS set for matching (case-insensitive)
        - Checks both exact matches and substring matches (e.g., "my_password" matches "password")
        - Recursively processes nested dictionaries and lists
        - You can add custom keys to SENSITIVE_KEYS for domain-specific redaction
        - None values are not redacted (remain as None)
    """
    # Create a new dict to avoid modifying nested structures
    redacted_dict = {}
    
    for key, value in event_dict.items():
        # Check if the key (case-insensitive) matches any sensitive pattern
        key_lower = key.lower()
        
        # Check for exact matches or keys containing sensitive words
        is_sensitive = key_lower in SENSITIVE_KEYS or any(
            sensitive_key in key_lower for sensitive_key in SENSITIVE_KEYS
        )
        
        if is_sensitive and value is not None:
            # Redact the value
            redacted_dict[key] = "***"
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            redacted_dict[key] = _redact_dict(value)
        elif isinstance(value, list):
            # Process lists that might contain dicts
            redacted_dict[key] = [
                _redact_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Keep the value as-is
            redacted_dict[key] = value
    
    return redacted_dict


def _redact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to recursively redact sensitive data in nested dictionaries.
    
    This internal function is used by redact_sensitive() to handle nested
    dictionary structures. It applies the same redaction rules as the main
    processor but is designed to be called recursively.
    
    Args:
        d: Dictionary to process. Can contain nested dicts and lists.
        
    Returns:
        Dict[str, Any]: New dictionary with sensitive values redacted.
                       Original dictionary is not modified.
    
    Example:
        >>> nested = {
        ...     "user": {"name": "Alice", "password": "secret"},
        ...     "tokens": [{"type": "bearer", "token": "abc123"}]
        ... }
        >>> redacted = _redact_dict(nested)
        >>> print(redacted)
        {
            "user": {"name": "Alice", "password": "***"},
            "tokens": [{"type": "bearer", "token": "***"}]
        }
    
    Note:
        - This is an internal function not meant for direct use
        - Follows the same redaction rules as redact_sensitive()
        - Handles arbitrary nesting depth (limited by Python recursion limit)
    """
    redacted = {}
    
    for key, value in d.items():
        key_lower = key.lower()
        is_sensitive = key_lower in SENSITIVE_KEYS or any(
            sensitive_key in key_lower for sensitive_key in SENSITIVE_KEYS
        )
        
        if is_sensitive and value is not None:
            redacted[key] = "***"
        elif isinstance(value, dict):
            redacted[key] = _redact_dict(value)
        elif isinstance(value, list):
            redacted[key] = [
                _redact_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            redacted[key] = value
    
    return redacted