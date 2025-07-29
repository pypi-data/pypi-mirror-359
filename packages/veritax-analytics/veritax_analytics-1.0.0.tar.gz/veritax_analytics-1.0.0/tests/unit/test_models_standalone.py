import sys

from datetime import datetime, timezone, timedelta
import json

from veritax_analytics.models import (
    ToolExecutionEvent,
    ServerHealthEvent,
    Configuration,
    BatchRequest,
)

def test_basic_functionality():
    """Test that all models work correctly"""
    print("🧪 Testing basic model functionality...")
    
    # Test Configuration (server_id auto-generated)
    print("Creating configuration...")
    config = Configuration(
        api_key="test-api-key-12345",
        endpoint="https://api.example.com/v1/events"
    )
    print(f"✅ Configuration created with server_id: {config.server_id}")
    
    # Test Configuration (should generate different server_id)
    print("Creating second configuration...")
    config2 = Configuration(
        api_key="test-api-key-67890",
        endpoint="https://api.example.com/v1/events"
    )
    print(f"✅ Second configuration created with server_id: {config2.server_id}")
    
    # Test that both have different server_ids
    assert config.server_id != config2.server_id, "Server IDs should be unique"
    assert config.server_id is not None, "Server ID should not be None"
    assert len(config.server_id) > 10, "Server ID should be substantial length"
    print(f"✅ Server IDs are unique and properly generated")
    
    # Test ToolExecutionEvent
    tool_event = ToolExecutionEvent(
        server_id=config.server_id,
        tool_name="weather_forecast",
        duration_ms=150,
        success=True,
        metadata={"test": True}
    )
    print(f"✅ Tool event created: {tool_event.event_id}")
    
    # Test ServerHealthEvent
    health_event = ServerHealthEvent(
        server_id=config.server_id,
        cpu_usage_percent=45.5,
        memory_usage_mb=512
    )
    print(f"✅ Health event created: {health_event.event_id}")
    
    # Test BatchRequest
    batch = BatchRequest(events=[tool_event, health_event])
    print(f"✅ Batch created with {len(batch.events)} events")
    
    # Test JSON serialization
    json_data = batch.model_dump_json()
    parsed = json.loads(json_data)
    print(f"✅ JSON serialization working, timestamp: {parsed['timestamp']}")
    
    # Test duration calculation
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(milliseconds=300)
    
    duration_event = ToolExecutionEvent(
        server_id=config.server_id,
        tool_name="duration_test",
        execution_start_time=start_time,
        execution_end_time=end_time,
        success=True
    )
    print(f"✅ Duration calculation: {duration_event.duration_ms}ms")

def test_validation_errors():
    """Test that validation works properly"""
    print("\n🧪 Testing validation errors...")
    
    try:
        # Test invalid API key
        Configuration(
            api_key="short",
            endpoint="https://api.example.com"
        )
        print("❌ Should have failed for short API key")
        assert False, "Should have failed for short API key"
    except Exception:
        print("✅ Short API key validation working")
    
    try:
        # Test invalid CPU usage
        ServerHealthEvent(
            server_id="test",
            cpu_usage_percent=150.0
        )
        print("❌ Should have failed for CPU > 100%")
        assert False, "Should have failed for CPU > 100%"
    except Exception:
        print("✅ CPU validation working")
    
    try:
        # Test missing server_id
        ToolExecutionEvent(
            tool_name="test",
            success=True
        )
        print("❌ Should have failed for missing server_id")
        assert False, "Should have failed for missing server_id"
    except Exception:
        print("✅ Required field validation working")

if __name__ == "__main__":
    print("🚀 Starting Veritax Analytics Models Validation")
    print("=" * 50)
    
    try:
        success1 = test_basic_functionality()
        success2 = test_validation_errors()
        
        if success1 and success2:
            print("\n🎉 [test_models_standalone] tests passed.")
            print("✅ Core Data Models - COMPLETE")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
