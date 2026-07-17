from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.market.entities.hot_topic import HotTopic


class HotTopicRepository(ABC):
    @abstractmethod
    def save(self, hot_topic: HotTopic) -> None:
        pass

    @abstractmethod
    def save_batch(self, hot_topics: List[HotTopic]) -> None:
        pass

    @abstractmethod
    def get_by_id(self, hot_topic_id: str) -> Optional[HotTopic]:
        pass

    @abstractmethod
    def get_by_source(self, source: str) -> List[HotTopic]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[HotTopic]:
        pass

    @abstractmethod
    def get_latest(self, limit: int = 50) -> List[HotTopic]:
        pass

    @abstractmethod
    def delete_by_date_before(self, date: datetime) -> None:
        pass