from typing import List
from sqlalchemy.orm import Session
from app.models.tag import Tag, ArticleTag
from app.models.article import NewsArticle
import logging

logger = logging.getLogger(__name__)

class TagService:
    def __init__(self, db: Session):
        self.db = db

    def link_tags_to_article(self, article: NewsArticle, tag_names: List[str]) -> List[Tag]:
        """
        Link a list of tag names to an article.
        Creates tags if they don't exist.
        Returns the list of Tag objects linked.
        """
        if not tag_names:
            return []

        try:
            # Normalize tags: lowercase and strip
            normalized_names = {name.strip().lower() for name in tag_names if name and name.strip()}
            if not normalized_names:
                return []

            # Find existing tags
            existing_tags = self.db.query(Tag).filter(Tag.name.in_(normalized_names)).all()
            existing_tag_map = {tag.name: tag for tag in existing_tags}

            # Create new tags
            all_tags = []
            new_tags_created = False
            
            for name in normalized_names:
                if name in existing_tag_map:
                    all_tags.append(existing_tag_map[name])
                else:
                    new_tag = Tag(name=name)
                    self.db.add(new_tag)
                    all_tags.append(new_tag)
                    new_tags_created = True
            
            if new_tags_created:
                self.db.commit()
                # Refresh new tags to get IDs
                for tag in all_tags:
                    if tag.id is None:
                        self.db.refresh(tag)

            # Link to article
            # Check existing links to avoid ConstraintViolation
            existing_links = self.db.query(ArticleTag).filter(
                ArticleTag.article_id == article.id
            ).all()
            linked_tag_ids = {link.tag_id for link in existing_links}

            new_links_created = False
            for tag in all_tags:
                if tag.id not in linked_tag_ids:
                    article_tag = ArticleTag(article_id=article.id, tag_id=tag.id)
                    self.db.add(article_tag)
                    new_links_created = True
            
            # Update cache field with comma-separated list of ALL linked tags
            current_text_tags = set(article.tags.split(',')) if article.tags else set()
            current_text_tags.update(normalized_names)
            article.tags = ",".join(sorted(current_text_tags))

            if new_links_created:
                self.db.commit()
                
            return all_tags

        except Exception as e:
            logger.error(f"Error linking tags to article {article.id}: {e}")
            self.db.rollback()
            return []

    def update_preference(self, user_id: int, tag_id: int, score_delta: float):
        """
        Update user's preference score for a tag.
        Score is clamped between 1.0 and 10.0.
        """
        try:
            from app.models.tag import UserTagPreference
            
            pref = self.db.query(UserTagPreference).filter(
                UserTagPreference.user_id == user_id,
                UserTagPreference.tag_id == tag_id
            ).first()
            
            if not pref:
                pref = UserTagPreference(
                    user_id=user_id, 
                    tag_id=tag_id, 
                    preference_score=5.0, # Start neutral
                    source="implicit"
                )
                self.db.add(pref)
            
            pref.preference_score += score_delta
            # Clamp between 1.0 and 10.0
            pref.preference_score = max(1.0, min(10.0, pref.preference_score))
            
            self.db.commit()
            return pref
            
        except Exception as e:
            logger.error(f"Error updating preference for user {user_id} tag {tag_id}: {e}")
            self.db.rollback()
            return None
