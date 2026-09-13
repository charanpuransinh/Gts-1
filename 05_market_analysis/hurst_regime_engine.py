from typing import Dict, Any
import numpy as np
import pandas as pd


class HurstRegimeEngine:
    """हर्स्ट एक्सपोनेंट (Hurst Exponent): मीन-रिवर्जन बनाम ट्रेंडिंग मार्केट डिसीजन (Pure Python)"""

    def calculate_hurst(self, price_series: pd.Series, max_lag: int = 20) -> Dict[str, Any]:
        if len(price_series) < 50:
            return {"error": "Need at least 50 bars for reliable Hurst Exponent"}

        prices = price_series.values
        lags = range(2, max_lag)
        tau = [np.sqrt(np.std(np.subtract(prices[lag:], prices[:-lag]))) for lag in lags]

        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst_val = float(poly[0] * 2.0)
        hurst_val = max(0.0, min(1.0, round(hurst_val, 4)))

        if hurst_val < 0.45:
            regime = "MEAN_REVERTING_RANGEBOUND"
        elif hurst_val > 0.55:
            regime = "TREND_PERSISTENT_BREAKOUT"
        else:
            regime = "RANDOM_WALK_NO_EDGE"

        return {"hurst_exponent": hurst_val, "market_regime": regime}
