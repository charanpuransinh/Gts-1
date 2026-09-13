import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable


class PureIntelligenceBacktestEngine:
    """
    AI-2 Pure Intelligence Signal Replay Engine
    (Zero execution/broker logic - pure signal accuracy validator)
    """

    def run_signal_backtest(
        self,
        ohlcv_df: pd.DataFrame,
        signal_generator_fn: Callable[[pd.DataFrame, int], Dict[str, Any]],
        holding_bars: int = 5
    ) -> Dict[str, Any]:

        if len(ohlcv_df) < 50:
            return {"error": "Insufficient bars for backtesting"}

        signals_logged = []
        winning_signals = 0
        losing_signals = 0
        total_return_pct = 0.0
        returns_list = []

        for i in range(30, len(ohlcv_df) - holding_bars):
            window_df = ohlcv_df.iloc[:i + 1]
            signal_res = signal_generator_fn(window_df, i)

            sig_type = signal_res.get("signal", "NEUTRAL")
            if sig_type in ["BUY", "SELL", "GAMMA_BLAST_CALL", "GAMMA_BLAST_PUT"]:
                entry_price = ohlcv_df.iloc[i]["close"]
                exit_price = ohlcv_df.iloc[i + holding_bars]["close"]

                if "BUY" in sig_type or "CALL" in sig_type:
                    pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
                else:
                    pnl_pct = ((entry_price - exit_price) / entry_price) * 100.0

                returns_list.append(pnl_pct)
                total_return_pct += pnl_pct

                if pnl_pct > 0:
                    winning_signals += 1
                else:
                    losing_signals += 1

                signals_logged.append({
                    "bar_index": i, "signal": sig_type, "entry": entry_price,
                    "exit": exit_price, "pnl_pct": round(pnl_pct, 2)
                })

        total_trades = winning_signals + losing_signals
        win_rate = round((winning_signals / total_trades) * 100.0, 2) if total_trades > 0 else 0.0

        cum_returns = np.cumsum(returns_list)
        peak = np.maximum.accumulate(cum_returns) if len(cum_returns) > 0 else [0]
        drawdown = peak - cum_returns if len(cum_returns) > 0 else [0]
        max_dd = round(float(np.max(drawdown)), 2) if len(drawdown) > 0 else 0.0

        return {
            "total_signals_generated": total_trades,
            "win_rate_pct": win_rate,
            "total_cumulative_return_pct": round(total_return_pct, 2),
            "max_signal_drawdown_pct": max_dd,
            "profit_factor": round(
                sum([r for r in returns_list if r > 0]) / max(abs(sum([r for r in returns_list if r < 0])), 1e-5), 2
            ),
            "sample_signals": signals_logged[:5]
        }
