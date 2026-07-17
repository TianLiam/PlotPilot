from typing import Optional, List, Dict, Any
from datetime import datetime
from domain.shared.base_entity import BaseEntity


class HotTopic(BaseEntity):
    SOURCE_WEIBO = "weibo"
    SOURCE_BAIDU = "baidu"
    SOURCE_ZHIHU = "zhihu"
    SOURCE_NEWS = "news"

    def __init__(
        self,
        id: str,
        source: str,
        title: str,
        rank: int,
        hot_value: Optional[int] = None,
        category: str = "",
        keywords: Optional[List[str]] = None,
        related_topics: Optional[List[str]] = None,
        collected_at: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(id)
        self.source = source
        self.title = title
        self.rank = rank
        self.hot_value = hot_value
        self.category = category
        self.keywords = keywords or []
        self.related_topics = related_topics or []
        self.collected_at = collected_at or datetime.utcnow()
        self.extra_data = extra_data or {}