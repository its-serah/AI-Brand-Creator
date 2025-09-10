#!/usr/bin/env python3
"""
AI Logo Generator with Local Stable Diffusion
Generates high-quality AI logos that run entirely on your laptop
"""

try:
    from diffusers import StableDiffusionPipeline
    import torch
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
import os
import json
from typing import List, Dict, Optional

class AILogoGenerator:
    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
    def load_stable_diffusion(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        """Load Stable Diffusion model for AI logo generation"""
        if not DIFFUSERS_AVAILABLE:
            print(" Diffusers not available. Install with: pip install diffusers")
            return False
            
        try:
            print(f" Loading Stable Diffusion model: {model_id}")
            print("  This will download ~4GB on first run...")
            
            # Load with optimizations for your laptop
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True
            )
            
            # Optimize for your AMD CPU/integrated GPU
            self.pipeline = self.pipeline.to(self.device)
            
            if self.device == "cpu":
                # CPU optimizations
                self.pipeline.enable_sequential_cpu_offload()
            
            # Memory optimizations for your 12GB RAM
            try:
                self.pipeline.enable_memory_efficient_attention()
                self.pipeline.enable_attention_slicing()
            except:
                pass
            
            print(" Stable Diffusion loaded successfully!")
            return True
            
        except Exception as e:
            print(f" Failed to load Stable Diffusion: {e}")
            print(" You can still use programmatic logo generation!")
            return False
    
    def generate_logo_prompt(self, brand_name: str, industry: str, 
                           personality: List[str], style: str = "minimalist") -> str:
        """Generate optimized prompt for logo creation"""
        personality_str = ", ".join(personality[:3])
        
        # Base prompt optimized for logo generation
        base_prompt = f"professional logo design, {brand_name}, {industry} company"
        
        # Style modifiers
        style_modifiers = {
            "minimalist": "clean minimalist design, simple geometric shapes, flat design",
            "modern": "modern sleek design, contemporary typography, gradient colors",
            "vintage": "vintage retro style, classic typography, aged aesthetic",
            "creative": "creative artistic design, unique abstract shapes, vibrant colors",
            "corporate": "professional corporate design, clean typography, business style"
        }
        
        style_desc = style_modifiers.get(style.lower(), style_modifiers["minimalist"])
        
        # Industry-specific elements
        industry_elements = {
            "tech": "circuit patterns, digital elements, tech symbols",
            "food": "organic shapes, food icons, appetite appeal",
            "fitness": "dynamic movement, energy symbols, health icons",
            "fashion": "elegant typography, style elements, luxury feel",
            "creative": "artistic elements, creative symbols, imaginative design",
            "finance": "trust symbols, stability elements, professional look",
            "healthcare": "medical crosses, care symbols, clean design"
        }
        
        industry_desc = industry_elements.get(industry.lower(), "professional symbols")
        
        # Quality enhancers for logo generation
        quality_terms = [
            "high quality vector style",
            "clean white background",
            "professional branding",
            "scalable design",
            "business logo",
            "corporate identity",
            f"{personality_str} personality"
        ]
        
        # Negative prompt to avoid unwanted elements
        negative_elements = [
            "blurry", "pixelated", "low quality", "text artifacts",
            "complex details", "realistic photo", "3d render",
            "multiple logos", "watermark", "signature"
        ]
        
        full_prompt = f"{base_prompt}, {style_desc}, {industry_desc}, {', '.join(quality_terms)}"
        negative_prompt = ", ".join(negative_elements)
        
        return full_prompt, negative_prompt
    
    def generate_ai_logo(self, brand_name: str, industry: str, 
                        personality: List[str], style: str = "minimalist",
                        num_images: int = 2) -> List[Image.Image]:
        """Generate AI logos using Stable Diffusion"""
        if not self.pipeline:
            print(" Stable Diffusion not loaded. Loading now...")
            if not self.load_stable_diffusion():
                return []
        
        positive_prompt, negative_prompt = self.generate_logo_prompt(
            brand_name, industry, personality, style
        )
        
        print(f" Generating {num_images} AI logo(s)...")
        print(f" Prompt: {positive_prompt[:100]}...")
        
        try:
            # Generation parameters optimized for logos
            images = self.pipeline(
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                num_images_per_prompt=num_images,
                num_inference_steps=20,  # Reduced for faster generation
                guidance_scale=7.5,      # Good balance for logos
                width=512,               # Square format good for logos
                height=512,
                generator=torch.manual_seed(42)  # Reproducible results
            ).images
            
            print(f" Generated {len(images)} AI logo(s)")
            return images
            
        except Exception as e:
            print(f" AI generation failed: {e}")
            return []
    
    def enhance_logo(self, image: Image.Image) -> Image.Image:
        """Enhance generated logo for professional use"""
        # Convert to RGBA for transparency support
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create a new image with white background
        white_bg = Image.new('RGBA', image.size, (255, 255, 255, 255))
        
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

def generate_logo_description_with_ollama(brand_name: str, industry: str, 
                                        personality: List[str]) -> str:
    """Generate detailed logo concept using Ollama"""
    personality_str = ', '.join(personality[:3])
    
    prompt = f"""You are a professional logo designer. Create a detailed visual concept for a logo:

Brand Name: {brand_name}
Industry: {industry}
Brand Personality: {personality_str}

Provide a comprehensive logo design concept including:

1. VISUAL CONCEPT:
   - Main symbol/icon (specific shapes, elements)
   - How it relates to the {industry} industry
   - Symbolic meaning

2. TYPOGRAPHY:
   - Font style (serif, sans-serif, script, etc.)
   - Weight and character
   - How text integrates with symbol

3. COLOR STRATEGY:
   - Primary color and meaning
   - Secondary color(s)
   - Color psychology for {industry}

4. COMPOSITION:
   - Logo layout (horizontal, stacked, symbol-only)
   - Size relationships
   - White space usage

5. INDUSTRY RELEVANCE:
   - How design reflects {industry} values
   - Target audience appeal
   - Competitive differentiation

Make it professional, scalable, and memorable. Focus on {personality_str} characteristics."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.6, "max_tokens": 600}
            },
            timeout=90
        )
        
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return f"Error: {response.status_code}"
            
    except Exception as e:
        return f"Ollama connection error: {e}"

def main():
    print(" AI Logo Generator")
    print("=" * 40)
    print("Generate professional logos using:")
    print("1.  Local Stable Diffusion AI")
    print("2.  Ollama concept generation")
    print("3.   Enhanced post-processing")
    
    # Initialize generator
    ai_gen = AILogoGenerator()
    
    # Get user input
    print("\n" + "=" * 40)
    brand_name = input("Enter brand name: ").strip() or "TechFlow"
    industry = input("Enter industry (tech, food, fitness, fashion, creative, finance, healthcare): ").strip() or "tech"
    
    print("\nSelect personality traits (enter numbers separated by commas):")
    traits = ["modern", "minimalist", "creative", "professional", "bold", 
              "elegant", "innovative", "trustworthy", "playful", "premium"]
    for i, trait in enumerate(traits, 1):
        print(f"{i:2d}. {trait}")
    
    trait_input = input("Your choices (e.g., 1,3,7): ").strip() or "1,2,7"
    selected_traits = []
    for num in trait_input.split(','):
        try:
            idx = int(num.strip()) - 1
            if 0 <= idx < len(traits):
                selected_traits.append(traits[idx])
        except ValueError:
            continue
    
    if not selected_traits:
        selected_traits = ["modern", "minimalist", "innovative"]
    
    # Style selection
    print("\nChoose logo style:")
    styles = ["minimalist", "modern", "vintage", "creative", "corporate"]
    for i, style in enumerate(styles, 1):
        print(f"{i}. {style}")
    
    style_choice = input("Style choice (1-5): ").strip() or "1"
    try:
        style = styles[int(style_choice) - 1]
    except:
        style = "minimalist"
    
    print(f"\n Creating logo for: {brand_name}")
    print(f" Industry: {industry}")
    print(f" Personality: {', '.join(selected_traits)}")
    print(f" Style: {style}")
    
    # Create output directory
    output_dir = f"./{brand_name.lower().replace(' ', '_')}_ai_logos"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate concept with Ollama
    print("\n Generating professional concept with Ollama...")
    concept = generate_logo_description_with_ollama(brand_name, industry, selected_traits)
    print(f"\n Professional Logo Concept:\n{'-' * 40}")
    print(concept)
    print("-" * 40)
    
    # Save concept
    concept_file = f"{output_dir}/{brand_name.lower()}_concept.txt"
    with open(concept_file, 'w') as f:
        f.write(f"Professional Logo Concept for {brand_name}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Industry: {industry}\n")
        f.write(f"Personality: {', '.join(selected_traits)}\n")
        f.write(f"Style: {style}\n\n")
        f.write("DETAILED CONCEPT:\n")
        f.write("-" * 20 + "\n")
        f.write(concept)
    
    print(f" Concept saved to: {concept_file}")
    
    # AI generation option
    if DIFFUSERS_AVAILABLE:
        generate_ai = input("\n Generate AI logos with Stable Diffusion? (y/n): ").lower() == 'y'
        
        if generate_ai:
            # Ask about model download
            if not ai_gen.pipeline:
                print("\n  First run will download ~4GB Stable Diffusion model")
                print(" This will take 10-30 minutes depending on internet speed")
                confirm_download = input("Continue with download? (y/n): ").lower() == 'y'
                
                if not confirm_download:
                    print("Skipping AI generation. You can run this again later!")
                    generate_ai = False
            
            if generate_ai:
                num_logos = int(input("How many AI logos to generate? (1-4): ").strip() or "2")
                num_logos = max(1, min(4, num_logos))
                
                print(f"\n Generating {num_logos} AI logo(s)...")
                print("⏰ This will take 2-10 minutes depending on your CPU...")
                
                ai_images = ai_gen.generate_ai_logo(
                    brand_name, industry, selected_traits, style, num_logos
                )
                
                if ai_images:
                    for i, img in enumerate(ai_images, 1):
                        # Enhance the logo
                        enhanced_img = ai_gen.enhance_logo(img)
                        
                        # Save original
                        original_path = f"{output_dir}/{brand_name.lower()}_ai_logo_{i}_original.png"
                        img.save(original_path)
                        
                        # Save enhanced
                        enhanced_path = f"{output_dir}/{brand_name.lower()}_ai_logo_{i}_enhanced.png"
                        enhanced_img.save(enhanced_path)
                        
                        print(f" Saved AI logo {i}: {enhanced_path}")
                    
                    print(f"\n Generated {len(ai_images)} AI logos!")
                else:
                    print(" AI logo generation failed")
    else:
        print("\n To enable AI logo generation, install: pip install diffusers torch")
    
    # Generate prompts for external AI tools
    print(f"\n External AI Tool Prompts:")
    print("-" * 40)
    
    if DIFFUSERS_AVAILABLE or ai_gen.pipeline:
        positive, negative = ai_gen.generate_logo_prompt(brand_name, industry, selected_traits, style)
        print(f" DALL-E/Midjourney Prompt:")
        print(positive)
        print(f"\n Avoid: {negative}")
    
    print(f"\n All files saved in: {output_dir}/")
    print("\n Next Steps:")
    print("1. Review generated concepts and AI logos")
    print("2. Use external AI tools with provided prompts")
    print("3. Refine designs in graphic design software")
    print("4. Create vector versions for scaling")

if __name__ == "__main__":
    main()
