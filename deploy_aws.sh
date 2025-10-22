#!/bin/bash

# AWS EC2 t2.micro deployment script for AI-Brand-Creator
# Optimized for 1GB RAM limitation

echo "========================================"
echo "AI-Brand-Creator AWS t2.micro Deployment"
echo "========================================"

# 1. Update system and install dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx supervisor

# 2. Create swap file (CRITICAL for t2.micro!)
echo "Creating 2GB swap file for model loading..."
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 3. Optimize system for low memory
echo "Optimizing system settings..."
sudo sysctl vm.swappiness=60
sudo sysctl vm.vfs_cache_pressure=50

# 4. Create app directory
cd /home/ubuntu
git clone https://github.com/its-serah/AI-Brand-Creator.git
cd AI-Brand-Creator

# 5. Create virtual environment with minimal packages
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 6. Install dependencies with memory optimization
echo "Installing Python packages (this will take time)..."
pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install --no-cache-dir transformers==4.30.0
pip install --no-cache-dir diffusers==0.21.0
pip install --no-cache-dir accelerate==0.20.0
pip install --no-cache-dir -r 01-mvp-monolith/requirements.txt

# 7. Pre-download the model (during deployment, not runtime)
echo "Pre-downloading model (one-time setup)..."
python3 << EOF
from diffusers import StableDiffusionPipeline
import torch
print("Downloading model...")
pipeline = StableDiffusionPipeline.from_pretrained(
    "hf-internal-testing/tiny-stable-diffusion-pipe",
    torch_dtype=torch.float32,
    cache_dir="/tmp/huggingface_cache"
)
print("Model cached successfully!")
EOF

# 8. Create systemd service for auto-restart
sudo tee /etc/systemd/system/ai-brand.service > /dev/null << EOF
[Unit]
Description=AI Brand Creator API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AI-Brand-Creator/01-mvp-monolith
Environment="PATH=/home/ubuntu/AI-Brand-Creator/venv/bin"
ExecStart=/home/ubuntu/AI-Brand-Creator/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1 --limit-concurrency 2
Restart=always
RestartSec=10
MemoryMax=768M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

# 9. Configure Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/ai-brand > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ai-brand /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 10. Start the service
sudo systemctl daemon-reload
sudo systemctl enable ai-brand.service
sudo systemctl start ai-brand.service

echo "========================================"
echo "Deployment complete!"
echo "API available at: http://YOUR_EC2_IP/"
echo "========================================"
echo ""
echo "Monitor logs with: sudo journalctl -u ai-brand -f"
echo "Check memory: free -h"
echo ""
echo "IMPORTANT: The first request will be slow as the model loads."
echo "Subsequent requests will be faster."
