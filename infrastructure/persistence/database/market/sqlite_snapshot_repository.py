"""历史快照SQLite仓储实现"""
import json
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional

from domain.market.entities.trend_snapshot import (
    RankingSnapshot,
    RankingSnapshotItem,
    HotTopicSnapshot,
    HotTopicSnapshotItem,
    TrendAlert,
)
from domain.market.repositories.snapshot_repository import (
    SnapshotRepository,
    TrendAlertRepository,
)
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SqliteSnapshotRepository(SnapshotRepository):
    """SQLite历史快照仓储"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_tables()
    
    def _ensure_tables(self):
        """创建表"""
        # 榜单快照表
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS ranking_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TEXT NOT NULL,
                platform TEXT NOT NULL,
                category TEXT NOT NULL,
                items_json TEXT NOT NULL,
                total_count INTEGER DEFAULT 0,
                collected_at TEXT NOT NULL,
                UNIQUE(snapshot_date, platform, category)
            )
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_ranking_snapshots_date
            ON ranking_snapshots(snapshot_date, platform, category)
        """)
        
        # 热点快照表
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS hot_topic_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TEXT NOT NULL,
                source TEXT NOT NULL,
                items_json TEXT NOT NULL,
                total_count INTEGER DEFAULT 0,
                collected_at TEXT NOT NULL,
                UNIQUE(snapshot_date, source)
            )
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_hot_topic_snapshots_date
            ON hot_topic_snapshots(snapshot_date, source)
        """)
        
        # 趋势预警表
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS trend_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                genre TEXT NOT NULL,
                platform TEXT NOT NULL,
                message TEXT NOT NULL,
                change_value REAL DEFAULT 0,
                duration_days INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_trend_alerts_active
            ON trend_alerts(is_active, created_at DESC)
        """)
        
        self.db.commit()
    
    async def save_ranking_snapshot(self, snapshot: RankingSnapshot) -> None:
        """保存榜单快照"""
        items_json = json.dumps([
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
            } for i in snapshot.items
        ])
        
        self.db.execute("""
            INSERT INTO ranking_snapshots 
            (snapshot_date, platform, category, items_json, total_count, collected_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(snapshot_date, platform, category) DO UPDATE SET
                items_json = excluded.items_json,
                total_count = excluded.total_count,
                collected_at = excluded.collected_at
        """, (
            snapshot.snapshot_date,
            snapshot.platform,
            snapshot.category,
            items_json,
            snapshot.total_count,
            snapshot.collected_at.isoformat(),
        ))
        self.db.commit()
    
    async def get_ranking_snapshot(
        self,
        snapshot_date: str,
        platform: str,
        category: str,
    ) -> Optional[RankingSnapshot]:
        """获取某天的快照"""
        row = self.db.fetch_one(
            """SELECT * FROM ranking_snapshots 
               WHERE snapshot_date = ? AND platform = ? AND category = ?""",
            (snapshot_date, platform, category)
        )
        
        if not row:
            return None
        
        return self._row_to_ranking_snapshot(dict(row))
    
    async def get_ranking_history(
        self,
        platform: str,
        category: str,
        days: int = 7,
    ) -> List[RankingSnapshot]:
        """获取历史快照列表"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        rows = self.db.fetch_all(
            """SELECT * FROM ranking_snapshots 
               WHERE platform = ? AND category = ? AND snapshot_date >= ?
               ORDER BY snapshot_date DESC""",
            (platform, category, cutoff)
        )
        
        return [self._row_to_ranking_snapshot(dict(row)) for row in rows]
    
    async def get_ranking_dates(
        self,
        platform: str,
        category: str,
        days: int = 30,
    ) -> List[str]:
        """获取有数据的日期列表"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        rows = self.db.fetch_all(
            """SELECT DISTINCT snapshot_date FROM ranking_snapshots 
               WHERE platform = ? AND category = ? AND snapshot_date >= ?
               ORDER BY snapshot_date DESC""",
            (platform, category, cutoff)
        )
        
        return [row["snapshot_date"] for row in rows]
    
    def _row_to_ranking_snapshot(self, row: dict) -> RankingSnapshot:
        """数据库行转快照实体"""
        items_data = json.loads(row.get("items_json", "[]"))
        items = [
            RankingSnapshotItem(
                platform=i.get("platform", ""),
                category=i.get("category", ""),
                novel_id=i.get("novel_id", ""),
                novel_name=i.get("novel_name", ""),
                author=i.get("author", ""),
                rank=i.get("rank", 0),
                word_count=i.get("word_count", 0),
                popularity=i.get("popularity", 0),
                score=i.get("score", 0.0),
            ) for i in items_data
        ]
        
        return RankingSnapshot(
            snapshot_date=row["snapshot_date"],
            platform=row["platform"],
            category=row["category"],
            items=items,
            total_count=row.get("total_count", 0),
            collected_at=datetime.fromisoformat(row["collected_at"]) if row.get("collected_at") else datetime.utcnow(),
        )
    
    # ── 热点快照 ──
    
    async def save_hot_topic_snapshot(self, snapshot: HotTopicSnapshot) -> None:
        """保存热点快照"""
        items_json = json.dumps([
            {
                "source": i.source,
                "title": i.title,
                "rank": i.rank,
                "hot_value": i.hot_value,
                "category": i.category,
                "keywords": i.keywords,
                "url": i.url,
            } for i in snapshot.items
        ])
        
        self.db.execute("""
            INSERT INTO hot_topic_snapshots 
            (snapshot_date, source, items_json, total_count, collected_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(snapshot_date, source) DO UPDATE SET
                items_json = excluded.items_json,
                total_count = excluded.total_count,
                collected_at = excluded.collected_at
        """, (
            snapshot.snapshot_date,
            snapshot.source,
            items_json,
            snapshot.total_count,
            snapshot.collected_at.isoformat(),
        ))
        self.db.commit()
    
    async def get_hot_topic_history(
        self,
        source: str,
        days: int = 7,
    ) -> List[HotTopicSnapshot]:
        """获取热点历史"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        rows = self.db.fetch_all(
            """SELECT * FROM hot_topic_snapshots 
               WHERE source = ? AND snapshot_date >= ?
               ORDER BY snapshot_date DESC""",
            (source, cutoff)
        )
        
        snapshots = []
        for row in rows:
            row = dict(row)
            items_data = json.loads(row.get("items_json", "[]"))
            items = [
                HotTopicSnapshotItem(
                    source=i.get("source", ""),
                    title=i.get("title", ""),
                    rank=i.get("rank", 0),
                    hot_value=i.get("hot_value", 0),
                    category=i.get("category", ""),
                    keywords=i.get("keywords", []),
                    url=i.get("url", ""),
                ) for i in items_data
            ]
            
            snapshots.append(HotTopicSnapshot(
                snapshot_date=row["snapshot_date"],
                source=row["source"],
                items=items,
                total_count=row.get("total_count", 0),
                collected_at=datetime.fromisoformat(row["collected_at"]) if row.get("collected_at") else datetime.utcnow(),
            ))
        
        return snapshots


class SqliteTrendAlertRepository(TrendAlertRepository):
    """SQLite趋势预警仓储"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    async def save_alert(self, alert: TrendAlert) -> None:
        """保存预警"""
        # 检查是否已存在相同题材+类型的活跃预警
        existing = self.db.fetch_one(
            """SELECT id FROM trend_alerts 
               WHERE genre = ? AND platform = ? AND alert_type = ? AND is_active = 1
               LIMIT 1""",
            (alert.genre, alert.platform, alert.alert_type)
        )
        
        if existing:
            # 更新已有预警
            self.db.execute(
                """UPDATE trend_alerts 
                   SET message = ?, change_value = ?, duration_days = ?,
                       severity = ?, created_at = ?
                   WHERE id = ?""",
                (
                    alert.message,
                    alert.change_value,
                    alert.duration_days,
                    alert.severity,
                    alert.created_at.isoformat(),
                    existing["id"],
                )
            )
        else:
            # 插入新预警
            self.db.execute(
                """INSERT INTO trend_alerts 
                   (alert_type, severity, genre, platform, message, 
                    change_value, duration_days, is_active, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)""",
                (
                    alert.alert_type,
                    alert.severity,
                    alert.genre,
                    alert.platform,
                    alert.message,
                    alert.change_value,
                    alert.duration_days,
                    alert.created_at.isoformat(),
                )
            )
        
        self.db.commit()
    
    async def list_active_alerts(self, limit: int = 50) -> List[TrendAlert]:
        """获取活跃预警"""
        rows = self.db.fetch_all(
            """SELECT * FROM trend_alerts 
               WHERE is_active = 1
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,)
        )
        
        return [self._row_to_alert(dict(row)) for row in rows]
    
    async def get_alerts_by_genre(self, genre: str, limit: int = 20) -> List[TrendAlert]:
        """获取某题材的预警"""
        rows = self.db.fetch_all(
            """SELECT * FROM trend_alerts 
               WHERE genre = ? AND is_active = 1
               ORDER BY created_at DESC
               LIMIT ?""",
            (genre, limit)
        )
        
        return [self._row_to_alert(dict(row)) for row in rows]
    
    def _row_to_alert(self, row: dict) -> TrendAlert:
        return TrendAlert(
            alert_type=row["alert_type"],
            severity=row["severity"],
            genre=row["genre"],
            platform=row["platform"],
            message=row["message"],
            change_value=row.get("change_value", 0.0),
            duration_days=row.get("duration_days", 0),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
        )