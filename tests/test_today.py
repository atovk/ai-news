
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestToday:
    """Today API tests"""
    
    def test_get_today_articles(self, client: TestClient):
        """Test getting today's articles"""
        response = client.get("/api/v1/today/articles")
        # Even if empty, should be 200
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert isinstance(data["articles"], list)

    def test_get_today_stats(self, client: TestClient):
        """Test getting today's stats"""
        response = client.get("/api/v1/today/stats")
        assert response.status_code == 200
        data = response.json()
        assert "today_total" in data
