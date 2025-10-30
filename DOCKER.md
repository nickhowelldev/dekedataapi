# Docker Deployment Guide

## Quick Start (3 steps)

### 1. Create `.env` file
```bash
cat > .env << EOF
PROJECT_NAME=DekeData API
API_V1_STR=/api/v1
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/database
EOF
```

### 2. Start the container
```bash
docker-compose up -d
```

### 3. Run migrations (first time only)
```bash
docker exec dekedataapi alembic upgrade head
```

**Done!** API running at http://localhost:8000

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run migrations
docker exec dekedataapi alembic upgrade head

# Access container shell
docker exec -it dekedataapi bash

# Check health
curl http://localhost:8000/health
```

## Manual Docker Commands

Without docker-compose:

```bash
# Build
docker build -t dekedataapi .

# Run
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name dekedataapi \
  dekedataapi

# Logs
docker logs -f dekedataapi

# Stop
docker stop dekedataapi
docker rm dekedataapi
```

## Environment Variables

Required in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `PROJECT_NAME` | API name | `DekeData API` |
| `API_V1_STR` | API version prefix | `/api/v1` |
| `ENVIRONMENT` | Environment name | `production` |

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs dekedataapi

# Common issues:
# 1. Database connection - verify DATABASE_URL
# 2. Port 8000 already in use - change port mapping
```

### Database connection errors
```bash
# Test database connectivity
docker exec dekedataapi python -c "from app.db.base import engine; print(engine.connect())"
```

### Reset everything
```bash
docker-compose down
docker-compose up -d --build
docker exec dekedataapi alembic upgrade head
```

## Production Deployment

### Deploy to Cloud Platforms

**Railway:**
- Push to Git repository
- Connect repository in Railway dashboard
- Add environment variables
- Railway auto-detects Dockerfile and deploys

**Render:**
- New Web Service → Connect repository
- Build command: (auto-detected)
- Start command: (auto-detected from Dockerfile)
- Add environment variables

**Fly.io:**
```bash
fly launch
fly secrets set DATABASE_URL="postgresql://..."
fly deploy
```

**DigitalOcean:**
- App Platform → Create App
- Select repository
- Dockerfile detected automatically
- Add environment variables

### Health Checks

All platforms should use:
- **Health check path:** `/health`
- **Port:** `8000`
- **Timeout:** 10s
- **Interval:** 30s

## Docker Image Details

- **Base:** `python:3.11-slim`
- **Size:** ~200MB
- **Port:** 8000
- **Workers:** 4 Gunicorn workers with Uvicorn
- **User:** root (can be changed for additional security)

## Security Hardening (Optional)

### Run as non-root user

Edit `Dockerfile`:
```dockerfile
# Add before CMD
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

### Multi-stage build for smaller image

Edit `Dockerfile`:
```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", ...]
```

## Monitoring

### Resource Usage
```bash
# CPU and Memory
docker stats dekedataapi

# Disk space
docker system df
```

### Application Metrics
- Use `/health` endpoint for basic monitoring
- Use `/` endpoint for API info
- Use `/docs` for interactive testing

## Backup & Restore

### Backup
```bash
# Export container image
docker save dekedataapi > dekedataapi-backup.tar

# Export compose config
docker-compose config > docker-compose-backup.yml
```

### Restore
```bash
# Load image
docker load < dekedataapi-backup.tar

# Start from backup
docker-compose -f docker-compose-backup.yml up -d
```

## Performance Tuning

### Adjust worker count

Edit `Dockerfile` CMD or `docker-compose.yml`:
```yaml
command: gunicorn app.main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Rule of thumb:** `(2 x CPU cores) + 1` workers

### Resource limits

Edit `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

**Need help?** Check the main [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.
