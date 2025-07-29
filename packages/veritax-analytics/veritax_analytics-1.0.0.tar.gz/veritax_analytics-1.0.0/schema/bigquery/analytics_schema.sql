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
