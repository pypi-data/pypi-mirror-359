"""
HTTP Transport Layer for the Veritax Analytics SDK.

This module provides HTTP-based communication with analytics backends,
including batch processing, retry logic, and comprehensive error handling.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx

from .models import BatchRequest, BatchResponse, AnalyticsEvent
from .exceptions import (
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
from .utils import exponential_backoff_retry, is_retryable_error, safe_json_serialize

# Configure transport logger
logger = logging.getLogger(__name__)


class Transport(ABC):
    """Abstract base class for transport implementations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the transport endpoint."""
        pass
    
    @abstractmethod
    async def send_batch(self, batch_request: BatchRequest) -> BatchResponse:
        """Send a batch of events to the transport endpoint."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check against the transport endpoint."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the transport connection and cleanup resources."""
        pass


class HTTPTransport(Transport):
    """
    HTTP-based transport implementation using httpx.
    
    Provides async HTTP communication with retry logic, connection pooling,
    and comprehensive error handling for analytics backends.
    """
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        user_agent: str = "veritax-analytics-sdk/1.0.0"
    ):
        """
        Initialize HTTP transport.
        
        Args:
            endpoint: Base URL for the analytics API
            api_key: Authentication API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            max_retry_delay: Maximum delay between retries in seconds
            user_agent: User agent string for requests
        """
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_retry_delay = max_retry_delay
        self.user_agent = user_agent
        
        # HTTP client will be initialized in connect()
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False
    
    async def connect(self) -> None:
        """
        Establish HTTP client connection and verify endpoint connectivity.
        
        Raises:
            ConnectionError: If connection cannot be established
            AuthenticationError: If API key is invalid
            ValidationError: If endpoint is unreachable
        """
        if self._connected and self._client:
            return
        
        try:
            
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                # --todo @mark , maybe we can keep these settings configurable
                # but for now, let's use reasonable defaults
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30.0
                ),
                headers={
                    "User-Agent": self.user_agent,
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            # Verify connectivity with health check
            await self.health_check()
            self._connected = True
            logger.info(f"HTTP transport connected to {self.endpoint}")
            
        # network level errors , i am not sure if we will need to close the connection here
        # i just decided not to as there was no connection established those are retryable    
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self.endpoint}: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Connection timeout to {self.endpoint}: {e}")
        
        # non-connection errors should close the connection
        except Exception as e:
            if self._client:
                await self._client.aclose()
                self._client = None
            raise ConnectionError(f"Connection failed: {e}")
    
    @exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0,
        exceptions=(ConnectionError, TimeoutError, ServerError)
    )
    async def send_batch(self, batch_request: BatchRequest) -> BatchResponse:
        """
        Send a batch of analytics events to the HTTP endpoint.
        
        Args:
            batch_request: Batch of events to send
            
        Returns:
            BatchResponse with processing results
            
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limits are exceeded (not retried automatically)
            ValidationError: If request data is invalid
            BatchError: If batch processing fails
            TimeoutError: If request times out
            ServerError: If server returns 5xx error
            ClientError: If client request is invalid (4xx)
        """
        if not self._connected or not self._client:
            await self.connect()
        
        # Serialize batch request
        try:
            payload = {
                "events": [
                    safe_json_serialize(event.model_dump()) 
                    for event in batch_request.events
                ],
                "batch_id": batch_request.batch_id,
                "timestamp": batch_request.timestamp.isoformat()
            }
        except Exception as e:
            raise ValidationError(f"Failed to serialize batch request: {e}")
        
        # Send HTTP request
        url = urljoin(self.endpoint + "/", "v1/events")
        
        try:
            response = await self._client.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            # Handle response status codes
            await self._handle_response_status(response)
            
            # Parse successful response
            try:
                response_data = response.json()
                return BatchResponse(
                    batch_id=response_data.get("batch_id", batch_request.batch_id),
                    success=response_data.get("success", True),
                    processed_count=response_data.get("processed_count", len(batch_request.events)),
                    failed_count=response_data.get("failed_count", 0),
                    errors=response_data.get("errors", [])
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Invalid response format from {url}: {e}")
                # Return default success response if we got 2xx but bad JSON
                return BatchResponse(
                    batch_id=batch_request.batch_id,
                    success=True,
                    processed_count=len(batch_request.events),
                    failed_count=0,
                    errors=[]
                )
        
        except httpx.TimeoutException:
            raise TimeoutError(
                f"Request timeout after {self.timeout}s",
                timeout_duration=self.timeout
            )
        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection failed to {url}: {e}")
        except Exception as e:
            if not isinstance(e, (
                AuthenticationError, RateLimitError, ValidationError,
                ServerError, ClientError, TimeoutError, ConnectionError
            )):
                raise TransportError(f"HTTP request failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check against the analytics endpoint.
        
        Returns:
            Dictionary with health check results
            
        Raises:
            ConnectionError: If health check fails
        """
        if not self._client:
            await self.connect()
        
        url = urljoin(self.endpoint + "/", "v1/health")
        
        try:
            response = await self._client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    return {
                        "status": "healthy",
                        "endpoint": self.endpoint,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        **health_data
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "healthy",
                        "endpoint": self.endpoint,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
            else:
                return {
                    "status": "unhealthy",
                    "endpoint": self.endpoint,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            raise ConnectionError(f"Health check failed for {self.endpoint}: {e}")
    
    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False
        logger.info("HTTP transport connection closed")
    
    async def _handle_response_status(self, response: httpx.Response) -> None:
        """
        Handle HTTP response status codes and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            
        Raises:
            AuthenticationError: For 401/403 status codes
            RateLimitError: For 429 status code
            ValidationError: For 400 status code
            ServerError: For 5xx status codes
            ClientError: For other 4xx status codes
        """
        if 200 <= response.status_code < 300:
            return  # Success
        
        # Extract error details from response
        error_details = {"status_code": response.status_code}
        try:
            error_data = response.json()
            error_details.update(error_data)
        except json.JSONDecodeError:
            error_details["message"] = response.text[:200]  # Truncate long messages
        
        # Map status codes to exceptions
        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid API key or authentication failed",
                details=error_details
            )
        elif response.status_code == 403:
            raise AuthenticationError(
                "API key lacks required permissions",
                details=error_details
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
                details=error_details
            )
        elif response.status_code == 400:
            raise ValidationError(
                error_details.get("message", "Bad request format"),
                details=error_details
            )
        elif 500 <= response.status_code < 600:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
                details=error_details
            )
        elif 400 <= response.status_code < 500:
            raise ClientError(
                f"Client error: {response.status_code}",
                status_code=response.status_code,
                details=error_details
            )
        else:
            raise TransportError(
                f"Unexpected status code: {response.status_code}",
                details=error_details
            )
    
    def __repr__(self) -> str:
        """String representation of the transport."""
        return f"HTTPTransport(endpoint='{self.endpoint}', connected={self._connected})"


# Async context manager support
class AsyncHTTPTransport(HTTPTransport):
    """HTTP Transport with async context manager support."""
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
