"""
新闻源数据模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, ConfigDict


class SourceBase(BaseModel):
    """新闻源基础模式"""
    name: str
    url: HttpUrl
    source_type: str = "rss"
    is_active: bool = True
    fetch_interval: int = 3600


class SourceCreate(SourceBase):
    """创建新闻源模式"""
    pass


class SourceUpdate(BaseModel):
    """更新新闻源模式"""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    source_type: Optional[str] = None
    is_active: Optional[bool] = None
    fetch_interval: Optional[int] = None


class Source(SourceBase):
    """新闻源响应模式"""
    id: int
    last_fetch_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SourceListResponse(BaseModel):
    """新闻源列表响应"""
    sources: List[Source]
    total: int
    skip: int
    limit: int
