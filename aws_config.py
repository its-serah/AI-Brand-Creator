"""
AWS Free Tier (t2.micro) Optimized Configuration
Memory: 1GB RAM
CPU: 1 vCPU
Storage: 8GB (free tier)
"""

import os

# Memory optimization settings
MAX_WORKERS = 1  # Single worker for t2.micro
WORKER_MEMORY_MB = 768  # Leave 256MB for OS
MODEL_CACHE_DIR = "/tmp/model_cache"  # Use ephemeral storage

# Model settings for minimal memory usage
MODEL_CONFIG = {
    "use_tiny_model": True,  # Use smallest possible model
    "image_size": 128,  # Minimum viable size
    "inference_steps": 2,  # Bare minimum steps
    "batch_size": 1,  # Process one at a time
    "enable_attention_slicing": True,
    "enable_cpu_offload": True,
    "torch_threads": 1,
    "guidance_scale": 2.0
}

# Uvicorn settings for t2.micro
UVICORN_CONFIG = {
    "workers": 1,  # Single worker only
    "loop": "asyncio",  # Most memory efficient
    "limit_concurrency": 2,  # Limit concurrent requests
    "timeout_keep_alive": 5,  # Short keepalive
    "access_log": False,  # Disable to save resources
}

# Environment variables for optimization
os.environ['TRANSFORMERS_CACHE'] = MODEL_CACHE_DIR
os.environ['HF_HOME'] = MODEL_CACHE_DIR
os.environ['TORCH_HOME'] = MODEL_CACHE_DIR
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# API rate limiting for t2.micro
RATE_LIMIT = {
    "requests_per_minute": 5,  # Max 5 requests per minute
    "max_queue_size": 2,  # Small queue to prevent OOM
}

print("AWS t2.micro optimizations loaded:")
print(f"- Memory limit: {WORKER_MEMORY_MB}MB")
print(f"- Image size: {MODEL_CONFIG['image_size']}px")
print(f"- Inference steps: {MODEL_CONFIG['inference_steps']}")
print(f"- Rate limit: {RATE_LIMIT['requests_per_minute']} req/min")
