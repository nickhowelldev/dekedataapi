from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from decimal import Decimal


class PlayerSeasonBase(BaseModel):
    player_id: UUID
    season_id: UUID
    team_id: Optional[UUID] = None
    league_id: UUID
    split: str = "Regular"
    age: Optional[int] = None
    level: Optional[str] = None
    competition_strength: Optional[Decimal] = None


class PlayerSeasonCreate(PlayerSeasonBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "123e4567-e89b-12d3-a456-426614174000",
                "season_id": "223e4567-e89b-12d3-a456-426614174000",
                "team_id": "323e4567-e89b-12d3-a456-426614174000",
                "league_id": "423e4567-e89b-12d3-a456-426614174000",
                "split": "Regular",
                "age": 18,
                "level": "U18",
                "competition_strength": 1.25
            }
        }
    )


class PlayerSeasonUpdate(BaseModel):
    team_id: Optional[UUID] = None
    league_id: Optional[UUID] = None
    split: Optional[str] = None
    age: Optional[int] = None
    level: Optional[str] = None
    competition_strength: Optional[Decimal] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 19
            }
        }
    )


class PlayerSeasonResponse(PlayerSeasonBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
