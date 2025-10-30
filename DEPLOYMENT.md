# DekeData API - Deployment Guide

## Pre-Deployment Checklist ✅

### 1. Environment Setup
- [x] `.env` file configured with production database URL
- [x] PostgreSQL database accessible
- [x] All environment variables set

### 2. Database
- [x] All migrations applied (`alembic upgrade head`)
- [x] Database schema version: `0878a2a8ac3b` (includes age field for youth scores)
- [x] Database indexes optimized for player search
- [x] Sample data loaded (3,412 players with 14,849 youth scores)

### 3. Code Quality
- [x] No hardcoded secrets or credentials
- [x] All imports optimized
- [x] Python cache files cleaned
- [x] No inline comments or dead code
- [x] Error handling in place

### 4. API Configuration
- [x] CORS middleware enabled (configured for all origins - update for production)
- [x] Health check endpoint at `/health`
- [x] API documentation at `/docs` and `/redoc`
- [x] Proper response models and validation

### 5. Dependencies
- [x] All production dependencies in `requirements.txt`
- [x] Gunicorn added for production server
- [x] FastAPI 0.115.5 with standard features
- [x] PostgreSQL driver (psycopg2-binary)

## Quick Start

### Option 1: Docker Deployment (Recommended) 🐳

**1. Set Environment Variables**
Create `.env` file:
```env
PROJECT_NAME=DekeData API
API_V1_STR=/api/v1
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/database
```

**2. Build and Run with Docker**
```bash
# Build the image
docker build -t dekedataapi .

# Run the container
docker run -d -p 8000:8000 --env-file .env --name dekedataapi dekedataapi

# Or use docker-compose (easier)
docker-compose up -d
```

**3. Run Migrations (First time only)**
```bash
docker exec dekedataapi alembic upgrade head
```

**4. Check Logs**
```bash
docker logs -f dekedataapi
```

**5. Stop/Restart**
```bash
# Stop
docker-compose down

# Restart
docker-compose up -d
```

### Option 2: Manual Deployment

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Set Environment Variables**
Create/update `.env`:
```env
PROJECT_NAME=DekeData API
API_V1_STR=/api/v1
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/database
```

**3. Run Database Migrations**
```bash
alembic upgrade head
```

**4. Start the Server**

**Development:**
```bash
uvicorn app.main:app --reload
```

**Production:**
```bash
# Option 1: Gunicorn with Uvicorn workers (recommended)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Option 2: Uvicorn with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints Overview

### Core Endpoints
- `GET /` - API welcome/info
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger)
- `GET /redoc` - Alternative API documentation

### DekeData Entities
- `/api/v1/dekedata/players` - Player profiles
- `/api/v1/dekedata/players/search` - **Advanced search with 20+ filters**
- `/api/v1/dekedata/teams` - Teams
- `/api/v1/dekedata/leagues` - Leagues
- `/api/v1/dekedata/seasons` - Seasons
- `/api/v1/dekedata/player-seasons` - Player affiliations
- `/api/v1/dekedata/player-stats` - Skater statistics
- `/api/v1/dekedata/goalie-stats` - Goalie statistics
- `/api/v1/dekedata/scores` - Scouting scores
- `/api/v1/dekedata/drafts` - Draft projections

## Key Features

### Player Search Endpoint
The `/api/v1/dekedata/players/search` endpoint is the flagship feature:

**Filters Available:**
- Name search (partial match)
- Position (F, D, G)
- Birth year range
- Height/weight ranges
- Handedness (shoots)
- **Score filters** (min/max for overall, skating, shot, iq, compete, physical)

**Sorting:**
- Any column (name, position, birth_year, height, weight, shoots, overall)
- Ascending or descending

**Response Features:**
- Pagination (skip/limit)
- Total count metadata
- Min/max ranges for filters
- Optional youth scores (ages 13-17)
- Overall rating (average of youth scores)

**Example Queries:**
```bash
# Top-rated prospects
GET /api/v1/dekedata/players/search?min_overall=85&sort_by=overall&sort_direction=desc

# Skilled forwards
GET /api/v1/dekedata/players/search?position=F&min_skating=80&min_shot=80

# Tall defensemen with high IQ
GET /api/v1/dekedata/players/search?position=D&min_height=185&min_iq=80
```

See [PLAYER_SEARCH.md](PLAYER_SEARCH.md) for complete documentation.

## Security Considerations

### 1. CORS Configuration
**Current:** Allows all origins (`allow_origins=["*"]`)

**For Production:** Update in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Database Security
- ✅ Credentials stored in `.env` (not committed)
- ✅ `.env` in `.gitignore`
- ✅ Connection pooling handled by SQLAlchemy
- ⚠️ Ensure database has SSL enabled for production

### 3. API Security
- ✅ Input validation via Pydantic schemas
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ Query parameter validation
- 🔄 Consider adding: Authentication, rate limiting, API keys

### 4. HTTPS
- Always deploy behind a reverse proxy (Nginx, Caddy, etc.)
- Let's Encrypt for SSL certificates
- Force HTTPS redirects

## Performance Optimization

### Database Indexes
The following indexes are in place for optimal query performance:

**Players table:**
- `ix_players_name_lower` - Case-insensitive name search
- `ix_players_position` - Position filtering
- `ix_players_birth_year` - Birth year filtering
- `ix_players_position_birth_year` - Combined filtering

**Scores table:**
- `ix_scores_player_season` - Player/season lookups
- `ix_scores_player_age` - Youth score queries

### Query Optimization
- Subqueries for score filtering (only joins when needed)
- Eager loading for relationships with `selectinload()`
- Pagination limits (max 1000 records per request)

### Recommended Production Settings
- Use connection pooling (default in SQLAlchemy)
- Enable query result caching for frequently accessed data
- Consider read replicas for heavy read workloads
- Monitor slow queries with database logging

## Monitoring & Maintenance

### Health Checks
```bash
# Basic health check
curl https://api.yourdomain.com/health

# API availability
curl https://api.yourdomain.com/

# Database connectivity
curl https://api.yourdomain.com/api/v1/dekedata/players?limit=1
```

### Database Maintenance
```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Apply pending migrations
alembic upgrade head

# Rollback last migration (if needed)
alembic downgrade -1
```

### Logs
Monitor application logs for:
- Database connection errors
- Slow query warnings
- Input validation errors
- Unhandled exceptions

## Deployment Platforms

### Recommended Platforms
1. **Railway** - Easy PostgreSQL + FastAPI deployment
2. **Render** - Free tier available, auto-deploys from Git
3. **Fly.io** - Global edge deployment
4. **DigitalOcean App Platform** - Managed infrastructure
5. **AWS ECS/Fargate** - Enterprise-grade, requires more setup

### Docker Deployment

**Files included:**
- `Dockerfile` - Production-ready container image
- `docker-compose.yml` - Easy orchestration
- `.dockerignore` - Optimized build context

**Deploy to any platform:**

**Railway:**
```bash
# Railway will auto-detect Dockerfile
railway up
```

**Render / Fly.io:**
- Connect your Git repository
- Set environment variables in dashboard
- Deploy will use Dockerfile automatically

**AWS ECS/Fargate:**
```bash
# Build and push to ECR
docker build -t dekedataapi .
docker tag dekedataapi:latest <account-id>.dkr.ecr.<region>.amazonaws.com/dekedataapi:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/dekedataapi:latest
```

**Self-hosted (any server with Docker):**
```bash
# Clone repo
git clone <your-repo-url>
cd dekedataapi

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Deploy
docker-compose up -d

# Run migrations
docker exec dekedataapi alembic upgrade head
```

## Post-Deployment Verification

### 1. Test Endpoints
```bash
# Health check
curl https://api.yourdomain.com/health

# Root endpoint
curl https://api.yourdomain.com/

# Search endpoint (basic)
curl "https://api.yourdomain.com/api/v1/dekedata/players/search?limit=5"

# Search with filters
curl "https://api.yourdomain.com/api/v1/dekedata/players/search?position=F&min_overall=80"
```

### 2. Verify Documentation
- Visit `https://api.yourdomain.com/docs`
- Test endpoints in Swagger UI
- Verify all schemas render correctly

### 3. Performance Testing
```bash
# Use Apache Bench for load testing
ab -n 1000 -c 10 https://api.yourdomain.com/api/v1/dekedata/players/search?limit=10
```

### 4. Monitor Logs
- Check for startup errors
- Verify database connections
- Monitor request/response times

## Troubleshooting

### Database Connection Issues
```bash
# Test database connectivity
python -c "from app.db.base import engine; print(engine.connect())"

# Verify migrations
alembic current
```

### CORS Errors
- Check browser console for specific error
- Verify `allow_origins` in `app/main.py`
- Ensure frontend domain is in allowed origins list

### Slow Queries
- Check database indexes: `SELECT * FROM pg_indexes WHERE schemaname = 'dekedata';`
- Monitor query performance in PostgreSQL logs
- Consider adding missing indexes for common queries

## Support & Documentation

- **API Documentation:** `/docs` and `/redoc` endpoints
- **Player Search Guide:** [PLAYER_SEARCH.md](PLAYER_SEARCH.md)
- **Schema Documentation:** [DEKEDATA_SCHEMA.md](DEKEDATA_SCHEMA.md)
- **Main README:** [README.md](README.md)

## Version Information

- **API Version:** 1.0.0
- **FastAPI Version:** 0.115.5
- **Python Version:** 3.8+
- **Database Schema Version:** 0878a2a8ac3b
- **Total Players:** 3,412
- **Total Youth Scores:** 14,849

---

**Ready for Production Deployment** ✅

Last Updated: 2025-10-30
