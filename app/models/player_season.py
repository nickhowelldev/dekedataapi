from sqlalchemy import Column, Text, Integer, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL
import uuid
from app.db.base import Base


class PlayerSeason(Base):
    __tablename__ = "player_seasons"
    __table_args__ = (
        CheckConstraint("split IN ('Regular','Playoffs','Exhibition')", name="player_seasons_split_check"),
        UniqueConstraint("player_id", "season_id", "league_id", "split", name="player_seasons_unique_key"),
        Index("ix_player_seasons_player_season", "player_id", "season_id"),
        Index("ix_player_seasons_league_season", "league_id", "season_id"),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.players.id", ondelete="CASCADE"), nullable=False)
    season_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.seasons.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.teams.id"))
    league_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.leagues.id"), nullable=False)
    split = Column(Text, nullable=False, default="Regular")
    age = Column(Integer)
    level = Column(Text)
    competition_strength = Column(DECIMAL(6, 3))

    player = relationship("Player", back_populates="player_seasons")
    season = relationship("Season", back_populates="player_seasons")
    team = relationship("Team", back_populates="player_seasons")
    league = relationship("League", back_populates="player_seasons")
    player_stats = relationship("PlayerStats", back_populates="player_season", uselist=False, cascade="all, delete-orphan")
    goalie_stats = relationship("GoalieStats", back_populates="player_season", uselist=False, cascade="all, delete-orphan")
