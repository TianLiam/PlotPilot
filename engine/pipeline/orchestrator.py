"""流水线编排器 - 协调多个Agent执行"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from engine.pipeline.entities.pipeline_entities import (
    AgentType,
    AgentStatus,
    PipelineStatus,
    PipelineRun,
    PipelineContext,
)
from engine.pipeline.agents.base_agent import BaseAgent
from engine.pipeline.agents.scan_ranking_agent import ScanRankingAgent
from engine.pipeline.agents.trend_analysis_agent import TrendAnalysisAgent
from engine.pipeline.agents.topic_planning_agent import TopicPlanningAgent
from engine.pipeline.agents.character_design_agent import CharacterDesignAgent
from engine.pipeline.agents.worldview_design_agent import WorldviewDesignAgent
from engine.pipeline.agents.pacing_agent import PacingAgent
from engine.pipeline.agents.writing_quality_revision_agents import (
    WritingAgent,
    QualityCheckAgent,
    RevisionAgent,
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """流水线编排器
    
    协调多个Agent按顺序执行：
    Agent1(扫榜) → Agent2(趋势) → Agent3(题材) → Agent4(人物) 
    → Agent5(世界观) → Agent6(节奏) → Agent7(写作) → Agent8(质检) → Agent9(修文)
    """
    
    # Agent执行顺序
    AGENT_ORDER = [
        AgentType.SCAN_RANKING,
        AgentType.TREND_ANALYSIS,
        AgentType.TOPIC_PLANNING,
        AgentType.CHARACTER_DESIGN,
        AgentType.WORLDVIEW_DESIGN,
        AgentType.PACING,
        AgentType.WRITING,
        AgentType.QUALITY_CHECK,
        AgentType.REVISION,
    ]
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self._init_agents()
        
        # 运行中的流水线
        self.active_pipelines: Dict[str, PipelineRun] = {}
    
    def _init_agents(self):
        """初始化所有Agent"""
        self.agents = {
            AgentType.SCAN_RANKING: ScanRankingAgent(),
            AgentType.TREND_ANALYSIS: TrendAnalysisAgent(),
            AgentType.TOPIC_PLANNING: TopicPlanningAgent(),
            AgentType.CHARACTER_DESIGN: CharacterDesignAgent(),
            AgentType.WORLDVIEW_DESIGN: WorldviewDesignAgent(),
            AgentType.PACING: PacingAgent(),
            AgentType.WRITING: WritingAgent(),
            AgentType.QUALITY_CHECK: QualityCheckAgent(),
            AgentType.REVISION: RevisionAgent(),
        }
    
    async def create_pipeline(
        self,
        user_request: Dict[str, Any],
    ) -> PipelineRun:
        """创建新的流水线运行
        
        Args:
            user_request: 用户请求，例如：
                {
                    "genres": ["末日", "系统"],
                    "golden_fingers": ["签到系统"],
                    "target_words": 1000000,
                    "chapters_to_write": 3,
                    "platforms": ["fanqie"],
                }
        
        Returns:
            PipelineRun对象
        """
        pipeline_id = f"pipeline-{uuid.uuid4().hex[:12]}"
        
        context = PipelineContext(
            pipeline_id=pipeline_id,
            user_request=user_request,
        )
        
        run = PipelineRun(
            pipeline_id=pipeline_id,
            status=PipelineStatus.PENDING,
            user_request=user_request,
            context=context,
            total_agents=len(self.AGENT_ORDER),
        )
        
        # 初始化所有Agent的输出状态（创建新实例，避免共享引用）
        from engine.pipeline.entities.pipeline_entities import AgentOutput, AgentStatus
        for agent_type in self.AGENT_ORDER:
            run.agent_outputs[agent_type.value] = AgentOutput(
                agent_type=agent_type,
                status=AgentStatus.PENDING,
            )
        
        self.active_pipelines[pipeline_id] = run
        
        logger.info(f"Created pipeline {pipeline_id}")
        
        return run
    
    async def run_pipeline(
        self,
        pipeline_id: str,
        start_from: Optional[str] = None,
    ) -> PipelineRun:
        """运行流水线
        
        Args:
            pipeline_id: 流水线ID
            start_from: 从哪个Agent开始（用于恢复）
        
        Returns:
            完成的PipelineRun
        """
        run = self.active_pipelines.get(pipeline_id)
        if not run:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        run.status = PipelineStatus.RUNNING
        run.started_at = datetime.utcnow()
        
        # 确定起始Agent
        start_index = 0
        if start_from:
            try:
                start_index = self.AGENT_ORDER.index(AgentType(start_from))
            except ValueError:
                start_index = 0
        
        try:
            for i, agent_type in enumerate(self.AGENT_ORDER):
                if i < start_index:
                    continue
                
                agent = self.agents[agent_type]
                
                # 检查前置条件
                if not agent.can_run(run.context):
                    logger.warning(f"Agent {agent_type.value} skipped: preconditions not met")
                    run.agent_outputs[agent_type.value].status = AgentStatus.SKIPPED
                    continue
                
                # 更新当前Agent
                run.current_agent = agent_type.value
                
                # 执行Agent
                logger.info(f"Running agent {agent_type.value}")
                output = await agent.run(run.context)
                
                run.agent_outputs[agent_type.value] = output
                
                # 更新进度
                if output.status == AgentStatus.COMPLETED:
                    run.completed_agents += 1
                    run.progress_percent = (run.completed_agents / run.total_agents) * 100
                    run.total_tokens += output.tokens_used
                    run.total_duration_seconds += output.duration_seconds
                    
                    # 保存检查点
                    run.checkpoint_agent = agent_type.value
                    run.checkpoint_data = output.data
                
                elif output.status == AgentStatus.FAILED:
                    run.status = PipelineStatus.FAILED
                    logger.error(f"Pipeline failed at {agent_type.value}: {output.error}")
                    break
            
            # 检查是否完成
            if run.status == PipelineStatus.RUNNING:
                run.status = PipelineStatus.COMPLETED
                run.completed_at = datetime.utcnow()
                
                # 构建最终输出
                run.final_output = self._build_final_output(run)
                
                logger.info(
                    f"Pipeline {pipeline_id} completed. "
                    f"Tokens: {run.total_tokens}, "
                    f"Duration: {run.total_duration_seconds:.1f}s"
                )
                
        except Exception as e:
            logger.error(f"Pipeline {pipeline_id} crashed: {e}")
            run.status = PipelineStatus.FAILED
        
        return run
    
    def _build_final_output(self, run: PipelineRun) -> Dict[str, Any]:
        """构建最终输出"""
        context = run.context
        
        return {
            "pipeline_id": run.pipeline_id,
            "status": run.status.value,
            "topic": {
                "genres": context.topic_result.get("selected_genres", []),
                "golden_fingers": context.topic_result.get("selected_golden_fingers", []),
                "core_selling_point": context.topic_result.get("core_selling_point", ""),
            },
            "characters": context.character_result,
            "worldview": context.worldview_result,
            "pacing": context.pacing_result,
            "writing": {
                "chapters_written": context.writing_result.get("chapters_written", 0),
                "total_words": context.writing_result.get("total_words", 0),
                "chapters": context.writing_result.get("chapters", []),
            },
            "quality": {
                "overall_score": context.quality_result.get("overall_score", 0),
            },
            "summary": {
                "total_tokens": run.total_tokens,
                "total_duration_seconds": run.total_duration_seconds,
            },
        }
    
    async def run_full_pipeline(
        self,
        user_request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """一站式运行完整流水线
        
        Args:
            user_request: 用户请求
        
        Returns:
            最终输出
        """
        run = await self.create_pipeline(user_request)
        run = await self.run_pipeline(run.pipeline_id)
        return run.to_dict()
    
    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineRun]:
        """获取流水线状态"""
        return self.active_pipelines.get(pipeline_id)
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """列出所有流水线"""
        return [run.to_dict() for run in self.active_pipelines.values()]
    
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """暂停流水线"""
        run = self.active_pipelines.get(pipeline_id)
        if run and run.status == PipelineStatus.RUNNING:
            run.status = PipelineStatus.PAUSED
            return True
        return False
    
    async def resume_pipeline(self, pipeline_id: str) -> PipelineRun:
        """恢复流水线"""
        run = self.active_pipelines.get(pipeline_id)
        if run and run.status == PipelineStatus.PAUSED:
            return await self.run_pipeline(
                pipeline_id,
                start_from=run.checkpoint_agent,
            )
        return run


# 全局编排器实例
_orchestrator: Optional[PipelineOrchestrator] = None


def get_orchestrator() -> PipelineOrchestrator:
    """获取全局编排器实例"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PipelineOrchestrator()
    return _orchestrator