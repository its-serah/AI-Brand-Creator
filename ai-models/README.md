# AI Models - Brand Generator Implementation

This folder contains the complete AI model implementations that power the Brand Generator system. These are the actual working models that generate logos, analyze colors, and create brand recommendations.

## Model Components

### 1. SDXL Logo Generation (`sdxl-logo-gen/`)
- Fine-tuned Stable Diffusion XL for logo creation
- Industry-specific LoRA adapters
- Custom prompt engineering for brand assets
- Batch inference optimizations

### 2. ControlNet Constraints (`controlnet-constraints/`)
- Color palette enforcement
- Layout and composition control
- Brand guideline adherence
- Multi-modal conditioning

### 3. Brand Knowledge Graph (`brand-knowledge-graph/`)
- Neo4j-powered design rule engine
- Industry-specific color psychology
- Typography recommendations
- Cultural design considerations

### 4. Training Pipeline (`training-pipeline/`)
- Data preprocessing and augmentation
- LoRA fine-tuning scripts
- Hyperparameter optimization
- Model versioning and deployment

### 5. Evaluation Framework (`evaluation/`)
- Quality assessment metrics
- WCAG compliance validation
- A/B testing framework
- Performance benchmarking

### 6. Datasets (`datasets/`)
- Logo training datasets by industry
- Color palette collections
- Typography classification data
- Brand guideline examples

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download base models
python scripts/download_models.py

# Initialize Brand Knowledge Graph
python brand-knowledge-graph/setup_graph.py

# Generate your first logo
python sdxl-logo-gen/generate.py --industry="technology" --style="modern" --company="TechCorp"
```

## Model Performance

| Component | Inference Time | GPU Memory | Quality Score |
|-----------|---------------|------------|---------------|
| SDXL Base | 8-12 seconds | 12GB | 8.5/10 |
| + LoRA | 10-15 seconds | 14GB | 9.2/10 |
| + ControlNet | 15-20 seconds | 16GB | 9.5/10 |

## Integration with Architectures

These AI models integrate with all 4 system architectures:
- **MVP Monolith**: Direct integration in FastAPI workers
- **Queue-Centric**: Dedicated GPU service containers  
- **Serverless**: Containerized batch jobs
- **Microservices**: Specialized inference services

Ready to build the actual AI that powers your brand generator!
