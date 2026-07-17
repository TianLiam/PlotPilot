"""趋势预测模块"""
from domain.market.entities.trend_snapshot import (
    RankingSnapshot,
    RankingSnapshotItem,
    HotTopicSnapshot,
    HotTopicSnapshotItem,
    GenreTrend,
    TrendAlert,
)
from domain.market.repositories.snapshot_repository import (
    SnapshotRepository,
    TrendAlertRepository,
)
from infrastructure.persistence.database.market.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
    SqliteTrendAlertRepository,
)
from application.market.trend.trend_analysis_service import TrendAnalysisService

__all__ = [
    "RankingSnapshot",
    "RankingSnapshotItem",
    "HotTopicSnapshot",
    "HotTopicSnapshotItem",
    "GenreTrend",
    "TrendAlert",
    "SnapshotRepository",
    "TrendAlertRepository",
    "SqliteSnapshotRepository",
    "SqliteTrendAlertRepository",
    "TrendAnalysisService",
]