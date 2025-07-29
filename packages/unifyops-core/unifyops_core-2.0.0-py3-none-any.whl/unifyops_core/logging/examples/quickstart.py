#!/usr/bin/env python3
"""
UnifyOps Logging Quick Start Example

This example demonstrates how to set up and use the UnifyOps logging system
in under 5 minutes. It covers basic configuration, structured logging,
and FastAPI integration.

Run this example:
    python quickstart.py
"""

import asyncio
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# Import UnifyOps logging components
from unifyops_core.logging import configure, get_logger
from unifyops_core.logging.middleware import configure_logging_middleware
from unifyops_core.logging.processors import SENSITIVE_KEYS


def basic_logging_example():
    """Example 1: Basic logging configuration and usage."""
    print("\n=== Example 1: Basic Logging ===")
    
    # Configure logging for your service
    configure(
        service_name="quickstart-demo",
        service_version="1.0.0",
        environment="development",
        log_level="INFO"
    )
    
    # Get a logger
    logger = structlog.get_logger(__name__)
    
    # Log some messages
    logger.info("Service started")
    logger.info("Processing user request", user_id=123, action="login")
    logger.warning("Rate limit approaching", current=85, limit=100)
    logger.error("Database connection failed", retry_count=3, error="timeout")


def structured_logging_example():
    """Example 2: Structured logging with context."""
    print("\n=== Example 2: Structured Logging with Context ===")
    
    # Configure with JSON output
    configure(
        service_name="user-service",
        service_version="2.0.0",
        environment="staging",
        json_logs=True  # JSON format for production
    )
    
    logger = structlog.get_logger()
    
    # Add persistent context for this execution
    structlog.contextvars.bind_contextvars(
        tenant_id="acme-corp",
        region="us-east-1"
    )
    
    # All logs will include tenant_id and region
    logger.info("Processing order", order_id=456)
    logger.info("Order completed", order_id=456, total=99.99)
    
    # Clear context when done
    structlog.contextvars.clear_contextvars()


def sensitive_data_example():
    """Example 3: Automatic sensitive data redaction."""
    print("\n=== Example 3: Sensitive Data Redaction ===")
    
    configure("security-demo", "1.0.0", "dev")
    logger = structlog.get_logger()
    
    # Sensitive data is automatically redacted
    logger.info("User authentication", 
                username="john.doe",
                password="super-secret-123",  # Will be redacted
                api_key="sk_live_abcd1234")    # Will be redacted
    
    # Add custom sensitive keys
    SENSITIVE_KEYS.add("credit_card")
    SENSITIVE_KEYS.add("ssn")
    
    logger.info("Payment processed",
                user_id=789,
                credit_card="4111-1111-1111-1111",  # Will be redacted
                amount=150.00)


def fastapi_integration_example():
    """Example 4: FastAPI integration with request tracking."""
    print("\n=== Example 4: FastAPI Integration ===")
    
    # Configure logging
    configure("api-demo", "1.0.0", "production")
    
    # Create FastAPI app
    app = FastAPI(title="QuickStart API")
    
    # Add logging middleware for request tracking
    configure_logging_middleware(app)
    
    # Define some routes
    @app.get("/")
    async def root():
        logger = structlog.get_logger()
        logger.info("Root endpoint accessed")
        return {"message": "Hello World"}
    
    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        logger = structlog.get_logger()
        logger.info("Fetching user", user_id=user_id)
        
        if user_id == 999:
            logger.error("User not found", user_id=user_id)
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("User fetched successfully", user_id=user_id)
        return {"user_id": user_id, "name": f"User {user_id}"}
    
    # Test the API
    client = TestClient(app)
    
    # Make requests
    print("\nMaking API requests...")
    response1 = client.get("/")
    print(f"GET / - Status: {response1.status_code}")
    print(f"Request ID: {response1.headers.get('X-Request-ID')}")
    
    response2 = client.get("/users/123")
    print(f"\nGET /users/123 - Status: {response2.status_code}")
    print(f"Request ID: {response2.headers.get('X-Request-ID')}")
    
    response3 = client.get("/users/999")
    print(f"\nGET /users/999 - Status: {response3.status_code}")
    print(f"Request ID: {response3.headers.get('X-Request-ID')}")


def error_handling_example():
    """Example 5: Error handling and exception logging."""
    print("\n=== Example 5: Error Handling ===")
    
    configure("error-demo", "1.0.0", "dev", log_level="DEBUG")
    logger = structlog.get_logger()
    
    def risky_operation(value: int):
        logger.debug("Starting risky operation", value=value)
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2
    
    # Success case
    try:
        result = risky_operation(5)
        logger.info("Operation successful", result=result)
    except Exception as e:
        logger.exception("Operation failed")
    
    # Failure case
    try:
        result = risky_operation(-1)
    except Exception as e:
        logger.exception("Operation failed with negative value")


async def async_context_example():
    """Example 6: Async context isolation."""
    print("\n=== Example 6: Async Context Isolation ===")
    
    configure("async-demo", "1.0.0", "dev")
    logger = structlog.get_logger()
    
    async def process_task(task_id: str):
        # Each async task has its own context
        structlog.contextvars.bind_contextvars(task_id=task_id)
        logger.info("Task started")
        await asyncio.sleep(0.1)  # Simulate work
        logger.info("Task completed")
        structlog.contextvars.clear_contextvars()
    
    # Run multiple tasks concurrently
    await asyncio.gather(
        process_task("task-1"),
        process_task("task-2"),
        process_task("task-3")
    )


def main():
    """Run all examples."""
    print("UnifyOps Logging Quick Start Examples")
    print("=" * 40)
    
    # Run synchronous examples
    basic_logging_example()
    structured_logging_example()
    sensitive_data_example()
    fastapi_integration_example()
    error_handling_example()
    
    # Run async example
    print("\nRunning async example...")
    asyncio.run(async_context_example())
    
    print("\n" + "=" * 40)
    print("Quick start complete! Check the log output above.")
    print("\nNext steps:")
    print("1. Try modifying the examples above")
    print("2. Read the full documentation in logging/README.md")
    print("3. Integrate into your own service")


if __name__ == "__main__":
    main()