import logging
import json
from datetime import datetime
from typing import List, Optional
from domain.market.entities.template import Template
from domain.market.repositories.template_repository import TemplateRepository
from infrastructure.persistence.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SqliteTemplateRepository(TemplateRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                template_type TEXT NOT NULL,
                genre TEXT NOT NULL,
                content TEXT NOT NULL,
                description TEXT DEFAULT '',
                popularity INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                extra_data TEXT DEFAULT '{}'
            )
        """
        self.db.execute(sql)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_templates_type ON templates(template_type)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_templates_genre ON templates(genre)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_templates_active ON templates(is_active)")
        self.db.get_connection().commit()

    def save(self, template: Template) -> None:
        sql = """
            INSERT INTO templates (
                id, name, template_type, genre, content, description,
                popularity, usage_count, is_active, created_at, updated_at, extra_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                template_type = excluded.template_type,
                genre = excluded.genre,
                content = excluded.content,
                description = excluded.description,
                popularity = excluded.popularity,
                usage_count = excluded.usage_count,
                is_active = excluded.is_active,
                updated_at = excluded.updated_at,
                extra_data = excluded.extra_data
        """
        self.db.execute(sql, (
            template.id,
            template.name,
            template.template_type,
            template.genre,
            template.content,
            template.description,
            template.popularity,
            template.usage_count,
            1 if template.is_active else 0,
            template.created_at.isoformat() if template.created_at else datetime.utcnow().isoformat(),
            template.updated_at.isoformat() if template.updated_at else datetime.utcnow().isoformat(),
            json.dumps(template.extra_data)
        ))
        self.db.get_connection().commit()

    def get_by_id(self, template_id: str) -> Optional[Template]:
        sql = "SELECT * FROM templates WHERE id = ?"
        row = self.db.fetch_one(sql, (template_id,))
        return self._row_to_entity(row) if row else None

    def get_by_type(self, template_type: str) -> List[Template]:
        sql = "SELECT * FROM templates WHERE template_type = ? AND is_active = 1 ORDER BY popularity DESC"
        rows = self.db.fetch_all(sql, (template_type,))
        return [self._row_to_entity(row) for row in rows]

    def get_by_genre(self, genre: str) -> List[Template]:
        sql = "SELECT * FROM templates WHERE genre = ? AND is_active = 1 ORDER BY popularity DESC"
        rows = self.db.fetch_all(sql, (genre,))
        return [self._row_to_entity(row) for row in rows]

    def get_by_type_and_genre(self, template_type: str, genre: str) -> List[Template]:
        sql = "SELECT * FROM templates WHERE template_type = ? AND genre = ? AND is_active = 1 ORDER BY popularity DESC"
        rows = self.db.fetch_all(sql, (template_type, genre))
        return [self._row_to_entity(row) for row in rows]

    def search(self, keyword: str) -> List[Template]:
        sql = """
            SELECT * FROM templates 
            WHERE is_active = 1 AND (name LIKE ? OR description LIKE ? OR content LIKE ?)
            ORDER BY popularity DESC
        """
        pattern = f"%{keyword}%"
        rows = self.db.fetch_all(sql, (pattern, pattern, pattern))
        return [self._row_to_entity(row) for row in rows]

    def list_all(self) -> List[Template]:
        sql = "SELECT * FROM templates WHERE is_active = 1 ORDER BY popularity DESC"
        rows = self.db.fetch_all(sql)
        return [self._row_to_entity(row) for row in rows]

    def increment_usage(self, template_id: str) -> None:
        sql = "UPDATE templates SET usage_count = usage_count + 1, updated_at = ? WHERE id = ?"
        self.db.execute(sql, (datetime.utcnow().isoformat(), template_id))
        self.db.get_connection().commit()

    def delete(self, template_id: str) -> None:
        sql = "DELETE FROM templates WHERE id = ?"
        self.db.execute(sql, (template_id,))
        self.db.get_connection().commit()

    def _row_to_entity(self, row: dict) -> Template:
        return Template(
            id=row['id'],
            name=row['name'],
            template_type=row['template_type'],
            genre=row['genre'],
            content=row['content'],
            description=row.get('description', ''),
            popularity=row.get('popularity', 0),
            usage_count=row.get('usage_count', 0),
            is_active=bool(row.get('is_active', 1)),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            extra_data=json.loads(row.get('extra_data', '{}'))
        )