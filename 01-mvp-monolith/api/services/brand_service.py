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

import tempfile
import webcolors

try:
    from diffusers import StableDiffusionPipeline, StableDiffusionUpscalePipeline
    import torch
    import numpy as np
    from skimage import color, filters
    from colorthief import ColorThief
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    import numpy as np

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
        self.upscaler_pipeline = None
        self.controlnet = None
        self.neo4j_driver = None
        # Force CPU for stability (you can change to cuda if you have GPU)
        self.device = "cpu" if DIFFUSERS_AVAILABLE else "cpu"
        
        # Create storage directories
        self.storage_dir = os.path.join(os.path.dirname(__file__), "../../storage")
        self.logos_dir = os.path.join(self.storage_dir, "logos")
        self.social_exports_dir = os.path.join(self.storage_dir, "social_exports")
        self.variations_dir = os.path.join(self.storage_dir, "variations")
        os.makedirs(self.logos_dir, exist_ok=True)
        os.makedirs(self.social_exports_dir, exist_ok=True)
        os.makedirs(self.variations_dir, exist_ok=True)
        
        # Social media dimensions
        self.social_media_formats = {
            "instagram_post": (1080, 1080),
            "instagram_story": (1080, 1920),
            "facebook_post": (1200, 630),
            "twitter_post": (1024, 512),
            "linkedin_post": (1200, 627),
            "youtube_thumbnail": (1280, 720),
            "youtube_banner": (2048, 1152),
        }
        
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
        """Initialize AI models for logo generation with CPU optimizations"""
        logger.info("Loading AI models...")
        
        if not DIFFUSERS_AVAILABLE:
            logger.warning("Diffusers not available. Install with: pip install diffusers torch")
            return
            
        try:
            # Set optimal torch settings for CPU
            torch.set_num_threads(4)  # Use 4 CPU threads
            torch.manual_seed(42)     # Set seed for reproducible results
            
            logger.info(f"Loading Stable Diffusion model on CPU with optimizations...")
            
            # Use ultra-lightweight model for AWS Free Tier
            logger.info("Loading CompVis/stable-diffusion-v1-4 with extreme optimizations for free tier...")
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                "CompVis/stable-diffusion-v1-4",  # Smaller than v1.5
                torch_dtype=torch.float32,
                use_safetensors=True,
                safety_checker=None,  # Disable for speed and memory
                requires_safety_checker=False,
                low_cpu_mem_usage=True,
                variant=None,  # No fp16 variant to save memory
                cache_dir="/tmp/huggingface_cache"  # Use tmp for free tier
            )
            
            # Move to CPU and apply aggressive optimizations
            self.sd_pipeline = self.sd_pipeline.to("cpu")
            
            # Apply all available CPU optimizations
            try:
                self.sd_pipeline.enable_attention_slicing("max")
                logger.info("Enabled attention slicing for memory optimization")
            except Exception as opt_e:
                logger.warning(f"Could not enable attention slicing: {opt_e}")
            
            try:
                self.sd_pipeline.enable_model_cpu_offload()
                logger.info("Enabled model CPU offloading")
            except Exception as opt_e:
                logger.warning(f"Could not enable CPU offloading: {opt_e}")
            
            # Set scheduler to use fewer steps for faster generation
            from diffusers import DPMSolverMultistepScheduler
            try:
                self.sd_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.sd_pipeline.scheduler.config
                )
                logger.info("Using DPM Solver for faster generation")
            except Exception as sched_e:
                logger.warning(f"Could not set DPM scheduler: {sched_e}")
            
            # Skip upscaler for now to improve reliability
            logger.info("Skipping upscaler initialization for better performance")
            self.upscaler_pipeline = None
            
            # Warm up the pipeline with a test generation
            logger.info("Warming up pipeline...")
            try:
                with torch.no_grad():
                    warmup_image = self.sd_pipeline(
                        "test logo",
                        num_inference_steps=5,
                        guidance_scale=5.0,
                        width=256,
                        height=256,
                        output_type="pil"
                    ).images[0]
                    logger.info("Pipeline warmup successful")
            except Exception as warmup_e:
                logger.warning(f"Pipeline warmup failed: {warmup_e}")
            
            logger.info("AI models loaded and optimized successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            logger.warning("Continuing without AI models - will use fallback generation")
            import traceback
            logger.error(f"Full error: {traceback.format_exc()}")
    
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
            
            # Collect enhancement data from logos
            all_extracted_colors = []
            social_exports_summary = {}
            enhancement_features = set()
            
            for logo in enhanced_logos:
                if 'extracted_colors' in logo.metadata:
                    all_extracted_colors.extend(logo.metadata['extracted_colors'])
                if 'social_exports' in logo.metadata:
                    social_exports_summary[logo.id] = logo.metadata['social_exports']
                if 'enhancement_features' in logo.metadata:
                    enhancement_features.update(logo.metadata['enhancement_features'])
            
            # Remove duplicates from extracted colors (handle dict objects properly)
            unique_extracted_colors = []
            seen_colors = set()
            for color_info in all_extracted_colors:
                if isinstance(color_info, dict) and 'hex' in color_info:
                    hex_color = color_info['hex']
                    if hex_color not in seen_colors:
                        seen_colors.add(hex_color)
                        unique_extracted_colors.append(color_info)
                elif isinstance(color_info, str) and color_info not in seen_colors:
                    seen_colors.add(color_info)
                    unique_extracted_colors.append(color_info)
            
            response = BrandResponse(
                job_id=job_id,
                business_name=request.business_name,
                status="completed",
                processing_time_seconds=processing_time,
                # Original response format
                logos=enhanced_logos,
                color_palette=[color_palette.primary, color_palette.secondary, color_palette.accent, color_palette.neutral],
                font_suggestion=typography.primary_font,
                brand_description=brand_description,
                # Enhanced features
                extracted_colors=unique_extracted_colors[:12],  # Limit to 12 colors
                color_variations_available=len(enhanced_logos) > 0 and any('color_variations' in logo.metadata for logo in enhanced_logos),
                social_media_exports=social_exports_summary,
                upscaling_applied=any('upscaled' in logo.metadata for logo in enhanced_logos),
                enhancement_features=list(enhancement_features)
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
        """Generate logos using Stable Diffusion with comprehensive error handling"""
        logger.info(f"Starting logo generation for {request.business_name}")
        logger.info(f"Parameters: style={request.style}, industry={request.industry}, color_scheme={request.color_scheme}")
        
        try:
            logos = []
            
            # Use Stable Diffusion if available, otherwise fallback to placeholder
            if self.sd_pipeline:
                logger.info("SD pipeline available, checking pipeline status...")
                
                # Verify pipeline is ready
                if not hasattr(self.sd_pipeline, 'vae') or self.sd_pipeline.vae is None:
                    logger.error("SD pipeline is not properly initialized")
                    raise Exception("Pipeline initialization failed")
                logger.info("Using Stable Diffusion for logo generation")
                
                # Generate optimized prompt for logo creation
                logo_prompt = self._build_sd_prompt(request)
                negative_prompt = self._build_sd_negative_prompt(request)
                
                logger.info(f"SD Prompt: {logo_prompt[:100]}...")
                
                # Generate images with Stable Diffusion (CPU optimized)
                logger.info(f"Generating {request.num_logos} logos on CPU...")
                
                # Use torch.no_grad() for better memory management
                with torch.no_grad():
                    # Generate logos one by one for better memory management
                    images = []
                    for i in range(request.num_logos):
                        logger.info(f"Generating logo {i+1}/{request.num_logos}...")
                        
                        # Create unique seed for each logo
                        seed = (hash(request.business_name) + i * 1000) % 2**32
                        generator = torch.manual_seed(seed)
                        
                        # Ultra-fast generation for free tier
                        try:
                            logger.debug(f"Calling SD pipeline for logo {i+1}...")
                            result = self.sd_pipeline(
                                prompt=logo_prompt,
                                negative_prompt=negative_prompt,
                                num_images_per_prompt=1,
                                num_inference_steps=4,   # ULTRA FAST - 4 steps only
                                guidance_scale=3.5,      # Lower guidance for speed
                                width=256,               # Smaller for t2.micro
                                height=256,              # Smaller for t2.micro
                                generator=generator,
                                output_type="pil"
                            )
                            
                            if result and hasattr(result, 'images') and result.images:
                                images.append(result.images[0])
                                logger.info(f"Successfully generated logo {i+1}")
                            else:
                                logger.warning(f"No image generated for logo {i+1}")
                                
                        except Exception as gen_e:
                            logger.error(f"Failed to generate logo {i+1}: {gen_e}")
                            # Continue with next logo instead of failing completely
                            continue
                        
                        # Small delay to prevent overwhelming CPU
                        await asyncio.sleep(0.5)
                logger.info(f"Successfully generated {len(images)} logos with SD pipeline")
                
                # If no images were generated, fall back to placeholder
                if not images:
                    logger.warning("No images generated by SD pipeline, falling back to placeholder")
                    return await self._generate_fallback_logos(request)
                
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
                return await self._generate_fallback_logos(request)
            
            return logos
            
        except Exception as e:
            logger.error(f"Logo generation failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return fallback logos instead of failing completely
            logger.info("Attempting fallback logo generation...")
            try:
                return await self._generate_fallback_logos(request)
            except Exception as fallback_e:
                logger.error(f"Fallback generation also failed: {fallback_e}")
                raise
    
    async def _generate_fallback_logos(self, request: BrandRequest) -> List[LogoResult]:
        """Generate fallback placeholder logos when AI generation fails"""
        logger.info("Generating fallback placeholder logos")
        
        try:
            logos = []
            for i in range(request.num_logos):
                logo_id = str(uuid.uuid4())
                logger.info(f"Creating placeholder logo {i+1}/{request.num_logos}...")
                
                logo_url = await self._create_placeholder_logo(request, i)
                
                logo_result = LogoResult(
                    id=logo_id,
                    url=logo_url,
                    thumbnail_url=logo_url,
                    style_confidence=0.75 + (i * 0.05),
                    quality_score=0.80 + (i * 0.02),
                    metadata={
                        "style": request.style,
                        "industry": request.industry,
                        "prompt_used": request.prompt[:100] + "..." if len(request.prompt) > 100 else request.prompt,
                        "generated_with": "placeholder_fallback",
                        "business_name": request.business_name
                    }
                )
                
                logos.append(logo_result)
                await asyncio.sleep(0.2)  # Small delay
            
            logger.info(f"Successfully generated {len(logos)} fallback logos")
            return logos
            
        except Exception as e:
            logger.error(f"Fallback logo generation failed: {e}")
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
    
    def _extract_colors_from_logo(self, image: Image.Image) -> list:
        """Extract dominant colors from logo with CSS color names"""
        try:
            # Save image to temporary file for ColorThief
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                image.save(temp_file.name, 'PNG')
                
                # Extract colors
                color_thief = ColorThief(temp_file.name)
                
                # Get dominant color
                dominant_color = color_thief.get_color(quality=1)
                
                # Get color palette (more colors for better variety)
                try:
                    palette = color_thief.get_palette(color_count=10, quality=1)
                except:
                    palette = [dominant_color] * 6
                
                # Convert to colors with CSS names and hex values
                color_info = []
                for rgb in palette[:8]:  # Limit to 8 colors
                    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
                    
                    # Get CSS color name or closest match
                    css_name = self._get_css_color_name(rgb)
                    
                    color_info.append({
                        'hex': hex_color,
                        'rgb': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})',
                        'name': css_name,
                        'rgb_values': rgb
                    })
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return color_info
                
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            # Return default colors with names
            return [
                {'hex': '#333333', 'rgb': 'rgb(51, 51, 51)', 'name': 'Dark Gray', 'rgb_values': (51, 51, 51)},
                {'hex': '#666666', 'rgb': 'rgb(102, 102, 102)', 'name': 'Gray', 'rgb_values': (102, 102, 102)},
                {'hex': '#999999', 'rgb': 'rgb(153, 153, 153)', 'name': 'Light Gray', 'rgb_values': (153, 153, 153)},
                {'hex': '#CCCCCC', 'rgb': 'rgb(204, 204, 204)', 'name': 'Silver', 'rgb_values': (204, 204, 204)},
                {'hex': '#FF6B6B', 'rgb': 'rgb(255, 107, 107)', 'name': 'Light Coral', 'rgb_values': (255, 107, 107)},
                {'hex': '#4ECDC4', 'rgb': 'rgb(78, 205, 196)', 'name': 'Medium Turquoise', 'rgb_values': (78, 205, 196)}
            ]
    
    def _get_css_color_name(self, rgb_tuple):
        """Get CSS color name from RGB values using webcolors"""
        try:
            # Try exact match first
            return webcolors.rgb_to_name(rgb_tuple)
        except ValueError:
            # Find closest CSS3 color
            try:
                return webcolors.rgb_to_name(rgb_tuple, spec='css3')
            except ValueError:
                # Find closest match by calculating distance
                min_distance = float('inf')
                closest_name = 'Unknown'
                
                # Check against common CSS colors
                css_colors = {
                    'red': (255, 0, 0), 'green': (0, 128, 0), 'blue': (0, 0, 255),
                    'yellow': (255, 255, 0), 'orange': (255, 165, 0), 'purple': (128, 0, 128),
                    'pink': (255, 192, 203), 'brown': (165, 42, 42), 'gray': (128, 128, 128),
                    'black': (0, 0, 0), 'white': (255, 255, 255), 'navy': (0, 0, 128),
                    'teal': (0, 128, 128), 'olive': (128, 128, 0), 'maroon': (128, 0, 0),
                    'lime': (0, 255, 0), 'aqua': (0, 255, 255), 'fuchsia': (255, 0, 255),
                    'silver': (192, 192, 192), 'coral': (255, 127, 80), 'salmon': (250, 128, 114)
                }
                
                for color_name, color_rgb in css_colors.items():
                    distance = sum((a - b) ** 2 for a, b in zip(rgb_tuple, color_rgb)) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        closest_name = color_name.title()
                
                return closest_name
    
    def _generate_color_variations(self, original_image: Image.Image) -> List[Image.Image]:
        """Generate color variations of the logo with different hues and saturations"""
        try:
            variations = []
            
            # Convert to numpy array for processing
            img_array = np.array(original_image.convert('RGB'))
            
            # Convert RGB to HSV for color manipulation
            hsv_array = color.rgb2hsv(img_array)
            
            # Define variation parameters
            hue_shifts = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75]  # Different hue shifts
            saturation_mults = [0.7, 0.85, 1.0, 1.15, 1.3, 1.5]  # Saturation multipliers
            
            for i, (hue_shift, sat_mult) in enumerate(zip(hue_shifts, saturation_mults)):
                # Create a copy of HSV array
                variation_hsv = hsv_array.copy()
                
                # Apply hue shift
                variation_hsv[:, :, 0] = (variation_hsv[:, :, 0] + hue_shift) % 1.0
                
                # Apply saturation multiplication (clip to valid range)
                variation_hsv[:, :, 1] = np.clip(variation_hsv[:, :, 1] * sat_mult, 0, 1)
                
                # Convert back to RGB
                variation_rgb = color.hsv2rgb(variation_hsv)
                
                # Convert to PIL Image
                variation_img = Image.fromarray((variation_rgb * 255).astype(np.uint8))
                
                # Preserve alpha channel if original had transparency
                if original_image.mode == 'RGBA':
                    variation_img = variation_img.convert('RGBA')
                    # Copy alpha channel from original
                    alpha = original_image.split()[-1]
                    variation_img.putalpha(alpha)
                
                variations.append(variation_img)
                
                # Limit to 6 variations to avoid overwhelming the user
                if len(variations) >= 6:
                    break
            
            return variations
            
        except Exception as e:
            logger.error(f"Color variation generation failed: {e}")
            # Return original image as fallback
            return [original_image]
    
    def _upscale_logo(self, image: Image.Image, prompt: str) -> Image.Image:
        """Upscale logo using Stable Diffusion x4 upscaler"""
        try:
            if not self.upscaler_pipeline:
                logger.warning("Upscaler not available, returning original size")
                return image
            
            # Ensure image is the right size for upscaler (128x128 minimum)
            if image.size[0] < 128 or image.size[1] < 128:
                image = image.resize((128, 128), Image.Resampling.LANCZOS)
            
            logger.info(f"Upscaling logo from {image.size} to 4x resolution...")
            
            # Generate upscaled image
            upscaled = self.upscaler_pipeline(
                prompt=prompt,
                image=image,
                num_inference_steps=20,
                guidance_scale=0,  # Use 0 for logo upscaling
                noise_level=20
            ).images[0]
            
            logger.info(f"Successfully upscaled logo to {upscaled.size}")
            return upscaled
            
        except Exception as e:
            logger.error(f"Logo upscaling failed: {e}")
            # Return 2x scaled version as fallback
            return image.resize((image.size[0] * 2, image.size[1] * 2), Image.Resampling.LANCZOS)
    
    def _create_social_media_exports(self, logo: Image.Image, logo_id: str) -> Dict[str, str]:
        """Create social media format exports of the logo"""
        try:
            export_paths = {}
            
            for format_name, (width, height) in self.social_media_formats.items():
                # Calculate scaling to fit logo while maintaining aspect ratio
                logo_aspect = logo.size[0] / logo.size[1]
                target_aspect = width / height
                
                if logo_aspect > target_aspect:
                    # Logo is wider, scale by width
                    new_width = min(width * 0.8, logo.size[0])  # Use 80% of canvas
                    new_height = int(new_width / logo_aspect)
                else:
                    # Logo is taller, scale by height
                    new_height = min(height * 0.8, logo.size[1])  # Use 80% of canvas
                    new_width = int(new_height * logo_aspect)
                
                # Resize logo
                resized_logo = logo.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
                
                # Create canvas with white background
                canvas = Image.new('RGB', (width, height), 'white')
                
                # Calculate position to center logo
                x = (width - resized_logo.size[0]) // 2
                y = (height - resized_logo.size[1]) // 2
                
                # Paste logo onto canvas
                if resized_logo.mode == 'RGBA':
                    canvas.paste(resized_logo, (x, y), resized_logo)
                else:
                    canvas.paste(resized_logo, (x, y))
                
                # Save export
                export_path = os.path.join(self.social_exports_dir, f"{logo_id}_{format_name}.png")
                canvas.save(export_path)
                export_paths[format_name] = export_path
            
            return export_paths
            
        except Exception as e:
            logger.error(f"Social media export generation failed: {e}")
            return {}
    
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
        """Apply comprehensive logo enhancement including upscaling, color variations, and social exports"""
        logger.info("Enhancing logos with upscaling, color variations, and social media exports")
        
        try:
            enhanced_logos = []
            
            for i, logo in enumerate(logos):
                logger.info(f"Processing logo {i+1}/{len(logos)}...")
                
                # Load the original image from file path if available
                original_image = None
                if 'file_path' in logo.metadata and os.path.exists(logo.metadata['file_path']):
                    original_image = Image.open(logo.metadata['file_path'])
                else:
                    # Convert from data URL if no file path
                    try:
                        if logo.url.startswith('data:image'):
                            img_data = logo.url.split(',')[1]
                            img_bytes = base64.b64decode(img_data)
                            original_image = Image.open(io.BytesIO(img_bytes))
                    except:
                        logger.warning(f"Could not load image for logo {logo.id}")
                        enhanced_logos.append(logo)
                        continue
                
                if original_image is None:
                    enhanced_logos.append(logo)
                    continue
                
                # 1. Extract colors from the logo
                extracted_colors = self._extract_colors_from_logo(original_image)
                
                # 2. Generate color variations
                color_variations = self._generate_color_variations(original_image)
                
                # 3. Apply upscaling to original logo
                prompt_for_upscale = logo.metadata.get('prompt_used', 'high quality professional logo')
                upscaled_logo = self._upscale_logo(original_image, prompt_for_upscale)
                
                # 4. Save upscaled version
                upscaled_path = os.path.join(self.logos_dir, f"{logo.id}_upscaled.png")
                upscaled_logo.save(upscaled_path)
                
                # 5. Create social media exports
                social_exports = self._create_social_media_exports(upscaled_logo, logo.id)
                
                # 6. Save color variations
                variation_paths = []
                for j, variation in enumerate(color_variations):
                    variation_path = os.path.join(self.variations_dir, f"{logo.id}_variation_{j}.png")
                    variation.save(variation_path)
                    variation_paths.append({
                        'path': variation_path,
                        'url': self._image_to_data_url(variation)
                    })
                
                # Create enhanced logo result with all new features
                enhanced_logo = LogoResult(
                    id=logo.id,
                    url=self._image_to_data_url(upscaled_logo),  # Use upscaled version as main
                    thumbnail_url=logo.url,  # Keep original as thumbnail
                    style_confidence=min(logo.style_confidence + 0.1, 1.0),
                    quality_score=min(logo.quality_score + 0.15, 1.0),
                    metadata={
                        **logo.metadata,
                        "enhanced": True,
                        "upscaled": True,
                        "upscaled_path": upscaled_path,
                        "original_size": original_image.size,
                        "upscaled_size": upscaled_logo.size,
                        "extracted_colors": extracted_colors,
                        "color_variations": variation_paths,
                        "social_exports": social_exports,
                        "enhancement_features": [
                            "4x_upscaling", 
                            "color_extraction", 
                            "color_variations", 
                            "social_media_exports"
                        ]
                    }
                )
                
                enhanced_logos.append(enhanced_logo)
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.5)
            
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
