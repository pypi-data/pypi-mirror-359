#!/bin/bash

# Veritax Analytics - Project Structure Setup Script
# This script creates the project directory structure and initial files

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

# Function to create project directory structure
create_project_structure() {
    print_header "Creating Project Structure"
    
    # Create directory structure and SDK distribution model
    mkdir -p ~/veritax_analytics/src/veritax_analytics/tests
    mkdir -p ~/veritax_analytics/infrastructure/ingestion_api
    mkdir -p ~/veritax_analytics/infrastructure/data_processor
    mkdir -p ~/veritax_analytics/infrastructure/monitoring
    mkdir -p ~/veritax_analytics/deploy/cloud_run
    mkdir -p ~/veritax_analytics/deploy/cloud_function
    mkdir -p ~/veritax_analytics/deploy/terraform
    mkdir -p ~/veritax_analytics/tests/unit
    mkdir -p ~/veritax_analytics/tests/integration
    mkdir -p ~/veritax_analytics/tests/e2e
    mkdir -p ~/veritax_analytics/examples/basic_usage
    mkdir -p ~/veritax_analytics/examples/mcp_server_integration
    mkdir -p ~/veritax_analytics/scripts
    mkdir -p ~/veritax_analytics/config/dev
    mkdir -p ~/veritax_analytics/config/staging
    mkdir -p ~/veritax_analytics/config/prod
    mkdir -p ~/veritax_analytics/schema/bigquery
    mkdir -p ~/veritax_analytics/schema/migrations
    
    print_success "Directory structure created"
}

# Function to create SDK package structure
create_sdk_structure() {
    print_header "Creating SDK Package Structure"
    
    # Create initial package structure for the shipped SDK
    cat > ~/veritax_analytics/src/veritax_analytics/__init__.py << 'EOF'
"""
Veritax Analytics SDK - Cloud-agnostic analytics for MCP servers
"""

from .client import AnalyticsSDK
from .models import AnalyticsEvent, Configuration

__version__ = "1.0.0"
__all__ = ["AnalyticsSDK", "AnalyticsEvent", "Configuration"]
EOF

    # Create placeholder files for SDK components
    touch ~/veritax_analytics/src/veritax_analytics/{client.py,models.py,transport.py,exceptions.py}
    
    print_success "SDK package structure created"
}

# Function to create documentation files
create_documentation() {
    print_header "Creating Documentation Files"
    
    # Main README
    cat > ~/veritax_analytics/README.md << 'EOF'
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
EOF
    
    # Infrastructure README
    cat > ~/veritax_analytics/infrastructure/README.md << 'EOF'
# Veritax Analytics Infrastructure

Internal backend services for the Veritax Analytics platform.

## Components

- `ingestion_api/` - Cloud Run service for event ingestion
- `data_processor/` - Cloud Function for data processing
- `monitoring/` - Monitoring and alerting configurations

## Architecture

SDK → Ingestion API (Cloud Run) → Pub/Sub → Cloud Function → BigQuery

These components are internal infrastructure and are NOT part of the shipped SDK package.
EOF
    
    # Examples README
    cat > ~/veritax_analytics/examples/README.md << 'EOF'
# Veritax Analytics Examples

Example integrations and usage patterns for the Veritax Analytics SDK.

## Examples

- `basic_usage/` - Simple SDK usage examples
- `mcp_server_integration/` - Full MCP server integration examples

These examples demonstrate how MCP server developers can integrate analytics tracking.
EOF
    
    print_success "Documentation files created"
}

# Function to create configuration templates
create_config_templates() {
    print_header "Creating Configuration Templates"
    
    # Environment configuration template
    cat > ~/veritax_analytics/.env.example << 'EOF'
# Veritax Analytics Configuration Template
# Copy this file to .env and fill in your specific values

# GCP Configuration (from setup_gcp_infrastructure.sh)
GOOGLE_CLOUD_PROJECT=your-project-id
REGION=us-central1
PUBSUB_TOPIC=mcp-analytics-events
PUBSUB_DLQ_TOPIC=mcp-analytics-dlq
BIGQUERY_DATASET=mcp_analytics
API_KEY_SECRET_NAME=mcp-analytics-api-keys

# SDK Configuration
MCP_ANALYTICS_API_KEY=your-generated-api-key
INGESTION_ENDPOINT=https://mcp-analytics-ingestion-XXXXXXXX.run.app/v1/events

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF

    # Development configuration
    cat > ~/veritax_analytics/config/dev/config.yaml << 'EOF'
# Development Environment Configuration
environment: development
debug: true
log_level: DEBUG

sdk:
  batch_size: 10
  flush_interval: 5
  retry_attempts: 3

infrastructure:
  ingestion_api:
    memory: 512Mi
    cpu: 1000m
    min_instances: 0
    max_instances: 10
  
  data_processor:
    memory: 256Mi
    timeout: 60s
    max_instances: 100
EOF

    # Staging configuration
    cat > ~/veritax_analytics/config/staging/config.yaml << 'EOF'
# Staging Environment Configuration
environment: staging
debug: false
log_level: INFO

sdk:
  batch_size: 50
  flush_interval: 30
  retry_attempts: 5

infrastructure:
  ingestion_api:
    memory: 1Gi
    cpu: 1000m
    min_instances: 1
    max_instances: 50
  
  data_processor:
    memory: 512Mi
    timeout: 120s
    max_instances: 500
EOF

    # Production configuration
    cat > ~/veritax_analytics/config/prod/config.yaml << 'EOF'
# Production Environment Configuration
environment: production
debug: false
log_level: WARNING

sdk:
  batch_size: 100
  flush_interval: 60
  retry_attempts: 5

infrastructure:
  ingestion_api:
    memory: 2Gi
    cpu: 2000m
    min_instances: 2
    max_instances: 100
  
  data_processor:
    memory: 1Gi
    timeout: 300s
    max_instances: 1000
EOF
    
    print_success "Configuration templates created"
}

# Function to create schema files
create_schema_files() {
    print_header "Creating Schema Files"
    
    # BigQuery schema
    cat > ~/veritax_analytics/schema/bigquery/analytics_schema.sql << 'EOF'
-- Veritax Analytics BigQuery Schema
-- This file defines the complete schema for analytics data

-- Tool execution events table
CREATE TABLE IF NOT EXISTS `mcp_analytics.tool_events` (
  event_id STRING NOT NULL,
  ingestion_timestamp TIMESTAMP NOT NULL,
  server_id STRING NOT NULL,
  tool_name STRING NOT NULL,
  execution_start_time TIMESTAMP,
  execution_end_time TIMESTAMP,
  duration_ms INTEGER,
  success BOOLEAN NOT NULL,
  error_type STRING,
  error_message STRING,
  user_agent STRING,
  sdk_version STRING,
  api_key_hash STRING NOT NULL,
  metadata JSON
);

-- Server health metrics table
CREATE TABLE IF NOT EXISTS `mcp_analytics.server_health` (
  server_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  cpu_usage_percent FLOAT64,
  memory_usage_mb INTEGER,
  active_connections INTEGER,
  requests_per_minute INTEGER,
  api_key_hash STRING NOT NULL
);

-- Ingestion logs table
CREATE TABLE IF NOT EXISTS `mcp_analytics.ingestion_logs` (
  log_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  level STRING NOT NULL,
  component STRING NOT NULL,
  message STRING NOT NULL,
  metadata JSON
);
EOF
    
    print_success "Schema files created"
}

# Function to display structure summary
display_structure_summary() {
    print_header "Project Structure Setup Complete!"
    
    echo -e "${GREEN}✅ Directory structure created${NC}"
    echo -e "${GREEN}✅ SDK package structure initialized${NC}"
    echo -e "${GREEN}✅ Documentation files created${NC}"
    echo -e "${GREEN}✅ Configuration templates created${NC}"
    echo -e "${GREEN}✅ Schema files created${NC}"
    
    print_header "Project Structure Ready"
    
    echo "Project location: ~/veritax_analytics/"
    echo
    echo "Key directories:"
    echo "  • src/veritax_analytics/     - Shipped SDK package"
    echo "  • infrastructure/            - Internal backend services"
    echo "  • deploy/                    - Deployment configurations"
    echo "  • tests/                     - Test suites"
    echo "  • examples/                  - Usage examples"
    echo "  • config/                    - Environment configs"
    echo
    echo "Next steps:"
    echo "1. Copy GCP config: source ~/veritax_analytics/.gcp_config"
    echo "2. Create .env: cp .env.example .env"
    echo "3. Start development per pyproject.toml"
    
    print_success "Project structure setup completed successfully!"
}

# Main execution function
main() {
    print_header "Veritax Analytics - Project Structure Setup"
    echo "This script creates the project directory structure and initial files"
    echo "Optimized for development workflow and SDK distribution"
    echo
    
    create_project_structure
    create_sdk_structure
    create_documentation
    create_config_templates
    create_schema_files
    display_structure_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
