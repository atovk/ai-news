"""
今日功能相关的 Pydantic 模式
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.article import LLMProcessingStatus


from app.schemas.tag import ArticleTagResponse
from pydantic import BaseModel, Field

class TodayArticleView(BaseModel):
    """今日文章视图模型"""
    id: int
    original_title: str
    chinese_title: str
    url: str
    author: Optional[str]
    source_name: str
    published_at: datetime
    llm_summary: str
    original_language: str
    tags: List[ArticleTagResponse] = Field(default=[], validation_alias="article_tags")
    is_recommended: bool = False
    recommendation_score: float = 0.0
    
    class Config:
        from_attributes = True


class TodayStatsResponse(BaseModel):
    """今日统计响应模型"""
    today_total: int
    processed: int
    processing: int
    pending: int
    failed: int
    language_distribution: Dict[str, int]


class TodayArticleListResponse(BaseModel):
    """今日文章列表响应模型"""
    total: int
    page: int
    size: int
    articles: List[TodayArticleView]


class ProcessingTaskResponse(BaseModel):
    """处理任务响应模型"""
    message: str
    task_id: Optional[str] = None
    articles_count: int = 0


class LLMHealthResponse(BaseModel):
    """LLM 健康检查响应模型"""
    providers: Dict[str, Dict[str, Any]]
    active_providers: List[str]
    default_provider: str
