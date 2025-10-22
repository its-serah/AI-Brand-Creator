"""
RunPod Handler for Your AI Brand Creator
Uses your sophisticated brand generation system
"""

import runpod
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageEnhance, ImageFilter
import base64
import io
import os

# Load model once globally
pipe = None

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

def enhance_logo(img):
    """Apply your logo enhancement pipeline"""
    try:
        # Sharpen the image
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        # Enhance contrast  
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Apply slight unsharp mask
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        
        return img
    except Exception as e:
        print(f"Enhancement failed: {e}")
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
        
        # Apply your enhancement pipeline
        enhanced_img = enhance_logo(img)
        
        # Convert to base64
        buffer = io.BytesIO()
        enhanced_img.save(buffer, format='PNG', quality=95)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "status": "success",
            "images": [img_base64],
            "prompt_used": brand_prompt,
            "industry": industry,
            "style": style,
            "enhanced": True,
            "resolution": "1024x1024"
        }
        
    except Exception as e:
        print(f"Brand generation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    print("Starting AI Brand Creator RunPod handler...")
    runpod.serverless.start({"handler": handler})
