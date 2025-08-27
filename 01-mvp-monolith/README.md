# MVP Monolith - Brand Generator System Design

## Architecture Rationale

### Why Choose MVP Monolith?

The MVP Monolith approach is designed for **speed of development and deployment** when you need to validate your AI Brand Creator concept quickly. This architecture prioritizes getting something working fast over scalability or operational sophistication.

**Choose this approach when:**
- You need a working prototype within days or weeks
- You're building for hackathons, demos, or early validation
- Your team size is small (1-3 developers)
- Expected traffic is low to moderate (< 100 concurrent users)
- You want minimal operational overhead
- Budget constraints require the lowest possible infrastructure cost

**Don't choose this approach if:**
- You expect high or unpredictable traffic patterns
- You need to scale individual components independently
- Multiple teams will be working on different parts of the system
- You require high availability (99.9%+ uptime)
- You need sophisticated monitoring and observability

## System Architecture

### High-Level Data Flow

```
Client Request → FastAPI → In-Process Queue → GPU Workers → Neo4j/BKG → S3 Storage → PDF Generation → Response
```

### Component Overview

**Single Deployable Application:**
- **FastAPI**: Handles HTTP API, validation, and orchestration
- **In-Process Queue**: Simple Python queue for job management
- **GPU Worker Pool**: Threaded workers for SDXL+LoRA inference
- **BKG Access**: Direct Neo4j queries for palette/font recommendations
- **Asset Storage**: Direct S3 uploads and management
- **PDF Service**: Integrated reportlab-based kit generation

### Infrastructure Requirements

**Minimal Setup:**
- 1x GPU-enabled VM (for inference)
  - 16GB+ RAM, 1x NVIDIA GPU (T4, V100, or A10)
  - CUDA-compatible environment
- 1x CPU VM (for API + database)
  - 8GB+ RAM, 4+ vCPUs
- Neo4j database (containerized on CPU VM)
- S3-compatible object storage (AWS S3 or MinIO)

## Technical Implementation

### Core Technologies

- **FastAPI**: Python web framework for API endpoints
- **Celery**: Optional for more sophisticated task queue (can start with Python Queue)
- **SDXL + LoRA**: Stable Diffusion XL with fine-tuned adapters
- **ControlNet**: For color palette and layout constraints
- **Neo4j**: Graph database for brand knowledge relationships
- **ReportLab**: PDF generation for brand kits
- **Docker**: Containerization for consistent deployments

### API Design

**Core Endpoints:**
```
POST /api/v1/brand/generate
GET  /api/v1/brand/{job_id}/status
GET  /api/v1/brand/{job_id}/result
GET  /api/v1/brand/{job_id}/download
```

**Request Flow:**
1. Client submits brand requirements (industry, style, colors)
2. API validates input and creates job record
3. Job queued in-process for GPU worker
4. Worker generates logo using SDXL+LoRA
5. Palette service queries BKG for color recommendations
6. Font service queries BKG for typography suggestions
7. Rationale service generates design explanation
8. PDF service compiles complete brand kit
9. Assets uploaded to S3, job marked complete
10. Client polls for completion and downloads result

## Project Structure

```
01-mvp-monolith/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Local development setup
├── Dockerfile               # Application container
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── brand.py         # Brand generation endpoints
│   │   └── health.py        # Health check endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py       # Pydantic request models
│   │   └── response.py      # Pydantic response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── brand_service.py # Main orchestration service
│   │   ├── bkg_service.py   # Brand Knowledge Graph queries
│   │   ├── pdf_service.py   # Brand kit PDF generation
│   │   └── storage_service.py # S3 asset management
│   └── config.py            # Application configuration
├── workers/
│   ├── __init__.py
│   ├── gpu_worker.py        # SDXL+LoRA inference worker
│   ├── models/
│   │   ├── __init__.py
│   │   ├── sdxl_loader.py   # Model loading utilities
│   │   └── controlnet.py    # ControlNet integration
│   └── utils/
│       ├── __init__.py
│       ├── image_processing.py
│       └── wcag_checker.py  # Color contrast validation
└── deploy/
    ├── docker-compose.prod.yml
    ├── nginx.conf           # Reverse proxy configuration
    └── scripts/
        ├── setup.sh         # Environment setup script
        └── deploy.sh        # Deployment script
```

## Development Setup

### Prerequisites

```bash
# System requirements
- Python 3.9+
- Docker & Docker Compose
- CUDA-compatible GPU (for local testing)
- Git

# Clone and setup
git clone <repo-url>
cd 01-mvp-monolith
pip install -r requirements.txt
```

### Local Development

```bash
# Start dependencies (Neo4j, MinIO)
docker-compose up -d neo4j minio

# Set environment variables
export NEO4J_URI="bolt://localhost:7687"
export S3_ENDPOINT="http://localhost:9000"
export S3_BUCKET="brand-assets"

# Run application
uvicorn api.main:app --reload --port 8000
```

### Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests (requires GPU)
pytest tests/integration/

# Test brand generation
curl -X POST "http://localhost:8000/api/v1/brand/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "technology",
    "style": "modern",
    "primary_color": "#2563eb",
    "company_name": "TechCorp"
  }'
```

## Deployment Options

### Option 1: Single VM Deployment

**VM Specifications:**
- GPU: NVIDIA T4 or better
- CPU: 8+ vCPUs
- RAM: 32GB+
- Storage: 100GB+ SSD

**Deployment Steps:**
```bash
# On target VM
git clone <repo-url>
cd 01-mvp-monolith
./deploy/scripts/setup.sh
./deploy/scripts/deploy.sh
```

### Option 2: Docker Compose Production

```bash
# Production deployment
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### Option 3: Cloud GPU Instance

**AWS EC2:**
- Instance type: g4dn.2xlarge or better
- AMI: Deep Learning AMI (Ubuntu)
- Security groups: HTTP/HTTPS + SSH

**Google Cloud:**
- Instance type: n1-standard-4 + NVIDIA T4
- Image: Deep Learning VM
- Firewall: Allow HTTP/HTTPS traffic

## Monitoring and Operations

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# GPU worker status
curl http://localhost:8000/health/workers

# Database connectivity
curl http://localhost:8000/health/database
```

### Basic Monitoring

- **Application logs**: Docker logs or systemd journal
- **GPU utilization**: `nvidia-smi` monitoring
- **Database health**: Neo4j built-in metrics
- **Storage usage**: S3 bucket metrics

### Scaling Limitations

**When you'll outgrow this architecture:**
- Queue builds up faster than GPU can process
- API becomes unresponsive during heavy inference
- Single point of failure causes downtime
- Need to scale different components independently
- Multiple developers need to deploy independently

## Cost Estimation

### AWS Example (us-east-1):
- EC2 g4dn.2xlarge: ~$0.75/hour ($540/month)
- EBS storage (100GB): ~$10/month
- S3 storage: ~$0.023/GB/month
- Data transfer: ~$0.09/GB out

**Monthly estimate for moderate usage:** $600-800

### Cost Optimization Tips:
- Use spot instances for development
- Implement auto-shutdown during off-hours
- Use lifecycle policies for S3 storage
- Monitor and optimize GPU utilization

## Migration Strategy

### To Queue-Centric Modular:

1. Extract GPU workers to separate service
2. Replace in-process queue with Redis/RabbitMQ
3. Separate BKG service from main API
4. Add load balancer for API instances
5. Implement proper service discovery

### Key Migration Triggers:
- Response times > 30 seconds during peak
- CPU utilization consistently > 80%
- Need for independent scaling of components
- Team growth requiring service boundaries
- Reliability requirements increase

## Common Pitfalls

1. **GPU Memory Management**: Not properly clearing CUDA memory between jobs
2. **Synchronous Operations**: Blocking API while waiting for GPU inference
3. **Resource Contention**: Running database on same machine as GPU workload
4. **Error Handling**: Poor error recovery when GPU workers fail
5. **Storage Limits**: Not implementing cleanup for generated assets

## Success Metrics

Track these KPIs to know when architecture is working:
- **Response time**: < 60 seconds for brand kit generation
- **Success rate**: > 95% successful completions
- **GPU utilization**: 60-80% average usage
- **Error rate**: < 5% API errors
- **Cost per brand**: Track $/generation to optimize resources

---

This MVP Monolith approach gets you from zero to working AI Brand Creator fastest, with clear migration paths as your needs grow.
