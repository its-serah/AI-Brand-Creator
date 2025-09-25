"""
Brand generation API routes
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from ..models.brand import BrandRequest, BrandResponse, BrandGenerationStatus
from ..models.base import APIResponse
from ..services.brand_service import BrandService
from ..config import Settings

router = APIRouter()
logger = logging.getLogger(__name__)

def get_brand_service(settings: Settings = Depends(lambda: Settings())) -> BrandService:
    """Dependency to get brand service instance"""
    # In a real application, you'd want to use dependency injection
    # For now, we'll create a new instance each time
    return BrandService(settings)

@router.post("/generate", response_model=BrandResponse)
async def generate_brand(
    request: BrandRequest,
    brand_service: BrandService = Depends(get_brand_service)
):
    """
    Generate a complete brand identity including logos, colors, and typography
    
    This endpoint processes the brand requirements and generates:
    - Multiple logo variations using AI models
    - Color palette recommendations
    - Typography suggestions
    - Brand description and guidelines
    """
    try:
        logger.info(f"Received brand generation request for: {request.business_name}")
        
        # Validate request
        if not request.business_name.strip():
            raise HTTPException(status_code=400, detail="Business name is required")
        
        if not request.personality_traits:
            raise HTTPException(status_code=400, detail="At least one personality trait is required")
        
        # Initialize service if needed
        await brand_service.initialize()
        
        # Generate brand identity
        result = await brand_service.generate_brand(request)
        
        logger.info(f"Brand generation completed for {request.business_name} in {result.processing_time_seconds:.2f}s")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Brand generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during brand generation"
        )

@router.get("/status/{job_id}", response_model=APIResponse[BrandGenerationStatus])
async def get_generation_status(
    job_id: str,
    brand_service: BrandService = Depends(get_brand_service)
):
    """
    Get the status of a brand generation job
    
    Returns the current progress and status of an ongoing brand generation job.
    """
    try:
        status = await brand_service.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        status_response = BrandGenerationStatus(
            job_id=job_id,
            status=status.get("status", "unknown"),
            progress=status.get("progress", 0.0),
            current_step=status.get("current_step"),
            error_message=status.get("error")
        )
        
        return APIResponse(data=status_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving job status")

@router.get("/styles", response_model=APIResponse[list])
async def get_available_styles():
    """Get available logo styles"""
    try:
        styles = [
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Clean and simple with minimal elements"
            },
            {
                "id": "geometric", 
                "name": "Geometric",
                "description": "Uses geometric shapes and mathematical precision"
            },
            {
                "id": "text-based",
                "name": "Text-based", 
                "description": "Focus on typography and lettering design"
            },
            {
                "id": "symbolic",
                "name": "Symbolic",
                "description": "Symbolic representation of brand concept"
            },
            {
                "id": "abstract",
                "name": "Abstract",
                "description": "Abstract forms and creative interpretation"
            },
            {
                "id": "classic",
                "name": "Classic",
                "description": "Timeless, traditional design principles"
            }
        ]
        
        return APIResponse(data=styles)
        
    except Exception as e:
        logger.error(f"Error retrieving styles: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving available styles")

@router.get("/industries", response_model=APIResponse[list])
async def get_available_industries():
    """Get available industries"""
    try:
        industries = [
            {"id": "technology", "name": "Technology"},
            {"id": "healthcare", "name": "Healthcare"},
            {"id": "education", "name": "Education"},
            {"id": "finance", "name": "Finance"},
            {"id": "retail", "name": "Retail"},
            {"id": "food", "name": "Food & Beverage"},
            {"id": "fashion", "name": "Fashion"},
            {"id": "automotive", "name": "Automotive"},
            {"id": "real-estate", "name": "Real Estate"},
            {"id": "consulting", "name": "Consulting"},
            {"id": "creative", "name": "Creative Services"},
            {"id": "other", "name": "Other"}
        ]
        
        return APIResponse(data=industries)
        
    except Exception as e:
        logger.error(f"Error retrieving industries: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving available industries")

@router.get("/personalities", response_model=APIResponse[list])
async def get_personality_traits():
    """Get available personality traits"""
    try:
        traits = [
            {"id": "professional", "name": "Professional"},
            {"id": "creative", "name": "Creative"},
            {"id": "friendly", "name": "Friendly"},
            {"id": "modern", "name": "Modern"},
            {"id": "trustworthy", "name": "Trustworthy"},
            {"id": "innovative", "name": "Innovative"}
        ]
        
        return APIResponse(data=traits)
        
    except Exception as e:
        logger.error(f"Error retrieving personality traits: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving personality traits")

@router.get("/color-schemes", response_model=APIResponse[list])
async def get_color_schemes():
    """Get available color schemes"""
    try:
        schemes = [
            {
                "id": "warm",
                "name": "Warm tones",
                "description": "Warm autumn colors like burnt orange, golden amber, and deep maroon",
                "sample_colors": ["#D2691E", "#CC5500", "#FFB000"]
            },
            {
                "id": "cool",
                "name": "Cool tones", 
                "description": "Cool colors like blues and teals",
                "sample_colors": ["#4A90E2", "#357ABD", "#2E86C1"]
            },
            {
                "id": "neutral",
                "name": "Neutral tones",
                "description": "Neutral colors like grays, whites, and earth tones", 
                "sample_colors": ["#6B6B6B", "#8B8B8B", "#A0A0A0"]
            },
            {
                "id": "vibrant",
                "name": "Vibrant colors",
                "description": "Vibrant and energetic colors",
                "sample_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
            }
        ]
        
        return APIResponse(data=schemes)
        
    except Exception as e:
        logger.error(f"Error retrieving color schemes: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving color schemes")

@router.get("/examples", response_model=APIResponse[list])
async def get_brand_examples():
    """Get example brand generations for inspiration"""
    try:
        examples = [
            {
                "business_name": "TechFlow Solutions",
                "industry": "technology",
                "style": "minimal",
                "color_scheme": "cool", 
                "personality_traits": ["professional", "innovative"],
                "target_audience": "businesses",
                "description": "A clean, professional tech consulting brand with cool blue tones"
            },
            {
                "business_name": "Bloom & Co",
                "industry": "fashion",
                "style": "creative",
                "color_scheme": "warm",
                "personality_traits": ["creative", "friendly"],
                "target_audience": "young-adults", 
                "description": "A creative fashion brand with warm, inviting colors"
            },
            {
                "business_name": "Sterling Finance",
                "industry": "finance",
                "style": "classic",
                "color_scheme": "neutral",
                "personality_traits": ["trustworthy", "professional"],
                "target_audience": "professionals",
                "description": "A traditional, trustworthy financial services brand"
            }
        ]
        
        return APIResponse(data=examples)
        
    except Exception as e:
        logger.error(f"Error retrieving examples: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving brand examples")
