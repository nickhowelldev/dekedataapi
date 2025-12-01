from sqlalchemy import Column, Text, Integer, TIMESTAMP, func, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class PlayerList(Base):
    __tablename__ = "player_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    player_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    is_default = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
