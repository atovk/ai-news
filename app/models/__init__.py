"""
数据库模型
"""
from app.models.database import Base, SessionLocal, get_db
from app.models.source import NewsSource
from app.models.article import NewsArticle
from app.models.category import Category

# 确保所有模型都被导入，以便SQLAlchemy能够正确处理关系
__all__ = ["Base", "SessionLocal", "get_db", "NewsSource", "NewsArticle", "Category"]
