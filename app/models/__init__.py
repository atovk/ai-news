"""
Database models package
"""
from app.models.database import Base, get_db, SessionLocal, engine
from app.models.article import NewsArticle, LLMProcessingStatus
from app.models.source import NewsSource
from app.models.category import Category
from app.models.user import User
from app.models.tag import Tag, ArticleTag, UserTagPreference
from app.models.interaction import (
    ReadingHistory,
    Favorite,
    AIPromptTemplate,
    AggregatedTopic,
    TopicArticle
)

__all__ = [
    "Base",
    "get_db",
    "SessionLocal",
    "engine",
    "NewsArticle",
    "LLMProcessingStatus",
    "NewsSource",
    "Category",
    "User",
    "Tag",
    "ArticleTag",
    "UserTagPreference",
    "ReadingHistory",
    "Favorite",
    "AIPromptTemplate",
    "AggregatedTopic",
    "TopicArticle",
]
