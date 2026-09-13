import pandas as pd


class OpenInterestEngine:
    """PCR, OI shifts, and Max Pain computation"""

    def calculate_pcr(self, chain_df: pd.DataFrame) -> float:
        total_pe_oi = chain_df[chain_df['option_type'] == 'PE']['open_interest'].sum()
        total_ce_oi = chain_df[chain_df['option_type'] == 'CE']['open_interest'].sum()
        return round(total_pe_oi / (total_ce_oi + 1e-9), 3)

    def calculate_max_pain(self, chain_df: pd.DataFrame) -> float:
        strikes = chain_df['strike'].unique()
        losses = {}
        for strike in strikes:
            ce_loss = chain_df[chain_df['option_type'] == 'CE'].apply(
                lambda r: max(0, strike - r['strike']) * r['open_interest'], axis=1).sum()
            pe_loss = chain_df[chain_df['option_type'] == 'PE'].apply(
                lambda r: max(0, r['strike'] - strike) * r['open_interest'], axis=1).sum()
            losses[strike] = ce_loss + pe_loss
        return min(losses, key=losses.get)
