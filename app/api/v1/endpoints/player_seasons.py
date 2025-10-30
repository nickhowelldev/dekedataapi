from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.player_season import PlayerSeasonCreate, PlayerSeasonUpdate, PlayerSeasonResponse
from app.models.player_season import PlayerSeason

router = APIRouter()


@router.get("/", response_model=List[PlayerSeasonResponse])
def get_player_seasons(
    skip: int = 0,
    limit: int = 100,
    player_id: UUID = None,
    season_id: UUID = None,
    league_id: UUID = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all player seasons with pagination and optional filtering.
    """
    query = db.query(PlayerSeason)
    if player_id:
        query = query.filter(PlayerSeason.player_id == player_id)
    if season_id:
        query = query.filter(PlayerSeason.season_id == season_id)
    if league_id:
        query = query.filter(PlayerSeason.league_id == league_id)
    player_seasons = query.offset(skip).limit(limit).all()
    return player_seasons


@router.get("/{player_season_id}", response_model=PlayerSeasonResponse)
def get_player_season(player_season_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific player season by ID.
    """
    player_season = db.query(PlayerSeason).filter(PlayerSeason.id == player_season_id).first()
    if not player_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player season with id {player_season_id} not found"
        )
    return player_season


@router.post("/", response_model=PlayerSeasonResponse, status_code=status.HTTP_201_CREATED)
def create_player_season(player_season: PlayerSeasonCreate, db: Session = Depends(get_db)):
    """
    Create a new player season.
    """
    # Check for duplicate
    existing = db.query(PlayerSeason).filter(
        PlayerSeason.player_id == player_season.player_id,
        PlayerSeason.season_id == player_season.season_id,
        PlayerSeason.league_id == player_season.league_id,
        PlayerSeason.split == player_season.split
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player season with this combination already exists"
        )

    db_player_season = PlayerSeason(**player_season.model_dump())
    db.add(db_player_season)
    db.commit()
    db.refresh(db_player_season)
    return db_player_season


@router.put("/{player_season_id}", response_model=PlayerSeasonResponse)
def update_player_season(player_season_id: UUID, player_season: PlayerSeasonUpdate, db: Session = Depends(get_db)):
    """
    Update an existing player season.
    """
    db_player_season = db.query(PlayerSeason).filter(PlayerSeason.id == player_season_id).first()
    if not db_player_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player season with id {player_season_id} not found"
        )

    update_data = player_season.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_player_season, field, value)

    db.commit()
    db.refresh(db_player_season)
    return db_player_season


@router.delete("/{player_season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player_season(player_season_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a player season.
    """
    db_player_season = db.query(PlayerSeason).filter(PlayerSeason.id == player_season_id).first()
    if not db_player_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player season with id {player_season_id} not found"
        )

    db.delete(db_player_season)
    db.commit()
    return None
