from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from application.market.analyzer.market_analyzer_service import MarketAnalyzerService
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_ranking_repository import SqliteRankingRepository
from infrastructure.persistence.database.market.sqlite_hot_topic_repository import SqliteHotTopicRepository
from infrastructure.persistence.database.market.sqlite_market_analysis_repository import SqliteMarketAnalysisRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/analyzer", tags=["market-analyzer"])


def get_market_analyzer_service() -> MarketAnalyzerService:
    ranking_repo = SqliteRankingRepository(get_database())
    hot_topic_repo = SqliteHotTopicRepository(get_database())
    analysis_repo = SqliteMarketAnalysisRepository(get_database())
    return MarketAnalyzerService(ranking_repo, hot_topic_repo, analysis_repo)


@router.get("/rankings")
async def analyze_rankings(
    days: int = 7,
    service: MarketAnalyzerService = Depends(get_market_analyzer_service)
):
    try:
        results = service.analyze_rankings(days)
        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze rankings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze rankings: {str(e)}")


@router.get("/hot-topics")
async def analyze_hot_topics(
    days: int = 7,
    service: MarketAnalyzerService = Depends(get_market_analyzer_service)
):
    try:
        results = service.analyze_hot_topics(days)
        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze hot topics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze hot topics: {str(e)}")


@router.post("/full-analysis")
async def generate_full_analysis(
    days: int = 7,
    service: MarketAnalyzerService = Depends(get_market_analyzer_service)
):
    try:
        analysis = await service.generate_full_analysis(days)
        return {
            "id": analysis.id,
            "analysis_date": analysis.analysis_date.isoformat(),
            "platform_summary": analysis.platform_summary,
            "genre_trends": [
                {
                    "genre": gt.genre,
                    "rank": gt.rank,
                    "popularity_score": gt.popularity_score,
                    "trend": gt.trend,
                    "trend_value": gt.trend_value,
                    "hot_tags": gt.hot_tags
                } for gt in analysis.genre_trends
            ],
            "hot_topics_summary": analysis.hot_topics_summary,
            "recommendations": analysis.recommendations,
            "ai_explanation": analysis.ai_explanation
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate full analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate full analysis: {str(e)}")


@router.get("/latest")
async def get_latest_analysis(
    service: MarketAnalyzerService = Depends(get_market_analyzer_service)
):
    try:
        analysis = service.market_analysis_repository.get_latest()
        if not analysis:
            raise HTTPException(status_code=404, detail="No market analysis found")
        
        return {
            "id": analysis.id,
            "analysis_date": analysis.analysis_date.isoformat(),
            "platform_summary": analysis.platform_summary,
            "genre_trends": [
                {
                    "genre": gt.genre,
                    "rank": gt.rank,
                    "popularity_score": gt.popularity_score,
                    "trend": gt.trend,
                    "trend_value": gt.trend_value,
                    "hot_tags": gt.hot_tags
                } for gt in analysis.genre_trends
            ],
            "hot_topics_summary": analysis.hot_topics_summary,
            "recommendations": analysis.recommendations,
            "ai_explanation": analysis.ai_explanation
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest analysis: {str(e)}")
