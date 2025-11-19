from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from decimal import Decimal
from app.schemas.player import PlayerResponse, MinimalPlayerResponse


class PlayerSearchMetadata(BaseModel):
    total: int
    returned: int
    skip: int
    limit: int
    min_height: Optional[Decimal] = None
    max_height: Optional[Decimal] = None
    min_weight: Optional[Decimal] = None
    max_weight: Optional[Decimal] = None
    min_birth_year: Optional[int] = None
    max_birth_year: Optional[int] = None
    min_overall: Optional[Decimal] = None
    max_overall: Optional[Decimal] = None
    min_skating: Optional[Decimal] = None
    max_skating: Optional[Decimal] = None
    min_shot: Optional[Decimal] = None
    max_shot: Optional[Decimal] = None
    min_iq: Optional[Decimal] = None
    max_iq: Optional[Decimal] = None
    min_compete: Optional[Decimal] = None
    max_compete: Optional[Decimal] = None
    min_physical: Optional[Decimal] = None
    max_physical: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerSearchResponse(BaseModel):
    data: List[PlayerResponse]
    metadata: PlayerSearchMetadata

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Connor Bedard",
                        "position": "F",
                        "birth_year": 2005,
                        "shoots": "R",
                        "height": 178.0,
                        "weight": 83.9,
                        "created_at": "2025-10-30T12:00:00Z",
                        "updated_at": "2025-10-30T12:00:00Z"
                    }
                ],
                "metadata": {
                    "total": 156,
                    "returned": 20,
                    "skip": 0,
                    "limit": 20,
                    "min_height": 165.5,
                    "max_height": 198.12,
                    "min_weight": 68.5,
                    "max_weight": 105.2,
                    "min_birth_year": 2003,
                    "max_birth_year": 2007
                }
            }
        }
    )


class MinimalSearchMetadata(BaseModel):
    """Minimal metadata for lightweight search responses."""
    total: int
    returned: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class MinimalPlayersResponse(BaseModel):
    """Minimal player search response - optimized for navigation/autocomplete."""
    data: List[MinimalPlayerResponse]
    metadata: MinimalSearchMetadata

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Connor Bedard",
                        "position": "F",
                        "birth_year": 2005,
                        "region": "North Vancouver, BC",
                        "photo_url": "https://example.com/bedard.jpg"
                    }
                ],
                "metadata": {
                    "total": 1,
                    "returned": 1,
                    "skip": 0,
                    "limit": 50
                }
            }
        }
    )
