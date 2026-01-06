"""
新闻源管理 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.source_service import SourceService
from app.services.news_aggregator import NewsAggregatorService
from app.models.article import NewsArticle
from app.schemas.source import Source, SourceCreate, SourceUpdate, SourceListResponse

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=SourceListResponse)
async def get_sources(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    active_only: bool = Query(False, description="仅显示活跃源"),
    db: Session = Depends(get_db)
):
    """获取新闻源列表"""
    source_service = SourceService(db)
    sources = source_service.get_sources(skip=skip, limit=limit, active_only=active_only)
    total = source_service.get_total_count(active_only=active_only)
    
    return SourceListResponse(
        sources=[Source.model_validate(source) for source in sources],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{source_id}", response_model=Source)
async def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """获取单个新闻源详情"""
    source_service = SourceService(db)
    source = source_service.get_source(source_id)
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return Source.model_validate(source)


@router.post("/", response_model=Source, status_code=status.HTTP_201_CREATED)
async def create_source(
    source: SourceCreate,
    db: Session = Depends(get_db)
):
    """创建新闻源"""
    source_service = SourceService(db)
    db_source = source_service.create_source(source)
    return Source.model_validate(db_source)


@router.put("/{source_id}", response_model=Source)
async def update_source(
    source_id: int,
    source_update: SourceUpdate,
    db: Session = Depends(get_db)
):
    """更新新闻源"""
    source_service = SourceService(db)
    db_source = source_service.update_source(source_id, source_update)
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return Source.model_validate(db_source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """删除新闻源"""
    source_service = SourceService(db)
    success = source_service.delete_source(source_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")


@router.post("/{source_id}/fetch")
async def fetch_source_endpoint(
    source_id: int,
    db: Session = Depends(get_db)
):
    """手动抓取指定新闻源"""
    source_service = SourceService(db)
    source = source_service.get_source(source_id)
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    try:
        aggregator = NewsAggregatorService(db)
        articles = await aggregator.fetch_source(source)
        return {
            "message": f"Successfully fetched {len(articles)} articles",
            "articles_count": len(articles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
