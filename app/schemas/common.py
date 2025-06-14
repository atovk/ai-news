"""
通用数据模式
"""
from typing import Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """基础响应模式"""
    success: bool = True
    message: str = "Success"


class ErrorResponse(BaseModel):
    """错误响应模式"""
    success: bool = False
    error: str
    message: str
    details: Optional[dict] = None


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    size: int = 20
    
    
class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    size: int
    pages: int
