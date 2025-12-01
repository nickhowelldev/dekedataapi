from fastapi import APIRouter
from app.api.v1.endpoints import (
    users,
    leagues,
    dekedata_leagues,
    teams,
    seasons,
    players,
    player_seasons,
    player_stats,
    goalie_stats,
    scores,
    drafts,
    lists
)

api_router = APIRouter()

# Original routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])

# DekeData schema routes
api_router.include_router(dekedata_leagues.router, prefix="/dekedata/leagues", tags=["dekedata-leagues"])
api_router.include_router(lists.router, prefix="/dekedata/lists", tags=["dekedata-lists"])
api_router.include_router(teams.router, prefix="/dekedata/teams", tags=["dekedata-teams"])
api_router.include_router(seasons.router, prefix="/dekedata/seasons", tags=["dekedata-seasons"])
api_router.include_router(players.router, prefix="/dekedata/players", tags=["dekedata-players"])
api_router.include_router(player_seasons.router, prefix="/dekedata/player-seasons", tags=["dekedata-player-seasons"])
api_router.include_router(player_stats.router, prefix="/dekedata/player-stats", tags=["dekedata-player-stats"])
api_router.include_router(goalie_stats.router, prefix="/dekedata/goalie-stats", tags=["dekedata-goalie-stats"])
api_router.include_router(scores.router, prefix="/dekedata/scores", tags=["dekedata-scores"])
api_router.include_router(drafts.router, prefix="/dekedata/drafts", tags=["dekedata-drafts"])
