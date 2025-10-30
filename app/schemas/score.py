from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ScoreBase(BaseModel):
    player_id: UUID
    season_id: Optional[UUID] = None
    age: Optional[int] = None
    overall: Decimal
    prospect: Optional[Decimal] = None
    skating: Optional[Decimal] = None
    shot: Optional[Decimal] = None
    iq: Optional[Decimal] = None
    compete: Optional[Decimal] = None
    physical: Optional[Decimal] = None
    projection_note: Optional[str] = None


class ScoreCreate(ScoreBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "123e4567-e89b-12d3-a456-426614174000",
                "season_id": "223e4567-e89b-12d3-a456-426614174000",
                "age": 16,
                "overall": 95.5,
                "prospect": 98.0,
                "skating": 92.0,
                "shot": 96.0,
                "iq": 98.0,
                "compete": 94.0,
                "physical": 88.0,
                "projection_note": "Elite NHL prospect, franchise player potential"
            }
        }
    )


class ScoreUpdate(BaseModel):
    season_id: Optional[UUID] = None
    age: Optional[int] = None
    overall: Optional[Decimal] = None
    prospect: Optional[Decimal] = None
    skating: Optional[Decimal] = None
    shot: Optional[Decimal] = None
    iq: Optional[Decimal] = None
    compete: Optional[Decimal] = None
    physical: Optional[Decimal] = None
    projection_note: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall": 96.0,
                "prospect": 99.0
            }
        }
    )


class ScoreResponse(ScoreBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
