#!/usr/bin/env python3
"""
启动完整的AI新闻系统，包括后台LLM处理
"""
import sys
import os
import asyncio
import signal
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.tasks import start_background_processing, stop_background_processing
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"接收到信号 {signum}，正在停止后台处理...")
    stop_background_processing()
    sys.exit(0)


def main():
    """主函数"""
    print("🚀 AI News System - 完整流程启动")
    print("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动后台LLM处理
        print("📝 启动后台LLM处理线程...")
        start_background_processing()
        print("✅ 后台LLM处理线程已启动")
        
        print("\n🔄 系统处理流程:")
        print("1. RSS抓取 → 保存原文章到数据库")
        print("2. 后台线程 → 自动发现未处理文章")
        print("3. LLM处理 → 生成中文摘要、翻译、分类")
        print("4. Today展示 → 显示处理完成的文章")
        
        print("\n📊 管理接口:")
        print("- GET  /api/v1/admin/processing/status     - 查看处理状态")
        print("- POST /api/v1/admin/processing/pause      - 暂停处理")
        print("- POST /api/v1/admin/processing/resume     - 恢复处理")
        print("- POST /api/v1/admin/processing/manual-run - 手动处理")
        
        print("\n💡 延迟选项:")
        print("- ten_minutes    - 延迟10分钟")
        print("- thirty_minutes - 延迟30分钟") 
        print("- one_hour       - 延迟1小时")
        print("- one_day        - 延迟1天")
        print("- forever        - 永久暂停")
        
        print("\n🌐 启动Web服务器...")
        print("使用命令: poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n✅ 系统启动完成！后台处理将持续运行...")
        print("按 Ctrl+C 停止")
        
        # 保持主进程运行
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 接收到停止信号...")
            
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1
    finally:
        print("🔄 正在停止后台处理...")
        stop_background_processing()
        print("✅ 系统已停止")
    
    return 0


if __name__ == "__main__":
    exit(main())
