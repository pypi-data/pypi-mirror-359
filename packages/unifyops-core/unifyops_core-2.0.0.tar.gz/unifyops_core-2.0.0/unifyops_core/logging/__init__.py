"""
UnifyOps Core Logging Module

This module provides centralized structured logging functionality for UnifyOps FastAPI services,
including automatic request tracking, sensitive data redaction, and service metadata injection.
"""

import logging


def get_logger(name: str, json_format: bool = False, metadata: dict = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    This is a compatibility function that returns a standard Python logger.
    For structured logging, use structlog.get_logger() instead.
    
    Args:
        name: The name of the logger, typically __name__ for module-level loggers
        json_format: Whether to use JSON formatting (currently ignored, use configure() instead)
        metadata: Additional metadata for the logger (currently ignored)
        
    Returns:
        A standard Python logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("This is a standard Python log message")
        
    Note:
        For structured logging with all features, use:
        >>> import structlog
        >>> logger = structlog.get_logger(__name__)
    """
    # Stub implementation - returns standard logger for now
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: int, message: str, **kwargs) -> None:
    """
    Log a message with additional context.
    
    This function logs a message with additional key-value pairs as context.
    The context is passed as extra data to the logger.
    
    Args:
        logger: The logger instance to use
        level: The logging level (e.g., logging.INFO, logging.ERROR)
        message: The log message to record
        **kwargs: Additional context to log as key-value pairs
        
    Example:
        >>> logger = get_logger(__name__)
        >>> log_with_context(logger, logging.INFO, "User logged in",
        ...                  user_id=123, ip_address="192.168.1.1")
        
    Note:
        For structured logging, use structlog directly:
        >>> logger = structlog.get_logger()
        >>> logger.info("User logged in", user_id=123, ip_address="192.168.1.1")
    """
    # Stub implementation
    logger.log(level, message, extra=kwargs)


def setup_otel_for_service(
    service_name: str,
    service_version: str,
    environment: str,
    additional_resource_attributes: dict = None
) -> bool:
    """
    Setup OpenTelemetry for a service.
    
    This is a placeholder function for OpenTelemetry integration.
    The actual implementation will configure tracing, metrics, and logs
    export to an OpenTelemetry collector.
    
    Args:
        service_name: Name of the service (e.g., "user-api", "auth-service")
        service_version: Version of the service (e.g., "1.0.0", "2.1.3")
        environment: Environment name (e.g., "production", "staging", "development")
        additional_resource_attributes: Optional dict of additional attributes to add 
                                       to the OpenTelemetry resource (e.g., {"team": "backend"})
        
    Returns:
        True if setup was successful, False otherwise
        
    Example:
        >>> success = setup_otel_for_service(
        ...     service_name="user-api",
        ...     service_version="1.2.0",
        ...     environment="production",
        ...     additional_resource_attributes={"team": "platform", "region": "us-east-1"}
        ... )
        
    Note:
        This is currently a stub implementation for future OpenTelemetry integration.
        Returns True to indicate readiness for future implementation.
    """
    # Stub implementation
    return True


def add_logging_metadata(**kwargs) -> None:
    """
    Add metadata to the logging context.
    
    This function adds key-value pairs to the current logging context using
    structlog's contextvars. The metadata will be included in all subsequent
    log messages within the same execution context.
    
    Args:
        **kwargs: Metadata key-value pairs to add to the logging context.
                 Common examples include user_id, tenant_id, request_id, etc.
    
    Example:
        >>> add_logging_metadata(user_id=123, tenant="acme-corp")
        >>> logger.info("Processing request")  # Will include user_id and tenant
        
        >>> # In a web request handler:
        >>> add_logging_metadata(
        ...     user_id=current_user.id,
        ...     ip_address=request.client.host,
        ...     user_agent=request.headers.get("User-Agent")
        ... )
        
    Note:
        - Metadata is scoped to the current execution context (e.g., async task, thread)
        - Use structlog.contextvars.clear_contextvars() to clear all metadata
        - For production use, this is a stub. Use structlog.contextvars.bind_contextvars()
          directly for full functionality
    """
    # Stub implementation
    pass


from .config import configure, get_config
from .processors import add_service_info, format_timestamp, redact_sensitive
from .middleware import LoggingContextMiddleware, configure_logging_middleware

__all__ = [
    "get_logger", 
    "log_with_context", 
    "setup_otel_for_service", 
    "add_logging_metadata",
    "format_timestamp",
    "add_service_info",
    "redact_sensitive",
    "configure",
    "get_config",
    "LoggingContextMiddleware",
    "configure_logging_middleware",
]