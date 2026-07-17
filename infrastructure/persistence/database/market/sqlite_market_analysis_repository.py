import logging
import json
from datetime import datetime
from typing import List, Optional
from domain.market.entities.market_analysis import MarketAnalysis, GenreTrend
from domain.market.repositories.market_analysis_repository import MarketAnalysisRepository
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SqliteMarketAnalysisRepository(MarketAnalysisRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_tables()

    def _ensure_tables(self):
        sql = """
            CREATE TABLE IF NOT EXISTS market_analysis (
                id TEXT PRIMARY KEY,
                analysis_date TEXT NOT NULL,
                platform_summary TEXT DEFAULT '{}',
                genre_trends TEXT DEFAULT '[]',
                hot_topics_summary TEXT DEFAULT '{}',
                recommendations TEXT DEFAULT '[]',
                ai_explanation TEXT DEFAULT '',
                extra_data TEXT DEFAULT '{}'
            )
        """
        self.db.execute(sql)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_market_analysis_date ON market_analysis(analysis_date)")
        self.db.get_connection().commit()

    def save(self, analysis: MarketAnalysis) -> None:
        sql = """
            INSERT INTO market_analysis (
                id, analysis_date, platform_summary, genre_trends,
                hot_topics_summary, recommendations, ai_explanation, extra_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                analysis_date = excluded.analysis_date,
                platform_summary = excluded.platform_summary,
                genre_trends = excluded.genre_trends,
                hot_topics_summary = excluded.hot_topics_summary,
                recommendations = excluded.recommendations,
                ai_explanation = excluded.ai_explanation,
                extra_data = excluded.extra_data
        """
        genre_trends_data = []
        for gt in analysis.genre_trends:
            gt_dict = gt.__dict__.copy()
            for key, value in gt_dict.items():
                if isinstance(value, datetime):
                    gt_dict[key] = value.isoformat()
            genre_trends_data.append(gt_dict)
        
        self.db.execute(sql, (
            analysis.id,
            analysis.analysis_date.isoformat(),
            json.dumps(analysis.platform_summary),
            json.dumps(genre_trends_data),
            json.dumps(analysis.hot_topics_summary),
            json.dumps(analysis.recommendations),
            analysis.ai_explanation,
            json.dumps(analysis.extra_data)
        ))
        self.db.get_connection().commit()

    def get_by_id(self, analysis_id: str) -> Optional[MarketAnalysis]:
        sql = "SELECT * FROM market_analysis WHERE id = ?"
        row = self.db.fetch_one(sql, (analysis_id,))
        return self._row_to_entity(row) if row else None

    def get_latest(self) -> Optional[MarketAnalysis]:
        sql = "SELECT * FROM market_analysis ORDER BY analysis_date DESC LIMIT 1"
        row = self.db.fetch_one(sql)
        return self._row_to_entity(row) if row else None

    def get_by_date(self, date: datetime) -> Optional[MarketAnalysis]:
        sql = "SELECT * FROM market_analysis WHERE DATE(analysis_date) = DATE(?)"
        row = self.db.fetch_one(sql, (date.isoformat(),))
        return self._row_to_entity(row) if row else None

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MarketAnalysis]:
        sql = "SELECT * FROM market_analysis WHERE analysis_date >= ? AND analysis_date <= ? ORDER BY analysis_date DESC"
        rows = self.db.fetch_all(sql, (start_date.isoformat(), end_date.isoformat()))
        return [self._row_to_entity(row) for row in rows]

    def list_all(self) -> List[MarketAnalysis]:
        sql = "SELECT * FROM market_analysis ORDER BY analysis_date DESC"
        rows = self.db.fetch_all(sql)
        return [self._row_to_entity(row) for row in rows]

    def _row_to_entity(self, row: dict) -> MarketAnalysis:
        genre_trends_data = json.loads(row.get('genre_trends', '[]'))
        genre_trends = [
            GenreTrend(
                id=gt.get('id', ''),
                genre=gt.get('genre', ''),
                rank=gt.get('rank', 0),
                popularity_score=gt.get('popularity_score', 0.0),
                trend=gt.get('trend', 'stable'),
                trend_value=gt.get('trend_value', 0.0),
                hot_tags=gt.get('hot_tags', []),
                analysis_date=datetime.fromisoformat(gt['analysis_date']) if gt.get('analysis_date') else None,
                extra_data=gt.get('extra_data', {})
            ) for gt in genre_trends_data
        ]
        return MarketAnalysis(
            id=row['id'],
            analysis_date=datetime.fromisoformat(row['analysis_date']),
            platform_summary=json.loads(row.get('platform_summary', '{}')),
            genre_trends=genre_trends,
            hot_topics_summary=json.loads(row.get('hot_topics_summary', '{}')),
            recommendations=json.loads(row.get('recommendations', '[]')),
            ai_explanation=row.get('ai_explanation', ''),
            extra_data=json.loads(row.get('extra_data', '{}'))
        )