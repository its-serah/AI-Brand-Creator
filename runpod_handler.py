"""
RunPod Serverless Handler for Stable Diffusion Logo Generation
This runs on RunPod, gets called by AWS
"""

import runpod
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import base64
import io

# Load model once globally
pipe = None

def load_model():
    global pipe
    if pipe is None:
        print("Loading Stable Diffusion model...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",  # More reliable model
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
            pipe.enable_attention_slicing()
        
        print("Model loaded successfully!")
    return pipe

def handler(job):
    """RunPod handler function"""
    try:
        job_input = job["input"]
        
        # Get parameters
        prompt = job_input.get("prompt", "logo design")
        negative_prompt = job_input.get("negative_prompt", "blurry, low quality")
        num_images = job_input.get("num_images", 1)
        width = job_input.get("width", 512)
        height = job_input.get("height", 512)
        steps = job_input.get("steps", 20)
        
        # Load model
        pipeline = load_model()
        
        # Generate images
        images = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_images_per_prompt=num_images,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=7.5
        ).images
        
        # Convert to base64
        results = []
        for img in images:
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            results.append(img_base64)
        
        return {
            "status": "success",
            "images": results,
            "count": len(results)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# RunPod serverless entrypoint
runpod.serverless.start({"handler": handler})
