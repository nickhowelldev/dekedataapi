from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class LeagueBase(BaseModel):
    code: str
    name: str
    tier: Optional[str] = None
    country: Optional[str] = None


class LeagueCreate(LeagueBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "NHL",
                "name": "National Hockey League",
                "tier": "NHL",
                "country": "North America"
            }
        }
    )


class LeagueUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    tier: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "country": "Canada"
            }
        }
    )


class LeagueResponse(LeagueBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
