import pandas as pd


class StraddleScanner:
    """ATM Straddle Scanner Engine.
    NOTE: strike-by-delta selection is intentionally NOT duplicated here — use the existing
    StrikeSelector.select_strike_by_delta() from strike_selection.py for that."""

    @staticmethod
    def get_atm_strike(spot_price: float, strike_gap: float) -> float:
        """Finds the exact ATM Strike based on Spot Price and Strike Interval"""
        return round(spot_price / strike_gap) * strike_gap

    @staticmethod
    def calculate_atm_straddle(chain_df: pd.DataFrame, spot_price: float, strike_gap: float) -> dict:
        """Calculates ATM Straddle Combined Premium, Breakevens, and Straddle Width"""
        atm_strike = StraddleScanner.get_atm_strike(spot_price, strike_gap)

        ce_row = chain_df[(chain_df['strike'] == atm_strike) & (chain_df['option_type'].str.upper().isin(['CE', 'CALL']))]
        pe_row = chain_df[(chain_df['strike'] == atm_strike) & (chain_df['option_type'].str.upper().isin(['PE', 'PUT']))]

        ce_price = float(ce_row['premium'].values[0]) if not ce_row.empty else 0.0
        pe_price = float(pe_row['premium'].values[0]) if not pe_row.empty else 0.0

        straddle_premium = ce_price + pe_price
        upper_breakeven = atm_strike + straddle_premium
        lower_breakeven = atm_strike - straddle_premium

        return {
            "atm_strike": atm_strike,
            "ce_price": ce_price,
            "pe_price": pe_price,
            "combined_straddle_premium": round(straddle_premium, 2),
            "upper_breakeven": round(upper_breakeven, 2),
            "lower_breakeven": round(lower_breakeven, 2),
            "expected_move_pct": round((straddle_premium / spot_price) * 100, 2)
        }
