class StrategySuggestionInput:
    """Prepares suggestion vectors for upstream strategy allocation engines"""

    def generate_input_vector(self, ai_payload: dict) -> dict:
        regime = ai_payload.get("market_regime", "")
        expiry = ai_payload.get("expiry_intelligence", {})

        priority_suggestion = "INTRADAY"
        if expiry.get("hours_to_expiry", 99) <= 6:
            priority_suggestion = "EXPIRY_SPECIALIST"
        elif "HIGH_VOLATILITY" in regime:
            priority_suggestion = "SCALPING"

        return {
            "suggested_priority": priority_suggestion,
            "raw_payload": ai_payload
        }
