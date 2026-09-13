import pandas as pd


class StrikeSelector:
    """Selects optimum strikes based on delta and strategy rules"""

    def select_strike_by_delta(self, chain_df: pd.DataFrame, target_delta: float, option_type: str = 'CE') -> float:
        subset = chain_df[chain_df['option_type'] == option_type].copy()
        if subset.empty:
            return 0.0
        subset['delta_diff'] = (subset['delta'].abs() - abs(target_delta)).abs()
        best_row = subset.sort_values('delta_diff').iloc[0]
        return best_row['strike']
