#!/usr/bin/env python3
"""
Local Logo Generator with Multiple Approaches
Generates visual PNG logos that run entirely on your laptop
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import colorsys
import json
import os
from typing import Dict, List, Tuple, Optional
import requests
import io

class LocalLogoGenerator:
    def __init__(self):
        self.colors = {
            'tech': ['#3498db', '#2c3e50', '#1abc9c', '#34495e', '#e74c3c'],
            'fashion': ['#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3'],
            'food': ['#ff5722', '#795548', '#607d8b', '#4caf50', '#ffc107'],
            'fitness': ['#4caf50', '#ff9800', '#f44336', '#2196f3', '#9c27b0'],
            'creative': ['#e91e63', '#9c27b0', '#3f51b5', '#00bcd4', '#4caf50'],
            'professional': ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#ecf0f1']
        }
        
        self.fonts_available = []
        self._check_fonts()
    
    def _check_fonts(self):
        """Check what fonts are available on the system"""
        common_fonts = [
            'DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'Cantarell',
            'Noto Sans', 'FreeSans', 'Arial', 'Helvetica'
        ]
        
        for font_name in common_fonts:
            try:
                ImageFont.truetype(f"/usr/share/fonts/truetype/*/{font_name}*", 24)
                self.fonts_available.append(font_name)
            except:
                try:
                    ImageFont.truetype(f"/usr/share/fonts/*/{font_name}*", 24)
                    self.fonts_available.append(font_name)
                except:
                    continue
        
        if not self.fonts_available:
            self.fonts_available = ['default']
    
    def get_brand_colors(self, industry: str, brand_personality: List[str]) -> List[str]:
        """Get appropriate colors based on industry and personality"""
        base_colors = self.colors.get(industry.lower(), self.colors['professional'])
        
        # Adjust based on personality
        if any(trait in ['modern', 'innovative', 'tech'] for trait in brand_personality):
            base_colors = self.colors['tech']
        elif any(trait in ['creative', 'artistic', 'bold'] for trait in brand_personality):
            base_colors = self.colors['creative']
        elif any(trait in ['natural', 'organic', 'eco'] for trait in brand_personality):
            base_colors = ['#27ae60', '#2ecc71', '#16a085', '#f39c12', '#e67e22']
        
        return base_colors[:3]  # Return top 3 colors
    
    def generate_geometric_logo(self, brand_name: str, colors: List[str], 
                              style: str = 'modern') -> Image.Image:
        """Generate geometric/abstract logo using shapes"""
        size = 400
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Get primary colors
        primary = colors[0] if colors else '#3498db'
        secondary = colors[1] if len(colors) > 1 else '#2c3e50'
        accent = colors[2] if len(colors) > 2 else '#1abc9c'
        
        center = size // 2
        
        if style.lower() == 'modern':
            # Modern geometric shapes
            # Main circle
            draw.ellipse([center-80, center-80, center+80, center+80], 
                        fill=primary, outline=secondary, width=3)
            
            # Inner geometric pattern
            draw.rectangle([center-40, center-40, center+40, center+40], 
                          fill=accent, outline=None)
            
            # Accent triangles
            triangle1 = [(center-60, center-30), (center-30, center-60), (center-30, center)]
            draw.polygon(triangle1, fill=secondary)
            
            triangle2 = [(center+60, center+30), (center+30, center+60), (center+30, center)]
            draw.polygon(triangle2, fill=secondary)
            
        elif style.lower() == 'minimalist':
            # Clean lines and simple shapes
            draw.ellipse([center-70, center-70, center+70, center+70], 
                        outline=primary, width=6)
            
            draw.line([center-50, center, center+50, center], fill=secondary, width=4)
            draw.line([center, center-50, center, center+50], fill=secondary, width=4)
            
        elif style.lower() == 'creative':
            # Organic/creative shapes
            # Abstract blob shape
            points = []
            num_points = 8
            for i in range(num_points):
                angle = (i / num_points) * 2 * np.pi
                radius = 60 + random.randint(-20, 20)
                x = center + radius * np.cos(angle)
                y = center + radius * np.sin(angle)
                points.append((x, y))
            
            draw.polygon(points, fill=primary, outline=secondary, width=2)
            
            # Inner accent
            inner_points = []
            for i in range(6):
                angle = (i / 6) * 2 * np.pi
                radius = 30
                x = center + radius * np.cos(angle)
                y = center + radius * np.sin(angle)
                inner_points.append((x, y))
            
            draw.polygon(inner_points, fill=accent)
        
        return img
    
    def generate_text_logo(self, brand_name: str, colors: List[str], 
                          font_style: str = 'modern') -> Image.Image:
        """Generate text-based logo"""
        # Determine size based on text length
        base_size = max(400, len(brand_name) * 30)
        img = Image.new('RGBA', (base_size, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Colors
        primary = colors[0] if colors else '#2c3e50'
        secondary = colors[1] if len(colors) > 1 else '#3498db'
        
        # Font selection
        font_size = min(60, max(40, 400 // len(brand_name)))
        
        try:
            if self.fonts_available and self.fonts_available[0] != 'default':
                font = ImageFont.truetype(f"/usr/share/fonts/truetype/*/{self.fonts_available[0]}*", font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), brand_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (base_size - text_width) // 2
        y = (200 - text_height) // 2
        
        if font_style.lower() == 'shadow':
            # Shadow effect
            draw.text((x+3, y+3), brand_name, fill='#00000040', font=font)
            draw.text((x, y), brand_name, fill=primary, font=font)
            
        elif font_style.lower() == 'outline':
            # Outline effect
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x+dx, y+dy), brand_name, fill=secondary, font=font)
            draw.text((x, y), brand_name, fill=primary, font=font)
            
        else:
            # Simple gradient effect (simulated)
            draw.text((x, y), brand_name, fill=primary, font=font)
            
            # Add accent line under text
            line_y = y + text_height + 10
            draw.rectangle([x, line_y, x + text_width, line_y + 4], fill=secondary)
        
        return img
    
    def generate_icon_logo(self, brand_name: str, industry: str, 
                          colors: List[str]) -> Image.Image:
        """Generate icon-style logos based on industry"""
        size = 400
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        primary = colors[0] if colors else '#3498db'
        secondary = colors[1] if len(colors) > 1 else '#2c3e50'
        accent = colors[2] if len(colors) > 2 else '#1abc9c'
        
        center = size // 2
        
        if industry.lower() == 'tech':
            # Circuit-inspired design
            # Main chip outline
            draw.rectangle([center-70, center-70, center+70, center+70], 
                          outline=primary, width=4, fill=None)
            
            # Circuit lines
            for i in range(-50, 51, 25):
                draw.line([center+i, center-70, center+i, center-50], fill=secondary, width=2)
                draw.line([center+i, center+50, center+i, center+70], fill=secondary, width=2)
                draw.line([center-70, center+i, center-50, center+i], fill=secondary, width=2)
                draw.line([center+50, center+i, center+70, center+i], fill=secondary, width=2)
            
            # Central processing unit
            draw.rectangle([center-30, center-30, center+30, center+30], 
                          fill=accent, outline=primary, width=2)
            
        elif industry.lower() == 'food':
            # Chef hat or plate design
            # Plate
            draw.ellipse([center-80, center-20, center+80, center+60], 
                        fill=primary, outline=secondary, width=3)
            
            # Food elements (abstract)
            draw.ellipse([center-40, center, center-10, center+30], fill=accent)
            draw.ellipse([center, center-5, center+30, center+25], fill=secondary)
            draw.ellipse([center+10, center+10, center+40, center+40], fill=accent)
            
        elif industry.lower() == 'fitness':
            # Dumbbell or heart rate design
            # Dumbbell
            draw.ellipse([center-70, center-20, center-30, center+20], fill=primary)
            draw.ellipse([center+30, center-20, center+70, center+20], fill=primary)
            draw.rectangle([center-30, center-10, center+30, center+10], fill=secondary)
            
            # Motion lines
            for i, offset in enumerate([-40, -30, -20]):
                alpha = 100 - i * 30
                draw.line([center-90, center+offset, center-80, center+offset], 
                         fill=accent + f'{alpha:02x}', width=3)
        
        else:
            # Generic professional icon
            # Abstract building/growth chart
            heights = [40, 60, 80, 70, 90]
            width = 20
            start_x = center - (len(heights) * width) // 2
            
            for i, height in enumerate(heights):
                x = start_x + i * width
                y = center + 50 - height
                color = [primary, secondary, accent][i % 3]
                draw.rectangle([x, y, x+width-2, center+50], fill=color)
        
        return img
    
    def generate_combined_logo(self, brand_name: str, industry: str, 
                             colors: List[str], style: str = 'modern') -> Image.Image:
        """Generate logo combining icon and text"""
        # Create icon
        icon_img = self.generate_icon_logo(brand_name, industry, colors)
        
        # Create text
        text_img = self.generate_text_logo(brand_name, colors, style)
        
        # Combine them
        total_width = max(icon_img.width, text_img.width)
        total_height = icon_img.height + text_img.height + 20
        
        combined = Image.new('RGBA', (total_width, total_height), (255, 255, 255, 0))
        
        # Paste icon centered at top
        icon_x = (total_width - icon_img.width) // 2
        combined.paste(icon_img, (icon_x, 0), icon_img)
        
        # Paste text centered at bottom
        text_x = (total_width - text_img.width) // 2
        combined.paste(text_img, (text_x, icon_img.height + 20), text_img)
        
        return combined
    
    def generate_ai_prompt_logo(self, brand_name: str, industry: str, 
                               personality: List[str]) -> str:
        """Generate a detailed prompt for AI image generation"""
        personality_str = ', '.join(personality[:3])
        
        prompt = f"""
        Professional logo design for "{brand_name}", a {industry} company.
        Style: {personality_str}, minimalist, vector-style.
        Requirements:
        - Clean, modern design
        - Suitable for business cards and websites
        - Simple geometric shapes or typography
        - Professional color scheme
        - Scalable vector style
        - White or transparent background
        - No complex details or textures
        
        Design type: Combine icon symbol with clean typography
        Industry: {industry}
        Mood: {personality_str}
        """
        
        return prompt.strip()

def generate_logo_with_ollama(brand_name: str, industry: str, 
                             personality: List[str], colors: List[str]) -> str:
    """Use Ollama to generate detailed logo description"""
    color_str = ', '.join(colors[:3])
    personality_str = ', '.join(personality[:3])
    
    prompt = f"""Create a detailed visual description for a professional logo design:

Brand Name: {brand_name}
Industry: {industry}
Personality: {personality_str}
Colors: {color_str}

Describe a logo design including:
1. Main visual element (icon/symbol)
2. Typography style
3. Color placement
4. Overall composition
5. Specific geometric shapes to use

Make it suitable for a {industry} business with {personality_str} personality.
Focus on clean, professional design that works at small and large sizes."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "max_tokens": 400}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return f"Error generating logo description: {response.status_code}"
            
    except Exception as e:
        return f"Could not connect to Ollama: {e}"

def main():
    print(" Local Logo Generator")
    print("=" * 40)
    
    generator = LocalLogoGenerator()
    
    # Get brand information
    brand_name = input("Enter brand name: ").strip() or "TechFlow"
    industry = input("Enter industry (tech, food, fitness, fashion, creative): ").strip() or "tech"
    
    print("\nSelect personality traits (enter numbers separated by commas):")
    traits = ["modern", "creative", "professional", "bold", "minimalist", "playful", "elegant", "innovative"]
    for i, trait in enumerate(traits, 1):
        print(f"{i}. {trait}")
    
    trait_input = input("Your choices (e.g., 1,3,8): ").strip() or "1,3,8"
    selected_traits = []
    for num in trait_input.split(','):
        try:
            idx = int(num.strip()) - 1
            if 0 <= idx < len(traits):
                selected_traits.append(traits[idx])
        except ValueError:
            continue
    
    if not selected_traits:
        selected_traits = ["modern", "professional", "innovative"]
    
    # Get colors
    colors = generator.get_brand_colors(industry, selected_traits)
    print(f"\n Using colors: {', '.join(colors)}")
    
    # Generate logo description with Ollama
    print("\n Generating logo concept with AI...")
    logo_description = generate_logo_with_ollama(brand_name, industry, selected_traits, colors)
    print(f"\n AI Logo Concept:\n{logo_description}")
    
    # Logo generation options
    print("\n  Choose logo type to generate:")
    print("1. Geometric/Abstract logo")
    print("2. Text-based logo")
    print("3. Industry icon logo")
    print("4. Combined icon + text logo")
    print("5. Generate all types")
    
    choice = input("Your choice (1-5): ").strip() or "5"
    
    output_dir = f"./{brand_name.lower().replace(' ', '_')}_logos"
    os.makedirs(output_dir, exist_ok=True)
    
    if choice == "1" or choice == "5":
        print("\n Generating geometric logo...")
        for style in ['modern', 'minimalist', 'creative']:
            logo = generator.generate_geometric_logo(brand_name, colors, style)
            filename = f"{output_dir}/{brand_name.lower()}_{style}_geometric.png"
            logo.save(filename, 'PNG')
            print(f" Saved: {filename}")
    
    if choice == "2" or choice == "5":
        print("\n  Generating text logo...")
        for style in ['modern', 'shadow', 'outline']:
            logo = generator.generate_text_logo(brand_name, colors, style)
            filename = f"{output_dir}/{brand_name.lower()}_{style}_text.png"
            logo.save(filename, 'PNG')
            print(f" Saved: {filename}")
    
    if choice == "3" or choice == "5":
        print("\n Generating industry icon logo...")
        logo = generator.generate_icon_logo(brand_name, industry, colors)
        filename = f"{output_dir}/{brand_name.lower()}_icon.png"
        logo.save(filename, 'PNG')
        print(f" Saved: {filename}")
    
    if choice == "4" or choice == "5":
        print("\n Generating combined logo...")
        for style in ['modern', 'shadow']:
            logo = generator.generate_combined_logo(brand_name, industry, colors, style)
            filename = f"{output_dir}/{brand_name.lower()}_{style}_combined.png"
            logo.save(filename, 'PNG')
            print(f" Saved: {filename}")
    
    # Save logo description
    description_file = f"{output_dir}/{brand_name.lower()}_concept.txt"
    with open(description_file, 'w') as f:
        f.write(f"Logo Concept for {brand_name}\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Industry: {industry}\n")
        f.write(f"Personality: {', '.join(selected_traits)}\n")
        f.write(f"Colors: {', '.join(colors)}\n\n")
        f.write("AI-Generated Concept:\n")
        f.write(logo_description)
    
    print(f"\n Logo generation complete!")
    print(f" All files saved in: {output_dir}/")
    print(f" Concept description: {description_file}")
    
    # Show AI prompt for external tools
    if input("\n Show AI image generation prompt? (y/n): ").lower() == 'y':
        ai_prompt = generator.generate_ai_prompt_logo(brand_name, industry, selected_traits)
        print(f"\n Use this prompt in DALL-E, Midjourney, or local Stable Diffusion:")
        print("-" * 60)
        print(ai_prompt)
        print("-" * 60)

if __name__ == "__main__":
    main()
