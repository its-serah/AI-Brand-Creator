"""
Brand generation service with AI model integration
"""

import asyncio
import uuid
import logging
import time
from typing import List, Optional, Dict, Any
from PIL import Image, ImageFilter
import io
import base64
import os

try:
    from diffusers import StableDiffusionPipeline
    import torch
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False

from ..models.brand import (
    BrandRequest, BrandResponse, LogoResult, 
    ColorPalette, Typography, BrandKit
)
from ..config import Settings

logger = logging.getLogger(__name__)

class BrandService:
    """Service for generating complete brand identities using AI models"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.active_jobs: Dict[str, Dict] = {}
        
        # Model components (to be initialized)
        self.sd_pipeline = None
        self.controlnet = None
        self.upscaler = None
        self.neo4j_driver = None
        # Force CPU for stability (you can change to cuda if you have GPU)
        self.device = "cpu" if DIFFUSERS_AVAILABLE else "cpu"
        
        # Create storage directories
        self.storage_dir = os.path.join(os.path.dirname(__file__), "../../storage")
        self.logos_dir = os.path.join(self.storage_dir, "logos")
        os.makedirs(self.logos_dir, exist_ok=True)
        
    async def initialize(self):
        """Initialize AI models and external services"""
        logger.info("Initializing Brand Service...")
        
        try:
            # Initialize AI models (placeholder - you'll integrate your actual models)
            await self._initialize_ai_models()
            
            # Initialize external services
            await self._initialize_external_services()
            
            logger.info("Brand Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Brand Service: {e}")
            raise
    
    async def _initialize_ai_models(self):
        """Initialize AI models for logo generation"""
        logger.info("Loading AI models...")
        
        if not DIFFUSERS_AVAILABLE:
            logger.warning("Diffusers not available. Install with: pip install diffusers torch")
            return
            
        try:
            logger.info(f"Loading Stable Diffusion model on {self.device}...")
            
            # Load Stable Diffusion model optimized for CPU logo generation
            logger.info("Loading Stable Diffusion v1.5 for CPU...")
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,  # Use float32 for CPU
                use_safetensors=True,
                safety_checker=None,  # Disable for speed
                requires_safety_checker=False
            )
            
            # Move to CPU and apply optimizations
            self.sd_pipeline = self.sd_pipeline.to("cpu")
            
            # CPU optimizations
            self.sd_pipeline.enable_sequential_cpu_offload()
            
            # Memory optimizations
            try:
                self.sd_pipeline.enable_attention_slicing()
                self.sd_pipeline.enable_memory_efficient_attention()
            except Exception as opt_e:
                logger.warning(f"Could not enable optimizations: {opt_e}")
            
            logger.info("AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            logger.warning("Continuing without AI models - will use fallback generation")
    
    async def _initialize_external_services(self):
        """Initialize Neo4j and other external services"""
        try:
            # Initialize Neo4j connection (placeholder)
            # from neo4j import AsyncGraphDatabase
            # self.neo4j_driver = AsyncGraphDatabase.driver(
            #     self.settings.neo4j_uri,
            #     auth=(self.settings.neo4j_user, self.settings.neo4j_password)
            # )
            
            logger.info("External services initialized (placeholder)")
            
        except Exception as e:
            logger.error(f"Failed to initialize external services: {e}")
            logger.warning("Continuing without external services for testing")
    
    async def generate_brand(self, request: BrandRequest) -> BrandResponse:
        """Generate a complete brand identity"""
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        logger.info(f"Starting brand generation for {request.business_name} (job: {job_id})")
        
        try:
            # Store job status
            self.active_jobs[job_id] = {
                "status": "processing",
                "progress": 0.0,
                "current_step": "Initializing",
                "request": request
            }
            
            # Step 1: Generate logos using AI models
            self._update_job_progress(job_id, 0.1, "Generating logo concepts...")
            logos = await self._generate_logos(request)
            
            # Step 2: Generate color palette using KGS
            self._update_job_progress(job_id, 0.4, "Creating color palette...")
            color_palette = await self._generate_color_palette(request)
            
            # Step 3: Generate typography recommendations
            self._update_job_progress(job_id, 0.6, "Selecting typography...")
            typography = await self._generate_typography(request)
            
            # Step 4: Generate brand description
            self._update_job_progress(job_id, 0.8, "Creating brand description...")
            brand_description = await self._generate_brand_description(request)
            
            # Step 5: Apply upscaling if needed
            self._update_job_progress(job_id, 0.9, "Enhancing images...")
            enhanced_logos = await self._enhance_logos(logos)
            
            # Step 6: Finalize response
            self._update_job_progress(job_id, 1.0, "Finalizing brand kit...")
            
            processing_time = time.time() - start_time
            
            response = BrandResponse(
                job_id=job_id,
                business_name=request.business_name,
                status="completed",
                processing_time_seconds=processing_time,
                # Simplified response format for frontend
                logos=enhanced_logos,
                color_palette=[color_palette.primary, color_palette.secondary, color_palette.accent, color_palette.neutral],
                font_suggestion=typography.primary_font,
                brand_description=brand_description
            )
            
            # Clean up job tracking
            self.active_jobs.pop(job_id, None)
            
            logger.info(f"Brand generation completed in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Brand generation failed: {e}")
            self.active_jobs[job_id] = {
                "status": "failed",
                "error": str(e)
            }
            raise
    
    async def _generate_logos(self, request: BrandRequest) -> List[LogoResult]:
        """Generate logos using Stable Diffusion"""
        logger.info(f"Generating logos with style: {request.style}")
        
        try:
            logos = []
            
            # Use Stable Diffusion if available, otherwise fallback to placeholder
            if self.sd_pipeline:
                logger.info("Using Stable Diffusion for logo generation")
                
                # Generate optimized prompt for logo creation
                logo_prompt = self._build_sd_prompt(request)
                negative_prompt = self._build_sd_negative_prompt(request)
                
                logger.info(f"SD Prompt: {logo_prompt[:100]}...")
                
                # Generate images with Stable Diffusion (CPU optimized)
                logger.info(f"Generating {request.num_logos} logos on CPU...")
                images = self.sd_pipeline(
                    prompt=logo_prompt,
                    negative_prompt=negative_prompt,
                    num_images_per_prompt=request.num_logos,
                    num_inference_steps=15,  # Reduced for CPU speed
                    guidance_scale=7.5,
                    width=512,
                    height=512,
                    generator=torch.manual_seed(hash(request.business_name) % 2**32)
                ).images
                logger.info(f"Successfully generated {len(images)} logos")
                
                for i, img in enumerate(images):
                    logo_id = str(uuid.uuid4())
                    
                    # Enhance the generated logo
                    enhanced_img = self._enhance_logo(img)
                    
                    # Save to file and get URL
                    logo_path = os.path.join(self.logos_dir, f"{logo_id}.png")
                    enhanced_img.save(logo_path)
                    
                    # Convert to base64 for immediate display
                    logo_url = self._image_to_data_url(enhanced_img)
                    
                    logo_result = LogoResult(
                        id=logo_id,
                        url=logo_url,
                        thumbnail_url=logo_url,
                        style_confidence=0.85 + (i * 0.05),
                        quality_score=0.90 + (i * 0.02),
                        metadata={
                            "style": request.style,
                            "industry": request.industry,
                            "prompt_used": logo_prompt[:150] + "..." if len(logo_prompt) > 150 else logo_prompt,
                            "file_path": logo_path,
                            "generated_with": "stable_diffusion"
                        }
                    )
                    
                    logos.append(logo_result)
            else:
                logger.warning("Stable Diffusion not available, using fallback")
                # Fallback to placeholder generation
                for i in range(request.num_logos):
                    logo_id = str(uuid.uuid4())
                    logo_url = await self._create_placeholder_logo(request, i)
                    
                    logo_result = LogoResult(
                        id=logo_id,
                        url=logo_url,
                        thumbnail_url=logo_url,
                        style_confidence=0.85 + (i * 0.05),
                        quality_score=0.90 + (i * 0.02),
                        metadata={
                            "style": request.style,
                            "industry": request.industry,
                            "prompt_used": request.prompt[:100] + "..." if len(request.prompt) > 100 else request.prompt,
                            "generated_with": "placeholder"
                        }
                    )
                    
                    logos.append(logo_result)
                    await asyncio.sleep(0.5)  # Simulate processing time
            
            return logos
            
        except Exception as e:
            logger.error(f"Logo generation failed: {e}")
            raise
    
    async def _create_placeholder_logo(self, request: BrandRequest, index: int) -> str:
        """Create a placeholder logo for testing (replace with actual AI generation)"""
        try:
            # Create a simple colored rectangle as placeholder
            color_map = {
                "warm": ["#D2691E", "#CC5500", "#FFB000"],
                "cool": ["#4A90E2", "#357ABD", "#2E86C1"],
                "neutral": ["#6B6B6B", "#8B8B8B", "#A0A0A0"],
                "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
            }
            
            colors = color_map.get(request.color_scheme, ["#333333", "#666666", "#999999"])
            color = colors[index % len(colors)]
            
            # Create a simple logo placeholder
            img = Image.new('RGB', (512, 512), color)
            
            # Convert to base64 data URL for immediate display
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            # Return as data URL for immediate display
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            logger.error(f"Placeholder logo creation failed: {e}")
            return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjY2NjIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzMzMyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkxvZ28gUGxhY2Vob2xkZXI8L3RleHQ+PC9zdmc+"
    
    def _build_sd_prompt(self, request: BrandRequest) -> str:
        """Build optimized Stable Diffusion prompt for logo generation"""
        personality_str = ", ".join(request.personality_traits[:3])
        
        # Base prompt optimized for logo generation
        base_prompt = f"professional logo design, {request.business_name}, {request.industry} company"
        
        # Style modifiers
        style_modifiers = {
            "minimal": "clean minimalist design, simple geometric shapes, flat design",
            "geometric": "geometric shapes, mathematical precision, modern clean lines",
            "text-based": "typography focused, lettering design, font-based logo",
            "symbolic": "symbolic representation, meaningful icons, brand symbols",
            "abstract": "abstract forms, creative interpretation, artistic shapes",
            "classic": "timeless design, traditional elements, elegant composition"
        }
        
        style_desc = style_modifiers.get(request.style, "minimalist design")
        
        # Industry-specific elements
        industry_elements = {
            "technology": "subtle tech elements, digital symbols, innovation themes",
            "healthcare": "medical symbols, care icons, trust elements",
            "education": "knowledge symbols, learning icons, growth elements",
            "finance": "stability symbols, trust icons, prosperity elements",
            "retail": "commerce symbols, shopping icons, consumer appeal",
            "food": "organic shapes, appetite appeal, freshness symbols",
            "fashion": "elegant design, style elements, luxury appeal",
            "automotive": "motion symbols, power elements, reliability icons",
            "real-estate": "stability symbols, home icons, growth elements",
            "consulting": "expertise symbols, guidance icons, professional elements",
            "creative": "artistic elements, creative symbols, imagination icons"
        }
        
        industry_desc = industry_elements.get(request.industry, "professional symbols")
        
        # Quality enhancers
        quality_terms = [
            "high quality vector style",
            "clean white background", 
            "professional branding",
            "scalable design",
            "corporate identity",
            f"{personality_str} personality"
        ]
        
        return f"{base_prompt}, {style_desc}, {industry_desc}, {', '.join(quality_terms)}"
    
    def _build_sd_negative_prompt(self, request: BrandRequest) -> str:
        """Build negative prompt to avoid unwanted elements"""
        negative_elements = [
            "blurry", "pixelated", "low quality", "text artifacts",
            "complex details", "realistic photo", "3d render",
            "multiple logos", "watermark", "signature", "cluttered",
            "amateur", "unprofessional", "distorted", "ugly"
        ]
        
        # Add industry-specific negatives
        industry_negatives = {
            "technology": "circuit boards, gears, lightbulbs, atoms",
            "healthcare": "red crosses, stethoscopes, pills, syringes",
            "education": "graduation caps, apples, books, pencils",
            "finance": "dollar signs, coins, piggy banks, graphs",
            "retail": "shopping carts, price tags, bags",
            "food": "chef hats, forks and knives, plates",
            "fashion": "hangers, mannequins, sewing machines",
            "automotive": "car silhouettes, wheels, keys",
            "real-estate": "house shapes, keys, rooftops",
            "consulting": "handshakes, briefcases, ties",
            "creative": "paint brushes, palettes, easels"
        }
        
        if request.industry in industry_negatives:
            negative_elements.append(industry_negatives[request.industry])
        
        return ", ".join(negative_elements)
    
    def _enhance_logo(self, image: Image.Image) -> Image.Image:
        """Enhance generated logo for professional use"""
        try:
            # Convert to RGBA for transparency support
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Remove background by making white pixels transparent
            data = image.getdata()
            new_data = []
            
            for item in data:
                # Make white and near-white pixels transparent
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))  # Transparent
                else:
                    new_data.append(item)
            
            image.putdata(new_data)
            
            # Apply slight sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=2))
            
            return image
        except Exception as e:
            logger.error(f"Logo enhancement failed: {e}")
            return image
    
    def _image_to_data_url(self, image: Image.Image) -> str:
        """Convert PIL Image to data URL for immediate display"""
        try:
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_data}"
        except Exception as e:
            logger.error(f"Failed to convert image to data URL: {e}")
            return ""
    
    async def _generate_color_palette(self, request: BrandRequest) -> ColorPalette:
        """Generate color palette using Brand Knowledge Graph"""
        logger.info(f"Generating color palette for {request.color_scheme} scheme")
        
        try:
            # Placeholder color palette generation
            # In a real implementation, you would query your KGS for:
            # - Industry-specific color trends
            # - Target audience preferences  
            # - Complementary color relationships
            
            palette_map = {
                "warm": {
                    "primary": "#D2691E",
                    "secondary": "#CC5500", 
                    "accent": "#FFB000",
                    "neutral": "#8B4513"
                },
                "cool": {
                    "primary": "#4A90E2",
                    "secondary": "#357ABD",
                    "accent": "#2E86C1", 
                    "neutral": "#708090"
                },
                "neutral": {
                    "primary": "#6B6B6B",
                    "secondary": "#8B8B8B",
                    "accent": "#A0A0A0",
                    "neutral": "#D3D3D3"
                },
                "vibrant": {
                    "primary": "#FF6B6B",
                    "secondary": "#4ECDC4", 
                    "accent": "#45B7D1",
                    "neutral": "#95A5A6"
                }
            }
            
            colors = palette_map.get(request.color_scheme, palette_map["neutral"])
            
            return ColorPalette(
                primary=colors["primary"],
                secondary=colors["secondary"],
                accent=colors["accent"],
                neutral=colors["neutral"],
                colors=[colors["primary"], colors["secondary"], colors["accent"], colors["neutral"]]
            )
            
        except Exception as e:
            logger.error(f"Color palette generation failed: {e}")
            # Return default palette
            return ColorPalette(
                primary="#333333",
                secondary="#666666", 
                accent="#999999",
                neutral="#CCCCCC",
                colors=["#333333", "#666666", "#999999", "#CCCCCC"]
            )
    
    async def _generate_typography(self, request: BrandRequest) -> Typography:
        """Generate typography recommendations based on brand personality"""
        logger.info("Generating typography recommendations")
        
        try:
            # Font recommendations based on personality and industry
            font_map = {
                ("professional", "technology"): ("Inter", "Roboto"),
                ("creative", "fashion"): ("Playfair Display", "Montserrat"),
                ("friendly", "education"): ("Open Sans", "Lato"),
                ("modern", "technology"): ("Poppins", "Source Sans Pro"),
                ("trustworthy", "finance"): ("Georgia", "Times New Roman"),
                ("innovative", "technology"): ("Helvetica Neue", "Arial"),
            }
            
            # Try to match personality + industry, fallback to personality only
            primary_trait = request.personality_traits[0] if request.personality_traits else "professional"
            key = (primary_trait, request.industry)
            
            if key in font_map:
                primary_font, secondary_font = font_map[key]
            else:
                # Fallback based on personality only
                personality_fonts = {
                    "professional": ("Inter", "Roboto"),
                    "creative": ("Playfair Display", "Montserrat"),
                    "friendly": ("Open Sans", "Lato"),
                    "modern": ("Poppins", "Source Sans Pro"),
                    "trustworthy": ("Georgia", "Times New Roman"),
                    "innovative": ("Helvetica Neue", "Arial")
                }
                primary_font, secondary_font = personality_fonts.get(primary_trait, ("Inter", "Roboto"))
            
            return Typography(
                primary_font=primary_font,
                secondary_font=secondary_font,
                font_family="sans-serif" if primary_font in ["Inter", "Roboto", "Open Sans", "Lato", "Poppins", "Helvetica Neue", "Arial"] else "serif",
                font_style="regular",
                weight="400"
            )
            
        except Exception as e:
            logger.error(f"Typography generation failed: {e}")
            return Typography(
                primary_font="Inter",
                secondary_font="Roboto",
                font_family="sans-serif"
            )
    
    async def _generate_brand_description(self, request: BrandRequest) -> str:
        """Generate brand description using LLM"""
        logger.info("Generating brand description")
        
        try:
            # Placeholder brand description generation
            # In a real implementation, you would use an LLM to generate
            # a comprehensive brand description based on the request
            
            personality_text = ", ".join(request.personality_traits)
            
            description = f"""
{request.business_name} is a {personality_text} {request.industry} company that serves {request.target_audience.replace('-', ' ')}. 

The brand embodies a {request.style} aesthetic with {request.color_scheme} tones, reflecting the company's commitment to innovation and excellence in the {request.industry} sector.

{request.business_name} stands out through its unique approach to combining traditional values with modern solutions, creating a trustworthy yet forward-thinking brand identity that resonates with its target market.
            """.strip()
            
            if request.additional_notes:
                description += f"\n\nAdditional considerations: {request.additional_notes}"
            
            return description
            
        except Exception as e:
            logger.error(f"Brand description generation failed: {e}")
            return f"A {request.industry} company focused on serving {request.target_audience.replace('-', ' ')} with innovative solutions."
    
    async def _enhance_logos(self, logos: List[LogoResult]) -> List[LogoResult]:
        """Apply upscaling and enhancement to logos"""
        logger.info("Enhancing logo quality")
        
        try:
            # Placeholder for image enhancement
            # In a real implementation, you would:
            # 1. Apply your upscaling model
            # 2. Enhance image quality
            # 3. Generate different formats (PNG, SVG, etc.)
            
            enhanced_logos = []
            for logo in logos:
                # For placeholder, just return the same logo
                enhanced_logo = LogoResult(
                    id=logo.id,
                    url=logo.url,
                    thumbnail_url=logo.thumbnail_url,
                    style_confidence=min(logo.style_confidence + 0.05, 1.0),  # Slight improvement
                    quality_score=min(logo.quality_score + 0.05, 1.0),
                    metadata={
                        **logo.metadata,
                        "enhanced": True,
                        "enhancement_applied": "placeholder_enhancement"
                    }
                )
                enhanced_logos.append(enhanced_logo)
                
                # Simulate processing time
                await asyncio.sleep(0.2)
            
            return enhanced_logos
            
        except Exception as e:
            logger.error(f"Logo enhancement failed: {e}")
            return logos  # Return original logos if enhancement fails
    
    def _update_job_progress(self, job_id: str, progress: float, step: str):
        """Update job progress for status tracking"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].update({
                "progress": progress,
                "current_step": step
            })
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get the status of a brand generation job"""
        return self.active_jobs.get(job_id)
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Brand Service...")
        
        try:
            if self.neo4j_driver:
                await self.neo4j_driver.close()
            
            # Cleanup AI models if needed
            
            logger.info("Brand Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
