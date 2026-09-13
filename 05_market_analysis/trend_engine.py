import pandas as pd


class TrendEngine:
    """Determines market trend direction and strength"""

    def analyze(self, df: pd.DataFrame) -> dict:
        latest = df.iloc[-1]

        ema_bullish = latest['ema_9'] > latest['ema_21'] > latest['ema_50']
        ema_bearish = latest['ema_9'] < latest['ema_21'] < latest['ema_50']

        trend = "SIDEWAYS"
        if ema_bullish and latest.get('direction', 0) == 1:
            trend = "BULLISH"
        elif ema_bearish and latest.get('direction', 0) == -1:
            trend = "BEARISH"

        strength = latest.get('adx', 0)

        return {
            "trend": trend,
            "strength": float(strength),
            "is_trending": bool(strength > 25)
        }
