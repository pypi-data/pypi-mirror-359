# Veritax Analytics Infrastructure

Internal backend services for the Veritax Analytics platform.

## Components

- `ingestion_api/` - Cloud Run service for event ingestion
- `data_processor/` - Cloud Function for data processing
- `monitoring/` - Monitoring and alerting configurations

## Architecture

SDK → Ingestion API (Cloud Run) → Pub/Sub → Cloud Function → BigQuery

These components are internal infrastructure and are NOT part of the shipped SDK package.
