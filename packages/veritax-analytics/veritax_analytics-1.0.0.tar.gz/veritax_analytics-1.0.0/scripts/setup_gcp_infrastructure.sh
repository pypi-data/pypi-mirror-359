#!/bin/bash

# Veritax Analytics - GCP Infrastructure Setup Script
# This script sets up Google Cloud Platform resources for MCP Analytics pipeline

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_PREFIX="veritaxanalytics"
DEFAULT_PROJECT_ID="${PROJECT_PREFIX}"
REGION="us-central1"
ZONE="us-central1-a"

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

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first:"
        echo "  https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if user is authenticated - using more robust method
    if ! gcloud auth list 2>/dev/null | grep -q "ACTIVE"; then
        print_error "Not authenticated with gcloud. Please run:"
        echo "  gcloud auth login"
        exit 1
    fi
    
    # Alternative check: try to get current account
    CURRENT_ACCOUNT=$(gcloud config get-value account 2>/dev/null)
    if [ -z "$CURRENT_ACCOUNT" ]; then
        print_error "No active gcloud account found. Please run:"
        echo "  gcloud auth login"
        exit 1
    fi
    
    print_success "Authenticated as: $CURRENT_ACCOUNT"
    
    # Check if bq command is available
    if ! command -v bq &> /dev/null; then
        print_error "BigQuery CLI (bq) is not available. Please ensure gcloud is properly installed."
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Function to get user input with defaults
get_project_config() {
    print_header "Project Configuration"
    
    echo "Please provide the following configuration:"
    echo
    
    # Project ID
    read -p "Enter GCP Project ID (default: ${DEFAULT_PROJECT_ID}): " PROJECT_ID
    PROJECT_ID=${PROJECT_ID:-$DEFAULT_PROJECT_ID}
    
    # Region
    read -p "Enter GCP Region (default: ${REGION}): " USER_REGION
    REGION=${USER_REGION:-$REGION}
    
    # Billing account (if creating new project)
    read -p "Do you want to create a new project? (y/n, default: n): " CREATE_PROJECT
    CREATE_PROJECT=${CREATE_PROJECT:-n}
    
    if [[ "$CREATE_PROJECT" =~ ^[Yy]$ ]]; then
        read -p "Enter Billing Account ID (required for new project): " BILLING_ACCOUNT
        if [ -z "$BILLING_ACCOUNT" ]; then
            print_error "Billing Account ID is required for creating a new project"
            exit 1
        fi
    fi
    
    echo
    print_status "Configuration:"
    echo "  Project ID: ${PROJECT_ID}"
    echo "  Region: ${REGION}"
    echo "  Create Project: ${CREATE_PROJECT}"
    if [[ "$CREATE_PROJECT" =~ ^[Yy]$ ]]; then
        echo "  Billing Account: ${BILLING_ACCOUNT}"
    fi
    echo
    
    read -p "Continue with this configuration? (y/n): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled by user"
        exit 1
    fi
}

# Function to create or configure project
setup_project() {
    print_header "Setting up GCP Project"
    
    if [[ "$CREATE_PROJECT" =~ ^[Yy]$ ]]; then
        print_status "Creating new project: ${PROJECT_ID}"
        
        # Create project
        gcloud projects create "$PROJECT_ID" --name="Veritax Analytics" || {
            print_error "Failed to create project. It might already exist."
            exit 1
        }
        
        # Link billing account
        print_status "Linking billing account..."
        gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT" || {
            print_error "Failed to link billing account"
            exit 1
        }
        
        print_success "Project created and billing linked"
    else
        print_status "Using existing project: ${PROJECT_ID}"
    fi
    
    # Set active project
    gcloud config set project "$PROJECT_ID"
    print_success "Active project set to: ${PROJECT_ID}"
}

# Function to enable required APIs
enable_apis() {
    print_header "Enabling Required APIs"
    
    APIs=(
        "cloudbuild.googleapis.com"
        "pubsub.googleapis.com"
        "bigquery.googleapis.com"
        "run.googleapis.com"
        "cloudfunctions.googleapis.com"
        "secretmanager.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    print_status "Enabling APIs (this may take a few minutes)..."
    
    for api in "${APIs[@]}"; do
        print_status "Enabling ${api}..."
        gcloud services enable "$api"
    done
    
    print_success "All APIs enabled successfully"
}

# Function to create Pub/Sub resources
create_pubsub() {
    print_header "Creating Pub/Sub Resources"
    
    # Create main topic
    print_status "Creating topic: mcp-analytics-events"
    gcloud pubsub topics create mcp-analytics-events || {
        print_warning "Topic mcp-analytics-events might already exist"
    }
    
    # Create dead letter topic
    print_status "Creating dead letter topic: mcp-analytics-dlq"
    gcloud pubsub topics create mcp-analytics-dlq || {
        print_warning "Topic mcp-analytics-dlq might already exist"
    }
    
    # Create subscription
    print_status "Creating subscription: process-analytics-events"
    gcloud pubsub subscriptions create process-analytics-events \
        --topic=mcp-analytics-events \
        --ack-deadline=600 \
        --message-retention-duration=7d \
        --dead-letter-topic=mcp-analytics-dlq \
        --max-delivery-attempts=5 || {
        print_warning "Subscription process-analytics-events might already exist"
    }
    
    print_success "Pub/Sub resources created"
}

# Function to create BigQuery resources
create_bigquery() {
    print_header "Creating BigQuery Resources"
    
    # Create dataset
    print_status "Creating BigQuery dataset: mcp_analytics"
    bq mk --dataset "${PROJECT_ID}:mcp_analytics" || {
        print_warning "Dataset mcp_analytics might already exist"
    }
    
    # Create tool_events table
    print_status "Creating table: tool_events"
    bq mk --table \
        "${PROJECT_ID}:mcp_analytics.tool_events" \
        "event_id:STRING,ingestion_timestamp:TIMESTAMP,server_id:STRING,tool_name:STRING,execution_start_time:TIMESTAMP,execution_end_time:TIMESTAMP,duration_ms:INTEGER,success:BOOLEAN,error_type:STRING,error_message:STRING,user_agent:STRING,sdk_version:STRING,api_key_hash:STRING,metadata:JSON" || {
        print_warning "Table tool_events might already exist"
    }
    
    # Create server_health table
    print_status "Creating table: server_health"
    bq mk --table \
        "${PROJECT_ID}:mcp_analytics.server_health" \
        "server_id:STRING,timestamp:TIMESTAMP,cpu_usage_percent:FLOAT64,memory_usage_mb:INTEGER,active_connections:INTEGER,requests_per_minute:INTEGER,api_key_hash:STRING" || {
        print_warning "Table server_health might already exist"
    }
    
    # Create ingestion_logs table
    print_status "Creating table: ingestion_logs"
    bq mk --table \
        "${PROJECT_ID}:mcp_analytics.ingestion_logs" \
        "log_id:STRING,timestamp:TIMESTAMP,level:STRING,component:STRING,message:STRING,metadata:JSON" || {
        print_warning "Table ingestion_logs might already exist"
    }
    
    print_success "BigQuery resources created"
}

# Function to create service accounts and IAM
setup_iam() {
    print_header "Setting up Service Accounts and IAM"
    
    # Create service account for Cloud Run
    print_status "Creating Cloud Run service account"
    gcloud iam service-accounts create mcp-analytics-ingestion \
        --display-name="MCP Analytics Ingestion Service" \
        --description="Service account for Cloud Run ingestion API" || {
        print_warning "Service account might already exist"
    }
    
    # Create service account for Cloud Function
    print_status "Creating Cloud Function service account"
    gcloud iam service-accounts create mcp-analytics-processor \
        --display-name="MCP Analytics Data Processor" \
        --description="Service account for data processing function" || {
        print_warning "Service account might already exist"
    }
    
    # Grant permissions to Cloud Run service account
    print_status "Granting permissions to Cloud Run service account"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:mcp-analytics-ingestion@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/pubsub.publisher"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:mcp-analytics-ingestion@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/logging.logWriter"
    
    # Grant permissions to Cloud Function service account
    print_status "Granting permissions to Cloud Function service account"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:mcp-analytics-processor@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/bigquery.dataEditor"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:mcp-analytics-processor@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/bigquery.jobUser"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:mcp-analytics-processor@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/pubsub.subscriber"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:mcp-analytics-processor@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/logging.logWriter"
    
    print_success "IAM configuration completed"
}

# Function to create sample API keys
create_api_keys() {
    print_header "Creating Sample API Keys"
    
    # Create secret for API keys
    print_status "Creating API key secret in Secret Manager"
    
    # Generate sample API keys
    SAMPLE_API_KEY=$(openssl rand -hex 32)
    
    echo "$SAMPLE_API_KEY" | gcloud secrets create mcp-analytics-api-keys \
        --data-file=- \
        --replication-policy="automatic" || {
        print_warning "Secret might already exist"
    }
    
    print_success "Sample API key created and stored in Secret Manager"
    print_warning "API Key: ${SAMPLE_API_KEY}"
    print_warning "Save this API key - you'll need it for SDK configuration"
    
    # Export for use by other scripts
    export MCP_ANALYTICS_API_KEY="$SAMPLE_API_KEY"
    export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
    export REGION="$REGION"
}

# Function to generate GCP configuration
generate_gcp_config() {
    print_header "Generating GCP Configuration"
    
    # Ensure the veritax_analytics directory exists
    if [ ! -d ~/veritax_analytics ]; then
        print_status "Creating ~/veritax_analytics directory for configuration..."
        mkdir -p ~/veritax_analytics
    fi
    
    # Create GCP-specific configuration
    cat > ~/veritax_analytics/.gcp_config << EOF
# GCP Infrastructure Configuration
GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
REGION=${REGION}
PUBSUB_TOPIC=mcp-analytics-events
PUBSUB_DLQ_TOPIC=mcp-analytics-dlq
BIGQUERY_DATASET=mcp_analytics
API_KEY_SECRET_NAME=mcp-analytics-api-keys
MCP_ANALYTICS_API_KEY=${SAMPLE_API_KEY}

# Service Accounts
INGESTION_SERVICE_ACCOUNT=mcp-analytics-ingestion@${PROJECT_ID}.iam.gserviceaccount.com
PROCESSOR_SERVICE_ACCOUNT=mcp-analytics-processor@${PROJECT_ID}.iam.gserviceaccount.com

# Generated on: $(date)
EOF
    
    print_success "GCP configuration saved to ~/veritax_analytics/.gcp_config"
}

# Function to display GCP summary
display_gcp_summary() {
    print_header "GCP Infrastructure Setup Complete!"
    
    echo -e "${GREEN}✅ GCP Project: ${PROJECT_ID}${NC}"
    echo -e "${GREEN}✅ Region: ${REGION}${NC}"
    echo -e "${GREEN}✅ Pub/Sub Topics: mcp-analytics-events, mcp-analytics-dlq${NC}"
    echo -e "${GREEN}✅ BigQuery Dataset: mcp_analytics${NC}"
    echo -e "${GREEN}✅ Service Accounts: Created with proper IAM roles${NC}"
    echo -e "${GREEN}✅ API Keys: Generated and stored in Secret Manager${NC}"
    
    print_header "GCP Resources Ready"
    
    echo "Configuration saved to: ~/veritax_analytics/.gcp_config"
    echo "API Key: ${SAMPLE_API_KEY}"
    echo
    echo "Verify setup:"
    echo "  gcloud pubsub topics list"
    echo "  bq ls ${PROJECT_ID}:mcp_analytics"
    echo "  gcloud iam service-accounts list"
    
    print_success "GCP infrastructure setup completed successfully!"
}

# Main execution function
main() {
    print_header "Veritax Analytics - GCP Infrastructure Setup"
    echo "This script sets up Google Cloud Platform resources for MCP Analytics"
    echo "Components: Pub/Sub, BigQuery, Service Accounts, Secret Manager"
    echo
    
    check_prerequisites
    get_project_config
    setup_project
    enable_apis
    create_pubsub
    create_bigquery
    setup_iam
    create_api_keys
    generate_gcp_config
    display_gcp_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
