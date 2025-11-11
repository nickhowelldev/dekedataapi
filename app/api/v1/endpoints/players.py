from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import func, text
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.db.base import get_db
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from app.schemas.player_search import PlayerSearchResponse, PlayerSearchMetadata
from app.schemas.player_profile import (
    PlayerSeasonsResponse, PlayerSeasonResponse, SeasonStatsDetail, GoalieSeasonStatsDetail,
    PlayerYouthScoresResponse, YouthScoreDetail,
    PlayerDraftResponse, DraftProbabilityDetail,
    PlayerSeasonProgressResponse, SeasonProgressSnapshot, GoalieSeasonProgressSnapshot,
    PlayerProfileResponse, PlayerDetails
)
from app.models.player import Player
from app.models.score import Score
from app.models.player_season import PlayerSeason
from app.models.season import Season
from app.models.league import League
from app.models.team import Team
from app.models.draft import Draft

router = APIRouter()


@router.get("/search", response_model=PlayerSearchResponse)
def search_players(
    q: Optional[str] = Query(None, description="Search query for player name"),
    position: Optional[str] = Query(None, description="Filter by position (F, D, G)"),
    birth_year_min: Optional[int] = Query(None, description="Minimum birth year"),
    birth_year_max: Optional[int] = Query(None, description="Maximum birth year"),
    shoots: Optional[str] = Query(None, description="Handedness (L, R, C)"),
    min_height: Optional[Decimal] = Query(None, description="Minimum height in cm"),
    max_height: Optional[Decimal] = Query(None, description="Maximum height in cm"),
    min_weight: Optional[Decimal] = Query(None, description="Minimum weight in kg"),
    max_weight: Optional[Decimal] = Query(None, description="Maximum weight in kg"),
    min_overall: Optional[Decimal] = Query(None, description="Minimum overall score (youth average)"),
    max_overall: Optional[Decimal] = Query(None, description="Maximum overall score (youth average)"),
    min_skating: Optional[Decimal] = Query(None, description="Minimum skating score (youth average)"),
    max_skating: Optional[Decimal] = Query(None, description="Maximum skating score (youth average)"),
    min_shot: Optional[Decimal] = Query(None, description="Minimum shot score (youth average)"),
    max_shot: Optional[Decimal] = Query(None, description="Maximum shot score (youth average)"),
    min_iq: Optional[Decimal] = Query(None, description="Minimum IQ score (youth average)"),
    max_iq: Optional[Decimal] = Query(None, description="Maximum IQ score (youth average)"),
    min_compete: Optional[Decimal] = Query(None, description="Minimum compete score (youth average)"),
    max_compete: Optional[Decimal] = Query(None, description="Maximum compete score (youth average)"),
    min_physical: Optional[Decimal] = Query(None, description="Minimum physical score (youth average)"),
    max_physical: Optional[Decimal] = Query(None, description="Maximum physical score (youth average)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    include_youth_scores: bool = Query(False, description="Include youth scores (ages 13-17)"),
    youth_score_age: Optional[int] = Query(None, description="Filter by specific youth score age (13-17)"),
    youth_score_min: Optional[Decimal] = Query(None, description="Minimum overall score for the specified age"),
    youth_score_max: Optional[Decimal] = Query(None, description="Maximum overall score for the specified age"),
    sort_by: str = Query("name", description="Column to sort by (name, position, birth_year, height, weight, shoots, overall)"),
    sort_direction: str = Query("asc", description="Sort direction (asc or desc)"),
    db: Session = Depends(get_db)
):
    """
    Advanced player search with multiple filters and metadata.

    Returns paginated results plus metadata including:
    - Total count of matching records
    - Min/max values for height, weight, birth_year from ALL matching records
    - Optional youth scores (ages 13-17) when include_youth_scores=true

    Searches are optimized with database indexes for fast performance.
    All filters can be combined for precise results.

    **Examples:**
    - `/search?q=bedard` - Search by name (sorted by name asc by default)
    - `/search?position=F&birth_year_min=2005` - Forwards born 2005 or later
    - `/search?min_height=180&max_height=190` - Players 180-190cm tall
    - `/search?position=D&shoots=L` - Left-handed defensemen
    - `/search?q=bedard&include_youth_scores=true` - Search with youth scores
    - `/search?include_youth_scores=true&youth_score_age=14` - Players with age 14 scores
    - `/search?include_youth_scores=true&youth_score_age=14&youth_score_min=88&youth_score_max=100` - Players with age 14 scores between 88-100
    - `/search?sort_by=birth_year&sort_direction=desc` - Sort by birth year newest first
    - `/search?sort_by=height&sort_direction=desc` - Sort by height tallest first
    - `/search?sort_by=overall&sort_direction=desc` - Sort by overall score (youth average) highest first
    - `/search?min_overall=75&max_overall=85` - Players with overall score between 75-85
    - `/search?position=F&min_skating=80&min_shot=80` - Forwards with 80+ skating and shot
    """
    query = db.query(Player)

    if include_youth_scores:
        query = query.options(selectinload(Player.scores))

    # Apply youth score age filters to filter which players are returned
    if youth_score_age is not None:
        score_subquery = (
            db.query(Score.player_id)
            .filter(Score.age == youth_score_age)
        )
        if youth_score_min is not None:
            score_subquery = score_subquery.filter(Score.overall >= youth_score_min)
        if youth_score_max is not None:
            score_subquery = score_subquery.filter(Score.overall <= youth_score_max)
        score_subquery = score_subquery.distinct().subquery()
        query = query.join(score_subquery, Player.id == score_subquery.c.player_id)

    score_filters_active = any([
        min_overall, max_overall, min_skating, max_skating,
        min_shot, max_shot, min_iq, max_iq,
        min_compete, max_compete, min_physical, max_physical
    ])

    if score_filters_active:
        avg_scores_subquery = (
            db.query(
                Score.player_id,
                func.avg(Score.overall).label('avg_overall'),
                func.avg(Score.skating).label('avg_skating'),
                func.avg(Score.shot).label('avg_shot'),
                func.avg(Score.iq).label('avg_iq'),
                func.avg(Score.compete).label('avg_compete'),
                func.avg(Score.physical).label('avg_physical')
            )
            .filter(Score.age.between(13, 17))
            .group_by(Score.player_id)
            .subquery()
        )
        query = query.join(avg_scores_subquery, Player.id == avg_scores_subquery.c.player_id)

        if min_overall:
            query = query.filter(avg_scores_subquery.c.avg_overall.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_overall >= min_overall)
        if max_overall:
            query = query.filter(avg_scores_subquery.c.avg_overall.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_overall <= max_overall)
        if min_skating:
            query = query.filter(avg_scores_subquery.c.avg_skating.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_skating >= min_skating)
        if max_skating:
            query = query.filter(avg_scores_subquery.c.avg_skating.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_skating <= max_skating)
        if min_shot:
            query = query.filter(avg_scores_subquery.c.avg_shot.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_shot >= min_shot)
        if max_shot:
            query = query.filter(avg_scores_subquery.c.avg_shot.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_shot <= max_shot)
        if min_iq:
            query = query.filter(avg_scores_subquery.c.avg_iq.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_iq >= min_iq)
        if max_iq:
            query = query.filter(avg_scores_subquery.c.avg_iq.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_iq <= max_iq)
        if min_compete:
            query = query.filter(avg_scores_subquery.c.avg_compete.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_compete >= min_compete)
        if max_compete:
            query = query.filter(avg_scores_subquery.c.avg_compete.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_compete <= max_compete)
        if min_physical:
            query = query.filter(avg_scores_subquery.c.avg_physical.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_physical >= min_physical)
        if max_physical:
            query = query.filter(avg_scores_subquery.c.avg_physical.isnot(None))
            query = query.filter(avg_scores_subquery.c.avg_physical <= max_physical)

    if q:
        query = query.filter(Player.name.ilike(f"%{q}%"))
    if position:
        query = query.filter(Player.position == position.upper())
    if birth_year_min:
        query = query.filter(Player.birth_year >= birth_year_min)
    if birth_year_max:
        query = query.filter(Player.birth_year <= birth_year_max)
    if shoots:
        query = query.filter(Player.shoots == shoots.upper())
    if min_height:
        query = query.filter(Player.height >= min_height)
    if max_height:
        query = query.filter(Player.height <= max_height)
    if min_weight:
        query = query.filter(Player.weight >= min_weight)
    if max_weight:
        query = query.filter(Player.weight <= max_weight)

    score_stats_subquery = (
        db.query(
            Score.player_id,
            func.avg(Score.overall).label('avg_overall'),
            func.avg(Score.skating).label('avg_skating'),
            func.avg(Score.shot).label('avg_shot'),
            func.avg(Score.iq).label('avg_iq'),
            func.avg(Score.compete).label('avg_compete'),
            func.avg(Score.physical).label('avg_physical')
        )
        .filter(Score.age.between(13, 17))
        .group_by(Score.player_id)
        .subquery()
    )

    stats_query = db.query(
        func.count(Player.id).label('total'),
        func.min(Player.height).label('min_height'),
        func.max(Player.height).label('max_height'),
        func.min(Player.weight).label('min_weight'),
        func.max(Player.weight).label('max_weight'),
        func.min(Player.birth_year).label('min_birth_year'),
        func.max(Player.birth_year).label('max_birth_year'),
        func.min(score_stats_subquery.c.avg_overall).label('min_overall'),
        func.max(score_stats_subquery.c.avg_overall).label('max_overall'),
        func.min(score_stats_subquery.c.avg_skating).label('min_skating'),
        func.max(score_stats_subquery.c.avg_skating).label('max_skating'),
        func.min(score_stats_subquery.c.avg_shot).label('min_shot'),
        func.max(score_stats_subquery.c.avg_shot).label('max_shot'),
        func.min(score_stats_subquery.c.avg_iq).label('min_iq'),
        func.max(score_stats_subquery.c.avg_iq).label('max_iq'),
        func.min(score_stats_subquery.c.avg_compete).label('min_compete'),
        func.max(score_stats_subquery.c.avg_compete).label('max_compete'),
        func.min(score_stats_subquery.c.avg_physical).label('min_physical'),
        func.max(score_stats_subquery.c.avg_physical).label('max_physical')
    ).outerjoin(score_stats_subquery, Player.id == score_stats_subquery.c.player_id)

    # Apply youth score age filters to metadata query
    if youth_score_age is not None:
        score_subquery_meta = (
            db.query(Score.player_id)
            .filter(Score.age == youth_score_age)
        )
        if youth_score_min is not None:
            score_subquery_meta = score_subquery_meta.filter(Score.overall >= youth_score_min)
        if youth_score_max is not None:
            score_subquery_meta = score_subquery_meta.filter(Score.overall <= youth_score_max)
        score_subquery_meta = score_subquery_meta.distinct().subquery()
        stats_query = stats_query.join(score_subquery_meta, Player.id == score_subquery_meta.c.player_id)

    if score_filters_active:
        if min_overall:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_overall.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_overall >= min_overall)
        if max_overall:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_overall.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_overall <= max_overall)
        if min_skating:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_skating.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_skating >= min_skating)
        if max_skating:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_skating.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_skating <= max_skating)
        if min_shot:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_shot.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_shot >= min_shot)
        if max_shot:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_shot.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_shot <= max_shot)
        if min_iq:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_iq.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_iq >= min_iq)
        if max_iq:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_iq.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_iq <= max_iq)
        if min_compete:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_compete.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_compete >= min_compete)
        if max_compete:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_compete.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_compete <= max_compete)
        if min_physical:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_physical.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_physical >= min_physical)
        if max_physical:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_physical.isnot(None))
            stats_query = stats_query.filter(score_stats_subquery.c.avg_physical <= max_physical)

    if q:
        stats_query = stats_query.filter(Player.name.ilike(f"%{q}%"))
    if position:
        stats_query = stats_query.filter(Player.position == position.upper())
    if birth_year_min:
        stats_query = stats_query.filter(Player.birth_year >= birth_year_min)
    if birth_year_max:
        stats_query = stats_query.filter(Player.birth_year <= birth_year_max)
    if shoots:
        stats_query = stats_query.filter(Player.shoots == shoots.upper())
    if min_height:
        stats_query = stats_query.filter(Player.height >= min_height)
    if max_height:
        stats_query = stats_query.filter(Player.height <= max_height)
    if min_weight:
        stats_query = stats_query.filter(Player.weight >= min_weight)
    if max_weight:
        stats_query = stats_query.filter(Player.weight <= max_weight)

    stats = stats_query.first()

    if sort_by == "overall":
        if not score_filters_active:
            avg_overall_subquery = (
                db.query(
                    Score.player_id,
                    func.avg(Score.overall).label('avg_overall')
                )
                .filter(Score.age.between(13, 17))
                .group_by(Score.player_id)
                .subquery()
            )
            query = query.outerjoin(avg_overall_subquery, Player.id == avg_overall_subquery.c.player_id)
            sort_col = avg_overall_subquery.c.avg_overall
        else:
            sort_col = avg_scores_subquery.c.avg_overall

        if sort_direction.lower() == "desc":
            query = query.order_by(sort_col.desc().nullslast())
        else:
            query = query.order_by(sort_col.asc().nullslast())
    else:
        sort_column = getattr(Player, sort_by, Player.name)
        if sort_direction.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    players = query.offset(skip).limit(limit).all()

    return PlayerSearchResponse(
        data=players,
        metadata=PlayerSearchMetadata(
            total=stats.total or 0,
            returned=len(players),
            skip=skip,
            limit=limit,
            min_height=stats.min_height,
            max_height=stats.max_height,
            min_weight=stats.min_weight,
            max_weight=stats.max_weight,
            min_birth_year=stats.min_birth_year,
            max_birth_year=stats.max_birth_year,
            min_overall=stats.min_overall,
            max_overall=stats.max_overall,
            min_skating=stats.min_skating,
            max_skating=stats.max_skating,
            min_shot=stats.min_shot,
            max_shot=stats.max_shot,
            min_iq=stats.min_iq,
            max_iq=stats.max_iq,
            min_compete=stats.min_compete,
            max_compete=stats.max_compete,
            min_physical=stats.min_physical,
            max_physical=stats.max_physical
        )
    )


@router.get("/", response_model=PlayerSearchResponse)
def get_players(
    skip: int = 0,
    limit: int = 100,
    position: str = None,
    name: str = None,
    include_youth_scores: bool = Query(False, description="Include youth scores"),
    youth_score_age: Optional[int] = Query(None, description="Filter by specific youth score age (13-17)"),
    youth_score_min: Optional[Decimal] = Query(None, description="Minimum overall score for the specified age"),
    youth_score_max: Optional[Decimal] = Query(None, description="Maximum overall score for the specified age"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all players with basic pagination and filtering.

    For advanced search with multiple filters, use /search endpoint.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **position**: Filter by position (F, D, G)
    - **name**: Search by name (case-insensitive partial match)
    - **include_youth_scores**: Include youth scores in the response
    - **youth_score_age**: Filter players by scores at specific age (requires include_youth_scores=true)
    - **youth_score_min**: Minimum overall score at the specified age
    - **youth_score_max**: Maximum overall score at the specified age

    **Examples:**
    - `/api/players?include_youth_scores=true&youth_score_age=14` - Players with scores at age 14
    - `/api/players?include_youth_scores=true&youth_score_age=14&youth_score_min=88&youth_score_max=100` - Players with age 14 scores between 88-100
    """
    query = db.query(Player)

    # Load scores if requested
    if include_youth_scores:
        query = query.options(selectinload(Player.scores))

    # Apply youth score age filters to filter which players are returned
    if youth_score_age is not None:
        # Join with Score table to filter by age
        score_subquery = (
            db.query(Score.player_id)
            .filter(Score.age == youth_score_age)
        )

        # Apply min/max filters if provided
        if youth_score_min is not None:
            score_subquery = score_subquery.filter(Score.overall >= youth_score_min)
        if youth_score_max is not None:
            score_subquery = score_subquery.filter(Score.overall <= youth_score_max)

        score_subquery = score_subquery.distinct().subquery()
        query = query.join(score_subquery, Player.id == score_subquery.c.player_id)

    # Apply basic filters
    if position:
        query = query.filter(Player.position == position)
    if name:
        query = query.filter(Player.name.ilike(f"%{name}%"))

    # Build metadata query (without pagination, to get total count and stats)
    metadata_query = db.query(Player)

    # Apply the same filters to metadata query
    if youth_score_age is not None:
        score_subquery_meta = (
            db.query(Score.player_id)
            .filter(Score.age == youth_score_age)
        )
        if youth_score_min is not None:
            score_subquery_meta = score_subquery_meta.filter(Score.overall >= youth_score_min)
        if youth_score_max is not None:
            score_subquery_meta = score_subquery_meta.filter(Score.overall <= youth_score_max)
        score_subquery_meta = score_subquery_meta.distinct().subquery()
        metadata_query = metadata_query.join(score_subquery_meta, Player.id == score_subquery_meta.c.player_id)

    if position:
        metadata_query = metadata_query.filter(Player.position == position)
    if name:
        metadata_query = metadata_query.filter(Player.name.ilike(f"%{name}%"))

    # Calculate metadata stats
    stats = metadata_query.with_entities(
        func.count(Player.id).label('total'),
        func.min(Player.height).label('min_height'),
        func.max(Player.height).label('max_height'),
        func.min(Player.weight).label('min_weight'),
        func.max(Player.weight).label('max_weight'),
        func.min(Player.birth_year).label('min_birth_year'),
        func.max(Player.birth_year).label('max_birth_year')
    ).first()

    # Get paginated results
    query = query.order_by(Player.name)
    players = query.offset(skip).limit(limit).all()

    return PlayerSearchResponse(
        data=players,
        metadata=PlayerSearchMetadata(
            total=stats.total or 0,
            returned=len(players),
            skip=skip,
            limit=limit,
            min_height=stats.min_height,
            max_height=stats.max_height,
            min_weight=stats.min_weight,
            max_weight=stats.max_weight,
            min_birth_year=stats.min_birth_year,
            max_birth_year=stats.max_birth_year,
            min_overall=None,
            max_overall=None,
            min_skating=None,
            max_skating=None,
            min_shot=None,
            max_shot=None,
            min_iq=None,
            max_iq=None,
            min_compete=None,
            max_compete=None,
            min_physical=None,
            max_physical=None
        )
    )


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific player by ID.
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id {player_id} not found"
        )
    return player


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """
    Create a new player.
    """
    db_player = Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: UUID, player: PlayerUpdate, db: Session = Depends(get_db)):
    """
    Update an existing player.
    """
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id {player_id} not found"
        )

    update_data = player.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_player, field, value)

    db.commit()
    db.refresh(db_player)
    return db_player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a player.
    """
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with id {player_id} not found"
        )

    db.delete(db_player)
    db.commit()
    return None


@router.get("/{player_id}/profile", response_model=PlayerProfileResponse)
def get_player_profile(
    player_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Comprehensive player profile endpoint - returns all player data in one call.

    Steps:
    1. Fetch player details by ID, raise 404 if not found
    2. Query all player seasons with eager-loaded relationships (season, league, team, stats)
    3. Transform seasons into response format
    4. Query youth development scores (ages 13-17) ordered by age
    5. Transform scores into response format
    6. Query draft probability data ordered by probability
    7. Transform drafts into response format
    8. If player has seasons, fetch historical snapshots for most recent season:
       - For goalies: query goalie_season_stats_history
       - For skaters: query player_season_stats_history
    9. Return complete profile with details, seasons, stats, snapshots, probabilities
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")

    player_seasons = (
        db.query(PlayerSeason)
        .options(
            joinedload(PlayerSeason.season),
            joinedload(PlayerSeason.league),
            joinedload(PlayerSeason.team),
            joinedload(PlayerSeason.player_stats),
            joinedload(PlayerSeason.goalie_stats)
        )
        .filter(PlayerSeason.player_id == player_id)
        .join(Season)
        .order_by(Season.start_year.desc(), Season.end_year.desc())
        .all()
    )

    seasons_data = [
        PlayerSeasonResponse(
            season=ps.season.label if ps.season else "Unknown",
            league=ps.league.name if ps.league else "Unknown",
            league_code=ps.league.code if ps.league else "",
            team=ps.team.name if ps.team else None,
            team_code=ps.team.code if ps.team else None,
            split=ps.split,
            age=ps.age,
            level=ps.level,
            competition_strength=ps.competition_strength,
            stats=SeasonStatsDetail.model_validate(ps.player_stats) if ps.player_stats else None,
            goalie_stats=GoalieSeasonStatsDetail.model_validate(ps.goalie_stats) if ps.goalie_stats else None
        )
        for ps in player_seasons
    ]

    scores = (
        db.query(Score)
        .options(joinedload(Score.season))
        .filter(Score.player_id == player_id, Score.age.between(13, 17))
        .order_by(Score.age.asc())
        .all()
    )

    youth_scores_data = [
        YouthScoreDetail(
            age=score.age,
            season=score.season.label if score.season else None,
            overall=score.overall,
            prospect=score.prospect,
            skating=score.skating,
            shot=score.shot,
            iq=score.iq,
            compete=score.compete,
            physical=score.physical,
            projection_note=score.projection_note
        )
        for score in scores
    ]

    drafts = (
        db.query(Draft)
        .options(joinedload(Draft.season))
        .filter(Draft.player_id == player_id)
        .order_by(Draft.probability.desc())
        .all()
    )

    drafts_data = [
        DraftProbabilityDetail(
            draft_league=draft.draft_league,
            season=draft.season.label if draft.season else None,
            probability=draft.probability,
            round_estimate=draft.round_estimate,
            team_hints=draft.team_hints
        )
        for draft in drafts
    ]

    snapshots = None
    if player_seasons:
        most_recent_season = player_seasons[0]

        if player.position == 'G':
            query = text("""
                SELECT snapshot_date, gp, gs, w, l, otl, so, ga, sa, sv, toi_min, gaa, sv_pct
                FROM dekedata.goalie_season_stats_history
                WHERE player_season_id = :player_season_id
                ORDER BY snapshot_date ASC
            """)
            rows = db.execute(query, {"player_season_id": most_recent_season.id}).fetchall()
            goalie_snapshots = [
                GoalieSeasonProgressSnapshot(
                    date=row[0].isoformat(),
                    gp=row[1] or 0,
                    gs=row[2],
                    w=row[3],
                    l=row[4],
                    otl=row[5],
                    so=row[6],
                    ga=row[7],
                    sa=row[8],
                    sv=row[9],
                    toi_min=row[10],
                    gaa=row[11],
                    sv_pct=row[12]
                )
                for row in rows
            ]
            snapshots = PlayerSeasonProgressResponse(snapshots=[], goalie_snapshots=goalie_snapshots)
        else:
            query = text("""
                SELECT snapshot_date, gp, g, a, pts, pim, plus_minus, sog, hits, blocks, pp_g, sh_g
                FROM dekedata.player_season_stats_history
                WHERE player_season_id = :player_season_id
                ORDER BY snapshot_date ASC
            """)
            rows = db.execute(query, {"player_season_id": most_recent_season.id}).fetchall()
            skater_snapshots = [
                SeasonProgressSnapshot(
                    date=row[0].isoformat(),
                    gp=row[1] or 0,
                    g=row[2] or 0,
                    a=row[3] or 0,
                    pts=row[4] or 0,
                    pim=row[5],
                    plus_minus=row[6],
                    sog=row[7],
                    hits=row[8],
                    blocks=row[9],
                    pp_g=row[10],
                    sh_g=row[11]
                )
                for row in rows
            ]
            snapshots = PlayerSeasonProgressResponse(snapshots=skater_snapshots, goalie_snapshots=[])

    return PlayerProfileResponse(
        details=PlayerDetails(
            player_id=str(player.id),
            name=player.name,
            position=player.position,
            birth_year=player.birth_year,
            shoots=player.shoots,
            height=player.height,
            weight=player.weight,
            photo_url=player.photo_url
        ),
        seasons=seasons_data,
        stats=youth_scores_data,
        snapshots=snapshots,
        probabilities=drafts_data
    )


@router.get("/{player_id}/seasons", response_model=PlayerSeasonsResponse)
def get_player_seasons(
    player_id: UUID,
    season_id: Optional[UUID] = Query(None),
    league_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns all season-by-season statistics for a player.

    Steps:
    1. Query player seasons with eager-loaded relationships
    2. Apply optional filters for season_id and league_id
    3. Order by most recent season first
    4. Transform to response format with stats
    5. Return seasons list
    """
    query = (
        db.query(PlayerSeason)
        .options(
            joinedload(PlayerSeason.season),
            joinedload(PlayerSeason.league),
            joinedload(PlayerSeason.team),
            joinedload(PlayerSeason.player_stats),
            joinedload(PlayerSeason.goalie_stats)
        )
        .filter(PlayerSeason.player_id == player_id)
    )

    if season_id:
        query = query.filter(PlayerSeason.season_id == season_id)
    if league_id:
        query = query.filter(PlayerSeason.league_id == league_id)

    player_seasons = query.join(Season).order_by(Season.start_year.desc(), Season.end_year.desc()).all()

    seasons_data = [
        PlayerSeasonResponse(
            season=ps.season.label if ps.season else "Unknown",
            league=ps.league.name if ps.league else "Unknown",
            league_code=ps.league.code if ps.league else "",
            team=ps.team.name if ps.team else None,
            team_code=ps.team.code if ps.team else None,
            split=ps.split,
            age=ps.age,
            level=ps.level,
            competition_strength=ps.competition_strength,
            stats=SeasonStatsDetail.model_validate(ps.player_stats) if ps.player_stats else None,
            goalie_stats=GoalieSeasonStatsDetail.model_validate(ps.goalie_stats) if ps.goalie_stats else None
        )
        for ps in player_seasons
    ]

    return PlayerSeasonsResponse(seasons=seasons_data)


@router.get("/{player_id}/youth-scores", response_model=PlayerYouthScoresResponse)
def get_player_youth_scores(player_id: UUID, db: Session = Depends(get_db)):
    """
    Returns youth development scores for ages 13-17.

    Steps:
    1. Query scores table filtered by player_id and age range (13-17)
    2. Eager-load season relationships
    3. Order by age ascending
    4. Transform to response format with all score attributes
    5. Return youth scores list
    """
    scores = (
        db.query(Score)
        .options(joinedload(Score.season))
        .filter(Score.player_id == player_id, Score.age.between(13, 17))
        .order_by(Score.age.asc())
        .all()
    )

    youth_scores_data = [
        YouthScoreDetail(
            age=score.age,
            season=score.season.label if score.season else None,
            overall=score.overall,
            prospect=score.prospect,
            skating=score.skating,
            shot=score.shot,
            iq=score.iq,
            compete=score.compete,
            physical=score.physical,
            projection_note=score.projection_note
        )
        for score in scores
    ]

    return PlayerYouthScoresResponse(youth_scores=youth_scores_data)


@router.get("/{player_id}/probabilities", response_model=PlayerDraftResponse)
def get_player_probabilities(player_id: UUID, db: Session = Depends(get_db)):
    """
    Returns draft probability data for a player.

    Steps:
    1. Query draft table filtered by player_id
    2. Eager-load season relationships
    3. Order by probability descending (highest probability first)
    4. Transform to response format with league, probability, round, team hints
    5. Return draft probabilities list
    """
    drafts = (
        db.query(Draft)
        .options(joinedload(Draft.season))
        .filter(Draft.player_id == player_id)
        .order_by(Draft.probability.desc())
        .all()
    )

    drafts_data = [
        DraftProbabilityDetail(
            draft_league=draft.draft_league,
            season=draft.season.label if draft.season else None,
            probability=draft.probability,
            round_estimate=draft.round_estimate,
            team_hints=draft.team_hints
        )
        for draft in drafts
    ]

    return PlayerDraftResponse(drafts=drafts_data)


@router.get("/{player_id}/season-progress", response_model=PlayerSeasonProgressResponse)
def get_player_season_progress(
    player_id: UUID,
    player_season_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """
    Returns daily snapshots of cumulative season stats for a specific player season.

    Steps:
    1. Validate player exists, raise 404 if not found
    2. Validate player_season exists, raise 404 if not found
    3. Check if player is goalie (position == 'G')
    4. If goalie: query goalie_season_stats_history table
    5. If skater: query player_season_stats_history table
    6. Transform raw SQL rows to snapshot objects
    7. Return snapshots ordered chronologically
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")

    player_season = db.query(PlayerSeason).filter(PlayerSeason.id == player_season_id).first()
    if not player_season:
        raise HTTPException(status_code=404, detail=f"Player season with id {player_season_id} not found")

    if player.position == 'G':
        query = text("""
            SELECT snapshot_date, gp, gs, w, l, otl, so, ga, sa, sv, toi_min, gaa, sv_pct
            FROM dekedata.goalie_season_stats_history
            WHERE player_season_id = :player_season_id
            ORDER BY snapshot_date ASC
        """)
        rows = db.execute(query, {"player_season_id": player_season_id}).fetchall()
        goalie_snapshots = [
            GoalieSeasonProgressSnapshot(
                date=row[0].isoformat(),
                gp=row[1] or 0,
                gs=row[2],
                w=row[3],
                l=row[4],
                otl=row[5],
                so=row[6],
                ga=row[7],
                sa=row[8],
                sv=row[9],
                toi_min=row[10],
                gaa=row[11],
                sv_pct=row[12]
            )
            for row in rows
        ]
        return PlayerSeasonProgressResponse(snapshots=[], goalie_snapshots=goalie_snapshots)
    else:
        query = text("""
            SELECT snapshot_date, gp, g, a, pts, pim, plus_minus, sog, hits, blocks, pp_g, sh_g
            FROM dekedata.player_season_stats_history
            WHERE player_season_id = :player_season_id
            ORDER BY snapshot_date ASC
        """)
        rows = db.execute(query, {"player_season_id": player_season_id}).fetchall()
        skater_snapshots = [
            SeasonProgressSnapshot(
                date=row[0].isoformat(),
                gp=row[1] or 0,
                g=row[2] or 0,
                a=row[3] or 0,
                pts=row[4] or 0,
                pim=row[5],
                plus_minus=row[6],
                sog=row[7],
                hits=row[8],
                blocks=row[9],
                pp_g=row[10],
                sh_g=row[11]
            )
            for row in rows
        ]
        return PlayerSeasonProgressResponse(snapshots=skater_snapshots, goalie_snapshots=[])
