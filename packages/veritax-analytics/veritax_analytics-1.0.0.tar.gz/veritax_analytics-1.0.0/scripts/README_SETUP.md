# Veritax Analytics - Week 1 Infrastructure Setup

This repository contains the automated setup script for the Veritax Analytics MCP (Model Context Protocol) infrastructure on Google Cloud Platform.

## Overview

The setup script automates the complete infrastructure provisioning based on our architecture:

```
SDK → Ingestion API (Cloud Run) → Pub/Sub → Cloud Function → BigQuery
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Billing Account ID** (if creating a new project)
4. **Appropriate permissions** to create projects and resources

### Installing gcloud CLI

**macOS:**
```bash
brew install google-cloud-sdk
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Authentication
```bash
# Login to your Google account
gcloud auth login

# Set up application default credentials
gcloud auth application-default login
```

## Quick Start

### Option 1: Google Cloud Shell (Recommended)

1. Open [Google Cloud Shell](https://shell.cloud.google.com)
2. Clone or download the setup script:
   ```bash
   curl -o setup_week1_infrastructure.sh https://raw.githubusercontent.com/your-repo/veritax_analytics/main/setup_week1_infrastructure.sh
   chmod +x setup_week1_infrastructure.sh
   ```
3. Run the setup:
   ```bash
   ./setup_week1_infrastructure.sh
   ```

### Option 2: Local Terminal

1. Ensure gcloud CLI is installed and authenticated
2. Download the setup script:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/veritax_analytics/main/setup_week1_infrastructure.sh
   chmod +x setup_week1_infrastructure.sh
   ```
3. Run the setup:
   ```bash
   ./setup_week1_infrastructure.sh
   ```

## What the Script Creates

### GCP Resources

1. **Project Configuration**
   - New GCP project (optional)
   - Billing account linkage
   - Required API enablement

2. **Pub/Sub Resources**
   - `mcp-analytics-events` topic
   - `mcp-analytics-dlq` dead letter topic
   - `process-analytics-events` subscription

3. **BigQuery Resources**
   - `mcp_analytics` dataset
   - `tool_events` table
   - `server_health` table
   - `ingestion_logs` table

4. **IAM & Security**
   - Service accounts for Cloud Run and Cloud Function
   - Proper IAM role assignments
   - API key generation and secret storage

5. **Project Structure**
   ```
   ~/veritax_analytics/
   ├── src/
   │   ├── analytics_sdk/
   │   ├── ingestion_api/
   │   └── data_processor/
   ├── deploy/
   │   ├── cloud_run/
   │   └── cloud_function/
   ├── tests/
   ├── examples/
   ├── terraform/
   └── schema/
   ```

## Configuration

The script generates several configuration files:

### `.env.example`
Contains all environment variables needed for development:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
PUBSUB_TOPIC=mcp-analytics-events
BIGQUERY_DATASET=mcp_analytics
# ... etc
```

### `deploy/config.yaml`
Deployment configuration for all services:
```yaml
project_id: your-project-id
region: us-central1
services:
  ingestion_api:
    name: mcp-analytics-ingestion
# ... etc
```

## Post-Setup Steps

After running the setup script:

1. **Set up development environment:**
   ```bash
   cd ~/veritax_analytics
   cp .env.example .env
   # Edit .env with your specific values
   ```

2. **Save the API key** (displayed in script output):
   ```bash
   export MCP_ANALYTICS_API_KEY='your-generated-api-key'
   ```

3. **Test the infrastructure:**
   ```bash
   # Test BigQuery access
   bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `your-project.mcp_analytics.tool_events`'
   
   # List Pub/Sub topics
   gcloud pubsub topics list
   
   # List BigQuery tables
   bq ls your-project:mcp_analytics
   ```

## Week 1 Development Timeline

With infrastructure ready, proceed with:

- **Day 4 (Wed)**: Develop cloud-agnostic Analytics SDK
- **Day 5 (Thu)**: Create Ingestion API (Cloud Run service)
- **Day 6 (Fri)**: Build Data Processor (Cloud Function)
- **Day 7 (Sat)**: End-to-end integration testing

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Check current user
   gcloud auth list
   
   # Check project permissions
   gcloud projects get-iam-policy PROJECT_ID
   ```

2. **API Not Enabled**
   ```bash
   # Check enabled APIs
   gcloud services list --enabled
   
   # Enable specific API
   gcloud services enable SERVICE_NAME
   ```

3. **Billing Issues**
   ```bash
   # Check billing account
   gcloud billing accounts list
   
   # Link billing account
   gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
   ```

4. **Resource Already Exists**
   - The script handles existing resources gracefully
   - Warnings are normal for pre-existing resources
   - Check output for any actual errors

### Verification Commands

```bash
# Verify project setup
gcloud config get-value project

# Check Pub/Sub resources
gcloud pubsub topics list
gcloud pubsub subscriptions list

# Check BigQuery resources
bq ls
bq ls PROJECT_ID:mcp_analytics

# Check service accounts
gcloud iam service-accounts list

# Check IAM policies
gcloud projects get-iam-policy PROJECT_ID
```

## Cost Estimation

Expected monthly costs for MVP usage (1M events/month):
- Cloud Run: $15-25
- Pub/Sub: $5-10
- Cloud Function: $5-10
- BigQuery Storage: $10-20
- BigQuery Queries: $20-40
- **Total: ~$55-105/month**

## Security Notes

- API keys are stored in Google Secret Manager
- Service accounts follow principle of least privilege
- All resources are configured with appropriate access controls
- Audit logging is enabled for compliance

## Support

For issues with the setup script:
1. Check the troubleshooting section above
2. Review Google Cloud Console for error details
3. Check Cloud Logging for detailed error messages
4. Consult Week 1 plan documentation

## Next Steps

After successful infrastructure setup:
1. ✅ GCP Infrastructure Complete
2. 🔄 Develop Analytics SDK (Day 4)
3. 🔄 Create Ingestion API (Day 5)  
4. 🔄 Build Data Processor (Day 6)
5. 🔄 End-to-end Testing (Day 7)

Ready to build the future of MCP Analytics! 🚀
