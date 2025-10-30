from sqlalchemy import Column, Text, Integer, ForeignKey, CheckConstraint, UniqueConstraint, Index, ARRAY
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL
import uuid
from app.db.base import Base


class Draft(Base):
    __tablename__ = "drafts"
    __table_args__ = (
        CheckConstraint("probability >= 0 AND probability <= 100", name="drafts_probability_check"),
        UniqueConstraint("player_id", "season_id", "draft_league", name="drafts_unique_key"),
        Index("ix_drafts_league_probability", "draft_league", "probability"),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.players.id", ondelete="CASCADE"), nullable=False)
    season_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.seasons.id"))
    draft_league = Column(CITEXT, nullable=False)
    probability = Column(DECIMAL(5, 2), nullable=False)
    round_estimate = Column(Integer)
    team_hints = Column(ARRAY(Text))

    player = relationship("Player", back_populates="drafts")
    season = relationship("Season", back_populates="drafts")
