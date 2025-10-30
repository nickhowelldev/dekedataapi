from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.score import ScoreCreate, ScoreUpdate, ScoreResponse
from app.models.score import Score

router = APIRouter()


@router.get("/", response_model=List[ScoreResponse])
def get_scores(
    skip: int = 0,
    limit: int = 100,
    player_id: UUID = None,
    season_id: UUID = None,
    min_overall: float = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all scores with pagination and optional filtering.

    - **player_id**: Filter by player
    - **season_id**: Filter by season
    - **min_overall**: Filter by minimum overall score
    """
    query = db.query(Score)
    if player_id:
        query = query.filter(Score.player_id == player_id)
    if season_id:
        query = query.filter(Score.season_id == season_id)
    if min_overall is not None:
        query = query.filter(Score.overall >= min_overall)
    scores = query.offset(skip).limit(limit).all()
    return scores


@router.get("/{score_id}", response_model=ScoreResponse)
def get_score(score_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific score by ID.
    """
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with id {score_id} not found"
        )
    return score


@router.post("/", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(score: ScoreCreate, db: Session = Depends(get_db)):
    """
    Create a new score.
    """
    # Check for duplicate
    existing = db.query(Score).filter(
        Score.player_id == score.player_id,
        Score.season_id == score.season_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score for this player and season already exists"
        )

    db_score = Score(**score.model_dump())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.put("/{score_id}", response_model=ScoreResponse)
def update_score(score_id: UUID, score: ScoreUpdate, db: Session = Depends(get_db)):
    """
    Update an existing score.
    """
    db_score = db.query(Score).filter(Score.id == score_id).first()
    if not db_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with id {score_id} not found"
        )

    update_data = score.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_score, field, value)

    db.commit()
    db.refresh(db_score)
    return db_score


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_score(score_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a score.
    """
    db_score = db.query(Score).filter(Score.id == score_id).first()
    if not db_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with id {score_id} not found"
        )

    db.delete(db_score)
    db.commit()
    return None
