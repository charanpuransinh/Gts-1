from typing import Dict, Any
import pandas as pd


class ZeroGammaFlipEngine:
    """Market Maker Long Gamma (Pinning) बनाम Short Gamma (Squeeze/Gamma Blast) का Flip Level"""

    def find_flip_point(self, chain_df: pd.DataFrame, current_spot: float) -> Dict[str, Any]:
        """chain_df requires columns: ['strike', 'gamma', 'open_interest', 'option_type']"""
        if chain_df.empty:
            return {"error": "Empty options chain"}

        strikes = sorted(chain_df["strike"].unique())
        gamma_profile = {}

        for k in strikes:
            sub = chain_df[chain_df["strike"] == k]
            call_gex = sub[sub["option_type"] == "CE"]["gamma"].sum() * sub[sub["option_type"] == "CE"]["open_interest"].sum()
            put_gex = sub[sub["option_type"] == "PE"]["gamma"].sum() * sub[sub["option_type"] == "PE"]["open_interest"].sum()
            net_gex = put_gex - call_gex
            gamma_profile[k] = net_gex

        flip_strike = current_spot
        prev_k = strikes[0]
        prev_gex = gamma_profile[prev_k]

        for k in strikes[1:]:
            curr_gex = gamma_profile[k]
            if (prev_gex < 0 and curr_gex >= 0) or (prev_gex > 0 and curr_gex <= 0):
                flip_strike = prev_k + (0 - prev_gex) * (k - prev_k) / (curr_gex - prev_gex)
                break
            prev_k, prev_gex = k, curr_gex

        current_gex_val = gamma_profile.get(min(strikes, key=lambda x: abs(x - current_spot)), 0)
        regime = "LONG_GAMMA_PINNING_RANGE" if current_gex_val >= 0 else "SHORT_GAMMA_VOLATILITY_SQUEEZE"

        return {
            "zero_gamma_flip_level": round(flip_strike, 2),
            "current_spot": current_spot,
            "dist_to_flip_pct": round(((flip_strike - current_spot) / current_spot) * 100, 2),
            "current_regime": regime
        }
