"""
新闻聚合服务 - 从RSS源获取文章
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.article import NewsArticle
from app.models.source import NewsSource
from app.utils.rss_parser import UniversalRSSParser

logger = logging.getLogger(__name__)


class NewsAggregatorService:
    """新闻聚合服务 - 负责从RSS源获取文章"""
    
    def __init__(self, db: Session):
        self.db = db
        self.parser = UniversalRSSParser()
    
    async def fetch_all_sources(self) -> Dict[str, Any]:
        """从所有活跃的新闻源获取文章"""
        # 获取所有活跃源
        sources = self.db.query(NewsSource).filter(
            NewsSource.is_active == True
        ).all()
        
        if not sources:
            logger.warning("没有活跃的新闻源")
            return {
                "total_sources": 0,
                "total_fetched": 0,
                "sources_processed": [],
                "errors": []
            }
        
        logger.info(f"开始从 {len(sources)} 个新闻源获取文章")
        
        total_fetched = 0
        sources_processed = []
        errors = []
        
        # 逐个处理源（避免并发问题）
        for source in sources:
            try:
                # Check if we should fetch based on fetch_interval
                if source.last_fetch_time:
                    delta = datetime.utcnow() - source.last_fetch_time
                    interval_minutes = float(source.fetch_interval) if source.fetch_interval else 60.0
                    if delta.total_seconds() < interval_minutes * 60:
                        logger.debug(f"Skipping source {source.name}, last fetch was {delta.total_seconds()/60:.1f} min ago (interval: {interval_minutes} min)")
                        continue
                
                articles = await self.fetch_source(source)
                sources_processed.append({
                    "source_id": source.id,
                    "source_name": source.name,
                    "articles_fetched": len(articles)
                })
                total_fetched += len(articles)
                
                # 更新源的最后抓取时间
                source.last_fetch_time = datetime.utcnow()
                self.db.commit()
                
            except Exception as e:
                error_msg = f"从源 {source.name} 获取失败: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "total_sources": len(sources),
            "total_fetched": total_fetched,
            "sources_processed": sources_processed,
            "errors": errors
        }
    
    async def fetch_source(self, source: NewsSource) -> List[NewsArticle]:
        """从单个新闻源获取文章"""
        logger.info(f"开始获取源: {source.name} ({source.url})")
        
        try:
            # 解析RSS - parser会自动检测配置
            async with self.parser as parser:
                articles_data =  await parser.parse_rss_url(source.url)
            
            if not articles_data:
                logger.warning(f"源 {source.name} 没有返回文章")
                return []
            
            # 保存文章到数据库
            saved_articles = []
            for article_data in articles_data:
                article = self._create_article_from_data(article_data, source.id)
                if article:
                    saved_articles.append(article)
            
            logger.info(f"从源 {source.name} 成功获取 {len(saved_articles)} 篇文章")
            return saved_articles
            
        except Exception as e:
            logger.error(f"获取源 {source.name} 失败: {e}")
            raise
    
    def _create_article_from_data(
        self, 
        article_data: Dict[str, Any], 
        source_id: int
    ) -> Optional[NewsArticle]:
        """从RSS数据创建文章对象"""
        try:
            # 检查文章是否已存在（通过URL去重）
            existing = self.db.query(NewsArticle).filter(
                NewsArticle.url == article_data.get("url")
            ).first()
            
            if existing:
                logger.debug(f"文章已存在: {article_data.get('title')}")
                return None
            
            # Extract tags list
            tags_list = article_data.get("tags") or []
            
            # 创建新文章
            article = NewsArticle(
                title=article_data.get("title", "")[:500],  # 限制长度
                summary=article_data.get("summary", "")[:1000],
                content=article_data.get("content", ""),
                url=article_data.get("url", ""),
                source_id=source_id,
                author=article_data.get("author", "")[:100],
                published_at=article_data.get("published_at"),
                fetched_at=datetime.utcnow(),
                is_processed=False,
                llm_processing_status="PENDING",  # Use uppercase for enum
                tags=",".join(tags_list[:10])  # 限制标签数量，保持文本字段兼容
            )
            
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            
            # Link tags to article using TagService
            if tags_list:
                from app.services.tag_service import TagService
                tag_service = TagService(self.db)
                tag_service.link_tags_to_article(article, tags_list)
            
            logger.debug(f"保存新文章: {article.title}")
            return article
            
        except IntegrityError as e:
            # URL唯一性约束冲突
            self.db.rollback()
            logger.debug(f"文章URL重复: {article_data.get('url')}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建文章失败: {e}, 数据: {article_data.get('title')}")
            return None
