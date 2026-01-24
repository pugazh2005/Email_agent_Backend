from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Bug(Base):
    __tablename__ = "bugs"

    bug_id = Column(String, primary_key=True)
    email_id = Column(String, index=True)

    description = Column(Text)
    status = Column(String, default="open")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
