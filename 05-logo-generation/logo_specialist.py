#!/usr/bin/env python3
"""
Logo Specialist - Creates clean, business-ready logos
Uses specialized prompts and techniques for actual logo design
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
import json

class LogoSpecialist:
    def __init__(self):
        self.device = "cpu"
        self.pipeline = None
        self.model_loaded = False
        
    def load_model(self):
        """Load model optimized specifically for logo generation"""
        print("🔧 Loading Logo-Optimized Stable Diffusion...")
        print("⚡ Using logo-specific optimizations")
        
        try:
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,
                use_safetensors=True,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            # Logo-optimized scheduler
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config,
                use_karras_sigmas=True,  # Better for clean images
                algorithm_type="dpmsolver++"
            )
            
            self.pipeline = self.pipeline.to("cpu")
            self.pipeline.enable_attention_slicing()
            
            print("✅ Logo specialist model ready!")
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
    
    def create_logo_prompt(self, brand_name, industry, style="minimalist"):
        """Create HIGHLY SPECIFIC logo prompts for clean results"""
        
        # Ultra-specific logo prompts
        logo_base = "simple minimalist logo design"
        
        industry_elements = {
            "tech": "geometric circuit symbol, tech icon",
            "creative": "abstract brush stroke, creative symbol", 
            "fitness": "dumbbell icon, fitness symbol",
            "food": "chef hat, food symbol",
            "finance": "arrow up, growth symbol",
            "healthcare": "medical cross, health symbol"
        }
        
        # VERY specific style modifiers for clean logos
        style_specs = {
            "minimalist": "flat design, simple geometric shapes, clean lines, minimal details",
            "modern": "sleek geometric icon, contemporary flat design, clean typography",
            "bold": "strong simple icon, bold flat colors, impactful minimal design",
            "elegant": "refined simple symbol, elegant minimal typography, sophisticated clean design"
        }
        
        industry_icon = industry_elements.get(industry.lower(), "simple geometric symbol")
        style_desc = style_specs.get(style.lower(), "flat design, simple geometric shapes")
        
        # LOGO-SPECIFIC prompt engineering
        prompt = f"""logo design, {logo_base}, {industry_icon}, {style_desc}, 
vector art style, flat design, simple icon, clean typography, 
white background, corporate branding, scalable design, 
business logo, professional identity, minimal colors, 
geometric symbol, clean lines, no gradients, 
simple shapes only, logo mark, brand identity"""
        
        # VERY specific negative prompt to avoid common issues
        negative_prompt = """photorealistic, photograph, realistic, 3d render, complex details, 
multiple logos, text inside logo, letters, words, cluttered, busy, 
gradients, shadows, textures, patterns, ornate, decorative, 
blurry, pixelated, low quality, artistic painting, sketch, 
watermark, signature, multiple elements, complex composition"""
        
        return prompt, negative_prompt
    
    def post_process_logo(self, image):
        """Clean up the generated image to look more logo-like"""
        
        # Convert to clean format
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create clean background
        clean_img = Image.new('RGBA', image.size, (255, 255, 255, 0))
        
        # Make background transparent/white
        data = image.getdata()
        new_data = []
        
        for item in data:
            # Make very light pixels transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        image.putdata(new_data)
        
        # Sharpen for crisp lines
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        # High contrast for logo clarity
        enhancer = ImageOps.autocontrast(image.convert('RGB'))
        
        return enhancer.convert('RGBA')
    
    def generate_clean_logo(self, brand_name, industry, style="minimalist", attempts=3):
        """Generate multiple attempts and pick the best logo-like result"""
        
        if not self.model_loaded:
            if not self.load_model():
                return []
        
        prompt, negative_prompt = self.create_logo_prompt(brand_name, industry, style)
        
        print(f"\n🎨 Generating CLEAN LOGO for {brand_name}")
        print(f"🎯 Strategy: Multiple attempts with logo-specific prompts")
        print(f"🔧 Style: {style} {industry} logo")
        
        best_images = []
        
        for attempt in range(attempts):
            print(f"\n🔄 Attempt {attempt + 1}/{attempts}")
            print(f"📝 Using: {prompt[:60]}...")
            
            try:
                # Logo-optimized generation settings
                images = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_images_per_prompt=1,
                    num_inference_steps=30,  # More steps for cleaner results
                    guidance_scale=8.5,     # Higher guidance for cleaner logos
                    width=512,
                    height=512,
                    generator=torch.manual_seed(42 + attempt)  # Different seed each attempt
                ).images
                
                if images:
                    # Post-process for logo cleanliness
                    clean_logo = self.post_process_logo(images[0])
                    best_images.append(clean_logo)
                    print(f"✅ Generated attempt {attempt + 1}")
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
        
        print(f"\n🎉 Generated {len(best_images)} logo candidates!")
        return best_images
    
    def save_logo_variants(self, images, brand_name, industry, style):
        """Save all logo variants"""
        
        if not images:
            return []
        
        output_dir = f"/home/serah/{brand_name.lower().replace(' ', '_')}_clean_logos"
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        for i, img in enumerate(images, 1):
            filename = f"{output_dir}/{brand_name.lower().replace(' ', '_')}_clean_logo_v{i}.png"
            img.save(filename, "PNG", quality=95)
            saved_files.append(filename)
            print(f"✅ Saved variant {i}: {filename}")
        
        # Save metadata
        metadata = {
            "brand_name": brand_name,
            "industry": industry, 
            "style": style,
            "variants_generated": len(images),
            "post_processed": True,
            "logo_optimized": True
        }
        
        with open(f"{output_dir}/logo_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return saved_files

def main():
    print("🎯 LOGO SPECIALIST")
    print("=" * 40)
    print("Creates CLEAN, BUSINESS-READY logos")
    print("Uses logo-specific AI optimization")
    
    specialist = LogoSpecialist()
    
    # Get input
    brand_name = input("\nBrand name: ").strip() or "CodeLogo"
    print(f"✅ Brand: {brand_name}")
    
    print("\nIndustries: tech, creative, fitness, food, finance, healthcare")
    industry = input("Industry: ").strip().lower() or "tech"
    print(f"✅ Industry: {industry}")
    
    print("\nStyles: minimalist, modern, bold, elegant")
    style = input("Style: ").strip().lower() or "minimalist"
    print(f"✅ Style: {style}")
    
    print(f"\n🎯 GENERATING CLEAN LOGO")
    print(f"🏢 {brand_name} - {industry} - {style}")
    print(f"🔧 Multiple attempts for best quality")
    
    confirm = input("\nStart generation? (y/n): ").lower()
    if confirm != 'y':
        return
    
    # Generate logo variants
    logos = specialist.generate_clean_logo(brand_name, industry, style, attempts=2)
    
    if logos:
        files = specialist.save_logo_variants(logos, brand_name, industry, style)
        
        print(f"\n🎉 SUCCESS! Generated {len(logos)} clean logo variants")
        print(f"📁 Saved to: {brand_name.lower().replace(' ', '_')}_clean_logos/")
        
        for file in files:
            print(f"   • {file}")
        
        print(f"\n🎨 These should look much more like actual logos!")
        print(f"💡 Open them to compare and pick the best one")
    else:
        print(f"\n❌ Logo generation failed")

if __name__ == "__main__":
    main()
