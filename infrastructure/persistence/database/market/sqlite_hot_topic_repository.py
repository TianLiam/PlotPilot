import logging
import json
from datetime import datetime
from typing import List, Optional
from domain.market.entities.hot_topic import HotTopic
from domain.market.repositories.hot_topic_repository import HotTopicRepository
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SqliteHotTopicRepository(HotTopicRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS hot_topics (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                rank INTEGER NOT NULL,
                hot_value INTEGER,
                category TEXT DEFAULT '',
                keywords TEXT DEFAULT '[]',
                related_topics TEXT DEFAULT '[]',
                collected_at TEXT NOT NULL,
                extra_data TEXT DEFAULT '{}',
                UNIQUE(source, title, collected_at)
            )
        """
        self.db.execute(sql)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_hot_topics_source ON hot_topics(source)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_hot_topics_collected_at ON hot_topics(collected_at)")
        self.db.get_connection().commit()

    def save(self, hot_topic: HotTopic) -> None:
        sql = """
            INSERT INTO hot_topics (
                id, source, title, rank, hot_value, category,
                keywords, related_topics, collected_at, extra_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                source = excluded.source,
                title = excluded.title,
                rank = excluded.rank,
                hot_value = excluded.hot_value,
                category = excluded.category,
                keywords = excluded.keywords,
                related_topics = excluded.related_topics,
                collected_at = excluded.collected_at,
                extra_data = excluded.extra_data
        """
        self.db.execute(sql, (
            hot_topic.id,
            hot_topic.source,
            hot_topic.title,
            hot_topic.rank,
            hot_topic.hot_value,
            hot_topic.category,
            json.dumps(hot_topic.keywords),
            json.dumps(hot_topic.related_topics),
            hot_topic.collected_at.isoformat() if hot_topic.collected_at else datetime.utcnow().isoformat(),
            json.dumps(hot_topic.extra_data)
        ))
        self.db.get_connection().commit()

    def save_batch(self, hot_topics: List[HotTopic]) -> None:
        sql = """
            INSERT INTO hot_topics (
                id, source, title, rank, hot_value, category,
                keywords, related_topics, collected_at, extra_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                source = excluded.source,
                title = excluded.title,
                rank = excluded.rank,
                hot_value = excluded.hot_value,
                category = excluded.category,
                keywords = excluded.keywords,
                related_topics = excluded.related_topics,
                collected_at = excluded.collected_at,
                extra_data = excluded.extra_data
        """
        params = []
        for ht in hot_topics:
            params.append((
                ht.id,
                ht.source,
                ht.title,
                ht.rank,
                ht.hot_value,
                ht.category,
                json.dumps(ht.keywords),
                json.dumps(ht.related_topics),
                ht.collected_at.isoformat() if ht.collected_at else datetime.utcnow().isoformat(),
                json.dumps(ht.extra_data)
            ))
        self.db.execute_many(sql, params)

    def get_by_id(self, hot_topic_id: str) -> Optional[HotTopic]:
        sql = "SELECT * FROM hot_topics WHERE id = ?"
        row = self.db.fetch_one(sql, (hot_topic_id,))
        return self._row_to_entity(row) if row else None

    def get_by_source(self, source: str) -> List[HotTopic]:
        sql = "SELECT * FROM hot_topics WHERE source = ? ORDER BY collected_at DESC, rank ASC"
        rows = self.db.fetch_all(sql, (source,))
        return [self._row_to_entity(row) for row in rows]

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[HotTopic]:
        sql = "SELECT * FROM hot_topics WHERE collected_at >= ? AND collected_at <= ? ORDER BY collected_at DESC"
        rows = self.db.fetch_all(sql, (start_date.isoformat(), end_date.isoformat()))
        return [self._row_to_entity(row) for row in rows]

    def get_latest(self, limit: int = 50) -> List[HotTopic]:
        sql = "SELECT * FROM hot_topics ORDER BY collected_at DESC, rank ASC LIMIT ?"
        rows = self.db.fetch_all(sql, (limit,))
        return [self._row_to_entity(row) for row in rows]

    def delete_by_date_before(self, date: datetime) -> None:
        sql = "DELETE FROM hot_topics WHERE collected_at < ?"
        self.db.execute(sql, (date.isoformat(),))
        self.db.get_connection().commit()

    def _row_to_entity(self, row: dict) -> HotTopic:
        return HotTopic(
            id=row['id'],
            source=row['source'],
            title=row['title'],
            rank=row['rank'],
            hot_value=row.get('hot_value'),
            category=row.get('category', ''),
            keywords=json.loads(row.get('keywords', '[]')),
            related_topics=json.loads(row.get('related_topics', '[]')),
            collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None,
            extra_data=json.loads(row.get('extra_data', '{}'))
        )