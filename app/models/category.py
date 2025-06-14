"""
分类模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from app.models.database import Base


class Category(Base):
    """分类模型"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
