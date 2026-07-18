"""趋势预测API路由"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
    SqliteTrendAlertRepository,
)
from application.market.trend.trend_analysis_service import TrendAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/trend", tags=["market-trend"])


# ── 依赖注入 ──

def get_snapshot_repo():
    return SqliteSnapshotRepository(get_database())

def get_alert_repo():
    return SqliteTrendAlertRepository(get_database())

def get_trend_service(
    snapshot_repo = Depends(get_snapshot_repo),
    alert_repo = Depends(get_alert_repo),
):
    return TrendAnalysisService(snapshot_repo, alert_repo)


# ── 请求/响应模型 ──

class SaveSnapshotRequest(BaseModel):
    """保存快照请求"""
    platform: str = Field(..., description="平台：fanqie, qidian, qimao")
    category: str = Field(..., description="分类")
    items: List[dict] = Field(..., description="榜单数据")


class SnapshotRequest(BaseModel):
    """快照请求"""
    platforms: List[str] = Field(default=["fanqie"], description="平台列表")
    categories: List[str] = Field(default=["都市", "玄幻", "言情"], description="分类列表")


class GenreTrendResponse(BaseModel):
    """题材趋势响应"""
    genre: str
    platform: str
    current_score: float
    current_top_rank: int
    score_change_1d: float
    score_change_3d: float
    score_change_7d: float
    trend: str
    trend_strength: float
    alert_level: str
    alert_message: str
    history_points: int


class AlertResponse(BaseModel):
    """预警响应"""
    alert_type: str
    severity: str
    genre: str
    platform: str
    message: str
    change_value: float
    duration_days: int
    created_at: str


# ── API端点 ──

@router.get("/dashboard", summary="获取真实趋势大盘数据")
async def get_trend_dashboard(
    days: int = Query(30, ge=1, le=90, description="历史天数"),
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """返回仅由持久化每日快照计算的趋势大盘。"""
    try:
        return await service.get_dashboard(days)
    except Exception as e:
        logger.error(f"Failed to build trend dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/snapshot/save", summary="保存每日快照")
async def save_snapshot(
    request: SaveSnapshotRequest,
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """保存榜单的每日快照
    
    通常由定时任务在爬取榜单后自动调用。
    """
    try:
        snapshot = await service.save_daily_snapshot(
            platform=request.platform,
            category=request.category,
            items=request.items,
        )
        return {
            "message": "Snapshot saved",
            "snapshot_date": snapshot.snapshot_date,
            "platform": snapshot.platform,
            "category": snapshot.category,
            "total_count": snapshot.total_count,
        }
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/genre", response_model=GenreTrendResponse, summary="分析题材趋势")
async def get_genre_trend(
    platform: str = Query("fanqie", description="平台"),
    category: str = Query(..., description="分类"),
    days: int = Query(7, ge=1, le=30, description="分析最近N天"),
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """分析某题材的趋势"""
    try:
        trend = await service.analyze_genre_trend(platform, category, days)
        if not trend:
            raise HTTPException(status_code=404, detail=f"No data for {platform}/{category}")
        return trend.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=List[GenreTrendResponse], summary="批量分析趋势")
async def analyze_all_trends(
    request: SnapshotRequest,
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """批量分析多个平台+分类的趋势"""
    try:
        all_trends = []
        for platform in request.platforms:
            trends = await service.analyze_all_genres(platform, request.categories)
            all_trends.extend(trends)
        
        # 自动生成预警
        await service.generate_alerts_from_trends(all_trends)
        
        return [t.to_dict() for t in all_trends]
    except Exception as e:
        logger.error(f"Failed to analyze trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rising", summary="获取正在上涨的题材")
async def get_rising_genres(
    platform: Optional[str] = Query(None, description="平台过滤"),
    min_change: float = Query(5.0, ge=0, le=100, description="最小涨幅"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """获取正在上涨的题材
    
    例如：修仙连续3天上涨12%，可能正在回暖
    """
    try:
        rising = await service.get_rising_genres(platform, min_change, limit)
        return {
            "total": len(rising),
            "items": rising,
        }
    except Exception as e:
        logger.error(f"Failed to get rising genres: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/declining", summary="获取正在下跌的题材")
async def get_declining_genres(
    platform: Optional[str] = Query(None, description="平台过滤"),
    max_change: float = Query(-5.0, le=0, ge=-100, description="最大跌幅"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """获取正在下跌的题材
    
    例如：全民转职连续3天下跌12%，可能正在退潮
    """
    try:
        declining = await service.get_declining_genres(platform, max_change, limit)
        return {
            "total": len(declining),
            "items": declining,
        }
    except Exception as e:
        logger.error(f"Failed to get declining genres: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[AlertResponse], summary="获取活跃预警")
async def get_active_alerts(
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    alert_repo = Depends(get_alert_repo),
):
    """获取所有活跃的趋势预警"""
    try:
        alerts = await alert_repo.list_active_alerts(limit)
        return [a.to_dict() for a in alerts]
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{genre}", response_model=List[AlertResponse], summary="获取题材预警")
async def get_genre_alerts(
    genre: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    alert_repo = Depends(get_alert_repo),
):
    """获取某题材的所有预警"""
    try:
        alerts = await alert_repo.get_alerts_by_genre(genre, limit)
        return [a.to_dict() for a in alerts]
    except Exception as e:
        logger.error(f"Failed to get genre alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="获取题材历史数据")
async def get_genre_history(
    platform: str = Query("fanqie", description="平台"),
    category: str = Query(..., description="分类"),
    days: int = Query(30, ge=1, le=90, description="历史天数"),
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """获取题材的详细历史数据（用于绘制趋势图）"""
    try:
        history = await service.get_genre_history(platform, category, days)
        return history
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snapshot/batch-save", summary="批量保存快照")
async def batch_save_snapshots(
    snapshots: List[SaveSnapshotRequest],
    background_tasks: BackgroundTasks,
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """批量保存多个快照（用于定时任务）"""
    async def save_all():
        for snap in snapshots:
            try:
                await service.save_daily_snapshot(
                    platform=snap.platform,
                    category=snap.category,
                    items=snap.items,
                )
            except Exception as e:
                logger.error(f"Failed to save snapshot {snap.platform}/{snap.category}: {e}")
    
    background_tasks.add_task(save_all)
    
    return {
        "message": "Batch save started",
        "total": len(snapshots),
    }
