from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class TeamBase(BaseModel):
    league_id: Optional[UUID] = None
    code: Optional[str] = None
    name: str
    city: Optional[str] = None


class TeamCreate(TeamBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "league_id": "123e4567-e89b-12d3-a456-426614174000",
                "code": "TOR",
                "name": "Toronto Maple Leafs",
                "city": "Toronto"
            }
        }
    )


class TeamUpdate(BaseModel):
    league_id: Optional[UUID] = None
    code: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "Toronto"
            }
        }
    )


class TeamResponse(TeamBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
