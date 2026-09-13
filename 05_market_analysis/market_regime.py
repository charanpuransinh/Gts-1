import pandas as pd
from .trend_engine import TrendEngine
from .volatility_engine import VolatilityEngine
from .momentum_engine import MomentumEngine
from .liquidity_engine import LiquidityEngine


class MarketRegimeEngine:
    """Aggregates all market intelligence components into an overall market regime.
    Works off plain OHLCV(+volume) data, so it applies to stocks, commodities, and options underlyings alike."""

    def __init__(self):
        self.trend_eng = TrendEngine()
        self.vol_eng = VolatilityEngine()
        self.mom_eng = MomentumEngine()
        self.liq_eng = LiquidityEngine()

    def detect_regime(self, df: pd.DataFrame) -> dict:
        trend_res = self.trend_eng.analyze(df)
        vol_res = self.vol_eng.analyze(df)
        mom_res = self.mom_eng.analyze(df)
        liq_res = self.liq_eng.analyze(df)

        regime = f"{trend_res['trend']}_{vol_res['state']}_VOLATILITY"

        return {
            "regime": regime,
            "trend": trend_res,
            "volatility": vol_res,
            "momentum": mom_res,
            "liquidity": liq_res
        }
