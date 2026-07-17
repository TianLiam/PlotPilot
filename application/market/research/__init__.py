"""创作前研究模块"""
from domain.market.entities.novel_research import (
    GenreRequest,
    NovelResearch,
    ResearchStatus,
    GenreStats,
    OpeningPattern,
    HistoricalSample,
    RecommendationItem,
    GenreElement,
)
from infrastructure.persistence.database.market.sqlite_historical_sample_repository import HistoricalSampleRepository
from application.market.research.genre_analyzer import (
    GenreSuccessAnalyzer,
    GoldenFingerConflictDetector,
)
from application.market.research.ai_research_agent import AIResearchAgent
from application.market.research.novel_research_service import NovelResearchService

__all__ = [
    "GenreRequest",
    "NovelResearch",
    "ResearchStatus",
    "GenreStats",
    "OpeningPattern",
    "HistoricalSample",
    "RecommendationItem",
    "GenreElement",
    "HistoricalSampleRepository",
    "GenreSuccessAnalyzer",
    "GoldenFingerConflictDetector",
    "AIResearchAgent",
    "NovelResearchService",
]