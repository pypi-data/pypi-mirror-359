# Veritax Analytics

Cloud-agnostic analytics SDK for Model Context Protocol (MCP) servers.

## Project Structure

- `src/veritax_analytics/` - Shipped SDK package (pip installable)
- `infrastructure/` - Internal backend services (not shipped)
- `deploy/` - Deployment configurations and scripts
- `tests/` - Test suites for all components
- `examples/` - Usage examples and integration guides
- `scripts/` - Development and deployment scripts
- `docs/` - Documentation
- `config/` - Environment-specific configurations
- `schema/` - Database schemas and migrations

## Quick Start

For SDK users:
```python
from veritax_analytics import AnalyticsSDK

analytics = AnalyticsSDK(
    api_key="your-api-key",
    endpoint="https://analytics.your-domain.com/v1/events"
)

analytics.track_tool_execution("weather_forecast", duration=150, success=True)
```

For infrastructure operators, see `infrastructure/README.md`.
