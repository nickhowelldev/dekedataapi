from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.db.base import get_db
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from app.schemas.player_search import PlayerSearchResponse, PlayerSearchMetadata
from app.models.player import Player
from app.models.score import Score

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
    - `/search?sort_by=birth_year&sort_direction=desc` - Sort by birth year newest first
    - `/search?sort_by=height&sort_direction=desc` - Sort by height tallest first
    - `/search?sort_by=overall&sort_direction=desc` - Sort by overall score (youth average) highest first
    - `/search?min_overall=75&max_overall=85` - Players with overall score between 75-85
    - `/search?position=F&min_skating=80&min_shot=80` - Forwards with 80+ skating and shot
    """
    query = db.query(Player)

    if include_youth_scores:
        query = query.options(selectinload(Player.scores))

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
            query = query.filter(avg_scores_subquery.c.avg_overall >= min_overall)
        if max_overall:
            query = query.filter(avg_scores_subquery.c.avg_overall <= max_overall)
        if min_skating:
            query = query.filter(avg_scores_subquery.c.avg_skating >= min_skating)
        if max_skating:
            query = query.filter(avg_scores_subquery.c.avg_skating <= max_skating)
        if min_shot:
            query = query.filter(avg_scores_subquery.c.avg_shot >= min_shot)
        if max_shot:
            query = query.filter(avg_scores_subquery.c.avg_shot <= max_shot)
        if min_iq:
            query = query.filter(avg_scores_subquery.c.avg_iq >= min_iq)
        if max_iq:
            query = query.filter(avg_scores_subquery.c.avg_iq <= max_iq)
        if min_compete:
            query = query.filter(avg_scores_subquery.c.avg_compete >= min_compete)
        if max_compete:
            query = query.filter(avg_scores_subquery.c.avg_compete <= max_compete)
        if min_physical:
            query = query.filter(avg_scores_subquery.c.avg_physical >= min_physical)
        if max_physical:
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

    if score_filters_active:
        if min_overall:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_overall >= min_overall)
        if max_overall:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_overall <= max_overall)
        if min_skating:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_skating >= min_skating)
        if max_skating:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_skating <= max_skating)
        if min_shot:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_shot >= min_shot)
        if max_shot:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_shot <= max_shot)
        if min_iq:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_iq >= min_iq)
        if max_iq:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_iq <= max_iq)
        if min_compete:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_compete >= min_compete)
        if max_compete:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_compete <= max_compete)
        if min_physical:
            stats_query = stats_query.filter(score_stats_subquery.c.avg_physical >= min_physical)
        if max_physical:
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


@router.get("/", response_model=List[PlayerResponse])
def get_players(
    skip: int = 0,
    limit: int = 100,
    position: str = None,
    name: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all players with basic pagination and filtering.

    For advanced search with multiple filters, use /search endpoint.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **position**: Filter by position (F, D, G)
    - **name**: Search by name (case-insensitive partial match)
    """
    query = db.query(Player)
    if position:
        query = query.filter(Player.position == position)
    if name:
        query = query.filter(Player.name.ilike(f"%{name}%"))

    query = query.order_by(Player.name)
    players = query.offset(skip).limit(limit).all()
    return players


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
