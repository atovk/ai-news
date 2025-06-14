"""
测试配置
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db
# Import all models to ensure they are registered with SQLAlchemy
from app.models import NewsSource, NewsArticle, Category

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """测试数据库会话"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """为每个测试函数设置和清理数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield
    # 清理所有表
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def db():
    """测试数据库会话"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
