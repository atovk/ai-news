"""
今日功能 API 路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.today import (
    TodayArticleListResponse,
    TodayStatsResponse,
    LLMHealthResponse,
)
from app.services.today_service import TodayService
from app.services.content_processor import ContentProcessorService
from app.services.llm_manager import LLMServiceManager
from app.services.llm_config import LLMConfig, OllamaConfig
from app.services.llm_interface import LLMProvider
from app.models.article import NewsArticle
from app.core.llm_factory import get_llm_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/today", tags=["today"])


def get_content_processor() -> ContentProcessorService:
    """获取内容处理服务实例"""
    llm_mgr = get_llm_manager()
    return ContentProcessorService(llm_mgr)


def get_today_service(
    db: Session = Depends(get_db),
    content_processor: ContentProcessorService = Depends(get_content_processor),
) -> TodayService:
    """获取今日服务实例"""
    return TodayService(db, content_processor)


@router.get("/articles", response_model=TodayArticleListResponse)
async def get_today_articles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    source: Optional[str] = Query(None, description="筛选特定新闻源"),
    language: Optional[str] = Query(None, description="筛选特定语言"),
    today_service: TodayService = Depends(get_today_service),
):
    """获取今日已处理文章列表（仅显示LLM处理完成的文章）"""
    try:
        return today_service.get_today_articles(
            page=page, size=size, source=source, language=language
        )
    except Exception as e:
        logger.error(f"获取今日文章失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取今日文章失败: {str(e)}")


@router.get("/stats", response_model=TodayStatsResponse)
async def get_today_stats(today_service: TodayService = Depends(get_today_service)):
    """获取今日统计信息（仅统计已处理文章）"""
    try:
        return today_service.get_today_stats()
    except Exception as e:
        logger.error(f"获取今日统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取今日统计失败: {str(e)}")


@router.get("/sources")
async def get_available_sources(
    today_service: TodayService = Depends(get_today_service),
):
    """获取可用的新闻源列表"""
    try:
        return {"sources": today_service.get_available_sources()}
    except Exception as e:
        logger.error(f"获取新闻源列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取新闻源列表失败: {str(e)}")


@router.get("/languages")
async def get_available_languages(
    today_service: TodayService = Depends(get_today_service),
):
    """获取今日文章的可用语言列表"""
    try:
        return {"languages": today_service.get_available_languages()}
    except Exception as e:
        logger.error(f"获取语言列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取语言列表失败: {str(e)}")


@router.post("/process")
async def process_today_articles(
    db: Session = Depends(get_db),
):
    """手动触发今日文章处理"""
    try:
        # Get unprocessed articles from today
        from datetime import datetime, timedelta
        from app.models.article import NewsArticle
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.fetched_at >= today_start)
            .filter(NewsArticle.llm_processing_status != "completed")
            .all()
        )
        
        return {
            "message": "文章处理功能开发中，当前仅返回统计信息",
            "found_articles": len(articles),
            "note": "需要实现文章获取和LLM处理功能"
        }
    except Exception as e:
        logger.error(f"处理今日文章失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理今日文章失败: {str(e)}")


@router.get("/llm/health", response_model=LLMHealthResponse)
async def get_llm_health():
    """获取 LLM 服务健康状态"""
    try:
        llm_mgr = get_llm_manager()
        health_results = await llm_mgr.health_check_all()

        return LLMHealthResponse(
            providers=health_results,
            active_providers=[p.value for p in llm_mgr.get_active_providers()],
            default_provider=llm_mgr.config.default_provider.value,
        )
    except Exception as e:
        logger.error(f"获取 LLM 健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取 LLM 健康状态失败: {str(e)}")
