from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.player_list import (
    PlayerListCreate,
    PlayerListUpdate,
    PlayerListResponse,
    AddPlayerRequest,
    BulkAddPlayerRequest,
    DeleteListResponse
)

router = APIRouter()


@router.get("/", response_model=List[PlayerListResponse])
def get_all_lists(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get all lists for a specific user.

    Returns all player lists belonging to the specified user,
    ordered by creation date (newest first).

    If the user has no lists, automatically creates a default "My Favorites" list.

    - **user_id**: The ID of the user whose lists to retrieve
    """
    result = db.execute(
        text("""
            SELECT id, user_id, name, description, player_ids, is_default, created_at, updated_at
            FROM player_lists
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """),
        {"user_id": user_id}
    )
    lists = result.mappings().all()

    if not lists:
        default_list_result = db.execute(
            text("""
                INSERT INTO player_lists (user_id, name, description, player_ids, is_default)
                VALUES (:user_id, :name, :description, :player_ids, :is_default)
                RETURNING id, user_id, name, description, player_ids, is_default, created_at, updated_at
            """),
            {
                "user_id": user_id,
                "name": "My Favorites",
                "description": "Your favorite players",
                "player_ids": [],
                "is_default": True
            }
        )
        db.commit()
        new_list = default_list_result.mappings().first()
        lists = [new_list]

    return lists


@router.get("/{list_id}", response_model=PlayerListResponse)
def get_list(
    list_id: UUID,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get single list by ID.

    Returns a specific player list if it belongs to the specified user.
    Raises 404 if the list doesn't exist or doesn't belong to the user.

    - **list_id**: The ID of the list to retrieve
    - **user_id**: The ID of the user who owns the list
    """
    result = db.execute(
        text("""
            SELECT id, user_id, name, description, player_ids, is_default, created_at, updated_at
            FROM player_lists
            WHERE id = :list_id AND user_id = :user_id
        """),
        {"list_id": list_id, "user_id": user_id}
    )
    player_list = result.mappings().first()

    if not player_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with id {list_id} not found"
        )

    return player_list


@router.post("/", response_model=PlayerListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: PlayerListCreate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Create new list.

    Creates a new player list for the specified user with the specified
    name and optional description. The list starts with an empty player_ids array.

    - **list_data**: The list name and optional description
    - **user_id**: The ID of the user who will own the list
    """
    result = db.execute(
        text("""
            INSERT INTO player_lists (user_id, name, description, player_ids, is_default)
            VALUES (:user_id, :name, :description, :player_ids, :is_default)
            RETURNING id, user_id, name, description, player_ids, is_default, created_at, updated_at
        """),
        {
            "user_id": user_id,
            "name": list_data.name,
            "description": list_data.description,
            "player_ids": [],
            "is_default": False
        }
    )
    db.commit()

    new_list = result.mappings().first()
    return new_list


@router.patch("/{list_id}", response_model=PlayerListResponse)
def update_list(
    list_id: UUID,
    list_data: PlayerListUpdate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Update list name/description.

    Updates the name and/or description of a player list.
    Only the fields provided in the request will be updated.
    Raises 404 if the list doesn't exist or doesn't belong to the user.

    - **list_id**: The ID of the list to update
    - **list_data**: The fields to update (name and/or description)
    - **user_id**: The ID of the user who owns the list
    """
    existing = db.execute(
        text("""
            SELECT id, user_id, name, description, player_ids, is_default, created_at, updated_at
            FROM player_lists
            WHERE id = :list_id AND user_id = :user_id
        """),
        {"list_id": list_id, "user_id": user_id}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with id {list_id} not found"
        )

    update_data = list_data.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    set_clauses = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
    query = f"UPDATE player_lists SET {set_clauses}, updated_at = NOW() WHERE id = :list_id AND user_id = :user_id RETURNING id, user_id, name, description, player_ids, is_default, created_at, updated_at"

    update_data["list_id"] = list_id
    update_data["user_id"] = user_id
    result = db.execute(text(query), update_data)
    db.commit()

    updated_list = result.mappings().first()
    return updated_list


@router.delete("/{list_id}", response_model=DeleteListResponse)
def delete_list(
    list_id: UUID,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Delete list (cannot delete default list).

    Permanently deletes a player list if it belongs to the specified user
    and is not marked as the default list.
    Raises 400 if attempting to delete the default list.
    Raises 404 if the list doesn't exist or doesn't belong to the user.

    - **list_id**: The ID of the list to delete
    - **user_id**: The ID of the user who owns the list
    """
    existing = db.execute(
        text("""
            SELECT id, is_default
            FROM player_lists
            WHERE id = :list_id AND user_id = :user_id
        """),
        {"list_id": list_id, "user_id": user_id}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with id {list_id} not found"
        )

    if existing['is_default']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default list"
        )

    db.execute(
        text("DELETE FROM player_lists WHERE id = :list_id AND user_id = :user_id"),
        {"list_id": list_id, "user_id": user_id}
    )
    db.commit()

    return DeleteListResponse(success=True)


@router.post("/{list_id}/players", response_model=PlayerListResponse)
def add_player_to_list(
    list_id: UUID,
    player_data: AddPlayerRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Add player to list.

    Adds a player ID to the list's player_ids array if it's not already present.
    Returns the updated list with the new player_ids array.
    Raises 404 if the list doesn't exist or doesn't belong to the user.

    - **list_id**: The ID of the list to add the player to
    - **player_data**: The player ID to add
    - **user_id**: The ID of the user who owns the list
    """
    existing = db.execute(
        text("""
            SELECT id, player_ids
            FROM player_lists
            WHERE id = :list_id AND user_id = :user_id
        """),
        {"list_id": list_id, "user_id": user_id}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with id {list_id} not found"
        )

    current_player_ids = existing['player_ids'] or []
    player_uuid = UUID(player_data.player_id)

    if player_uuid not in current_player_ids:
        current_player_ids.append(player_uuid)

    result = db.execute(
        text("""
            UPDATE player_lists
            SET player_ids = :player_ids, updated_at = NOW()
            WHERE id = :list_id AND user_id = :user_id
            RETURNING id, user_id, name, description, player_ids, is_default, created_at, updated_at
        """),
        {"list_id": list_id, "user_id": user_id, "player_ids": current_player_ids}
    )
    db.commit()

    updated_list = result.mappings().first()
    return updated_list


@router.delete("/{list_id}/players/{player_id}", response_model=PlayerListResponse)
def remove_player_from_list(
    list_id: UUID,
    player_id: UUID,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Remove player from list.

    Removes a player ID from the list's player_ids array.
    Returns the updated list with the modified player_ids array.
    Raises 404 if the list doesn't exist or doesn't belong to the user.

    - **list_id**: The ID of the list to remove the player from
    - **player_id**: The ID of the player to remove
    - **user_id**: The ID of the user who owns the list
    """
    existing = db.execute(
        text("""
            SELECT id, player_ids
            FROM player_lists
            WHERE id = :list_id AND user_id = :user_id
        """),
        {"list_id": list_id, "user_id": user_id}
    ).mappings().first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List with id {list_id} not found"
        )

    current_player_ids = existing['player_ids'] or []
    if player_id in current_player_ids:
        current_player_ids.remove(player_id)

    result = db.execute(
        text("""
            UPDATE player_lists
            SET player_ids = :player_ids, updated_at = NOW()
            WHERE id = :list_id AND user_id = :user_id
            RETURNING id, user_id, name, description, player_ids, is_default, created_at, updated_at
        """),
        {"list_id": list_id, "user_id": user_id, "player_ids": current_player_ids}
    )
    db.commit()

    updated_list = result.mappings().first()
    return updated_list


@router.post("/bulk/add-player", response_model=List[PlayerListResponse])
def bulk_add_player(
    bulk_data: BulkAddPlayerRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Add player to multiple lists at once.

    Adds the specified player ID to multiple lists simultaneously.
    Only updates lists that belong to the specified user.
    Returns all updated lists.
    Raises 404 if none of the specified lists exist or belong to the user.

    - **bulk_data**: The player ID and list of list IDs to add the player to
    - **user_id**: The ID of the user who owns the lists
    """
    player_uuid = UUID(bulk_data.player_id)
    list_uuids = [UUID(list_id) for list_id in bulk_data.list_ids]

    result = db.execute(
        text("""
            SELECT id, user_id, name, description, player_ids, is_default, created_at, updated_at
            FROM player_lists
            WHERE id = ANY(:list_ids) AND user_id = :user_id
        """),
        {"list_ids": list_uuids, "user_id": user_id}
    )
    lists = result.mappings().all()

    if not lists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching lists found"
        )

    updated_lists = []
    for player_list in lists:
        current_player_ids = player_list['player_ids'] or []

        if player_uuid not in current_player_ids:
            current_player_ids.append(player_uuid)

            result = db.execute(
                text("""
                    UPDATE player_lists
                    SET player_ids = :player_ids, updated_at = NOW()
                    WHERE id = :list_id
                    RETURNING id, user_id, name, description, player_ids, is_default, created_at, updated_at
                """),
                {"list_id": player_list['id'], "player_ids": current_player_ids}
            )
            updated_list = result.mappings().first()
            updated_lists.append(updated_list)
        else:
            updated_lists.append(player_list)

    db.commit()
    return updated_lists
