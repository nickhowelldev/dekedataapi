from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.draft import DraftCreate, DraftUpdate, DraftResponse
from app.models.draft import Draft

router = APIRouter()


@router.get("/", response_model=List[DraftResponse])
def get_drafts(
    skip: int = 0,
    limit: int = 100,
    player_id: UUID = None,
    draft_league: str = None,
    min_probability: float = None,
    season_id: UUID = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all draft probabilities with pagination and optional filtering.

    - **player_id**: Filter by player
    - **draft_league**: Filter by draft league (e.g., 'NHL', 'WHL')
    - **min_probability**: Filter by minimum probability
    - **season_id**: Filter by season
    """
    query = db.query(Draft)
    if player_id:
        query = query.filter(Draft.player_id == player_id)
    if draft_league:
        query = query.filter(Draft.draft_league == draft_league)
    if min_probability is not None:
        query = query.filter(Draft.probability >= min_probability)
    if season_id:
        query = query.filter(Draft.season_id == season_id)

    # Order by probability descending by default
    query = query.order_by(Draft.probability.desc())

    drafts = query.offset(skip).limit(limit).all()
    return drafts


@router.get("/{draft_id}", response_model=DraftResponse)
def get_draft(draft_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific draft by ID.
    """
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft with id {draft_id} not found"
        )
    return draft


@router.post("/", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def create_draft(draft: DraftCreate, db: Session = Depends(get_db)):
    """
    Create a new draft probability.
    """
    # Check for duplicate
    existing = db.query(Draft).filter(
        Draft.player_id == draft.player_id,
        Draft.season_id == draft.season_id,
        Draft.draft_league == draft.draft_league
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft entry for this player, season, and league already exists"
        )

    db_draft = Draft(**draft.model_dump())
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


@router.put("/{draft_id}", response_model=DraftResponse)
def update_draft(draft_id: UUID, draft: DraftUpdate, db: Session = Depends(get_db)):
    """
    Update an existing draft probability.
    """
    db_draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not db_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft with id {draft_id} not found"
        )

    update_data = draft.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_draft, field, value)

    db.commit()
    db.refresh(db_draft)
    return db_draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft(draft_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a draft probability.
    """
    db_draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not db_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft with id {draft_id} not found"
        )

    db.delete(db_draft)
    db.commit()
    return None
