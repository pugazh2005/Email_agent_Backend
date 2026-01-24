from sqlalchemy import Column,String,DateTime,ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class EmailEmbedding(Base):
    __tablename__ = "email_embeddings"

    email_id = Column(String, ForeignKey("emails.email_id"), primary_key=True)
    embedding = Column(Vector(384))
    created_at = Column(DateTime(timezone=True), server_default=func.now())