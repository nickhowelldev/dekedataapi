from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A FastAPI-based REST API for managing users, teams, leagues, and hockey player data.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "users",
            "description": "Operations with users. Create, read, update, and delete user accounts.",
        },
        {
            "name": "leagues",
            "description": "Manage leagues. CRUD operations for sports leagues.",
        },
        {
            "name": "dekedata-leagues",
            "description": "DekeData leagues - canonical league list with tier and country information.",
        },
        {
            "name": "dekedata-teams",
            "description": "DekeData teams - teams associated with leagues.",
        },
        {
            "name": "dekedata-seasons",
            "description": "DekeData seasons - season catalog (e.g., 2024-25).",
        },
        {
            "name": "dekedata-players",
            "description": "DekeData players - master player profiles with position, birth year, physical stats.",
        },
        {
            "name": "dekedata-player-seasons",
            "description": "DekeData player seasons - player membership in league/team for a season.",
        },
        {
            "name": "dekedata-player-stats",
            "description": "DekeData player stats - skater statistics (forwards and defensemen).",
        },
        {
            "name": "dekedata-goalie-stats",
            "description": "DekeData goalie stats - goalie-specific statistics.",
        },
        {
            "name": "dekedata-scores",
            "description": "DekeData scores - scouting scores and evaluations.",
        },
        {
            "name": "dekedata-drafts",
            "description": "DekeData drafts - multi-league draft probabilities and projections.",
        },
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Welcome to DekeData API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["root"])
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
