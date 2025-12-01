from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class PlayerListBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlayerListCreate(PlayerListBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Top Prospects",
                "description": "My favorite draft prospects for 2025"
            }
        }
    )


class PlayerListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated List Name",
                "description": "Updated description"
            }
        }
    )


class PlayerListResponse(PlayerListBase):
    id: UUID
    player_ids: List[UUID]
    created_at: datetime
    updated_at: datetime
    is_default: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class AddPlayerRequest(BaseModel):
    player_id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class BulkAddPlayerRequest(BaseModel):
    player_id: str
    list_ids: List[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "123e4567-e89b-12d3-a456-426614174000",
                "list_ids": ["223e4567-e89b-12d3-a456-426614174001", "323e4567-e89b-12d3-a456-426614174002"]
            }
        }
    )


class DeleteListResponse(BaseModel):
    success: bool
