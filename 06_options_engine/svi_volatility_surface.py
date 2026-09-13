import math
import numpy as np
from typing import Dict, Any, List


class SVIVolatilitySurfaceEngine:
    """
    Stochastic Volatility Inspired (SVI) Volatility Surface Model
    Fits IV Skew (as a degree-2 polynomial in log-moneyness) to detect mispriced strikes.
    """

    def fit_svi_skew(self, strikes: List[float], ivs: List[float], spot: float,
                      time_to_expiry_years: float) -> Dict[str, Any]:
        if len(strikes) < 3:
            return {"error": "Need at least 3 strikes for SVI fitting"}

        T = max(time_to_expiry_years, 0.0001)
        k_vec = [math.log(st / spot) for st in strikes]

        # BUG FIX: if all strikes collapse to the same log-moneyness (e.g. stale/duplicate chain rows),
        # the degree-2 fit is singular and numpy raises LinAlgError. Guard against it explicitly.
        if len(set(round(k, 8) for k in k_vec)) < 3:
            return {"error": "Need at least 3 DISTINCT strikes for SVI fitting (duplicates detected)"}

        w_vec = [(iv ** 2) * T for iv in ivs]

        poly = np.polyfit(k_vec, w_vec, 2)
        fitted_variances = np.polyval(poly, k_vec)
        fitted_ivs = [math.sqrt(max(v, 1e-6) / T) for v in fitted_variances]

        mispricings = []
        for i in range(len(strikes)):
            diff = ivs[i] - fitted_ivs[i]
            if diff > 0.02:
                status = "OVERPRICED_IV_RICH"
            elif diff < -0.02:
                status = "UNDERPRICED_IV_CHEAP"
            else:
                status = "FAIRLY_PRICED"
            mispricings.append({
                "strike": strikes[i], "actual_iv": round(ivs[i], 4), "model_fitted_iv": round(fitted_ivs[i], 4),
                "iv_diff": round(diff, 4), "pricing_status": status
            })

        return {"spot": spot, "fitted_strikes_count": len(strikes), "strike_mispricings": mispricings}
