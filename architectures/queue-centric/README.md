# Queue-Centric Modular - Brand Generator System Design

## Architecture Rationale

### Why Choose Queue-Centric Modular?

The Queue-Centric Modular approach is designed for **production-ready scalability** with manageable operational complexity. This architecture balances the simplicity of a monolith with the benefits of service separation, making it ideal for teams transitioning from prototype to production.

** We can choose this approach when:**
- You're launching to first real users (100-1,000+ concurrent)
- You need independent scaling of different components
- You have 2-5 developers working on the system
- You require fault isolation between services
- You want to optimize resource utilization (CPU vs GPU workloads)
- You need predictable throughput and performance
- You're planning A/B testing of models or algorithms

**We can not choose this approach when:**
- Prototyping phase 
- Minimization of operational complexity at all costs
- Global scale with complex routing 
- Traffic patterns are extremely spiky 
- Working solo and need maximum development speed

## System Architecture

### High-Level Data Flow

```
Client → API Gateway → Queue (SQS/RabbitMQ) → Specialized Workers → Results → Client
                ↓
            Database & Storage
```

### Service Breakdown

**API Service (CPU-optimized):**
- HTTP request handling and validation
- Job orchestration and status tracking
- Result aggregation and delivery
- Authentication and rate limiting

**Logo Generation Service (GPU-optimized):**
- SDXL + LoRA model inference
- ControlNet integration for constraints
- Image post-processing and optimization
- GPU memory management and pooling

**Palette Service (CPU-optimized):**
- Brand Knowledge Graph queries
- Color theory calculations
- WCAG contrast validation
- Industry-specific recommendations

**Rationale Service (CPU-optimized):**
- LLM-based design explanation
- Multi-language support
- Template-based content generation
- Context-aware recommendations

**PDF Service (CPU-optimized):**
- Brand kit compilation
- Layout and typography
- Asset integration and optimization
- Export format handling

### Infrastructure Components

- **Message Queue**: RabbitMQ or AWS SQS for job distribution
- **Database**: Neo4j for Brand Knowledge Graph
- **Cache**: Redis for session data and temporary results
- **Storage**: S3 for generated assets and templates
- **Load Balancer**: Nginx or AWS ALB for API distribution
- **Monitoring**: Prometheus + Grafana for metrics
- **Orchestration**: Docker Compose or Kubernetes

## Technical Implementation

### Inter-Service Communication

**Queue-Based Messaging:**
```python
# Job lifecycle
1. API receives request → creates job ID
2. API publishes to logo-gen queue
3. Logo service processes → publishes to palette queue
4. Palette service processes → publishes to rationale queue
5. Rationale service processes → publishes to pdf queue
6. PDF service processes → updates job status
7. Client polls API for completion
```

**Message Format:**
```json
{
  "job_id": "uuid-here",
  "type": "brand_generation",
  "payload": {
    "industry": "technology",
    "style": "modern",
    "company_name": "TechCorp",
    "primary_color": "#2563eb"
  },
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z",
    "priority": "normal",
    "timeout": 300
  }
}
```

### Service Architecture Patterns

**API Service Pattern:**
- Gateway pattern for external requests
- Circuit breaker for downstream services
- Request/response correlation
- Async job tracking

**Worker Service Pattern:**
- Consumer pattern for queue messages
- Idempotent processing
- Error handling with retry logic
- Graceful shutdown handling

**Data Service Pattern:**
- Repository pattern for data access
- Connection pooling
- Query optimization
- Caching layer integration

## Project Structure

```
02-queue-centric-modular/
├── README.md                    # This file
├── docker-compose.yml           # Multi-service development setup
├── docker-compose.prod.yml      # Production configuration
├── shared/                      # Shared libraries and utilities
│   ├── __init__.py
│   ├── models/                  # Common data models
│   ├── utils/                   # Shared utilities
│   └── messaging/               # Queue abstractions
├── api-service/
│   ├── README.md               # Service-specific documentation
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application
│   │   ├── routes/            # API endpoints
│   │   ├── models/            # Request/Response models
│   │   ├── services/          # Business logic
│   │   └── middleware/        # Custom middleware
│   └── tests/
├── logo-gen-service/
│   ├── README.md
│   ├── Dockerfile.gpu         # GPU-enabled container
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── worker.py          # Queue consumer
│   │   ├── models/            # SDXL/ControlNet models
│   │   ├── processors/        # Image processing
│   │   └── utils/            # GPU utilities
│   └── tests/
├── palette-service/
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── worker.py          # Queue consumer
│   │   ├── bkg/              # Brand Knowledge Graph
│   │   ├── color/            # Color theory algorithms
│   │   └── wcag/             # Accessibility validation
│   └── tests/
├── rationale-service/
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── worker.py          # Queue consumer
│   │   ├── llm/              # Language model integration
│   │   ├── templates/        # Content templates
│   │   └── i18n/             # Internationalization
│   └── tests/
├── pdf-service/
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── worker.py          # Queue consumer
│   │   ├── generators/       # PDF generation
│   │   ├── templates/        # Layout templates
│   │   └── assets/           # Static resources
│   └── tests/
└── infrastructure/
    ├── terraform/             # Infrastructure as Code
    ├── k8s/                  # Kubernetes manifests
    ├── monitoring/           # Prometheus/Grafana configs
    └── scripts/              # Deployment scripts
```

## Development Workflow

### Local Development Setup

```bash
# Clone repository
git clone <repo-url>
cd 02-queue-centric-modular

# Start infrastructure services
docker-compose up -d rabbitmq neo4j redis minio

# Start individual services (in separate terminals)
cd api-service && uvicorn app.main:app --reload --port 8000
cd logo-gen-service && python app/worker.py
cd palette-service && python app/worker.py
cd rationale-service && python app/worker.py
cd pdf-service && python app/worker.py
```

### Testing Strategy

**Unit Tests:**
- Individual service logic
- Message processing functions
- Data validation and transformation

**Integration Tests:**
- Queue message flow
- Database operations
- External API calls

**End-to-End Tests:**
- Complete brand generation workflow
- Error scenarios and recovery
- Performance under load

### CI/CD Pipeline

**Build Stage:**
```yaml
- Build Docker images for each service
- Run unit tests in parallel
- Static code analysis (mypy, flake8)
- Security scanning
```

**Test Stage:**
```yaml
- Deploy to test environment
- Run integration tests
- Run E2E tests
- Performance benchmarking
```

**Deploy Stage:**
```yaml
- Deploy to staging environment
- Run smoke tests
- Deploy to production (blue/green)
- Health checks and monitoring
```

## Deployment Options

### Option 1: Docker Compose (Simple Production)

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale logo-gen-service=3
```

### Option 2: Kubernetes (Recommended)

```bash
# Deploy infrastructure
kubectl apply -f infrastructure/k8s/namespace.yml
kubectl apply -f infrastructure/k8s/configmaps/
kubectl apply -f infrastructure/k8s/secrets/

# Deploy services
kubectl apply -f infrastructure/k8s/services/
kubectl apply -f infrastructure/k8s/deployments/

# Setup autoscaling
kubectl apply -f infrastructure/k8s/hpa/
```

### Option 3: Cloud Services

**AWS:**
- ECS for service orchestration
- SQS for message queuing
- Neptune for graph database
- S3 for asset storage
- ALB for load balancing

**GCP:**
- GKE for container orchestration
- Pub/Sub for messaging
- Cloud Storage for assets
- Cloud Load Balancing

## Monitoring and Observability

### Key Metrics to Track

**API Service:**
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- Error rate by endpoint
- Queue depth and processing time

**GPU Services:**
- GPU utilization and memory
- Model inference latency
- Queue wait time
- Failed generation rate

**System-wide:**
- End-to-end job completion time
- Resource utilization per service
- Message queue health
- Database connection pool status

### Alerting Rules

```yaml
# High priority alerts
- GPU service down > 5 minutes
- Queue depth > 100 messages
- API error rate > 5%
- End-to-end latency > 5 minutes

# Medium priority alerts
- GPU utilization < 30% (waste)
- Database connection pool > 80%
- Disk usage > 85%
- Memory usage > 90%
```

## Scaling Strategies

### Horizontal Scaling

**GPU Services:**
- Add more GPU nodes for inference
- Auto-scaling based on queue depth
- Load balancing across GPU instances

**CPU Services:**
- Scale API service based on request rate
- Scale palette/rationale services based on queue depth
- Database read replicas for query distribution

### Vertical Scaling

**When to Scale Up:**
- GPU memory constraints (larger models)
- Database query performance
- Complex PDF generation requirements

### Cost Optimization

**GPU Cost Management:**
- Spot instances for non-critical workloads
- Auto-shutdown during low usage periods
- Model optimization (quantization, pruning)

**General Optimization:**
- Reserved instances for predictable workloads
- S3 lifecycle policies for asset cleanup
- Database query optimization
- Connection pooling and caching

## Migration and Evolution

### From MVP Monolith

**Migration Steps:**
1. Extract GPU workers as separate service
2. Introduce message queue (RabbitMQ/SQS)
3. Split API service from business logic
4. Separate database access services
5. Add monitoring and alerting
6. Implement proper CI/CD

**Data Migration:**
- Export existing data from monolith database
- Set up queue infrastructure
- Gradual traffic migration with feature flags

### To Microservices Architecture

**Evolution Triggers:**
- Need for independent team deployments
- Complex business logic requiring separation
- Different SLA requirements per component
- Advanced routing and traffic management needs

**Evolution Strategy:**
- Introduce service mesh (Istio/Linkerd)
- Implement distributed tracing
- Add sophisticated monitoring
- Break down large services further

## Common Challenges and Solutions

### Challenge: Queue Message Ordering

**Problem:** Logo generation must complete before palette selection
**Solution:** Use topic-based routing with sequential processing

### Challenge: GPU Memory Management

**Problem:** Multiple concurrent jobs causing out-of-memory errors
**Solution:** Implement job batching and memory cleanup between jobs

### Challenge: Service Communication Failures

**Problem:** Downstream service failures breaking the pipeline
**Solution:** Implement circuit breakers and retry with exponential backoff

### Challenge: Data Consistency

**Problem:** Job state inconsistency across services
**Solution:** Event sourcing pattern with compensating transactions

## Performance Benchmarks

### Expected Performance

**End-to-End Latency:**
- Simple brand kit: 45-90 seconds
- Complex brand kit: 2-4 minutes
- Batch processing: 10-15 brands/hour per GPU

**Throughput:**
- API requests: 1,000+ req/sec
- Concurrent brand generations: 5-10 per GPU
- Queue processing: 100+ msg/sec per service

**Resource Utilization:**
- GPU utilization: 70-85% optimal
- CPU services: 50-70% average
- Memory usage: < 80% per service
- Queue depth: < 50 messages average

## Success Criteria

This architecture is successful when:
- 99.5% uptime for API service
- < 2 minute average brand generation time
- Ability to scale individual components independently
- Clear service boundaries enabling team autonomy
- Comprehensive monitoring and alerting
- Cost per brand generation < $2.00

---

