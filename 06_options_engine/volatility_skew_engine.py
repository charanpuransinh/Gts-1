import pandas as pd


class VolatilitySkewEngine:
    """Options-specific IV skew analysis (needs an options chain)."""

    def analyze_skew_collapse(self, chain_df: pd.DataFrame) -> dict:
        otm_calls = chain_df[(chain_df['option_type'] == 'CE')].tail(3)
        otm_puts = chain_df[(chain_df['option_type'] == 'PE')].head(3)

        call_iv = otm_calls['iv'].mean() if not otm_calls.empty else 0.0
        put_iv = otm_puts['iv'].mean() if not otm_puts.empty else 0.0
        skew_ratio = put_iv / (call_iv + 1e-9)

        return {"skew_ratio": float(round(skew_ratio, 3)), "call_iv": call_iv, "put_iv": put_iv}
