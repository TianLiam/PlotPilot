"""历史榜单快照实体 - 每日保存的榜单数据"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class RankingSnapshotItem:
    """快照中的单个小说条目"""
    platform: str
    category: str
    novel_id: str
    novel_name: str
    author: str
    rank: int
    word_count: int = 0
    popularity: int = 0
    score: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class RankingSnapshot:
    """某一天的榜单快照"""
    snapshot_date: str              # 日期 YYYY-MM-DD
    platform: str                   # 平台
    category: str                   # 分类
    items: List[RankingSnapshotItem] = field(default_factory=list)
    total_count: int = 0            # 榜单总条目数
    collected_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_date": self.snapshot_date,
            "platform": self.platform,
            "category": self.category,
            "total_count": self.total_count,
            "items": [
                {
                    "platform": i.platform,
                    "category": i.category,
                    "novel_id": i.novel_id,
                    "novel_name": i.novel_name,
                    "author": i.author,
                    "rank": i.rank,
                    "word_count": i.word_count,
                    "popularity": i.popularity,
                    "score": i.score,
                    "tags": i.tags,
                } for i in self.items
            ],
        }


@dataclass
class HotTopicSnapshotItem:
    """热点快照条目"""
    source: str                     # 来源：weibo, baidu, zhihu
    title: str
    rank: int
    hot_value: int = 0
    category: str = ""
    keywords: List[str] = field(default_factory=list)
    url: str = ""


@dataclass
class HotTopicSnapshot:
    """某一天的热点快照"""
    snapshot_date: str
    source: str                     # weibo, baidu, zhihu
    items: List[HotTopicSnapshotItem] = field(default_factory=list)
    total_count: int = 0
    collected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GenreTrend:
    """题材趋势分析结果"""
    genre: str
    platform: str
    
    # 当前状态
    current_score: float = 0.0          # 当前热度分
    current_top_rank: int = 999         # 当前最高排名
    
    # 变化指标
    score_change_1d: float = 0.0        # 1天变化
    score_change_3d: float = 0.0        # 3天变化
    score_change_7d: float = 0.0        # 7天变化
    
    # 趋势方向
    trend: str = "stable"               # rising, stable, declining
    trend_strength: float = 0.0         # 趋势强度 0-1
    
    # 预警信息
    alert_level: str = "normal"         # normal, warning, danger
    alert_message: str = ""
    
    # 历史数据点
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "genre": self.genre,
            "platform": self.platform,
            "current_score": round(self.current_score, 2),
            "current_top_rank": self.current_top_rank,
            "score_change_1d": round(self.score_change_1d, 2),
            "score_change_3d": round(self.score_change_3d, 2),
            "score_change_7d": round(self.score_change_7d, 2),
            "trend": self.trend,
            "trend_strength": round(self.trend_strength, 2),
            "alert_level": self.alert_level,
            "alert_message": self.alert_message,
            "history_points": len(self.history),
        }


@dataclass
class TrendAlert:
    """趋势预警"""
    alert_type: str                   # rising, declining, surge, decline
    severity: str                     # info, warning, danger
    genre: str
    platform: str
    message: str                      # 预警消息
    change_value: float = 0.0
    duration_days: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "genre": self.genre,
            "platform": self.platform,
            "message": self.message,
            "change_value": round(self.change_value, 2),
            "duration_days": self.duration_days,
            "created_at": self.created_at.isoformat(),
        }
