# Google Cloud Platform Setup Guide

This guide walks you through setting up the AI Brand Creator on Google Cloud Platform (GCP) with all required services and configurations.

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and configured
- Docker installed locally
- Terraform (optional, for infrastructure as code)

## Quick Setup

### 1. Project Setup

```bash
# Create a new GCP project
export PROJECT_ID="ai-brand-creator-$(date +%s)"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  cloudtasks.googleapis.com \
  pubsub.googleapis.com \
  aiplatform.googleapis.com \
  container.googleapis.com
```

### 2. Storage Setup

```bash
# Create Cloud Storage bucket for assets
export BUCKET_NAME="${PROJECT_ID}-brand-assets"
gsutil mb gs://$BUCKET_NAME

# Create another bucket for ML models
export MODEL_BUCKET="${PROJECT_ID}-ml-models"
gsutil mb gs://$MODEL_BUCKET
```

### 3. Service Account Setup

```bash
# Create service account
gcloud iam service-accounts create brand-creator-sa \
    --description="AI Brand Creator service account" \
    --display-name="Brand Creator SA"

export SA_EMAIL="brand-creator-sa@${PROJECT_ID}.iam.gserviceaccount.com"

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

# Create and download service account key
gcloud iam service-accounts keys create ~/brand-creator-key.json \
    --iam-account=$SA_EMAIL
```

### 4. Environment Configuration

```bash
# Copy environment template
cp architectures/mvp-monolith/.env.example architectures/mvp-monolith/.env

# Edit .env file with your GCP settings
cat > architectures/mvp-monolith/.env << EOF
# GCP Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json
GCS_BUCKET=$BUCKET_NAME
GCS_MODEL_BUCKET=$MODEL_BUCKET

# Database (Cloud SQL or Cloud Memorystore)
NEO4J_URI=bolt://neo4j-instance:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password

# Redis (Cloud Memorystore)
REDIS_URL=redis://redis-instance:6379

# AI Configuration
AI_MODEL_ID=runwayml/stable-diffusion-v1-5
DEVICE=cuda  # or cpu for Cloud Run

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO
EOF
```

## Deployment Options

### Option 1: Cloud Run (Serverless)

Best for: Development, testing, variable traffic

```bash
cd architectures/mvp-monolith

# Build and deploy to Cloud Run
gcloud run deploy brand-creator \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --set-env-vars GCS_BUCKET=$BUCKET_NAME
```

### Option 2: Google Kubernetes Engine (GKE)

Best for: Production workloads, scalability

```bash
# Create GKE cluster
gcloud container clusters create brand-creator-cluster \
    --machine-type e2-standard-4 \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --region us-central1

# Deploy with Kubernetes
kubectl apply -f architectures/mvp-monolith/gcp/k8s/
```

### Option 3: Compute Engine

Best for: Full control, GPU workloads

```bash
# Create VM instance with GPU
gcloud compute instances create brand-creator-vm \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --accelerator=count=1,type=nvidia-tesla-t4 \
    --image-family=pytorch-latest-gpu \
    --image-project=deeplearning-platform-release \
    --boot-disk-size=100GB \
    --metadata-from-file startup-script=scripts/vm-startup.sh
```

## Database Setup

### Neo4j (Graph Database)

```bash
# Option 1: Neo4j AuraDB (Managed)
# Visit https://console.neo4j.io/ and create instance

# Option 2: Self-hosted on Compute Engine
gcloud compute instances create neo4j-instance \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --metadata-from-file startup-script=scripts/neo4j-startup.sh
```

### Redis (Cache)

```bash
# Create Cloud Memorystore Redis instance
gcloud redis instances create brand-cache \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_6_x
```

## Monitoring and Security

### Cloud Monitoring

```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create monitoring dashboard (optional)
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json
```

### Security Configuration

```bash
# Create firewall rules (if using Compute Engine)
gcloud compute firewall-rules create allow-brand-creator \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Brand Creator API access"

# Enable Cloud Armor (DDoS protection)
gcloud compute security-policies create brand-creator-policy \
    --description "Brand Creator security policy"
```

## Testing the Deployment

```bash
# Get the deployment URL
export SERVICE_URL=$(gcloud run services describe brand-creator \
    --platform managed --region us-central1 --format "value(status.url)")

# Test the health endpoint
curl $SERVICE_URL/api/health

# Test brand generation (with sample data)
curl -X POST "$SERVICE_URL/api/v1/brand/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Test Company",
    "industry": "technology",
    "style": "minimal",
    "color_scheme": "professional",
    "target_audience": "businesses"
  }'
```

## Cost Optimization

### Cloud Run
- Automatic scaling to zero when not in use
- Pay per request pricing
- Use minimum instances: 0

### Storage
- Use lifecycle policies for old assets
- Enable compression for stored files
- Use regional buckets for better performance

### Compute
- Use preemptible instances for batch processing
- Enable auto-scaling based on demand
- Use sustained use discounts

## Troubleshooting

### Common Issues

1. **Service Account Permissions**
   ```bash
   # Check current permissions
   gcloud projects get-iam-policy $PROJECT_ID \
       --flatten="bindings[].members" \
       --filter="bindings.members:$SA_EMAIL"
   ```

2. **Storage Access Issues**
   ```bash
   # Test bucket access
   gsutil ls gs://$BUCKET_NAME
   ```

3. **Memory Issues on Cloud Run**
   ```bash
   # Increase memory allocation
   gcloud run services update brand-creator \
       --memory 8Gi --region us-central1
   ```

### Logs and Debugging

```bash
# View Cloud Run logs
gcloud logs read --service=brand-creator --limit=50

# Stream logs in real-time
gcloud logs tail --service=brand-creator
```

## Architecture-Specific Setup

### MVP Monolith
- Single Cloud Run service
- Cloud Storage for assets
- Cloud SQL or managed Neo4j

### Queue-Centric
- Multiple Cloud Run services
- Cloud Tasks for job queuing
- Pub/Sub for event messaging

### Serverless
- Cloud Functions for processing
- Cloud Workflows for orchestration
- Eventarc for event-driven triggers

### Microservices
- GKE cluster with Istio
- Cloud Load Balancer
- Cloud Monitoring and Logging

## Next Steps

1. Set up CI/CD with Cloud Build
2. Configure custom domains
3. Implement authentication
4. Set up monitoring alerts
5. Enable backup strategies

For detailed architecture-specific instructions, see the README files in each architecture directory.
