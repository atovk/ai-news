"""
种子数据导入脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import SessionLocal
from app.services.source_service import SourceService
from app.services.category_service import CategoryService
from app.schemas.source import SourceCreate


def get_default_news_sources():
    """获取默认新闻源配置"""
    return [
        {
            "name": "AI News",
            "url": "https://artificialintelligence-news.com/feed/",
            "source_type": "rss",
            "is_active": True,
            "fetch_interval": 3600
        },
        {
            "name": "VentureBeat AI",
            "url": "https://venturebeat.com/ai/feed/",
            "source_type": "rss",
            "is_active": True,
            "fetch_interval": 3600
        },
        {
            "name": "MIT Technology Review AI",
            "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
            "source_type": "rss",
            "is_active": True,
            "fetch_interval": 7200
        },
        {
            "name": "OpenAI Blog",
            "url": "https://openai.com/blog/rss.xml",
            "source_type": "rss",
            "is_active": True,
            "fetch_interval": 7200
        },
        {
            "name": "Google AI Blog",
            "url": "https://ai.googleblog.com/feeds/posts/default",
            "source_type": "rss",
            "is_active": True,
            "fetch_interval": 7200
        },
        {
            "name": "Towards Data Science",
            "url": "https://towardsdatascience.com/feed",
            "source_type": "rss",
            "is_active": True,
            "fetch_interval": 3600
        }
    ]


def import_news_sources():
    """导入新闻源"""
    db = SessionLocal()
    try:
        source_service = SourceService(db)
        sources_data = get_default_news_sources()
        
        imported_count = 0
        skipped_count = 0
        
        for source_data in sources_data:
            try:
                # 检查是否已存在相同URL的源
                existing_sources = source_service.get_sources()
                existing_urls = [str(source.url) for source in existing_sources]
                
                if source_data["url"] in existing_urls:
                    print(f"Skipping existing source: {source_data['name']}")
                    skipped_count += 1
                    continue
                
                # 创建新源
                source_create = SourceCreate(**source_data)
                new_source = source_service.create_source(source_create)
                print(f"Imported source: {new_source.name}")
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing source {source_data['name']}: {e}")
                continue
        
        print(f"\nImport completed:")
        print(f"  - Imported: {imported_count} sources")
        print(f"  - Skipped: {skipped_count} sources")
        
        return imported_count > 0
        
    except Exception as e:
        print(f"Error importing news sources: {e}")
        return False
    finally:
        db.close()


def import_categories():
    """导入默认分类"""
    db = SessionLocal()
    try:
    success = True
    
    # 导入分类
    print("\n=== Importing Categories ===")
    if not import_categories():
        success = False
        print("Categories import failed!")
    
    # 导入新闻源
    print("\n=== Importing News Sources ===")
    if not import_news_sources():
        success = False
        print("News sources import failed!")
    
    if success:
        print("\n✅ Seed data import completed successfully!")
        print("You can now fetch news with the aggregator.")
    else:
        print("\n❌ nCategories ensured:")
        for cat in categories:
            print(f"  - {cat.name}: {cat.description}")
        
        return True
        
    except Exception as e:
        print(f"Error importing categories: {e}")
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("Importing seed data...")
    
    # 导入新闻源
    if import_news_sources():
        print("\nSeed data import completed successfully!")
        print("You can now fetch news with the aggregator.")
    else:
        print("\nSeed data import failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
