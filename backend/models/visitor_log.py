from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base


class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id = Column(Integer, primary_key=True, index=True)
    page = Column(String(255))
    referrer = Column(String(500))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)
