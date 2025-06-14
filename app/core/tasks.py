"""
异步处理任务模块 - 完整的后台LLM处理流程
"""
import asyncio
import threading
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import SessionLocal
from app.models.article import NewsArticle, LLMProcessingStatus
from app.services.content_processor import ContentProcessorService
from app.core.llm_factory import get_llm_manager
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class TaskDelay(Enum):
    """任务延迟选项"""
    NO_DELAY = 0
    TEN_MINUTES = 600  # 10分钟
    THIRTY_MINUTES = 1800  # 30分钟
    ONE_HOUR = 3600  # 1小时
    ONE_DAY = 86400  # 1天
    FOREVER = -1  # 永远暂停


class BackgroundTaskManager:
    """后台任务管理器"""
    
    def __init__(self):
        self._is_running = False
        self._is_paused = False
        self._delay_until = None
        self._worker_thread = None
        self._stop_event = threading.Event()
        self.content_processor = None
        
    def start(self):
        """启动后台处理线程"""
        if self._is_running:
            logger.warning("后台处理线程已在运行")
            return
            
        self._is_running = True
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._background_worker, daemon=True)
        self._worker_thread.start()
        logger.info("后台LLM处理线程已启动")
        
    def stop(self):
        """停止后台处理线程"""
        if not self._is_running:
            return
            
        self._is_running = False
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("后台LLM处理线程已停止")
        
    def pause(self, delay: TaskDelay = TaskDelay.FOREVER):
        """暂停处理"""
        if delay == TaskDelay.FOREVER:
            self._is_paused = True
            self._delay_until = None
            logger.info("后台处理已永久暂停")
        elif delay == TaskDelay.NO_DELAY:
            self._is_paused = False
            self._delay_until = None
            logger.info("后台处理已恢复")
        else:
            self._delay_until = datetime.now() + timedelta(seconds=delay.value)
            self._is_paused = True
            logger.info(f"后台处理已暂停至 {self._delay_until}")
    
    def resume(self):
        """恢复处理"""
        self._is_paused = False
        self._delay_until = None
        logger.info("后台处理已恢复")
        
    def get_status(self) -> Dict[str, Any]:
        """获取处理状态"""
        return {
            "is_running": self._is_running,
            "is_paused": self._is_paused,
            "delay_until": self._delay_until.isoformat() if self._delay_until else None,
            "thread_alive": self._worker_thread.is_alive() if self._worker_thread else False
        }
        
    def _background_worker(self):
        """后台工作线程"""
        logger.info("后台LLM处理工作线程开始运行")
        
        while not self._stop_event.is_set():
            try:
                # 检查是否需要暂停
                if self._should_pause():
                    time.sleep(30)  # 暂停时每30秒检查一次
                    continue
                    
                # 初始化内容处理器（延迟初始化）
                if self.content_processor is None:
                    self.content_processor = ContentProcessorService(get_llm_manager())
                    
                # 执行处理任务
                asyncio.run(self._process_articles_batch())
                
                # 等待一段时间后继续
                time.sleep(60)  # 每分钟检查一次新文章
                
            except Exception as e:
                logger.error(f"后台处理线程错误: {e}")
                time.sleep(30)  # 出错后等待30秒
                
        logger.info("后台LLM处理工作线程已退出")
        
    def _should_pause(self) -> bool:
        """检查是否应该暂停"""
        if self._is_paused:
            if self._delay_until is None:
                return True  # 永久暂停
            elif datetime.now() < self._delay_until:
                return True  # 延迟未到
            else:
                # 延迟时间已到，自动恢复
                self._is_paused = False
                self._delay_until = None
                logger.info("延迟时间已到，自动恢复后台处理")
                return False
        return False
        
    async def _process_articles_batch(self):
        """处理一批文章"""
        processor = AsyncTaskProcessor()
        result = await processor.process_pending_articles()
        if result["processed_count"] > 0:
            logger.info(f"后台处理完成: 成功 {result['processed_count']}, 失败 {result['failed_count']}")


class AsyncTaskProcessor:
    """异步任务处理器"""
    
    def __init__(self):
        self.content_processor = ContentProcessorService(get_llm_manager())
    
    async def process_pending_articles(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """处理待处理的文章"""
        if limit is None:
            limit = settings.BATCH_PROCESS_SIZE
            
        db = SessionLocal()
        try:
            # 获取待处理文章
            pending_articles = db.query(NewsArticle).filter(
                NewsArticle.llm_processing_status == LLMProcessingStatus.PENDING
            ).limit(limit).all()
            
            if not pending_articles:
                return {
                    "message": "没有待处理的文章",
                    "processed_count": 0,
                    "failed_count": 0
                }
            
            logger.info(f"开始处理 {len(pending_articles)} 篇待处理文章")
            
            processed_count = 0
            failed_count = 0
            
            for article in pending_articles:
                try:
                    # 更新状态为处理中
                    article.llm_processing_status = LLMProcessingStatus.PROCESSING
                    db.commit()
                    
                    # 使用内容处理器处理文章
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
                        
                        db.commit()
                        processed_count += 1
                        logger.info(f"文章 {article.id} 处理成功")
                        
                    else:
                        article.llm_processing_status = LLMProcessingStatus.FAILED
                        db.commit()
                        failed_count += 1
                        logger.error(f"文章 {article.id} 处理失败: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    logger.error(f"处理文章 {article.id} 时发生异常: {e}")
                    article.llm_processing_status = LLMProcessingStatus.FAILED
                    db.commit()
                    failed_count += 1
            
            return {
                "message": f"批量处理完成，成功: {processed_count}, 失败: {failed_count}",
                "processed_count": processed_count,
                "failed_count": failed_count
            }
            
        finally:
            db.close()
    
    async def process_today_articles(self) -> Dict[str, Any]:
        """专门处理今日的文章"""
        db = SessionLocal()
        try:
            # 获取今日待处理文章
            today_pending = db.query(NewsArticle).filter(
                func.date(NewsArticle.published_at) == date.today(),
                NewsArticle.llm_processing_status == LLMProcessingStatus.PENDING
            ).all()
            
            if not today_pending:
                return {
                    "message": "今日没有待处理的文章",
                    "processed_count": 0,
                    "failed_count": 0
                }
            
            # 使用批量处理
            return await self.process_pending_articles(len(today_pending))
            
        finally:
            db.close()
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        db = SessionLocal()
        try:
            total = db.query(NewsArticle).count()
            pending = db.query(NewsArticle).filter(
                NewsArticle.llm_processing_status == LLMProcessingStatus.PENDING
            ).count()
            processing = db.query(NewsArticle).filter(
                NewsArticle.llm_processing_status == LLMProcessingStatus.PROCESSING
            ).count()
            completed = db.query(NewsArticle).filter(
                NewsArticle.llm_processing_status == LLMProcessingStatus.COMPLETED
            ).count()
            failed = db.query(NewsArticle).filter(
                NewsArticle.llm_processing_status == LLMProcessingStatus.FAILED
            ).count()
            
            return {
                "total_articles": total,
                "pending": pending,
                "processing": processing,
                "completed": completed,
                "failed": failed,
                "completion_rate": round(completed / total * 100, 2) if total > 0 else 0
            }
            
        finally:
            db.close()


# 全局任务管理器实例
background_task_manager = BackgroundTaskManager()


# 便利函数
def start_background_processing():
    """启动后台处理"""
    background_task_manager.start()


def stop_background_processing():
    """停止后台处理"""
    background_task_manager.stop()


def pause_background_processing(delay: TaskDelay = TaskDelay.FOREVER):
    """暂停后台处理"""
    background_task_manager.pause(delay)


def resume_background_processing():
    """恢复后台处理"""
    background_task_manager.resume()


def get_background_processing_status():
    """获取后台处理状态"""
    return background_task_manager.get_status()
