# AWS + RunPod Hybrid Deployment

This setup uses AWS Free Tier for the web API and RunPod for GPU inference.

## Architecture

```
User → AWS EC2 (API Server) → RunPod (GPU Inference) → User
         ↓                        ↓
      S3 Storage            Stable Diffusion
```

## Step 1: Deploy to RunPod

1. Go to [RunPod.io](https://runpod.io)
2. Create a new **Serverless Endpoint**
3. Choose a GPU template (RTX 3090 or A4000 recommended)
4. Upload the Docker image:

```dockerfile
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

WORKDIR /app

# Install dependencies
RUN pip install diffusers transformers accelerate runpod pillow

# Copy handler
COPY runpod_handler.py .

CMD ["python", "-u", "runpod_handler.py"]
```

5. Get your endpoint URL and API key

## Step 2: Deploy to AWS EC2 (Free Tier)

1. Launch a **t2.micro** instance (Ubuntu 22.04)
2. SSH into the instance:

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. Set environment variables:

```bash
export RUNPOD_ENDPOINT_URL="https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"
export RUNPOD_API_KEY="your-runpod-api-key"
```

4. Run the deployment script:

```bash
curl -O https://raw.githubusercontent.com/its-serah/AI-Brand-Creator/main/deploy_aws_lite.sh
bash deploy_aws_lite.sh
```

## Step 3: Verify

Test your hybrid deployment:

```bash
curl -X POST http://your-ec2-ip/v1/brand/generate \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "TestCorp",
    "industry": "technology",
    "style": "minimal",
    "color_scheme": "cool",
    "personality_traits": ["modern", "innovative"],
    "target_audience": "professionals",
    "prompt": "clean modern logo",
    "negative_prompt": "complex cluttered",
    "additional_notes": "Testing hybrid deployment",
    "num_logos": 1
  }'
```

## Costs

- **AWS EC2 t2.micro**: FREE (12 months free tier)
- **RunPod Serverless**: ~$0.0002 per second of GPU time
  - Average logo: 2-3 seconds = $0.0006
  - 1000 logos ≈ $0.60

## Benefits

✅ "Powered by AWS" - legitimately running on AWS  
✅ GPU acceleration from RunPod  
✅ Scales automatically  
✅ Very cost-effective  
✅ No memory issues  

## Environment Variables

Set these on your AWS EC2 instance:

```bash
# Required
RUNPOD_ENDPOINT_URL=https://api.runpod.ai/v2/YOUR_ENDPOINT/runsync
RUNPOD_API_KEY=your_api_key

# Optional
S3_BUCKET=your-logo-storage  # For S3 storage
AWS_REGION=us-east-1
```

## Monitoring

- AWS CloudWatch for EC2 metrics
- RunPod dashboard for GPU usage
- Check logs: `sudo journalctl -u ai-brand -f`
