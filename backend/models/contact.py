from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from database import Base


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(255))
    organization = Column(String(255), nullable=True)
    topic = Column(String(100))
    message = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
