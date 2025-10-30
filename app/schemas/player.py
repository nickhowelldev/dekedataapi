from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class PlayerBase(BaseModel):
    name: str
    position: str
    birth_year: Optional[int] = None
    shoots: Optional[str] = None
    region: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    photo_url: Optional[str] = None


class PlayerCreate(PlayerBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Connor Bedard",
                "position": "F",
                "birth_year": 2005,
                "shoots": "R",
                "region": "North Vancouver, BC",
                "height": 178.0,
                "weight": 83.9,
                "photo_url": "https://example.com/bedard.jpg"
            }
        }
    )


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    birth_year: Optional[int] = None
    shoots: Optional[str] = None
    region: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    photo_url: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "height": 180.0,
                "weight": 85.0
            }
        }
    )


class PlayerResponse(PlayerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    overall: Optional[Decimal] = None
    youth_scores: Optional[List] = None

    model_config = ConfigDict(from_attributes=True)
