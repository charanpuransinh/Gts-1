
from __future__ import annotations
from db_manager import DatabaseManager

AUDIT_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS audit_events ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "event_time TEXT NOT NULL,"
    "actor TEXT NOT NULL,"
    "action TEXT NOT NULL,"
    "module TEXT NOT NULL,"
    "payload_json TEXT NOT NULL)"
)

class SchemaManager:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def bootstrap(self) -> None:
        self.db.execute(AUDIT_SCHEMA)
