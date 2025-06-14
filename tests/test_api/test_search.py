"""
测试搜索API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_search_articles():
    """测试文章搜索"""
    response = client.get("/api/v1/search/?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data
    assert isinstance(data["articles"], list)
    assert isinstance(data["total"], int)


def test_search_empty_query():
    """测试空查询搜索"""
    response = client.get("/api/v1/search/?q=")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data


def test_search_with_filters():
    """测试带过滤器的搜索"""
    response = client.get("/api/v1/search/?q=test&category=technology&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data
    assert len(data["articles"]) <= 5


def test_search_pagination():
    """测试搜索分页"""
    response = client.get("/api/v1/search/?q=test&skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data
