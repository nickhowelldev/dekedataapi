from sqlalchemy import Column, Integer, ForeignKey, Computed
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"
    __table_args__ = {"schema": "dekedata"}

    player_season_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dekedata.player_seasons.id", ondelete="CASCADE"),
        primary_key=True
    )
    gp = Column(Integer, nullable=False, default=0)
    g = Column(Integer, nullable=False, default=0)
    a = Column(Integer, nullable=False, default=0)
    pts = Column(Integer, Computed("g + a"))
    pim = Column(Integer)
    plus_minus = Column(Integer)
    sog = Column(Integer)
    hits = Column(Integer)
    blocks = Column(Integer)
    pp_g = Column(Integer)
    sh_g = Column(Integer)

    player_season = relationship("PlayerSeason", back_populates="player_stats")
