class GEXRegimeEngine:
    """Options-specific gamma-exposure regime classifier (needs an options chain, not plain OHLCV)."""

    def analyze_gamma_regime(self, gex_data: dict) -> dict:
        total_gex = gex_data.get("total_gex", 0.0)
        is_acceleration = gex_data.get("acceleration_zone", False)

        if total_gex < 0 and is_acceleration:
            env = "HYPER_VOLATILE_SQUEEZE_ZONE"
        elif total_gex > 0:
            env = "HIGH_PINNING_LOW_VOLATILITY"
        else:
            env = "TRANSITION_ZONE"

        return {"environment": env, "gex_value": total_gex}
