from pydantic import BaseModel, ConfigDict
from typing import Optional

class TagBase(BaseModel):
    name: str
    slug: Optional[str] = None

class TagResponse(TagBase):
    id: int
    article_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ArticleTagResponse(BaseModel):
    tag: TagResponse
    relevance_score: float = 1.0
    
    model_config = ConfigDict(from_attributes=True)
