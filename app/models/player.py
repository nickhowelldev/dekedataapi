from sqlalchemy import Column, Text, Integer, CheckConstraint, TIMESTAMP, func, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL
import uuid
from app.db.base import Base


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        CheckConstraint("position IN ('F','D','G')", name="players_position_check"),
        CheckConstraint("shoots IN ('L','R','C')", name="players_shoots_check"),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    position = Column(CHAR(1), nullable=False)
    dob = Column(Text)
    player_id = Column(Text)
    shoots = Column(CHAR(1))
    region = Column(Text)
    height = Column(DECIMAL(5, 2))
    weight = Column(DECIMAL(6, 3))
    photo_url = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    player_seasons = relationship("PlayerSeason", back_populates="player", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="player", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="player", cascade="all, delete-orphan")

    @property
    def birth_year(self):
        """Extract birth year from dob for backward compatibility."""
        if not self.dob:
            return None
        try:
            return int(self.dob.split('-')[0])
        except (ValueError, IndexError):
            return None

    @property
    def youth_scores(self):
        from app.schemas.score import ScoreResponse
        filtered_scores = [s for s in self.scores if s.age and 13 <= s.age <= 17]
        return [ScoreResponse.model_validate(s) for s in filtered_scores]

    @property
    def overall(self):
        from decimal import Decimal
        filtered_scores = [s for s in self.scores if s.age and 13 <= s.age <= 17]
        if not filtered_scores:
            return None
        overall_sum = sum(float(s.overall) for s in filtered_scores if s.overall)
        count = len([s for s in filtered_scores if s.overall])
        return round(Decimal(overall_sum / count), 2) if count > 0 else None
