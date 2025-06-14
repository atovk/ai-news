"""
搜索相关数据模式
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.article import Article


class SearchQuery(BaseModel):
    """搜索查询模式"""
    q: str  # 搜索关键词
    category: Optional[str] = None
    page: int = 1
    size: int = 20
    sort: str = "published_at"  # published_at, relevance
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class SearchResponse(BaseModel):
    """搜索响应模式"""
    query: str
    total: int
    page: int
    size: int
    articles: List[Article]
    took: float  # 搜索耗时(秒)
