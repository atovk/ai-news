"""
测试新闻源API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_sources():
    """测试获取新闻源列表"""
    response = client.get("/api/v1/sources/")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "total" in data
    assert isinstance(data["sources"], list)
    assert isinstance(data["total"], int)


def test_get_source_by_id():
    """测试根据ID获取新闻源"""
    # 首先获取源列表
    response = client.get("/api/v1/sources/")
    sources = response.json()["sources"]
    
    if sources:
        source_id = sources[0]["id"]
        response = client.get(f"/api/v1/sources/{source_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == source_id
        assert "name" in data
        assert "url" in data


def test_get_nonexistent_source():
    """测试获取不存在的新闻源"""
    response = client.get("/api/v1/sources/99999")
    assert response.status_code == 404


def test_create_source():
    """测试创建新闻源"""
    source_data = {
        "name": "Test Source",
        "url": "https://test.example.com/rss",
        "source_type": "rss",
        "is_active": True,
        "fetch_interval": 3600
    }
    
    response = client.post("/api/v1/sources/", json=source_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == source_data["name"]
    assert data["url"] == source_data["url"]
    assert "id" in data


def test_update_source():
    """测试更新新闻源"""
    # 首先创建一个新闻源
    source_data = {
        "name": "Test Source for Update",
        "url": "https://test-update.example.com/rss",
        "source_type": "rss",
        "is_active": True,
        "fetch_interval": 3600
    }
    
    create_response = client.post("/api/v1/sources/", json=source_data)
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]
    
    # 更新新闻源
    update_data = {
        "name": "Updated Test Source",
        "url": "https://updated.example.com/rss",
        "source_type": "rss",
        "is_active": False,
        "fetch_interval": 7200
    }
    
    response = client.put(f"/api/v1/sources/{source_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["is_active"] == update_data["is_active"]


def test_delete_source():
    """测试删除新闻源"""
    # 首先创建一个新闻源
    source_data = {
        "name": "Test Source for Delete",
        "url": "https://test-delete.example.com/rss",
        "source_type": "rss",
        "is_active": True,
        "fetch_interval": 3600
    }
    
    create_response = client.post("/api/v1/sources/", json=source_data)
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]
    
    # 删除新闻源
    response = client.delete(f"/api/v1/sources/{source_id}")
    assert response.status_code == 204
    
    # 验证已删除
    get_response = client.get(f"/api/v1/sources/{source_id}")
    assert get_response.status_code == 404
