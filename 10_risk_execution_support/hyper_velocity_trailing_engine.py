import math
from typing import Dict, Any


class HyperVelocityTrailingEngine:
    """
    Hyper-Velocity Trailing Stop-Loss & Re-Entry Trigger Engine for Gamma Blasts.
    Calculates dynamic non-linear trailing levels based on price acceleration.
    """

    def __init__(self, base_atr_mult: float = 1.5, min_trail_pct: float = 0.025):
        self.base_atr_mult = base_atr_mult
        self.min_trail_pct = min_trail_pct  # Minimum 2.5% trail gap during peak blast

    def calculate_hyper_tsl(self, entry_price: float, current_price: float, high_water_mark: float,
                             atr_val: float, time_elapsed_sec: float, price_change_1s: float) -> Dict[str, Any]:

        # BUG FIX: entry_price<=0 or current_price<=0 (bad tick / data glitch) would divide by zero below
        if entry_price <= 0 or current_price <= 0:
            return {"error": f"Invalid price (entry={entry_price}, current={current_price}) — both must be > 0"}

        high_water_mark = max(high_water_mark, current_price)
        total_gain_pct = ((high_water_mark - entry_price) / entry_price)

        velocity = max(price_change_1s, 0.0)
        velocity_multiplier = 1.0 + math.log1p(velocity)

        base_trail_gap = atr_val * self.base_atr_mult
        hyper_trail_gap = base_trail_gap / velocity_multiplier

        min_allowed_gap = high_water_mark * self.min_trail_pct
        final_trail_gap = max(hyper_trail_gap, min_allowed_gap)

        calculated_tsl = high_water_mark - final_trail_gap

        # BUG FIX (major): the original defaulted ratchet_sl = entry_price even at ZERO profit.
        # Since calculated_tsl sits below entry_price whenever there's no real gain yet, max()
        # always picked entry_price — forcing the stop to breakeven the instant the trade opened,
        # with NO room for normal entry noise. This would stop nearly every gamma-blast trade out
        # within seconds, before the blast even develops. Fix: below the first profit-lock
        # threshold (25%), the ratchet must NOT override the ATR-based calculated_tsl at all.
        ratchet_sl = calculated_tsl
        ratchet_status = "INITIAL_RISK"

        if total_gain_pct >= 2.0:
            ratchet_sl = max(calculated_tsl, entry_price * 2.75)
            ratchet_status = "LOCKED_275_PCT_PROFIT"
        elif total_gain_pct >= 1.0:
            ratchet_sl = max(calculated_tsl, entry_price * 1.80)
            ratchet_status = "LOCKED_180_PCT_PROFIT"
        elif total_gain_pct >= 0.50:
            ratchet_sl = max(calculated_tsl, entry_price * 1.35)
            ratchet_status = "LOCKED_135_PCT_PROFIT"
        elif total_gain_pct >= 0.25:
            ratchet_sl = max(calculated_tsl, entry_price * 1.05)
            ratchet_status = "COST_PLUS_LOCK"

        final_tsl = max(calculated_tsl, ratchet_sl)

        is_stop_triggered = current_price <= final_tsl
        re_entry_trigger_price = high_water_mark * 1.002 if is_stop_triggered else None

        return {
            "current_price": round(current_price, 2),
            "high_water_mark": round(high_water_mark, 2),
            "trailing_stop_price": round(final_tsl, 2),
            "distance_to_tsl_pct": round(((current_price - final_tsl) / current_price) * 100.0, 2),
            "velocity_multiplier": round(velocity_multiplier, 2),
            "ratchet_status": ratchet_status,
            "is_stop_triggered": is_stop_triggered,
            "re_entry_breakout_trigger": round(re_entry_trigger_price, 2) if re_entry_trigger_price else None
        }
