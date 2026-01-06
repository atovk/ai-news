from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.tag_service import TagService
from app.schemas.tag import TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/{tag_id}/follow", status_code=status.HTTP_200_OK)
async def follow_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Follow a tag (explicit preference) or increase score.
    """
    tag_service = TagService(db)
    # Explicit follow gives a high score (e.g., +5.0 or set to max?)
    # Let's say we add 2.0 to score for 'follow' action usage.
    # Or if we want a binary 'followed' state, we might need a separate field or logic.
    # For now, following implies high preference.
    
    pref = tag_service.update_preference(current_user.id, tag_id, 5.0)
    
    if not pref:
        raise HTTPException(status_code=404, detail="Tag not found or error updating preference")
    
    return {"message": "Tag followed successfully", "score": pref.preference_score}

@router.post("/{tag_id}/unfollow", status_code=status.HTTP_200_OK)
async def unfollow_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unfollow a tag (decrease preference).
    """
    tag_service = TagService(db)
    pref = tag_service.update_preference(current_user.id, tag_id, -5.0)
    
    if not pref:
        raise HTTPException(status_code=404, detail="Tag not found or error updating preference")
    
    return {"message": "Tag unfollowed successfully", "score": pref.preference_score}

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Get tag details by ID.
    """
    from app.models.tag import Tag
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag
