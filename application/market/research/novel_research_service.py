"""完整研究服务 - 协调所有组件生成最终报告"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from domain.market.entities.novel_research import (
    GenreRequest,
    NovelResearch,
    ResearchStatus,
)
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.persistence.database.connection import DatabaseConnection
from infrastructure.persistence.database.market.sqlite_historical_sample_repository import HistoricalSampleRepository
from infrastructure.persistence.database.market.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
    SqliteTrendAlertRepository,
)
from application.market.research.genre_analyzer import (
    GenreSuccessAnalyzer,
    GoldenFingerConflictDetector,
)
from application.market.research.ai_research_agent import AIResearchAgent
from application.market.trend.trend_analysis_service import TrendAnalysisService

logger = logging.getLogger(__name__)


class NovelResearchService:
    """完整的小说创作前研究服务
    
    协调以下组件：
    1. 历史样本库（已存已分析的小说）
    2. 题材成功率分析器
    3. 金手指冲突检测器
    4. 趋势分析服务
    5. AI研究Agent
    """
    
    def __init__(
        self,
        db: DatabaseConnection,
        sample_repo: HistoricalSampleRepository,
        template_repo: DynamicTemplateRepository,
    ):
        self.db = db
        self.sample_repo = sample_repo
        self.template_repo = template_repo
        self.genre_analyzer = GenreSuccessAnalyzer(sample_repo)
        self.conflict_detector = GoldenFingerConflictDetector(template_repo)
        self.trend_service = TrendAnalysisService(
            SqliteSnapshotRepository(db),
            SqliteTrendAlertRepository(db),
        )
        self.ai_agent = AIResearchAgent()
    
    async def conduct_research(
        self,
        user_request: GenreRequest,
        platform: Optional[str] = None,
    ) -> NovelResearch:
        """执行完整的创作前研究
        
        Args:
            user_request: 用户请求
            platform: 指定平台（可选）
        
        Returns:
            完整的研究报告
        """
        research_id = f"research-{uuid.uuid4().hex[:12]}"
        logger.info(f"Starting novel research {research_id}: {user_request.genres}")
        
        research = NovelResearch(
            research_id=research_id,
            user_request=user_request,
            status=ResearchStatus.ANALYZING,
        )
        
        try:
            # 1. 收集历史数据
            historical_data = await self._gather_historical_data(user_request, platform)
            research.sample_count = historical_data.get("total_samples", 0)
            
            # 2. 题材统计
            if user_request.genres:
                genre_stats = await self.genre_analyzer.analyze_multiple_genres(user_request.genres)
                research.genre_stats = genre_stats
                historical_data["genre_stats"] = genre_stats
            
            # 3. 开局模式分析
            opening_patterns = []
            for genre in user_request.genres:
                patterns = await self.genre_analyzer.extract_opening_patterns(genre)
                opening_patterns.extend(patterns)
            research.opening_patterns = opening_patterns[:10]  # 限制数量
            historical_data["opening_patterns"] = opening_patterns
            
            # 4. 金手指冲突检测
            if user_request.golden_fingers:
                conflict_result = await self.conflict_detector.detect_conflicts(
                    user_request.golden_fingers,
                    platform,
                )
                historical_data["conflicts"] = conflict_result["conflicts"]
                historical_data["saturation"] = conflict_result["saturation"]
            else:
                historical_data["conflicts"] = []
                historical_data["saturation"] = {
                    "level": "unknown",
                    "score": 0.0,
                    "message": "未指定金手指",
                }
            
            # 5. 时机分析
            if user_request.genres and platform:
                timing_info = await self._analyze_timing(user_request.genres, platform)
                historical_data["timing"] = timing_info
            else:
                historical_data["timing"] = {
                    "timing_score": 50,
                    "timing_advice": "未指定题材或平台，无法分析时机",
                }
            
            # 6. AI生成完整报告
            ai_research = await self.ai_agent.generate_research_report(
                user_request, historical_data
            )
            
            # 7. 合并结果
            research.overall_score = ai_research.overall_score
            research.risk_level = ai_research.risk_level
            research.risk_factors = ai_research.risk_factors
            research.ai_summary = ai_research.ai_summary
            research.ai_suggestions = ai_research.ai_suggestions
            research.ai_warnings = ai_research.ai_warnings
            research.timing_score = ai_research.timing_score
            research.timing_advice = ai_research.timing_advice
            research.recommendations = ai_research.recommendations
            
            research.status = ResearchStatus.COMPLETED
            research.completed_at = datetime.utcnow()
            
            logger.info(f"Research {research_id} completed. Score: {research.overall_score}")
            
        except Exception as e:
            logger.error(f"Research {research_id} failed: {e}")
            research.status = ResearchStatus.FAILED
            research.ai_warnings = f"研究失败: {str(e)}"
        
        return research
    
    async def _gather_historical_data(
        self,
        user_request: GenreRequest,
        platform: Optional[str],
    ) -> Dict[str, Any]:
        """收集历史数据"""
        # 计算组合成功率
        if user_request.genres:
            combo_data = await self.genre_analyzer.compute_combination_success(
                user_request.genres,
                user_request.golden_fingers,
            )
        else:
            combo_data = {
                "total_samples": 0,
                "success_rate": 0.0,
                "sample_novels": [],
            }
        
        return {
            "total_samples": combo_data.get("total_samples", 0),
            "successful_samples": combo_data.get("successful_samples", 0),
            "success_rate": combo_data.get("success_rate", 0.0),
            "sample_novels": combo_data.get("sample_novels", []),
            "avg_word_count": combo_data.get("avg_word_count", 0),
            "platforms": combo_data.get("platforms", []),
            "common_golden_fingers": combo_data.get("common_golden_fingers", []),
            "common_openings": combo_data.get("common_openings", []),
        }
    
    async def _analyze_timing(
        self,
        genres: List[str],
        platform: str,
    ) -> Dict[str, Any]:
        """分析时机"""
        timing_scores = []
        advice_parts = []
        
        for genre in genres:
            try:
                trend = await self.trend_service.analyze_genre_trend(
                    platform, genre, days=7
                )
                if trend:
                    # 趋势评分：上升=高分，平稳=中分，下降=低分
                    if trend.trend == "rising":
                        score = 80 + min(20, trend.trend_strength * 20)
                    elif trend.trend == "stable":
                        score = 50 + (trend.score_change_3d / 20)
                    else:
                        score = 30 + (trend.score_change_3d / 10)
                    
                    timing_scores.append(max(0, min(100, score)))
                    
                    if trend.alert_message:
                        advice_parts.append(
                            f"{genre}: {trend.alert_message}"
                        )
            except Exception as e:
                logger.error(f"Failed to analyze timing for {genre}: {e}")
        
        avg_score = mean(timing_scores) if timing_scores else 50
        
        if avg_score >= 70:
            advice = "✅ 当前是合适的创作时机，题材处于上升期"
        elif avg_score >= 50:
            advice = "⚖️ 时机一般，可以创作但需要差异化竞争"
        else:
            advice = "⚠️ 时机不佳，题材正在退潮，建议重新选择或等待"
        
        if advice_parts:
            advice += "\n" + "\n".join(advice_parts)
        
        return {
            "timing_score": round(avg_score, 2),
            "timing_advice": advice,
        }


def mean(values: List[float]) -> float:
    """计算平均值"""
    return sum(values) / len(values) if values else 0