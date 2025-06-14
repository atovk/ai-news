"""
新闻聚合服务
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.source import NewsSource
from app.models.article import NewsArticle
from app.services.article_service import ArticleService
from app.services.source_service import SourceService
from app.utils.rss_parser import RSSParser
from app.config import settings


class NewsAggregator:
    """新闻聚合器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.article_service = ArticleService(db)
        self.source_service = SourceService(db)
    
    async def fetch_from_source(self, source: NewsSource) -> List[Dict[str, Any]]:
        """从单个新闻源获取新闻"""
        try:
            if source.source_type == "rss":
                return await self._fetch_rss_articles(source)
            else:
                print(f"Unsupported source type: {source.source_type}")
                return []
        except Exception as e:
            print(f"Error fetching from source {source.name}: {e}")
            return []
    
    async def _fetch_rss_articles(self, source: NewsSource) -> List[Dict[str, Any]]:
        """从RSS源获取文章"""
        async with RSSParser() as parser:
            articles = await parser.parse_rss_url(source.url)
            
            # 添加source_id到每篇文章
            for article in articles:
                article['source_id'] = source.id
            
            return articles
    
    async def fetch_all_sources(self) -> Dict[str, Any]:
        """从所有活跃的新闻源获取新闻"""
        sources = self.source_service.get_sources(active_only=True)
        
        if not sources:
            return {"total_sources": 0, "total_articles": 0, "new_articles": 0}
        
        print(f"Starting to fetch from {len(sources)} sources...")
        
        # 并发获取所有源的新闻
        tasks = []
        for source in sources:
            task = self.fetch_from_source(source)
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_articles = 0
        new_articles = 0
        
        # 处理结果
        for i, result in enumerate(results):
            source = sources[i]
            
            if isinstance(result, Exception):
                print(f"Error processing source {source.name}: {result}")
                continue
            
            if not result:
                continue
            
            print(f"Fetched {len(result)} articles from {source.name}")
            total_articles += len(result)
            
            # 保存文章到数据库
            saved_count = await self._save_articles(result)
            new_articles += saved_count
            
            # 更新源的最后抓取时间
            self.source_service.update_last_fetch_time(source.id)
        
        return {
            "total_sources": len(sources),
            "total_articles": total_articles,
            "new_articles": new_articles
        }
    
    async def _save_articles(self, articles: List[Dict[str, Any]]) -> int:
        """保存文章到数据库"""
        saved_count = 0
        
        for article_data in articles:
            try:
                # 检查文章是否已存在
                existing_article = self.article_service.get_article_by_url(article_data['url'])
                if existing_article:
                    continue
                
                # 创建新文章 (状态自动设为PENDING，等待LLM处理)
                from app.schemas.article import ArticleCreate
                article_create = ArticleCreate(**article_data)
                new_article = self.article_service.create_article(article_create)
                saved_count += 1
                
                # 记录新文章，便于后续处理
                print(f"新文章已保存: {new_article.title[:50]}... (ID: {new_article.id})")
                
            except Exception as e:
                print(f"Error saving article {article_data.get('title', 'Unknown')}: {e}")
                continue
        
        # 如果有新文章保存，记录信息
        if saved_count > 0:
            print(f"本次共保存 {saved_count} 篇新文章，等待后台LLM处理")
        
        return saved_count
    
    async def schedule_fetch_tasks(self):
        """调度抓取任务（这个方法在scheduler中调用）"""
        result = await self.fetch_all_sources()
        print(f"Scheduled fetch completed: {result}")
        return result
