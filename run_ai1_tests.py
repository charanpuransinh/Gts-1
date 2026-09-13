
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
