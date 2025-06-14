"""
搜索 API 路由
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.database import get_db
from app.models.article import NewsArticle
from app.schemas.search import SearchQuery, SearchResponse
from app.schemas.article import Article

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search_articles(
    q: str = Query(..., description="搜索关键词"),
    category: str = Query(None, description="分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort: str = Query("published_at", description="排序方式"),
    db: Session = Depends(get_db)
):
    """搜索新闻文章"""
    start_time = time.time()
    
    # 构建搜索查询
    query = db.query(NewsArticle)
    
    # 关键词搜索（简单的LIKE搜索，生产环境建议使用全文搜索）
    if q:
        search_filter = or_(
            NewsArticle.title.contains(q),
            NewsArticle.summary.contains(q),
            NewsArticle.content.contains(q)
        )
        query = query.filter(search_filter)
    
    # 分类筛选
    if category:
        query = query.filter(NewsArticle.category == category)
    
    # 计算总数
    total = query.count()
    
    # 排序
    if sort == "published_at":
        query = query.order_by(NewsArticle.published_at.desc())
    elif sort == "fetched_at":
        query = query.order_by(NewsArticle.fetched_at.desc())
    
    # 分页
    skip = (page - 1) * size
    articles = query.offset(skip).limit(size).all()
    
    # 计算搜索耗时
    took = time.time() - start_time
    
    return SearchResponse(
        query=q,
        total=total,
        page=page,
        size=size,
        articles=[Article.model_validate(article) for article in articles],
        took=took
    )
