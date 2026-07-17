from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging

from application.market.recommender.genre_recommender_service import GenreRecommenderService
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_market_analysis_repository import SqliteMarketAnalysisRepository
from infrastructure.persistence.database.market.sqlite_template_repository import SqliteTemplateRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/recommender", tags=["market-recommender"])


def get_genre_recommender_service() -> GenreRecommenderService:
    analysis_repo = SqliteMarketAnalysisRepository(get_database())
    template_repo = SqliteTemplateRepository(get_database())
    return GenreRecommenderService(analysis_repo, template_repo)


@router.get("/genres")
async def get_genre_recommendations(
    limit: int = 6,
    service: GenreRecommenderService = Depends(get_genre_recommender_service)
):
    try:
        recommendations = service.get_recommendations(limit)
        return recommendations
    except Exception as e:
        logger.error(f"Failed to get genre recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get genre recommendations: {str(e)}")


@router.get("/genres/{genre}")
async def get_genre_recommendation(
    genre: str,
    service: GenreRecommenderService = Depends(get_genre_recommender_service)
):
    try:
        recommendation = service.get_recommendation_by_genre(genre)
        if not recommendation:
            raise HTTPException(status_code=404, detail=f"No recommendation found for genre: {genre}")
        return recommendation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get genre recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get genre recommendation: {str(e)}")