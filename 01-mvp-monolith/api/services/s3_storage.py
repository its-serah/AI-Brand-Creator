"""
AWS S3 Storage Service for Free Tier optimization
Handles file uploads and downloads to S3 bucket
"""

import boto3
import logging
import os
from typing import Optional, Dict
from botocore.exceptions import ClientError, NoCredentialsError
from PIL import Image
import io

logger = logging.getLogger(__name__)

class S3StorageService:
    """S3 service optimized for AWS Free Tier limits"""
    
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            self.s3_client = boto3.client('s3', region_name=self.region)
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Using local storage fallback.")
            self.s3_client = None
    
    def upload_image(self, image: Image.Image, key: str, optimize_for_freetier: bool = True) -> Optional[str]:
        """
        Upload image to S3 with free tier optimizations
        Returns S3 URL or None if failed
        """
        if not self.s3_client or not self.bucket_name:
            logger.warning("S3 not available, saving locally")
            return self._save_locally(image, key)
        
        try:
            # Optimize image for free tier (reduce size/quality to save bandwidth)
            if optimize_for_freetier:
                image = self._optimize_for_freetier(image)
            
            # Convert image to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                img_buffer,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': 'image/png',
                    'CacheControl': 'max-age=86400',  # 1 day cache
                    'ACL': 'public-read'
                }
            )
            
            # Return public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            logger.info(f"Image uploaded to S3: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return self._save_locally(image, key)
    
    def _optimize_for_freetier(self, image: Image.Image) -> Image.Image:
        """Optimize image to reduce S3 storage and bandwidth usage"""
        
        # Resize if too large (free tier bandwidth optimization)
        max_size = 512
        if image.size[0] > max_size or image.size[1] > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            logger.info(f"Image resized to {image.size} for free tier optimization")
        
        # Convert to RGB if RGBA to reduce file size
        if image.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        
        return image
    
    def _save_locally(self, image: Image.Image, key: str) -> str:
        """Fallback to local storage if S3 fails"""
        local_path = f"storage/{key}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        image.save(local_path)
        return f"/storage/{key}"
    
    def get_storage_usage(self) -> Dict[str, any]:
        """Get current S3 usage (for free tier monitoring)"""
        if not self.s3_client or not self.bucket_name:
            return {"error": "S3 not configured"}
        
        try:
            # List objects to calculate usage
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                return {"objects": 0, "total_size": 0, "free_tier_usage": "0%"}
            
            total_size = sum(obj['Size'] for obj in response['Contents'])
            object_count = len(response['Contents'])
            
            # Free tier limits: 5GB storage
            free_tier_limit = 5 * 1024 * 1024 * 1024  # 5GB in bytes
            usage_percentage = (total_size / free_tier_limit) * 100
            
            return {
                "objects": object_count,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "free_tier_limit_gb": 5,
                "free_tier_usage": f"{usage_percentage:.1f}%",
                "warning": usage_percentage > 80
            }
            
        except ClientError as e:
            logger.error(f"Failed to get S3 usage: {e}")
            return {"error": str(e)}
    
    def cleanup_old_files(self, days_old: int = 7) -> int:
        """Clean up old files to stay within free tier limits"""
        if not self.s3_client or not self.bucket_name:
            return 0
        
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' not in response:
                return 0
            
            deleted_count = 0
            for obj in response['Contents']:
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
                    deleted_count += 1
                    logger.info(f"Deleted old file: {obj['Key']}")
            
            return deleted_count
            
        except ClientError as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
