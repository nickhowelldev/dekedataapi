from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class LeagueBase(BaseModel):
    value: str
    label: str
    active: bool = True
    league_status: str = "inactive"
    hub_status: str = "inactive"


class LeagueCreate(LeagueBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": "nhl",
                "label": "National Hockey League",
                "active": True,
                "league_status": "active",
                "hub_status": "active"
            }
        }
    )


class LeagueUpdate(BaseModel):
    value: Optional[str] = None
    label: Optional[str] = None
    active: Optional[bool] = None
    league_status: Optional[str] = None
    hub_status: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "active": False,
                "league_status": "inactive"
            }
        }
    )


class LeagueResponse(LeagueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "value": "nhl",
                "label": "National Hockey League",
                "active": True,
                "league_status": "active",
                "hub_status": "active",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )
