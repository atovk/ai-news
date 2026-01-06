"""
今日功能服务层
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.article import NewsArticle, LLMProcessingStatus
from app.models.source import NewsSource
from app.schemas.today import TodayArticleView, TodayStatsResponse, TodayArticleListResponse
from app.services.content_processor import ContentProcessorService
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class TodayService:
    """
    今日功能服务
    
    专注于展示今日已经过后台LLM异步处理的文章。
    - 提供已处理文章的展示和筛选功能
    - 统计今日文章的处理状态
    - 支持按状态、来源、语言筛选
    - 后台异步处理由独立的任务队列负责
    """
    
    def __init__(self, db: Session, content_processor: ContentProcessorService):
        self.db = db
        self.content_processor = content_processor
    
    def get_today_articles(
        self,
        page: int = 1,
        size: int = 20,
        source: Optional[str] = None,
        language: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> TodayArticleListResponse:
        """
        Get today's articles.
        If user_id is provided, sort by personalization score (UserTagPreference).
        """
        from app.models.tag import ArticleTag, UserTagPreference
        
        # Base query
        query = self.db.query(NewsArticle).filter(
            func.date(NewsArticle.published_at) == date.today(),
            NewsArticle.llm_processing_status == LLMProcessingStatus.COMPLETED
        )

        if source:
            query = query.join(NewsSource).filter(NewsSource.name == source)
        if language:
            query = query.filter(NewsArticle.original_language == language)
            
        total = query.count()
        
        if user_id:
            # Personalization Sort
            
            # Fetch user tag preferences for this user
            user_prefs = self.db.query(UserTagPreference).filter(
                UserTagPreference.user_id == user_id
            ).all()
            pref_map = {p.tag_id: p.preference_score for p in user_prefs}
            
            # Use eager loading for article_tags
            from sqlalchemy.orm import joinedload
            query = query.options(joinedload(NewsArticle.article_tags))
            
            # Fetch ALL today's articles
            # Note: For larger datasets, we should do this scoring in SQL,
            # but for "Today's" view (usually <100 items), Python side is fine.
            all_candidates = query.all()
            
            if not all_candidates:
                return TodayArticleListResponse(total=0, page=page, size=size, articles=[])

            # Score articles
            scored_articles = []
            for art in all_candidates:
                score = 0
                for at in art.article_tags:
                    if at.tag_id in pref_map:
                        pref_val = pref_map[at.tag_id]
                        # (Pref - 5.0) * Relevance
                        score += (pref_val - 5.0) * (at.relevance_score or 1.0)
                
                scored_articles.append((art, score))
            
            # Sort by score desc, then published_at desc
            scored_articles.sort(key=lambda x: (x[1], x[0].published_at), reverse=True)
            
            # Paginate
            start = (page - 1) * size
            end = start + size
            articles = []
            rec_scores = {}
            
            for art, score in scored_articles[start:end]:
                articles.append(art)
                rec_scores[art.id] = score
            
        else:
            # Standard Sort - Optimization: Eager Load
            from sqlalchemy.orm import joinedload
            articles = query.options(joinedload(NewsArticle.article_tags))\
                           .order_by(NewsArticle.published_at.desc())\
                           .offset((page - 1) * size)\
                           .limit(size)\
                           .all()
            rec_scores = {}

        
        # 转换为视图模型
        article_views = []
        for article in articles:
            try:
                tags = []
                if article.tags:
                    try:
                        tags = json.loads(article.tags)
                    except json.JSONDecodeError:
                        tags = []
                
                article_view = TodayArticleView(
                    id=article.id,
                    original_title=article.title,
                    chinese_title=article.chinese_title or article.title,
                    url=article.url,
                    author=article.author,
                    source_name=article.source.name if article.source else "未知来源",
                    published_at=article.published_at,
                    llm_summary=article.llm_summary or "暂无摘要",
                    original_language=article.original_language or "unknown",
                    tags=tags,
                    is_recommended=(rec_scores.get(article.id, 0) > 0.5), # Simple threshold
                    recommendation_score=rec_scores.get(article.id, 0)
                )
                article_views.append(article_view)
            except Exception as e:
                logger.error(f"转换文章 {article.id} 为视图模型失败: {e}")
                continue
        
        return TodayArticleListResponse(
            total=total,
            page=page,
            size=size,
            articles=article_views
        )
    
    def get_today_stats(self) -> TodayStatsResponse:
        """获取今日统计信息（仅统计已处理文章相关信息）"""
        
        # 今日已完成处理的文章总数
        processed = self.db.query(NewsArticle).filter(
            func.date(NewsArticle.published_at) == date.today(),
            NewsArticle.llm_processing_status == LLMProcessingStatus.COMPLETED
        ).count()
        
        # 今日文章总数（所有状态）
        today_total = self.db.query(NewsArticle).filter(
            func.date(NewsArticle.published_at) == date.today()
        ).count()
        
        # 语言分布统计（仅已处理文章）
        language_stats = self.db.query(
            NewsArticle.original_language,
            func.count(NewsArticle.id).label('count')
        ).filter(
            func.date(NewsArticle.published_at) == date.today(),
            NewsArticle.llm_processing_status == LLMProcessingStatus.COMPLETED
        ).group_by(NewsArticle.original_language).all()
        
        language_distribution = {}
        for lang, count in language_stats:
            language_distribution[lang or "unknown"] = count
        
        return TodayStatsResponse(
            today_total=today_total,
            processed=processed,
            processing=0,  # C端不显示处理中状态
            pending=0,     # C端不显示待处理状态
            failed=0,      # C端不显示失败状态
            language_distribution=language_distribution
        )
    
    async def process_today_pending_articles(self, limit: int = 50) -> Dict[str, Any]:
        """处理今日待处理文章"""
        
        # 获取待处理文章
        pending_articles = self.db.query(NewsArticle).filter(
            func.date(NewsArticle.published_at) == date.today(),
            NewsArticle.llm_processing_status == LLMProcessingStatus.PENDING
        ).limit(limit).all()
        
        if not pending_articles:
            return {
                "message": "没有待处理的文章",
                "processed_count": 0
            }
        
        # 批量处理
        processed_count = 0
        failed_count = 0
        
        for article in pending_articles:
            try:
                # 更新状态为处理中
                article.llm_processing_status = LLMProcessingStatus.PROCESSING
                self.db.commit()
                
                # 处理文章
                result = await self.content_processor.process_article_content(article)
                
                # 更新文章信息
                if result.get("llm_processing_status") == LLMProcessingStatus.COMPLETED:
                    article.chinese_title = result.get("chinese_title")
                    article.llm_summary = result.get("llm_summary")
                    article.original_language = result.get("original_language")
                    article.llm_processed_at = result.get("llm_processed_at")
                    article.llm_processing_status = LLMProcessingStatus.COMPLETED
                    
                    # 更新关键词和分类
                    if result.get("keywords"):
                        article.tags = json.dumps(result["keywords"], ensure_ascii=False)
                    if result.get("category"):
                        article.category = result["category"]
                    
                    processed_count += 1
                else:
                    article.llm_processing_status = LLMProcessingStatus.FAILED
                    failed_count += 1
                
                self.db.commit()
                
            except Exception as e:
                logger.error(f"处理文章 {article.id} 失败: {e}")
                article.llm_processing_status = LLMProcessingStatus.FAILED
                self.db.commit()
                failed_count += 1
        
        return {
            "message": f"处理完成，成功: {processed_count}, 失败: {failed_count}",
            "processed_count": processed_count,
            "failed_count": failed_count
        }

    def start_batch_processing(self) -> Optional[str]:
        """启动批量处理任务 - 返回任务ID"""
        # 这里可以实现异步任务队列，比如使用Celery
        # 目前返回None表示同步处理
        logger.info("启动今日文章批量处理任务")
        return None

    def get_available_sources(self) -> List[Dict[str, str]]:
        """获取可用的新闻源列表"""
        sources = self.db.query(NewsSource).filter(NewsSource.is_active == True).all()
        return [{"name": source.name, "url": source.url} for source in sources]
    
    def get_available_languages(self) -> List[str]:
        """获取今日文章的可用语言列表"""
        languages = self.db.query(NewsArticle.original_language).filter(
            func.date(NewsArticle.published_at) == date.today(),
            NewsArticle.llm_processing_status == LLMProcessingStatus.COMPLETED,
            NewsArticle.original_language.isnot(None)
        ).distinct().all()
        
        return [lang[0] for lang in languages if lang[0]]
