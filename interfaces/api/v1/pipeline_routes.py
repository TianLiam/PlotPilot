"""多Agent流水线API路由"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from engine.pipeline.orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelineRequest(BaseModel):
    """流水线请求"""
    genres: List[str] = Field(default_factory=list, description="题材偏好")
    golden_fingers: List[str] = Field(default_factory=list, description="金手指偏好")
    target_words: int = Field(default=500000, description="目标字数")
    chapters_to_write: int = Field(default=3, ge=1, le=10, description="写作章节数")
    platforms: List[str] = Field(default=["fanqie"], description="数据平台")


@router.post("/create", summary="创建流水线")
async def create_pipeline(request: PipelineRequest):
    """创建新的多Agent流水线
    
    流程：
    1. Agent1 扫榜：爬取起点/番茄/七猫榜单
    2. Agent2 趋势分析：分析题材涨跌
    3. Agent3 题材策划：确定题材+金手指+卖点
    4. Agent4 人物设计：设计主角/反派/配角
    5. Agent5 世界观设计：力量体系/地点/势力
    6. Agent6 节奏安排：幕结构/节拍表/爽点分布
    7. Agent7 章节写作：实际写内容
    8. Agent8 质量检测：文风/节奏/问题检测
    9. Agent9 修文：根据问题修改
    """
    orchestrator = get_orchestrator()
    
    run = await orchestrator.create_pipeline(request.dict())
    
    return {
        "pipeline_id": run.pipeline_id,
        "status": run.status.value,
        "message": "Pipeline created. Call /pipeline/{id}/run to start.",
    }


@router.post("/{pipeline_id}/run", summary="运行流水线")
async def run_pipeline(
    pipeline_id: str,
    start_from: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
):
    """运行流水线
    
    Args:
        pipeline_id: 流水线ID
        start_from: 从哪个Agent开始恢复（可选）
    """
    orchestrator = get_orchestrator()
    
    # 后台运行
    async def run_task():
        await orchestrator.run_pipeline(pipeline_id, start_from)
    
    background_tasks.add_task(run_task)
    
    return {
        "pipeline_id": pipeline_id,
        "message": "Pipeline started in background",
    }


@router.post("/run-full", summary="一键运行完整流水线")
async def run_full_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
):
    """一键运行完整流水线（创建+运行+返回结果）
    
    这是主要入口，适合自动化场景。
    """
    orchestrator = get_orchestrator()
    
    run = await orchestrator.create_pipeline(request.dict())
    
    # 后台运行
    async def run_task():
        await orchestrator.run_pipeline(run.pipeline_id)
    
    background_tasks.add_task(run_task)
    
    return {
        "pipeline_id": run.pipeline_id,
        "status": "started",
        "message": "Pipeline started. Use GET /pipeline/{id} to check progress.",
    }


@router.get("/{pipeline_id}", summary="获取流水线状态")
async def get_pipeline_status(pipeline_id: str):
    """获取流水线执行状态和进度"""
    orchestrator = get_orchestrator()
    run = orchestrator.get_pipeline(pipeline_id)
    
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return run.to_dict()


@router.get("", summary="列出所有流水线")
async def list_pipelines():
    """列出所有流水线运行记录"""
    orchestrator = get_orchestrator()
    return orchestrator.list_pipelines()


@router.post("/{pipeline_id}/pause", summary="暂停流水线")
async def pause_pipeline(pipeline_id: str):
    """暂停流水线"""
    orchestrator = get_orchestrator()
    success = await orchestrator.pause_pipeline(pipeline_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot pause pipeline")
    
    return {"message": "Pipeline paused", "pipeline_id": pipeline_id}


@router.post("/{pipeline_id}/resume", summary="恢复流水线")
async def resume_pipeline(pipeline_id: str):
    """从暂停处恢复流水线"""
    orchestrator = get_orchestrator()
    run = await orchestrator.resume_pipeline(pipeline_id)
    
    return run.to_dict()


@router.get("/{pipeline_id}/output", summary="获取最终输出")
async def get_pipeline_output(pipeline_id: str):
    """获取流水线的最终输出（策划案+章节内容）"""
    orchestrator = get_orchestrator()
    run = orchestrator.get_pipeline(pipeline_id)
    
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    if run.status.value != "completed":
        raise HTTPException(status_code=400, detail=f"Pipeline not completed: {run.status.value}")
    
    return run.final_output


@router.get("/agents/list", summary="获取Agent列表")
async def list_agents():
    """获取所有Agent类型和说明"""
    return [
        {
            "type": "scan_ranking",
            "name": "扫榜Agent",
            "description": "爬取起点、番茄、七猫等平台排行榜",
            "dependencies": [],
        },
        {
            "type": "trend_analysis",
            "name": "趋势分析Agent",
            "description": "分析题材涨跌、发现创作机会",
            "dependencies": ["scan_ranking"],
        },
        {
            "type": "topic_planning",
            "name": "题材策划Agent",
            "description": "确定题材、金手指、核心卖点",
            "dependencies": ["scan_ranking", "trend_analysis"],
        },
        {
            "type": "character_design",
            "name": "人物设计Agent",
            "description": "设计主角、反派、配角和关系网",
            "dependencies": ["topic_planning"],
        },
        {
            "type": "worldview_design",
            "name": "世界观设计Agent",
            "description": "设计力量体系、地点、势力、规则",
            "dependencies": ["topic_planning", "character_design"],
        },
        {
            "type": "pacing",
            "name": "节奏安排Agent",
            "description": "规划幕结构、节拍表、爽点分布",
            "dependencies": ["topic_planning", "character_design", "worldview_design"],
        },
        {
            "type": "writing",
            "name": "章节写作Agent",
            "description": "根据策划案写出章节内容",
            "dependencies": ["topic_planning", "character_design", "worldview_design", "pacing"],
        },
        {
            "type": "quality_check",
            "name": "质量检测Agent",
            "description": "检测文风、节奏、问题",
            "dependencies": ["writing"],
        },
        {
            "type": "revision",
            "name": "修文Agent",
            "description": "根据检测结果修改内容",
            "dependencies": ["writing", "quality_check"],
        },
    ]