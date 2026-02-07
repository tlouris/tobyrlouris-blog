from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(100))
    author = Column(String(100))
    email = Column(String(255))
    content = Column(Text)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
