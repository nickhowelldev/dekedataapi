from sqlalchemy import Column, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class League(Base):
    __tablename__ = "leagues"
    __table_args__ = (
        CheckConstraint(
            "tier IN ('NHL','AHL','ECHL','Juniors','College','HS','Intl','Other')",
            name="leagues_tier_check"
        ),
        {"schema": "dekedata"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(CITEXT, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    tier = Column(Text)
    country = Column(Text)

    teams = relationship("Team", back_populates="league")
    player_seasons = relationship("PlayerSeason", back_populates="league")
