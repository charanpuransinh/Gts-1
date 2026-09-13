import ast
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_ai2_instruments_imports():
    assert importlib.import_module("02_instruments.instrument_master") is not None
    assert importlib.import_module("02_instruments.contract_builder") is not None
    assert importlib.import_module("02_instruments.expiry_calendar") is not None

def test_v2_options_files_exist():
    p = ROOT / "06_options_engine"
    assert p.is_dir()
    for name in ["options_chain.py", "instrument_wiring.py"]:
        assert (p / name).is_file(), name

def test_v2_options_source_is_syntax_valid():
    p = ROOT / "06_options_engine"
    files = list(p.glob("*.py"))
    assert files
    for f in files:
        ast.parse(f.read_text(encoding="utf-8"), filename=str(f))

def test_v2_indicator_source_is_syntax_valid():
    p = ROOT / "04_indicators"
    assert p.is_dir()
    files = list(p.glob("*.py"))
    assert files
    for f in files:
        ast.parse(f.read_text(encoding="utf-8"), filename=str(f))

def test_expiry_wiring_is_dependency_safe():
    p = ROOT / "06_options_engine" / "instrument_wiring.py"
    source = p.read_text(encoding="utf-8")
    assert "02_instruments" in source
    assert "expiry" in source.lower()
