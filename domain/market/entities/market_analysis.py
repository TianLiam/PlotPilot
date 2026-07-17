from typing import Optional, Dict, List, Any
from datetime import datetime
from domain.shared.base_entity import BaseEntity


class GenreTrend(BaseEntity):
    TREND_UP = "up"
    TREND_DOWN = "down"
    TREND_STABLE = "stable"

    def __init__(
        self,
        id: str,
        genre: str,
        rank: int,
        popularity_score: float,
        trend: str,
        trend_value: float,
        hot_tags: List[str],
        analysis_date: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(id)
        self.genre = genre
        self.rank = rank
        self.popularity_score = popularity_score
        self.trend = trend
        self.trend_value = trend_value
        self.hot_tags = hot_tags
        self.analysis_date = analysis_date or datetime.utcnow()
        self.extra_data = extra_data or {}


class MarketAnalysis(BaseEntity):
    def __init__(
        self,
        id: str,
        analysis_date: datetime,
        platform_summary: Dict[str, Any],
        genre_trends: List[GenreTrend],
        hot_topics_summary: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        ai_explanation: str = "",
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(id)
        self.analysis_date = analysis_date
        self.platform_summary = platform_summary
        self.genre_trends = genre_trends
        self.hot_topics_summary = hot_topics_summary
        self.recommendations = recommendations
        self.ai_explanation = ai_explanation
        self.extra_data = extra_data or {}