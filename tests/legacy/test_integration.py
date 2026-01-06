"""
测试新闻抓取功能的端到端测试
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app
from app.services.source_service import SourceService
from app.services.article_service import ArticleService
from app.schemas.source import SourceCreate
from app.schemas.article import ArticleCreate


def test_create_source_and_article_workflow(db):
    """测试创建新闻源和文章的完整工作流"""
    source_service = SourceService(db)
    article_service = ArticleService(db)
    
    # 创建测试新闻源
    source_data = SourceCreate(
        name="Test RSS Feed",
        url="https://test.example.com/rss.xml",
        source_type="rss",
        is_active=True,
        fetch_interval=3600
    )
    
    db_source = source_service.create_source(source_data)
    assert db_source.id is not None
    assert db_source.name == "Test RSS Feed"
    
    # 创建测试文章
    article_data = ArticleCreate(
        title="Test Article",
        summary="This is a test article summary",
        url="https://test.example.com/article1",
        content="Full content of test article",
        source_id=db_source.id,
        author="Test Author",
        tags=["tech", "ai"],
        category="technology"
    )
    
    created_article = article_service.create_article(article_data)
    assert created_article.id is not None
    assert created_article.title == "Test Article"
    assert created_article.source_id == db_source.id
    
    # 验证可以检索文章
    retrieved_article = article_service.get_article(created_article.id)
    assert retrieved_article is not None
    assert retrieved_article.title == "Test Article"
    
    # 验证可以获取文章列表
    articles = article_service.get_articles()
    assert len(articles) > 0
    assert any(article.id == created_article.id for article in articles)


def test_api_endpoints_integration(client):
    """测试API端点的集成"""
    # 测试根端点
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to AI News"
    
    # 测试获取文章列表
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data
    
    # 测试获取新闻源列表
    response = client.get("/api/v1/sources/")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "total" in data
    
    # 测试搜索API
    response = client.get("/api/v1/search/?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data


def test_source_crud_operations(client):
    """测试新闻源的CRUD操作"""
    # 创建新闻源
    source_data = {
        "name": "Integration Test Source",
        "url": "https://integration-test.example.com/rss",
        "source_type": "rss",
        "is_active": True,
        "fetch_interval": 3600
    }
    
    response = client.post("/api/v1/sources/", json=source_data)
    assert response.status_code == 201
    created_source = response.json()
    source_id = created_source["id"]
    
    # 读取新闻源
    response = client.get(f"/api/v1/sources/{source_id}")
    assert response.status_code == 200
    source = response.json()
    assert source["name"] == source_data["name"]
    
    # 更新新闻源
    update_data = {
        "name": "Updated Integration Test Source",
        "url": "https://updated-integration-test.example.com/rss",
        "source_type": "rss",
        "is_active": False,
        "fetch_interval": 7200
    }
    
    response = client.put(f"/api/v1/sources/{source_id}", json=update_data)
    assert response.status_code == 200
    updated_source = response.json()
    assert updated_source["name"] == update_data["name"]
    assert updated_source["is_active"] == False
    
    # 删除新闻源
    response = client.delete(f"/api/v1/sources/{source_id}")
    assert response.status_code == 204
    
    # 验证已删除
    response = client.get(f"/api/v1/sources/{source_id}")
    assert response.status_code == 404
