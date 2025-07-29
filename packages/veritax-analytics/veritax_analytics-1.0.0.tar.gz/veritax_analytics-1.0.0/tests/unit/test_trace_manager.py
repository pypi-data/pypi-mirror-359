"""
Unit tests for TraceManager - trace execution coordination and event collection.

Tests cover:
- Trace lifecycle (start, end, context management)
- Event creation and buffering integration
- File writing functionality (new feature)
- HTTP transport integration
- Configuration management and sampling
- Thread safety and concurrent operations
- Error handling and edge cases
- Metrics collection
"""

import os
import json
import tempfile
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from src.veritax_analytics.trace_manager import TraceManager, RemoteConfig, configure_trace_manager, get_trace_manager
from src.veritax_analytics.models import ToolExecutionEvent, EventType
from src.veritax_analytics.transport import HTTPTransport
from src.veritax_analytics.exceptions import VeritaxAnalyticsError


def create_mock_transport():
    """Create a mock HTTP transport for testing."""
    transport = Mock(spec=HTTPTransport)
    transport.send_events = Mock()
    return transport


def test_trace_manager_initialization():
    """Test TraceManager initialization with different configurations."""
    # Default initialization
    manager = TraceManager()
    assert manager.transport is None
    assert manager.file_path is None
    assert isinstance(manager.config, RemoteConfig)
    assert manager.config.enabled is True
    assert manager.config.sampling_rate == 1.0
    assert len(manager._active_traces) == 0
    
    # Custom initialization
    transport = create_mock_transport()
    config = RemoteConfig(enabled=False, sampling_rate=0.5)
    file_path = "/tmp/test_events.json"
    
    manager = TraceManager(
        transport=transport,
        config=config,
        buffer_size=50,
        flush_interval=15.0,
        file_path=file_path
    )
    
    assert manager.transport is transport
    assert manager.config is config
    assert manager.file_path == file_path
    assert manager.buffer.max_size == 50
    assert manager.buffer.flush_interval == 15.0


def test_trace_lifecycle_basic():
    """Test basic trace start and end operations."""
    manager = TraceManager()
    
    # Start trace
    trace_id = manager.start_trace("test_tool", {"key": "value"})
    assert trace_id != ""
    assert len(manager._active_traces) == 1
    assert trace_id in manager._active_traces
    
    context = manager._active_traces[trace_id]
    assert context.tool_name == "test_tool"
    assert context.metadata == {"key": "value"}
    assert context.trace_id == trace_id
    
    # End trace
    manager.end_trace(trace_id, success=True)
    assert len(manager._active_traces) == 0
    assert trace_id not in manager._active_traces


def test_trace_lifecycle_with_error():
    """Test trace lifecycle when function fails."""
    manager = TraceManager()
    
    trace_id = manager.start_trace("test_tool")
    error = ValueError("Test error")
    
    manager.end_trace(trace_id, success=False, error=error)
    
    # Verify trace is cleaned up
    assert len(manager._active_traces) == 0


def test_trace_sampling():
    """Test trace sampling based on configuration."""
    # Test with sampling disabled
    config = RemoteConfig(enabled=False)
    manager = TraceManager(config=config)
    
    trace_id = manager.start_trace("test_tool")
    assert trace_id == ""  # Should return empty string when disabled
    assert len(manager._active_traces) == 0
    
    # Test with tool exclusion
    config = RemoteConfig(excluded_tools=["excluded_tool"])
    manager = TraceManager(config=config)
    
    trace_id = manager.start_trace("excluded_tool")
    assert trace_id == ""
    assert len(manager._active_traces) == 0
    
    # Test with sampling rate
    with patch('random.random', return_value=0.8):
        config = RemoteConfig(sampling_rate=0.5)  # 50% sampling
        manager = TraceManager(config=config)
        
        trace_id = manager.start_trace("test_tool")
        assert trace_id == ""  # 0.8 > 0.5, should be excluded


def test_file_writing_functionality():
    """Test the new file writing functionality."""
    # Use a simple, consistent file path
    file_path = "test_output/events.json"
    
    # Create manager with file output
    manager = TraceManager(file_path=file_path)
    
    # Create and add some events
    trace_id = manager.start_trace("test_tool", {"test": "metadata"})
    manager.end_trace(trace_id, success=True)
    
    # Force flush to write to file
    manager.flush()
    
    # Wait for background thread to complete
    time.sleep(0.1)
    
    # Verify file was created and contains events
    assert os.path.exists(file_path)
    
    with open(file_path, 'r') as f:
        events = json.load(f)
    
    assert len(events) == 1
    event = events[0]
    assert event['event_type'] == 'tool_execution'
    assert event['tool_name'] == 'test_tool'
    assert event['success'] is True
    assert 'test' in event['metadata']
    assert event['metadata']['test'] == 'metadata'
    
    print(f"\n📁 Test created file: {file_path} (not cleaned up for inspection)")


def test_file_writing_with_directory_creation():
    """Test file writing with automatic directory creation."""
    file_path = "test_output/events.json"
    
    manager = TraceManager(file_path=file_path)
    
    trace_id = manager.start_trace("directory_test_tool")
    manager.end_trace(trace_id, success=True)
    manager.flush()
    
    # Wait for background thread
    time.sleep(0.1)
    
    # Verify directory was created
    assert os.path.exists(os.path.dirname(file_path))
    assert os.path.exists(file_path)


def test_file_writing_error_handling():
    """Test file writing error handling."""
    # Use an invalid file path (directory doesn't exist and can't be created)
    invalid_path = "/root/nonexistent/events.json"  # Assuming no write permission to /root
    
    manager = TraceManager(file_path=invalid_path)
    
    # This should not raise an exception, just log an error
    trace_id = manager.start_trace("test_tool")
    manager.end_trace(trace_id, success=True)
    manager.flush()
    
    # Wait for background thread
    time.sleep(0.1)
    
    # Manager should still be functional
    assert len(manager._active_traces) == 0


def test_dual_output_http_and_file():
    """Test simultaneous HTTP transport and file output."""
    transport = create_mock_transport()
    file_path = "test_output/events.json"
    
    manager = TraceManager(transport=transport, file_path=file_path)
    
    trace_id = manager.start_trace("dual_output_tool")
    manager.end_trace(trace_id, success=True)
    manager.flush()
    
    # Wait for background thread
    time.sleep(0.1)
    
    # Verify HTTP transport was called
    transport.send_events.assert_called_once()
    
    # Verify file was written
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        events = json.load(f)
    assert len(events) == 1


def test_metrics_collection():
    """Test metrics collection and integration."""
    manager = TraceManager()
    
    trace_id = manager.start_trace("test_tool")
    
    # Add metrics during trace
    manager.add_metric("processing_time", 1.5)
    manager.add_metric("items_count", 42.0)
    
    # End trace with additional metrics
    manager.end_trace(trace_id, success=True, metrics={"final_score": 0.95})
    
    # Force flush and check the event
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert "metric_processing_time" in event.metadata
    assert event.metadata["metric_processing_time"] == 1.5
    assert "metric_items_count" in event.metadata
    assert event.metadata["metric_items_count"] == 42.0
    assert "metric_final_score" in event.metadata
    assert event.metadata["metric_final_score"] == 0.95


def test_thread_safety():
    """Test thread safety with concurrent trace operations."""
    manager = TraceManager()
    trace_ids = []
    errors = []
    
    def create_traces():
        try:
            for i in range(10):
                trace_id = manager.start_trace(f"tool_{i}")
                trace_ids.append(trace_id)
                time.sleep(0.01)  # Small delay to increase chance of race conditions
                manager.end_trace(trace_id, success=True)
        except Exception as e:
            errors.append(e)
    
    # Run multiple threads
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=create_traces)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify no errors occurred
    assert len(errors) == 0
    
    # Verify all traces were cleaned up
    assert len(manager._active_traces) == 0
    
    # Verify events were created
    events = manager.buffer.flush(force=True)
    assert len(events) == 50  # 5 threads * 10 traces each


def test_configuration_management():
    """Test configuration updates and validation."""
    manager = TraceManager()
    
    # Test valid configuration update
    new_config = {
        "enabled": False,
        "sampling_rate": 0.3,
        "excluded_tools": ["tool1", "tool2"]
    }
    
    manager.update_config(new_config)
    
    assert manager.config.enabled is False
    assert manager.config.sampling_rate == 0.3
    assert manager.config.excluded_tools == ["tool1", "tool2"]
    
    # Test invalid configuration (should not crash)
    invalid_config = {"sampling_rate": 1.5}  # > 1.0
    
    # This should log an error but not crash
    manager.update_config(invalid_config)


def test_stats_reporting():
    """Test statistics reporting functionality."""
    manager = TraceManager()
    
    # Get initial stats
    stats = manager.get_stats()
    assert stats['buffer_size'] == 0
    assert stats['active_traces'] == 0
    assert 'config' in stats
    
    # Start some traces
    trace_id1 = manager.start_trace("tool1")
    trace_id2 = manager.start_trace("tool2")
    
    stats = manager.get_stats()
    assert stats['active_traces'] == 2
    
    # End traces
    manager.end_trace(trace_id1, success=True)
    manager.end_trace(trace_id2, success=True)
    
    stats = manager.get_stats()
    assert stats['active_traces'] == 0
    assert stats['buffer_size'] > 0  # Events should be in buffer


def test_shutdown_functionality():
    """Test proper shutdown with cleanup."""
    manager = TraceManager()
    
    # Add some events
    trace_id = manager.start_trace("test_tool")
    manager.end_trace(trace_id, success=True)
    
    # Shutdown should flush remaining events
    manager.shutdown()
    
    # Buffer should be empty after shutdown
    assert manager.buffer.size() == 0


def test_global_trace_manager():
    """Test global trace manager singleton behavior."""
    # Get global instance
    manager1 = get_trace_manager()
    manager2 = get_trace_manager()
    
    # Should be the same instance
    assert manager1 is manager2
    
    # Configure global instance
    transport = create_mock_transport()
    configured_manager = configure_trace_manager(transport=transport)
    
    # Should be a new instance
    assert configured_manager is not manager1
    
    # New calls should return the configured instance
    manager3 = get_trace_manager()
    assert manager3 is configured_manager


def test_event_serialization():
    """Test event serialization for file output."""
    manager = TraceManager()
    
    # Create a trace with various data types
    trace_id = manager.start_trace("test_tool", {
        "string_value": "test",
        "number_value": 42,
        "boolean_value": True,
        "datetime_value": datetime.now(timezone.utc)
    })
    
    manager.end_trace(trace_id, success=True)
    
    # Get the events and test serialization
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    
    # Test that event can be serialized to dict
    event_dict = event.model_dump()
    assert isinstance(event_dict, dict)
    assert 'timestamp' in event_dict
    assert 'metadata' in event_dict


def test_nested_traces():
    """Test nested trace functionality with parent-child relationships."""
    manager = TraceManager()
    
    # Start parent trace
    parent_id = manager.start_trace("parent_tool", {"level": "parent"})
    
    # Start child trace (would normally be handled by trace context)
    child_id = manager.start_trace("child_tool", {"level": "child"}, parent_trace_id=parent_id)
    
    # End child first
    manager.end_trace(child_id, success=True)
    
    # End parent
    manager.end_trace(parent_id, success=True)
    
    # Verify both traces were created
    events = manager.buffer.flush(force=True)
    assert len(events) == 2
    
    # Find parent and child events
    parent_event = next(e for e in events if e.metadata.get("level") == "parent")
    child_event = next(e for e in events if e.metadata.get("level") == "child")
    
    assert parent_event.tool_name == "parent_tool"
    assert child_event.tool_name == "child_tool"


def test_add_metric_without_active_trace():
    """Test adding metrics when no trace is active."""
    manager = TraceManager()
    
    # This should not crash, just log a debug message
    manager.add_metric("test_metric", 1.0)
    
    # No events should be created
    events = manager.buffer.flush(force=True)
    assert len(events) == 0


def test_end_unknown_trace():
    """Test ending a trace that doesn't exist."""
    manager = TraceManager()
    
    # This should not crash, just log a warning
    manager.end_trace("unknown-trace-id", success=True)
    
    # No events should be created
    events = manager.buffer.flush(force=True)
    assert len(events) == 0


def test_remote_config_validation():
    """Test RemoteConfig validation and edge cases."""
    # Valid config
    config = RemoteConfig(
        enabled=True,
        sampling_rate=0.5,
        buffer_size=50,
        flush_interval=15.0
    )
    
    assert config.enabled is True
    assert config.sampling_rate == 0.5
    
    # Test should_trace method with deterministic random values
    with patch('random.random', return_value=0.3):  # < 0.5, should pass sampling
        assert config.should_trace("any_tool") is True
    
    config.enabled = False
    with patch('random.random', return_value=0.3):
        assert config.should_trace("any_tool") is False
    
    config.enabled = True
    config.excluded_tools = ["excluded"]
    with patch('random.random', return_value=0.3):
        assert config.should_trace("excluded") is False
        assert config.should_trace("allowed") is True


def test_file_overwrite_behavior():
    """Test that file writing overwrites previous content."""
    file_path = "test_output/events.json"
    
    manager = TraceManager(file_path=file_path)
    
    # First batch of events
    trace_id1 = manager.start_trace("tool1")
    manager.end_trace(trace_id1, success=True)
    manager.flush()
    time.sleep(0.1)
    
    # Verify first event
    with open(file_path, 'r') as f:
        events = json.load(f)
    assert len(events) == 1
    assert events[0]['tool_name'] == 'tool1'
    
    # Second batch of events (should overwrite)
    trace_id2 = manager.start_trace("tool2")
    trace_id3 = manager.start_trace("tool3")
    manager.end_trace(trace_id2, success=True)
    manager.end_trace(trace_id3, success=True)
    manager.flush()
    time.sleep(0.1)
    
    # Verify file was overwritten with new events
    with open(file_path, 'r') as f:
        events = json.load(f)
    assert len(events) == 2
    tool_names = [e['tool_name'] for e in events]
    assert 'tool2' in tool_names
    assert 'tool3' in tool_names
    assert 'tool1' not in tool_names  # Should be overwritten
    
    print(f"\n📁 Test created overwrite test file: {file_path} (not cleaned up for inspection)") 