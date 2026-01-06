"""
"今日"功能测试脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal
from app.models.article import NewsArticle, LLMProcessingStatus
from app.models.source import NewsSource
from app.core.llm_factory import get_llm_manager
from app.services.content_processor import ContentProcessorService
from app.services.today_service import TodayService
from datetime import datetime, date
import json


async def test_llm_manager():
    """测试LLM管理器"""
    print("=== 测试LLM管理器 ===")
    
    try:
        llm_manager = get_llm_manager()
        print(f"默认提供商: {llm_manager.config.default_provider.value}")
        print(f"活跃提供商: {[p.value for p in llm_manager.get_active_providers()]}")
        
        # 测试健康检查
        health = await llm_manager.health_check_all()
        print(f"健康检查结果: {health}")
        
        # 测试语言检测
        language = await llm_manager.detect_language("Hello, this is a test article.")
        print(f"语言检测结果: {language}")
        
        # 测试摘要生成
        content = "这是一篇测试文章的内容。人工智能技术正在快速发展，特别是大语言模型在各个领域都展现出了强大的能力。"
        summary = await llm_manager.summarize_content(content, target_length=100)
        print(f"摘要生成结果: {summary}")
        
        print("LLM管理器测试成功！")
        
    except Exception as e:
        print(f"LLM管理器测试失败: {e}")


async def test_content_processor():
    """测试内容处理器"""
    print("\n=== 测试内容处理器 ===")
    
    try:
        llm_manager = get_llm_manager()
        processor = ContentProcessorService(llm_manager)
        
        # 创建测试文章
        test_article = NewsArticle(
            id=999,
            title="Test Article: AI Technology Advances",
            content="Artificial intelligence technology is rapidly evolving. Large language models are showing great capabilities across various domains. Machine learning algorithms are becoming more sophisticated and efficient.",
            url="http://test.com/article/999",
            source_id=1
        )
        
        # 处理文章
        result = await processor.process_article_content(test_article)
        print(f"处理结果: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
        
        print("内容处理器测试成功！")
        
    except Exception as e:
        print(f"内容处理器测试失败: {e}")


def test_today_service():
    """测试今日服务"""
    print("\n=== 测试今日服务 ===")
    
    try:
        db = SessionLocal()
        llm_manager = get_llm_manager()
        processor = ContentProcessorService(llm_manager)
        today_service = TodayService(db, processor)
        
        # 测试获取今日统计
        stats = today_service.get_today_stats()
        print(f"今日统计: {stats}")
        
        # 测试获取今日文章
        articles_response = today_service.get_today_articles(page=1, size=5)
        print(f"今日文章数量: {articles_response.total}")
        print(f"返回文章数: {len(articles_response.articles)}")
        
        # 测试获取可用源
        sources = today_service.get_available_sources()
        print(f"可用新闻源: {len(sources)} 个")
        
        # 测试获取可用语言
        languages = today_service.get_available_languages()
        print(f"可用语言: {languages}")
        
        db.close()
        print("今日服务测试成功！")
        
    except Exception as e:
        print(f"今日服务测试失败: {e}")


def create_test_data():
    """创建测试数据"""
    print("\n=== 创建测试数据 ===")
    
    try:
        db = SessionLocal()
        
        # 创建测试新闻源
        test_source = db.query(NewsSource).filter(NewsSource.name == "测试新闻源").first()
        if not test_source:
            test_source = NewsSource(
                name="测试新闻源",
                url="http://test.com/rss",
                source_type="rss",
                is_active=True
            )
            db.add(test_source)
            db.commit()
            print("创建测试新闻源成功")
        
        # 创建测试文章
        test_articles = [
            {
                "title": "人工智能技术的最新进展",
                "content": "人工智能技术正在快速发展，大语言模型在各个领域展现出强大能力。机器学习算法变得更加复杂和高效。深度学习技术推动了计算机视觉、自然语言处理等领域的突破。",
                "url": "http://test.com/article/1"
            },
            {
                "title": "AI Technology Breakthrough in 2024",
                "content": "Artificial intelligence has made significant strides in 2024. Large language models continue to improve in reasoning capabilities. Machine learning applications are expanding across industries.",
                "url": "http://test.com/article/2"
            },
            {
                "title": "機械学習の新しい発展",
                "content": "機械学習技術は急速に進歩しています。深層学習アルゴリズムはより効率的になり、様々な分野で応用されています。人工知能の未来は明るいです。",
                "url": "http://test.com/article/3"
            }
        ]
        
        for i, article_data in enumerate(test_articles):
            existing = db.query(NewsArticle).filter(NewsArticle.url == article_data["url"]).first()
            if not existing:
                article = NewsArticle(
                    title=article_data["title"],
                    content=article_data["content"],
                    url=article_data["url"],
                    source_id=test_source.id,
                    published_at=datetime.now(),
                    llm_processing_status=LLMProcessingStatus.PENDING
                )
                db.add(article)
        
        db.commit()
        db.close()
        print("创建测试文章成功")
        
    except Exception as e:
        print(f"创建测试数据失败: {e}")


async def main():
    """主测试函数"""
    print("开始今日功能测试...")
    
    # 创建测试数据
    create_test_data()
    
    # 测试LLM管理器
    await test_llm_manager()
    
    # 测试内容处理器
    await test_content_processor()
    
    # 测试今日服务
    test_today_service()
    
    print("\n=== 所有测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
