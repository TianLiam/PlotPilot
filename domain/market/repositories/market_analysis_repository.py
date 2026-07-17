from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.market.entities.market_analysis import MarketAnalysis


class MarketAnalysisRepository(ABC):
    @abstractmethod
    def save(self, analysis: MarketAnalysis) -> None:
        pass

    @abstractmethod
    def get_by_id(self, analysis_id: str) -> Optional[MarketAnalysis]:
        pass

    @abstractmethod
    def get_latest(self) -> Optional[MarketAnalysis]:
        pass

    @abstractmethod
    def get_by_date(self, date: datetime) -> Optional[MarketAnalysis]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MarketAnalysis]:
        pass

    @abstractmethod
    def list_all(self) -> List[MarketAnalysis]:
        pass