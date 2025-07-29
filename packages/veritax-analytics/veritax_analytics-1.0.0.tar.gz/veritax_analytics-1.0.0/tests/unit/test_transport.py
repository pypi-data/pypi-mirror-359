"""
Unit tests for the Veritax Analytics SDK transport layer.

Tests HTTP transport functionality, error handling, retry logic, and batch processing.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

from veritax_analytics.transport import HTTPTransport, AsyncHTTPTransport
from veritax_analytics.models import BatchRequest, ToolExecutionEvent, BatchResponse
from veritax_analytics.exceptions import (
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    RetryExhaustedError,
    ValidationError,
    ServerError,
    ClientError,
    TimeoutError
)


class TestHTTPTransport:
    """Test HTTP transport functionality"""
    
    def setup_method(self):
        """Set up test transport instance"""
        self.transport = HTTPTransport(
            endpoint="https://api.example.com",
            api_key="test-api-key-12345",
            timeout=5.0,
            max_retries=2
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test transport initialization"""
        assert self.transport.endpoint == "https://api.example.com"
        assert self.transport.api_key == "test-api-key-12345"
        assert self.transport.timeout == 5.0
        assert self.transport._connected is False
        assert self.transport._client is None
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock health check response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_response.elapsed.total_seconds.return_value = 0.1
            mock_client.get.return_value = mock_response
            
            await self.transport.connect()
            
            assert self.transport._connected is True
            assert self.transport._client is not None
            mock_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            import httpx
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            
            with pytest.raises(ConnectionError, match="Health check failed"):
                await self.transport.connect()
            
            assert self.transport._connected is False
    
    @pytest.mark.asyncio
    async def test_send_batch_success(self):
        """Test successful batch sending"""
        events = [
            ToolExecutionEvent(
                server_id="test-server",
                tool_name="test-tool",
                duration_ms=100,
                success=True
            )
        ]
        batch = BatchRequest(events=events)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            self.transport._connected = True
            
            mock_response = Mock()
            mock_response.status_code = 200
        
            mock_response.json.return_value = {
                "batch_id": batch.batch_id,
                "success": True,
                "processed_count": 1,
                "failed_count": 0
            }
            mock_client.post.return_value = mock_response
            
            result = await self.transport.send_batch(batch)
            
            assert isinstance(result, BatchResponse)
            assert result.success is True
            assert result.processed_count == 1
            assert result.failed_count == 0
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_batch_authentication_error(self):
        """Test authentication error handling"""
        events = [ToolExecutionEvent(server_id="test", tool_name="test", duration_ms=100 , success=True)]
        batch = BatchRequest(events=events)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            self.transport._connected = True
            
            # Mock 401 response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Invalid API key"}
            mock_client.post.return_value = mock_response
            
            with pytest.raises(AuthenticationError, match="Invalid API key"):
                await self.transport.send_batch(batch)
    
    @pytest.mark.asyncio
    async def test_send_batch_rate_limit_error(self):
        """Test rate limit error handling - should not be retried"""
        events = [ToolExecutionEvent(server_id="test", tool_name="test", duration_ms=100, success=True)]
        batch = BatchRequest(events=events)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            self.transport._connected = True
            
            # Mock 429 response with retry-after
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_client.post.return_value = mock_response
            
            with pytest.raises(RateLimitError) as exc_info:
                await self.transport.send_batch(batch)
            
            assert exc_info.value.retry_after == 60
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_batch_server_error(self):
        """Test server error handling"""
        events = [ToolExecutionEvent(server_id="test", tool_name="test", duration_ms=100, success=True)]
        batch = BatchRequest(events=events)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            self.transport._connected = True
            
            # Mock 500 response
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_client.post.return_value = mock_response
            
            with pytest.raises(RetryExhaustedError) as exc_info:
                await self.transport.send_batch(batch)
            
            assert exc_info.value.last_error.status_code == 500
    
    @pytest.mark.asyncio
    async def test_send_batch_timeout(self):
        """Test timeout handling - should be retried and then exhausted"""
        events = [ToolExecutionEvent(server_id="test", tool_name="test", duration_ms=100, success=True)]
        batch = BatchRequest(events=events)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            self.transport._connected = True
            
            # Mock timeout
            import httpx
            mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
            
            with pytest.raises(RetryExhaustedError) as exc_info:
                await self.transport.send_batch(batch)
            
            # Verify the underlying error was a TimeoutError
            assert isinstance(exc_info.value.last_error, TimeoutError)
            assert "Request timeout" in str(exc_info.value.last_error)
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            
            # Mock successful health response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy", "version": "1.0.0"}
            mock_response.elapsed.total_seconds.return_value = 0.05
            mock_client.get.return_value = mock_response
            
            result = await self.transport.health_check()
            
            assert result["status"] == "healthy"
            assert result["endpoint"] == "https://api.example.com"
            assert "response_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test unhealthy health check"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            self.transport._client = mock_client
            
            # Mock unhealthy response
            mock_response = Mock()
            mock_response.status_code = 503
            mock_client.get.return_value = mock_response
            
            result = await self.transport.health_check()
            
            assert result["status"] == "unhealthy"
            assert result["status_code"] == 503
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test connection cleanup"""
        mock_client = AsyncMock()
        self.transport._client = mock_client
        self.transport._connected = True
        
        await self.transport.close()
        
        assert self.transport._connected is False
        assert self.transport._client is None
        mock_client.aclose.assert_called_once()
    
    def test_repr(self):
        """Test string representation"""
        repr_str = repr(self.transport)
        assert "HTTPTransport" in repr_str
        assert "https://api.example.com" in repr_str
        assert "connected=False" in repr_str


class TestAsyncHTTPTransport:
    """Test async context manager functionality"""
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager usage"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock health check
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_response.elapsed.total_seconds.return_value = 0.1
            mock_client.get.return_value = mock_response
            
            async with AsyncHTTPTransport(
                endpoint="https://api.example.com",
                api_key="test-key"
            ) as transport:
                assert transport._connected is True
                assert transport._client is not None
            
            # Should be cleaned up after context
            mock_client.aclose.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
