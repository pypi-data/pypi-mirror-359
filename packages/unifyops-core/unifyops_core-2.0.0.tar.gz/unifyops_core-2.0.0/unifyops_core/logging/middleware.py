"""
FastAPI middleware for logging context enrichment.

This module provides middleware to extract or generate request IDs and bind them
to the structlog context for each request.
"""

import uuid
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enriches logging context with request information.
    
    This middleware automatically adds request-specific context to all logs
    generated during request processing. It's essential for distributed tracing
    and debugging in microservice architectures.
    
    Features:
    - Extracts X-Request-ID header or generates a new UUID if not present
    - Binds the request ID to structlog context for all logs in the request
    - Optionally adds request path, HTTP method, and client information
    - Automatically clears context after request completion
    - Adds request ID to response headers for client correlation
    
    The middleware ensures that every log entry during a request includes
    consistent request identification, making it easy to trace all logs
    for a specific request across services.
    
    Example:
        >>> app = FastAPI()
        >>> app.add_middleware(
        ...     LoggingContextMiddleware,
        ...     request_id_header="X-Trace-ID",
        ...     include_path=True
        ... )
    """
    
    def __init__(
        self, 
        app, 
        request_id_header: str = "X-Request-ID",
        include_path: bool = True,
        include_method: bool = True,
        include_client: bool = True,
    ):
        """
        Initialize the middleware with configuration options.
        
        Args:
            app: The FastAPI/Starlette application instance to wrap
            request_id_header: Name of the header to extract/set request ID.
                             Common values: "X-Request-ID", "X-Trace-ID", 
                             "X-Correlation-ID". Defaults to "X-Request-ID".
            include_path: Whether to include request path in logging context.
                         Useful for filtering logs by endpoint. Defaults to True.
            include_method: Whether to include HTTP method (GET, POST, etc.) 
                          in logging context. Defaults to True.
            include_client: Whether to include client IP and port in logging 
                          context. Useful for security and debugging. Defaults to True.
        
        Note:
            Including more context fields provides better debugging capabilities
            but increases log size. Adjust based on your needs.
        """
        super().__init__(app)
        self.request_id_header = request_id_header
        self.include_path = include_path
        self.include_method = include_method
        self.include_client = include_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request, adding context before calling the next handler.
        
        This method is called for every HTTP request. It:
        1. Extracts or generates a request ID
        2. Binds request context to structlog for the duration of the request
        3. Calls the next handler (middleware or route)
        4. Adds the request ID to response headers
        5. Clears the context to prevent context leakage
        
        Args:
            request: The incoming HTTP request object containing headers, path, etc.
            call_next: Callable that invokes the next middleware or route handler
            
        Returns:
            Response: The HTTP response from the application, with X-Request-ID header added
            
        Raises:
            Any exception from the application is re-raised after clearing context
        
        Example Context Added:
            {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "path": "/api/users/123",
                "method": "GET",
                "client_ip": "192.168.1.100",
                "client_port": 54321
            }
        """
        # Extract or generate request ID
        request_id = request.headers.get(self.request_id_header)
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Build context dictionary
        context = {"request_id": request_id}
        
        if self.include_path:
            context["path"] = request.url.path
        
        if self.include_method:
            context["method"] = request.method
        
        if self.include_client and request.client:
            context["client_ip"] = request.client.host
            context["client_port"] = request.client.port
        
        # Bind context to structlog for this request
        structlog.contextvars.bind_contextvars(**context)
        
        try:
            # Call the next handler
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers[self.request_id_header] = request_id
            
            return response
        finally:
            # Clear the context after the request
            structlog.contextvars.clear_contextvars()


def configure_logging_middleware(
    app,
    request_id_header: str = "X-Request-ID",
    include_path: bool = True,
    include_method: bool = True,
    include_client: bool = True,
) -> None:
    """
    Convenience function to add logging middleware to a FastAPI app.
    
    This is the recommended way to add the LoggingContextMiddleware to your
    FastAPI application. It configures the middleware with sensible defaults
    while allowing customization of key behaviors.
    
    Args:
        app: The FastAPI application instance to configure
        request_id_header: Name of the header to use for request tracking.
                         Common values: "X-Request-ID" (default), "X-Trace-ID",
                         "X-Correlation-ID". This header will be extracted from
                         incoming requests and added to outgoing responses.
        include_path: Whether to include the request path (e.g., "/api/users/123")
                     in the logging context. Useful for filtering logs by endpoint.
                     Defaults to True.
        include_method: Whether to include the HTTP method (GET, POST, PUT, etc.)
                       in the logging context. Helpful for debugging RESTful APIs.
                       Defaults to True.
        include_client: Whether to include client IP address and port in the logging
                       context. Important for security auditing and geographic debugging.
                       Defaults to True.
        
    Example:
        >>> from fastapi import FastAPI
        >>> from unifyops_core.logging import configure
        >>> from unifyops_core.logging.middleware import configure_logging_middleware
        >>> 
        >>> # Create and configure app
        >>> app = FastAPI(title="My API")
        >>> 
        >>> # Configure logging first
        >>> configure("my-api", "1.0.0", "production")
        >>> 
        >>> # Then add middleware
        >>> configure_logging_middleware(app)
        >>> 
        >>> # Or with custom configuration
        >>> configure_logging_middleware(
        ...     app,
        ...     request_id_header="X-Trace-ID",
        ...     include_client=False  # Don't log client IPs for privacy
        ... )
        
    Note:
        - Call this after creating your FastAPI app but before defining routes
        - The middleware will be added to the app's middleware stack
        - All logs during request processing will include the configured context
    """
    app.add_middleware(
        LoggingContextMiddleware,
        request_id_header=request_id_header,
        include_path=include_path,
        include_method=include_method,
        include_client=include_client,
    )