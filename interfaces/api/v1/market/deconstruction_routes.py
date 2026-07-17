"""拆书API路由"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.market.sqlite_dynamic_template_repository import SqliteDynamicTemplateRepository
from application.market.deconstruction.novel_deconstruction_service import NovelDeconstructionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market/deconstruction", tags=["market-deconstruction"])


def get_deconstruction_service():
    db = get_database()
    template_repo = SqliteDynamicTemplateRepository(db)
    return NovelDeconstructionService(db, template_repo=template_repo)


class DeconstructRequest(BaseModel):
    platform: str = Field(default="fanqie", description="平台")
    book_id: str = Field(..., description="小说ID")
    max_chapters: int = Field(default=30, ge=5, le=50)


@router.post("/run", summary="拆解小说")
async def deconstruct_novel(
    request: DeconstructRequest,
    background_tasks: BackgroundTasks,
    service: NovelDeconstructionService = Depends(get_deconstruction_service),
):
    """对单本爆款小说进行深度拆解
    
    流程：
    1. 爬取免费章节
    2. AI逐章分析（节奏/情绪/爽点/冲突/钩子）
    3. 提取人物模型、剧情结构、金手指设计
    4. 生成爆款DNA（可复用模板）
    5. 沉淀到模板库
    """
    try:
        result = await service.deconstruct_novel(
            platform=request.platform,
            book_id=request.book_id,
            max_chapters=request.max_chapters,
        )
        return result.to_dict()
    except Exception as e:
        logger.error(f"Deconstruction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deconstruction_id}", summary="获取拆书详情")
async def get_deconstruction(
    deconstruction_id: str,
    service: NovelDeconstructionService = Depends(get_deconstruction_service),
):
    """获取拆书详情"""
    result = await service.get_deconstruction(deconstruction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Deconstruction not found")
    return result


@router.get("", summary="列出拆书结果")
async def list_deconstructions(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    service: NovelDeconstructionService = Depends(get_deconstruction_service),
):
    """列出已完成的拆书结果"""
    return await service.list_deconstructions(platform, category, limit)


@router.get("/dna/library", summary="获取DNA库")
async def get_dna_library(
    limit: int = 50,
    service: NovelDeconstructionService = Depends(get_deconstruction_service),
):
    """获取所有拆书沉淀的爆款DNA"""
    return await service.get_dna_library(limit)


@router.get("/dna/{deconstruction_id}", summary="获取单本DNA")
async def get_single_dna(
    deconstruction_id: str,
    service: NovelDeconstructionService = Depends(get_deconstruction_service),
):
    """获取某本小说的爆款DNA"""
    result = await service.get_deconstruction(deconstruction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result.get("dna") if isinstance(result, dict) else None
