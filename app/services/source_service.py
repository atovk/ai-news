"""
新闻源服务
"""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.source import NewsSource
from app.schemas.source import SourceCreate, SourceUpdate


class SourceService:
    """新闻源服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_source(self, source_id: int) -> Optional[NewsSource]:
        """获取单个新闻源"""
        return self.db.query(NewsSource).filter(NewsSource.id == source_id).first()
    
    def get_sources(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[NewsSource]:
        """获取新闻源列表"""
        query = self.db.query(NewsSource)
        
        if active_only:
            query = query.filter(NewsSource.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def get_sources_count(self, active_only: bool = False) -> int:
        """获取新闻源总数"""
        query = self.db.query(NewsSource)
        
        if active_only:
            query = query.filter(NewsSource.is_active == True)
        
        return query.count()
    
    def create_source(self, source: SourceCreate) -> NewsSource:
        """创建新闻源"""
        source_data = source.model_dump()
        # 将HttpUrl转换为字符串
        if 'url' in source_data:
            source_data['url'] = str(source_data['url'])
        
        db_source = NewsSource(**source_data)
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        return db_source
    
    def update_source(self, source_id: int, source_update: SourceUpdate) -> Optional[NewsSource]:
        """更新新闻源"""
        db_source = self.get_source(source_id)
        if not db_source:
            return None

        update_data = source_update.model_dump(exclude_unset=True)
        # 将HttpUrl转换为字符串
        if 'url' in update_data:
            update_data['url'] = str(update_data['url'])
            
        for field, value in update_data.items():
            setattr(db_source, field, value)

        db_source.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(db_source)
        return db_source
    
    def delete_source(self, source_id: int) -> bool:
        """删除新闻源"""
        db_source = self.get_source(source_id)
        if not db_source:
            return False
        
        self.db.delete(db_source)
        self.db.commit()
        return True
    
    def update_last_fetch_time(self, source_id: int) -> bool:
        """更新最后抓取时间"""
        db_source = self.get_source(source_id)
        if not db_source:
            return False
        
        db_source.last_fetch_time = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    def get_total_count(self, active_only: bool = False) -> int:
        """获取新闻源总数"""
        query = self.db.query(NewsSource)
        if active_only:
            query = query.filter(NewsSource.is_active == True)
        return query.count()
