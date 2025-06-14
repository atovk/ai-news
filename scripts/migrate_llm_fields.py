"""
添加 LLM 处理相关字段的数据库迁移脚本
"""
from sqlalchemy import text
from app.models.database import engine


def upgrade():
    """添加 LLM 处理相关字段"""
    
    with engine.connect() as connection:
        # 添加字段
        try:
            connection.execute(text("""
                ALTER TABLE news_articles 
                ADD COLUMN chinese_title TEXT;
            """))
            print("添加 chinese_title 字段成功")
        except Exception as e:
            print(f"添加 chinese_title 字段失败或已存在: {e}")
        
        try:
            connection.execute(text("""
                ALTER TABLE news_articles 
                ADD COLUMN llm_summary TEXT;
            """))
            print("添加 llm_summary 字段成功")
        except Exception as e:
            print(f"添加 llm_summary 字段失败或已存在: {e}")
        
        try:
            connection.execute(text("""
                ALTER TABLE news_articles 
                ADD COLUMN original_language VARCHAR(10);
            """))
            print("添加 original_language 字段成功")
        except Exception as e:
            print(f"添加 original_language 字段失败或已存在: {e}")
        
        try:
            connection.execute(text("""
                ALTER TABLE news_articles 
                ADD COLUMN llm_processed_at DATETIME;
            """))
            print("添加 llm_processed_at 字段成功")
        except Exception as e:
            print(f"添加 llm_processed_at 字段失败或已存在: {e}")
        
        try:
            connection.execute(text("""
                ALTER TABLE news_articles 
                ADD COLUMN llm_processing_status VARCHAR(20) DEFAULT 'pending';
            """))
            print("添加 llm_processing_status 字段成功")
        except Exception as e:
            print(f"添加 llm_processing_status 字段失败或已存在: {e}")
        
        # 添加索引
        try:
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_articles_today 
                ON news_articles(published_at, llm_processing_status);
            """))
            print("创建今日文章索引成功")
        except Exception as e:
            print(f"创建今日文章索引失败: {e}")
        
        try:
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_articles_published_at 
                ON news_articles(published_at);
            """))
            print("创建发布时间索引成功")
        except Exception as e:
            print(f"创建发布时间索引失败: {e}")
        
        connection.commit()


def downgrade():
    """移除 LLM 处理相关字段"""
    
    with engine.connect() as connection:
        # SQLite 不支持 DROP COLUMN，所以这里只是示例
        # 在生产环境中需要创建新表并迁移数据
        print("SQLite 不支持 DROP COLUMN，需要手动处理降级")


if __name__ == "__main__":
    print("开始数据库迁移...")
    upgrade()
    print("数据库迁移完成")
