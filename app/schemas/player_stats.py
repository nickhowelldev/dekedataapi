from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class PlayerStatsBase(BaseModel):
    player_season_id: UUID
    gp: int = 0
    g: int = 0
    a: int = 0
    pim: Optional[int] = None
    plus_minus: Optional[int] = None
    sog: Optional[int] = None
    hits: Optional[int] = None
    blocks: Optional[int] = None
    pp_g: Optional[int] = None
    sh_g: Optional[int] = None


class PlayerStatsCreate(PlayerStatsBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_season_id": "123e4567-e89b-12d3-a456-426614174000",
                "gp": 68,
                "g": 51,
                "a": 49,
                "pim": 24,
                "plus_minus": 15,
                "sog": 220,
                "hits": 45,
                "blocks": 30,
                "pp_g": 15,
                "sh_g": 2
            }
        }
    )


class PlayerStatsUpdate(BaseModel):
    gp: Optional[int] = None
    g: Optional[int] = None
    a: Optional[int] = None
    pim: Optional[int] = None
    plus_minus: Optional[int] = None
    sog: Optional[int] = None
    hits: Optional[int] = None
    blocks: Optional[int] = None
    pp_g: Optional[int] = None
    sh_g: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "g": 52,
                "a": 50
            }
        }
    )


class PlayerStatsResponse(BaseModel):
    player_season_id: UUID
    gp: int
    g: int
    a: int
    pts: int
    pim: Optional[int]
    plus_minus: Optional[int]
    sog: Optional[int]
    hits: Optional[int]
    blocks: Optional[int]
    pp_g: Optional[int]
    sh_g: Optional[int]

    model_config = ConfigDict(from_attributes=True)
