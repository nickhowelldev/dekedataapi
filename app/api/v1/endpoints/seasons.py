from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.season import SeasonCreate, SeasonUpdate, SeasonResponse
from app.models.season import Season

router = APIRouter()


@router.get("/", response_model=List[SeasonResponse])
def get_seasons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all seasons with pagination.
    """
    seasons = db.query(Season).offset(skip).limit(limit).all()
    return seasons


@router.get("/{season_id}", response_model=SeasonResponse)
def get_season(season_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific season by ID.
    """
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with id {season_id} not found"
        )
    return season


@router.post("/", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
def create_season(season: SeasonCreate, db: Session = Depends(get_db)):
    """
    Create a new season.
    """
    # Check if label already exists
    existing = db.query(Season).filter(Season.label == season.label).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Season with label '{season.label}' already exists"
        )

    db_season = Season(**season.model_dump())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season


@router.put("/{season_id}", response_model=SeasonResponse)
def update_season(season_id: UUID, season: SeasonUpdate, db: Session = Depends(get_db)):
    """
    Update an existing season.
    """
    db_season = db.query(Season).filter(Season.id == season_id).first()
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with id {season_id} not found"
        )

    update_data = season.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_season, field, value)

    db.commit()
    db.refresh(db_season)
    return db_season


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season(season_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a season.
    """
    db_season = db.query(Season).filter(Season.id == season_id).first()
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with id {season_id} not found"
        )

    db.delete(db_season)
    db.commit()
    return None
