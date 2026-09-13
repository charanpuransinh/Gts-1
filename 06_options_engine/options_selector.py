import pandas as pd
from .strike_selection import StrikeSelector
from .gamma_blast_selector import GammaBlastStrikeSelector


class OptionsSelector:
    """Wrapper to select strikes for Scalping, Intraday, and Expiry"""

    def __init__(self):
        self.selector = StrikeSelector()
        self.blast_selector = GammaBlastStrikeSelector()

    def get_best_expiry_strike(self, chain_df: pd.DataFrame, option_type: str) -> float:
        return self.selector.select_strike_by_delta(chain_df, target_delta=0.35, option_type=option_type)

    def get_strike_for_scenario(self, chain_df, gex_regime: dict, volatility_state: dict,
                                 expiry_bias: str, option_type: str = 'CE', capital_per_trade: float = 1000.0) -> dict:
        """Decides at runtime: normal ATM/delta strike, OR cheap-OTM gamma-blast strike + higher quantity."""
        decision = self.blast_selector.decide(chain_df, gex_regime, volatility_state, expiry_bias,
                                               option_type=option_type, capital_per_trade=capital_per_trade)
        if decision["mode"] == "BLAST_MODE":
            return decision
        atm_strike = self.get_best_expiry_strike(chain_df, option_type)
        return {"mode": "NORMAL_ATM_MODE", "strike": atm_strike, "suggested_quantity": 1}
