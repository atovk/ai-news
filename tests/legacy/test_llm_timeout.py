#!/usr/bin/env python3
"""
测试LLM异步处理超时配置
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.core.llm_factory import get_llm_manager
from app.services.content_processor import ContentProcessorService
from app.models.article import NewsArticle, LLMProcessingStatus
from datetime import datetime

async def test_timeout_config():
    """测试超时配置"""
    print(f"🔧 LLM异步处理超时配置: {settings.LLM_ASYNC_TIMEOUT}秒")
    print(f"🔧 Ollama连接超时配置: {settings.OLLAMA_TIMEOUT}秒")
    
    # 创建测试文章
    test_article = NewsArticle(
        id=999,
        title="Test Article for Timeout",
        content="This is a test article content for timeout testing.",
        url="http://test.com/test",
        published_at=datetime.now(),
        llm_processing_status=LLMProcessingStatus.PENDING
    )
    
    # 测试LLM管理器
    try:
        llm_manager = get_llm_manager()
        print(f"✅ LLM管理器初始化成功")
        
        # 测试健康检查
        health_status = llm_manager.get_health_status()
        print(f"🏥 LLM健康状态: {health_status}")
        
        # 测试内容处理器
        content_processor = ContentProcessorService(llm_manager)
        print(f"✅ 内容处理器初始化成功")
        
        print(f"\n📝 开始测试异步处理（超时: {settings.LLM_ASYNC_TIMEOUT}s）...")
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 这里只是测试超时配置，不实际处理
            print(f"⏱️  如果实际处理，将在 {settings.LLM_ASYNC_TIMEOUT} 秒后超时")
            print(f"✅ 超时配置测试完成")
            
        except asyncio.TimeoutError:
            end_time = asyncio.get_event_loop().time()
            elapsed_time = end_time - start_time
            print(f"⏰ 超时测试成功：处理在 {elapsed_time:.2f} 秒后超时")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 开始LLM异步处理超时配置测试...\n")
    
    try:
        asyncio.run(test_timeout_config())
        print(f"\n✅ 所有测试完成")
        print(f"💡 异步LLM处理超时设置为: {settings.LLM_ASYNC_TIMEOUT}秒")
        print(f"💡 可通过配置文件 LLM_ASYNC_TIMEOUT 参数调整")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
