import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User

@pytest.mark.auth
class TestAuthentication:
    """Authentication API tests"""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newtestuser",
                "email": "newtest@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newtest@example.com"
        assert data["user"]["username"] == "newtestuser"
        
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with existing email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "otheruser",
                "email": "test@example.com",  # Same as test_user
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_token: str):
        """Test get current user profile"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code != 200:
            print(f"\nAuth Error: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
