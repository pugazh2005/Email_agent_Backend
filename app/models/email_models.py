from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Email(Base):
    __tablename__ = "emails"

    email_id = Column(String, primary_key=True, index=True)
    sender_email = Column(String, index=True)
    customer_name = Column(String)

    subject = Column(String, nullable=True)
    body = Column(Text)

    intent = Column(String)
    urgency = Column(String)
    topic = Column(String)
    summary = Column(Text)

    
    status = Column(String, default="received")
    

    
    draft_response = Column(Text, nullable=True)
    final_response = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())