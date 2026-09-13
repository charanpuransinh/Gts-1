class MarketAIAdapter:
    """Formats market and options intelligence into normalized AI inputs"""

    def format_ai_payload(self, regime_data: dict, expiry_data: dict) -> dict:
        return {
            "status": "SUCCESS",
            "market_regime": regime_data.get("regime", "UNKNOWN"),
            "expiry_intelligence": expiry_data,
            "data_quality": "HIGH"
        }
