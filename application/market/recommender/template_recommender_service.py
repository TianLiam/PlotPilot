import logging
from typing import List, Dict, Any, Optional
from domain.market.entities.template import Template
from domain.market.repositories.template_repository import TemplateRepository

logger = logging.getLogger(__name__)


class TemplateRecommenderService:
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    def get_templates_by_type(self, template_type: str, genre: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        if genre:
            templates = self.template_repository.get_by_type_and_genre(template_type, genre)
        else:
            templates = self.template_repository.get_by_type(template_type)
        
        result = []
        for template in templates[:limit]:
            result.append({
                "id": template.id,
                "name": template.name,
                "type": template.template_type,
                "genre": template.genre,
                "description": template.description,
                "popularity": template.popularity,
                "usage_count": template.usage_count
            })
        
        return result

    def get_golden_fingers(self, genre: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        return self.get_templates_by_type(Template.TYPE_GOLDEN_FINGER, genre, limit)

    def get_characters(self, genre: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        return self.get_templates_by_type(Template.TYPE_CHARACTER, genre, limit)

    def get_worldviews(self, genre: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        return self.get_templates_by_type(Template.TYPE_WORLDVIEW, genre, limit)

    def get_cool_points(self, genre: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        return self.get_templates_by_type(Template.TYPE_COOL_POINT, genre, limit)

    def search_templates(self, keyword: str) -> List[Dict[str, Any]]:
        templates = self.template_repository.search(keyword)
        result = []
        for template in templates:
            result.append({
                "id": template.id,
                "name": template.name,
                "type": template.template_type,
                "genre": template.genre,
                "description": template.description,
                "popularity": template.popularity,
                "usage_count": template.usage_count
            })
        return result

    def get_template_detail(self, template_id: str) -> Optional[Dict[str, Any]]:
        template = self.template_repository.get_by_id(template_id)
        if not template:
            return None
        
        return {
            "id": template.id,
            "name": template.name,
            "type": template.template_type,
            "genre": template.genre,
            "content": template.content,
            "description": template.description,
            "popularity": template.popularity,
            "usage_count": template.usage_count,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        }

    def use_template(self, template_id: str) -> bool:
        try:
            self.template_repository.increment_usage(template_id)
            return True
        except Exception as e:
            logger.error(f"Failed to increment template usage: {e}")
            return False