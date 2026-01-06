
import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.article import NewsArticle, LLMProcessingStatus
from app.models.tag import Tag, ArticleTag, UserTagPreference
from app.models.source import NewsSource
from app.models.user import User
from app.core.security import AuthService

@pytest.fixture
def phase3_data(db_session: Session):
    # Create Source
    source = NewsSource(name="TechDaily", url="https://techdaily.com", is_active=True)
    db_session.add(source)
    db_session.commit()
    
    # Create Tags
    tag_ai = Tag(name="artificial intelligence")
    tag_python = Tag(name="python")
    tag_rust = Tag(name="rust")
    db_session.add_all([tag_ai, tag_python, tag_rust])
    db_session.commit()
    
    # Create Today's Articles (Completed)
    # Article 1: AI & Python (More relevant to AI)
    art1 = NewsArticle(
        title="AI in Python",
        url="https://example.com/1",
        published_at=datetime.now(),
        fetched_at=datetime.now(),
        source_id=source.id,
        is_processed=True,
        llm_processing_status=LLMProcessingStatus.COMPLETED,
        llm_summary="Summary 1",
        original_language="en",
        chinese_title="Python AI"
    )
    
    # Article 2: Rust (No AI)
    art2 = NewsArticle(
        title="Rust 2.0 Released",
        url="https://example.com/2",
        published_at=datetime.now() - timedelta(hours=1), # Older
        fetched_at=datetime.now(),
        source_id=source.id,
        is_processed=True,
        llm_processing_status=LLMProcessingStatus.COMPLETED,
        llm_summary="Summary 2",
        original_language="en",
        chinese_title="Rust 2.0"
    )

    # Article 3: AI (Newest)
    art3 = NewsArticle(
        title="Future of AI",
        url="https://example.com/3",
        published_at=datetime.now() + timedelta(hours=1), # Future? No, just newer
        fetched_at=datetime.now(),
        source_id=source.id,
        is_processed=True,
        llm_processing_status=LLMProcessingStatus.COMPLETED,
        llm_summary="Summary 3",
        original_language="en",
        chinese_title="AI Future"
    )

    db_session.add_all([art1, art2, art3])
    db_session.commit()
    
    # Link Tags
    # Art1: AI (relevance 0.8), Python (0.5)
    at1_ai = ArticleTag(article_id=art1.id, tag_id=tag_ai.id, relevance_score=0.8)
    at1_py = ArticleTag(article_id=art1.id, tag_id=tag_python.id, relevance_score=0.5)
    
    # Art2: Rust (0.9)
    at2_rust = ArticleTag(article_id=art2.id, tag_id=tag_rust.id, relevance_score=0.9)

    # Art3: AI (0.9)
    at3_ai = ArticleTag(article_id=art3.id, tag_id=tag_ai.id, relevance_score=0.9)
    
    db_session.add_all([at1_ai, at1_py, at2_rust, at3_ai])
    db_session.commit()
    
    return {
        "tags": {"ai": tag_ai, "python": tag_python, "rust": tag_rust},
        "articles": [art1, art2, art3]
    }

def test_tag_filtering(client: TestClient, db_session: Session, phase3_data):
    """Test filtering articles by tag_id"""
    tag_ai = phase3_data["tags"]["ai"]
    tag_rust = phase3_data["tags"]["rust"]
    
    # Filter by AI
    resp = client.get(f"/api/v1/articles?tag_id={tag_ai.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2 # Art1 and Art3
    ids = [a["id"] for a in data["articles"]]
    assert phase3_data["articles"][0].id in ids
    assert phase3_data["articles"][2].id in ids
    assert phase3_data["articles"][1].id not in ids # Rust article
    
    # Filter by Rust
    resp = client.get(f"/api/v1/articles?tag_id={tag_rust.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["articles"][0]["id"] == phase3_data["articles"][1].id

def test_personalization(client: TestClient, db_session: Session, phase3_data, test_user):
    """Test personalized sorting in Today articles"""
    # 1. Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Today articles (Default sort: published_at desc)
    # Expected: Art3 (Newest), Art1 (Now), Art2 (1h ago)
    resp = client.get("/api/v1/today/articles", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    articles = data["articles"]
    assert len(articles) == 3
    # Verify default order: 3, 1, 2
    assert articles[0]["id"] == phase3_data["articles"][2].id
    assert articles[1]["id"] == phase3_data["articles"][0].id
    assert articles[2]["id"] == phase3_data["articles"][1].id
    
    # 3. Follow 'Rust' tag (Art2)
    # This should boost Art2 score.
    # Base score is 0. 
    # Follow => pref score increases. Let's say +2.0 (implicit follow usually small, but let's emulate explicit)
    # Actually wait, we need to call the follow endpoint.
    tag_rust = phase3_data["tags"]["rust"]
    
    # Explicit follow sets score? Or adds?
    # POST /api/v1/tags/{id}/follow calls TagService.update_preference(delta=2.0 usually for follow?)
    # Let's check api/v1/tags.py implementation of follow.
    # It calls update_preference(user_id, tag_id, 2.0). 
    # Default is 5.0. 5.0 + 2.0 = 7.0.
    # Score math in TodayService: (pref - 5.0) * relevance
    # Rust Art2: (7.0 - 5.0) * 0.9 = 1.8 score.
    # AI Art1: (5.0 - 5.0) * ... = 0 score.
    # AI Art3: 0 score.
    # So Art2 should come first!
    
    follow_resp = client.post(f"/api/v1/tags/{tag_rust.id}/follow", headers=headers)
    assert follow_resp.status_code == 200
    
    # 4. Get Today articles again
    resp = client.get("/api/v1/today/articles", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    articles = data["articles"]
    
    # Expected order: Art2 (Score 1.8), Art3 (Score 0), Art1 (Score 0)
    # Note: Art3 is newer than Art1, so Art3 comes before Art1 in tie-break.
    
    assert articles[0]["id"] == phase3_data["articles"][1].id # Rust article boosted!
    assert articles[1]["id"] == phase3_data["articles"][2].id
    assert articles[2]["id"] == phase3_data["articles"][0].id

