from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from decimal import Decimal


class DraftBase(BaseModel):
    player_id: UUID
    season_id: Optional[UUID] = None
    draft_league: str
    probability: Decimal
    round_estimate: Optional[int] = None
    team_hints: Optional[List[str]] = None


class DraftCreate(DraftBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "123e4567-e89b-12d3-a456-426614174000",
                "season_id": "223e4567-e89b-12d3-a456-426614174000",
                "draft_league": "NHL",
                "probability": 99.5,
                "round_estimate": 1,
                "team_hints": ["CHI", "ANA", "CBJ"]
            }
        }
    )


class DraftUpdate(BaseModel):
    season_id: Optional[UUID] = None
    draft_league: Optional[str] = None
    probability: Optional[Decimal] = None
    round_estimate: Optional[int] = None
    team_hints: Optional[List[str]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "probability": 100.0,
                "round_estimate": 1
            }
        }
    )


class DraftResponse(DraftBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
