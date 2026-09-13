from typing import Dict, Any, Optional


class MTFConfluenceEngine:
    """मल्टी-टाइमफ्रेम ट्रेंड, मोमेंटम और वोलेटिलिटी का वेटेड कॉनफ्लुएंस स्कोर (0-100)"""

    def __init__(self, tf_weights: Optional[Dict[str, float]] = None):
        self.weights = tf_weights or {"1m": 0.10, "5m": 0.20, "15m": 0.30, "1h": 0.25, "1d": 0.15}

    def evaluate(self, tf_signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        total_weight = 0.0
        weighted_score = 0.0
        details = {}

        for tf, data in tf_signals.items():
            if tf not in self.weights:
                continue
            w = self.weights[tf]
            trend = data.get("trend_bias", 0)
            rsi = data.get("rsi", 50)
            supertrend = 1 if data.get("supertrend_direction", "UP") == "UP" else -1
            rsi_score = (rsi - 50.0) / 50.0
            score = (trend * 0.4) + (supertrend * 0.4) + (rsi_score * 0.2)
            weighted_score += score * w
            total_weight += w
            details[tf] = round(score, 3)

        final_normalized_score = round(((weighted_score / total_weight) + 1.0) * 50.0, 2) if total_weight > 0 else 50.0

        if final_normalized_score >= 70:
            bias = "STRONG_BULLISH_CONFLUENCE"
        elif final_normalized_score <= 30:
            bias = "STRONG_BEARISH_CONFLUENCE"
        else:
            bias = "MIXED_NEUTRAL"

        return {"confluence_score": final_normalized_score, "overall_bias": bias, "timeframe_breakdown": details}
