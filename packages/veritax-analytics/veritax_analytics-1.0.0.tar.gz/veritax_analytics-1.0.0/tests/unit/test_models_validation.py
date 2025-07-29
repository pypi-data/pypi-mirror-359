from datetime import datetime, timezone, timedelta
import json
import pytest
from pydantic import ValidationError

from veritax_analytics.models import (
    EventType,
    AnalyticsEvent,
    ToolExecutionEvent,
    ServerHealthEvent,
    Configuration,
    BatchRequest,
    BatchResponse,
    APIResponse,
    HealthCheckResponse
)


def test_event_type_enum():
    """Test EventType enum values and serialization"""
    assert EventType.TOOL_EXECUTION == "tool_execution"
    assert EventType.SERVER_HEALTH == "server_health"
    
    # Test enum in JSON serialization
    assert EventType.TOOL_EXECUTION.value == "tool_execution"


def test_analytics_event_base_model():
    """Test AnalyticsEvent base model with required fields"""
    # Valid event creation
    event = AnalyticsEvent(
        event_type=EventType.TOOL_EXECUTION,
        server_id="test-server-123"
    )
    
    assert event.event_id is not None
    assert len(event.event_id) > 10  # UUID should be substantial
    assert event.event_type == EventType.TOOL_EXECUTION
    assert event.server_id == "test-server-123"
    assert event.sdk_version == "1.0.0"
    assert isinstance(event.timestamp, datetime)
    
    # Test JSON serialization
    json_data = event.model_dump_json()
    data = json.loads(json_data)
    assert data["event_type"] == "tool_execution"
    assert data["timestamp"].endswith("Z")  # UTC timezone format


def test_analytics_event_validation_errors():
    """Test AnalyticsEvent validation failures"""
    # Missing required server_id
    with pytest.raises(ValidationError) as exc_info:
        AnalyticsEvent(event_type=EventType.TOOL_EXECUTION)
    
    assert "server_id" in str(exc_info.value)
    
    # Empty server_id
    with pytest.raises(ValidationError):
        AnalyticsEvent(
            event_type=EventType.TOOL_EXECUTION,
            server_id=""
        )
    
    # Server_id too long
    with pytest.raises(ValidationError):
        AnalyticsEvent(
            event_type=EventType.TOOL_EXECUTION,
            server_id="a" * 256
        )


def test_tool_execution_event_valid():
    """Test ToolExecutionEvent with valid data"""
    event = ToolExecutionEvent(
        server_id="test-server",
        tool_name="search_by_query",
        duration_ms=150,
        success=True,
        metadata={"user_id": "123", "version": "1.0"}
    )
    
    assert event.event_type == EventType.TOOL_EXECUTION
    assert event.tool_name == "search_by_query"
    assert event.duration_ms == 150
    assert event.success is True
    assert event.metadata == {"user_id": "123", "version": "1.0"}


def test_tool_execution_event_duration_calculation():
    """Test automatic duration calculation from start/end times"""
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(milliseconds=500)
    
    event = ToolExecutionEvent(
        server_id="test-server",
        tool_name="search_by_query",
        execution_start_time=start_time,
        execution_end_time=end_time,
        success=True
    )
    
    assert event.duration_ms == 500


def test_tool_execution_event_duration_calculation_with_string_timestamps():
    """Test duration calculation with ISO string timestamps"""
    event_data = {
        "server_id": "test-server",
        "tool_name": "search_by_query", 
        "execution_start_time": "2023-06-01T10:00:00Z",
        "execution_end_time": "2023-06-01T10:00:03.500Z",
        "success": True
    }
    
    event = ToolExecutionEvent(**event_data)
    assert event.duration_ms == 3500


def test_tool_execution_event_time_validation():
    """Test execution time validation"""
    start_time = datetime.now(timezone.utc)
    end_time = start_time - timedelta(seconds=1)
        
    with pytest.raises(ValidationError) as exc_info:
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="test_tool",
            execution_start_time=start_time,
            execution_end_time=end_time,
            success=True
        )

    assert "execution_start_time cannot be after execution_end_time" in str(exc_info.value)


def test_tool_execution_event_error_fields():
    """Test error type and message validation"""
    # Valid error fields
    event = ToolExecutionEvent(
        server_id="test-server",
        tool_name="test-tool",
        success=False,
        error_type="ValidationError",
        error_message="Invalid parameter provided"
    )
    
    assert event.error_type == "ValidationError"
    assert event.error_message == "Invalid parameter provided"
    
    # Error type too long should fail
    with pytest.raises(ValidationError):
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="test-tool",
            success=False,
            error_type="x" * 101
        )
    
    # Error message too long should fail
    with pytest.raises(ValidationError):
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="test-tool",
            success=False,
            error_message="x" * 1001
        )


def test_tool_execution_event_validation_errors():
    """Test ToolExecutionEvent validation failures"""
    # Tool name too long
    with pytest.raises(ValidationError):
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="a" * 256,
            success=True
        )
    
    # Duration too large
    with pytest.raises(ValidationError):
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="test_tool",
            duration_ms=3600001,  # Over 1 hour limit
            success=True
        )
    
    # Negative duration
    with pytest.raises(ValidationError):
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="test_tool",
            duration_ms=-1,
            success=True
        )


def test_server_health_event_valid():
    """Test ServerHealthEvent with valid data"""
    event = ServerHealthEvent(
        server_id="test-server",
        cpu_usage_percent=45.5,
        memory_usage_mb=512,
        active_connections=10,
        requests_per_minute=150
    )
    
    assert event.event_type == EventType.SERVER_HEALTH
    assert event.cpu_usage_percent == 45.5
    assert event.memory_usage_mb == 512
    assert event.active_connections == 10
    assert event.requests_per_minute == 150


def test_server_health_event_validation():
    """Test ServerHealthEvent validation"""
    # CPU usage over 100%
    with pytest.raises(ValidationError) as exc_info:
        ServerHealthEvent(
            server_id="test-server",
            cpu_usage_percent=150.0
        )
    
    assert "CPU usage must be between 0 and 100 percent" in str(exc_info.value)
    
    # Negative CPU usage
    with pytest.raises(ValidationError):
        ServerHealthEvent(
            server_id="test-server",
            cpu_usage_percent=-5.0
        )
    
    # Negative memory
    with pytest.raises(ValidationError):
        ServerHealthEvent(
            server_id="test-server",
            memory_usage_mb=-100
        )


def test_server_health_event_optional_fields():
    """Test that health event fields are optional"""
    event = ServerHealthEvent(server_id="test-server")
    
    assert event.cpu_usage_percent is None
    assert event.memory_usage_mb is None
    assert event.active_connections is None
    assert event.requests_per_minute is None


def test_configuration_valid():
    """Test Configuration with valid data"""
    config = Configuration(
        api_key="test-api-key-12345",
        endpoint="https://api.example.com/v1/events"
    )
    
    assert config.api_key == "test-api-key-12345"
    assert str(config.endpoint) == "https://api.example.com/v1/events"
    assert config.batch_size == 50  # Default
    assert config.flush_interval == 30  # Default
    assert config.timeout == 10  # Default
    assert config.max_retries == 3  # Default
    assert config.retry_backoff_factor == 2.0  # Default
    
    # Check auto-generated fields
    assert config.server_id is not None
    assert len(config.server_id) > 5
    assert config.user_agent is not None
    assert "VeritaxAnalyticsSDK" in config.user_agent


def test_configuration_validation():
    """Test Configuration validation failures"""
    # API key too short
    with pytest.raises(ValidationError):
        Configuration(
            api_key="short",
            endpoint="https://api.example.com"
        )
    
    # Invalid URL
    with pytest.raises(ValidationError):
        Configuration(
            api_key="valid-api-key-12345",
            endpoint="not-a-url"
        )
    
    # Batch size too large
    with pytest.raises(ValidationError):
        Configuration(
            api_key="valid-api-key-12345",
            endpoint="https://api.example.com",
            batch_size=1001
        )
    
    # Negative timeout
    with pytest.raises(ValidationError):
        Configuration(
            api_key="valid-api-key-12345",
            endpoint="https://api.example.com",
            timeout=-1
        )


def test_configuration_custom_values():
    """Test Configuration with custom values"""
    config = Configuration(
        api_key="  custom-api-key-with-spaces  ",
        endpoint="https://custom.api.com/events",
        batch_size=100,
        flush_interval=60,
        timeout=30,
        max_retries=5,
        retry_backoff_factor=3.0,
        server_id="custom-server-id",
        user_agent="CustomAgent/1.0"
    )
    
    assert config.api_key == "custom-api-key-with-spaces"  # Stripped
    assert config.batch_size == 100
    assert config.flush_interval == 60
    assert config.timeout == 30
    assert config.max_retries == 5
    assert config.retry_backoff_factor == 3.0
    assert config.server_id == "custom-server-id"
    assert config.user_agent == "CustomAgent/1.0"


def test_batch_request_valid():
    """Test BatchRequest with valid data"""
    events = [
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="tool1",
            success=True
        ),
        ServerHealthEvent(
            server_id="test-server",
            cpu_usage_percent=50.0
        )
    ]
    
    batch = BatchRequest(events=events)
    
    assert len(batch.events) == 2
    assert batch.batch_id is not None
    assert isinstance(batch.timestamp, datetime)
    
    # Test JSON serialization
    json_data = batch.model_dump_json()
    data = json.loads(json_data)
    assert len(data["events"]) == 2
    assert data["timestamp"].endswith("Z")


def test_batch_request_validation():
    """Test BatchRequest validation"""
    # Empty events list
    with pytest.raises(ValidationError, match="Batch must contain at least one event"):
        BatchRequest(events=[])
    
    # Too many events
    events = [
        ToolExecutionEvent(
            server_id="test-server",
            tool_name=f"tool{i}",
            success=True
        ) for i in range(1001)
    ]
    
    with pytest.raises(ValidationError):
        BatchRequest(events=events)


def test_batch_request_batch_id_uniqueness():
    """Test that batch IDs are unique"""
    events = [ToolExecutionEvent(server_id="test", tool_name="test", success=True)]
    
    batch1 = BatchRequest(events=events)
    batch2 = BatchRequest(events=events)
    
    assert batch1.batch_id != batch2.batch_id


def test_batch_response_valid():
    """Test BatchResponse with valid data"""
    response = BatchResponse(
        batch_id="test-batch-123",
        success=True,
        processed_count=5,
        failed_count=1,
        errors=["Event 3 failed validation"],
        processing_time_ms=250
    )
    
    assert response.batch_id == "test-batch-123"
    assert response.success is True
    assert response.processed_count == 5
    assert response.failed_count == 1
    assert response.errors == ["Event 3 failed validation"]
    assert response.processing_time_ms == 250


def test_batch_response_defaults():
    """Test BatchResponse with minimal data"""
    response = BatchResponse(
        batch_id="test-batch-123",
        success=True,
        processed_count=3
    )
    
    assert response.failed_count == 0
    assert response.errors == []
    assert response.processing_time_ms is None


def test_batch_response_validation():
    """Test BatchResponse validation"""
    with pytest.raises(ValidationError):
        BatchResponse(
            batch_id="test-batch-123",
            success=False,
            processed_count=2,
            failed_count=1,
            errors=[]
        )
    
    # Negative processed count
    with pytest.raises(ValidationError):
        BatchResponse(
            batch_id="test-batch-123",
            success=True,
            processed_count=-1
        )
    
    # Negative failed count
    with pytest.raises(ValidationError):
        BatchResponse(
            batch_id="test-batch-123",
            success=True,
            processed_count=1,
            failed_count=-1
        )


def test_api_response_valid():
    """Test APIResponse with valid data"""
    response = APIResponse(
        success=True,
        message="Operation completed successfully",
        data={"result_count": 42},
        request_id="req-123"
    )
    
    assert response.success is True
    assert response.message == "Operation completed successfully"
    assert response.data == {"result_count": 42}
    assert response.request_id == "req-123"
    assert response.timestamp is not None


def test_api_response_minimal():
    """Test APIResponse with only required fields"""
    response = APIResponse(
        success=False,
        message="Operation failed"
    )
    
    assert response.success is False
    assert response.message == "Operation failed"
    assert response.data is None
    assert response.request_id is None


def test_health_check_response():
    """Test HealthCheckResponse with default and custom values"""
    # Default values
    health = HealthCheckResponse(status="healthy")
    
    assert health.status == "healthy"
    assert health.version == "1.0.0"
    assert isinstance(health.timestamp, datetime)
    assert health.uptime_seconds is None
    assert health.checks == {}
    assert health.metrics == {}
    
    # Custom values
    custom_health = HealthCheckResponse(
        status="degraded",
        version="2.0.0",
        uptime_seconds=3600,
        checks={"database": True, "cache": False},
        metrics={"requests_per_sec": 100.5, "error_rate": 0.01}
    )
    
    assert custom_health.status == "degraded"
    assert custom_health.version == "2.0.0"
    assert custom_health.uptime_seconds == 3600
    assert custom_health.checks == {"database": True, "cache": False}
    assert custom_health.metrics == {"requests_per_sec": 100.5, "error_rate": 0.01}


def test_health_check_response_status_validation():
    """Test health check status validation"""
    # Valid statuses
    for status in ["healthy", "degraded", "unhealthy"]:
        response = HealthCheckResponse(status=status)
        assert response.status == status
    
    # Invalid status should fail
    with pytest.raises(ValidationError, match="Status must be one of"):
        HealthCheckResponse(status="invalid")


def test_json_serialization_consistency():
    """Test that all models serialize consistently to JSON"""
    # Create sample events
    tool_event = ToolExecutionEvent(
        server_id="test-server",
        tool_name="test_tool",
        success=True
    )
    
    health_event = ServerHealthEvent(
        server_id="test-server",
        cpu_usage_percent=50.0
    )
    
    config = Configuration(
        api_key="test-api-key-12345",
        endpoint="https://api.example.com"
    )
    
    batch = BatchRequest(events=[tool_event, health_event])
    batch_response = BatchResponse(
        batch_id="test-batch",
        success=True,
        processed_count=2
    )
    api_response = APIResponse(success=True, message="Test")
    health_response = HealthCheckResponse(status="healthy")
    
    # Test all can be serialized
    models = [tool_event, health_event, config, batch, batch_response, api_response, health_response]
    
    for model in models:
        json_str = model.model_dump_json()
        data = json.loads(json_str)
        
        # All timestamps should end with Z
        if 'timestamp' in data:
            assert data['timestamp'].endswith('Z')
        
        # Should be valid JSON
        assert isinstance(data, dict)


def test_model_validation_edge_cases():
    """Test edge cases and boundary conditions"""
    # Maximum valid duration
    event = ToolExecutionEvent(
        server_id="test-server",
        tool_name="long_tool",
        duration_ms=3600000,  # Exactly 1 hour
        success=True
    )
    assert event.duration_ms == 3600000
    
    # Maximum batch size
    events = [
        ToolExecutionEvent(
            server_id="test-server",
            tool_name=f"tool{i}",
            success=True
        ) for i in range(1000)
    ]
    
    batch = BatchRequest(events=events)
    assert len(batch.events) == 1000
    
    # Minimum valid values
    config = Configuration(
        api_key="1234567890",  # Exactly 10 chars
        endpoint="https://a.co",
        batch_size=1,
        flush_interval=1,
        timeout=1,
        max_retries=0,
        retry_backoff_factor=1.0
    )
    assert config.batch_size == 1


def test_mixed_event_types_in_batch():
    """Test BatchRequest with mixed event types"""
    events = [
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="tool1",
            success=True
        ),
        ServerHealthEvent(
            server_id="test-server",
            cpu_usage_percent=75.0
        ),
        ToolExecutionEvent(
            server_id="test-server",
            tool_name="tool2",
            success=False,
            error_type="TimeoutError",
            error_message="Tool execution timed out"
        )
    ]
    
    batch = BatchRequest(events=events)
    assert len(batch.events) == 3
    assert isinstance(batch.events[0], ToolExecutionEvent)
    assert isinstance(batch.events[1], ServerHealthEvent)
    assert isinstance(batch.events[2], ToolExecutionEvent)
    
    # Verify the batch can be serialized
    json_data = batch.model_dump_json()
    data = json.loads(json_data)
    assert len(data["events"]) == 3


if __name__ == "__main__":
    print("🧪 Running comprehensive model validation tests...")
    
    # Run all test functions
    test_functions = [
        test_event_type_enum,
        test_analytics_event_base_model,
        test_analytics_event_validation_errors,
        test_tool_execution_event_valid,
        test_tool_execution_event_duration_calculation,
        test_tool_execution_event_duration_calculation_with_string_timestamps,
        test_tool_execution_event_time_validation,
        test_tool_execution_event_validation_errors,
        test_tool_execution_event_error_fields,
        test_server_health_event_valid,
        test_server_health_event_validation,
        test_server_health_event_optional_fields,
        test_configuration_valid,
        test_configuration_validation,
        test_configuration_custom_values,
        test_batch_request_valid,
        test_batch_request_validation,
        test_batch_request_batch_id_uniqueness,
        test_batch_response_valid,
        test_batch_response_defaults,
        test_batch_response_validation,
        test_api_response_valid,
        test_api_response_minimal,
        test_health_check_response,
        test_health_check_response_status_validation,
        test_json_serialization_consistency,
        test_model_validation_edge_cases,
        test_mixed_event_types_in_batch
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All validation tests passed for models")
    else:
        print("⚠️  Some tests failed.")
        exit(1)
