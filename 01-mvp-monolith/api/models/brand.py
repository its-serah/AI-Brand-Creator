"""
Brand generation API models and schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Industry(str, Enum):
    """Supported industries"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    RETAIL = "retail"
    FOOD = "food"
    FASHION = "fashion"
    AUTOMOTIVE = "automotive"
    REAL_ESTATE = "real-estate"
    CONSULTING = "consulting"
    CREATIVE = "creative"
    OTHER = "other"

class LogoStyle(str, Enum):
    """Logo style options"""
    MINIMAL = "minimal"
    GEOMETRIC = "geometric"
    TEXT_BASED = "text-based"
    SYMBOLIC = "symbolic"
    ABSTRACT = "abstract"
    CLASSIC = "classic"

class ColorScheme(str, Enum):
    """Color scheme preferences"""
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"
    VIBRANT = "vibrant"

class TargetAudience(str, Enum):
    """Target audience segments"""
    YOUNG_ADULTS = "young-adults"
    PROFESSIONALS = "professionals"
    FAMILIES = "families"
    SENIORS = "seniors"
    BUSINESSES = "businesses"
    GLOBAL = "global"

class PersonalityTrait(str, Enum):
    """Brand personality traits"""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    FRIENDLY = "friendly"
    MODERN = "modern"
    TRUSTWORTHY = "trustworthy"
    INNOVATIVE = "innovative"

class BrandRequest(BaseModel):
    """Request model for brand generation"""
    business_name: str = Field(..., min_length=1, max_length=100)
    industry: Industry
    style: LogoStyle
    color_scheme: ColorScheme
    personality_traits: List[PersonalityTrait] = Field(..., min_items=1, max_items=6)
    target_audience: TargetAudience
    prompt: str = Field(..., min_length=10, max_length=2000)
    negative_prompt: str = Field(..., min_length=5, max_length=1000)
    additional_notes: Optional[str] = Field(None, max_length=500)
    
    # Generation parameters
    num_logos: int = Field(default=3, ge=1, le=5)
    num_variations: int = Field(default=1, ge=1, le=3)
    
    @validator('business_name')
    def validate_business_name(cls, v):
        if not v.strip():
            raise ValueError('Business name cannot be empty')
        return v.strip()
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if len(v.split()) < 3:
            raise ValueError('Prompt must contain at least 3 words')
        return v
    
    class Config:
        use_enum_values = True

class LogoResult(BaseModel):
    """Individual logo result"""
    id: str
    url: str
    thumbnail_url: str
    style_confidence: float = Field(ge=0.0, le=1.0)
    quality_score: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}
    
class ColorPalette(BaseModel):
    """Brand color palette"""
    primary: str
    secondary: Optional[str] = None
    accent: Optional[str] = None
    neutral: Optional[str] = None
    colors: List[str] = Field(default_factory=list)
    
    @validator('primary', 'secondary', 'accent', 'neutral')
    def validate_hex_color(cls, v):
        if v and not (v.startswith('#') and len(v) == 7):
            raise ValueError('Color must be a valid hex color (e.g., #FF0000)')
        return v

class Typography(BaseModel):
    """Typography recommendations"""
    primary_font: str
    secondary_font: Optional[str] = None
    font_family: str
    font_style: str = "regular"
    weight: str = "400"

class BrandKit(BaseModel):
    """Complete brand kit with all assets"""
    logos: List[LogoResult]
    color_palette: ColorPalette
    typography: Typography
    brand_description: str
    usage_guidelines: Optional[str] = None
    file_formats: List[str] = Field(default=["png", "svg", "pdf"])

class BrandResponse(BaseModel):
    """Response model for brand generation"""
    job_id: str
    business_name: str
    status: str = "completed"
    brand_kit: Optional[BrandKit] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Simplified fields for immediate response
    logos: Optional[List[LogoResult]] = None
    color_palette: Optional[List[str]] = None
    font_suggestion: Optional[str] = None
    brand_description: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class BrandGenerationStatus(BaseModel):
    """Brand generation job status"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float = Field(ge=0.0, le=1.0)
    current_step: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
