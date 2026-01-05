"""
分类管理 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.category_service import CategoryService
from app.services.article_service import ArticleService
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryListResponse
from app.schemas.article import ArticleListResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    active_only: bool = Query(True, description="仅显示活跃分类"),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    category_service = CategoryService(db)
    
    # 确保默认分类存在
    category_service.ensure_default_categories()
    
    categories = category_service.get_categories(skip=skip, limit=limit, active_only=active_only)
    total = category_service.get_total_count(active_only=active_only)
    
    return CategoryListResponse(
        categories=[Category.model_validate(cat) for cat in categories],
        total=total
    )


@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """获取单个分类详情"""
    category_service = CategoryService(db)
    category = category_service.get_category(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return Category.model_validate(category)


@router.get("/{category_id}/articles", response_model=ArticleListResponse)
async def get_category_articles(
    category_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取分类下的文章"""
    # 验证分类是否存在
    category_service = CategoryService(db)
    category = category_service.get_category(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 获取该分类下的文章
    article_service = ArticleService(db)
    skip = (page - 1) * size
    articles = article_service.get_articles(
        skip=skip, 
        limit=size, 
        category=category.name
    )
    
    total = article_service.get_articles_count(category=category.name)
    
    from app.schemas.article import Article
    return ArticleListResponse(
        total=total,
        page=page,
        size=size,
        articles=[Article.model_validate(article) for article in articles]
    )


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """创建分类"""
    category_service = CategoryService(db)
    
    # 检查是否已存在同名分类
    existing = category_service.get_category_by_name(category.name)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Category with name '{category.name}' already exists"
        )
    
    db_category = category_service.create_category(category)
    return Category.model_validate(db_category)


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """更新分类"""
    category_service = CategoryService(db)
    db_category = category_service.update_category(category_id, category_update)
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return Category.model_validate(db_category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """删除分类"""
    category_service = CategoryService(db)
    success = category_service.delete_category(category_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
