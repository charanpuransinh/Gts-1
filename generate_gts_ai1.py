
#!/usr/bin/env python3
'''
GTS AI-1 one-shot generator.

Run from the cleared GTS repository root:
    python3 generate_gts_ai1.py
Then:
    python3 run_ai1_tests.py

The original AI-1 market-data archive is embedded byte-for-byte and restored
only after SHA-256 verification. No AI-2/AI-3/AI-4 trading logic, Risk,
Strategy, Signal, Execution or Broker logic is generated.
'''
from __future__ import annotations

import base64
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from textwrap import dedent

ROOT = Path.cwd()
EMBEDDED_SHA256 = "c7943f100dafa23197d2fc188f92cc4e41ab5bb6685a4784b11bb633c4146889"
ORIGINAL_ZIP_B64 = "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"

def stop(msg: str) -> None:
    print("\\nAI-1 GENERATION STOPPED: " + msg)
    raise SystemExit(2)

def write(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    if p.exists():
        if p.read_bytes() != data:
            stop("refusing to overwrite conflicting file: " + rel)
        return
    p.write_bytes(data)

def restore_original_ai1() -> None:
    data = base64.b64decode(ORIGINAL_ZIP_B64)
    if hashlib.sha256(data).hexdigest() != EMBEDDED_SHA256:
        stop("embedded original AI-1 archive hash mismatch")
    with tempfile.TemporaryDirectory(prefix="gts_ai1_") as td:
        zpath = Path(td) / "ai1.zip"
        out = Path(td) / "out"
        zpath.write_bytes(data)
        with zipfile.ZipFile(zpath) as zf:
            names = [n for n in zf.namelist()
                     if not n.endswith("/") and "__pycache__" not in n]
            if not names:
                stop("embedded original AI-1 archive is empty")
            for n in names:
                if not n.startswith("01_market_data/"):
                    stop("original archive contains out-of-scope path: " + n)
            zf.extractall(out)
        srcdir = out / "01_market_data"
        for p in srcdir.rglob("*"):
            if p.is_dir() or "__pycache__" in p.parts:
                continue
            target = ROOT / "01_market_data" / p.relative_to(srcdir)
            target.parent.mkdir(parents=True, exist_ok=True)
            data = p.read_bytes()
            if target.exists() and target.read_bytes() != data:
                stop("original AI-1 file conflict: " + str(target.relative_to(ROOT)))
            if not target.exists():
                target.write_bytes(data)

def backend() -> None:
    write("23_database/db_manager.py", dedent('''
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any, Iterable

class DatabaseManager:
    def __init__(self, db_path: str | Path = "runtime/gts.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        with self.connect() as conn:
            conn.execute(sql, tuple(params))
            conn.commit()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]
'''))

    write("23_database/schema_manager.py", dedent('''
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
'''))

    write("27_system/config_manager.py", dedent('''
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
'''))

    write("27_system/audit_logger.py", dedent('''
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
'''))

    write("27_system/health_monitor.py", dedent('''
from __future__ import annotations
import time

class HealthMonitor:
    def __init__(self, feed=None) -> None:
        self.feed = feed
        self.started_at = time.time()

    def status(self) -> dict:
        result = {
            "system": "GTS",
            "component": "AI-1",
            "status": "UP",
            "uptime_seconds": round(time.time() - self.started_at, 3),
        }
        if self.feed is not None:
            s = self.feed.get_status()
            result["feed_status"] = s.feed_status.value
            result["market_state"] = s.state.value
            result["exchange"] = s.exchange
        return result
'''))

    write("24_api/api_router.py", dedent('''
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
MARKET = ROOT / "01_market_data"
if str(MARKET) not in sys.path:
    sys.path.insert(0, str(MARKET))

from market_data_cache import MarketDataCache
from market_data_feed import SimulatedMarketDataFeed

class AIRouter:
    def __init__(self) -> None:
        self.feed = SimulatedMarketDataFeed(exchange="SIM", seed=1)
        self.cache = MarketDataCache()
        self.feed.on_tick(self.cache.update_tick)
        self.feed.on_quote(self.cache.update_quote)
        self.feed.connect()
        self.feed.subscribe(["NIFTY"])
        self.feed.pump("NIFTY")

    def handle(self, path: str) -> tuple[int, dict]:
        parsed = urlparse(path)
        if parsed.path == "/health":
            return 200, {"system": "GTS", "component": "AI-1", "status": "UP"}
        if parsed.path == "/market/status":
            s = self.feed.get_status()
            return 200, {
                "exchange": s.exchange,
                "state": s.state.value,
                "feed_status": s.feed_status.value,
            }
        if parsed.path == "/market/tick":
            symbol = parse_qs(parsed.query).get("symbol", [""])[0].strip()
            if not symbol:
                return 400, {"error": "symbol query parameter is required"}
            if symbol not in self.feed.subscribed_symbols:
                return 404, {"error": "symbol not subscribed: " + symbol}
            tick = self.cache.get_tick(symbol)
            if tick is None:
                return 404, {"error": "no tick available: " + symbol}
            return 200, {
                "symbol": tick.symbol, "ltp": tick.ltp, "ltq": tick.ltq,
                "timestamp": tick.timestamp, "exchange": tick.exchange,
                "volume": tick.volume,
            }
        return 404, {"error": "not found"}

    @staticmethod
    def encode(payload: dict) -> bytes:
        return json.dumps(payload, sort_keys=True).encode("utf-8")
'''))

    write("24_api/api_server.py", dedent('''
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from api_router import AIRouter
from config_manager import load_config

ROUTER = AIRouter()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        status, payload = ROUTER.handle(self.path)
        body = ROUTER.encode(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print("GTS-AI1-API | " + fmt % args)

def main() -> None:
    cfg = load_config()
    server = ThreadingHTTPServer((cfg.host, cfg.port), Handler)
    print("GTS AI-1 API: http://%s:%s" % (cfg.host, cfg.port))
    server.serve_forever()

if __name__ == "__main__":
    main()
'''))

def frontend() -> None:
    write("20_dashboard/index.html", dedent('''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GTS - AI-1 Market Data</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<main>
<h1>GTS - AI-1 Market Data</h1>
<section id="health">Loading health...</section>
<section id="market">Loading market status...</section>
<section id="tick">Loading NIFTY tick...</section>
</main>
<script src="app.js"></script>
</body>
</html>
'''))

    write("20_dashboard/app.js", dedent('''
"use strict";
async function getJSON(path) {
  const r = await fetch(path);
  const d = await r.json();
  if (!r.ok) throw new Error(d.error || ("HTTP " + r.status));
  return d;
}
async function refresh() {
  try {
    const h = await getJSON("http://127.0.0.1:8765/health");
    document.querySelector("#health").textContent =
      "Health: " + h.status + " | " + h.system + " | " + h.component;
    const m = await getJSON("http://127.0.0.1:8765/market/status");
    document.querySelector("#market").textContent =
      "Market: " + m.exchange + " | " + m.state + " | Feed: " + m.feed_status;
    const t = await getJSON("http://127.0.0.1:8765/market/tick?symbol=NIFTY");
    document.querySelector("#tick").textContent =
      "NIFTY LTP: " + t.ltp + " | Volume: " + t.volume;
  } catch (e) {
    document.querySelector("#health").textContent = "API error: " + e.message;
  }
}
refresh();
setInterval(refresh, 2000);
'''))

    write("20_dashboard/styles.css", dedent('''
body { font-family: system-ui, sans-serif; margin: 0; background: #0A1628; color: #F5F5F5; }
main { max-width: 760px; margin: 0 auto; padding: 24px; }
section { border: 1px solid #2E86C1; border-radius: 10px; padding: 16px; margin: 12px 0; }
'''))

def contracts_tests() -> None:
    write("29_docs/architecture_contract.md", dedent('''
# GTS AI-1 Architecture Contract

Market Source -> Canonical Market Data -> Cache -> Read-only API -> Dashboard

AI-1 supplies common architecture services and stable market-data interfaces.
It does not implement Strategy, Signal, Risk, Execution or Broker logic.
Credentials are never hard-coded.
'''))

    write("29_docs/interface_contract.md", dedent('''
# GTS AI-1 Interface Contract

Every cross-module interface is defined by:
INPUT / OUTPUT / CALLER / CALLEE / DEPENDENCIES / ERRORS / VERSION

Read-only AI-1 API:
GET /health
GET /market/status
GET /market/tick?symbol=SYMBOL

No order or broker endpoint is defined by AI-1.
'''))

    write("29_docs/wiring_map.md", dedent('''
# GTS AI-1 Wiring Map

Market Source / Simulation
  -> 01_market_data.market_data_feed
  -> data_normalizer
  -> canonical Tick/Bar/OptionQuote
  -> 01_market_data.market_data_cache
  -> 24_api.api_router
  -> 24_api.api_server
  -> 20_dashboard

Common:
  27_system/config_manager -> 24_api
  23_database/db_manager -> 23_database/schema_manager
  27_system/audit_logger -> 23_database

Downstream handoff is interface-only.
AI-1 does not bypass Risk, Strategy, Signal, Execution or Broker.
'''))

    write("29_docs/file_registry.md", dedent('''
# GTS AI-1 File Registry

Preserved:
  01_market_data/

Generated backend:
  23_database/
  24_api/
  27_system/

Generated frontend:
  20_dashboard/

Verification:
  28_tests/
  run_ai1_tests.py

AI-1 does not mutate:
  07_strategy/
  08_signal_engine/
  12_risk/
  14_execution/
  15_broker/
  21_ai/
'''))

    write("28_tests/test_ai1_integration.py", dedent('''
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for name in ("01_market_data", "24_api", "23_database"):
    p = ROOT / name
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from market_data_cache import MarketDataCache
from market_data_types import Tick
from api_router import AIRouter
from db_manager import DatabaseManager
from schema_manager import SchemaManager

class AI1IntegrationTests(unittest.TestCase):
    def test_market_cache(self):
        c = MarketDataCache()
        c.update_tick(Tick(symbol="NIFTY", ltp=22000.0))
        self.assertEqual(c.get_ltp("NIFTY"), 22000.0)

    def test_api_health(self):
        status, payload = AIRouter().handle("/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "UP")

    def test_api_tick(self):
        status, payload = AIRouter().handle("/market/tick?symbol=NIFTY")
        self.assertEqual(status, 200)
        self.assertEqual(payload["symbol"], "NIFTY")
        self.assertGreater(payload["ltp"], 0)

    def test_database_schema(self):
        with tempfile.TemporaryDirectory() as td:
            db = DatabaseManager(Path(td) / "test.db")
            SchemaManager(db).bootstrap()
            rows = db.fetch_all(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='audit_events'"
            )
            self.assertEqual(len(rows), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
'''))

    write("run_ai1_tests.py", dedent('''
#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover(str(ROOT / "28_tests"), pattern="test_*.py"))
    suite.addTests(loader.discover(
        str(ROOT / "01_market_data" / "tests"), pattern="test_*.py"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "system": "GTS",
        "stage": "AI-1",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success": result.wasSuccessful(),
    }
    (ROOT / "AI1_TEST_RESULTS.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    raise SystemExit(main())
'''))

def manifest() -> None:
    entries = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        if any(x in {".git", "__pycache__"} for x in p.parts):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel == Path(__file__).name:
            continue
        entries.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        })
    out = {
        "system": "GTS",
        "stage": "AI-1",
        "original_ai1_sha256": EMBEDDED_SHA256,
        "file_count": len(entries),
        "files": entries,
    }
    (ROOT / "AI1_GENERATION_MANIFEST.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    write("AI1_GENERATION_REPORT.md", dedent('''
# GTS AI-1 Generation Report

Original AI-1 package restored only after SHA-256 verification.

Generated:
- original 01_market_data implementation
- common database boundary
- read-only API
- configuration/audit/health services
- dashboard frontend shell
- contracts and wiring map
- AI-1 tests and deterministic manifest

Generation is not a test PASS. Run:
  python3 run_ai1_tests.py

Only the actual test result is evidence of test success.
'''))

def main() -> int:
    if ROOT.name.lower() in {"gnt", "argt", "gst"}:
        stop("wrong project root; this generator is for GTS only")
    restore_original_ai1()
    backend()
    frontend()
    contracts_tests()
    manifest()
    print("=" * 70)
    print("GTS AI-1 GENERATION COMPLETE")
    print("=" * 70)
    print("Original AI-1 preserved; backend + frontend + wiring + tests generated.")
    print("No AI-2/AI-3/AI-4/Risk/Strategy/Signal/Execution/Broker logic generated.")
    print("NEXT: python3 run_ai1_tests.py")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
