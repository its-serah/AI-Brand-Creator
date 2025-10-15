#!/bin/bash

# AWS FREE TIER DEPLOYMENT SCRIPT
# For t2.micro EC2 instance (1 CPU, 1GB RAM)

echo "AWS Free Tier Deployment for AI Brand Creator"
echo "=============================================="

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.10
sudo apt-get install -y python3.10 python3.10-venv python3-pip git htop

# Install Docker (optional for future use)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Clone repository
cd /home/ubuntu
git clone https://github.com/its-serah/AI-Brand-Creator.git
cd AI-Brand-Creator/01-mvp-monolith

# Create virtual environment
python3.10 -m venv venv-freetier
source venv-freetier/bin/activate

# Install lightweight requirements
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements-freetier.txt

# Set up environment variables for AWS
cat > .env << EOF
# AWS Free Tier Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# AWS S3 Configuration (Free Tier: 5GB storage)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here  
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-brand-creator-bucket

# Model Configuration for t2.micro
MODEL_CACHE_DIR=/tmp/huggingface_cache
MAX_CONCURRENT_REQUESTS=1
INFERENCE_STEPS=4
IMAGE_SIZE=256
ENABLE_UPSCALING=false

# Memory optimization
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
OMP_NUM_THREADS=1
EOF

# Create systemd service for auto-start
sudo tee /etc/systemd/system/brandcreator.service > /dev/null << EOF
[Unit]
Description=AI Brand Creator FastAPI App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AI-Brand-Creator/01-mvp-monolith
Environment=PATH=/home/ubuntu/AI-Brand-Creator/01-mvp-monolith/venv-freetier/bin
ExecStart=/home/ubuntu/AI-Brand-Creator/01-mvp-monolith/venv-freetier/bin/python server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable brandcreator
sudo systemctl start brandcreator

# Install nginx for reverse proxy (free tier optimization)
sudo apt-get install -y nginx

# Configure nginx
sudo tee /etc/nginx/sites-available/brandcreator > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Cache static files
    location /frontend/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_cache_valid 200 1d;
        add_header Cache-Control "public, max-age=86400";
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/brandcreator /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Set up log rotation to save disk space
sudo tee /etc/logrotate.d/brandcreator > /dev/null << EOF
/home/ubuntu/AI-Brand-Creator/01-mvp-monolith/*.log {
    daily
    missingok
    rotate 3
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
}
EOF

echo "Deployment complete!"
echo ""
echo "AWS Free Tier Usage:"
echo "- EC2: t2.micro (1 CPU, 1GB RAM) - 750 hours/month"
echo "- S3: 5GB storage for generated images"
echo "- Data transfer: 15GB out/month"
echo ""
echo "Your app is running at: http://YOUR_EC2_PUBLIC_IP"
echo ""
echo "Next steps:"
echo "1. Update .env with your AWS credentials"
echo "2. Create S3 bucket: aws s3 mb s3://your-brand-creator-bucket"
echo "3. Open port 80 in EC2 security group"
echo "4. (Optional) Set up Route 53 for custom domain"
echo ""
echo "Monitoring commands:"
echo "- Check app status: sudo systemctl status brandcreator"
echo "- View logs: sudo journalctl -u brandcreator -f"
echo "- Check memory: htop"
