"""
Unit tests for the Veritax Analytics SDK exceptions.

Tests the exception hierarchy and specific exception functionality.
"""

import pytest
from veritax_analytics.exceptions import (
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


def test_base_exception():
    """Test base VeritaxAnalyticsError functionality"""
    # Basic exception
    error = VeritaxAnalyticsError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.details == {}
    
    # Exception with details
    details = {"code": 500, "endpoint": "/api/test"}
    error_with_details = VeritaxAnalyticsError("Test error", details)
    assert error_with_details.details == details
    assert "Details: " in str(error_with_details)


def test_exception_hierarchy():
    """Test that exceptions inherit correctly"""
    # Test inheritance chain
    config_error = ConfigurationError("Config issue")
    assert isinstance(config_error, VeritaxAnalyticsError)
    
    # Test transport error chain
    connection_error = ConnectionError("Connection failed")
    assert isinstance(connection_error, TransportError)
    assert isinstance(connection_error, VeritaxAnalyticsError)
    
    # Test auth error
    auth_error = AuthenticationError("Invalid API key")
    assert isinstance(auth_error, TransportError)
    assert isinstance(auth_error, VeritaxAnalyticsError)


def test_rate_limit_error():
    """Test RateLimitError with retry_after parameter"""
    # Without retry_after
    error = RateLimitError("Rate limit exceeded")
    assert error.retry_after is None
    
    # With retry_after
    error_with_retry = RateLimitError("Rate limit exceeded", retry_after=60)
    assert error_with_retry.retry_after == 60


def test_batch_error():
    """Test BatchError with failed events"""
    # Without failed events
    error = BatchError("Batch failed")
    assert error.failed_events == []
    
    # With failed events
    failed_events = [{"event_id": "1"}, {"event_id": "2"}]
    error_with_events = BatchError("Batch failed", failed_events=failed_events)
    assert error_with_events.failed_events == failed_events


def test_timeout_error():
    """Test TimeoutError with timeout duration"""
    # Without timeout duration
    error = TimeoutError("Operation timed out")
    assert error.timeout_duration is None
    
    # With timeout duration
    error_with_duration = TimeoutError("Operation timed out", timeout_duration=30.0)
    assert error_with_duration.timeout_duration == 30.0


def test_retry_exhausted_error():
    """Test RetryExhaustedError with attempt count and last error"""
    original_error = ValueError("Original failure")
    error = RetryExhaustedError("Retries exhausted", attempt_count=3, last_error=original_error)
    
    assert error.attempt_count == 3
    assert error.last_error == original_error


def test_server_error():
    """Test ServerError with status code"""
    error = ServerError("Internal server error", status_code=500)
    assert error.status_code == 500


def test_client_error():
    """Test ClientError with status code"""
    error = ClientError("Bad request", status_code=400)
    assert error.status_code == 400


def test_exception_catching():
    """Test that exceptions can be caught properly"""
    # Test catching specific exceptions
    try:
        raise AuthenticationError("Invalid credentials")
    except AuthenticationError as e:
        assert "Invalid credentials" in str(e)
    except Exception:
        pytest.fail("Should have caught AuthenticationError specifically")
    
    # Test catching base exception
    try:
        raise ValidationError("Invalid data")
    except VeritaxAnalyticsError as e:
        assert "Invalid data" in str(e)
    except Exception:
        pytest.fail("Should have caught VeritaxAnalyticsError base class")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
