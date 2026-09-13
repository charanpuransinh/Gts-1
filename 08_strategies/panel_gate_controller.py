from typing import Dict, Any, Optional
from datetime import date


class PanelGateController:
    """
    Decides which trading panel is ACTIVE right now, per Owner's rule:
    - EXPIRY PANEL unlocks ONLY on the actual expiry day for the instrument — locked every other day.
    - SCALP PANEL runs on non-expiry days, and specifically on choppy/range-bound market days.
    - On the expiry day itself, the Expiry panel takes exclusive precedence (matches this project's
      own blueprint priority order: Expiry -> Scalping -> Intraday -> Swing) — Scalp panel is locked
      out that day so the two don't fight over the same capital/attention.

    NOTE ON expiry_weekday: NSE weekly index expiry days have changed by SEBI circular more than once
    (Thursday historically, moved to Tuesday for some indices more recently) and differ by instrument
    (equity F&O, monthly expiries, US 0DTE, etc.). This is left CONFIGURABLE on purpose — verify the
    correct weekday(s) for whichever instrument/broker feed you're running before relying on this in
    paper trade, don't assume the default below is current.
    """

    def __init__(self, expiry_weekdays=(1,)):  # default: Tuesday (Python weekday(): Mon=0..Sun=6)
        self.expiry_weekdays = set(expiry_weekdays)

    def determine_active_panel(self, current_date: date, market_regime: Optional[Dict[str, Any]] = None,
                                is_expiry_day_override: Optional[bool] = None) -> Dict[str, Any]:
        """
        current_date: today's date (caller supplies — this engine has no clock of its own)
        market_regime: optional output from MarketRegimeEngine.detect_regime(), used only to annotate
                        WHY the scalp panel is active (choppy vs trending) — does not change the gate.
        is_expiry_day_override: pass True/False directly if you maintain an explicit expiry calendar
                                 (holidays, monthly expiries, instrument-specific dates) instead of a
                                 fixed weekday — this always wins over the weekday check when provided.
        """
        if is_expiry_day_override is not None:
            is_expiry_day = is_expiry_day_override
        else:
            is_expiry_day = current_date.weekday() in self.expiry_weekdays

        regime_note = ""
        if market_regime:
            trend = market_regime.get("trend", {}).get("trend", "")
            if trend == "SIDEWAYS":
                regime_note = " — choppy/range-bound market"

        if is_expiry_day:
            return {
                "active_panel": "EXPIRY", "expiry_panel_locked": False, "scalp_panel_locked": True,
                "reason": "Today is expiry day — Expiry panel has exclusive precedence"
            }
        else:
            return {
                "active_panel": "SCALP", "expiry_panel_locked": True, "scalp_panel_locked": False,
                "reason": "Non-expiry day" + regime_note
            }


# ==============================================================================
# PANEL REGISTRY — which engine belongs in which panel (Claude's own system design,
# grouped by what each engine actually needs / was built for)
# ==============================================================================

EXPIRY_PANEL_ENGINES = [
    "GEXRegimeEngine",              # 06_options_engine — gamma pinning vs squeeze regime
    "ZeroGammaFlipEngine",          # 06_options_engine — dealer long/short gamma flip level
    "ExpiryEngine",                 # 06_options_engine — PCR + max pain + expiry bias
    "ExpirySignalEngine",           # 06_options_engine — expiry bias -> recommended action
    "StraddleScanner",              # 06_options_engine — ATM straddle premium/breakevens
    "GammaBlastStrikeSelector",     # 06_options_engine — cheap far-OTM strike + auto quantity
    "GammaBlastHouseMoneyEngine",   # 06_options_engine — single 5x-trigger counter-hedge
    "GammaBlastLadderEngine",       # 06_options_engine — laddered doubling counter-hedge
    "HyperVelocityTrailingEngine",  # 10_risk_execution_support — velocity-aware exit for blast legs
    "GammaAccelerationEngine",      # 06_options_engine — how fast a squeeze is building
    "SyntheticForwardEngine",       # 06_options_engine — institutional lead/lag detection
]

SCALP_PANEL_ENGINES = [
    "TrendEngine",                  # 05_market_analysis — trend direction/strength (bias)
    "MomentumEngine",               # 05_market_analysis — RSI/MACD momentum state
    "VolatilityEngine",             # 05_market_analysis — HIGH/NORMAL/LOW volatility state
    "LiquidityEngine",              # 05_market_analysis — volume liquidity check
    "MTFConfluenceEngine",          # 05_market_analysis — multi-timeframe confluence score
    "StrikeSelector",               # 06_options_engine — standard ATM/delta strike picker
    "PullbackCounterScalpEngine",   # 06_options_engine — repeated small scalps on pullbacks
    "BreadthMicroScalperEngine",    # 06_options_engine — breadth-validated micro-scalper
    "OptionMicroPriceEngine",       # 06_options_engine — bid/ask order-flow imbalance
]

# Shared by both panels regardless of gate state (pure calculation, no strategy bias):
SHARED_UTILITY_ENGINES = [
    "IndicatorEngine", "MarketRegimeEngine", "AllGreeksEngine", "OptionsPricingModels",
    "calculate_implied_volatility", "OpenInterestEngine", "PremiumAnalysis",
    "SVIVolatilitySurfaceEngine", "NetDeltaExposureEngine", "VolatilitySkewEngine",
    "EconomicCalendarEngine", "MarketHoursEngine", "HurstRegimeEngine", "CrossAssetCorrelationEngine",
]
