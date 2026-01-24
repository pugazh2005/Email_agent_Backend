from app.core.database import Base
from sqlalchemy import Column, Text, String, DateTime
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
import uuid
class ResponseExperience(Base):
    __tablename__ = "response_experience"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    email_intent = Column(String)
    urgency = Column(String)
    topic = Column(String)

    email_embedding = Column(Vector(384))
    response_text = Column(Text)

    outcome = Column(String)
    feedback = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
