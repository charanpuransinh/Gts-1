import pandas as pd


class OptionsChain:
    """Manages raw option chain matrix"""

    def __init__(self, raw_chain_df: pd.DataFrame):
        self.chain = raw_chain_df

    def get_atm_strike(self, spot_price: float) -> float:
        strikes = self.chain['strike'].values
        return min(strikes, key=lambda x: abs(x - spot_price))

    def get_strike_data(self, strike: float) -> pd.DataFrame:
        return self.chain[self.chain['strike'] == strike]
