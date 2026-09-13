import pandas as pd


class OptionsVolumeAnalysis:
    """Calculates Option volume dynamics and unusual surge"""

    def analyze_volume_spike(self, chain_df: pd.DataFrame) -> pd.DataFrame:
        df = chain_df.copy()
        df['vol_oi_ratio'] = df['volume'] / (df['open_interest'] + 1e-9)
        df['is_unusual_volume'] = df['vol_oi_ratio'] > 2.0
        return df
