from typing import Dict, Any, List


class GammaAccelerationEngine:
    """
    Gamma Acceleration Index (GAI) - 3rd Order Spot Derivative
    Measures the speed/acceleration of Gamma Exposure change per spot_step move.
    """

    def calculate_gamma_acceleration(self, chain_data: List[Dict[str, Any]], spot_price: float,
                                      spot_step: float = 10.0) -> Dict[str, Any]:
        # BUG FIX: spot_step <= 0 caused a ZeroDivisionError (used as a denominator below)
        if spot_step <= 0:
            return {"error": f"Invalid spot_step ({spot_step}) — must be > 0"}

        def _get_total_gex(s_val: float) -> float:
            total_gex = 0.0
            for row in chain_data:
                gamma = row["gamma"]
                oi = row["open_interest"]
                opt_type = row["option_type"]
                if opt_type == "CE":
                    total_gex -= gamma * oi * s_val
                else:
                    total_gex += gamma * oi * s_val
            return total_gex

        gex_base = _get_total_gex(spot_price)
        gex_up = _get_total_gex(spot_price + spot_step)
        gex_down = _get_total_gex(spot_price - spot_step)

        dgex_ds = (gex_up - gex_down) / (2.0 * spot_step)
        d2gex_ds2 = (gex_up - 2.0 * gex_base + gex_down) / (spot_step ** 2)

        if d2gex_ds2 > 10.0:
            squeeze_velocity = "HIGH_ACCELERATION_HYPER_SQUEEZE"
        elif d2gex_ds2 < -10.0:
            squeeze_velocity = "RAPID_DECOMPRESSION_COLLAPSE"
        else:
            squeeze_velocity = "STABLE_GAMMA_FLOW"

        return {
            "spot_price": spot_price, "base_gex": round(gex_base, 2), "gamma_speed": round(dgex_ds, 4),
            "gamma_acceleration": round(d2gex_ds2, 6), "squeeze_velocity_status": squeeze_velocity
        }
