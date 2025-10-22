#!/bin/bash

echo "========================================="
echo "RunPod Serverless Deployment"
echo "========================================="

# Step 1: Build Docker image
echo "Building Docker image for RunPod..."
docker build -f Dockerfile.runpod -t ai-brand-runpod .

# Step 2: Tag for Docker Hub (replace with your username)
echo "Tagging image..."
read -p "Enter your Docker Hub username: " DOCKER_USER
docker tag ai-brand-runpod:latest $DOCKER_USER/ai-brand-runpod:latest

# Step 3: Push to Docker Hub
echo "Pushing to Docker Hub..."
docker login
docker push $DOCKER_USER/ai-brand-runpod:latest

echo "========================================="
echo "Docker image ready: $DOCKER_USER/ai-brand-runpod:latest"
echo ""
echo "Next steps on RunPod.io:"
echo "1. Go to Serverless → Create Endpoint"
echo "2. Select GPU: 24GB VRAM (RTX 3090/4090)"
echo "3. Container Image: $DOCKER_USER/ai-brand-runpod:latest"
echo "4. Configure:"
echo "   - Max Workers: 3"
echo "   - Idle Timeout: 5 seconds"
echo "   - Container Disk: 20 GB"
echo "5. Click 'Deploy'"
echo ""
echo "After deployment, you'll get:"
echo "- Endpoint ID: xxxxxxxx-xxxx-xxxx"
echo "- API Key: RP_xxxxxxxxxxxxx"
echo "========================================="
