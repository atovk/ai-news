"""
内容处理服务 - 使用策略模式集成 LLM 能力
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from app.services.llm_manager import LLMServiceManager
from app.models.article import NewsArticle, LLMProcessingStatus
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ContentProcessorService:
    """内容处理服务 - 使用策略模式集成 LLM 能力"""
    
    def __init__(self, llm_manager: LLMServiceManager):
        self.llm_manager = llm_manager
    
    async def process_article_content(self, article: NewsArticle) -> Dict[str, Any]:
        """综合处理文章内容"""
        try:
            # 使用超时包装整个处理过程
            return await asyncio.wait_for(
                self._process_article_content_internal(article),
                timeout=settings.LLM_ASYNC_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"文章 {article.id} 处理超时 ({settings.LLM_ASYNC_TIMEOUT}s)")
            return {
                "llm_processing_status": LLMProcessingStatus.FAILED,
                "error": f"处理超时 ({settings.LLM_ASYNC_TIMEOUT}s)"
            }
        except Exception as e:
            logger.error(f"处理文章内容失败: {e}")
            return {
                "llm_processing_status": LLMProcessingStatus.FAILED,
                "error": str(e)
            }
    
    async def _process_article_content_internal(self, article: NewsArticle) -> Dict[str, Any]:
        """内部处理方法 - 不包含超时包装"""
    async def _process_article_content_internal(self, article: NewsArticle) -> Dict[str, Any]:
        """内部处理方法 - 不包含超时包装"""
        content = article.content or article.summary or ""
        title = article.title or ""
        
        if not content.strip():
            raise ValueError("文章内容为空")
        
        # 检测语言
        original_language = await self.llm_manager.detect_language(f"{title} {content}")
        
        # 翻译标题
        chinese_title = await self.llm_manager.translate_to_chinese(title, original_language)
        
        # 生成摘要
        llm_summary = await self.llm_manager.summarize_content(content, target_length=400)
        
        # 提取关键词
        keywords = await self.llm_manager.extract_keywords(content, max_keywords=5)
        
        categories = ["科技", "财经", "体育", "娱乐", "政治", "社会", "教育", "健康", "其他"]
        raw_category = await self.llm_manager.categorize_article(title, content, categories)
        
        # Clean up category - try to find one of the valid categories in the output
        category = "其他"
        for cat in categories:
            if cat in raw_category:
                category = cat
                break
        
        return {
            "chinese_title": chinese_title,
            "llm_summary": llm_summary,
            "original_language": original_language,
            "keywords": keywords,
            "category": category,
            "llm_processed_at": datetime.utcnow(),
            "llm_processing_status": LLMProcessingStatus.COMPLETED
        }
    
    async def batch_process_articles(self, articles: List[NewsArticle]) -> List[Dict[str, Any]]:
        """批量处理文章 - 带超时控制"""
        try:
            # 批量处理超时 = 单篇超时 * 文章数量
            batch_timeout = settings.LLM_ASYNC_TIMEOUT * len(articles)
            return await asyncio.wait_for(
                self._batch_process_articles_internal(articles),
                timeout=batch_timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"批量处理 {len(articles)} 篇文章超时 ({settings.LLM_ASYNC_TIMEOUT * len(articles)}s)")
            # 返回失败状态的结果
            return [
                {
                    "article_id": article.id,
                    "llm_processing_status": LLMProcessingStatus.FAILED,
                    "error": f"批量处理超时 ({settings.LLM_ASYNC_TIMEOUT * len(articles)}s)"
                }
                for article in articles
            ]
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            return [
                {
                    "article_id": article.id,
                    "llm_processing_status": LLMProcessingStatus.FAILED,
                    "error": str(e)
                }
                for article in articles
            ]
    
    async def _batch_process_articles_internal(self, articles: List[NewsArticle]) -> List[Dict[str, Any]]:
        """内部批量处理方法"""
        results = []
        for article in articles:
            result = await self.process_article_content(article)
            result["article_id"] = article.id
            results.append(result)
        return results
