import pandas as pd


class LiquidityEngine:
    """Measures volume liquidity profile"""

    def analyze(self, df: pd.DataFrame) -> dict:
        curr_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].tail(20).mean()

        vol_ratio = curr_vol / (avg_vol + 1e-9)

        return {
            "current_volume": float(curr_vol),
            "volume_ratio": float(vol_ratio),
            "is_liquid": bool(vol_ratio >= 1.0)
        }
