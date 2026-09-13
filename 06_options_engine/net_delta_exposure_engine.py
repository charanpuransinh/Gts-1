import pandas as pd
from typing import Dict, Any


class NetDeltaExposureEngine:
    """
    Net Delta Exposure (DEX) Regime Engine
    Calculates total dealer delta positioning across Call and Put chains.
    """

    def calculate_dex_regime(self, chain_df: pd.DataFrame, spot_price: float, contract_size: int = 25) -> Dict[str, Any]:
        """chain_df requires: ['strike', 'delta', 'open_interest', 'option_type']"""
        if chain_df.empty:
            return {"error": "Empty chain dataframe"}

        call_sub = chain_df[chain_df["option_type"] == "CE"]
        put_sub = chain_df[chain_df["option_type"] == "PE"]

        call_dex = (call_sub["delta"] * call_sub["open_interest"]).sum() * contract_size * spot_price
        put_dex = (put_sub["delta"].abs() * put_sub["open_interest"]).sum() * contract_size * spot_price

        net_dealer_dex = put_dex - call_dex

        if net_dealer_dex > 1e7:
            regime = "DEALER_LONG_DELTA_BULLISH_SUPPORT"
        elif net_dealer_dex < -1e7:
            regime = "DEALER_SHORT_DELTA_BEARISH_PRESSURE"
        else:
            regime = "DEALER_DELTA_NEUTRAL"

        return {
            "spot_price": spot_price, "call_dex_val": round(call_dex, 2), "put_dex_val": round(put_dex, 2),
            "net_dealer_dex": round(net_dealer_dex, 2), "dex_regime": regime
        }
