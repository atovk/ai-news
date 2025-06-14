"""
手动抓取新闻脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import SessionLocal
from app.core.aggregator import NewsAggregator


async def fetch_news():
    """手动抓取新闻"""
    db = SessionLocal()
    try:
        print("Starting news aggregation...")
        aggregator = NewsAggregator(db)
        
        # 执行抓取
        result = await aggregator.fetch_all_sources()
        
        print(f"\nAggregation completed:")
        print(f"  - Total sources: {result['total_sources']}")
        print(f"  - Total articles fetched: {result['total_articles']}")
        print(f"  - New articles saved: {result['new_articles']}")
        
        if result['new_articles'] == 0:
            print("\nNo new articles were found. This could mean:")
            print("  - All articles are already in the database")
            print("  - News sources are not updating")
            print("  - There might be connectivity issues")
        
    except Exception as e:
        print(f"Error during news aggregation: {e}")
        return False
    finally:
        db.close()
    
    return True


def main():
    """主函数"""
    print("Manual news fetch script")
    print("========================")
    
    try:
        # 运行异步抓取
        success = asyncio.run(fetch_news())
        
        if success:
            print("\nNews fetch completed successfully!")
        else:
            print("\nNews fetch failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nNews fetch interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
