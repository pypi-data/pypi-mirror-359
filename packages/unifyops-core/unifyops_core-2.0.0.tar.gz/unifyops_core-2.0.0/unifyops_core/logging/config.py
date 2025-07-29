"""
Logging configuration module for UnifyOps Core.

This module provides configuration settings and utilities for the logging system.
"""

import logging
import sys
from typing import Optional

import structlog
from pythonjsonlogger import jsonlogger

from .processors import add_service_info, format_timestamp, redact_sensitive


def configure(
    service_name: str,
    service_version: str,
    environment: str,
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """
    Configure logging for a UnifyOps service.
    
    This function sets up both standard Python logging and structlog with:
    - JSON formatting for logs (when json_logs=True)
    - Service metadata injection (service name, version, environment)
    - ISO8601 timestamps with UTC timezone
    - Automatic sensitive data redaction
    - Proper processor chain for structured logging
    
    This should be called once at application startup, before any logging occurs.
    
    Args:
        service_name: Name of the service (e.g., "auth-api", "user-service").
                     This will appear in every log entry as "service".
        service_version: Version of the service (e.g., "1.0.0", "2.1.3").
                        Typically from your package version or git tag.
        environment: Environment name (e.g., "production", "staging", "development").
                    Used for filtering logs by deployment environment.
        log_level: Logging level as string. Valid values: "DEBUG", "INFO", "WARNING", 
                  "ERROR", "CRITICAL". Defaults to "INFO". Invalid values fall back to "INFO".
        json_logs: Whether to output JSON formatted logs (default: True).
                  Set to False for human-readable output during development.
    
    Raises:
        None: This function handles all errors gracefully and falls back to safe defaults.
    
    Example:
        >>> # Basic configuration
        >>> configure("my-api", "1.0.0", "production")
        
        >>> # Development configuration with human-readable logs
        >>> configure(
        ...     service_name="my-api",
        ...     service_version="1.0.0-dev",
        ...     environment="development",
        ...     log_level="DEBUG",
        ...     json_logs=False
        ... )
        
        >>> # After configuration, use structlog
        >>> import structlog
        >>> logger = structlog.get_logger()
        >>> logger.info("Service started", port=8080)
    
    Note:
        - This configures both Python's standard logging and structlog
        - Standard Python loggers will output JSON when json_logs=True
        - Service metadata is stored in contextvars and automatically added to all logs
        - Call this before creating any loggers or logging any messages
    """
    # Store service metadata in contextvars for processors
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    try:
        root_logger.setLevel(getattr(logging, log_level.upper()))
    except AttributeError:
        # Default to INFO if invalid level provided
        root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler with JSON formatter for standard loggers
    console_handler = logging.StreamHandler(sys.stdout)
    
    if json_logs:
        # Use python-json-logger for standard Python loggers
        json_formatter = jsonlogger.JsonFormatter()
        console_handler.setFormatter(json_formatter)
    else:
        # Use standard formatter for non-JSON logs
        standard_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(standard_formatter)
    
    root_logger.addHandler(console_handler)
    
    # Configure structlog
    processors = [
        # Add service info from contextvars
        add_service_info,
        # Add timestamp
        format_timestamp,
        # Redact sensitive information
        redact_sensitive,
        # Add log level
        structlog.stdlib.add_log_level,
        # Render the final event dict as JSON
        structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer(),
    ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_config() -> dict:
    """
    Get the current logging configuration including service metadata.
    
    This function retrieves the current logging context from structlog's
    contextvars, including service metadata and any additional context
    that has been bound (e.g., request_id from middleware).
    
    Returns:
        dict: A dictionary containing:
            - context: Full context dictionary with all bound variables
            - service_name: The configured service name (if set)
            - service_version: The configured service version (if set)
            - environment: The configured environment (if set)
            - error: Error message if context retrieval fails (only on error)
    
    Example:
        >>> configure("my-api", "1.0.0", "production")
        >>> config = get_config()
        >>> print(config)
        {
            "context": {
                "service_name": "my-api",
                "service_version": "1.0.0",
                "environment": "production"
            },
            "service_name": "my-api",
            "service_version": "1.0.0",
            "environment": "production"
        }
        
        >>> # With additional context
        >>> import structlog
        >>> structlog.contextvars.bind_contextvars(request_id="abc-123")
        >>> config = get_config()
        >>> print(config["context"]["request_id"])
        "abc-123"
    
    Note:
        - This is useful for debugging and verifying configuration
        - Returns gracefully with error key if context retrieval fails
        - The returned dictionary is a snapshot; changes won't affect logging
    """
    try:
        context = structlog.contextvars.get_contextvars()
        return {
            "context": context,
            "service_name": context.get("service_name"),
            "service_version": context.get("service_version"),
            "environment": context.get("environment"),
        }
    except Exception:
        return {"context": {}, "error": "Failed to retrieve context"}