import math
from typing import Dict, Any


class SyntheticForwardEngine:
    """
    Put-Call Parity Synthetic Forward Engine
    Formula: F_synth = Strike + e^(r*T) * (Call_Premium - Put_Premium)
    Detects institutional lead/lag before spot moves.
    """

    def __init__(self, risk_free_rate: float = 0.07):
        self.r = risk_free_rate

    def calculate_synthetic_forward(self, spot_price: float, atm_strike: float, call_price: float,
                                     put_price: float, days_to_expiry: float) -> Dict[str, Any]:
        # BUG FIX: spot_price <= 0 (bad tick / feed glitch) caused a division-by-zero crash on spread_pct
        if spot_price <= 0:
            return {"error": f"Invalid spot_price ({spot_price}) — must be > 0"}

        T = max(days_to_expiry / 365.0, 0.0001)
        discount_factor = math.exp(self.r * T)

        synthetic_forward = atm_strike + discount_factor * (call_price - put_price)
        spread = synthetic_forward - spot_price
        spread_pct = (spread / spot_price) * 100.0

        if spread_pct > 0.15:
            bias = "INSTITUTIONAL_BULLISH_PREMIUM"
        elif spread_pct < -0.15:
            bias = "INSTITUTIONAL_BEARISH_DISCOUNT"
        else:
            bias = "FAIR_VALUE_BALANCED"

        return {
            "spot_price": round(spot_price, 2), "synthetic_forward": round(synthetic_forward, 2),
            "synthetic_spread": round(spread, 2), "synthetic_spread_pct": round(spread_pct, 4),
            "institutional_bias": bias
        }
