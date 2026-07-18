"""历史快照仓储接口"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import date

from domain.market.entities.trend_snapshot import (
    RankingSnapshot,
    HotTopicSnapshot,
)


class SnapshotRepository(ABC):
    """历史快照仓储接口"""
    
    # ── 榜单快照 ──
    
    @abstractmethod
    async def save_ranking_snapshot(self, snapshot: RankingSnapshot) -> None:
        """保存榜单快照"""
        pass
    
    @abstractmethod
    async def get_ranking_snapshot(
        self,
        snapshot_date: str,
        platform: str,
        category: str,
    ) -> Optional[RankingSnapshot]:
        """获取某天的快照"""
        pass
    
    @abstractmethod
    async def get_ranking_history(
        self,
        platform: str,
        category: str,
        days: int = 7,
    ) -> List[RankingSnapshot]:
        """获取历史快照列表"""
        pass
    
    @abstractmethod
    async def get_ranking_dates(
        self,
        platform: str,
        category: str,
        days: int = 30,
    ) -> List[str]:
        """获取有数据的日期列表"""
        pass

    @abstractmethod
    async def list_ranking_series(self, days: int = 30) -> List[Dict[str, Any]]:
        """列出时间窗口内存在快照的平台/分类序列"""
        pass
    
    # ── 热点快照 ──
    
    @abstractmethod
    async def save_hot_topic_snapshot(self, snapshot: HotTopicSnapshot) -> None:
        """保存热点快照"""
        pass
    
    @abstractmethod
    async def get_hot_topic_history(
        self,
        source: str,
        days: int = 7,
    ) -> List[HotTopicSnapshot]:
        """获取热点历史快照"""
        pass


class TrendAlertRepository(ABC):
    """趋势预警仓储接口"""
    
    @abstractmethod
    async def save_alert(self, alert) -> None:
        """保存预警"""
        pass
    
    @abstractmethod
    async def list_active_alerts(self, limit: int = 50) -> List:
        """获取活跃预警"""
        pass
    
    @abstractmethod
    async def get_alerts_by_genre(self, genre: str, limit: int = 20) -> List:
        """获取某题材的预警"""
        pass
