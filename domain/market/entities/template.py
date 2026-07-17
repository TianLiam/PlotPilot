from typing import Optional, Dict, Any
from datetime import datetime
from domain.shared.base_entity import BaseEntity


class Template(BaseEntity):
    TYPE_GOLDEN_FINGER = "golden_finger"
    TYPE_CHARACTER = "character"
    TYPE_WORLDVIEW = "worldview"
    TYPE_CLIMAX = "climax"
    TYPE_CONFLICT = "conflict"
    TYPE_REWARD = "reward"
    TYPE_FORESADOW = "foreshadow"
    TYPE_ENDING = "ending"
    TYPE_UPGRADE_PATH = "upgrade_path"
    TYPE_COOL_POINT = "cool_point"

    def __init__(
        self,
        id: str,
        name: str,
        template_type: str,
        genre: str,
        content: str,
        description: str = "",
        popularity: int = 0,
        usage_count: int = 0,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(id)
        self.name = name
        self.template_type = template_type
        self.genre = genre
        self.content = content
        self.description = description
        self.popularity = popularity
        self.usage_count = usage_count
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.extra_data = extra_data or {}