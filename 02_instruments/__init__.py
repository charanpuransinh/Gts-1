try:
    from . import instrument_types as _instrument_types
    import sys as _sys
    _sys.modules.setdefault("instrument_types", _instrument_types)
    from . import instrument_master as _instrument_master
    _sys.modules.setdefault("instrument_master", _instrument_master)
    from . import expiry_calendar as _expiry_calendar
    _sys.modules.setdefault("expiry_calendar", _expiry_calendar)
except ImportError:
    # Pytest can load numeric-folder __init__ as a top-level test module.
    pass
