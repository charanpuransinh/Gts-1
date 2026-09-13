from typing import Dict, List, Any


class GammaBlastLadderEngine:
    """
    Laddered Counter-Hedge Engine for Gamma-Blast Reversals (Owner's mechanism):

    - Track A (existing, via OptionsSelector): normal ATM-based strike — runs independently, let it ride.
    - Track B (existing, via GammaBlastStrikeSelector): cheap OTM strike bought in quantity once a
      blast is confirmed.
    - THIS ENGINE: as Track B's price climbs through successive multiplier rungs (e.g. entry ₹10 ->
      ₹20 -> ₹30 -> ₹40), ladder in a fresh counter-hedge buy on the OPPOSITE side at each rung, at a
      cheap (~₹4-5) premium, DOUBLING the counter quantity at every successive rung.

    Rationale: if the blast keeps running, Track A/B keep compounding — that's the main win. If it
    reverses instead, these laddered counter legs catch the reversal. But a reversal move is usually
    SLOWER than the initial blast, so these counter legs use a SMALLER profit target (~2x, e.g.
    ₹5 -> ₹10-11) with a tighter trail once that zone is reached — not the aggressive ratchet used
    for the primary blast leg.

    Stateless by design (matches the rest of this codebase): the caller persists `triggered_levels`
    (which rungs have already fired for this position) and passes it back in each call.
    """

    def __init__(self, ladder_multipliers=(2.0, 3.0, 4.0, 6.0, 8.0), base_counter_lots: int = 1,
                 counter_target_premium: float = 5.0, counter_take_profit_multiplier: float = 2.0,
                 counter_trail_pct: float = 0.15):
        self.ladder_multipliers = sorted(ladder_multipliers)
        self.base_counter_lots = base_counter_lots
        self.counter_target_premium = counter_target_premium
        self.counter_take_profit_multiplier = counter_take_profit_multiplier  # e.g. 2.0x: 5 -> 10
        self.counter_trail_pct = counter_trail_pct

    def evaluate_ladder_trigger(self, primary_trade: Dict[str, Any], opposite_chain: List[Dict[str, Any]],
                                 triggered_levels: List[float]) -> Dict[str, Any]:
        entry_p = primary_trade["entry_price"]
        curr_p = primary_trade["current_price"]
        if entry_p <= 0:
            return {"error": f"Invalid entry_price ({entry_p}) — must be > 0"}

        current_multiplier = curr_p / entry_p

        next_level = None
        rung_index = None
        for idx, level in enumerate(self.ladder_multipliers):
            if current_multiplier >= level and level not in triggered_levels:
                next_level = level
                rung_index = idx

        if next_level is None:
            return {"trigger_status": "NO_NEW_RUNG", "current_multiplier": round(current_multiplier, 2)}

        selected = None
        min_diff = float("inf")
        for opt in opposite_chain:
            prem = opt.get("premium", 0.0)
            if 2.0 <= prem <= 8.0:
                diff = abs(prem - self.counter_target_premium)
                if diff < min_diff:
                    min_diff = diff
                    selected = opt

        if not selected:
            return {"trigger_status": "RUNG_HIT_NO_SUITABLE_STRIKE", "rung_level": next_level,
                    "current_multiplier": round(current_multiplier, 2)}

        counter_lots = self.base_counter_lots * (2 ** rung_index)  # doubles every rung
        counter_price = selected["premium"]

        return {
            "trigger_status": "LADDER_RUNG_TRIGGERED",
            "rung_level": next_level,
            "rung_index": rung_index,
            "current_multiplier": round(current_multiplier, 2),
            "counter_hedge_signal": {
                "signal_action": "BUY_COUNTER_HEDGE_LADDER",
                "strike": selected["strike"], "option_type": selected["option_type"],
                "entry_target_price": round(counter_price, 2),
                "calculated_lots": counter_lots,
                "take_profit_target": round(counter_price * self.counter_take_profit_multiplier, 2)
            },
            "updated_triggered_levels": sorted(list(triggered_levels) + [next_level])
        }

    def process_counter_leg_exit(self, entry_price: float, current_price: float, high_water_mark: float) -> Dict[str, Any]:
        """Gentler exit for laddered counter legs — small target (~2x, e.g. 5 -> 10-11), light trail
        while still building toward that target, then tightens hard once the target zone is reached."""
        if entry_price <= 0 or current_price <= 0:
            return {"error": f"Invalid price (entry={entry_price}, current={current_price}) — both must be > 0"}

        high_water_mark = max(high_water_mark, current_price)
        hard_sl = entry_price * 0.50
        target_price = entry_price * self.counter_take_profit_multiplier

        if current_price <= entry_price:
            active_sl = hard_sl
            state = "HARD_50_PCT_SL"
        elif current_price < target_price:
            active_sl = max(entry_price, high_water_mark - (high_water_mark * 0.20))
            state = "APPROACHING_TARGET"
        else:
            trail_gap = max(high_water_mark * self.counter_trail_pct, 0.30)
            active_sl = max(entry_price, high_water_mark - trail_gap)
            state = "TARGET_ZONE_LOCKING_PROFIT"

        is_stopped_out = current_price <= active_sl
        return {
            "current_price": round(current_price, 2), "high_water_mark": round(high_water_mark, 2),
            "target_price": round(target_price, 2), "active_stop_loss": round(active_sl, 2),
            "sl_state": state, "is_stopped_out": is_stopped_out
        }
