from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.base import get_db
from app.schemas.league import LeagueCreate, LeagueUpdate, LeagueResponse

router = APIRouter()


@router.get("/", response_model=List[LeagueResponse])
def get_leagues(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieve all leagues with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **active_only**: Only return active leagues (default: False)
    """
    query = "SELECT * FROM leagues"
    if active_only:
        query += " WHERE active = true"
    query += " ORDER BY id LIMIT :limit OFFSET :skip"

    result = db.execute(text(query), {"limit": limit, "skip": skip})
    leagues = result.mappings().all()
    return leagues


@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(league_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific league by ID.
    """
    result = db.execute(
        text("SELECT * FROM leagues WHERE id = :league_id"),
        {"league_id": league_id}
    )
    league = result.mappings().first()

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
    # Check if value already exists
    existing = db.execute(
        text("SELECT id FROM leagues WHERE value = :value"),
        {"value": league.value}
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with value '{league.value}' already exists"
        )

    result = db.execute(
        text("""
            INSERT INTO leagues (value, label, active, league_status, hub_status)
            VALUES (:value, :label, :active, :league_status, :hub_status)
            RETURNING *
        """),
        {
            "value": league.value,
            "label": league.label,
            "active": league.active,
            "league_status": league.league_status,
            "hub_status": league.hub_status
        }
    )
    db.commit()

    new_league = result.mappings().first()
    return new_league


@router.put("/{league_id}", response_model=LeagueResponse)
def update_league(league_id: int, league: LeagueUpdate, db: Session = Depends(get_db)):
    """
    Update an existing league.
    """
    # Check if league exists
    existing = db.execute(
        text("SELECT * FROM leagues WHERE id = :league_id"),
        {"league_id": league_id}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found"
        )

    # Build dynamic update query
    update_data = league.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    set_clauses = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
    query = f"UPDATE leagues SET {set_clauses}, updated_at = NOW() WHERE id = :league_id RETURNING *"

    update_data["league_id"] = league_id
    result = db.execute(text(query), update_data)
    db.commit()

    updated_league = result.mappings().first()
    return updated_league


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league(league_id: int, db: Session = Depends(get_db)):
    """
    Delete a league.
    """
    result = db.execute(
        text("DELETE FROM leagues WHERE id = :league_id RETURNING id"),
        {"league_id": league_id}
    )
    db.commit()

    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found"
        )

    return None
