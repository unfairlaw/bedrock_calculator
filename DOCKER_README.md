# AWS Cost Agent - Docker Deployment

Complete guide for deploying AWS Cost Agent using Docker and Docker Compose.

## 🐳 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: **http://localhost:5000**

### Option 2: Docker CLI

```bash
# Build image
docker build -t aws-cost-agent .

# Run container
docker run -d \
  --name aws-cost-agent \
  -p 5000:5000 \
  aws-cost-agent

# View logs
docker logs -f aws-cost-agent

# Stop container
docker stop aws-cost-agent
docker rm aws-cost-agent
```

Access at: **http://localhost:5000**

## 📦 What's Included

The Docker image contains:
- ✅ Flask web application
- ✅ AI Cost Agent
- ✅ All 3 calculators (RAG, Compute, Abstract)
- ✅ Web UI (HTML/CSS/JS)
- ✅ REST API
- ✅ Gunicorn WSGI server (4 workers)
- ✅ Health checks
- ✅ Optimized multi-stage build

**Image Size:** ~150MB (compressed)

## 🏗️ Build Configuration

### Dockerfile

```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Build Arguments

Build with custom Python version:
```bash
docker build \
  --build-arg PYTHON_VERSION=3.12 \
  -t aws-cost-agent .
```

## 🚀 Deployment Options

### 1. Development Mode

```bash
docker run -d \
  --name aws-cost-agent-dev \
  -p 5000:5000 \
  -e FLASK_ENV=development \
  -v $(pwd):/app \
  aws-cost-agent
```

Features:
- Auto-reload on code changes
- Debug mode enabled
- Volume mounting for live editing

### 2. Production Mode (Default)

```bash
docker run -d \
  --name aws-cost-agent-prod \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  --restart unless-stopped \
  aws-cost-agent
```

Features:
- Gunicorn with 4 workers
- Production-optimized
- Auto-restart on failure
- Health checks

### 3. With Nginx Reverse Proxy

```bash
# Start with production profile
docker-compose --profile production up -d
```

Features:
- Nginx on port 80
- Load balancing
- Static file caching
- SSL/TLS ready

Access at: **http://localhost**

## 🔧 Configuration

### Environment Variables

```bash
docker run -d \
  --name aws-cost-agent \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e WORKERS=8 \
  -e TIMEOUT=120 \
  -e LOG_LEVEL=info \
  aws-cost-agent
```

**Available Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `WORKERS` | `4` | Gunicorn workers |
| `TIMEOUT` | `120` | Request timeout (seconds) |
| `PORT` | `5000` | Server port |
| `LOG_LEVEL` | `info` | Logging level |

### Volume Mounts

```bash
docker run -d \
  --name aws-cost-agent \
  -p 5000:5000 \
  -v $(pwd)/pricing_cache:/app/.aws_pricing_cache \
  -v $(pwd)/logs:/app/logs \
  aws-cost-agent
```

**Useful Mounts:**

- `/app/.aws_pricing_cache` - Pricing data cache
- `/app/logs` - Application logs
- `/app/static` - Static files (for customization)

## 📊 Docker Compose

### Basic Configuration

```yaml
version: '3.8'

services:
  aws-cost-agent:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Advanced Configuration

```yaml
version: '3.8'

services:
  aws-cost-agent:
    build:
      context: .
      dockerfile: Dockerfile
    image: aws-cost-agent:latest
    container_name: aws-cost-agent
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - WORKERS=4
    volumes:
      - pricing_cache:/app/.aws_pricing_cache
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - app-network

volumes:
  pricing_cache:

networks:
  app-network:
    driver: bridge
```

### Commands

```bash
# Build
docker-compose build

# Start (detached)
docker-compose up -d

# Start (with logs)
docker-compose up

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Scale workers (if using multiple containers)
docker-compose up -d --scale aws-cost-agent=3
```

## 🌐 Nginx Integration

### With Docker Compose

```bash
# Start with Nginx
docker-compose --profile production up -d
```

This starts:
1. **aws-cost-agent** on port 5000 (internal)
2. **nginx** on port 80 (public)

### Nginx Configuration

File: `nginx.conf`

```nginx
http {
    upstream app {
        server aws-cost-agent:5000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
        }
    }
}
```

### SSL/TLS Setup

Add certificates:

```bash
# Create certs directory
mkdir -p certs

# Add your certificates
cp your-cert.crt certs/
cp your-key.key certs/

# Update nginx.conf
# Add:
#   listen 443 ssl;
#   ssl_certificate /etc/nginx/certs/your-cert.crt;
#   ssl_certificate_key /etc/nginx/certs/your-key.key;
```

Update docker-compose.yml:

```yaml
nginx:
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./certs:/etc/nginx/certs:ro
  ports:
    - "80:80"
    - "443:443"
```

## 🔍 Monitoring

### Health Checks

Built-in health check:

```bash
# Docker
docker inspect --format='{{.State.Health.Status}}' aws-cost-agent

# Docker Compose
docker-compose ps
```

Manual check:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T...",
  "version": "1.0.0"
}
```

### Logs

```bash
# Docker
docker logs aws-cost-agent
docker logs -f aws-cost-agent  # Follow
docker logs --tail 100 aws-cost-agent  # Last 100 lines

# Docker Compose
docker-compose logs
docker-compose logs -f
docker-compose logs aws-cost-agent
```

### Resource Usage

```bash
# Stats
docker stats aws-cost-agent

# Inspect
docker inspect aws-cost-agent
```

## 🎯 Production Best Practices

### 1. Resource Limits

```yaml
services:
  aws-cost-agent:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. Logging

```yaml
services:
  aws-cost-agent:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. Security

```bash
# Run as non-root user
# Update Dockerfile:
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only filesystem
docker run -d \
  --read-only \
  --tmpfs /tmp \
  aws-cost-agent
```

### 4. Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 5. Restart Policy

```yaml
restart: unless-stopped
```

Options:
- `no` - Never restart
- `on-failure` - Restart on non-zero exit
- `always` - Always restart
- `unless-stopped` - Always restart unless manually stopped

## 🚢 Cloud Deployment

### AWS ECS

```bash
# Build and tag
docker build -t aws-cost-agent .
docker tag aws-cost-agent:latest <account>.dkr.ecr.us-east-1.amazonaws.com/aws-cost-agent:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/aws-cost-agent:latest

# Deploy to ECS (use AWS Console or CLI)
```

### Google Cloud Run

```bash
# Build and push
docker build -t gcr.io/PROJECT_ID/aws-cost-agent .
docker push gcr.io/PROJECT_ID/aws-cost-agent

# Deploy
gcloud run deploy aws-cost-agent \
  --image gcr.io/PROJECT_ID/aws-cost-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Build and push to ACR
az acr build --registry myregistry --image aws-cost-agent .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name aws-cost-agent \
  --image myregistry.azurecr.io/aws-cost-agent:latest \
  --ports 5000 \
  --dns-name-label aws-cost-agent
```

### DigitalOcean App Platform

```bash
# Use docker-compose.yml or Dockerfile
# Deploy via DigitalOcean UI or CLI
doctl apps create --spec app.yaml
```

## 🧪 Testing

### Build Test

```bash
docker build -t aws-cost-agent:test .
```

### Run Test

```bash
# Start container
docker run -d --name test -p 5000:5000 aws-cost-agent:test

# Test API
curl http://localhost:5000/api/health

# Test estimation
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -d '{"query": "How much for 10 t3.medium instances?"}'

# Cleanup
docker stop test && docker rm test
```

### Integration Test

```bash
# Start with docker-compose
docker-compose up -d

# Wait for healthy
sleep 10

# Run tests
curl http://localhost:5000/api/health
curl http://localhost:5000/api/tools
curl http://localhost:5000/api/examples

# Cleanup
docker-compose down
```

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs aws-cost-agent

# Check if port is in use
lsof -i :5000

# Try different port
docker run -p 8080:5000 aws-cost-agent
```

### Health Check Failing

```bash
# Exec into container
docker exec -it aws-cost-agent bash

# Test internally
curl http://localhost:5000/api/health

# Check Python
python -c "import flask; print(flask.__version__)"
```

### Slow Performance

```bash
# Increase workers
docker run -e WORKERS=8 aws-cost-agent

# Increase memory
docker run -m 2g aws-cost-agent

# Check resources
docker stats aws-cost-agent
```

### Cache Issues

```bash
# Clear cache
docker-compose down
docker-compose rm -f
docker volume rm bedrock_calculator_pricing_cache

# Rebuild without cache
docker-compose build --no-cache
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## 🔐 Security Checklist

- [ ] Run as non-root user
- [ ] Use specific version tags (not `:latest`)
- [ ] Scan images for vulnerabilities
- [ ] Use secrets management for sensitive data
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Minimal base image (alpine/slim)
- [ ] Read-only filesystem where possible
- [ ] Network isolation

## 📝 Example docker-compose.yml

Complete production-ready configuration:

```yaml
version: '3.8'

services:
  aws-cost-agent:
    build:
      context: .
      dockerfile: Dockerfile
    image: aws-cost-agent:1.0
    container_name: aws-cost-agent
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - WORKERS=4
      - TIMEOUT=120
    volumes:
      - pricing_cache:/app/.aws_pricing_cache
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - app-network

volumes:
  pricing_cache:
    driver: local

networks:
  app-network:
    driver: bridge
```

---

**Ready for Production!** 🚀

Your AWS Cost Agent is now containerized and ready to deploy anywhere Docker runs.
