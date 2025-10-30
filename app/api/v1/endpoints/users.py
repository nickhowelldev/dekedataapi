from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.base import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all users with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    result = db.execute(
        text("SELECT * FROM users WHERE deleted_at IS NULL ORDER BY id LIMIT :limit OFFSET :skip"),
        {"limit": limit, "skip": skip}
    )
    users = result.mappings().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific user by ID.
    """
    result = db.execute(
        text("SELECT * FROM users WHERE id = :user_id AND deleted_at IS NULL"),
        {"user_id": user_id}
    )
    user = result.mappings().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Note: In production, you should hash the password before storing it.
    """
    # Check if email already exists
    existing = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": user.email}
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # In production, hash the password using bcrypt or similar
    result = db.execute(
        text("""
            INSERT INTO users (email, name, password_hash, role)
            VALUES (:email, :name, :password_hash, :role)
            RETURNING *
        """),
        {
            "email": user.email,
            "name": user.name,
            "password_hash": user.password,  # TODO: Hash this in production
            "role": user.role
        }
    )
    db.commit()

    new_user = result.mappings().first()
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Update an existing user.
    """
    # Check if user exists
    existing = db.execute(
        text("SELECT * FROM users WHERE id = :user_id AND deleted_at IS NULL"),
        {"user_id": user_id}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Build dynamic update query
    update_data = user.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    set_clauses = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
    query = f"UPDATE users SET {set_clauses}, updated_at = NOW() WHERE id = :user_id RETURNING *"

    update_data["user_id"] = user_id
    result = db.execute(text(query), update_data)
    db.commit()

    updated_user = result.mappings().first()
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a user (sets deleted_at timestamp).
    """
    result = db.execute(
        text("""
            UPDATE users
            SET deleted_at = NOW()
            WHERE id = :user_id AND deleted_at IS NULL
            RETURNING id
        """),
        {"user_id": user_id}
    )
    db.commit()

    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return None
