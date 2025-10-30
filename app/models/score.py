from sqlalchemy import Column, Text, Integer, ForeignKey, UniqueConstraint, TIMESTAMP, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL
import uuid
from app.db.base import Base


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("player_id", "season_id", name="scores_player_season_key"),
        Index("ix_scores_player_season", "player_id", "season_id"),
        Index("ix_scores_player_age", "player_id", "age"),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.players.id", ondelete="CASCADE"), nullable=False)
    season_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.seasons.id"))
    age = Column(Integer)
    overall = Column(DECIMAL(5, 2), nullable=False)
    prospect = Column(DECIMAL(5, 2))
    skating = Column(DECIMAL(5, 2))
    shot = Column(DECIMAL(5, 2))
    iq = Column(DECIMAL(5, 2))
    compete = Column(DECIMAL(5, 2))
    physical = Column(DECIMAL(5, 2))
    projection_note = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    player = relationship("Player", back_populates="scores")
    season = relationship("Season", back_populates="scores")
