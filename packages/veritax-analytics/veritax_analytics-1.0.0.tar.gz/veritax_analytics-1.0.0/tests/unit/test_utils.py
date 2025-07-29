"""
Unit tests for the Veritax Analytics SDK utilities.

Tests validation, sanitization, retry logic, and other utility functions.
"""

import logging
import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from veritax_analytics.utils import (
    validate_api_key,
    validate_endpoint_url,
    sanitize_metadata,
    validate_event_data,
    safe_json_serialize,
    calculate_batch_size,
    is_retryable_error,
    exponential_backoff_retry,
    setup_logging
)
from veritax_analytics.exceptions import (
    ValidationError,
    AuthenticationError,
    ServerError,
    RetryExhaustedError
)


class TestValidation:
    """Test validation functions"""
    
    def test_validate_api_key_success(self):
        """Test successful API key validation"""
        # Valid key
        result = validate_api_key("test-api-key-123")
        assert result == "test-api-key-123"
        
        # Key with whitespace
        result = validate_api_key("  test-api-key-123  ")
        assert result == "test-api-key-123"
    
    def test_validate_api_key_failures(self):
        """Test API key validation failures"""
        # Empty key
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            validate_api_key("")
        
        # Too short
        with pytest.raises(ValidationError, match="at least 10 characters"):
            validate_api_key("short")
        
        # Invalid characters
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_api_key("test key with spaces!")
    
    def test_validate_endpoint_url_success(self):
        """Test successful URL validation"""
        # Full HTTPS URL
        result = validate_endpoint_url("https://api.example.com")
        assert result == "https://api.example.com"
        
        # Auto-add HTTPS
        result = validate_endpoint_url("api.example.com")
        assert result == "https://api.example.com"
    
    def test_validate_endpoint_url_failures(self):
        """Test URL validation failures"""
        # Empty URL
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            validate_endpoint_url("")
        
        # Invalid URL
        with pytest.raises(ValidationError, match="missing hostname"):
            validate_endpoint_url("https://")


class TestSanitization:
    """Test data sanitization functions"""
    
    def test_sanitize_metadata_basic(self):
        """Test basic metadata sanitization"""
        metadata = {
            "valid_key": "valid_value",
            "number": 42,
            "boolean": True,
            "float": 3.14
        }
        result = sanitize_metadata(metadata)
        assert result == metadata
    
    def test_sanitize_metadata_filtering(self):
        """Test metadata filtering and cleaning"""
        metadata = {
            "valid_key": "valid_value",
            "control_chars": "text\x00with\nbad\r\nchars",
            "too_long": "x" * 1100,  # Over max_size
            "invalid_key_" + "x" * 100: "should_be_skipped",  # Key too long
            123: "numeric_key_converted",  # Non-string key
            "complex": {"nested": "data"},
            "list_data": [1, 2, 3]
        }
        
        result = sanitize_metadata(metadata)
        
        # Valid data preserved
        assert result["valid_key"] == "valid_value"
        
        # Control characters removed
        assert result["control_chars"] == "textwithbadchars"
        
        # Long strings truncated
        assert len(result["too_long"]) == 1000
        
        # Complex objects converted to strings
        assert isinstance(result["complex"], str)
        assert isinstance(result["list_data"], str)
        
        # Invalid keys skipped
        assert len([k for k in result.keys() if "invalid_key" in str(k)]) == 0
    
    def test_sanitize_metadata_invalid_input(self):
        """Test metadata sanitization with invalid input"""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            sanitize_metadata("not_a_dict")


class TestEventValidation:
    """Test event data validation"""
    
    def test_validate_event_data_success(self):
        """Test successful event validation"""
        event_data = {
            "event_type": "tool_execution",
            "server_id": "test-server",
            "additional_field": "value"
        }
        result = validate_event_data(event_data)
        assert result == event_data
    
    def test_validate_event_data_failures(self):
        """Test event validation failures"""
        # Missing required fields
        with pytest.raises(ValidationError, match="Missing required field"):
            validate_event_data({"event_type": "tool_execution"})
        
        # Invalid event type
        with pytest.raises(ValidationError, match="Invalid event_type"):
            validate_event_data({
                "event_type": "invalid_type",
                "server_id": "test-server"
            })
        
        # Invalid server_id
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            validate_event_data({
                "event_type": "tool_execution",
                "server_id": ""
            })


class TestUtilityFunctions:
    """Test utility helper functions"""
    
    def test_safe_json_serialize(self):
        """Test JSON serialization safety"""
        # Basic types
        assert safe_json_serialize("string") == "string"
        assert safe_json_serialize(42) == 42
        assert safe_json_serialize(True) is True
        assert safe_json_serialize(None) is None
        
        # Complex objects
        data = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        result = safe_json_serialize(data)
        assert isinstance(result, dict)
        assert result["string"] == "value"
        assert result["list"] == [1, 2, 3]
        
        # Custom objects become strings
        class CustomObject:
            def __str__(self):
                return "custom_object"
        
        result = safe_json_serialize(CustomObject())
        assert result == "custom_object"
    
    def test_calculate_batch_size(self):
        """Test batch size calculations"""
        # Small batch
        assert calculate_batch_size(50, 1000) == [50]
        
        # Exact multiple
        assert calculate_batch_size(2000, 1000) == [1000, 1000]
        
        # With remainder
        assert calculate_batch_size(2500, 1000) == [1000, 1000, 500]

        assert calculate_batch_size(3600, 1000) == [1000, 1000, 1000, 600]

        
        # Zero events
        assert calculate_batch_size(0, 1000) == []
    
    def test_is_retryable_error(self):
        """Test error retry logic"""
        # Retryable errors
        assert is_retryable_error(ServerError("Server error", status_code=500)) is True
        
        # Non-retryable errors
        assert is_retryable_error(AuthenticationError("Auth failed")) is False
        
        # Unknown errors default to retryable
        assert is_retryable_error(Exception("Unknown error")) is True


class TestRetryLogic:
    """Test exponential backoff retry logic"""
    
    def test_retry_success_sync(self):
        """Test successful retry on sync function"""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=2, base_delay=1)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 2
    
    def test_retry_exhausted_sync(self):
        """Test retry exhaustion on sync function"""
        @exponential_backoff_retry(max_retries=1, base_delay=2)
        def always_fail():
            raise ValueError("Always fails")
        
        with pytest.raises(RetryExhaustedError):
            always_fail()
    
    @pytest.mark.asyncio
    async def test_retry_success_async(self):
        """Test successful retry on async function"""
        call_count = 0

        @exponential_backoff_retry(max_retries=2, base_delay=1)
        async def async_flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "async_success"
        
        result = await async_flaky_function()
        assert result == "async_success"
        assert call_count == 2


class TestLogging:
    """Test logging setup"""
    
    def test_setup_logging(self):
        """Test logging configuration"""
        logger = setup_logging(logging.DEBUG)
        assert logger.level == 10 
        assert len(logger.handlers) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
