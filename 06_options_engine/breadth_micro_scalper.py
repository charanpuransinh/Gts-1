from typing import Dict, List, Any, Optional


class BreadthMicroScalperEngine:
    """
    3-Point Market Breadth Validation + Backbone Profit-Buffered Counter Scalper.
    """

    def __init__(self, breadth_threshold_pct: float = 0.50, backbone_profit_pct: float = 0.10,
                 counter_lot_ratio: float = 0.50, micro_scalp_sl_points: float = 1.0):
        self.breadth_threshold_pct = breadth_threshold_pct
        self.backbone_profit_pct = backbone_profit_pct
        self.counter_lot_ratio = counter_lot_ratio
        self.micro_scalp_sl_points = micro_scalp_sl_points

    def validate_market_regime(self, index_trend_positive: bool, advancing_stocks_pct: float,
                                net_money_flow_positive: bool) -> Dict[str, Any]:
        """Validates 3-point alignment: Index Trend + Market Breadth + Money Flow."""
        is_breadth_ok = advancing_stocks_pct >= self.breadth_threshold_pct
        is_bullish_regime = index_trend_positive and is_breadth_ok and net_money_flow_positive

        return {
            "is_bullish_regime": is_bullish_regime, "index_trend": "POSITIVE" if index_trend_positive else "NEGATIVE",
            "advancing_stocks_pct": round(advancing_stocks_pct * 100, 1),
            "net_money_flow": "POSITIVE" if net_money_flow_positive else "NEGATIVE",
            "signal": "BUY_PRIMARY_CE" if is_bullish_regime else "NO_TRADE"
        }

    def process_scalp_lifecycle(self, primary_trade: Dict[str, Any], opposite_option: Dict[str, Any]) -> Dict[str, Any]:
        """
        primary_trade: {"entry_price": 100.0, "current_price": 112.0, "lots": 10}
        opposite_option: {"entry_price": 80.0, "current_price": 85.0, "high_mark": 85.0}
        """
        p_entry = primary_trade["entry_price"]
        p_curr = primary_trade["current_price"]
        p_lots = primary_trade.get("lots", 10)

        p_gain_pct = (p_curr - p_entry) / p_entry if p_entry > 0 else 0.0
        backbone_secured = p_gain_pct >= self.backbone_profit_pct

        counter_signal = "HOLD_OR_INACTIVE"
        counter_active = False

        # BUG FIX: comparing p_curr against a freshly-computed float threshold (entry*(1+a+b))
        # can fail at the exact boundary due to floating-point rounding (0.10+0.02 != exactly
        # 0.12 in binary floats) — the original demo's own example (112.0 vs threshold
        # 112.00000000000001) silently failed to trigger. Add a tiny epsilon tolerance.
        trigger_threshold = p_entry * (1.0 + self.backbone_profit_pct + 0.02)
        if backbone_secured and p_curr >= (trigger_threshold - 1e-6):
            counter_active = True
            counter_signal = "INITIATE_COUNTER_MICRO_SCALP"

        # BUG FIX: int(p_lots * ratio) truncates to 0 for small lot counts (e.g. 1 lot * 0.5 = 0),
        # which would report "scalp initiated" with literally zero size, and even show a spurious
        # exit trigger on a position that was never sized. Floor at 1 lot once active.
        counter_lots = max(1, round(p_lots * self.counter_lot_ratio)) if counter_active else 0

        c_entry = opposite_option.get("entry_price", 0.0)
        c_curr = opposite_option.get("current_price", 0.0)
        c_high = opposite_option.get("high_mark", c_curr)

        # BUG FIX: the original always floored the trailing SL at c_entry (max(high-gap, entry)),
        # which meant a FRESH counter leg (high_mark == entry, no real move yet) had its stop sitting
        # exactly AT entry — any normal entry-noise dip triggered an immediate false exit. Fix: only
        # floor at entry once the leg has actually moved up by at least micro_scalp_sl_points; until
        # then, give it its full SL cushion below entry like a normal fresh position.
        if c_entry > 0:
            if (c_high - c_entry) >= self.micro_scalp_sl_points:
                tight_sl = max(c_high - self.micro_scalp_sl_points, c_entry)
            else:
                tight_sl = c_entry - self.micro_scalp_sl_points
        else:
            tight_sl = 0.0

        is_counter_exit_triggered = c_curr <= tight_sl if counter_active and c_entry > 0 else False

        return {
            "primary_status": {
                "entry_price": round(p_entry, 2), "current_price": round(p_curr, 2),
                "gain_pct": round(p_gain_pct * 100, 2), "backbone_secured": backbone_secured
            },
            "counter_scalp_status": {
                "counter_active": counter_active, "counter_lots": counter_lots, "counter_signal": counter_signal,
                "opposite_entry": round(c_entry, 2), "opposite_current": round(c_curr, 2),
                "tight_trailing_sl": round(tight_sl, 2), "is_scalp_exit_triggered": is_counter_exit_triggered
            }
        }
