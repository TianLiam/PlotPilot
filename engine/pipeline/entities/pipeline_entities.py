"""多Agent流水线实体定义"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class AgentType(str, Enum):
    """Agent类型"""
    SCAN_RANKING = "scan_ranking"           # 扫榜Agent
    TREND_ANALYSIS = "trend_analysis"        # 趋势分析Agent
    TOPIC_PLANNING = "topic_planning"        # 题材策划Agent
    CHARACTER_DESIGN = "character_design"    # 人物设计Agent
    WORLDVIEW_DESIGN = "worldview_design"    # 世界观设计Agent
    PACING = "pacing"                        # 节奏安排Agent
    WRITING = "writing"                      # 章节写作Agent
    QUALITY_CHECK = "quality_check"          # 质量检测Agent
    REVISION = "revision"                    # 修文Agent


class AgentStatus(str, Enum):
    """Agent状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(str, Enum):
    """流水线状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentOutput:
    """Agent输出"""
    agent_type: AgentType
    status: AgentStatus = AgentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_seconds: float = 0.0
    tokens_used: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "data": self.data,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "tokens_used": self.tokens_used,
        }


@dataclass
class PipelineContext:
    """流水线上下文（Agent间共享的数据）"""
    pipeline_id: str
    
    # 用户输入
    user_request: Dict[str, Any] = field(default_factory=dict)
    
    # 各Agent输出（累积）
    scan_result: Dict[str, Any] = field(default_factory=dict)
    trend_result: Dict[str, Any] = field(default_factory=dict)
    topic_result: Dict[str, Any] = field(default_factory=dict)
    character_result: Dict[str, Any] = field(default_factory=dict)
    worldview_result: Dict[str, Any] = field(default_factory=dict)
    pacing_result: Dict[str, Any] = field(default_factory=dict)
    writing_result: Dict[str, Any] = field(default_factory=dict)
    quality_result: Dict[str, Any] = field(default_factory=dict)
    revision_result: Dict[str, Any] = field(default_factory=dict)
    
    # 最终输出
    final_output: Dict[str, Any] = field(default_factory=dict)
    
    def get_agent_output(self, agent_type: AgentType) -> Dict[str, Any]:
        """获取某Agent的输出"""
        output_map = {
            AgentType.SCAN_RANKING: self.scan_result,
            AgentType.TREND_ANALYSIS: self.trend_result,
            AgentType.TOPIC_PLANNING: self.topic_result,
            AgentType.CHARACTER_DESIGN: self.character_result,
            AgentType.WORLDVIEW_DESIGN: self.worldview_result,
            AgentType.PACING: self.pacing_result,
            AgentType.WRITING: self.writing_result,
            AgentType.QUALITY_CHECK: self.quality_result,
            AgentType.REVISION: self.revision_result,
        }
        return output_map.get(agent_type, {})
    
    def set_agent_output(self, agent_type: AgentType, data: Dict[str, Any]):
        """设置某Agent的输出"""
        if agent_type == AgentType.SCAN_RANKING:
            self.scan_result = data
        elif agent_type == AgentType.TREND_ANALYSIS:
            self.trend_result = data
        elif agent_type == AgentType.TOPIC_PLANNING:
            self.topic_result = data
        elif agent_type == AgentType.CHARACTER_DESIGN:
            self.character_result = data
        elif agent_type == AgentType.WORLDVIEW_DESIGN:
            self.worldview_result = data
        elif agent_type == AgentType.PACING:
            self.pacing_result = data
        elif agent_type == AgentType.WRITING:
            self.writing_result = data
        elif agent_type == AgentType.QUALITY_CHECK:
            self.quality_result = data
        elif agent_type == AgentType.REVISION:
            self.revision_result = data


@dataclass
class PipelineRun:
    """一次流水线运行"""
    pipeline_id: str
    status: PipelineStatus = PipelineStatus.PENDING
    
    # 用户请求
    user_request: Dict[str, Any] = field(default_factory=dict)
    # 例如：{"genres": ["末日", "系统"], "target_words": 1000000, "auto_mode": true}
    
    # 上下文
    context: PipelineContext = None
    
    # 各Agent状态
    agent_outputs: Dict[str, AgentOutput] = field(default_factory=dict)
    
    # 当前阶段
    current_agent: Optional[str] = None
    
    # 进度
    total_agents: int = 9
    completed_agents: int = 0
    progress_percent: float = 0.0
    
    # 资源消耗
    total_tokens: int = 0
    total_duration_seconds: float = 0.0
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 检查点（用于恢复）
    checkpoint_agent: Optional[str] = None
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "user_request": self.user_request,
            "current_agent": self.current_agent,
            "total_agents": self.total_agents,
            "completed_agents": self.completed_agents,
            "progress_percent": round(self.progress_percent, 1),
            "total_tokens": self.total_tokens,
            "total_duration_seconds": round(self.total_duration_seconds, 1),
            "agent_outputs": {
                k: v.to_dict() for k, v in self.agent_outputs.items()
            },
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "checkpoint_agent": self.checkpoint_agent,
        }


# Agent输出数据结构

@dataclass
class ScanResult:
    """扫榜Agent输出"""
    platforms: List[str] = field(default_factory=list)
    top_novels: List[Dict[str, Any]] = field(default_factory=list)
    hot_topics: List[Dict[str, Any]] = field(default_factory=list)
    collected_at: str = ""


@dataclass
class TrendResult:
    """趋势分析Agent输出"""
    rising_genres: List[Dict[str, Any]] = field(default_factory=list)
    declining_genres: List[Dict[str, Any]] = field(default_factory=list)
    opportunities: List[Dict[str, Any]] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TopicResult:
    """题材策划Agent输出"""
    selected_genres: List[str] = field(default_factory=list)
    selected_golden_fingers: List[str] = field(default_factory=list)
    core_selling_point: str = ""
    target_audience: str = ""
    differentiation_strategy: str = ""
    success_prediction: float = 0.0


@dataclass
class CharacterResult:
    """人物设计Agent输出"""
    protagonist: Dict[str, Any] = field(default_factory=dict)
    antagonists: List[Dict[str, Any]] = field(default_factory=list)
    supporting_characters: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WorldviewResult:
    """世界观设计Agent输出"""
    world_name: str = ""
    power_system: str = ""
    geography: List[Dict[str, Any]] = field(default_factory=list)
    factions: List[Dict[str, Any]] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)


@dataclass
class PacingResult:
    """节奏安排Agent输出"""
    total_chapters: int = 0
    act_structure: List[Dict[str, Any]] = field(default_factory=list)
    beat_sheet: List[Dict[str, Any]] = field(default_factory=list)
    cool_point_schedule: List[Dict[str, Any]] = field(default_factory=list)
    conflict_schedule: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WritingResult:
    """章节写作Agent输出"""
    chapters_written: int = 0
    total_words: int = 0
    chapters: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class QualityResult:
    """质量检测Agent输出"""
    overall_score: float = 0.0
    style_score: float = 0.0
    pacing_score: float = 0.0
    tension_curve: List[float] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass  
class RevisionResult:
    """修文Agent输出"""
    chapters_revised: int = 0
    revisions: List[Dict[str, Any]] = field(default_factory=list)
    final_score: float = 0.0