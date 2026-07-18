import sqlite3

from application.market.data.initial_templates import (
    get_initial_templates,
    save_initial_templates,
)
from infrastructure.persistence.database.connection import DatabaseConnection


def test_initial_templates_can_be_seeded_into_fresh_database(tmp_path):
    db_path = tmp_path / "fresh.db"
    database = DatabaseConnection(str(db_path))
    database.close_all()

    save_initial_templates(str(db_path))
    save_initial_templates(str(db_path))

    with sqlite3.connect(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM templates").fetchone()[0]
        indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list('templates')").fetchall()
        }

    assert count == len(get_initial_templates())
    assert {
        "idx_market_templates_type",
        "idx_market_templates_genre",
        "idx_market_templates_active",
    }.issubset(indexes)
