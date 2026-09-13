import math
from typing import Dict, List, Any


class VannaCharmEngine:
    """
    2nd Order Greeks Engine (Pure Python, No SciPy):
    - Vanna: Volatility के 1% बदलाव पर Delta में परिवर्तन
    - Charm: समय बीतने (Time Decay) के साथ Delta Drift
    """

    @staticmethod
    def _norm_pdf(x: float) -> float:
        return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

    @staticmethod
    def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        if T <= 0 or sigma <= 0:
            return 0.0
        return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

    def calculate_vanna_charm(self, S: float, K: float, T_days: float, r: float, sigma: float) -> Dict[str, float]:
        T = max(T_days / 365.0, 0.0001)
        sigma = max(sigma, 0.001)

        d1 = self._d1(S, K, T, r, sigma)
        d2 = d1 - sigma * math.sqrt(T)
        pdf_d1 = self._norm_pdf(d1)

        vanna = -math.exp(-r * T) * pdf_d1 * (d2 / sigma)
        charm_call = -math.exp(-r * T) * pdf_d1 * (
            2 * r * T - d2 * sigma * math.sqrt(T)
        ) / (2 * T * sigma * math.sqrt(T))

        return {"vanna": round(vanna, 6), "charm": round(charm_call, 6)}

    def aggregate_chain_exposures(self, options_chain: List[Dict[str, Any]], spot: float) -> Dict[str, Any]:
        total_vanna_exp = 0.0
        total_charm_exp = 0.0

        for row in options_chain:
            K = row["strike"]
            T_days = row["time_to_expiry_days"]
            iv = row["implied_volatility"]
            oi = row["open_interest"]
            r = 0.07

            greeks = self.calculate_vanna_charm(spot, K, T_days, r, iv)
            total_vanna_exp += greeks["vanna"] * oi * 100
            total_charm_exp += greeks["charm"] * oi * 100

        return {
            "spot_price": spot,
            "net_vanna_exposure": round(total_vanna_exp, 2),
            "net_charm_exposure": round(total_charm_exp, 2),
            "expiry_afternoon_bias": "BULLISH_DRIFT" if total_charm_exp > 0 else "BEARISH_DRIFT"
        }
