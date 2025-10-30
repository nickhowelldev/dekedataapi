from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.models.team import Team

router = APIRouter()


@router.get("/", response_model=List[TeamResponse])
def get_teams(
    skip: int = 0,
    limit: int = 100,
    league_id: UUID = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all teams with pagination and optional filtering.
    """
    query = db.query(Team)
    if league_id:
        query = query.filter(Team.league_id == league_id)
    teams = query.offset(skip).limit(limit).all()
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific team by ID.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found"
        )
    return team


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """
    Create a new team.
    """
    db_team = Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team_id: UUID, team: TeamUpdate, db: Session = Depends(get_db)):
    """
    Update an existing team.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found"
        )

    update_data = team.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_team, field, value)

    db.commit()
    db.refresh(db_team)
    return db_team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a team.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found"
        )

    db.delete(db_team)
    db.commit()
    return None
