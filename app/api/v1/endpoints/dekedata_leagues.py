from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.dekedata_league import LeagueCreate, LeagueUpdate, LeagueResponse
from app.models.league import League

router = APIRouter()


@router.get("/", response_model=List[LeagueResponse])
def get_leagues(
    skip: int = 0,
    limit: int = 100,
    tier: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all leagues with pagination and optional filtering.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **tier**: Filter by tier (optional)
    """
    query = db.query(League)
    if tier:
        query = query.filter(League.tier == tier)
    leagues = query.offset(skip).limit(limit).all()
    return leagues


@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(league_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific league by ID.
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found"
        )
    return league


@router.post("/", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
def create_league(league: LeagueCreate, db: Session = Depends(get_db)):
    """
    Create a new league.
    """
    # Check if code already exists
    existing = db.query(League).filter(League.code == league.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with code '{league.code}' already exists"
        )

    db_league = League(**league.model_dump())
    db.add(db_league)
    db.commit()
    db.refresh(db_league)
    return db_league


@router.put("/{league_id}", response_model=LeagueResponse)
def update_league(league_id: UUID, league: LeagueUpdate, db: Session = Depends(get_db)):
    """
    Update an existing league.
    """
    db_league = db.query(League).filter(League.id == league_id).first()
    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found"
        )

    update_data = league.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_league, field, value)

    db.commit()
    db.refresh(db_league)
    return db_league


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league(league_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a league.
    """
    db_league = db.query(League).filter(League.id == league_id).first()
    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found"
        )

    db.delete(db_league)
    db.commit()
    return None
