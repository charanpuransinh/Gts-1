class ExpirySignalEngine:
    """Generates direct trading setup inputs for Expiry Day"""

    def generate_signal_input(self, expiry_analysis: dict) -> dict:
        bias = expiry_analysis.get('expiry_bias', 'NEUTRAL')
        pte = expiry_analysis.get('hours_to_expiry', 24)

        signal = "HOLD"
        confidence = 0.0

        if bias in ["BULLISH_PINNING", "BEARISH_PINNING"] and pte < 4:
            signal = "SELL_STRADDLE_OR_STRANGLE"
            confidence = 0.85
        elif bias == "HERO_ZERO_BREAKOUT" and pte < 2:
            signal = "BUY_MOMENTUM_OPTION"
            confidence = 0.75

        return {
            "recommended_action": signal,
            "confidence": confidence,
            "strategy_type": "EXPIRY_SPECIALIST"
        }
