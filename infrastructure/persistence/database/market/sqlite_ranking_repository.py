import logging
import json
from datetime import datetime
from typing import List, Optional
from domain.market.entities.ranking import Ranking
from domain.market.repositories.ranking_repository import RankingRepository
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SqliteRankingRepository(RankingRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS rankings (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                category TEXT NOT NULL,
                rank INTEGER NOT NULL,
                novel_name TEXT NOT NULL,
                author TEXT NOT NULL,
                description TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                update_time TEXT,
                word_count INTEGER,
                popularity INTEGER,
                score REAL,
                comments INTEGER,
                favorites INTEGER,
                collected_at TEXT NOT NULL,
                extra_data TEXT DEFAULT '{}',
                UNIQUE(platform, category, rank, collected_at)
            )
        """
        self.db.execute(sql)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_rankings_platform ON rankings(platform)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_rankings_category ON rankings(category)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_rankings_collected_at ON rankings(collected_at)")
        self.db.get_connection().commit()

    def save(self, ranking: Ranking) -> None:
        sql = """
            INSERT INTO rankings (
                id, platform, category, rank, novel_name, author,
                description, tags, update_time, word_count, popularity,
                score, comments, favorites, collected_at, extra_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                platform = excluded.platform,
                category = excluded.category,
                rank = excluded.rank,
                novel_name = excluded.novel_name,
                author = excluded.author,
                description = excluded.description,
                tags = excluded.tags,
                update_time = excluded.update_time,
                word_count = excluded.word_count,
                popularity = excluded.popularity,
                score = excluded.score,
                comments = excluded.comments,
                favorites = excluded.favorites,
                collected_at = excluded.collected_at,
                extra_data = excluded.extra_data
        """
        self.db.execute(sql, (
            ranking.id,
            ranking.platform,
            ranking.category,
            ranking.rank,
            ranking.novel_name,
            ranking.author,
            ranking.description,
            ranking.tags,
            ranking.update_time,
            ranking.word_count,
            ranking.popularity,
            ranking.score,
            ranking.comments,
            ranking.favorites,
            ranking.collected_at.isoformat() if ranking.collected_at else datetime.utcnow().isoformat(),
            json.dumps(ranking.extra_data)
        ))
        self.db.get_connection().commit()

    def save_batch(self, rankings: List[Ranking]) -> None:
        sql = """
            INSERT INTO rankings (
                id, platform, category, rank, novel_name, author,
                description, tags, update_time, word_count, popularity,
                score, comments, favorites, collected_at, extra_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                platform = excluded.platform,
                category = excluded.category,
                rank = excluded.rank,
                novel_name = excluded.novel_name,
                author = excluded.author,
                description = excluded.description,
                tags = excluded.tags,
                update_time = excluded.update_time,
                word_count = excluded.word_count,
                popularity = excluded.popularity,
                score = excluded.score,
                comments = excluded.comments,
                favorites = excluded.favorites,
                collected_at = excluded.collected_at,
                extra_data = excluded.extra_data
        """
        params = []
        for r in rankings:
            params.append((
                r.id,
                r.platform,
                r.category,
                r.rank,
                r.novel_name,
                r.author,
                r.description,
                r.tags,
                r.update_time,
                r.word_count,
                r.popularity,
                r.score,
                r.comments,
                r.favorites,
                r.collected_at.isoformat() if r.collected_at else datetime.utcnow().isoformat(),
                json.dumps(r.extra_data)
            ))
        self.db.execute_many(sql, params)

    def get_by_id(self, ranking_id: str) -> Optional[Ranking]:
        sql = "SELECT * FROM rankings WHERE id = ?"
        row = self.db.fetch_one(sql, (ranking_id,))
        return self._row_to_entity(row) if row else None

    def get_by_platform(self, platform: str) -> List[Ranking]:
        sql = "SELECT * FROM rankings WHERE platform = ? ORDER BY collected_at DESC, rank ASC"
        rows = self.db.fetch_all(sql, (platform,))
        return [self._row_to_entity(row) for row in rows]

    def get_by_platform_and_category(self, platform: str, category: str) -> List[Ranking]:
        sql = "SELECT * FROM rankings WHERE platform = ? AND category = ? ORDER BY collected_at DESC, rank ASC"
        rows = self.db.fetch_all(sql, (platform, category))
        return [self._row_to_entity(row) for row in rows]

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Ranking]:
        sql = "SELECT * FROM rankings WHERE collected_at >= ? AND collected_at <= ? ORDER BY collected_at DESC"
        rows = self.db.fetch_all(sql, (start_date.isoformat(), end_date.isoformat()))
        return [self._row_to_entity(row) for row in rows]

    def get_latest_by_platform(self, platform: str, limit: int = 100) -> List[Ranking]:
        sql = """
            SELECT * FROM rankings 
            WHERE platform = ? 
            ORDER BY collected_at DESC, rank ASC 
            LIMIT ?
        """
        rows = self.db.fetch_all(sql, (platform, limit))
        return [self._row_to_entity(row) for row in rows]

    def delete_by_date_before(self, date: datetime) -> None:
        sql = "DELETE FROM rankings WHERE collected_at < ?"
        self.db.execute(sql, (date.isoformat(),))
        self.db.get_connection().commit()

    def clear_platform_data(self, platform: str) -> None:
        sql = "DELETE FROM rankings WHERE platform = ?"
        self.db.execute(sql, (platform,))
        self.db.get_connection().commit()

    def _row_to_entity(self, row: dict) -> Ranking:
        return Ranking(
            id=row['id'],
            platform=row['platform'],
            category=row['category'],
            rank=row['rank'],
            novel_name=row['novel_name'],
            author=row['author'],
            description=row.get('description', ''),
            tags=row.get('tags', ''),
            update_time=row.get('update_time'),
            word_count=row.get('word_count'),
            popularity=row.get('popularity'),
            score=row.get('score'),
            comments=row.get('comments'),
            favorites=row.get('favorites'),
            collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None,
            extra_data=json.loads(row.get('extra_data', '{}'))
        )