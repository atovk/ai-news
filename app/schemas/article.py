"""
新闻文章数据模式
"""
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict


class ArticleBase(BaseModel):
    """文章基础模式"""
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: HttpUrl
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    tags: List[str] = []


class ArticleCreate(ArticleBase):
    """创建文章模式"""
    source_id: int


class ArticleUpdate(BaseModel):
    """更新文章模式"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_processed: Optional[bool] = None


from app.schemas.tag import ArticleTagResponse
from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict, Field

# ... (skipped types)

class Article(ArticleBase):
    """文章响应模式"""
    id: int
    source_id: int
    fetched_at: datetime
    is_processed: bool = False
    
    # Engagement metrics
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    trending_score: float = 0.0
    
    # Map to article_tags relationship
    tags: List[ArticleTagResponse] = Field(default=[], validation_alias="article_tags")
    
    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    total: int
    page: int
    size: int
    articles: List[Article]
