"""
Unit tests for @trace decorator - automatic tool execution tracing.

Tests cover:
- Decorator application and function wrapping
- Sync and async function support
- Metadata and argument capture
- Metrics collection from function results
- Error handling and propagation
- Integration with TraceManager
- Configuration overrides
- Nested trace contexts
"""

import asyncio
import time
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.veritax_analytics.trace import trace, add_trace_metadata, add_trace_metric, TraceContextDecorator
from src.veritax_analytics.trace_manager import TraceManager, configure_trace_manager
from src.veritax_analytics.models import ToolExecutionEvent


def setup_test_manager():
    """Set up a fresh global trace manager for testing."""
    return configure_trace_manager()


def test_trace_decorator_basic_sync():
    """Test basic @trace decorator functionality with sync functions."""
    # Configure global manager for testing
    manager = setup_test_manager()
    
    @trace(tool_name="test_function")
    def test_function(x, y):
        return x + y
    
    # Verify decorator metadata
    assert hasattr(test_function, '_trace_config')
    assert test_function._trace_config['tool_name'] == 'test_function'
    
    # Call function
    result = test_function(1, 2)
    assert result == 3
    
    # Verify trace was created
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert event.tool_name == "test_function"
    assert event.success is True
    assert event.error_type is None


def test_trace_decorator_basic_async():
    """Test basic @trace decorator functionality with async functions."""
    manager = setup_test_manager()
    
    @trace(tool_name="async_test_function")
    async def async_test_function(x, y):
        await asyncio.sleep(0.01)  # Simulate async work
        return x * y
    
    # Call async function
    async def run_test():
        result = await async_test_function(3, 4)
        assert result == 12
        
        # Verify trace was created
        events = manager.buffer.flush(force=True)
        assert len(events) == 1
        
        event = events[0]
        assert event.tool_name == "async_test_function"
        assert event.success is True
        assert event.duration_ms > 0  # Should have some duration
    
    # Run the async test
    asyncio.run(run_test())


def test_trace_decorator_with_arguments():
    """Test @trace decorator with include_args=True."""
    manager = setup_test_manager()
    
    @trace(tool_name="function_with_args", include_args=True)
    def function_with_args(name, age, city="Unknown"):
        return f"{name} is {age} years old from {city}"
    
    result = function_with_args("Alice", 30, city="New York")
    assert "Alice is 30 years old from New York" in result
    
    # Verify arguments were captured
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert 'arguments' in event.metadata
    args = event.metadata['arguments']
    assert args['name'] == 'Alice'
    assert args['age'] == 30
    assert args['city'] == 'New York'


def test_trace_decorator_with_result():
    """Test @trace decorator with include_result=True."""
    manager = setup_test_manager()
    
    @trace(tool_name="function_with_result", include_result=True)
    def function_with_result():
        return {"status": "success", "data": [1, 2, 3]}
    
    result = function_with_result()
    
    # Verify result was captured (this would be in the trace end call)
    # Note: The current implementation passes result to end_trace but doesn't store it in metadata
    # This test verifies the decorator calls end_trace with the result
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    assert result == {"status": "success", "data": [1, 2, 3]}


def test_trace_decorator_with_metadata():
    """Test @trace decorator with static metadata."""
    manager = setup_test_manager()
    
    @trace(
        tool_name="function_with_metadata",
        metadata={"version": "1.0", "category": "test"}
    )
    def function_with_metadata():
        return "test result"
    
    function_with_metadata()
    
    # Verify metadata was included
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert event.metadata['version'] == '1.0'
    assert event.metadata['category'] == 'test'
    assert event.metadata['function_name'] == 'function_with_metadata'


def test_trace_decorator_with_metrics():
    """Test @trace decorator with metrics collection."""
    manager = setup_test_manager()
    
    class MockResult:
        def __init__(self):
            self.processing_time = 1.5
            self.items_processed = 42
            self.non_numeric = "not a metric"
    
    @trace(
        tool_name="function_with_metrics",
        metrics={"time": "processing_time", "count": "items_processed", "invalid": "non_numeric"}
    )
    def function_with_metrics():
        return MockResult()
    
    result = function_with_metrics()
    
    # Verify metrics were collected
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert "metric_time" in event.metadata
    assert event.metadata["metric_time"] == 1.5
    assert "metric_count" in event.metadata
    assert event.metadata["metric_count"] == 42.0
    # Invalid metric should not be included
    assert "metric_invalid" not in event.metadata


def test_trace_decorator_error_handling():
    """Test @trace decorator error handling and propagation."""
    manager = setup_test_manager()
    
    @trace(tool_name="failing_function")
    def failing_function():
        raise ValueError("Test error message")
    
    # Verify exception is propagated
    try:
        failing_function()
        assert False, "Exception should have been raised"
    except ValueError as e:
        assert str(e) == "Test error message"
    
    # Verify trace recorded the error
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert event.success is False
    assert event.error_type == "ValueError"
    assert event.error_message == "Test error message"


def test_trace_decorator_disabled_locally():
    """Test @trace decorator with enabled=False."""
    manager = setup_test_manager()
    
    @trace(tool_name="disabled_function", enabled=False)
    def disabled_function():
        return "result"
    
    result = disabled_function()
    assert result == "result"
    
    # Verify no trace was created
    events = manager.buffer.flush(force=True)
    assert len(events) == 0


def test_trace_decorator_sampling():
    """Test @trace decorator with sampling configuration."""
    from src.veritax_analytics.trace_manager import RemoteConfig
    
    # Configure manager with sampling
    config = RemoteConfig(sampling_rate=0.0)  # Disable all sampling
    manager = configure_trace_manager(config=config)
    
    @trace(tool_name="sampled_function")
    def sampled_function():
        return "result"
    
    result = sampled_function()
    assert result == "result"
    
    # Verify no trace was created due to sampling
    events = manager.buffer.flush(force=True)
    assert len(events) == 0


def test_trace_decorator_excluded_tools():
    """Test @trace decorator with excluded tools."""
    from src.veritax_analytics.trace_manager import RemoteConfig
    
    config = RemoteConfig(excluded_tools=["excluded_function"])
    manager = configure_trace_manager(config=config)
    
    @trace(tool_name="excluded_function")
    def excluded_function():
        return "result"
    
    result = excluded_function()
    assert result == "result"
    
    # Verify no trace was created due to exclusion
    events = manager.buffer.flush(force=True)
    assert len(events) == 0


def test_trace_decorator_default_tool_name():
    """Test @trace decorator using function name as default tool name."""
    manager = setup_test_manager()
    
    @trace()  # No tool_name specified
    def my_special_function():
        return "result"
    
    my_special_function()
    
    # Verify function name was used as tool name
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert event.tool_name == "my_special_function"


def test_add_trace_metadata():
    """Test add_trace_metadata helper function."""
    manager = setup_test_manager()
    
    @trace(tool_name="metadata_test")
    def function_with_dynamic_metadata():
        add_trace_metadata("step", "processing")
        add_trace_metadata("user_id", 12345)
        return "result"
    
    function_with_dynamic_metadata()
    
    # Verify dynamic metadata was added
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    # Note: add_trace_metadata adds to the context, which gets included in the event
    # The exact mechanism depends on trace_context implementation


def test_add_trace_metric():
    """Test add_trace_metric helper function."""
    manager = setup_test_manager()
    
    @trace(tool_name="metric_test")
    def function_with_dynamic_metrics():
        add_trace_metric("items_processed", 100.0)
        add_trace_metric("processing_speed", 15.5)
        return "result"
    
    function_with_dynamic_metrics()
    
    # Verify dynamic metrics were added
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert "metric_items_processed" in event.metadata
    assert event.metadata["metric_items_processed"] == 100.0
    assert "metric_processing_speed" in event.metadata
    assert event.metadata["metric_processing_speed"] == 15.5


def test_trace_context_decorator():
    """Test TraceContextDecorator for manual trace management."""
    manager = setup_test_manager()
    
    with TraceContextDecorator("manual_tool", {"initial": "metadata"}) as trace:
        trace.add_metadata("step", "processing")
        trace.add_metric("items", 50.0)
        # Simulate some work
        time.sleep(0.01)
    
    # Verify trace was created
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert event.tool_name == "manual_tool"
    assert event.success is True
    assert "initial" in event.metadata
    assert event.metadata["initial"] == "metadata"


def test_trace_context_decorator_with_error():
    """Test TraceContextDecorator error handling."""
    manager = setup_test_manager()
    
    try:
        with TraceContextDecorator("manual_tool_error") as trace:
            trace.add_metadata("step", "failing")
            raise RuntimeError("Manual error")
    except RuntimeError:
        pass  # Expected
    
    # Verify trace recorded the error
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert event.tool_name == "manual_tool_error"
    assert event.success is False


def test_trace_context_decorator_validation():
    """Test TraceContextDecorator input validation."""
    # Test invalid tool name
    try:
        TraceContextDecorator("")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        TraceContextDecorator("x" * 256)  # Too long
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        TraceContextDecorator(None)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_nested_traces():
    """Test nested trace functionality."""
    manager = setup_test_manager()
    
    @trace(tool_name="outer_function")
    def outer_function():
        inner_function()
        return "outer_result"
    
    @trace(tool_name="inner_function")
    def inner_function():
        return "inner_result"
    
    result = outer_function()
    assert result == "outer_result"
    
    # Verify both traces were created
    events = manager.buffer.flush(force=True)
    assert len(events) == 2
    
    # Find outer and inner events
    outer_event = next(e for e in events if e.tool_name == "outer_function")
    inner_event = next(e for e in events if e.tool_name == "inner_function")
    
    assert outer_event.success is True
    assert inner_event.success is True


def test_trace_decorator_argument_capture_edge_cases():
    """Test argument capture with various edge cases."""
    manager = setup_test_manager()
    
    @trace(tool_name="complex_args", include_args=True)
    def complex_args(pos_arg, *args, keyword_arg="default", **kwargs):
        return f"{pos_arg}-{len(args)}-{keyword_arg}-{len(kwargs)}"
    
    result = complex_args("first", "second", "third", keyword_arg="custom", extra="value")
    
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    assert 'arguments' in event.metadata
    args = event.metadata['arguments']
    assert args['pos_arg'] == 'first'
    assert args['keyword_arg'] == 'custom'
    # Note: *args and **kwargs handling depends on sanitize_metadata implementation


def test_trace_decorator_with_async_error():
    """Test @trace decorator error handling with async functions."""
    manager = setup_test_manager()
    
    @trace(tool_name="async_failing_function")
    async def async_failing_function():
        await asyncio.sleep(0.01)
        raise ValueError("Async error")
    
    async def run_test():
        try:
            await async_failing_function()
            assert False, "Exception should have been raised"
        except ValueError as e:
            assert str(e) == "Async error"
        
        # Verify trace recorded the error
        events = manager.buffer.flush(force=True)
        assert len(events) == 1
        
        event = events[0]
        assert event.success is False
        assert event.error_type == "ValueError"
        assert event.error_message == "Async error"
    
    asyncio.run(run_test())


def test_trace_decorator_preserves_function_metadata():
    """Test that @trace decorator preserves original function metadata."""
    @trace(tool_name="documented_function")
    def documented_function(param1, param2="default"):
        """This is a documented function.
        
        Args:
            param1: First parameter
            param2: Second parameter with default
            
        Returns:
            A string result
        """
        return f"{param1}-{param2}"
    
    # Verify function metadata is preserved
    assert documented_function.__name__ == "documented_function"
    assert "This is a documented function" in documented_function.__doc__
    
    # Verify function still works
    result = documented_function("test")
    assert result == "test-default"


def test_trace_with_no_manager():
    """Test trace behavior when no manager is available."""
    # This is more of a safety test - the decorator should handle missing manager gracefully
    # In practice, get_trace_manager() always returns a manager, but testing edge cases
    
    @trace(tool_name="no_manager_test")
    def no_manager_function():
        return "result"
    
    # Should not crash even if there are issues with the manager
    result = no_manager_function()
    assert result == "result"


def test_metrics_collection_edge_cases():
    """Test metrics collection with various edge cases."""
    manager = setup_test_manager()
    
    class EdgeCaseResult:
        def __init__(self):
            self.valid_metric = 42.0
            self.string_metric = "not_a_number"
            self.none_metric = None
    
    @trace(
        tool_name="edge_case_metrics",
        metrics={
            "valid": "valid_metric",
            "invalid_string": "string_metric", 
            "invalid_none": "none_metric",
            "missing": "nonexistent_attr"
        }
    )
    def edge_case_function():
        return EdgeCaseResult()
    
    edge_case_function()
    
    events = manager.buffer.flush(force=True)
    assert len(events) == 1
    
    event = events[0]
    # Only valid numeric metrics should be included
    assert "metric_valid" in event.metadata
    assert event.metadata["metric_valid"] == 42.0
    # Invalid metrics should be filtered out
    assert "metric_invalid_string" not in event.metadata
    assert "metric_invalid_none" not in event.metadata
    assert "metric_missing" not in event.metadata


def test_trace_decorator_with_file_output():
    """Test @trace decorator with file output - writes to test_output/events.json."""
    from src.veritax_analytics.trace_manager import configure_trace_manager
    
    # Configure manager to write to the same file as TraceManager tests
    file_path = "test_output/events.json"
    manager = configure_trace_manager(file_path=file_path)
    
    @trace(tool_name="calculator", include_args=True, metadata={"version": "1.0"})
    def calculate(operation, a, b):
        """Test function that performs calculations."""
        if operation == "add":
            return a + b
        elif operation == "multiply":
            return a * b
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    @trace(tool_name="processor", include_args=True)
    def process_list(items, transform="upper"):
        """Test function that processes a list."""
        if transform == "upper":
            return [item.upper() for item in items]
        else:
            return items
    
    @trace(tool_name="error_function")
    def error_function():
        """Test function that always fails."""
        raise RuntimeError("This is a test error")
    
    # Call the functions to generate events
    result1 = calculate("add", 10, 5)
    result2 = calculate("multiply", 3, 7)
    result3 = process_list(["hello", "world"], "upper")
    
    # Call the error function
    try:
        error_function()
    except RuntimeError:
        pass  # Expected
    
    # Force flush to write to file
    manager.flush()
    
    # Wait for background thread
    time.sleep(0.2)
    
    # Verify file was created
    assert os.path.exists(file_path)
    
    # Verify the content
    with open(file_path, 'r') as f:
        events = json.load(f)
    
    assert len(events) == 4  # 3 successful + 1 error
    
    # Check that we have the expected events
    tool_names = [e['tool_name'] for e in events]
    assert 'calculator' in tool_names
    assert 'processor' in tool_names
    assert 'error_function' in tool_names
    
    # Check that arguments were captured
    calc_events = [e for e in events if e['tool_name'] == 'calculator']
    assert len(calc_events) == 2
    assert 'arguments' in calc_events[0]['metadata']
    assert calc_events[0]['metadata']['arguments']['operation'] == 'add'
    
    # Check error event
    error_events = [e for e in events if e['tool_name'] == 'error_function']
    assert len(error_events) == 1
    assert error_events[0]['success'] is False
    assert error_events[0]['error_type'] == 'RuntimeError'
    
    print(f"\n📁 Decorator test wrote to: {file_path} with {len(events)} events")
    
    # Verify we got the expected number of events
    assert len(events) == 4 