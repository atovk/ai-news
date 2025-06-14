"""
数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import engine, Base
from app.config import settings


def create_data_directories():
    """创建数据目录"""
    data_dir = Path("data")
    database_dir = data_dir / "database"
    logs_dir = data_dir / "logs"
    cache_dir = data_dir / "cache"
    
    # 创建目录
    database_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Created data directories:")
    print(f"  - {database_dir}")
    print(f"  - {logs_dir}")
    print(f"  - {cache_dir}")


def create_database_tables():
    """创建数据库表"""
    try:
        # 导入所有模型以确保它们被注册到Base.metadata
        from app.models.source import NewsSource
        from app.models.article import NewsArticle
        from app.models.category import Category
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # 显示创建的表
        print("Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print(f"Initializing {settings.APP_NAME} database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # 创建数据目录
    create_data_directories()
    
    # 创建数据库表
    if create_database_tables():
        print("\nDatabase initialization completed successfully!")
        print("You can now start the application with: make run")
    else:
        print("\nDatabase initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
