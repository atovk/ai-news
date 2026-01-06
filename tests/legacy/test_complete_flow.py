#!/usr/bin/env python3
"""
测试完整的AI新闻处理流程
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.tasks import AsyncTaskProcessor, background_task_manager, TaskDelay
from app.models.database import SessionLocal
from app.models.article import NewsArticle, LLMProcessingStatus
from sqlalchemy import func
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_complete_flow():
    """测试完整流程"""
    print("🔍 测试完整的AI新闻处理流程")
    print("=" * 50)
    
    # 1. 检查数据库中的文章状态
    db = SessionLocal()
    try:
        total_articles = db.query(NewsArticle).count()
        pending_articles = db.query(NewsArticle).filter(
            NewsArticle.llm_processing_status == LLMProcessingStatus.PENDING
        ).count()
        completed_articles = db.query(NewsArticle).filter(
            NewsArticle.llm_processing_status == LLMProcessingStatus.COMPLETED
        ).count()
        
        print(f"📊 文章统计:")
        print(f"  总文章数: {total_articles}")
        print(f"  待处理: {pending_articles}")
        print(f"  已完成: {completed_articles}")
        
        if pending_articles == 0:
            print("⚠️  没有待处理的文章，创建测试文章...")
            
            # 创建测试文章
            test_article = NewsArticle(
                title="Test AI News Article - 测试AI新闻文章",
                content="This is a test article content for AI processing. It contains English text that should be processed by LLM.",
                summary="Test summary",
                url=f"http://test.com/article-{total_articles + 1}",
                published_at=date.today(),
                llm_processing_status=LLMProcessingStatus.PENDING,
                source_id=1  # 假设source_id为1
            )
            db.add(test_article)
            db.commit()
            print(f"✅ 创建测试文章: ID {test_article.id}")
        
    finally:
        db.close()
    
    # 2. 测试后台任务管理器
    print(f"\n🔧 测试后台任务管理器:")
    status = background_task_manager.get_status()
    print(f"  运行状态: {status}")
    
    # 3. 测试异步处理器
    print(f"\n⚡ 测试异步处理器:")
    processor = AsyncTaskProcessor()
    
    # 获取统计
    stats = processor.get_processing_statistics()
    print(f"  处理统计: {stats}")
    
    # 手动处理一篇文章
    if stats["pending"] > 0:
        print(f"\n🔄 手动处理 1 篇文章:")
        result = await processor.process_pending_articles(1)
        print(f"  处理结果: {result}")
    
    # 4. 测试今日文章处理
    print(f"\n📅 测试今日文章处理:")
    today_result = await processor.process_today_articles()
    print(f"  今日处理结果: {today_result}")
    
    # 5. 测试后台管理功能
    print(f"\n🎛️  测试后台管理功能:")
    
    # 启动后台处理
    print("  启动后台处理...")
    background_task_manager.start()
    print(f"  状态: {background_task_manager.get_status()}")
    
    # 暂停10秒
    print("  暂停后台处理(10分钟)...")
    background_task_manager.pause(TaskDelay.TEN_MINUTES)
    print(f"  状态: {background_task_manager.get_status()}")
    
    # 恢复处理
    print("  恢复后台处理...")
    background_task_manager.resume()
    print(f"  状态: {background_task_manager.get_status()}")
    
    # 停止后台处理
    print("  停止后台处理...")
    background_task_manager.stop()
    print(f"  状态: {background_task_manager.get_status()}")
    
    print(f"\n✅ 完整流程测试完成！")


def main():
    """主函数"""
    try:
        asyncio.run(test_complete_flow())
        return 0
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
