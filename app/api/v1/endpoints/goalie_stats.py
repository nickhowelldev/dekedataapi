from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.goalie_stats import GoalieStatsCreate, GoalieStatsUpdate, GoalieStatsResponse
from app.models.goalie_stats import GoalieStats

router = APIRouter()


@router.get("/", response_model=List[GoalieStatsResponse])
def get_goalie_stats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all goalie stats with pagination.
    """
    stats = db.query(GoalieStats).offset(skip).limit(limit).all()
    return stats


@router.get("/{player_season_id}", response_model=GoalieStatsResponse)
def get_goalie_stat(player_season_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve specific goalie stats by player_season_id.
    """
    stats = db.query(GoalieStats).filter(GoalieStats.player_season_id == player_season_id).first()
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goalie stats for player_season_id {player_season_id} not found"
        )
    return stats


@router.post("/", response_model=GoalieStatsResponse, status_code=status.HTTP_201_CREATED)
def create_goalie_stats(stats: GoalieStatsCreate, db: Session = Depends(get_db)):
    """
    Create new goalie stats.

    Note: This will fail if the player's position is not 'G' (goalie) due to database triggers.
    """
    # Check if stats already exist
    existing = db.query(GoalieStats).filter(
        GoalieStats.player_season_id == stats.player_season_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goalie stats for this player_season_id already exist"
        )

    try:
        db_stats = GoalieStats(**stats.model_dump())
        db.add(db_stats)
        db.commit()
        db.refresh(db_stats)
        return db_stats
    except Exception as e:
        db.rollback()
        if "Only goalies can have goalie_stats" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create goalie stats for a non-goalie"
            )
        raise


@router.put("/{player_season_id}", response_model=GoalieStatsResponse)
def update_goalie_stats(player_season_id: UUID, stats: GoalieStatsUpdate, db: Session = Depends(get_db)):
    """
    Update existing goalie stats.
    """
    db_stats = db.query(GoalieStats).filter(GoalieStats.player_season_id == player_season_id).first()
    if not db_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goalie stats for player_season_id {player_season_id} not found"
        )

    update_data = stats.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stats, field, value)

    db.commit()
    db.refresh(db_stats)
    return db_stats


@router.delete("/{player_season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goalie_stats(player_season_id: UUID, db: Session = Depends(get_db)):
    """
    Delete goalie stats.
    """
    db_stats = db.query(GoalieStats).filter(GoalieStats.player_season_id == player_season_id).first()
    if not db_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goalie stats for player_season_id {player_season_id} not found"
        )

    db.delete(db_stats)
    db.commit()
    return None
