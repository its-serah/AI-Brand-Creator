#!/usr/bin/env python3
"""
Local Brand Generator with Knowledge Graph Integration
Runs entirely on your laptop using Ollama + NetworkX
"""

import json
import requests
import networkx as nx
import matplotlib.pyplot as plt
import os
from typing import Dict, List, Optional
import random

class LocalBrandGenerator:
    def __init__(self, model_name="qwen2.5:3b", ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.knowledge_graph = nx.DiGraph()
        self.brand_database = {}
        
    def generate_with_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using local Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "max_tokens": max_tokens,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Connection error: {str(e)}"

    def create_brand_knowledge_graph(self, brand_data: Dict):
        """Create knowledge graph from brand data"""
        brand_name = brand_data.get("name", "Unknown")
        
        # Add brand as central node
        self.knowledge_graph.add_node(brand_name, type="brand")
        
        # Add connected concepts
        for key, value in brand_data.items():
            if key != "name" and value:
                if isinstance(value, list):
                    for item in value:
                        self.knowledge_graph.add_node(item, type=key)
                        self.knowledge_graph.add_edge(brand_name, item, relationship=key)
                else:
                    self.knowledge_graph.add_node(value, type=key)
                    self.knowledge_graph.add_edge(brand_name, value, relationship=key)
    
    def generate_brand_name(self, industry: str, style: str = "modern") -> str:
        """Generate brand name using local LLM"""
        prompt = f"""Generate 5 creative brand names for a {industry} company with a {style} style.
Requirements:
- Memorable and unique
- Easy to pronounce
- Professional yet creative
- Suitable for {industry} industry

Brand names:"""

        response = self.generate_with_ollama(prompt, max_tokens=200)
        return response
    
    def generate_brand_identity(self, brand_name: str, industry: str) -> Dict:
        """Generate complete brand identity"""
        prompt = f"""Create a comprehensive brand identity for "{brand_name}" in the {industry} industry.

Include:
1. Brand Mission (1 sentence)
2. Core Values (3-4 values)
3. Target Audience (specific description)
4. Brand Personality (3-4 traits)
5. Color Palette (3-4 colors with meanings)
6. Typography Style
7. Brand Voice (tone and style)
8. Unique Value Proposition

Format as JSON:"""

        response = self.generate_with_ollama(prompt, max_tokens=600)
        
        # Try to extract JSON, fallback to structured text
        try:
            # Basic JSON cleaning
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
            
        # Fallback: parse as structured text
        return self._parse_brand_identity(response, brand_name, industry)
    
    def _parse_brand_identity(self, text: str, brand_name: str, industry: str) -> Dict:
        """Parse brand identity from text response"""
        return {
            "name": brand_name,
            "industry": industry,
            "mission": self._extract_field(text, ["mission", "purpose"]),
            "values": self._extract_list_field(text, ["values", "core values"]),
            "target_audience": self._extract_field(text, ["target audience", "audience"]),
            "personality": self._extract_list_field(text, ["personality", "traits"]),
            "colors": self._extract_list_field(text, ["colors", "color palette"]),
            "typography": self._extract_field(text, ["typography", "font"]),
            "voice": self._extract_field(text, ["voice", "tone"]),
            "value_proposition": self._extract_field(text, ["value proposition", "unique"])
        }
    
    def _extract_field(self, text: str, keywords: List[str]) -> str:
        """Extract single field from text"""
        lines = text.split('\n')
        for line in lines:
            for keyword in keywords:
                if keyword.lower() in line.lower() and ':' in line:
                    return line.split(':', 1)[1].strip().strip('"')
        return "Generated by AI"
    
    def _extract_list_field(self, text: str, keywords: List[str]) -> List[str]:
        """Extract list field from text"""
        result = []
        lines = text.split('\n')
        in_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering the section
            for keyword in keywords:
                if keyword.lower() in line.lower() and ':' in line:
                    in_section = True
                    # Try to get items from the same line
                    after_colon = line.split(':', 1)[1].strip()
                    if after_colon:
                        result.extend([item.strip().strip('"') for item in after_colon.split(',')])
                    continue
            
            # If in section, collect items
            if in_section and line:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.')):
                    item = line.lstrip('-•*0123456789. ').strip().strip('"')
                    if item:
                        result.append(item)
                elif ':' in line and not any(kw.lower() in line.lower() for kw in keywords):
                    in_section = False
        
        return result[:4] if result else ["Modern", "Innovative", "Professional", "Trustworthy"]
    
    def visualize_knowledge_graph(self, brand_name: str, save_path: Optional[str] = None):
        """Visualize the knowledge graph"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.knowledge_graph, k=2, iterations=50)
        
        # Color nodes by type
        colors = {
            'brand': '#FF6B6B',
            'values': '#4ECDC4', 
            'colors': '#45B7D1',
            'personality': '#96CEB4',
            'industry': '#FECA57',
            'default': '#DDA0DD'
        }
        
        node_colors = [colors.get(self.knowledge_graph.nodes[node].get('type', 'default'), 
                                colors['default']) for node in self.knowledge_graph.nodes()]
        
        nx.draw(self.knowledge_graph, pos, 
                node_color=node_colors,
                node_size=2000,
                font_size=8,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                with_labels=True)
        
        plt.title(f"Brand Knowledge Graph: {brand_name}", fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Knowledge graph saved to: {save_path}")
        
        plt.show()
    
    def save_brand(self, brand_data: Dict, filename: Optional[str] = None):
        """Save brand data to JSON file"""
        if not filename:
            brand_name = brand_data.get('name', 'unknown_brand')
            filename = f"{brand_name.lower().replace(' ', '_')}_brand.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(brand_data, f, indent=2, ensure_ascii=False)
        
        print(f"Brand saved to: {filename}")
        return filename

def main():
    """Main function to demonstrate the brand generator"""
    print(" Local Brand Generator with Knowledge Graphs")
    print("=" * 50)
    
    generator = LocalBrandGenerator()
    
    # Get user input
    industry = input("Enter industry (e.g., tech, fashion, food): ").strip() or "tech"
    style = input("Enter style (e.g., modern, classic, playful): ").strip() or "modern"
    
    print(f"\n Generating brand names for {industry} industry with {style} style...")
    
    # Generate brand names
    brand_names_response = generator.generate_brand_name(industry, style)
    print(f"\n Suggested Brand Names:\n{brand_names_response}")
    
    # Let user select or input a brand name
    brand_name = input("\n  Enter your chosen brand name: ").strip()
    if not brand_name:
        # Extract first name from response as fallback
        lines = brand_names_response.split('\n')
        for line in lines:
            if line.strip() and not line.lower().startswith(('generate', 'brand', 'requirements')):
                brand_name = line.strip().lstrip('1234567890.-* ')
                break
        brand_name = brand_name or "TechFlow"
    
    print(f"\n Creating comprehensive brand identity for: {brand_name}")
    
    # Generate complete brand identity
    brand_identity = generator.generate_brand_identity(brand_name, industry)
    
    # Create knowledge graph
    generator.create_brand_knowledge_graph(brand_identity)
    
    # Display results
    print(f"\n Brand Identity for {brand_name}:")
    print("=" * 40)
    for key, value in brand_identity.items():
        if key != "name":
            if isinstance(value, list):
                print(f"{key.title()}: {', '.join(value)}")
            else:
                print(f"{key.title()}: {value}")
    
    # Save brand data
    filename = generator.save_brand(brand_identity)
    
    # Visualize knowledge graph
    try:
        print(f"\n Generating knowledge graph visualization...")
        graph_path = filename.replace('.json', '_graph.png')
        generator.visualize_knowledge_graph(brand_name, graph_path)
    except Exception as e:
        print(f"Note: Could not generate graph visualization: {e}")
        print("Install matplotlib with: pip install matplotlib")

if __name__ == "__main__":
    main()
