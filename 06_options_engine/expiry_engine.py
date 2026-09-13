import pandas as pd
from .open_interest import OpenInterestEngine


class ExpiryEngine:
    """Core logic engine tailored for EXPIRY SPECIALIST strategies"""

    def __init__(self):
        self.oi_eng = OpenInterestEngine()

    def analyze_expiry_setup(self, spot_price: float, chain_df: pd.DataFrame, hours_to_expiry: float) -> dict:
        pcr = self.oi_eng.calculate_pcr(chain_df)
        max_pain = self.oi_eng.calculate_max_pain(chain_df)

        max_pain_distance = ((spot_price - max_pain) / spot_price) * 100.0

        expiry_bias = "NEUTRAL"
        if pcr > 1.2 and spot_price <= max_pain:
            expiry_bias = "BULLISH_PINNING"
        elif pcr < 0.8 and spot_price >= max_pain:
            expiry_bias = "BEARISH_PINNING"
        elif hours_to_expiry < 3 and abs(max_pain_distance) > 1.0:
            expiry_bias = "HERO_ZERO_BREAKOUT"

        return {
            "pcr": pcr,
            "max_pain": max_pain,
            "max_pain_distance_pct": round(max_pain_distance, 2),
            "hours_to_expiry": hours_to_expiry,
            "expiry_bias": expiry_bias
        }
