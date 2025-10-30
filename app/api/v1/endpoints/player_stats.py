from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.player_stats import PlayerStatsCreate, PlayerStatsUpdate, PlayerStatsResponse
from app.models.player_stats import PlayerStats

router = APIRouter()


@router.get("/", response_model=List[PlayerStatsResponse])
def get_player_stats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all player stats (skaters only) with pagination.
    """
    stats = db.query(PlayerStats).offset(skip).limit(limit).all()
    return stats


@router.get("/{player_season_id}", response_model=PlayerStatsResponse)
def get_player_stat(player_season_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve specific player stats by player_season_id.
    """
    stats = db.query(PlayerStats).filter(PlayerStats.player_season_id == player_season_id).first()
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player stats for player_season_id {player_season_id} not found"
        )
    return stats


@router.post("/", response_model=PlayerStatsResponse, status_code=status.HTTP_201_CREATED)
def create_player_stats(stats: PlayerStatsCreate, db: Session = Depends(get_db)):
    """
    Create new player stats for a skater.

    Note: This will fail if the player's position is 'G' (goalie) due to database triggers.
    """
    # Check if stats already exist
    existing = db.query(PlayerStats).filter(
        PlayerStats.player_season_id == stats.player_season_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player stats for this player_season_id already exist"
        )

    try:
        db_stats = PlayerStats(**stats.model_dump())
        db.add(db_stats)
        db.commit()
        db.refresh(db_stats)
        return db_stats
    except Exception as e:
        db.rollback()
        if "Goalies cannot have player_stats" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create skater stats for a goalie"
            )
        raise


@router.put("/{player_season_id}", response_model=PlayerStatsResponse)
def update_player_stats(player_season_id: UUID, stats: PlayerStatsUpdate, db: Session = Depends(get_db)):
    """
    Update existing player stats.
    """
    db_stats = db.query(PlayerStats).filter(PlayerStats.player_season_id == player_season_id).first()
    if not db_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player stats for player_season_id {player_season_id} not found"
        )

    update_data = stats.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stats, field, value)

    db.commit()
    db.refresh(db_stats)
    return db_stats


@router.delete("/{player_season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player_stats(player_season_id: UUID, db: Session = Depends(get_db)):
    """
    Delete player stats.
    """
    db_stats = db.query(PlayerStats).filter(PlayerStats.player_season_id == player_season_id).first()
    if not db_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player stats for player_season_id {player_season_id} not found"
        )

    db.delete(db_stats)
    db.commit()
    return None
