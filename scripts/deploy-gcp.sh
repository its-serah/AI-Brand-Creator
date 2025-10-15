#!/bin/bash

# AI Brand Creator GCP Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="brand-creator"
ARCHITECTURE=${1:-"mvp-monolith"}

echo -e "${BLUE}🚀 Starting AI Brand Creator GCP Deployment${NC}"
echo -e "${BLUE}Architecture: ${ARCHITECTURE}${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker${NC}"
        exit 1
    fi
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ GOOGLE_CLOUD_PROJECT not set${NC}"
        echo "Please set your project ID:"
        echo "export GOOGLE_CLOUD_PROJECT=your-project-id"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Setup GCP project and APIs
setup_project() {
    echo -e "${YELLOW}🔧 Setting up GCP project...${NC}"
    
    gcloud config set project $PROJECT_ID
    
    echo "Enabling required APIs..."
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        storage.googleapis.com \
        cloudtasks.googleapis.com \
        pubsub.googleapis.com \
        aiplatform.googleapis.com \
        container.googleapis.com \
        sqladmin.googleapis.com \
        redis.googleapis.com
    
    echo -e "${GREEN}✅ Project setup complete${NC}"
}

# Create storage buckets
create_storage() {
    echo -e "${YELLOW}💾 Creating storage buckets...${NC}"
    
    BUCKET_NAME="${PROJECT_ID}-brand-assets"
    MODEL_BUCKET="${PROJECT_ID}-ml-models"
    
    # Create buckets if they don't exist
    gsutil ls gs://$BUCKET_NAME &>/dev/null || gsutil mb gs://$BUCKET_NAME
    gsutil ls gs://$MODEL_BUCKET &>/dev/null || gsutil mb gs://$MODEL_BUCKET
    
    # Set proper CORS for web access
    cat > cors.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF
    
    gsutil cors set cors.json gs://$BUCKET_NAME
    rm cors.json
    
    echo -e "${GREEN}✅ Storage buckets created${NC}"
}

# Create service account
create_service_account() {
    echo -e "${YELLOW}🔑 Creating service account...${NC}"
    
    SA_NAME="brand-creator-sa"
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
        gcloud iam service-accounts create $SA_NAME \
            --description="AI Brand Creator service account" \
            --display-name="Brand Creator SA"
    fi
    
    # Grant necessary permissions
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/storage.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/cloudtasks.admin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/pubsub.admin"
        
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/cloudsql.client"
    
    echo -e "${GREEN}✅ Service account configured${NC}"
}

# Deploy based on architecture
deploy_architecture() {
    echo -e "${YELLOW}🏗️ Deploying ${ARCHITECTURE} architecture...${NC}"
    
    cd "architectures/${ARCHITECTURE}"
    
    case $ARCHITECTURE in
        "mvp-monolith")
            deploy_cloud_run
            ;;
        "queue-centric")
            deploy_queue_centric
            ;;
        "serverless")
            deploy_serverless
            ;;
        "microservices")
            deploy_microservices
            ;;
        *)
            echo -e "${RED}❌ Unknown architecture: ${ARCHITECTURE}${NC}"
            exit 1
            ;;
    esac
}

# Deploy MVP Monolith to Cloud Run
deploy_cloud_run() {
    echo -e "${YELLOW}☁️ Deploying to Cloud Run...${NC}"
    
    # Use the GCP-specific Dockerfile
    cp gcp/Dockerfile ./Dockerfile.gcp
    
    gcloud run deploy $SERVICE_NAME \
        --source . \
        --dockerfile ./Dockerfile.gcp \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 8Gi \
        --cpu 4 \
        --timeout 3600 \
        --max-instances 10 \
        --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
        --set-env-vars GCS_BUCKET="${PROJECT_ID}-brand-assets" \
        --set-env-vars GCS_MODEL_BUCKET="${PROJECT_ID}-ml-models" \
        --set-env-vars API_PORT=8080 \
        --service-account="brand-creator-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --platform managed --region $REGION --format "value(status.url)")
    
    echo -e "${GREEN}✅ Cloud Run deployment complete${NC}"
    echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
    
    # Clean up
    rm -f ./Dockerfile.gcp
}

# Deploy Queue-Centric architecture
deploy_queue_centric() {
    echo -e "${YELLOW}⚙️ Deploying queue-centric architecture...${NC}"
    # Implementation for queue-centric deployment
    echo "Queue-centric deployment not yet implemented"
}

# Deploy Serverless architecture  
deploy_serverless() {
    echo -e "${YELLOW}⚡ Deploying serverless architecture...${NC}"
    # Implementation for serverless deployment
    echo "Serverless deployment not yet implemented"
}

# Deploy Microservices architecture
deploy_microservices() {
    echo -e "${YELLOW}🔧 Deploying microservices architecture...${NC}"
    # Implementation for microservices deployment  
    echo "Microservices deployment not yet implemented"
}

# Test deployment
test_deployment() {
    echo -e "${YELLOW}🧪 Testing deployment...${NC}"
    
    if [ "$ARCHITECTURE" = "mvp-monolith" ]; then
        SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
            --platform managed --region $REGION --format "value(status.url)")
        
        # Test health endpoint
        if curl -f "${SERVICE_URL}/api/health" &>/dev/null; then
            echo -e "${GREEN}✅ Health check passed${NC}"
        else
            echo -e "${RED}❌ Health check failed${NC}"
            return 1
        fi
        
        # Test API documentation
        echo -e "${BLUE}📖 API Documentation: ${SERVICE_URL}/docs${NC}"
        echo -e "${BLUE}🎨 Frontend: ${SERVICE_URL}${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting deployment for project: ${PROJECT_ID}${NC}"
    
    check_prerequisites
    setup_project
    create_storage
    create_service_account
    deploy_architecture
    test_deployment
    
    echo -e "${GREEN}🎉 Deployment complete!${NC}"
    echo -e "${GREEN}Your AI Brand Creator is now running on GCP${NC}"
}

# Run main function
main
