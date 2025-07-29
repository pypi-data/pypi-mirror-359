"""
Custom exceptions for the Veritax Analytics SDK.

This module provides a hierarchical exception structure for handling errors
that may occur during the operation of the SDK.
It includes specific exceptions for configuration issues, transport errors,
validation errors, and more, allowing for granular error handling and reporting.

Most of these errors should not stop the tool execution and are just raised for debugging purposes.
"""

from typing import Optional, Dict, Any


class VeritaxAnalyticsError(Exception):
    """
    Base exception for all Veritax Analytics SDK errors.
    
    This is the root of our exception hierarchy, allowing users to catch
    all SDK-related errors with a single except clause.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ConfigurationError(VeritaxAnalyticsError):
    """
    Raised when there are issues with SDK configuration.
    
    Examples:
    - Invalid API key format
    - Missing required configuration
    - Invalid endpoint URLs
    """
    pass


class TransportError(VeritaxAnalyticsError):
    """
    Base class for all transport-related errors.
    
    This covers network connectivity, HTTP transport issues,
    and communication failures with the analytics backend.
    """
    pass


class ConnectionError(TransportError):
    """
    Raised when unable to establish connection to the analytics endpoint.
    
    Examples:
    - Network unreachable
    - DNS resolution failure
    - Connection timeout
    """
    pass


class AuthenticationError(TransportError):
    """
    Raised when authentication fails with the analytics backend.
    
    Examples:
    - Invalid API key
    - Expired credentials
    - Missing authorization header
    """
    pass


class RateLimitError(TransportError):
    """
    Raised when hitting rate limits on the analytics endpoint.
    
    Includes retry-after information when available.
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.retry_after = retry_after


class ValidationError(VeritaxAnalyticsError):
    """
    Raised when event data fails validation.
    
    Examples:
    - Invalid event structure
    - Missing required fields
    - Data type mismatches
    """
    pass


class BatchError(VeritaxAnalyticsError):
    """
    Raised when batch processing encounters errors.
    
    Examples:
    - Batch size exceeded
    - Partial batch failures
    - Batch timeout
    """
    
    def __init__(self, message: str, failed_events: Optional[list] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.failed_events = failed_events or []


class TimeoutError(TransportError):
    """
    Raised when operations exceed configured timeout limits.
    
    Examples:
    - HTTP request timeout
    - Batch flush timeout
    - Connection establishment timeout
    """
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.timeout_duration = timeout_duration


class RetryExhaustedError(TransportError):
    """
    Raised when retry attempts are exhausted.
    
    Contains information about all failed attempts.

    This is a critical error indicating that the operation could not be completed. Not sure yet how to handle this.
    --todo @mark explore more
    """
    
    def __init__(self, message: str, attempt_count: int, last_error: Optional[Exception] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.attempt_count = attempt_count
        self.last_error = last_error


class ServerError(TransportError):
    """
    Raised when the analytics backend returns server errors (5xx).
    
    Examples:
    - Internal server error
    - Service unavailable
    - Gateway timeout

    This should not affect the tool execution anyways , and can be retried.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.status_code = status_code


class ClientError(TransportError):
    """
    Raised when requests are rejected due to client errors (4xx).
    
    Examples:
    - Bad request format
    - Unauthorized access
    - Resource not found
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.status_code = status_code
