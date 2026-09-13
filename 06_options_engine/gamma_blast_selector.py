import pandas as pd


class GammaBlastStrikeSelector:
    """ADDITIONAL strategy layer — sits alongside normal ATM strike selection (StrikeSelector /
    OptionsSelector), does NOT replace it.

    When the system senses a big move coming (gamma squeeze / high volatility breakout / expiry
    hero-zero setup), it should NOT buy the usual ATM strike. Instead it grabs the cheapest far-OTM
    strikes (e.g. $4-6 premium) in HIGHER quantity — so even a modest $10-20 move in the underlying
    still pays off well, because the leverage on a cheap option is much bigger.

    This stays within the EXPIRY_SPECIALIST + SCALPING mandate — it's a sizing/strike variant used
    only when a blast is detected, not a separate trading style.
    """

    def is_blast_likely(self, gex_regime: dict, volatility_state: dict, expiry_bias: str) -> bool:
        """Combines 3 existing signals you already have (GEXRegimeEngine, VolatilityEngine, ExpiryEngine)
        to flag a probable big/explosive move."""
        gamma_squeeze = gex_regime.get("environment") == "HYPER_VOLATILE_SQUEEZE_ZONE"
        high_vol = volatility_state.get("state") == "HIGH"
        breakout_bias = expiry_bias == "HERO_ZERO_BREAKOUT"
        return bool(gamma_squeeze or high_vol or breakout_bias)

    def select_blast_strikes(self, chain_df: pd.DataFrame, option_type: str = 'CE',
                              min_premium: float = 2.0, max_premium: float = 8.0,
                              capital_per_trade: float = 1000.0, lot_size: int = 1) -> dict:
        """Picks the cheapest strike inside the [min_premium, max_premium] band (far OTM = cheap)
        and sizes quantity so total capital deployed stays close to capital_per_trade.
        Requires chain_df to have a 'premium' column (live LTP of each strike)."""

        if 'premium' not in chain_df.columns:
            raise ValueError("chain_df must include a 'premium' column (live option LTP) for blast strike selection")

        subset = chain_df[chain_df['option_type'] == option_type].copy()
        subset = subset[(subset['premium'] >= min_premium) & (subset['premium'] <= max_premium)]

        if subset.empty:
            return {
                "strike": None,
                "premium": None,
                "suggested_quantity": 0,
                "strategy_tag": "GAMMA_BLAST_CHEAP_OTM",
                "note": f"No strikes found in premium band {min_premium}-{max_premium}"
            }

        # cheapest strike in the band = furthest OTM = maximum leverage
        subset = subset.sort_values('premium')
        best = subset.iloc[0]

        raw_qty = capital_per_trade / (best['premium'] + 1e-9)
        suggested_quantity = max(lot_size, int(raw_qty // lot_size) * lot_size)
        capital_deployed = round(float(best['premium']) * suggested_quantity, 2)

        # SAFETY CHECK: buying at least 1 lot is unavoidable (brokers don't sell fractional lots),
        # but if that minimum lot alone costs more than the capital allowed, the caller MUST know —
        # otherwise risk limits get silently breached.
        capital_exceeded = capital_deployed > capital_per_trade

        return {
            "strike": float(best['strike']),
            "premium": float(best['premium']),
            "suggested_quantity": int(suggested_quantity),
            "capital_deployed": capital_deployed,
            "capital_allowed": capital_per_trade,
            "capital_exceeded": bool(capital_exceeded),
            "strategy_tag": "GAMMA_BLAST_CHEAP_OTM"
        }

    def decide(self, chain_df: pd.DataFrame, gex_regime: dict, volatility_state: dict,
               expiry_bias: str, option_type: str = 'CE', capital_per_trade: float = 1000.0) -> dict:
        """One-shot helper: checks if a blast is likely, and if so returns blast strikes;
        otherwise tells the caller to fall back to the normal ATM/delta-based StrikeSelector."""
        if self.is_blast_likely(gex_regime, volatility_state, expiry_bias):
            result = self.select_blast_strikes(chain_df, option_type=option_type, capital_per_trade=capital_per_trade)
            result["mode"] = "BLAST_MODE"
            return result
        return {"mode": "NORMAL_ATM_MODE", "note": "No blast signal — use standard StrikeSelector / OptionsSelector"}
