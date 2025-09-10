#!/usr/bin/env python3
"""
Quick Demo of Logo Generation Capabilities
Shows what types of logos can be generated locally
"""

import subprocess
import os

def show_logo_examples():
    """Display information about logo generation capabilities"""
    
    print(" LOCAL LOGO GENERATION CAPABILITIES")
    print("=" * 60)
    
    print("\n LOGO TYPES AVAILABLE:")
    print("1.  Geometric/Abstract Logos - Modern shapes and patterns")
    print("2.   Text-Based Logos - Typography with effects")  
    print("3.  Industry Icon Logos - Tech, food, fitness, fashion icons")
    print("4.  Combined Logos - Icon + text combinations")
    print("5.  AI-Generated Logos - Using Stable Diffusion (optional)")
    
    print("\n STYLE OPTIONS:")
    print("• Modern - Clean geometric shapes")
    print("• Minimalist - Simple lines and forms")
    print("• Creative - Organic, artistic shapes") 
    print("• Shadow - Text with drop shadow effects")
    print("• Outline - Bold outline typography")
    
    print("\n INDUSTRY SPECIALIZATIONS:")
    print("• Tech - Circuit patterns, digital elements")
    print("• Food - Plates, organic shapes, appetite appeal") 
    print("• Fitness - Dumbbells, movement lines, energy")
    print("• Fashion - Elegant typography, luxury feel")
    print("• Creative - Artistic elements, vibrant colors")
    print("• Professional - Corporate charts, stability")
    
    print(f"\n EXISTING LOGO EXAMPLES:")
    if os.path.exists('./techflow_logos/'):
        logos = [f for f in os.listdir('./techflow_logos/') if f.endswith('.png')]
        if logos:
            print(f" Found {len(logos)} example logos in ./techflow_logos/:")
            for logo in sorted(logos):
                print(f"   • {logo}")
        else:
            print("   No PNG files found")
    else:
        print("   No example logos found yet")
    
    print(f"\n HOW TO GENERATE LOGOS:")
    print("1. Basic Logo Generator:")
    print("   python3 logo_generator.py")
    print("   → Creates geometric, text, icon, and combined logos")
    print("   → Uses AI concepts from Ollama")
    print("   → Generates 8-10 PNG files per brand")
    
    print("\n2. AI Logo Generator:")
    print("   python3 ai_logo_generator.py") 
    print("   → Uses Stable Diffusion for AI generation")
    print("   → Downloads ~4GB model on first run")
    print("   → Creates enhanced, professional logos")
    
    print("\n3. Integrated with Brand Generator:")
    print("   python3 brand_generator.py")
    print("   → Complete brand identity + knowledge graphs")
    print("   → Can be extended to include logo generation")

def main():
    show_logo_examples()
    
    if input("\n Try generating a quick demo logo? (y/n): ").lower() == 'y':
        print("\n Running logo generator with demo settings...")
        
        # Create a simple demo logo
        demo_input = "DemoLogo\ntech\n1,2,7\n1"  # DemoLogo, tech, modern+creative+elegant, geometric only
        
        try:
            result = subprocess.run(
                ['python3', 'logo_generator.py'],
                input=demo_input,
                text=True,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(" Demo logo generated successfully!")
                if os.path.exists('./demologo_logos/'):
                    logos = [f for f in os.listdir('./demologo_logos/') if f.endswith('.png')]
                    print(f" Created {len(logos)} demo logos in ./demologo_logos/")
                    for logo in sorted(logos):
                        print(f"   • {logo}")
            else:
                print(" Demo generation failed")
                print(result.stderr)
        
        except subprocess.TimeoutExpired:
            print("⏰ Demo generation timed out")
        except Exception as e:
            print(f" Error: {e}")
    
    print("\n Logo generation demo complete!")
    print("\n Next steps:")
    print("1. Run logo_generator.py for full logo creation")
    print("2. Run ai_logo_generator.py for AI-generated logos") 
    print("3. Integrate with brand_generator.py for complete branding")

if __name__ == "__main__":
    main()
