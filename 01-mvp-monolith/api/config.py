"""
Configuration settings for Brand Generator API
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "Brand Generator API"
    api_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "brandpassword"
    neo4j_database: str = "neo4j"
    
    # S3 Configuration
    s3_endpoint: Optional[str] = None
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin123"
    s3_bucket: str = "brand-assets"
    s3_region: str = "us-east-1"
    
    # Redis Configuration (for Celery)
    redis_url: str = "redis://localhost:6379/0"
    
    # GPU Configuration
    device: str = "cuda"  # or "cpu" for CPU-only mode
    model_cache_dir: str = "./models"
    
    # SDXL Configuration
    sdxl_model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"
    sdxl_refiner_id: str = "stabilityai/stable-diffusion-xl-refiner-1.0"
    controlnet_model_id: str = "diffusers/controlnet-canny-sdxl-1.0"
    lora_weights_dir: str = "./models/lora"
    
    # Generation Configuration
    max_concurrent_jobs: int = 2
    job_timeout_seconds: int = 300
    image_output_size: tuple = (1024, 1024)
    
    # WCAG Configuration
    min_contrast_ratio: float = 4.5  # AA standard
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
