
from __future__ import annotations
import json
from datetime import datetime, timezone

class AuditLogger:
    def __init__(self, db) -> None:
        self.db = db

    def record(self, actor: str, action: str, module: str, payload: dict) -> None:
        self.db.execute(
            "INSERT INTO audit_events(event_time,actor,action,module,payload_json) VALUES (?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), actor, action, module,
             json.dumps(payload, sort_keys=True)),
        )
