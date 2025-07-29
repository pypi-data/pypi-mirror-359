"""
Utility functions for the Veritax Analytics SDK.

This module provides shared functionality used across the SDK:
- Retry logic with exponential backoff
- Validation helpers
- Data sanitization
- Logging utilities
"""

import asyncio
import random
import time
import re
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union, List, Tuple, Type, TYPE_CHECKING
from functools import wraps
from urllib.parse import urlparse
from datetime import datetime, timezone
import json
import uuid

from .exceptions import (
    ValidationError, 
    TimeoutError, 
    RetryExhaustedError,
    ConfigurationError
)

# Type variable for retry decorator
T = TypeVar('T')

# Configure SDK logger
logger = logging.getLogger(__name__)

# Import for type hints - avoid circular imports by importing only when needed
if TYPE_CHECKING:
    from .models import AnalyticsEvent


def validate_api_key(api_key: str) -> str:
    """
    Validate and sanitize API key format.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Cleaned API key string
        
    Raises:
        ValidationError: If API key format is invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key must be a non-empty string")
    
    # Remove whitespace
    cleaned_key = api_key.strip()
    
    if len(cleaned_key) < 10:
        raise ValidationError("API key must be at least 10 characters long")
    
    # Check for basic format (alphanumeric + common special chars)
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', cleaned_key):
        raise ValidationError("API key contains invalid characters")
    
    return cleaned_key


def validate_endpoint_url(url: str) -> str:
    """
    Validate and normalize endpoint URL.
    
    Args:
        url: The endpoint URL to validate
        
    Returns:
        Normalized URL string
        
    Raises:
        ValidationError: If URL format is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("Endpoint URL must be a non-empty string")
    
    # Add https:// if no scheme provided
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValidationError("Invalid URL format: missing hostname")
        
        # Ensure HTTPS in production (allow HTTP for localhost/testing)
        if parsed.scheme == 'http' and parsed.hostname not in ('localhost', '127.0.0.1'):
            logger.warning("Using HTTP instead of HTTPS for endpoint. This is not recommended for production.")
        
        return url
        
    except Exception as e:
        raise ValidationError(f"Invalid endpoint URL: {e}")


def sanitize_metadata(metadata: Dict[str, Any], max_size: int = 1000) -> Dict[str, Any]:
    """
    Sanitize and validate metadata dictionary.
    --todo @mark , this is a very basic santization , i dont know what else need to be sanitized 
    probably some furhter santization for meta data will be needed , I will figure this out later
    
    Args:
        metadata: Dictionary to sanitize
        max_size: Maximum size for string values
        
    Returns:
        Sanitized metadata dictionary
        
    Raises:
        ValidationError: If metadata is invalid
    """
    if not isinstance(metadata, dict):
        raise ValidationError("Metadata must be a dictionary")
    
    sanitized = {}
    
    for key, value in metadata.items():
        if not isinstance(key, str) or len(key) > 100:
            logger.warning(f"Skipping invalid metadata key: {key}")
            continue
        
        if isinstance(value, str):
            # Truncate long strings
            sanitized_value = value[:max_size] if len(value) > max_size else value
            # Remove potentially problematic characters
            # removes the entire range \x00-\x1f because all control characters (including tabs, newlines, form feeds, etc.)
            # \x0A removes \n (Line Feed)
            # \x0D removes \r (Carriage Return)
            # those characters can break the structure the string in BQ tables
            sanitized_value = re.sub(r'[\x00-\x1f\x7f]', '', sanitized_value)
            sanitized[key] = sanitized_value
            
        elif isinstance(value, (int, float, bool)):
            sanitized[key] = value
            
        elif isinstance(value, (list, dict)):
            # Convert complex list and dicts to strings
            sanitized[key] = str(value)[:max_size]
            
        else:
            # Convert other types to strings
            sanitized[key] = str(value)[:max_size]
    
    return sanitized


def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        jitter: Whether to add random jitter to delay
        exceptions: Tuple of exceptions to retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Retry exhausted for {func.__name__} after {attempt + 1} attempts")
                        raise RetryExhaustedError(
                            f"Failed after {attempt + 1} attempts",
                            attempt_count=attempt + 1,
                            last_error=e
                        )
                    
                    # exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    # Add jitter to prevent exaausting the server on global error
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay:.2f}s: {e}")
                    time.sleep(delay)
            
            # default exception
            raise last_exception
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Retry exhausted for {func.__name__} after {attempt + 1} attempts")
                        raise RetryExhaustedError(
                            f"Failed after {attempt + 1} attempts",
                            attempt_count=attempt + 1,
                            last_error=e
                        )
                    
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_event_data(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate event data structure and content
    --todo @mark , currently this si very basic validations , quite the same in the 
    models.py , created by pydantic , but we use this as a base to add further validations
    that will require data manupilation beyond pydantic
    
    Args:
        event_data: Event data to validate
        
    Returns:
        Validated event data
        
    Raises:
        ValidationError: If event data is invalid
    """
    if not isinstance(event_data, dict):
        raise ValidationError("Event data must be a dictionary")
    
    # --todo @mark , i will need to check if there is other fields i will need here
    required_fields = ['event_type', 'server_id']
    
    for field in required_fields:
        if field not in event_data:
            raise ValidationError(f"Missing required field: {field}")
    
    valid_event_types = ['tool_execution', 'server_health']
    if event_data.get('event_type') not in valid_event_types:
        raise ValidationError(f"Invalid event_type. Must be one of: {valid_event_types}")
    
    server_id = event_data.get('server_id')
    if not isinstance(server_id, str) or len(server_id.strip()) == 0:
        raise ValidationError("server_id must be a non-empty string")
    
    return event_data


def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize objects to JSON-compatible format.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable version of the object
    """
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, dict):
        return {str(k): safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    else:
        # Convert other types to string representation
        return str(obj)


def calculate_batch_size(event_count: int, max_batch_size: int = 1000) -> List[int]:
    """
    Calculate optimal batch sizes for processing events.
    
    Args:
        event_count: Total number of events
        max_batch_size: Maximum events per batch
        
    Returns:
        List of batch sizes
    """
    if event_count <= 0:
        return []
    
    if event_count <= max_batch_size:
        return [event_count]
    
    full_batches, remainder = divmod(event_count, max_batch_size)
    
    batch_sizes = [max_batch_size] * full_batches
    if remainder > 0:
        batch_sizes.append(remainder)
    
    return batch_sizes


def is_retryable_error(exception: Exception) -> bool:
    """
    Determine if an error is retryable with exponential backoff.
    
    Note: RateLimitError is considered "retryable" in general, but should
    use the server's retry_after guidance rather than exponential backoff.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if the error should be retried with exponential backoff
    """
    from .exceptions import (
        ConnectionError, TimeoutError, RateLimitError, 
        ServerError, AuthenticationError, ValidationError
    )
    
    # Retryable errors with exponential backoff
    if isinstance(exception, (ConnectionError, TimeoutError, ServerError)):
        return True
    
    # Non-retryable errors
    # RateLimitError is "retryable" but should use server guidance, not exponential backoff , i dont think we should retry this even from hthe client side
    # i would prefer to use this only for logging
    if isinstance(exception, (AuthenticationError, ValidationError, RateLimitError)):
        return False
    
    
    # For HTTP errors, check status codes
    if hasattr(exception, 'status_code'):
        status_code = exception.status_code
        # Retry on server errors (5xx) and timeouts, but not rate limits (429)
        if 500 <= status_code < 600 or status_code in {408}:  # Removed 429
            return True
        return False
    
    # --todo @mark , this is a very basic deafault return , i will need to add more checks here
    # For other exceptions, assume retryable by default
    return True


def setup_logging(level: int = logging.INFO, format_string: Optional[str] = None) -> logging.Logger:
    """
    Set up logging for the SDK.
    
    Args:
        level: Logging level (use logging constants: logging.DEBUG, logging.INFO, etc.)
        format_string: Custom format string for log messages
        
    Returns:
        Configured logger instance
        
    Raises:
        ValidationError: If logging level is invalid
    """
    valid_levels = {
        logging.DEBUG,
        logging.INFO, 
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL
    }
    
    if level not in valid_levels:
        raise ValidationError(
            f"Invalid logging level: {level}. "
            f"Must be one of: {sorted(valid_levels)}"
        )
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger for the SDK
    sdk_logger = logging.getLogger('veritax_analytics')
    sdk_logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not sdk_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format_string))
        sdk_logger.addHandler(handler)
    
    return sdk_logger


def write_events_to_json_file(
    events: List['AnalyticsEvent'], 
    file_path: str = "analytics_events.json",
    pretty_print: bool = True,
    append_mode: bool = True
) -> bool:
    """
    Simple callback function to write events to a JSON file.
    
    Args:
        events: List of analytics events to write
        file_path: Path to JSON file
        pretty_print: Whether to format JSON with indentation
        append_mode: If True, append to file. If False, overwrite.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from pathlib import Path
        import json
        from datetime import datetime
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert events to serializable format
        events_data = []
        for event in events:
            event_dict = event.model_dump()
            # Convert datetime objects to ISO strings
            event_dict = _serialize_datetime_recursive(event_dict)
            events_data.append(event_dict)
        
        # Prepare batch data
        batch_data = {
            "timestamp": datetime.now().isoformat(),
            "event_count": len(events_data),
            "events": events_data
        }
        
        if append_mode and file_path.exists():
            # Append to existing file
            with open(file_path, 'a') as f:
                f.write('\n')  # Separator
                if pretty_print:
                    json.dump(batch_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(batch_data, f, ensure_ascii=False)
        else:
            # Write new file or overwrite
            with open(file_path, 'w') as f:
                if pretty_print:
                    json.dump(batch_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(batch_data, f, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to write events to {file_path}: {e}")
        return False


def write_events_to_jsonl_file(
    events: List['AnalyticsEvent'], 
    file_path: str = "analytics_events.jsonl"
) -> bool:
    """
    Write events to JSONL (JSON Lines) file - one event per line.
    More efficient for streaming and large datasets.
    
    Args:
        events: List of analytics events to write
        file_path: Path to JSONL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from pathlib import Path
        import json
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'a') as f:
            for event in events:
                event_dict = event.model_dump()
                event_dict = _serialize_datetime_recursive(event_dict)
                json.dump(event_dict, f, ensure_ascii=False)
                f.write('\n')
        
        return True
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to write events to {file_path}: {e}")
        return False


def _serialize_datetime_recursive(obj):
    """Recursively convert datetime objects to ISO format strings."""
    from datetime import datetime
    
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _serialize_datetime_recursive(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_datetime_recursive(item) for item in obj]
    else:
        return obj
