from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class SeasonBase(BaseModel):
    label: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class SeasonCreate(SeasonBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "2024-25",
                "start_year": 2024,
                "end_year": 2025
            }
        }
    )


class SeasonUpdate(BaseModel):
    label: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "end_year": 2025
            }
        }
    )


class SeasonResponse(SeasonBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
