from typing import Any, Dict, List, Optional, Union , Literal
from datetime import datetime, timezone
from uuid import uuid4
import platform
import socket
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from enum import Enum


class EventType(str, Enum):
    TOOL_EXECUTION = "tool_execution"
    SERVER_HEALTH = "server_health"


class AnalyticsEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    server_id: str = Field(..., min_length=1, max_length=255)
    sdk_version: str = Field(default="1.0.0")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat().replace('+00:00', 'Z')
        }


class ToolExecutionEvent(AnalyticsEvent):
    event_type: Literal[EventType.TOOL_EXECUTION] = Field(default=EventType.TOOL_EXECUTION)
    tool_name: str = Field(..., min_length=1, max_length=255)
    execution_start_time: Optional[datetime] = None
    execution_end_time: Optional[datetime] = None
    duration_ms: Optional[int] = Field(None, ge=0, le=3600000)
    success: bool
    error_type: Optional[str] = Field(None, max_length=100)
    error_message: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_and_validate_duration(cls, data):
        if isinstance(data, dict):
            if 'duration_ms' not in data or data['duration_ms'] is None:
                start = data.get('execution_start_time')
                end = data.get('execution_end_time')
                
                if start and end:
                    if isinstance(start, str):
                        start = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    if isinstance(end, str):
                        end = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    
                    if start > end:
                        raise ValueError('execution_start_time cannot be after execution_end_time')
                    
                    calculated_duration = int((end - start).total_seconds() * 1000)
                    
                    # Check for negative duration (should not happen after time validation, but safety check)
                    if calculated_duration < 0:
                        raise ValueError('Calculated duration cannot be negative')
                    
                    data['duration_ms'] = calculated_duration
        return data


class ServerHealthEvent(AnalyticsEvent):
    event_type: Literal[EventType.SERVER_HEALTH] = Field(default=EventType.SERVER_HEALTH)
    cpu_usage_percent: Optional[float] = Field(None, ge=0, le=100)
    memory_usage_mb: Optional[int] = Field(None, ge=0)
    active_connections: Optional[int] = Field(None, ge=0)
    requests_per_minute: Optional[int] = Field(None, ge=0)
    
    @field_validator('cpu_usage_percent', mode='before')
    @classmethod
    def validate_cpu_usage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('CPU usage must be between 0 and 100 percent')
        return v


class Configuration(BaseModel):
    api_key: str = Field(..., min_length=10)
    endpoint: HttpUrl
    batch_size: int = Field(default=50, ge=1, le=1000)
    flush_interval: int = Field(default=30, ge=1, le=300)
    timeout: int = Field(default=10, ge=1, le=60)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff_factor: float = Field(default=2.0, ge=1.0, le=10.0)
    server_id: str = Field(default_factory=lambda: f"{platform.node()}-{str(uuid4())[:8]}")
    user_agent: str = Field(default_factory=lambda: f"VeritaxAnalyticsSDK/1.0.0 Python/{platform.python_version()} {platform.system()}")
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('API key must be at least 10 characters long')
        return v.strip()
    
    class Config:
        validate_assignment = True


class BatchRequest(BaseModel):
    """
    Request model for sending batches of analytics events.
    
    Represents a collection of events being sent together for efficient
    network transmission and processing.
    """
    
    batch_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this batch"
    )
    
    events: List[Union[ToolExecutionEvent, ServerHealthEvent]] = Field(
        ...,
        description="List of analytics events in this batch",
        min_length=1,
        max_length=1000
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this batch was created"
    )
    
    @field_validator('events', mode="before")
    @classmethod
    def validate_events_not_empty(cls, v):
        """Ensure batch contains at least one event."""
        if not v:
            raise ValueError("Batch must contain at least one event")
        return v


class BatchResponse(BaseModel):
    """
    Response model for batch processing results.
    
    Indicates the success/failure status and provides details
    about processing results for each event in the batch.
    """
    
    batch_id: str = Field(
        ...,
        description="Unique identifier for the processed batch"
    )
    
    success: bool = Field(
        ...,
        description="Whether the batch was processed successfully"
    )
    
    processed_count: int = Field(
        ...,
        description="Number of events successfully processed",
        ge=0
    )
    
    failed_count: int = Field(
        default=0,
        description="Number of events that failed processing",
        ge=0
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="List of error messages for failed events"
    )
    
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Time taken to process the batch in milliseconds",
        ge=0
    )
    
    @model_validator(mode='after')
    def validate_counts(self):
        """Ensure processed and failed counts are consistent."""
        total_expected = self.processed_count + self.failed_count
        if self.failed_count > 0 and not self.errors:
            raise ValueError("Errors list must not be empty when failed_count > 0")
        return self


class APIResponse(BaseModel):
    """
    Generic API response model for non-batch endpoints.
    
    Provides a standardized structure for API responses including
    status, messages, and optional data payload.
    """
    
    success: bool = Field(
        ...,
        description="Whether the API operation was successful"
    )
    
    message: str = Field(
        ...,
        description="Human-readable message about the operation result"
    )
    
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional data payload for the response"
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this response was generated"
    )
    
    request_id: Optional[str] = Field(
        default=None,
        description="Optional request identifier for tracing"
    )


class HealthCheckResponse(BaseModel):
    """
    Health check response model for service monitoring.
    
    Provides information about service status, version,
    and operational metrics for monitoring systems.
    """
    
    status: str = Field(
        ...,
        description="Service status (healthy, degraded, unhealthy)"
    )
    
    version: str = Field(
        default="1.0.0",
        description="Service version information"
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this health check was performed"
    )
    
    uptime_seconds: Optional[int] = Field(
        default=None,
        description="Service uptime in seconds",
        ge=0
    )
    
    checks: Dict[str, bool] = Field(
        default_factory=dict,
        description="Individual health check results"
    )
    
    metrics: Dict[str, Union[int, float, str]] = Field(
        default_factory=dict,
        description="Operational metrics and statistics"
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Ensure status is one of the allowed values."""
        allowed_statuses = {'healthy', 'degraded', 'unhealthy'}
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v
