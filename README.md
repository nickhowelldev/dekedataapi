# DekeData API

A FastAPI-based REST API for managing users, teams, leagues, and comprehensive hockey player statistics, scouting scores, and draft projections.

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL database (Supabase or local)

### Installation

1. Clone the repository

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory:
```env
PROJECT_NAME=DekeData API
API_V1_STR=/api/v1
DATABASE_URL=postgresql://user:password@host:5432/database
```

6. Initialize the database (if starting fresh):
```bash
# Run migrations to sync with your database
alembic upgrade head
```

### Running the Application

**Option 1: Docker (Recommended)**
```bash
# Quick start with Docker
docker-compose up -d
docker exec dekedataapi alembic upgrade head

# See DOCKER.md for full Docker guide
```

**Option 2: Local Development**
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

### API Endpoints

#### Users
- `GET /api/v1/users` - Get all users
- `GET /api/v1/users/{user_id}` - Get a specific user
- `POST /api/v1/users` - Create a new user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

#### Leagues
- `GET /api/v1/leagues` - Get all leagues
- `GET /api/v1/leagues/{league_id}` - Get a specific league
- `POST /api/v1/leagues` - Create a new league
- `PUT /api/v1/leagues/{league_id}` - Update a league
- `DELETE /api/v1/leagues/{league_id}` - Delete a league

#### DekeData Schema
Complete documentation available in [DEKEDATA_SCHEMA.md](DEKEDATA_SCHEMA.md)

The DekeData schema provides comprehensive hockey data management with 9 entity types:
- **Leagues** (`/api/v1/dekedata/leagues`) - League information with tier classifications
- **Teams** (`/api/v1/dekedata/teams`) - Team rosters and affiliations
- **Seasons** (`/api/v1/dekedata/seasons`) - Season definitions (e.g., "2024-25")
- **Players** (`/api/v1/dekedata/players`) - Player profiles with physical stats
- **Player Seasons** (`/api/v1/dekedata/player-seasons`) - Player affiliations per season
- **Player Stats** (`/api/v1/dekedata/player-stats`) - Skater statistics (F/D)
- **Goalie Stats** (`/api/v1/dekedata/goalie-stats`) - Goaltender statistics
- **Scores** (`/api/v1/dekedata/scores`) - Scouting evaluations and ratings
- **Drafts** (`/api/v1/dekedata/drafts`) - Draft probabilities across leagues

**Features:**
- Database triggers enforce position-based stats (skaters vs goalies)
- Materialized view for current player affiliations
- Analytics view combining all player/season/stats data
- Support for Regular/Playoff/Exhibition splits
- Multi-league draft probability tracking
- Height stored in centimeters, weight in kilograms (frontend handles unit conversion)

#### Player Profile Endpoints

Comprehensive endpoints for retrieving player profile data. All endpoints return data organized for frontend consumption.

**Comprehensive Endpoint** (recommended):
- `GET /api/v1/dekedata/players/{player_id}/profile` - Get all player data in one call
  - Returns: player details, all seasons, youth scores (ages 13-17), draft probabilities, and historical snapshots for most recent season
  - No query parameters needed - automatically fetches most recent season progress

**Individual Endpoints** (for granular data access):
- `GET /api/v1/dekedata/players/{player_id}/seasons` - Season-by-season statistics
  - Query params: `season_id` (optional), `league_id` (optional)
  - Returns: List of seasons with team, league, and stats (skater or goalie)

- `GET /api/v1/dekedata/players/{player_id}/youth-scores` - Youth development scores
  - Returns: Scouting scores for ages 13-17 (overall, skating, shot, IQ, compete, physical)

- `GET /api/v1/dekedata/players/{player_id}/probabilities` - Draft probability data
  - Returns: Draft league, probability percentage, round estimate, team hints

- `GET /api/v1/dekedata/players/{player_id}/season-progress` - Historical stat tracking
  - Query params: `player_season_id` (required)
  - Returns: Daily snapshots of cumulative season stats (for charting season progression)

**Implementation Notes:**
- All endpoints use eager loading to prevent N+1 queries
- Position-aware: automatically returns skater or goalie stats based on player position
- Historical tracking requires `player_season_stats_history` and `goalie_season_stats_history` tables
- Date snapshots stored as ISO format strings for frontend compatibility

## Database Migrations

This project uses Alembic for database migrations (similar to Drizzle in Next.js).

### Common Migration Commands

```bash
# Generate a new migration after changing models
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# Check current migration version
alembic current

# View migration history
alembic history
```

### Making Schema Changes

1. Make changes to your database directly or modify SQLAlchemy models
2. Generate a migration: `alembic revision --autogenerate -m "add new column"`
3. Review the generated migration file in `alembic/versions/`
4. Apply the migration: `alembic upgrade head`

## Development

### Adding New Endpoints

1. Create a new file in `app/api/v1/endpoints/`
2. Define your router and endpoints
3. Create corresponding schemas in `app/schemas/`
4. Import and include the router in `app/api/v1/api.py`

### Project Organization

```
dekedataapi/
├── app/
│   ├── api/v1/endpoints/  # API route handlers
│   ├── core/              # Config and settings
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models (optional)
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── alembic/               # Database migrations
│   └── versions/          # Migration files
├── tests/                 # Test files
└── .env                   # Environment variables
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Deployment

### Environment Configuration

For production, update your `.env` file:

```env
PROJECT_NAME=DekeData API
API_V1_STR=/api/v1
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Running in Production

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn + Uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Pre-Deployment Checklist

- ✅ All migrations applied: `alembic upgrade head`
- ✅ Environment variables configured in `.env`
- ✅ Database connection tested
- ✅ CORS origins configured (currently allows all origins)
- ✅ API documentation accessible at `/docs`
- ✅ Health check endpoint at `/`

### Security Considerations

1. **CORS**: Currently configured to allow all origins (`allow_origins=["*"]`). For production, update in `app/main.py`:
   ```python
   allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"]
   ```

2. **Database**: Ensure PostgreSQL credentials are secure and not committed to version control

3. **Rate Limiting**: Consider adding rate limiting middleware for production use

4. **HTTPS**: Always use HTTPS in production (configure at reverse proxy/load balancer level)