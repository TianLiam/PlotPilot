"""动态模板发现API路由"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from domain.market.entities.dynamic_template import TemplateType
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_ranking_repository import SqliteRankingRepository
from infrastructure.persistence.database.market.sqlite_dynamic_template_repository import SqliteDynamicTemplateRepository
from application.market.discovery.template_discovery_service import TemplateDiscoveryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/discovery", tags=["market-discovery"])


# ── 依赖注入 ──

def get_ranking_repo():
    return SqliteRankingRepository(get_database())

def get_template_repo():
    return SqliteDynamicTemplateRepository(get_database())

def get_discovery_service(
    ranking_repo = Depends(get_ranking_repo),
    template_repo = Depends(get_template_repo),
):
    return TemplateDiscoveryService(ranking_repo, template_repo)


# ── 请求/响应模型 ──

class DiscoveryRequest(BaseModel):
    """发现请求"""
    platform: str = Field(default="fanqie", description="平台：fanqie, qidian")
    category: Optional[str] = Field(default=None, description="分类：都市、玄幻等")
    top_n: int = Field(default=5, ge=1, le=20, description="分析前N本小说")
    max_chapters: int = Field(default=20, ge=5, le=50, description="每本最大章节数")


class DailyDiscoveryRequest(BaseModel):
    """每日发现请求"""
    platforms: List[str] = Field(default=["fanqie"], description="平台列表")
    categories: List[str] = Field(default=["都市", "玄幻", "言情", "仙侠"], description="分类列表")
    top_n: int = Field(default=3, ge=1, le=10, description="每个分类分析前N本")


class TemplateResponse(BaseModel):
    """模板响应"""
    id: str
    name: str
    description: str
    pattern_type: str
    genre: str
    content: str
    occurrence_count: int
    avg_rank: float
    trend: str
    trend_value: float
    confidence_score: float
    tags: List[str]
    source_novels: List[dict]
    status: str
    usage_count: int


# ── API端点 ──

@router.post("/run", summary="运行模板发现")
async def run_discovery(
    request: DiscoveryRequest,
    background_tasks: BackgroundTasks,
    service: TemplateDiscoveryService = Depends(get_discovery_service),
):
    """运行模板发现任务（后台执行）
    
    从热门小说中自动发现模板。
    
    流程：
    1. 获取热门榜单
    2. 爬取免费章节
    3. AI分析提取模板
    4. 保存到模板库
    """
    async def run_task():
        try:
            result = await service.discover_from_top_novels(
                platform=request.platform,
                category=request.category,
                top_n=request.top_n,
                max_chapters=request.max_chapters,
            )
            logger.info(f"Discovery completed: {result}")
        except Exception as e:
            logger.error(f"Discovery task failed: {e}")
    
    background_tasks.add_task(run_task)
    
    return {
        "message": "Discovery task started in background",
        "params": request.dict(),
    }


@router.post("/daily", summary="每日自动发现")
async def run_daily_discovery(
    request: DailyDiscoveryRequest,
    background_tasks: BackgroundTasks,
    service: TemplateDiscoveryService = Depends(get_discovery_service),
):
    """运行每日自动发现任务（后台执行）
    
    扫描多个平台和分类，从热门小说中发现模板。
    """
    async def run_task():
        try:
            result = await service.run_daily_discovery(
                platforms=request.platforms,
                categories=request.categories,
                top_n=request.top_n,
            )
            logger.info(f"Daily discovery completed: {result}")
        except Exception as e:
            logger.error(f"Daily discovery task failed: {e}")
    
    background_tasks.add_task(run_task)
    
    return {
        "message": "Daily discovery task started in background",
        "params": request.dict(),
    }


@router.get("/templates", response_model=List[TemplateResponse], summary="获取发现的模板")
async def get_templates(
    pattern_type: Optional[str] = Query(None, description="模板类型：golden_finger, character, worldview, cool_point, opening, pacing"),
    genre: Optional[str] = Query(None, description="题材分类"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    service: TemplateDiscoveryService = Depends(get_discovery_service),
):
    """获取已发现的模板列表
    
    支持按类型和题材筛选。
    """
    try:
        pt = TemplateType(pattern_type) if pattern_type else None
        templates = await service.get_discovered_templates(pt, genre, limit)
        return templates
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid pattern_type: {pattern_type}")
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending", response_model=List[TemplateResponse], summary="获取热门模板")
async def get_trending_templates(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    service: TemplateDiscoveryService = Depends(get_discovery_service),
):
    """获取热门模板（趋势上升的模板）"""
    try:
        templates = await service.get_trending_templates(limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get trending templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=List[TemplateResponse], summary="获取最近发现的模板")
async def get_recent_templates(
    days: int = Query(7, ge=1, le=30, description="最近N天"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    service: TemplateDiscoveryService = Depends(get_discovery_service),
):
    """获取最近发现的模板"""
    try:
        templates = await service.get_recent_discoveries(days, limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get recent templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[TemplateResponse], summary="搜索模板")
async def search_templates(
    keyword: str = Query(..., description="搜索关键词"),
    pattern_type: Optional[str] = Query(None, description="模板类型"),
    genre: Optional[str] = Query(None, description="题材分类"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    service: TemplateDiscoveryService = Depends(get_discovery_service),
):
    """搜索模板"""
    try:
        pt = TemplateType(pattern_type) if pattern_type else None
        templates = await service.search_templates(keyword, pt, genre, limit)
        return templates
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid pattern_type: {pattern_type}")
    except Exception as e:
        logger.error(f"Failed to search templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}", summary="获取模板详情")
async def get_template_detail(
    template_id: str,
    template_repo = Depends(get_template_repo),
):
    """获取单个模板的详细信息"""
    try:
        template = await template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        return template.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/use", summary="标记模板使用")
async def mark_template_used(
    template_id: str,
    template_repo = Depends(get_template_repo),
):
    """标记模板已使用（增加使用次数）"""
    try:
        await template_repo.update_usage(template_id)
        return {"message": "Template usage recorded", "template_id": template_id}
    except Exception as e:
        logger.error(f"Failed to update template usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 模板类型说明 ──

@router.get("/types", summary="获取模板类型列表")
async def get_template_types():
    """获取所有支持的模板类型"""
    return [
        {
            "value": "golden_finger",
            "label": "金手指模板",
            "description": "主角的特殊能力、系统、神器等设定",
        },
        {
            "value": "character",
            "label": "人物模板",
            "description": "主要人物的性格、特点、关系模板",
        },
        {
            "value": "worldview",
            "label": "世界观模板",
            "description": "故事背景、力量体系、社会结构设定",
        },
        {
            "value": "cool_point",
            "label": "爽点模板",
            "description": "让读者感到爽快的设计模式",
        },
        {
            "value": "opening",
            "label": "开局模板",
            "description": "前几章的节奏安排、爽点分布",
        },
        {
            "value": "pacing",
            "label": "节奏模板",
            "description": "剧情推进的节奏模式",
        },
        {
            "value": "plot_structure",
            "label": "剧情结构模板",
            "description": "主线推进方式、支线安排",
        },
    ]