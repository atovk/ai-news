"""
新闻文章服务
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.article import NewsArticle
from app.schemas.article import ArticleCreate, ArticleUpdate


class ArticleService:
    """新闻文章服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_article(self, article_id: int) -> Optional[NewsArticle]:
        """获取单个文章"""
        return self.db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    
    def get_articles(
        self, 
        skip: int = 0, 
        limit: int = 20,
        category: Optional[str] = None,
        source_id: Optional[int] = None,
        tag_id: Optional[int] = None
    ) -> List[NewsArticle]:
        """获取文章列表"""
        query = self.db.query(NewsArticle)
        
        if category:
            query = query.filter(NewsArticle.category == category)
        
        if source_id:
            query = query.filter(NewsArticle.source_id == source_id)
            
        if tag_id:
            from app.models.tag import ArticleTag
            query = query.join(NewsArticle.article_tags).filter(ArticleTag.tag_id == tag_id)
        
        return query.order_by(desc(NewsArticle.published_at)).offset(skip).limit(limit).all()
    
    def get_articles_count(
        self, 
        category: Optional[str] = None,
        source_id: Optional[int] = None,
        tag_id: Optional[int] = None
    ) -> int:
        """获取文章总数"""
        query = self.db.query(NewsArticle)
        
        if category:
            query = query.filter(NewsArticle.category == category)
        
        if source_id:
            query = query.filter(NewsArticle.source_id == source_id)

        if tag_id:
            from app.models.tag import ArticleTag
            query = query.join(NewsArticle.article_tags).filter(ArticleTag.tag_id == tag_id)
        
        return query.count()
    
    def create_article(self, article: ArticleCreate) -> NewsArticle:
        """创建文章"""
        article_data = article.model_dump()
        # 将HttpUrl转换为字符串
        if 'url' in article_data:
            article_data['url'] = str(article_data['url'])
        # 将tags列表转换为JSON字符串
        if 'tags' in article_data and isinstance(article_data['tags'], list):
            article_data['tags'] = json.dumps(article_data['tags'])
        
        db_article = NewsArticle(**article_data)
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article
    
    def update_article(self, article_id: int, article_update: ArticleUpdate) -> Optional[NewsArticle]:
        """更新文章"""
        db_article = self.get_article(article_id)
        if not db_article:
            return None

        update_data = article_update.model_dump(exclude_unset=True)
        # 将HttpUrl转换为字符串
        if 'url' in update_data:
            update_data['url'] = str(update_data['url'])
        # 将tags列表转换为JSON字符串
        if 'tags' in update_data and isinstance(update_data['tags'], list):
            update_data['tags'] = json.dumps(update_data['tags'])
            
        for field, value in update_data.items():
            setattr(db_article, field, value)

        self.db.commit()
        self.db.refresh(db_article)
        return db_article
    
    def delete_article(self, article_id: int) -> bool:
        """删除文章"""
        db_article = self.get_article(article_id)
        if not db_article:
            return False
        
        self.db.delete(db_article)
        self.db.commit()
        return True
    
    def get_article_by_url(self, url: str) -> Optional[NewsArticle]:
        """根据URL获取文章"""
        return self.db.query(NewsArticle).filter(NewsArticle.url == url).first()
