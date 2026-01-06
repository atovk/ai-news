"""
Tag system models with hierarchy support
"""
from sqlalchemy import Boolean, Column, Integer, String, Text, TIMESTAMP, Float, ARRAY, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base


class Tag(Base):
    """标签模型 - 支持层级结构"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    slug = Column(String(100), unique=True, index=True)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey("tags.id"), nullable=True)
    level = Column(Integer, default=1)  # 1: 一级分类, 2: 二级标签, 3: 关键词
    
    # Display
    icon = Column(String(50))
    color = Column(String(20))
    description = Column(Text)
    
    # AI features
    ai_keywords = Column(Text)  # JSON string array for SQLite compatibility
    ai_prompt_id = Column(Integer, ForeignKey("ai_prompt_templates.id"), nullable=True)
    
    # Stats
    article_count = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    parent = relationship("Tag", remote_side=[id], backref="children")
    article_tags = relationship("ArticleTag", back_populates="tag")
    user_preferences = relationship("UserTagPreference", back_populates="tag")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', level={self.level})>"


class ArticleTag(Base):
    """文章-标签关联表"""
    __tablename__ = "article_tags"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    
    relevance_score = Column(Float, default=1.0)  # AI计算的相关性 0-1
    assigned_by = Column(String(20), default="ai")  # ai, manual, user
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    tag = relationship("Tag", back_populates="article_tags")
    article = relationship("NewsArticle", back_populates="article_tags")
    
    __table_args__ = (
        {"schema": None},
    )


class UserTagPreference(Base):
    """用户标签偏好"""
    __tablename__ = "user_tag_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    
    preference_score = Column(Float, default=5.0)  # 1.0-10.0 兴趣强度
    source =Column(String(20), default="manual")  # manual, implicit, ai
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tag_preferences")
    tag = relationship("Tag", back_populates="user_preferences")
    
    __table_args__ = (
        {"schema": None},
    )
