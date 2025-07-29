#!/bin/bash

# Veritax Analytics - Complete Setup Script
# This master script orchestrates the complete setup process

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

# Function to check if script exists and is executable
check_script() {
    local script_path="$1"
    local script_name="$2"
    
    if [ ! -f "$script_path" ]; then
        print_error "Script not found: $script_path"
        print_error "Please ensure all setup scripts are in the scripts/ directory"
        exit 1
    fi
    
    if [ ! -x "$script_path" ]; then
        print_status "Making $script_name executable..."
        chmod +x "$script_path"
    fi
    
    print_success "$script_name is ready"
}

# Function to run a script with error handling
run_script() {
    local script_path="$1"
    local script_name="$2"
    local description="$3"
    
    print_header "Running: $script_name"
    print_status "$description"
    
    if bash "$script_path"; then
        print_success "$script_name completed successfully"
    else
        print_error "$script_name failed with exit code $?"
        print_error "Setup process terminated"
        exit 1
    fi
    
    echo
}

# Function to get user confirmation for setup steps
get_setup_options() {
    print_header "Veritax Analytics - Complete Setup"
    echo "This script will run the complete setup process:"
    echo
    echo "1. GCP Infrastructure Setup (required)"
    echo "   - Creates GCP project, Pub/Sub, BigQuery, Service Accounts"
    echo "   - Generates API keys and configures IAM"
    echo
    echo "2. Project Structure Setup (required)"
    echo "   - Creates directory structure for SDK and infrastructure"
    echo "   - Generates configuration templates and documentation"
    echo
    echo "3. Verification (optional)"
    echo "   - Tests that all components are properly configured"
    echo
    
    read -p "Do you want to run the complete setup? (y/n): " RUN_COMPLETE
    if [[ ! "$RUN_COMPLETE" =~ ^[Yy]$ ]]; then
        print_status "You can run individual scripts manually:"
        echo "  • GCP Infrastructure: ./scripts/setup_gcp_infrastructure.sh"
        echo "  • Project Structure: ./scripts/setup_project_structure.sh"
        echo "  • Verification: ./scripts/verify_setup.sh"
        exit 0
    fi
    
    read -p "Run verification after setup? (y/n, default: y): " RUN_VERIFICATION
    RUN_VERIFICATION=${RUN_VERIFICATION:-y}
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if we're in the right directory
    if [ ! -d "scripts" ]; then
        print_error "Please run this script from the veritax_analytics root directory"
        print_error "Expected directory structure:"
        echo "  veritax_analytics/"
        echo "  └── scripts/"
        echo "      ├── setup_complete.sh"
        echo "      ├── setup_gcp_infrastructure.sh"
        echo "      └── setup_project_structure.sh"
        exit 1
    fi
    
    # Check that required scripts exist
    check_script "scripts/setup_gcp_infrastructure.sh" "GCP Infrastructure Setup"
    check_script "scripts/setup_project_structure.sh" "Project Structure Setup"
    
    if [[ "$RUN_VERIFICATION" =~ ^[Yy]$ ]]; then
        check_script "scripts/verify_setup.sh" "Verification Script"
    fi
    
    print_success "All prerequisites satisfied"
}

# Function to load configuration from previous steps
load_configuration() {
    print_header "Loading Configuration"
    
    # Check if GCP config exists from previous run
    if [ -f "~/veritax_analytics/.gcp_config" ]; then
        print_status "Found existing GCP configuration"
        source ~/veritax_analytics/.gcp_config
        print_status "Loaded configuration for project: $GOOGLE_CLOUD_PROJECT"
    else
        print_status "No existing configuration found - will create new setup"
    fi
}

# Function to create final configuration
create_final_configuration() {
    print_header "Creating Final Configuration"
    
    GCP_CONFIG_FILE="./.gcp_config"
    ENV_FILE="./.env"
    
    echo "Looking for config file: $GCP_CONFIG_FILE"
    echo "Will create env file: $ENV_FILE"
    
    if [ -f "$GCP_CONFIG_FILE" ]; then
        echo "Config file found, sourcing..."
        source "$GCP_CONFIG_FILE"
        
        # Create the final .env file in current directory
        cat > "$ENV_FILE" << EOF
# Veritax Analytics Configuration
# Generated by setup_complete.sh on $(date)

# GCP Configuration
GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
REGION=${REGION}
PUBSUB_TOPIC=${PUBSUB_TOPIC}
PUBSUB_DLQ_TOPIC=${PUBSUB_DLQ_TOPIC}
BIGQUERY_DATASET=${BIGQUERY_DATASET}
API_KEY_SECRET_NAME=${API_KEY_SECRET_NAME}

# SDK Configuration  
MCP_ANALYTICS_API_KEY=${MCP_ANALYTICS_API_KEY}
INGESTION_ENDPOINT=https://mcp-analytics-ingestion-\${GOOGLE_CLOUD_PROJECT}.run.app/v1/events

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF

        print_success "Final configuration created at $ENV_FILE"
        echo "File contents:"
        cat "$ENV_FILE"
    else
        print_warning "GCP configuration not found at: $GCP_CONFIG_FILE"
    fi
}

# Function to display final summary
display_final_summary() {
    print_header "🎉 Setup Complete!"
    
    echo -e "${GREEN}✅ GCP Infrastructure: Fully configured${NC}"
    echo -e "${GREEN}✅ Project Structure: Ready for development${NC}"
    echo -e "${GREEN}✅ Configuration: Generated and ready${NC}"
    
    if [[ "$RUN_VERIFICATION" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Verification: All tests passed${NC}"
    fi
    
    print_header "🚀 Ready for Development!"
    
    echo "Your Veritax Analytics project is ready! Here's what was set up:"
    echo
    echo "📁 Project Structure:"
    echo "   ~/veritax_analytics/"
    echo "   ├── src/veritax_analytics/      # Your SDK package"
    echo "   ├── infrastructure/             # Backend services"
    echo "   ├── deploy/                     # Deployment configs"
    echo "   ├── tests/                      # Test suites"
    echo "   └── scripts/                    # Setup and utility scripts"
    echo
    echo "☁️  GCP Resources:"
    if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
        echo "   Project: $GOOGLE_CLOUD_PROJECT"
        echo "   Region: $REGION"
        echo "   Pub/Sub: mcp-analytics-events"
        echo "   BigQuery: mcp_analytics dataset"
        echo "   API Key: $(echo $MCP_ANALYTICS_API_KEY | cut -c1-8)..."
    fi
    echo
    echo "🔧 Next Steps:"
    echo "1. Navigate to project: cd ~/veritax_analytics"
    echo "2. Start development:"
    echo "   • Day 4: Develop SDK (src/veritax_analytics/)"
    echo "   • Day 5: Create Ingestion API (infrastructure/ingestion_api/)"
    echo "   • Day 6: Build Data Processor (infrastructure/data_processor/)"
    echo "   • Day 7: End-to-end testing"
    echo
    echo "📚 Documentation:"
    echo "   • Main README: ~/veritax_analytics/README.md"
    echo "   • Infrastructure: ~/veritax_analytics/infrastructure/README.md"
    echo "   • Examples: ~/veritax_analytics/examples/README.md"
    echo
    echo "🔐 Important:"
    echo "   • API Key saved in: ~/veritax_analytics/.env"
    echo "   • GCP Config saved in: ~/veritax_analytics/.gcp_config"
    echo "   • Keep these files secure and never commit them"
    
    print_success "Happy coding!"
}

# Main execution function
main() {
    print_header "Veritax Analytics - Complete Setup Orchestrator"
    echo "This script runs the complete infrastructure and project setup"
    echo "Architecture: SDK → Cloud Run → Pub/Sub → Cloud Function → BigQuery"
    echo
    
    get_setup_options
    check_prerequisites
    load_configuration
    
    # Run GCP Infrastructure Setup
    run_script \
        "scripts/setup_gcp_infrastructure.sh" \
        "GCP Infrastructure Setup" \
        "Setting up Google Cloud Platform resources (Pub/Sub, BigQuery, IAM, etc.)"
    
    # Run Project Structure Setup
    run_script \
        "scripts/setup_project_structure.sh" \
        "Project Structure Setup" \
        "Creating project directories, templates, and initial files"
    
    # Create final configuration
    create_final_configuration
    
    # Run verification if requested
    if [[ "$RUN_VERIFICATION" =~ ^[Yy]$ ]]; then
        if [ -f "scripts/verify_setup.sh" ]; then
            run_script \
                "scripts/verify_setup.sh" \
                "Setup Verification" \
                "Verifying that all components are properly configured"
        else
            print_warning "Verification script not found - skipping verification"
        fi
    fi
    
    # Display final summary
    display_final_summary
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
