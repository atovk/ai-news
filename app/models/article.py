"""
新闻文章模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from app.models.database import Base
import enum


class LLMProcessingStatus(enum.Enum):
    """LLM 处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class NewsArticle(Base):
    """新闻文章模型"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(Text, unique=True, nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("news_sources.id"))
    author = Column(String(100))
    published_at = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_processed = Column(Boolean, default=False)
    category = Column(String(50))
    tags = Column(Text)  # JSON格式存储标签数组
    
    # LLM 处理相关字段
    chinese_title = Column(Text, comment="中文标题")
    llm_summary = Column(Text, comment="LLM 生成的400字摘要")
    original_language = Column(String(10), comment="原文语言代码")
    llm_processed_at = Column(DateTime, comment="LLM 处理时间")
    llm_processing_status = Column(
        Enum(LLMProcessingStatus),
        default=LLMProcessingStatus.PENDING,
        comment="LLM 处理状态"
    )
    
    # Engagement metrics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    trending_score = Column(Float, default=0.0)
    
    # 关系
    source = relationship("NewsSource", back_populates="articles")
    article_tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
