# Analytics SDK Design Specification

## Core Design Principles

1. **Complete Cloud Abstraction**: SDK has zero knowledge of GCP, AWS, or any cloud provider
2. **Simple Configuration**: Only endpoint URL, API key, and basic performance settings
3. **Reliable Delivery**: Built-in retry logic, batching, and error handling
4. **Developer Friendly**: Easy integration, minimal boilerplate, clear error messages
5. **Performance Optimized**: Async by default, configurable batching, minimal overhead

## Public SDK Interface

### Configuration
```python
from mcp_analytics import AnalyticsSDK

# Minimal configuration - only what users need to know
sdk = AnalyticsSDK(
    api_key="your-api-key",
    endpoint="https://your-analytics-api.run.app/v1/events",
    # Optional performance tuning
    batch_size=50,           # Events per batch
    flush_interval=30,       # Seconds between automatic flushes
    max_retries=3,          # Network retry attempts
    timeout=10,             # Request timeout in seconds
    # Optional identification
    server_id="my-weather-server",
    user_agent="MyMCPServer/1.0"
)
```

### Core Tracking Methods
```python
# Tool execution tracking
sdk.track_tool_execution(
    tool_name="get_forecast",
    duration_ms=150,
    success=True,
    metadata={"location": "Sacramento", "units": "metric"}
)

# Error tracking
sdk.track_tool_error(
    tool_name="get_forecast", 
    error_type="ValidationError",
    error_message="Invalid location format",
    duration_ms=50
)

# Server health metrics (optional)
sdk.track_server_health(
    cpu_usage=45.2,
    memory_mb=256,
    active_connections=3
)

# Custom events (extensible)
sdk.track_custom_event(
    event_type="server_start",
    metadata={"version": "1.2.3", "config": "production"}
)
```

### Lifecycle Management
```python
# Manual control
await sdk.flush()        # Send pending events immediately
await sdk.close()        # Graceful shutdown

# Context manager (recommended)
async with AnalyticsSDK(...) as sdk:
    sdk.track_tool_execution(...)
    # Automatic flush and cleanup on exit
```

## Internal SDK Architecture

### Component Structure
