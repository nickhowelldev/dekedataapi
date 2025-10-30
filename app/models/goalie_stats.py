from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL
from app.db.base import Base


class GoalieStats(Base):
    __tablename__ = "goalie_stats"
    __table_args__ = {"schema": "dekedata"}

    player_season_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dekedata.player_seasons.id", ondelete="CASCADE"),
        primary_key=True
    )
    gp = Column(Integer, nullable=False, default=0)
    gs = Column(Integer)
    w = Column(Integer)
    l = Column(Integer)
    otl = Column(Integer)
    so = Column(Integer)
    ga = Column(Integer)
    sa = Column(Integer)
    sv = Column(Integer)
    toi_min = Column(Integer)
    gaa = Column(DECIMAL(5, 3))
    sv_pct = Column(DECIMAL(6, 4))

    player_season = relationship("PlayerSeason", back_populates="goalie_stats")
