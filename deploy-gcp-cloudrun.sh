#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-us-central1}"
PROJECT_ID="$(gcloud config get-value project)"
REPO="${REPO:-brand-registry}"
TAG="${TAG:-v$(date +%Y%m%d%H%M)}"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/brand-api:$TAG"
SERVICE_CPU="${SERVICE_CPU:-brand-api-cpu}"
SERVICE_GPU="${SERVICE_GPU:-brand-api}"

echo "Project: $PROJECT_ID"
echo "Image:   $IMAGE"

gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com logging.googleapis.com

gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="AI Brand Creator images" \
  2>/dev/null || true

gcloud builds submit --tag "$IMAGE" --timeout=1800

gcloud run deploy "$SERVICE_CPU" \
  --image "$IMAGE" \
  --region "$REGION" \
  --cpu=4 --memory=8Gi \
  --timeout=1800 --concurrency=1 \
  --min-instances=1 --max-instances=1 \
  --allow-unauthenticated

gcloud run deploy "$SERVICE_GPU" \
  --image "$IMAGE" \
  --region "$REGION" \
  --gpu=1 --gpu-type=nvidia-l4 \
  --cpu=4 --memory=16Gi \
  --timeout=1800 --concurrency=1 \
  --min-instances=1 --max-instances=1 \
  --zonal-redundancy=none \
  --allow-unauthenticated || true

CPU_URL="$(gcloud run services describe "$SERVICE_CPU" --region "$REGION" --format='value(status.url)')"
GPU_URL="$(gcloud run services describe "$SERVICE_GPU" --region "$REGION" --format='value(status.url)')"
echo "CPU URL: $CPU_URL"
echo "GPU URL: $GPU_URL"

curl -s "$CPU_URL/health" || true

echo "=== CPU logs (last 100) ==="
gcloud run services logs read "$SERVICE_CPU" --region "$REGION" --limit=100 || true
echo "=== GPU logs (last 100) ==="
gcloud run services logs read "$SERVICE_GPU" --region "$REGION" --limit=100 || true
