"""
Base API models and schemas
"""

from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = datetime.now()
    services: dict[str, str] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
