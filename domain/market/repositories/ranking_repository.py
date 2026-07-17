from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.market.entities.ranking import Ranking


class RankingRepository(ABC):
    @abstractmethod
    def save(self, ranking: Ranking) -> None:
        pass

    @abstractmethod
    def save_batch(self, rankings: List[Ranking]) -> None:
        pass

    @abstractmethod
    def get_by_id(self, ranking_id: str) -> Optional[Ranking]:
        pass

    @abstractmethod
    def get_by_platform(self, platform: str) -> List[Ranking]:
        pass

    @abstractmethod
    def get_by_platform_and_category(self, platform: str, category: str) -> List[Ranking]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Ranking]:
        pass

    @abstractmethod
    def get_latest_by_platform(self, platform: str, limit: int = 100) -> List[Ranking]:
        pass

    @abstractmethod
    def delete_by_date_before(self, date: datetime) -> None:
        pass

    @abstractmethod
    def clear_platform_data(self, platform: str) -> None:
        pass