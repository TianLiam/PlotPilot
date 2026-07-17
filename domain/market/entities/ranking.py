from typing import Optional, Dict, Any
from datetime import datetime
from domain.shared.base_entity import BaseEntity


class Ranking(BaseEntity):
    PLATFORM_QIDIAN = "qidian"
    PLATFORM_FANQIE = "fanqie"
    PLATFORM_QIMAO = "qimao"
    PLATFORM_ZHIHU = "zhihu"

    def __init__(
        self,
        id: str,
        platform: str,
        category: str,
        rank: int,
        novel_name: str,
        author: str,
        description: str = "",
        tags: str = "",
        update_time: Optional[str] = None,
        word_count: Optional[int] = None,
        popularity: Optional[int] = None,
        score: Optional[float] = None,
        comments: Optional[int] = None,
        favorites: Optional[int] = None,
        collected_at: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(id)
        self.platform = platform
        self.category = category
        self.rank = rank
        self.novel_name = novel_name
        self.author = author
        self.description = description
        self.tags = tags
        self.update_time = update_time
        self.word_count = word_count
        self.popularity = popularity
        self.score = score
        self.comments = comments
        self.favorites = favorites
        self.collected_at = collected_at or datetime.utcnow()
        self.extra_data = extra_data or {}