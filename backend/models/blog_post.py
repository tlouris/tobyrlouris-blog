from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True)
    title = Column(String(500))
    excerpt = Column(Text)
    content = Column(Text)
    category = Column(String(100))
    author = Column(String(100), default="Toby R. Louris")
    featured = Column(Boolean, default=False)
    status = Column(String(20), default="published")
    reading_time = Column(String(20))
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
