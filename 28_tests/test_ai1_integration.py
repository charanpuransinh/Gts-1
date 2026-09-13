
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
