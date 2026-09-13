from typing import Dict, Any
import pandas as pd


class CrossAssetCorrelationEngine:
    """DXY, Gold, Crude, Nifty, VIX इत्यादि का रोलिंग पियर्सन कोरिलेशन और डाइवर्जेंस ट्रिगर"""

    def calculate_matrix(self, price_df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
        if price_df.empty or len(price_df) < window:
            return {"error": "Insufficient historical data for correlation"}

        returns = price_df.pct_change().dropna().tail(window)
        corr_matrix = returns.corr().round(4).to_dict()

        divergence_alerts = []
        if "DXY" in corr_matrix and "GOLD" in corr_matrix:
            curr_corr = corr_matrix["DXY"]["GOLD"]
            if curr_corr > 0.4:
                divergence_alerts.append({
                    "pair": "DXY_GOLD", "correlation": curr_corr,
                    "alert": "ANOMALOUS_POSITIVE_CORRELATION_DIVERGENCE"
                })

        return {"window": window, "correlation_matrix": corr_matrix, "divergence_alerts": divergence_alerts}
