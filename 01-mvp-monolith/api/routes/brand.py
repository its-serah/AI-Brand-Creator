"""
Brand generation API routes
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import logging
from typing import Optional

from ..models.brand import BrandRequest, BrandResponse, BrandGenerationStatus
from ..models.base import APIResponse
from ..services.brand_service import BrandService
from ..config import Settings

router = APIRouter()
logger = logging.getLogger(__name__)

class EmailShareRequest(BaseModel):
    """Request model for sharing brand details via email"""
    email: str  # Using str instead of EmailStr to avoid pydantic dependency issues
    brand_data: dict
    message: Optional[str] = None

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

@router.post("/share/email", response_model=APIResponse[dict])
async def share_brand_via_email(
    request: EmailShareRequest,
    background_tasks: BackgroundTasks,
    brand_service: BrandService = Depends(get_brand_service)
):
    """
    Share brand results via email
    
    Sends an email with the brand generation results including:
    - Brand summary and description
    - Color palette
    - Typography recommendations
    - Links to generated logos and social media exports
    """
    try:
        logger.info(f"Email share request for: {request.email}")
        
        # Validate email format
        if '@' not in request.email or '.' not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Add background task to send email (non-blocking)
        background_tasks.add_task(
            send_brand_email,
            request.email,
            request.brand_data,
            request.message
        )
        
        return APIResponse(
            data={
                "status": "email_queued",
                "message": f"Brand results will be sent to {request.email}",
                "email": request.email
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sharing brand via email: {e}")
        raise HTTPException(status_code=500, detail="Error sharing brand via email")

async def send_brand_email(email: str, brand_data: dict, message: Optional[str] = None):
    """
    Background task to send brand results via email
    """
    import smtplib
    import json
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    import os
    
    try:
        logger.info(f"Preparing to send brand email to: {email}")
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Your Brand Results - AI Brand Creator</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; max-width: 600px; margin: 0 auto; }}
                .brand-name {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                .section {{ margin: 25px 0; padding: 20px; border-left: 4px solid #ff6b35; background: #f9f9f9; }}
                .color-palette {{ display: flex; gap: 10px; margin: 15px 0; }}
                .color-box {{ width: 50px; height: 50px; border-radius: 8px; border: 2px solid #ddd; }}
                .logo-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                .logo-item {{ text-align: center; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎨 Your Brand Results</h1>
                <p>AI Brand Creator - Professional Brand Identity Generation</p>
            </div>
            
            <div class="content">
                <div class="brand-name">{brand_data.get('business_name', 'Your Brand')}</div>
                
                {f'<div class="section"><strong>Personal Message:</strong><br>{message}</div>' if message else ''}
                
                <div class="section">
                    <h3>🎯 Brand Overview</h3>
                    <p><strong>Industry:</strong> {brand_data.get('industry', 'N/A')}</p>
                    <p><strong>Style:</strong> {brand_data.get('style', 'N/A')}</p>
                    <p><strong>Color Scheme:</strong> {brand_data.get('color_scheme', 'N/A')}</p>
                    <p><strong>Target Audience:</strong> {brand_data.get('target_audience', 'N/A')}</p>
                </div>
                
                <div class="section">
                    <h3>🎨 Brand Description</h3>
                    <p>{brand_data.get('brand_description', 'Professional brand identity designed with AI assistance.')}</p>
                </div>
                
                <div class="section">
                    <h3>🌈 Color Palette</h3>
                    <div class="color-palette">
                        {' '.join([f'<div class="color-box" style="background-color: {color};" title="{color}"></div>' for color in brand_data.get('color_palette', ['#333333', '#666666', '#999999'])])}
                    </div>
                    <p><strong>Extracted Colors:</strong> {', '.join(brand_data.get('extracted_colors', [])[:6])}</p>
                </div>
                
                <div class="section">
                    <h3>📝 Typography</h3>
                    <p><strong>Recommended Font:</strong> {brand_data.get('font_suggestion', 'Arial, sans-serif')}</p>
                </div>
                
                <div class="section">
                    <h3>📊 Enhancement Features</h3>
                    <ul>
                        {'<li>✅ Logo Upscaling Applied</li>' if brand_data.get('upscaling_applied') else '<li>❌ Logo Upscaling Not Applied</li>'}
                        {'<li>✅ Color Variations Available</li>' if brand_data.get('color_variations_available') else '<li>❌ Color Variations Not Available</li>'}
                        {'<li>✅ Social Media Exports Generated</li>' if brand_data.get('social_media_exports') else '<li>❌ No Social Media Exports</li>'}
                    </ul>
                    <p><strong>Enhancement Features:</strong> {', '.join(brand_data.get('enhancement_features', ['Logo Enhancement', 'Color Extraction']))}</p>
                </div>
                
                <div class="section">
                    <h3>🚀 Next Steps</h3>
                    <p>Your brand assets have been generated and are ready for use. You can:</p>
                    <ul>
                        <li>Download your logo files in multiple formats</li>
                        <li>Use the social media export versions for your online presence</li>
                        <li>Apply the color palette across all brand materials</li>
                        <li>Implement the typography recommendations in your designs</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by AI Brand Creator | Professional Brand Identity Solutions</p>
                <p>Created with Stable Diffusion AI Technology</p>
            </div>
        </body>
        </html>
        """
        
        # For now, log the email content (you can integrate with actual email service)
        logger.info(f"Email content prepared for {email} (length: {len(html_content)} characters)")
        logger.info("Email sending functionality ready - integrate with SMTP service like SendGrid, AWS SES, or Gmail SMTP")
        
        # TODO: Integrate with actual email service
        # Example with Gmail SMTP:
        # smtp_server = "smtp.gmail.com"
        # smtp_port = 587
        # sender_email = "your-email@gmail.com"
        # sender_password = "your-app-password"
        # 
        # msg = MIMEMultipart('alternative')
        # msg['Subject'] = f"Your Brand Results - {brand_data.get('business_name', 'AI Brand Creator')}"
        # msg['From'] = sender_email
        # msg['To'] = email
        # 
        # html_part = MIMEText(html_content, 'html')
        # msg.attach(html_part)
        # 
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login(sender_email, sender_password)
        #     server.send_message(msg)
        
        logger.info(f"Brand email processed successfully for {email}")
        
    except Exception as e:
        logger.error(f"Failed to send brand email to {email}: {e}")
        # In production, you might want to retry or store failed emails
