"""
Veritax Analytics SDK - Cloud-agnostic analytics for MCP servers
"""

from .models import (
    AnalyticsEvent, 
    ToolExecutionEvent, 
    ServerHealthEvent, 
    Configuration,
    BatchRequest,
    BatchResponse,
    APIResponse,
    HealthCheckResponse
)
from .transport import Transport, HTTPTransport, AsyncHTTPTransport
from .trace_manager import configure_trace_manager, get_trace_manager
from .trace import trace
from .exceptions import (
    VeritaxAnalyticsError,
    ConfigurationError,
    TransportError,
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    BatchError,
    TimeoutError,
    RetryExhaustedError,
    ServerError,
    ClientError
)

__version__ = "1.0.0"
__all__ = [
    # Core models
    "AnalyticsEvent", 
    "ToolExecutionEvent", 
    "ServerHealthEvent", 
    "Configuration",
    "BatchRequest",
    "BatchResponse", 
    "APIResponse",
    "HealthCheckResponse",
    
    # Transport layer
    "Transport",
    "HTTPTransport",
    "AsyncHTTPTransport",
    
    # Tracing
    "configure_trace_manager",
    "get_trace_manager", 
    "trace",
    
    # Exceptions
    "VeritaxAnalyticsError",
    "ConfigurationError", 
    "TransportError",
    "ConnectionError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "BatchError",
    "TimeoutError",
    "RetryExhaustedError",
    "ServerError",
    "ClientError"
]
