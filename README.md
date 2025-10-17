# BrandForge AI - Complete Brand Identity Generator

**Professional AI-powered brand generation with full pipeline: Text → Logo → Upscaling → Color Extraction → Social Export**

## Production Branches

### Ready-to-Deploy Production Branches

- **`production-gcp`** - Complete production build with all features + GCP Cloud Run deployment
  - ✅ Stable Diffusion x4 Crisp Upscaler
  - ✅ Smart image resizing with aspect ratio preservation
  - ✅ Multiple logo size variants (favicon, print, web, mobile)
  - ✅ Color extraction and palette generation
  - ✅ Social media export presets
  - ✅ Automated GCP deployment scripts
  - ✅ Cloud Run optimized with monitoring

- **`production-aws`** - Complete production build with all features + AWS ECS deployment
  - ✅ All features from GCP branch
  - ✅ AWS ECS Fargate deployment (free tier optimized)
  - ✅ ECR container registry integration
  - ✅ CloudWatch logging and monitoring
  - ✅ Auto-scaling and health checks

## Live Production Deployment

- **Frontend**: https://generatethatbrand.netlify.app
- **Backend API**: https://brand-api-gpu-905163229563.us-central1.run.app
- **Status**: Fully functional with complete AI pipeline

## Complete AI Pipeline

```
📝 TEXT PROMPT → 🎨 STABLE DIFFUSION → 🖼️ BASE LOGO
    ↓
🔄 IMAGE-TO-IMAGE REFINEMENT → ✨ ENHANCED LOGO
    ↓
⬆️ 4X CRISP UPSCALER → 📐 SMART RESIZE → 🎨 COLOR EXTRACTION
    ↓
📱 SOCIAL MEDIA EXPORTS → 📦 COMPLETE BRAND KIT
```

## Quick Production Deployment

```bash
# Deploy to Google Cloud Platform
git checkout production-gcp
./gcp/deploy.sh

# Deploy to AWS
git checkout production-aws
./aws/deploy.sh

# Return to main
git checkout master
```

## Development Branches (Feature-Specific)

- **`stable-diffusion-x4-crisp-upscaler`** - Upscaler model integration
- **`resize-feature`** - Image resizing and variants
- **`gcp-deployment`** - GCP deployment scripts only
- **`aws-deployment`** - AWS deployment scripts only

# AI-Brand-Creator

A comprehensive AI-powered brand generation platform with multiple architectural approaches. This repository provides four production-ready system designs, each optimized for different use cases, scales, and operational requirements.

Generate complete brand kits including logos, color palettes, fonts, and design rationale using SDXL models, ControlNet, and intelligent prompt engineering.

## System Overview

The AI Brand Creator generates complete brand kits including logos, color palettes, fonts, and design rationale using:

- **SDXL + LoRA models** for logo generation
- **ControlNet** for design constraints
- **Neo4j/Neptune** for Brand Knowledge Graph (BKG)
- **FastAPI** for REST endpoints
- **Queue systems** for async processing
- **S3** for asset storage
- **WCAG compliance** checks
- **Bilingual rationale** generation

## Architecture Options Comparison

| Architecture | Best For | Complexity | Cost | Scale | GCP Support |
|-------------|----------|------------|------|-------|-------------|
| [MVP Monolith](./architectures/mvp-monolith/) | Demos, hackathons, prototypes | Low | Low | Small | Yes |
| [Queue-Centric](./architectures/queue-centric/) | Production (100-1K users) | Medium | Medium | Medium | Yes |
| [Serverless](./architectures/serverless/) | Variable traffic, cost optimization | Medium | Variable | High | Yes |
| [Microservices](./architectures/microservices/) | Enterprise scale, continuous deployment | High | High | Very High | Yes |

## Repository Structure

```
├── architectures/               # Architecture implementations
│   ├── mvp-monolith/           # Single deployable application
│   │   ├── api/                # FastAPI backend
│   │   ├── frontend/           # Web interface
│   │   ├── docker-compose.yml  # Local development
│   │   └── gcp/               # Google Cloud deployment
│   ├── queue-centric/         # Production-ready with queues
│   │   ├── services/          # Microservices
│   │   ├── infrastructure/    # Infrastructure as Code
│   │   └── gcp/              # GCP-specific configs
│   ├── serverless/            # Event-driven architecture
│   │   ├── functions/         # Cloud Functions
│   │   ├── workflows/         # Cloud Workflows
│   │   └── terraform/         # Terraform configs
│   └── microservices/         # Full enterprise setup
│       ├── services/          # Individual services
│       ├── k8s/              # Kubernetes manifests
│       └── monitoring/        # Observability stack
├── docs/                      # Comprehensive documentation
│   ├── GCP_SETUP.md          # Google Cloud Platform guide
│   ├── API.md                # API documentation
│   └── DEPLOYMENT.md         # Deployment guides
└── scripts/                   # Deployment and utility scripts
    ├── deploy-gcp.sh         # GCP deployment
    └── setup-env.sh          # Environment setup
```

## Quick Start Guide


### Common Setup Requirements

All architectures require:
- GPU access for SDXL inference
- Graph database (Neo4j or Neptune)
- Object storage (S3 or compatible)
- Container runtime (Docker)

## Cross-Cutting Concerns

### Model Management
- **SDXL + LoRA**: Industry-specific fine-tuned weights
- **ControlNet**: Palette and shape constraints
- **Triton/ONNX**: Runtime optimization where possible

### Brand Knowledge Graph (BKG)
- Start with Neo4j for faster development
- Consider Neptune for serverless integration
- Graph queries for palette/font recommendations

### Quality Assurance
- Automated WCAG contrast checks
- Bilingual font script validation
- Golden test kits per industry
- Prompt/version pinning for reproducibility

### Security & Compliance
- Signed URLs for asset access
- Per-job IAM policies
- Audit logs for prompts and outputs
- Data retention policies

## Performance Characteristics

| Metric | MVP Monolith | Queue-Centric | Serverless | Microservices |
|--------|--------------|---------------|------------|---------------|
| **Startup Time** | Fast | Medium | Slow (cold starts) | Medium |
| **Throughput** | Low-Medium | High | Variable | Very High |
| **Latency** | Low | Medium | High (initial) | Low |
| **Fault Tolerance** | Low | Medium | High | Very High |
| **Operational Complexity** | Low | Medium | Medium | High |

## Development Workflow

Each architecture includes:
- Development environment setup
- Testing strategies
- CI/CD pipelines
- Monitoring configurations
- Deployment guides

## Migration Path Options

Starting simple and evolving:
1. **MVP Monolith** to **Queue-Centric Modular** (when hitting resource limits)
2. **Queue-Centric** to **Serverless** (for cost optimization)
3. **Any** to **Microservices** (for maximum flexibility and scale)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes to the appropriate architecture folder
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


4. Start building your AI Brand Creator!

---

*Each architecture folder contains detailed implementation guides, starter code, and deployment instructions tailored to its specific approach.*
