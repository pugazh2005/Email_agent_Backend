from sqlalchemy import Column,Text,String
from pgvector.sqlalchemy import Vector
from app.core.database import Base
import uuid

class Knowledge_Base(Base):
    __tablename__ = "knowledge_base"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text)
    embedding = Column(Vector(384))
    source = Column(String)
