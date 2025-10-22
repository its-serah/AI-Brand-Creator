#!/bin/bash

# AWS EC2 t2.micro deployment (API server only, no AI models)
echo "========================================"
echo "AWS EC2 Lightweight Deployment"
echo "API Server Only - AI runs on RunPod"
echo "========================================"

# Get RunPod credentials
read -p "Enter your RunPod Endpoint ID: " RUNPOD_ENDPOINT_ID
read -p "Enter your RunPod API Key: " RUNPOD_API_KEY

# Update and install basics
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx git

# Clone the repository
cd /home/ubuntu
git clone https://github.com/its-serah/AI-Brand-Creator.git
cd AI-Brand-Creator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install ONLY the API dependencies (no AI models!)
pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pydantic==2.5.0 \
    pillow==10.0.0 \
    requests==2.31.0 \
    python-multipart==0.0.6 \
    boto3==1.28.62

# Create environment file
cat > /home/ubuntu/AI-Brand-Creator/.env << EOF
RUNPOD_ENDPOINT_URL=https://api.runpod.ai/v2/$RUNPOD_ENDPOINT_ID/runsync
RUNPOD_API_KEY=$RUNPOD_API_KEY
EOF

# Create systemd service
sudo tee /etc/systemd/system/ai-brand.service > /dev/null << EOF
[Unit]
Description=AI Brand Creator API (AWS + RunPod)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AI-Brand-Creator/01-mvp-monolith
EnvironmentFile=/home/ubuntu/AI-Brand-Creator/.env
ExecStart=/home/ubuntu/AI-Brand-Creator/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/ai-brand > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/ai-brand /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable ai-brand
sudo systemctl start ai-brand

echo "========================================"
echo "AWS Deployment Complete!"
echo "API: http://$(curl -s ifconfig.me)"
echo "Logs: sudo journalctl -u ai-brand -f"
echo ""
echo "Architecture:"
echo "- AWS EC2: API Server (This instance)"
echo "- RunPod: GPU Inference ($RUNPOD_ENDPOINT_ID)"
echo "========================================"
