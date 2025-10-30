from sqlalchemy import Column, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("league_id", "name", name="teams_league_id_name_key"),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("dekedata.leagues.id"))
    code = Column(CITEXT)
    name = Column(Text, nullable=False)
    city = Column(Text)

    league = relationship("League", back_populates="teams")
    player_seasons = relationship("PlayerSeason", back_populates="team")
