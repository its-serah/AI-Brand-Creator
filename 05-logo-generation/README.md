# 🎨 AI Logo Generation Module

Complete local logo generation system with brand identity creation and knowledge graphs.

## 🚀 Features

- **📊 Brand Identity Generation**: Complete brand creation with knowledge graphs
- **🎨 Visual Logo Generation**: Multiple logo styles and formats
- **🤖 AI-Powered**: Uses Stable Diffusion and Ollama for professional results
- **🧠 Dataset Fine-tuning**: Trained on 803 professional logo examples
- **💻 100% Local**: Runs entirely on your laptop, no cloud dependencies
- **🔧 CPU Optimized**: Designed for AMD Ryzen 5 6600U and similar hardware

## 📁 File Structure

```
05-logo-generation/
├── README.md                    # This file
├── brand_generator.py           # Complete brand identity + knowledge graphs
├── logo_generator.py            # Basic programmatic logo generation
├── ai_logo_generator.py         # AI-powered Stable Diffusion logos
├── logo_specialist.py           # Clean, business-ready logo specialist
├── pro_logo_generator.py        # Professional AI logo generator
├── working_logo_train.py        # Dataset fine-tuning with HuggingFace
├── demo_logos.py               # Demo and testing script
├── examples/                   # Generated logo examples
│   ├── baseline_logo_1.png     # Vanilla Stable Diffusion
│   ├── enhanced_logo_1.png     # Dataset-enhanced prompts
│   ├── ideal_logo_1.png        # Optimized logo-specific prompts
│   └── training_metadata.json  # Dataset analysis results
└── requirements.txt            # Python dependencies
```

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install diffusers torch transformers datasets
pip install pillow matplotlib networkx requests
pip install accelerate peft
```

### 2. Start Ollama (for AI concepts)
```bash
ollama serve
ollama pull qwen2.5:3b
```

### 3. Generate Your First Logo
```bash
# Quick demo
python3 demo_logos.py

# Complete brand identity with logos
python3 brand_generator.py

# AI-powered professional logos
python3 pro_logo_generator.py
```

## 🎯 Logo Generation Options

### Option 1: Complete Brand System
```bash
python3 brand_generator.py
```
- Brand identity + knowledge graphs
- Visual graph exports
- JSON brand data
- Industry-specific recommendations

### Option 2: Professional AI Logos
```bash
python3 pro_logo_generator.py
```
- Stable Diffusion v1.5
- Professional prompting
- Multiple variations
- High-quality PNG output

### Option 3: Dataset-Enhanced Training
```bash
python3 working_logo_train.py
```
- Uses 803 professional logo examples
- Dataset-informed prompt engineering
- Comparative generation (baseline vs enhanced)
- Training metadata export

### Option 4: Logo Specialist
```bash
python3 logo_specialist.py
```
- Clean, business-ready logos
- Logo-specific post-processing
- Multiple generation attempts
- Optimized for professional use

## 🏗️ Architecture

### Core Components

1. **Brand Generator (`brand_generator.py`)**
   - Ollama integration for AI concepts
   - NetworkX knowledge graphs
   - Visual graph generation
   - JSON export system

2. **AI Logo Pipeline (`pro_logo_generator.py`)**
   - Stable Diffusion v1.5 base model
   - Industry-specific prompting
   - CPU-optimized inference
   - Batch generation support

3. **Dataset Training (`working_logo_train.py`)**
   - HuggingFace dataset integration
   - Pattern extraction from 803 logos
   - Enhanced prompt engineering
   - Comparative analysis

4. **Logo Specialist (`logo_specialist.py`)**
   - Clean logo post-processing
   - Multiple seed attempts
   - Business-ready output
   - Format optimization

## 📊 Performance Specifications

### Hardware Requirements
- **CPU**: AMD Ryzen 5 6600U or equivalent (6+ cores recommended)
- **RAM**: 12GB+ (8GB minimum)
- **Storage**: 10GB for models + outputs
- **GPU**: Optional (CPU inference supported)

### Generation Times (AMD Ryzen 5 6600U)
- **Simple logos**: 2-5 minutes per logo
- **AI-enhanced logos**: 5-15 minutes per logo
- **Dataset training**: 15-30 minutes for analysis
- **Batch generation**: 10-25 minutes for 5 logos

### Model Sizes
- **Stable Diffusion v1.5**: ~4GB download
- **Ollama Qwen2.5:3b**: ~1.9GB
- **Additional models**: 2-8GB each

## 🎨 Logo Quality Levels

### 1. Programmatic Logos (`logo_generator.py`)
- ✅ Fast generation (< 1 minute)
- ✅ Consistent style
- ❌ Basic/amateur appearance
- **Use case**: Prototyping, placeholders

### 2. AI-Enhanced Logos (`pro_logo_generator.py`)
- ✅ Professional quality
- ✅ Industry-specific designs
- ❌ Slower generation (5-15 min)
- **Use case**: Client presentations, final designs

### 3. Dataset-Trained Logos (`working_logo_train.py`)
- ✅ Based on 803 professional examples
- ✅ Pattern-informed generation
- ✅ Comparative analysis
- **Use case**: Research, optimization

### 4. Specialist Logos (`logo_specialist.py`)
- ✅ Business-ready output
- ✅ Clean post-processing
- ✅ Multiple attempts per prompt
- **Use case**: Production logos

## 🔧 Configuration Options

### Model Selection
```python
# In pro_logo_generator.py
model_options = {
    "stable-diffusion-v1-5": "Standard quality, 4GB",
    "stable-diffusion-v2-1": "Improved quality, 5GB", 
    "sdxl-turbo": "Fast generation, 6GB"
}
```

### Generation Parameters
```python
# Optimize for your hardware
generation_config = {
    "num_inference_steps": 25,    # 15-35 (quality vs speed)
    "guidance_scale": 7.5,        # 5.0-12.0 (creativity vs adherence)
    "batch_size": 1,              # 1-4 (memory vs speed)
    "resolution": 512,            # 256/512/768 (quality vs memory)
}
```

## 📈 Dataset Integration

### HuggingFace Dataset
- **Source**: `logo-wizard/modern-logo-dataset`
- **Size**: 803 professional logo examples
- **License**: CC BY-NC 3.0 (non-commercial)
- **Format**: Images + text descriptions

### Analysis Results
```json
{
  "dataset_size": 803,
  "top_logo_terms": ["background", "minimalism", "modern", "foreground"],
  "common_patterns": ["coffee shop", "geometric", "flat design"],
  "approach": "dataset-informed prompt engineering"
}
```

## 🎯 Integration with Main Architecture

This logo generation module can be integrated into any of the main architectures:

### MVP Monolith Integration
```python
from logo_generation.brand_generator import LocalBrandGenerator
from logo_generation.pro_logo_generator import ProfessionalLogoGenerator

# In your Flask/FastAPI app
@app.post("/generate-brand")
async def generate_brand(request: BrandRequest):
    generator = LocalBrandGenerator()
    brand_data = generator.generate_brand_identity(
        request.name, request.industry
    )
    return brand_data
```

### Queue-Centric Integration  
```python
# Add to your Celery tasks
@celery.task
def generate_logo_task(brand_name, industry, style):
    generator = ProfessionalLogoGenerator()
    return generator.generate_logo(brand_name, industry, style)
```

### Serverless Integration
```python
# AWS Lambda function
def lambda_handler(event, context):
    from logo_generation.logo_specialist import LogoSpecialist
    specialist = LogoSpecialist()
    logos = specialist.generate_clean_logo(
        event['brand_name'], 
        event['industry']
    )
    return {'logos': logos}
```

## 🚀 Deployment Options

### Local Development
```bash
# Clone repository
git clone https://github.com/its-serah/AI-Brand-Creator.git
cd AI-Brand-Creator
git checkout logo-generation

# Install dependencies
pip install -r 05-logo-generation/requirements.txt

# Start services
ollama serve &
python3 05-logo-generation/pro_logo_generator.py
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://ollama.ai/install.sh | sh

COPY 05-logo-generation/ /app/
WORKDIR /app

RUN pip install -r requirements.txt
EXPOSE 8000

CMD ["python", "pro_logo_generator.py"]
```

### Production Scaling
```yaml
# docker-compose.yml
version: '3.8'
services:
  logo-generator:
    build: .
    replicas: 3
    resources:
      limits:
        memory: 8G
        cpus: '4'
  
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
```

## 🔍 Example Outputs

### Brand Identity Example
```json
{
  "name": "TechFlow",
  "industry": "technology", 
  "mission": "Streamlined solutions for digital transformation",
  "values": ["Innovation", "Efficiency", "Reliability"],
  "colors": ["#3498db", "#2c3e50", "#1abc9c"],
  "personality": ["Modern", "Professional", "Trustworthy"]
}
```

### Logo Generation Results
- **Baseline quality**: Standard Stable Diffusion output
- **Enhanced quality**: Dataset-informed prompting  
- **Professional quality**: Logo specialist processing
- **Production ready**: Clean, scalable, business-appropriate

## 📚 References

- [Stable Diffusion Documentation](https://huggingface.co/docs/diffusers)
- [Ollama Model Library](https://ollama.ai/library)
- [Logo Dataset](https://huggingface.co/datasets/logo-wizard/modern-logo-dataset)
- [Brand Identity Design Principles](https://www.designcouncil.org.uk)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/logo-enhancement`)
3. Make changes in `05-logo-generation/`
4. Add examples and update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. The logo dataset is under CC BY-NC 3.0.

---

**Ready to generate professional logos locally! 🎨✨**
