#!/usr/bin/env python3
"""
Professional Logo Generator - Immediate Use
Downloads Stable Diffusion and generates professional logos
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU usage

try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    import torch
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print(" Install diffusers: pip install diffusers")

from PIL import Image
import requests
import json

class ProfessionalLogoGenerator:
    def __init__(self):
        self.device = "cpu"
        self.pipeline = None
        self.model_loaded = False
        
    def load_model(self):
        """Load Stable Diffusion optimized for CPU"""
        if not DIFFUSERS_AVAILABLE:
            print(" Please install: pip install diffusers torch")
            return False
            
        print(" Loading Stable Diffusion for professional logo generation...")
        print(" First run downloads ~4GB model (one-time setup)")
        print("⏰ This will take 5-15 minutes...")
        
        try:
            # Load with CPU optimizations
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,
                use_safetensors=True,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            # Optimize for CPU
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            # CPU optimizations
            self.pipeline = self.pipeline.to("cpu")
            self.pipeline.enable_attention_slicing()
            
            print(" Model loaded successfully!")
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f" Model loading failed: {e}")
            print(" Check internet connection and try again")
            return False
    
    def create_logo_prompt(self, brand_name, industry, style="modern"):
        """Create professional logo prompt"""
        
        # Industry-specific elements
        industry_prompts = {
            "tech": "technology, circuit patterns, digital, innovation",
            "fitness": "athletic, dumbbell, energy, movement, strength",
            "food": "culinary, chef hat, organic, appetite appeal",
            "fashion": "elegant, luxury, style, boutique, sophisticated",
            "finance": "trust, growth, professional, stability, investment",
            "healthcare": "medical, care, cross symbol, trustworthy, clean",
            "creative": "artistic, imagination, colorful, brush stroke",
            "consulting": "professional, corporate, growth chart, business"
        }
        
        # Style modifiers
        style_prompts = {
            "minimalist": "clean, simple, geometric shapes, white space",
            "modern": "contemporary, sleek, gradient, professional",
            "vintage": "retro, classic, aged, traditional",
            "bold": "strong, impactful, vibrant, eye-catching",
            "elegant": "sophisticated, refined, luxury, premium"
        }
        
        base_prompt = f"professional logo design for {brand_name}"
        industry_desc = industry_prompts.get(industry.lower(), "professional business")
        style_desc = style_prompts.get(style.lower(), "modern professional")
        
        # High-quality logo prompt
        prompt = f"{base_prompt}, {industry_desc}, {style_desc}, vector style logo, clean typography, corporate branding, scalable design, high quality, business logo, flat design, professional identity"
        
        negative_prompt = "blurry, pixelated, low quality, photorealistic, complex details, 3d render, multiple logos, text artifacts, watermark, signature, cluttered, busy background"
        
        return prompt, negative_prompt
    
    def generate_logo(self, brand_name, industry, style="modern", num_logos=2):
        """Generate professional logo"""
        
        if not self.model_loaded:
            if not self.load_model():
                return []
        
        prompt, negative_prompt = self.create_logo_prompt(brand_name, industry, style)
        
        print(f"\n Generating {num_logos} professional logo(s) for {brand_name}...")
        print(f" Industry: {industry}")
        print(f" Style: {style}")
        print(f"⏰ Estimated time: {num_logos * 3}-{num_logos * 8} minutes")
        print(f" Prompt: {prompt[:80]}...")
        
        try:
            # Generate with CPU-optimized settings
            images = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_images_per_prompt=num_logos,
                num_inference_steps=25,  # Good quality vs speed
                guidance_scale=7.5,
                width=512,
                height=512,
                generator=torch.manual_seed(42)  # Reproducible
            ).images
            
            print(f" Successfully generated {len(images)} professional logo(s)!")
            return images
            
        except Exception as e:
            print(f" Logo generation failed: {e}")
            return []
    
    def save_logos(self, images, brand_name, industry, style):
        """Save generated logos with metadata"""
        
        if not images:
            return []
        
        # Create output directory
        output_dir = f"./{brand_name.lower()}_professional_logos"
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        for i, img in enumerate(images, 1):
            # Save original
            filename = f"{output_dir}/{brand_name.lower()}_{style}_{industry}_logo_{i}.png"
            img.save(filename, "PNG", quality=95)
            saved_files.append(filename)
            print(f" Saved: {filename}")
        
        # Save metadata
        metadata = {
            "brand_name": brand_name,
            "industry": industry,
            "style": style,
            "generated_logos": len(images),
            "files": saved_files,
            "model": "stable-diffusion-v1-5",
            "resolution": "512x512"
        }
        
        metadata_file = f"{output_dir}/{brand_name.lower()}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f" Metadata saved: {metadata_file}")
        return saved_files

def generate_concept_with_ollama(brand_name, industry):
    """Get AI concept from Ollama"""
    prompt = f"Create a professional logo design concept for {brand_name}, a {industry} company. Include visual elements, colors, and style recommendations in 2-3 sentences."
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.6, "max_tokens": 150}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["response"].strip()
    except:
        pass
    
    return f"Modern {industry} logo with clean typography and professional color scheme"

def main():
    print(" PROFESSIONAL LOGO GENERATOR")
    print("=" * 50)
    print("Generate high-quality AI logos using Stable Diffusion")
    print("Optimized for your AMD Ryzen 5 6600U laptop")
    
    if not DIFFUSERS_AVAILABLE:
        print("\n Missing requirements!")
        print("Install with: pip install diffusers torch")
        return
    
    generator = ProfessionalLogoGenerator()
    
    # Get user input
    print("\n" + "=" * 30)
    brand_name = input("Enter brand name: ").strip()
    if not brand_name:
        brand_name = "TechCorp"
        print(f"Using default: {brand_name}")
    
    print("\nIndustry options: tech, fitness, food, fashion, finance, healthcare, creative, consulting")
    industry = input("Enter industry: ").strip().lower()
    if not industry:
        industry = "tech"
        print(f"Using default: {industry}")
    
    print("\nStyle options: minimalist, modern, vintage, bold, elegant")
    style = input("Enter style: ").strip().lower()
    if not style:
        style = "modern"
        print(f"Using default: {style}")
    
    num_logos = input("\nHow many logos to generate? (1-3, default 2): ").strip()
    try:
        num_logos = max(1, min(3, int(num_logos)))
    except:
        num_logos = 2
    
    print(f"\n GENERATING LOGOS FOR: {brand_name.upper()}")
    print(f" Industry: {industry}")
    print(f" Style: {style}")
    print(f" Quantity: {num_logos}")
    
    # Get AI concept
    print(f"\n Getting design concept from Ollama...")
    concept = generate_concept_with_ollama(brand_name, industry)
    print(f" Concept: {concept}")
    
    # Generate logos
    print(f"\n Starting professional logo generation...")
    print(f"  First run downloads ~4GB model")
    
    confirm = input("\nProceed with generation? (y/n): ").lower()
    if confirm != 'y':
        print("Logo generation cancelled.")
        return
    
    images = generator.generate_logo(brand_name, industry, style, num_logos)
    
    if images:
        # Save logos
        saved_files = generator.save_logos(images, brand_name, industry, style)
        
        print(f"\n SUCCESS! Generated {len(images)} professional logos")
        print(f" Saved to: ./{brand_name.lower()}_professional_logos/")
        print(f"\n Generated files:")
        for file in saved_files:
            print(f"   • {file}")
        
        print(f"\n Logo files are ready to use!")
        print(f" Open them in any image viewer or design software")
        
    else:
        print(f"\n Logo generation failed")
        print(f" Check internet connection and try again")

if __name__ == "__main__":
    main()
