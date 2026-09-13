
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class GTSConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    stale_after_seconds: float = 15.0
    db_path: str = "runtime/gts.db"

def load_config() -> GTSConfig:
    return GTSConfig(
        host=os.getenv("GTS_API_HOST", "127.0.0.1"),
        port=int(os.getenv("GTS_API_PORT", "8765")),
        stale_after_seconds=float(os.getenv("GTS_STALE_AFTER_SECONDS", "15")),
        db_path=os.getenv("GTS_DB_PATH", "runtime/gts.db"),
    )
