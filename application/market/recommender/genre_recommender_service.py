import logging
from typing import List, Dict, Any
from domain.market.repositories.market_analysis_repository import MarketAnalysisRepository
from domain.market.repositories.template_repository import TemplateRepository

logger = logging.getLogger(__name__)


class GenreRecommenderService:
    def __init__(
        self,
        market_analysis_repository: MarketAnalysisRepository,
        template_repository: TemplateRepository
    ):
        self.market_analysis_repository = market_analysis_repository
        self.template_repository = template_repository

    def get_recommendations(self, limit: int = 6) -> List[Dict[str, Any]]:
        latest_analysis = self.market_analysis_repository.get_latest()
        
        if not latest_analysis:
            return self._get_default_recommendations()
        
        recommendations = latest_analysis.recommendations[:limit]
        
        for rec in recommendations:
            golden_finger_templates = self.template_repository.get_by_type_and_genre(
                "golden_finger", rec["genre"]
            )
            rec["golden_finger_options"] = [
                {"id": t.id, "name": t.name, "description": t.description}
                for t in golden_finger_templates[:5]
            ]
            
            character_templates = self.template_repository.get_by_type_and_genre(
                "character", rec["genre"]
            )
            rec["character_options"] = [
                {"id": t.id, "name": t.name, "description": t.description}
                for t in character_templates[:3]
            ]
        
        return recommendations

    def get_recommendation_by_genre(self, genre: str) -> Dict[str, Any]:
        latest_analysis = self.market_analysis_repository.get_latest()
        
        if latest_analysis:
            for rec in latest_analysis.recommendations:
                if rec["genre"] == genre:
                    golden_finger_templates = self.template_repository.get_by_type_and_genre(
                        "golden_finger", genre
                    )
                    rec["golden_finger_options"] = [
                        {"id": t.id, "name": t.name, "description": t.description}
                        for t in golden_finger_templates[:5]
                    ]
                    return rec
        
        return self._get_default_recommendation(genre)

    def _get_default_recommendations(self) -> List[Dict[str, Any]]:
        default_genres = [
            {"genre": "都市", "score": 95, "stars": "★★★★★", "trend": "up", "trend_value": 15.5, "hot_tags": ["神豪", "重生", "直播"], "reason": "都市题材一直是网文热门，受众广泛"},
            {"genre": "玄幻", "score": 88, "stars": "★★★★☆", "trend": "stable", "trend_value": 2.3, "hot_tags": ["系统", "重生", "无敌"], "reason": "玄幻题材读者基数大，稳定热门"},
            {"genre": "仙侠", "score": 85, "stars": "★★★★☆", "trend": "up", "trend_value": 8.2, "hot_tags": ["修仙", "长生", "渡劫"], "reason": "仙侠题材近期热度上涨"},
            {"genre": "历史", "score": 82, "stars": "★★★☆☆", "trend": "stable", "trend_value": 1.5, "hot_tags": ["穿越", "争霸", "种田"], "reason": "历史题材有稳定的读者群"},
            {"genre": "游戏", "score": 78, "stars": "★★★☆☆", "trend": "up", "trend_value": 6.8, "hot_tags": ["网游", "电竞", "直播"], "reason": "游戏题材结合直播热点"},
            {"genre": "科幻", "score": 75, "stars": "★★★☆☆", "trend": "stable", "trend_value": -1.2, "hot_tags": ["末世", "星际", "机甲"], "reason": "科幻题材有固定受众"}
        ]
        
        for rec in default_genres:
            golden_finger_templates = self.template_repository.get_by_type_and_genre(
                "golden_finger", rec["genre"]
            )
            rec["golden_finger_options"] = [
                {"id": t.id, "name": t.name, "description": t.description}
                for t in golden_finger_templates[:5]
            ]
        
        return default_genres

    def _get_default_recommendation(self, genre: str) -> Dict[str, Any]:
        golden_finger_templates = self.template_repository.get_by_type_and_genre(
            "golden_finger", genre
        )
        
        return {
            "genre": genre,
            "score": 70,
            "stars": "★★★☆☆",
            "trend": "stable",
            "trend_value": 0,
            "hot_tags": [],
            "reason": f"{genre}题材是网文常见类型",
            "golden_finger_options": [
                {"id": t.id, "name": t.name, "description": t.description}
                for t in golden_finger_templates[:5]
            ]
        }