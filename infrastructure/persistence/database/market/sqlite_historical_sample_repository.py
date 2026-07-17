"""历史小说样本库 - 存储已分析的爆款小说样本"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from domain.market.entities.novel_research import HistoricalSample
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class HistoricalSampleRepository:
    """历史样本仓储"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_tables()
    
    def _ensure_tables(self):
        """创建表"""
        # 小说样本表
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS historical_novel_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id TEXT NOT NULL,
                novel_name TEXT NOT NULL,
                author TEXT,
                platform TEXT NOT NULL,
                category TEXT,
                word_count INTEGER DEFAULT 0,
                chapter_count INTEGER DEFAULT 0,
                popularity INTEGER DEFAULT 0,
                avg_chapter_words INTEGER DEFAULT 0,
                golden_fingers TEXT,
                genre_tags TEXT,
                opening_type TEXT,
                is_successful INTEGER DEFAULT 0,
                peak_rank INTEGER DEFAULT 999,
                days_on_chart INTEGER DEFAULT 0,
                trend_direction TEXT DEFAULT 'stable',
                first_seen_date TEXT,
                last_seen_date TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_genre 
            ON historical_novel_samples(platform, category)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_tags 
            ON historical_novel_samples(genre_tags)
        """)
        self.db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_samples_unique
            ON historical_novel_samples(novel_id, platform)
        """)
        self.db.commit()
    
    async def save_sample(self, sample: HistoricalSample) -> None:
        """保存样本"""
        now = datetime.utcnow().isoformat()
        try:
            self.db.execute("""
                INSERT INTO historical_novel_samples 
                (novel_id, novel_name, author, platform, category,
                 word_count, chapter_count, popularity, avg_chapter_words,
                 golden_fingers, genre_tags, opening_type,
                 is_successful, peak_rank, days_on_chart, trend_direction,
                 first_seen_date, last_seen_date, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(novel_id, platform) DO UPDATE SET
                    novel_name = excluded.novel_name,
                    author = excluded.author,
                    category = excluded.category,
                    word_count = excluded.word_count,
                    chapter_count = excluded.chapter_count,
                    popularity = excluded.popularity,
                    avg_chapter_words = excluded.avg_chapter_words,
                    golden_fingers = excluded.golden_fingers,
                    genre_tags = excluded.genre_tags,
                    opening_type = excluded.opening_type,
                    is_successful = excluded.is_successful,
                    peak_rank = excluded.peak_rank,
                    days_on_chart = excluded.days_on_chart,
                    trend_direction = excluded.trend_direction,
                    last_seen_date = excluded.last_seen_date,
                    metadata = excluded.metadata
            """, (
                sample.novel_id,
                sample.novel_name,
                sample.author,
                sample.platform,
                sample.category,
                sample.word_count,
                sample.chapter_count,
                sample.popularity,
                sample.avg_chapter_words,
                json.dumps(sample.golden_fingers),
                json.dumps(sample.genre_tags),
                sample.opening_type,
                1 if sample.is_successful else 0,
                sample.peak_rank,
                sample.days_on_chart,
                sample.trend_direction,
                now,
                now,
                json.dumps({}),
                now,
            ))
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to save sample: {e}")
            self.db.rollback()
    
    async def save_samples_batch(self, samples: List[HistoricalSample]) -> int:
        """批量保存"""
        count = 0
        for sample in samples:
            try:
                await self.save_sample(sample)
                count += 1
            except Exception as e:
                logger.error(f"Failed to save sample {sample.novel_name}: {e}")
        return count
    
    async def find_by_genre(
        self,
        genres: List[str],
        platforms: Optional[List[str]] = None,
        successful_only: bool = True,
        limit: int = 100,
    ) -> List[HistoricalSample]:
        """按题材查找样本"""
        conditions = ["category IN ({})".format(",".join("?" * len(genres)))]
        params: List[Any] = list(genres)
        
        if platforms:
            conditions.append("platform IN ({})".format(",".join("?" * len(platforms))))
            params.extend(platforms)
        
        if successful_only:
            conditions.append("is_successful = 1")
        
        params.append(limit)
        
        sql = f"""SELECT * FROM historical_novel_samples 
                  WHERE {' AND '.join(conditions)}
                  ORDER BY popularity DESC, peak_rank ASC
                  LIMIT ?"""
        
        rows = self.db.fetch_all(sql, params)
        return [self._row_to_sample(dict(row)) for row in rows]
    
    async def find_by_tags(
        self,
        tags: List[str],
        platforms: Optional[List[str]] = None,
        successful_only: bool = True,
        limit: int = 100,
    ) -> List[HistoricalSample]:
        """按标签查找（任何标签匹配）"""
        conditions = []
        params: List[Any] = []
        
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("genre_tags LIKE ?")
            params.append(f"%{tag}%")
        conditions.append(f"({' OR '.join(tag_conditions)})")
        
        if platforms:
            conditions.append("platform IN ({})".format(",".join("?" * len(platforms))))
            params.extend(platforms)
        
        if successful_only:
            conditions.append("is_successful = 1")
        
        params.append(limit)
        
        sql = f"""SELECT * FROM historical_novel_samples 
                  WHERE {' AND '.join(conditions)}
                  ORDER BY popularity DESC
                  LIMIT ?"""
        
        rows = self.db.fetch_all(sql, params)
        return [self._row_to_sample(dict(row)) for row in rows]
    
    async def find_by_golden_finger(
        self,
        golden_fingers: List[str],
        platforms: Optional[List[str]] = None,
        successful_only: bool = True,
        limit: int = 100,
    ) -> List[HistoricalSample]:
        """按金手指标签查找"""
        conditions = []
        params: List[Any] = []
        
        gf_conditions = []
        for gf in golden_fingers:
            gf_conditions.append("golden_fingers LIKE ?")
            params.append(f"%{gf}%")
        conditions.append(f"({' OR '.join(gf_conditions)})")
        
        if platforms:
            conditions.append("platform IN ({})".format(",".join("?" * len(platforms))))
            params.extend(platforms)
        
        if successful_only:
            conditions.append("is_successful = 1")
        
        params.append(limit)
        
        sql = f"""SELECT * FROM historical_novel_samples 
                  WHERE {' AND '.join(conditions)}
                  ORDER BY popularity DESC
                  LIMIT ?"""
        
        rows = self.db.fetch_all(sql, params)
        return [self._row_to_sample(dict(row)) for row in rows]
    
    async def count_by_genre(self, genre: str) -> int:
        """统计某题材的样本数"""
        row = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM historical_novel_samples WHERE category = ?",
            (genre,)
        )
        return row["count"] if row else 0
    
    async def count_successful_by_genre(self, genre: str) -> int:
        """统计某题材的成功样本数"""
        row = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM historical_novel_samples WHERE category = ? AND is_successful = 1",
            (genre,)
        )
        return row["count"] if row else 0
    
    def _row_to_sample(self, row: dict) -> HistoricalSample:
        return HistoricalSample(
            novel_id=row["novel_id"],
            novel_name=row["novel_name"],
            author=row.get("author", ""),
            platform=row["platform"],
            category=row.get("category", ""),
            word_count=row.get("word_count", 0),
            chapter_count=row.get("chapter_count", 0),
            popularity=row.get("popularity", 0),
            avg_chapter_words=row.get("avg_chapter_words", 0),
            golden_fingers=json.loads(row.get("golden_fingers", "[]")),
            genre_tags=json.loads(row.get("genre_tags", "[]")),
            opening_type=row.get("opening_type", ""),
            is_successful=bool(row.get("is_successful", 0)),
            peak_rank=row.get("peak_rank", 999),
            days_on_chart=row.get("days_on_chart", 0),
            trend_direction=row.get("trend_direction", "stable"),
        )