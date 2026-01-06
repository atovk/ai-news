import pytest
from fastapi.testclient import TestClient
from app.models import NewsArticle, NewsSource

@pytest.mark.integration
class TestArticles:
    """Articles API tests"""
    
    def test_get_articles_list(self, client: TestClient, db_session):
        """Test getting list of articles"""
        # Create some test/dummy articles
        source = NewsSource(name="Test Source", url="http://test.com")
        db_session.add(source)
        db_session.commit()
        
        article = NewsArticle(
            title="Test Article 1",
            url="http://test.com/1",
            source_id=source.id,
            view_count=10
        )
        db_session.add(article)
        db_session.commit()
        
        response = client.get("/api/v1/articles/")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert len(data["articles"]) >= 1
        assert "total" in data

    def test_get_article_detail(self, client: TestClient, db_session):
        """Test getting article detail"""
        # Setup data
        source = NewsSource(name="Detail Source", url="http://detail.com")
        db_session.add(source)
        db_session.commit()
        
        article = NewsArticle(
            title="Detail Article",
            url="http://detail.com/d",
            source_id=source.id,
            content="Some content",
            view_count=5
        )
        db_session.add(article)
        db_session.commit()
        
        response = client.get(f"/api/v1/articles/{article.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Detail Article"
        # Check if view count incremented (if implemented) or just returns 5
        assert data["view_count"] >= 5

    def test_get_article_not_found(self, client: TestClient):
        """Test getting non-existent article"""
        response = client.get("/api/v1/articles/999999")
        assert response.status_code == 404
