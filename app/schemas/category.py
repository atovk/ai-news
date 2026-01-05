"""
分类相关的 Pydantic Schema
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    """分类基础Schema"""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """创建分类Schema"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class Category(CategoryBase):
    """分类Schema"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """分类列表响应"""
    categories: list[Category]
    total: int
