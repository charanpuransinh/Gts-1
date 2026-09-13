import pandas as pd
from .ema import calculate_ema
from .rsi import calculate_rsi
from .macd import calculate_macd
from .supertrend import calculate_supertrend
from .adx import calculate_adx
from .atr import calculate_atr
from .price_action import detect_candlestick_patterns
from .fibonacci import calculate_fibonacci_levels
from .pivot import calculate_pivot_points


class IndicatorEngine:
    """Master Engine to process all technical indicators on standard OHLCV Data.

    process_all(df)  -> full time-series DataFrame with every indicator as a column
                         (use this for backtesting / charting / historical analysis)
    snapshot(df)     -> dict of the latest bar's values, plus Fibonacci & Pivot levels
                         computed off the latest swing (use this for real-time decisions)
    """

    def process_all(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out['ema_9'] = calculate_ema(out, 9)
        out['ema_21'] = calculate_ema(out, 21)
        out['ema_50'] = calculate_ema(out, 50)
        out['rsi'] = calculate_rsi(out)

        macd_df = calculate_macd(out)
        out = pd.concat([out, macd_df], axis=1)

        st_df = calculate_supertrend(out)
        out = pd.concat([out, st_df], axis=1)

        adx_df = calculate_adx(out)
        out = pd.concat([out, adx_df], axis=1)

        out['atr'] = calculate_atr(out)

        patterns = detect_candlestick_patterns(out)
        out = pd.concat([out, patterns], axis=1)

        return out

    def snapshot(self, df: pd.DataFrame, swing_lookback: int = 20) -> dict:
        processed = self.process_all(df)
        latest = processed.iloc[-1].to_dict()

        swing_high = float(df['high'].tail(swing_lookback).max())
        swing_low = float(df['low'].tail(swing_lookback).min())
        latest_close = float(df['close'].iloc[-1])

        latest['fibonacci'] = calculate_fibonacci_levels(swing_high, swing_low)
        latest['pivot'] = calculate_pivot_points(swing_high, swing_low, latest_close)
        return latest
