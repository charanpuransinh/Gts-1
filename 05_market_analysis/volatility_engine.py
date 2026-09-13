import pandas as pd


class VolatilityEngine:
    """Evaluates market volatility status"""

    def analyze(self, df: pd.DataFrame) -> dict:
        latest_atr = df['atr'].iloc[-1]
        mean_atr = df['atr'].tail(50).mean()

        volatility_ratio = latest_atr / (mean_atr + 1e-9)

        state = "NORMAL"
        if volatility_ratio > 1.5:
            state = "HIGH"
        elif volatility_ratio < 0.7:
            state = "LOW"

        return {
            "atr": float(latest_atr),
            "volatility_ratio": float(volatility_ratio),
            "state": state
        }
