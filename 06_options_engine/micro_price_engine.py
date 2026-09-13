from typing import Dict, Any


class OptionMicroPriceEngine:
    """
    Option Micro-Price & Order Flow Imbalance (OFI) Engine
    MicroPrice = (Bid_Size * Ask_Price + Ask_Size * Bid_Price) / (Bid_Size + Ask_Size)
    """

    def calculate_micro_price(self, bid_price: float, ask_price: float, bid_size: float, ask_size: float) -> Dict[str, Any]:
        total_depth = bid_size + ask_size
        if total_depth <= 0:
            mid_price = (bid_price + ask_price) / 2.0
            return {"micro_price": mid_price, "imbalance_ratio": 0.0, "scalp_signal": "NEUTRAL"}

        micro_price = (bid_size * ask_price + ask_size * bid_price) / total_depth
        mid_price = (bid_price + ask_price) / 2.0
        imbalance = (bid_size - ask_size) / total_depth

        if imbalance > 0.4:
            signal = "AGGRESSIVE_BUY_IMBALANCE"
        elif imbalance < -0.4:
            signal = "AGGRESSIVE_SELL_IMBALANCE"
        else:
            signal = "BALANCED_ORDER_BOOK"

        return {
            "mid_price": round(mid_price, 2), "micro_price": round(micro_price, 2),
            "micro_mid_diff": round(micro_price - mid_price, 4),
            "order_imbalance_ratio": round(imbalance, 4), "scalp_signal": signal
        }
