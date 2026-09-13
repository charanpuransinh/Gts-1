import math
import sys
import os
from typing import Dict, List, Any, Optional

# Reuse the ACTUAL velocity-aware trailing engine (10_risk_execution_support) instead of
# reinventing a weaker, flat-percentage trail under a "Hyper-Velocity" label.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from importlib import import_module
_hvt_mod = import_module('10_risk_execution_support.hyper_velocity_trailing_engine')
HyperVelocityTrailingEngine = _hvt_mod.HyperVelocityTrailingEngine


class GammaBlastHouseMoneyEngine:
    """
    House Money Counter-Hedge Engine for Expiry Blast Reversals.
    Triggers cheap OTM counter-options using locked gains from a 5x primary move.
    """

    def __init__(self, trigger_multiplier: float = 5.0, reinvest_profit_pct: float = 0.10,
                 counter_target_premium: float = 5.0, initial_sl_ratio: float = 0.50):
        self.trigger_multiplier = trigger_multiplier
        self.reinvest_profit_pct = reinvest_profit_pct
        self.counter_target_premium = counter_target_premium
        self.initial_sl_ratio = initial_sl_ratio
        self._hvt_engine = HyperVelocityTrailingEngine()

    def evaluate_counter_hedge_trigger(self, primary_trade: Dict[str, Any],
                                        opposite_chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        primary_trade dict: {"symbol":..., "entry_price":..., "current_price":..., "lots":...,
                              "lot_size":..., "triggered_already": False}
        """
        entry_p = primary_trade["entry_price"]
        curr_p = primary_trade["current_price"]
        lots = primary_trade.get("lots", 1)
        lot_size = primary_trade.get("lot_size", 25)

        # BUG FIX: lot_size <= 0 (bad config/data) caused a ZeroDivisionError further down
        if lot_size <= 0:
            return {"error": f"Invalid lot_size ({lot_size}) — must be > 0"}

        current_multiplier = curr_p / entry_p if entry_p > 0 else 0.0
        unrealized_profit = (curr_p - entry_p) * (lots * lot_size)

        if current_multiplier < self.trigger_multiplier or primary_trade.get("triggered_already", False):
            return {
                "trigger_status": "NO_TRIGGER", "current_multiplier": round(current_multiplier, 2),
                "unrealized_profit": round(unrealized_profit, 2), "counter_hedge_signal": None
            }

        allocated_budget = unrealized_profit * self.reinvest_profit_pct

        selected_counter_option = None
        min_price_diff = float("inf")
        for opt in opposite_chain:
            prem = opt.get("premium", 0.0)
            if 2.0 <= prem <= 8.0:
                diff = abs(prem - self.counter_target_premium)
                if diff < min_price_diff:
                    min_price_diff = diff
                    selected_counter_option = opt

        if not selected_counter_option:
            return {
                "trigger_status": "MULTIPLIER_MET_BUT_NO_SUITABLE_COUNTER_STRIKE",
                "current_multiplier": round(current_multiplier, 2), "counter_hedge_signal": None
            }

        counter_price = selected_counter_option["premium"]
        max_contracts = math.floor(allocated_budget / (counter_price * lot_size))
        counter_lots = max(max_contracts, 1)

        actual_cost = counter_price * counter_lots * lot_size
        # BUG FIX: forcing a minimum of 1 lot can cost more than the "house money" budget
        # allocated from profit — that silently pulls in fresh capital beyond what this
        # strategy is supposed to risk. Flag it explicitly, same pattern as gamma_blast_selector.
        budget_exceeded = actual_cost > allocated_budget

        hard_sl_price = counter_price * self.initial_sl_ratio

        counter_signal = {
            "signal_action": "BUY_COUNTER_HEDGE", "strike": selected_counter_option["strike"],
            "option_type": selected_counter_option["option_type"], "entry_target_price": round(counter_price, 2),
            "calculated_lots": counter_lots, "allocated_budget": round(allocated_budget, 2),
            "actual_cost": round(actual_cost, 2), "budget_exceeded": bool(budget_exceeded),
            "initial_hard_sl": round(hard_sl_price, 2), "trailing_engine_active": True
        }

        return {
            "trigger_status": "COUNTER_HEDGE_TRIGGERED", "primary_multiplier": round(current_multiplier, 2),
            "primary_unrealized_profit": round(unrealized_profit, 2), "counter_hedge_signal": counter_signal
        }

    def process_counter_leg_trailing(self, entry_price: float, current_price: float, high_water_mark: float,
                                      atr_val: float = None, price_change_1s: float = 0.0,
                                      time_elapsed_sec: float = 0.0) -> Dict[str, Any]:
        """
        Manages Hard SL and Trailing SL for the cheap counter-hedge leg.

        FIX: below entry, kept as a fixed 50% hard SL (simple, deliberate — no trailing needed on
        the downside since it hasn't worked yet).

        Above entry: now genuinely delegates to HyperVelocityTrailingEngine (velocity-aware,
        non-linear) instead of a flat static 3% trail — the counter-hedge leg is bought specifically
        to catch a fast reversal, so its own exit must be at least as fast-reacting as the engine
        already built for exactly this purpose. Pass price_change_1s (points/sec) from your live
        tick feed for this to actually react to speed; it degrades safely to a plain ATR trail if
        you don't have tick-level velocity data yet (atr_val defaults to 3% of price if not given).
        """
        if entry_price <= 0 or current_price <= 0:
            return {"error": f"Invalid price (entry={entry_price}, current={current_price}) — both must be > 0"}

        high_water_mark = max(high_water_mark, current_price)
        hard_sl = entry_price * self.initial_sl_ratio

        if current_price <= entry_price:
            active_sl = hard_sl
            sl_state = "HARD_50_PCT_SL"
            is_stopped_out = current_price <= active_sl
            return {
                "current_price": round(current_price, 2), "high_water_mark": round(high_water_mark, 2),
                "active_stop_loss": round(active_sl, 2), "sl_state": sl_state, "is_stopped_out": is_stopped_out
            }

        # Above entry: delegate to the real velocity-aware engine
        effective_atr = atr_val if atr_val is not None else high_water_mark * 0.03
        hvt_result = self._hvt_engine.calculate_hyper_tsl(
            entry_price=entry_price, current_price=current_price, high_water_mark=high_water_mark,
            atr_val=effective_atr, time_elapsed_sec=time_elapsed_sec, price_change_1s=price_change_1s
        )
        return {
            "current_price": hvt_result.get("current_price"), "high_water_mark": hvt_result.get("high_water_mark"),
            "active_stop_loss": hvt_result.get("trailing_stop_price"), "sl_state": "HYPER_TRAILING_ACTIVE",
            "is_stopped_out": hvt_result.get("is_stop_triggered"), "velocity_multiplier": hvt_result.get("velocity_multiplier"),
            "ratchet_status": hvt_result.get("ratchet_status")
        }
