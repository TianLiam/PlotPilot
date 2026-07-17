"""创作前研究API路由"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from domain.market.entities.novel_research import GenreRequest
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_historical_sample_repository import HistoricalSampleRepository
from infrastructure.persistence.database.market.sqlite_dynamic_template_repository import SqliteDynamicTemplateRepository
from application.market.research.novel_research_service import NovelResearchService
from application.market.research.genre_analyzer import (
    GenreSuccessAnalyzer,
    GoldenFingerConflictDetector,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/research", tags=["market-research"])


# ── 依赖注入 ──

def get_sample_repo():
    return HistoricalSampleRepository(get_database())

def get_template_repo():
    return SqliteDynamicTemplateRepository(get_database())

def get_research_service(
    sample_repo = Depends(get_sample_repo),
    template_repo = Depends(get_template_repo),
):
    return NovelResearchService(get_database(), sample_repo, template_repo)


# ── 请求/响应模型 ──

class ResearchRequest(BaseModel):
    """研究请求"""
    genres: List[str] = Field(default_factory=list, description="题材列表")
    golden_fingers: List[str] = Field(default_factory=list, description="金手指列表")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    target_word_count: int = Field(default=0, description="目标字数")
    target_chapter_count: int = Field(default=0, description="目标章节数")
    additional_notes: str = Field(default="", description="额外说明")
    platform: Optional[str] = Field(default=None, description="指定平台")


class GenreAnalysisRequest(BaseModel):
    """题材分析请求"""
    genres: List[str] = Field(..., description="要分析的题材列表")


class SampleDataRequest(BaseModel):
    """样本数据请求（用于录入历史样本）"""
    novel_id: str
    novel_name: str
    author: str = ""
    platform: str
    category: str
    word_count: int = 0
    chapter_count: int = 0
    popularity: int = 0
    avg_chapter_words: int = 0
    golden_fingers: List[str] = Field(default_factory=list)
    genre_tags: List[str] = Field(default_factory=list)
    opening_type: str = ""
    is_successful: bool = False
    peak_rank: int = 999
    days_on_chart: int = 0
    trend_direction: str = "stable"


# ── API端点 ──

@router.post("/conduct", summary="执行创作前研究")
async def conduct_research(
    request: ResearchRequest,
    service: NovelResearchService = Depends(get_research_service),
):
    """执行完整的创作前研究
    
    核心入口。返回完整的研究报告。
    """
    try:
        user_request = GenreRequest(
            genres=request.genres,
            golden_fingers=request.golden_fingers,
            keywords=request.keywords,
            target_word_count=request.target_word_count,
            target_chapter_count=request.target_chapter_count,
            additional_notes=request.additional_notes,
        )
        
        research = await service.conduct_research(user_request, request.platform)
        
        return research.to_dict()
        
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-genres", summary="分析题材统计")
async def analyze_genres(
    request: GenreAnalysisRequest,
    sample_repo = Depends(get_sample_repo),
):
    """分析指定题材的统计数据"""
    try:
        analyzer = GenreSuccessAnalyzer(sample_repo)
        stats_list = await analyzer.analyze_multiple_genres(request.genres)
        
        return {
            "genres": request.genres,
            "stats": [s.to_dict() for s in stats_list],
        }
    except Exception as e:
        logger.error(f"Failed to analyze genres: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opening-patterns", summary="提取开局模式")
async def get_opening_patterns(
    genre: str = Query(..., description="题材"),
    top_n: int = Query(5, ge=1, le=10, description="返回数量"),
    sample_repo = Depends(get_sample_repo),
):
    """提取指定题材的成功开局模式"""
    try:
        analyzer = GenreSuccessAnalyzer(sample_repo)
        patterns = await analyzer.extract_opening_patterns(genre, top_n)
        
        return {
            "genre": genre,
            "patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "success_count": p.success_count,
                    "total_count": p.total_count,
                    "success_rate": round(p.success_rate, 4),
                    "avg_popularity": round(p.avg_popularity, 2),
                    "sample_novels": p.sample_novels,
                    "key_points": p.key_points,
                } for p in patterns
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get opening patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-conflicts", summary="检测金手指冲突")
async def check_golden_finger_conflicts(
    golden_fingers: List[str],
    platform: Optional[str] = None,
    template_repo = Depends(get_template_repo),
):
    """检测金手指与市场的冲突"""
    try:
        detector = GoldenFingerConflictDetector(template_repo)
        result = await detector.detect_conflicts(golden_fingers, platform)
        return result
    except Exception as e:
        logger.error(f"Failed to check conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/combination-success", summary="计算题材组合成功率")
async def calculate_combination_success(
    genres: List[str],
    golden_fingers: List[str] = None,
    sample_repo = Depends(get_sample_repo),
):
    """计算题材组合的成功率"""
    try:
        analyzer = GenreSuccessAnalyzer(sample_repo)
        result = await analyzer.compute_combination_success(genres, golden_fingers)
        return result
    except Exception as e:
        logger.error(f"Failed to calculate combination success: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 历史样本管理 ──

@router.post("/samples", summary="添加历史样本")
async def add_sample(
    sample: SampleDataRequest,
    sample_repo = Depends(get_sample_repo),
):
    """添加一本历史样本小说"""
    try:
        from domain.market.entities.novel_research import HistoricalSample
        
        h_sample = HistoricalSample(
            novel_id=sample.novel_id,
            novel_name=sample.novel_name,
            author=sample.author,
            platform=sample.platform,
            category=sample.category,
            word_count=sample.word_count,
            chapter_count=sample.chapter_count,
            popularity=sample.popularity,
            avg_chapter_words=sample.avg_chapter_words,
            golden_fingers=sample.golden_fingers,
            genre_tags=sample.genre_tags,
            opening_type=sample.opening_type,
            is_successful=sample.is_successful,
            peak_rank=sample.peak_rank,
            days_on_chart=sample.days_on_chart,
            trend_direction=sample.trend_direction,
        )
        
        await sample_repo.save_sample(h_sample)
        
        return {"message": "Sample saved", "novel_id": sample.novel_id}
    except Exception as e:
        logger.error(f"Failed to save sample: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/samples/batch", summary="批量添加历史样本")
async def add_samples_batch(
    samples: List[SampleDataRequest],
    sample_repo = Depends(get_sample_repo),
):
    """批量添加历史样本小说"""
    try:
        from domain.market.entities.novel_research import HistoricalSample
        
        h_samples = []
        for s in samples:
            h_samples.append(HistoricalSample(
                novel_id=s.novel_id,
                novel_name=s.novel_name,
                author=s.author,
                platform=s.platform,
                category=s.category,
                word_count=s.word_count,
                chapter_count=s.chapter_count,
                popularity=s.popularity,
                avg_chapter_words=s.avg_chapter_words,
                golden_fingers=s.golden_fingers,
                genre_tags=s.genre_tags,
                opening_type=s.opening_type,
                is_successful=s.is_successful,
                peak_rank=s.peak_rank,
                days_on_chart=s.days_on_chart,
                trend_direction=s.trend_direction,
            ))
        
        saved_count = await sample_repo.save_samples_batch(h_samples)
        
        return {
            "message": f"Saved {saved_count}/{len(samples)} samples",
            "total": len(samples),
            "saved": saved_count,
        }
    except Exception as e:
        logger.error(f"Failed to save samples batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/samples/search", summary="搜索历史样本")
async def search_samples(
    genre: Optional[str] = Query(None, description="题材"),
    tag: Optional[str] = Query(None, description="标签"),
    golden_finger: Optional[str] = Query(None, description="金手指"),
    successful_only: bool = Query(True, description="仅成功样本"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    sample_repo = Depends(get_sample_repo),
):
    """按条件搜索历史样本"""
    try:
        samples = []
        if genre:
            samples = await sample_repo.find_by_genre(
                genres=[genre],
                successful_only=successful_only,
                limit=limit,
            )
        elif tag:
            samples = await sample_repo.find_by_tags(
                tags=[tag],
                successful_only=successful_only,
                limit=limit,
            )
        elif golden_finger:
            samples = await sample_repo.find_by_golden_finger(
                golden_fingers=[golden_finger],
                successful_only=successful_only,
                limit=limit,
            )
        else:
            raise HTTPException(status_code=400, detail="Please provide genre, tag, or golden_finger")
        
        return {
            "total": len(samples),
            "samples": [
                {
                    "novel_id": s.novel_id,
                    "novel_name": s.novel_name,
                    "author": s.author,
                    "platform": s.platform,
                    "category": s.category,
                    "word_count": s.word_count,
                    "popularity": s.popularity,
                    "golden_fingers": s.golden_fingers,
                    "genre_tags": s.genre_tags,
                    "opening_type": s.opening_type,
                    "is_successful": s.is_successful,
                    "peak_rank": s.peak_rank,
                } for s in samples
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search samples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/samples/count", summary="统计样本数量")
async def count_samples(
    genre: Optional[str] = Query(None, description="题材"),
    successful_only: bool = Query(False, description="仅成功样本"),
    sample_repo = Depends(get_sample_repo),
):
    """统计某题材的样本数量"""
    try:
        if not genre:
            raise HTTPException(status_code=400, detail="Genre is required")
        
        if successful_only:
            count = await sample_repo.count_successful_by_genre(genre)
        else:
            count = await sample_repo.count_by_genre(genre)
        
        return {
            "genre": genre,
            "successful_only": successful_only,
            "count": count,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to count samples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 快速预检 ──

@router.post("/quick-check", summary="快速预检")
async def quick_check(
    request: ResearchRequest,
    service: NovelResearchService = Depends(get_research_service),
):
    """快速预检（不调用LLM）
    
    快速返回基础数据，供前端展示。
    """
    try:
        user_request = GenreRequest(
            genres=request.genres,
            golden_fingers=request.golden_fingers,
            keywords=request.keywords,
            target_word_count=request.target_word_count,
            target_chapter_count=request.target_chapter_count,
            additional_notes=request.additional_notes,
        )
        
        result = {
            "user_request": user_request.to_dict(),
            "genre_stats": [],
            "conflict_check": {},
            "saturation": {},
        }
        
        # 题材统计
        if user_request.genres:
            stats = await service.genre_analyzer.analyze_multiple_genres(user_request.genres)
            result["genre_stats"] = [s.to_dict() for s in stats]
        
        # 金手指冲突
        if user_request.golden_fingers:
            conflict = await service.conflict_detector.detect_conflicts(
                user_request.golden_fingers,
                request.platform,
            )
            result["conflict_check"] = {
                "conflicts": conflict["conflicts"],
                "recommendations": conflict["recommendations"],
            }
            result["saturation"] = conflict["saturation"]
        
        return result
        
    except Exception as e:
        logger.error(f"Quick check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 预定义题材/金手指选项 ──

@router.get("/options/genres", summary="获取可选题材")
async def get_genre_options():
    """获取所有可选的题材列表"""
    return {
        "genres": [
            {"value": "都市", "label": "都市", "description": "现代都市生活"},
            {"value": "玄幻", "label": "玄幻", "description": "东方玄幻世界"},
            {"value": "仙侠", "label": "仙侠", "description": "修真仙侠"},
            {"value": "言情", "label": "言情", "description": "现代言情"},
            {"value": "古言", "label": "古言", "description": "古代言情"},
            {"value": "科幻", "label": "科幻", "description": "未来科幻"},
            {"value": "末日", "label": "末日", "description": "末日生存"},
            {"value": "系统", "label": "系统流", "description": "系统流"},
            {"value": "种田", "label": "种田", "description": "种田经营"},
            {"value": "重生", "label": "重生流", "description": "重生回到过去"},
            {"value": "穿越", "label": "穿越流", "description": "穿越到异世界"},
            {"value": "无敌", "label": "无敌流", "description": "开局无敌"},
            {"value": "签到", "label": "签到流", "description": "每日签到"},
            {"value": "鉴宝", "label": "鉴宝流", "description": "古玩鉴宝"},
            {"value": "神医", "label": "神医流", "description": "神医传承"},
            {"value": "兵王", "label": "兵王流", "description": "特种兵王"},
            {"value": "神豪", "label": "神豪流", "description": "神豪系统"},
            {"value": "游戏", "label": "游戏", "description": "游戏竞技"},
            {"value": "历史", "label": "历史", "description": "历史穿越"},
            {"value": "军事", "label": "军事", "description": "军事战争"},
        ]
    }


@router.get("/options/golden-fingers", summary="获取可选金手指")
async def get_golden_finger_options():
    """获取所有可选的金手指类型"""
    return {
        "golden_fingers": [
            {"value": "签到系统", "label": "签到系统", "category": "系统"},
            {"value": "神级系统", "label": "神级系统", "category": "系统"},
            {"value": "强化系统", "label": "强化系统", "category": "系统"},
            {"value": "反派系统", "label": "反派系统", "category": "系统"},
            {"value": "重生回过去", "label": "重生回过去", "category": "重生"},
            {"value": "穿越到异世界", "label": "穿越到异世界", "category": "穿越"},
            {"value": "魂穿", "label": "魂穿", "category": "穿越"},
            {"value": "开局无敌", "label": "开局无敌", "category": "无敌"},
            {"value": "扮猪吃虎", "label": "扮猪吃虎", "category": "无敌"},
            {"value": "每日签到", "label": "每日签到", "category": "签到"},
            {"value": "随身仓库", "label": "随身仓库", "category": "仓库"},
            {"value": "空间仓库", "label": "空间仓库", "category": "仓库"},
            {"value": "古玩鉴宝", "label": "古玩鉴宝", "category": "鉴宝"},
            {"value": "神医传承", "label": "神医传承", "category": "神医"},
            {"value": "特种兵王", "label": "特种兵王", "category": "兵王"},
            {"value": "神豪系统", "label": "神豪系统", "category": "神豪"},
        ]
    }