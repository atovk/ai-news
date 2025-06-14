"""
文章API测试
"""
import pytest
from fastapi.testclient import TestClient


def test_get_articles(client: TestClient):
    """测试获取文章列表"""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "articles" in data


def test_health_check(client: TestClient):
    """测试健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
