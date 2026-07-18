"""动态模板SQLite仓储实现"""
import logging
from datetime import datetime
from typing import List, Optional
import sqlite3

from domain.market.entities.dynamic_template import (
    DiscoveredTemplate,
    TemplatePattern,
    TemplateType,
    TrendDirection,
    SourceNovel,
)
from domain.market.repositories.dynamic_template_repository import DynamicTemplateRepository
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SqliteDynamicTemplateRepository(DynamicTemplateRepository):
    """动态模板SQLite仓储实现"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_table()
    
    def _ensure_table(self):
        """确保表存在"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS discovered_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                pattern_type TEXT NOT NULL,
                genre TEXT,
                content TEXT,
                occurrence_count INTEGER DEFAULT 1,
                avg_rank REAL DEFAULT 0,
                trend TEXT DEFAULT 'stable',
                trend_value REAL DEFAULT 0,
                confidence_score REAL DEFAULT 0,
                tags TEXT,
                source_novels TEXT,
                status TEXT DEFAULT 'active',
                usage_count INTEGER DEFAULT 0,
                last_used_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_discovered_templates_type
            ON discovered_templates(pattern_type)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_discovered_templates_genre
            ON discovered_templates(genre)
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_discovered_templates_trend
            ON discovered_templates(trend, confidence_score DESC)
        """)
        self.db.commit()
    
    def _row_to_template(self, row: dict) -> DiscoveredTemplate:
        """数据库行转实体"""
        import json
        
        source_novels_data = json.loads(row.get("source_novels", "[]"))
        source_novels = [
            SourceNovel(
                platform=n.get("platform", ""),
                novel_id=n.get("novel_id", ""),
                novel_name=n.get("novel_name", ""),
                author=n.get("author", ""),
                rank=n.get("rank", 0),
                category=n.get("category", ""),
                word_count=n.get("word_count", 0),
                popularity=n.get("popularity", 0),
                score=n.get("score", 0.0),
            ) for n in source_novels_data
        ]
        
        pattern = TemplatePattern(
            name=row["name"],
            description=row.get("description", ""),
            pattern_type=TemplateType(row["pattern_type"]),
            genre=row.get("genre", ""),
            content=row.get("content", ""),
            source_novels=source_novels,
            occurrence_count=row.get("occurrence_count", 1),
            avg_rank=row.get("avg_rank", 0.0),
            trend=TrendDirection(row.get("trend", "stable")),
            trend_value=row.get("trend_value", 0.0),
            confidence_score=row.get("confidence_score", 0.0),
            tags=json.loads(row.get("tags", "[]")),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.utcnow(),
        )
        
        return DiscoveredTemplate(
            id=row["id"],
            pattern=pattern,
            status=row.get("status", "active"),
            usage_count=row.get("usage_count", 0),
            last_used_at=datetime.fromisoformat(row["last_used_at"]) if row.get("last_used_at") else None,
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.utcnow(),
        )
    
    async def save(self, template: DiscoveredTemplate) -> DiscoveredTemplate:
        """保存模板"""
        import json
        
        now = datetime.utcnow().isoformat()
        source_novels_json = json.dumps([
            {
                "platform": n.platform,
                "novel_id": n.novel_id,
                "novel_name": n.novel_name,
                "author": n.author,
                "rank": n.rank,
                "category": n.category,
                "word_count": n.word_count,
                "popularity": n.popularity,
                "score": n.score,
            } for n in template.pattern.source_novels
        ])
        
        self.db.execute("""
            INSERT INTO discovered_templates (
                id, name, description, pattern_type, genre, content,
                occurrence_count, avg_rank, trend, trend_value, confidence_score,
                tags, source_novels, status, usage_count, last_used_at,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                content = excluded.content,
                occurrence_count = excluded.occurrence_count,
                avg_rank = excluded.avg_rank,
                trend = excluded.trend,
                trend_value = excluded.trend_value,
                confidence_score = excluded.confidence_score,
                tags = excluded.tags,
                source_novels = excluded.source_novels,
                status = excluded.status,
                usage_count = excluded.usage_count,
                updated_at = excluded.updated_at
        """, (
            template.id,
            template.pattern.name,
            template.pattern.description,
            template.pattern.pattern_type.value,
            template.pattern.genre,
            template.pattern.content,
            template.pattern.occurrence_count,
            template.pattern.avg_rank,
            template.pattern.trend.value,
            template.pattern.trend_value,
            template.pattern.confidence_score,
            json.dumps(template.pattern.tags),
            source_novels_json,
            template.status,
            template.usage_count,
            template.last_used_at.isoformat() if template.last_used_at else None,
            template.created_at.isoformat(),
            now,
        ))
        self.db.commit()
        return template
    
    async def get_by_id(self, template_id: str) -> Optional[DiscoveredTemplate]:
        """根据ID获取模板"""
        row = self.db.fetch_one(
            "SELECT * FROM discovered_templates WHERE id = ?",
            (template_id,)
        )
        if not row:
            return None
        return self._row_to_template(dict(row))
    
    async def get_by_name_and_type(
        self, 
        name: str, 
        pattern_type: TemplateType
    ) -> Optional[DiscoveredTemplate]:
        """根据名称和类型获取模板"""
        row = self.db.fetch_one(
            "SELECT * FROM discovered_templates WHERE name = ? AND pattern_type = ?",
            (name, pattern_type.value)
        )
        if not row:
            return None
        return self._row_to_template(dict(row))
    
    async def list_by_type(
        self, 
        pattern_type: TemplateType,
        limit: int = 20
    ) -> List[DiscoveredTemplate]:
        """按类型列出模板"""
        rows = self.db.fetch_all(
            """SELECT * FROM discovered_templates 
               WHERE pattern_type = ? AND status = 'active'
               ORDER BY confidence_score DESC, occurrence_count DESC
               LIMIT ?""",
            (pattern_type.value, limit)
        )
        return [self._row_to_template(dict(row)) for row in rows]
    
    async def list_by_genre(
        self, 
        genre: str,
        limit: int = 20
    ) -> List[DiscoveredTemplate]:
        """按题材列出模板"""
        rows = self.db.fetch_all(
            """SELECT * FROM discovered_templates 
               WHERE genre = ? AND status = 'active'
               ORDER BY confidence_score DESC, occurrence_count DESC
               LIMIT ?""",
            (genre, limit)
        )
        return [self._row_to_template(dict(row)) for row in rows]
    
    async def list_trending(self, limit: int = 10) -> List[DiscoveredTemplate]:
        """获取热门模板"""
        rows = self.db.fetch_all(
            """SELECT * FROM discovered_templates 
               WHERE status = 'active' AND trend = 'rising'
               ORDER BY trend_value DESC, confidence_score DESC
               LIMIT ?""",
            (limit,)
        )
        return [self._row_to_template(dict(row)) for row in rows]
    
    async def list_recent(self, days: int = 7, limit: int = 20) -> List[DiscoveredTemplate]:
        """获取最近发现的模板"""
        cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0)
        cutoff_str = cutoff.isoformat()
        
        rows = self.db.fetch_all(
            """SELECT * FROM discovered_templates 
               WHERE status = 'active' AND created_at >= ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (cutoff_str, limit)
        )
        return [self._row_to_template(dict(row)) for row in rows]
    
    async def update_usage(self, template_id: str) -> None:
        """更新使用次数"""
        now = datetime.utcnow().isoformat()
        self.db.execute(
            """UPDATE discovered_templates 
               SET usage_count = usage_count + 1, last_used_at = ?, updated_at = ?
               WHERE id = ?""",
            (now, now, template_id)
        )
        self.db.commit()
    
    async def update_trend(
        self, 
        template_id: str, 
        trend: TrendDirection,
        trend_value: float
    ) -> None:
        """更新趋势"""
        now = datetime.utcnow().isoformat()
        self.db.execute(
            """UPDATE discovered_templates 
               SET trend = ?, trend_value = ?, updated_at = ?
               WHERE id = ?""",
            (trend.value, trend_value, now, template_id)
        )
        self.db.commit()
    
    async def delete_old(self, days: int = 30) -> int:
        """删除旧模板"""
        cutoff = datetime.utcnow()
        cutoff_str = cutoff.isoformat()
        
        cursor = self.db.execute(
            """DELETE FROM discovered_templates 
               WHERE status = 'deprecated' AND updated_at < ?""",
            (cutoff_str,)
        )
        self.db.commit()
        return cursor.rowcount
    
    async def search(
        self,
        keyword: str,
        pattern_type: Optional[TemplateType] = None,
        genre: Optional[str] = None,
        limit: int = 20
    ) -> List[DiscoveredTemplate]:
        """搜索模板"""
        conditions = ["status = 'active'", "name LIKE ?"]
        params = [f"%{keyword}%"]
        
        if pattern_type:
            conditions.append("pattern_type = ?")
            params.append(pattern_type.value)
        
        if genre:
            conditions.append("genre = ?")
            params.append(genre)
        
        params.append(limit)
        
        sql = f"""SELECT * FROM discovered_templates 
                  WHERE {' AND '.join(conditions)}
                  ORDER BY confidence_score DESC
                  LIMIT ?"""
        
        rows = self.db.fetch_all(sql, params)
        return [self._row_to_template(dict(row)) for row in rows]
