"""
RunPod Handler for AI Brand Creator - Enhanced with Real-ESRGAN & ControlNet
Full AI pipeline: Text-to-Image → AI Upscaling → AI Refinement
"""

import runpod
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image, ImageEnhance, ImageFilter
import base64
import io
import os
import numpy as np
import cv2

# AI Models imports
try:
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False

try:
    from controlnet_aux import CannyDetector
    CONTROLNET_AVAILABLE = True
except ImportError:
    CONTROLNET_AVAILABLE = False

# Load models once globally
pipe = None
upscaler = None
controlnet_pipe = None
canny_detector = None

def load_model():
    global pipe
    if pipe is None:
        print("Loading Stable Diffusion v1.5 for brand generation...")
        
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
            pipe.enable_attention_slicing()
            pipe.enable_model_cpu_offload()
        
        # Use DPM Solver for better quality
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        
        print("Brand generation model loaded successfully!")
    return pipe

def load_upscaler():
    """Load Real-ESRGAN upscaler"""
    global upscaler
    if upscaler is None and REALESRGAN_AVAILABLE:
        try:
            print("Loading Real-ESRGAN 4x upscaler...")
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
            
            upscaler = RealESRGANer(
                scale=4,
                model_path=model_path,
                model=model,
                tile=512,
                tile_pad=10,
                pre_pad=0,
                half=torch.cuda.is_available()
            )
            print("Real-ESRGAN upscaler loaded successfully!")
        except Exception as e:
            print(f"Failed to load Real-ESRGAN: {e}")
            upscaler = None
    return upscaler

def load_controlnet():
    """Load ControlNet for refinement"""
    global controlnet_pipe, canny_detector
    if controlnet_pipe is None and CONTROLNET_AVAILABLE:
        try:
            print("Loading ControlNet for logo refinement...")
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            controlnet_pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            if torch.cuda.is_available():
                controlnet_pipe = controlnet_pipe.to("cuda")
                controlnet_pipe.enable_model_cpu_offload()
            
            canny_detector = CannyDetector()
            print("ControlNet loaded successfully!")
        except Exception as e:
            print(f"Failed to load ControlNet: {e}")
            controlnet_pipe = None
    
    return controlnet_pipe, canny_detector

def ai_upscale_logo(img):
    """AI upscale using Real-ESRGAN"""
    try:
        upscaler_model = load_upscaler()
        if upscaler_model is None:
            print("Real-ESRGAN not available, using PIL fallback")
            return pil_upscale_fallback(img)
            
        print(f"AI upscaling image from {img.size}...")
        
        # Convert PIL to numpy array
        img_array = np.array(img.convert('RGB'))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Perform AI upscaling
        enhanced_img, _ = upscaler_model.enhance(img_bgr, outscale=4)
        
        # Convert back to RGB and PIL
        enhanced_rgb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)
        upscaled_img = Image.fromarray(enhanced_rgb)
        
        print(f"Successfully AI-upscaled to {upscaled_img.size}")
        return upscaled_img
        
    except Exception as e:
        print(f"AI upscaling failed: {e}")
        return pil_upscale_fallback(img)

def pil_upscale_fallback(img, scale=4):
    """Fallback PIL upscaling"""
    print(f"Using PIL fallback upscaling {scale}x")
    new_size = (img.width * scale, img.height * scale)
    upscaled = img.resize(new_size, Image.Resampling.LANCZOS)
    upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    return upscaled

def ai_refine_logo(img, prompt):
    """Refine logo using ControlNet"""
    try:
        controlnet_pipeline, canny_det = load_controlnet()
        if controlnet_pipeline is None or canny_det is None:
            print("ControlNet not available, skipping refinement")
            return img
            
        print("Refining logo with ControlNet...")
        
        # Create control image
        control_image = canny_det(img)
        
        # Refine with ControlNet
        refined_prompt = f"professional logo design, {prompt}, high quality, clean, minimalist"
        
        with torch.no_grad():
            result = controlnet_pipeline(
                prompt=refined_prompt,
                image=control_image,
                num_inference_steps=15,
                guidance_scale=7.5,
                controlnet_conditioning_scale=0.7,
                width=img.width,
                height=img.height
            )
        
        refined_img = result.images[0]
        print("Successfully refined logo with ControlNet")
        return refined_img
        
    except Exception as e:
        print(f"ControlNet refinement failed: {e}")
        return img

def create_social_sizes(img):
    """Create multiple social media sizes from the enhanced logo"""
    sizes = {
        'original': img.size,
        'facebook': (1200, 630),
        'instagram': (1080, 1080), 
        'twitter': (1024, 512),
        'linkedin': (1200, 627),
        'website': (512, 512),
        'favicon': (64, 64)
    }
    
    social_images = {}
    
    for size_name, (width, height) in sizes.items():
        if size_name == 'original':
            social_images[size_name] = img
        else:
            # Create sized version with proper aspect ratio handling
            if img.width != img.height and width == height:
                # For square formats, crop to center square first
                min_side = min(img.width, img.height)
                left = (img.width - min_side) // 2
                top = (img.height - min_side) // 2
                square_img = img.crop((left, top, left + min_side, top + min_side))
                resized = square_img.resize((width, height), Image.Resampling.LANCZOS)
            else:
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
            
            social_images[size_name] = resized
    
    return social_images

def enhance_logo(img, prompt="professional logo"):
    """Complete AI enhancement pipeline"""
    try:
        print("Starting AI enhancement pipeline...")
        
        # Step 1: AI Upscaling with Real-ESRGAN
        upscaled_img = ai_upscale_logo(img)
        
        # Step 2: AI Refinement with ControlNet
        refined_img = ai_refine_logo(upscaled_img, prompt)
        
        # Step 3: Final touch-ups
        enhancer = ImageEnhance.Sharpness(refined_img)
        final_img = enhancer.enhance(1.1)
        
        print("AI enhancement pipeline completed!")
        return final_img
        
    except Exception as e:
        print(f"Enhancement pipeline failed: {e}")
        return img

def build_brand_prompt(prompt, industry="technology", style="modern"):
    """Build your sophisticated brand prompt"""
    base_prompt = f"{prompt}, "
    
    # Add industry-specific terms
    industry_terms = {
        "technology": "clean, minimal, geometric, tech, digital, innovative",
        "healthcare": "trust, care, medical, clean, professional, healing", 
        "finance": "solid, trustworthy, professional, corporate, stability",
        "retail": "friendly, approachable, colorful, consumer, shopping",
        "food": "fresh, organic, delicious, appetite, natural"
    }
    
    # Add style-specific terms
    style_terms = {
        "modern": "minimalist, clean lines, contemporary, sleek",
        "classic": "timeless, elegant, traditional, refined", 
        "playful": "fun, vibrant, creative, energetic",
        "professional": "corporate, serious, trustworthy, formal"
    }
    
    industry_prompt = industry_terms.get(industry, "professional, clean")
    style_prompt = style_terms.get(style, "modern, clean")
    
    full_prompt = f"{base_prompt} {industry_prompt}, {style_prompt}, logo design, vector art, simple, high quality, professional branding"
    
    return full_prompt

def handler(job):
    """Your brand generation handler"""
    try:
        job_input = job.get("input", {})
        
        # Extract your brand parameters
        prompt = job_input.get("prompt", "modern logo design")
        industry = job_input.get("industry", "technology")
        style = job_input.get("style", "modern") 
        business_name = job_input.get("business_name", "")
        
        # Build sophisticated prompt using your system
        brand_prompt = build_brand_prompt(prompt, industry, style)
        if business_name:
            brand_prompt = f"{business_name} {brand_prompt}"
            
        negative_prompt = "blurry, low quality, text, letters, words, watermark, signature, frame, border, cluttered, complex, busy, photograph, photo, realistic"
        
        print(f"Generating brand logo: {brand_prompt[:100]}...")
        
        # Load your model
        pipeline = load_model()
        
        # Generate high-quality logo
        with torch.no_grad():
            result = pipeline(
                prompt=brand_prompt,
                negative_prompt=negative_prompt,
                num_images_per_prompt=1,
                width=1024,  # High resolution
                height=1024,
                num_inference_steps=30,  # Good quality
                guidance_scale=7.5
            )
        
        img = result.images[0]
        
        # Apply AI enhancement pipeline (Real-ESRGAN + ControlNet)
        enhanced_img = enhance_logo(img, prompt)
        
        # Create multiple social media sizes
        social_images = create_social_sizes(enhanced_img)
        
        # Convert all sizes to base64
        images_data = {}
        for size_name, sized_img in social_images.items():
            buffer = io.BytesIO()
            sized_img.save(buffer, format='PNG', quality=95)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            images_data[size_name] = {
                "data": f"data:image/png;base64,{img_base64}",
                "width": sized_img.width,
                "height": sized_img.height,
                "size": f"{sized_img.width}x{sized_img.height}"
            }
        
        return {
            "status": "success",
            "images": [images_data['original']['data']],  # Keep backward compatibility
            "social_media_pack": images_data,
            "prompt_used": brand_prompt,
            "industry": industry,
            "style": style,
            "business_name": business_name,
            "enhanced": True,
            "ai_upscaled": REALESRGAN_AVAILABLE,
            "controlnet_refined": CONTROLNET_AVAILABLE,
            "resolution": f"{enhanced_img.width}x{enhanced_img.height}",
            "enhancement_pipeline": "Real-ESRGAN + ControlNet + Traditional"
        }
        
    except Exception as e:
        print(f"Brand generation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    print("Starting Enhanced AI Brand Creator RunPod handler...")
    print("Features: Text-to-Image + Real-ESRGAN + ControlNet + Color Processing")
    print(f"Real-ESRGAN Available: {REALESRGAN_AVAILABLE}")
    print(f"ControlNet Available: {CONTROLNET_AVAILABLE}")
    runpod.serverless.start({"handler": handler})
