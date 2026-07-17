"""动态模板实体 - AI自动发现的爆款模板"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class TemplateType(str, Enum):
    """模板类型"""
    GOLDEN_FINGER = "golden_finger"      # 金手指模板
    CHARACTER = "character"               # 人物模板
    WORLDVIEW = "worldview"               # 世界观模板
    COOL_POINT = "cool_point"             # 爽点模板
    OPENING = "opening"                   # 开局模板
    PLOT_STRUCTURE = "plot_structure"     # 剧情结构模板
    PACING = "pacing"                     # 节奏模板


class TrendDirection(str, Enum):
    """趋势方向"""
    RISING = "rising"      # 上升
    STABLE = "stable"      # 稳定
    DECLINING = "declining"  # 下降


@dataclass
class SourceNovel:
    """来源小说信息"""
    platform: str                    # 平台：fanqie, qidian, qimao
    novel_id: str                    # 小说ID
    novel_name: str                  # 小说名称
    author: str                      # 作者
    rank: int                        # 排名
    category: str                    # 分类
    word_count: int = 0              # 字数
    popularity: int = 0              # 热度
    score: float = 0.0               # 评分
    collected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TemplatePattern:
    """模板模式 - 从爆款中提取的规律"""
    name: str                                   # 模式名称
    description: str                            # 描述
    pattern_type: TemplateType                  # 模式类型
    genre: str                                  # 适用题材
    content: str                                # 模板内容/设定
    source_novels: List[SourceNovel] = field(default_factory=list)  # 来源小说
    occurrence_count: int = 1                   # 出现次数（多少本爆款中出现）
    avg_rank: float = 0.0                       # 平均排名
    trend: TrendDirection = TrendDirection.STABLE  # 趋势
    trend_value: float = 0.0                    # 趋势变化值
    confidence_score: float = 0.0               # 置信度（0-1）
    tags: List[str] = field(default_factory=list)      # 标签
    metadata: Dict[str, Any] = field(default_factory=dict)  # 扩展元数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiscoveredTemplate:
    """已发现的动态模板"""
    id: str
    pattern: TemplatePattern
    status: str = "active"                       # active, deprecated, trending
    usage_count: int = 0                         # 使用次数
    last_used_at: Optional[datetime] = None     # 最后使用时间
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.pattern.name,
            "description": self.pattern.description,
            "pattern_type": self.pattern.pattern_type.value,
            "genre": self.pattern.genre,
            "content": self.pattern.content,
            "occurrence_count": self.pattern.occurrence_count,
            "avg_rank": self.pattern.avg_rank,
            "trend": self.pattern.trend.value,
            "trend_value": self.pattern.trend_value,
            "confidence_score": self.pattern.confidence_score,
            "tags": self.pattern.tags,
            "source_novels": [
                {
                    "platform": n.platform,
                    "novel_name": n.novel_name,
                    "rank": n.rank,
                } for n in self.pattern.source_novels
            ],
            "status": self.status,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }