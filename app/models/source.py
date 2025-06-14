"""
新闻源模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.database import Base


class NewsSource(Base):
    """新闻源模型"""
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    source_type = Column(String(20), default="rss")  # rss, api
    is_active = Column(Boolean, default=True)
    fetch_interval = Column(Integer, default=3600)  # 秒
    last_fetch_time = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    articles = relationship("NewsArticle", back_populates="source")
