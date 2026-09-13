from typing import Dict, Any, Optional


class PullbackCounterScalpEngine:
    """
    Counter-Side Pullback Scalping alongside a core trending position (Owner's mechanism):

    - Track A (primary, e.g. 10 lots CE): a core trend position is bought and simply held while
      the trend runs — no averaging on this leg here, that's managed elsewhere.
    - THIS ENGINE (counter side): the market never moves in a straight line — the primary leg
      periodically pulls back (e.g. CE 115 -> 108), and during that exact pullback the OPPOSITE
      side's price bounces up (e.g. PE -> 80). That bounce is bought — a small fixed quantity
      (default 5 lots), with a tight symmetric bracket (default 5-point SL / 5-point target) —
      a quick scalp, not a directional bet.
    - Either outcome favors the trader: if the main trend resumes, the primary's running gains
      dwarf this scalp's small defined loss. If the pullback continues and the target is hit,
      it's extra profit on top.
    - After a scalp resolves, the NEXT counter-entry requires a DEEPER pullback than the last one
      (e.g. 80 -> then 77 -> then 75), so shallow wiggles don't trigger repeated re-entries —
      each subsequent entry demands more proof of a real pullback.

    Stateless by design: the caller persists `last_entry_level` (and open scalp state) and passes
    it back in each call.
    """

    def __init__(self, counter_lots: int = 5, bracket_points: float = 5.0, level_step_down: float = 3.0):
        self.counter_lots = counter_lots
        self.bracket_points = bracket_points
        self.level_step_down = level_step_down  # how much deeper the next entry threshold must be

    def evaluate_pullback_entry(self, counter_side_price: float, last_entry_level: Optional[float] = None) -> Dict[str, Any]:
        """
        counter_side_price: current price of the OPPOSITE side (the one rising during the
        primary's pullback).
        last_entry_level: price level of the previous counter-scalp entry (None for the first one).
        """
        if last_entry_level is None:
            required_level = None
            can_enter = True
        else:
            required_level = last_entry_level - self.level_step_down
            can_enter = counter_side_price <= required_level

        if not can_enter:
            return {
                "trigger_status": "WAITING_FOR_DEEPER_PULLBACK",
                "current_price": round(counter_side_price, 2),
                "required_level": round(required_level, 2) if required_level is not None else None
            }

        target = counter_side_price + self.bracket_points
        stop_loss = counter_side_price - self.bracket_points

        return {
            "trigger_status": "COUNTER_SCALP_ENTRY",
            "entry_price": round(counter_side_price, 2),
            "lots": self.counter_lots,
            "target": round(target, 2),
            "stop_loss": round(stop_loss, 2),
            "next_entry_must_be_at_or_below": round(counter_side_price - self.level_step_down, 2)
        }

    def check_scalp_outcome(self, entry_price: float, current_price: float) -> Dict[str, Any]:
        """Check if this scalp's fixed bracket has been hit yet."""
        if entry_price <= 0:
            return {"error": f"Invalid entry_price ({entry_price}) — must be > 0"}

        target = entry_price + self.bracket_points
        stop_loss = entry_price - self.bracket_points

        if current_price >= target:
            return {"outcome": "TARGET_HIT", "pnl_points": self.bracket_points}
        elif current_price <= stop_loss:
            return {"outcome": "STOP_LOSS_HIT", "pnl_points": -self.bracket_points}
        else:
            return {"outcome": "STILL_OPEN", "pnl_points": round(current_price - entry_price, 2)}
