import pandas as pd


class MomentumEngine:
    """Evaluates momentum oversold/overbought states"""

    def analyze(self, df: pd.DataFrame) -> dict:
        rsi = df['rsi'].iloc[-1]
        macd_hist = df['histogram'].iloc[-1]

        status = "NEUTRAL"
        if rsi > 70:
            status = "OVERBOUGHT"
        elif rsi < 30:
            status = "OVERSOLD"

        return {
            "rsi": float(rsi),
            "macd_hist": float(macd_hist),
            "status": status,
            "momentum_direction": "BULLISH" if macd_hist > 0 else "BEARISH"
        }
