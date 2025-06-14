"""
测试服务层功能
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.article_service import ArticleService
from app.services.source_service import SourceService
from app.schemas.article import ArticleCreate
from app.schemas.source import SourceCreate


class TestArticleService:
    """测试文章服务"""
    
    def test_get_articles(self):
        """测试获取文章列表"""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        service = ArticleService(mock_db)
        articles = service.get_articles()
        
        assert articles == []
        mock_db.query.assert_called_once()
    
    def test_get_article_by_url(self):
        """测试通过URL获取文章"""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        service = ArticleService(mock_db)
        article = service.get_article_by_url("https://test.com/article")
        
        assert article is None
        mock_db.query.assert_called_once()


class TestSourceService:
    """测试新闻源服务"""
    
    def test_get_sources(self):
        """测试获取新闻源列表"""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        service = SourceService(mock_db)
        sources = service.get_sources()
        
        assert sources == []
        mock_db.query.assert_called_once()
    
    def test_create_source(self):
        """测试创建新闻源"""
        mock_db = Mock()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        service = SourceService(mock_db)
        source_data = SourceCreate(
            name="Test Source",
            url="https://test.example.com/rss",
            source_type="rss",
            is_active=True,
            fetch_interval=3600
        )
        
        result = service.create_source(source_data)
        
        # Check that the result is a NewsSource object
        assert result is not None
        assert result.name == "Test Source"
        assert result.url == "https://test.example.com/rss"
        assert result.source_type == "rss"
        assert result.is_active == True
        assert result.fetch_interval == 3600
        
        # Check that database operations were called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
