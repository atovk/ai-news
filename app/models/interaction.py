"""
User interaction models: history, favorites, prompts
"""
from sqlalchemy import Boolean, Column, Integer, String, Text, TIMESTAMP, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base


class ReadingHistory(Base):
    """阅读历史"""
    __tablename__ = "reading_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    
    reading_duration = Column(Integer, default=0)  # 阅读时长(秒)
    completion_rate = Column(Float, default=0.0)  # 完成度 0-1
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="reading_history")
    article = relationship("NewsArticle")
    
    __table_args__ = (
        {"schema": None},
    )


class Favorite(Base):
    """收藏"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    
    folder = Column(String(50), default="default")  # 收藏夹分类
    notes = Column(Text)  # 用户笔记
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    article = relationship("NewsArticle")
    
    __table_args__ = (
        {"schema": None},
    )


class AIPromptTemplate(Base):
    """AI提示词模板"""
    __tablename__ = "ai_prompt_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # summary, translation, classification, aggregation
    
    # LLM settings
    model_name = Column(String(50), default="qwen3:4b")
    system_prompt = Column(Text)
    user_prompt_template = Column(Text)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=400)
    
    # Status & versioning
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])


class AggregatedTopic(Base):
    """聚合话题"""
    __tablename__ = "aggregated_topics"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    
    # AI generated content
    ai_summary = Column(Text)  # AI综合摘要
    ai_key_points = Column(Text)  # JSON array stored as text
    
    # Stats
    source_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    trending_score = Column(Float, default=0.0)
    
    # Tags (stored as comma-separated IDs for simplicity)
    tag_ids = Column(String(500))
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    topic_articles = relationship("TopicArticle", back_populates="topic")


class TopicArticle(Base):
    """话题-文章关联"""
    __tablename__ = "topic_articles"
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("aggregated_topics.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    
    relevance_score = Column(Float, default=1.0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    topic = relationship("AggregatedTopic", back_populates="topic_articles")
    article = relationship("NewsArticle")
    
    __table_args__ = (
        {"schema": None},
    )
