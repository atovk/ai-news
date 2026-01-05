"""
分类服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """分类服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """获取单个分类"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_categories(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> List[Category]:
        """获取分类列表"""
        query = self.db.query(Category)
        
        if active_only:
            query = query.filter(Category.is_active == True)
        
        return query.order_by(Category.name).offset(skip).limit(limit).all()
    
    def get_total_count(self, active_only: bool = False) -> int:
        """获取分类总数"""
        query = self.db.query(Category)
        
        if active_only:
            query = query.filter(Category.is_active == True)
        
        return query.count()
    
    def create_category(self, category: CategoryCreate) -> Category:
        """创建分类"""
        db_category = Category(**category.model_dump())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def update_category(self, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
        """更新分类"""
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        update_data = category_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def delete_category(self, category_id: int) -> bool:
        """删除分类"""
        db_category = self.get_category(category_id)
        if not db_category:
            return False
        
        self.db.delete(db_category)
        self.db.commit()
        return True
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """根据名称获取分类"""
        return self.db.query(Category).filter(Category.name == name).first()
    
    def ensure_default_categories(self) -> List[Category]:
        """确保默认分类存在"""
        default_categories = [
            {"name": "科技", "description": "科技、互联网、AI等相关新闻"},
            {"name": "财经", "description": "金融、商业、经济相关新闻"},
            {"name": "体育", "description": "体育赛事、运动相关新闻"},
            {"name": "娱乐", "description": "娱乐、影视、音乐相关新闻"},
            {"name": "政治", "description": "政治、国际关系相关新闻"},
            {"name": "社会", "description": "社会民生、生活相关新闻"},
            {"name": "教育", "description": "教育、学术相关新闻"},
            {"name": "健康", "description": "健康、医疗、养生相关新闻"},
            {"name": "其他", "description": "其他未分类新闻"},
        ]
        
        created_categories = []
        for cat_data in default_categories:
            # 检查是否已存在
            existing = self.get_category_by_name(cat_data["name"])
            if not existing:
                # 创建新分类
                category = CategoryCreate(**cat_data)
                db_category = self.create_category(category)
                created_categories.append(db_category)
            else:
                created_categories.append(existing)
        
        return created_categories
