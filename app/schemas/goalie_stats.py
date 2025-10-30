from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from decimal import Decimal


class GoalieStatsBase(BaseModel):
    player_season_id: UUID
    gp: int = 0
    gs: Optional[int] = None
    w: Optional[int] = None
    l: Optional[int] = None
    otl: Optional[int] = None
    so: Optional[int] = None
    ga: Optional[int] = None
    sa: Optional[int] = None
    sv: Optional[int] = None
    toi_min: Optional[int] = None
    gaa: Optional[Decimal] = None
    sv_pct: Optional[Decimal] = None


class GoalieStatsCreate(GoalieStatsBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_season_id": "123e4567-e89b-12d3-a456-426614174000",
                "gp": 50,
                "gs": 48,
                "w": 35,
                "l": 10,
                "otl": 3,
                "so": 5,
                "ga": 120,
                "sa": 1450,
                "sv": 1330,
                "toi_min": 2950,
                "gaa": 2.44,
                "sv_pct": 0.9172
            }
        }
    )


class GoalieStatsUpdate(BaseModel):
    gp: Optional[int] = None
    gs: Optional[int] = None
    w: Optional[int] = None
    l: Optional[int] = None
    otl: Optional[int] = None
    so: Optional[int] = None
    ga: Optional[int] = None
    sa: Optional[int] = None
    sv: Optional[int] = None
    toi_min: Optional[int] = None
    gaa: Optional[Decimal] = None
    sv_pct: Optional[Decimal] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "w": 36,
                "so": 6
            }
        }
    )


class GoalieStatsResponse(GoalieStatsBase):
    model_config = ConfigDict(from_attributes=True)
