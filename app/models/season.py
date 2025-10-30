from sqlalchemy import Column, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        CheckConstraint("start_year >= 1900", name="seasons_start_year_check"),
        CheckConstraint("end_year >= start_year", name="seasons_end_year_check"),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(CITEXT, unique=True, nullable=False)
    start_year = Column(Integer)
    end_year = Column(Integer)

    player_seasons = relationship("PlayerSeason", back_populates="season")
    scores = relationship("Score", back_populates="season")
    drafts = relationship("Draft", back_populates="season")
