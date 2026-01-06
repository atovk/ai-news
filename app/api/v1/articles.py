"""
新闻文章 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.article_service import ArticleService
from app.schemas.article import Article, ArticleListResponse
from app.schemas.common import PaginationParams

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: str = Query(None, description="分类筛选"),
    source_id: int = Query(None, description="新闻源ID筛选"),
    tag_id: int = Query(None, description="标签ID筛选"),
    db: Session = Depends(get_db)
):
    """获取新闻文章列表"""
    article_service = ArticleService(db)
    
    skip = (page - 1) * size
    articles = article_service.get_articles(
        skip=skip, 
        limit=size, 
        category=category,
        source_id=source_id,
        tag_id=tag_id
    )
    
    total = article_service.get_articles_count(
        category=category,
        source_id=source_id,
        tag_id=tag_id
    )
    
    return ArticleListResponse(
        total=total,
        page=page,
        size=size,
        articles=[Article.model_validate(article) for article in articles]
    )


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """获取单篇新闻文章详情"""
    article_service = ArticleService(db)
    article = article_service.get_article(article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return Article.model_validate(article)


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """删除新闻文章"""
    article_service = ArticleService(db)
    success = article_service.delete_article(article_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {"message": "Article deleted successfully"}
