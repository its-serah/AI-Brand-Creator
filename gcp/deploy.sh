#!/bin/bash
# Google Cloud Platform Deployment Script for BrandForge AI
# This script builds and deploys the brand generation service to Cloud Run

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-ringed-metric-448307-u9}
SERVICE_NAME=${SERVICE_NAME:-brand-api-gpu}
REGION=${REGION:-us-central1}
REPOSITORY=${REPOSITORY:-brand-registry}
IMAGE_NAME=${IMAGE_NAME:-brand-api}
MEMORY=${MEMORY:-16Gi}
CPU=${CPU:-4}
TIMEOUT=${TIMEOUT:-600}
MAX_INSTANCES=${MAX_INSTANCES:-5}
MIN_INSTANCES=${MIN_INSTANCES:-0}

echo "🚀 Starting GCP deployment for BrandForge AI..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Memory: $MEMORY, CPU: $CPU"
echo

# Check if gcloud is authenticated
echo "📋 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated. Please run: gcloud auth login"
    exit 1
fi

# Set project
echo "🔧 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "📦 Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION &>/dev/null; then
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for BrandForge AI"
fi

# Build image with Cloud Build
echo "🏗️ Building container image..."
IMAGE_URI=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:latest

cd /home/serah/AI-Brand-Creator

gcloud builds submit --tag $IMAGE_URI --timeout=1200s \
    --machine-type=e2-highcpu-8 \
    --disk-size=100 \
    .

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build completed successfully!"

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_URI \
    --region $REGION \
    --platform managed \
    --port 8080 \
    --memory $MEMORY \
    --cpu $CPU \
    --timeout $TIMEOUT \
    --max-instances $MAX_INSTANCES \
    --min-instances $MIN_INSTANCES \
    --allow-unauthenticated \
    --set-env-vars="DEBUG=false,HF_HOME=/models/hf,HUGGINGFACE_HUB_CACHE=/models/hf/hub" \
    --execution-environment=gen2 \
    --cpu-boost \
    --no-use-http2

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed!"
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo
echo "🎉 Deployment successful!"
echo "Service URL: $SERVICE_URL"
echo "Service name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Project: $PROJECT_ID"
echo
echo "🔗 Links:"
echo "Cloud Run Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/overview?project=$PROJECT_ID"
echo "Cloud Build History: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "Logs: https://console.cloud.google.com/logs/query;query=resource.type%3D%22cloud_run_revision%22%20resource.labels.service_name%3D%22$SERVICE_NAME%22?project=$PROJECT_ID"
echo
echo "Test the API:"
echo "curl $SERVICE_URL/health"
echo
echo "✅ GCP deployment completed!"
