import pandas as pd
import numpy as np


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Average Directional Index (ADX) Calculation"""
    high = df['high']
    low = df['low']
    close = df['close']

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    tr1 = high - low
    tr2 = np.abs(high - close.shift(1))
    tr3 = np.abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # FIX: +1e-9 added to avoid divide-by-zero on flat/sideways candles
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(window=period).mean() / (atr + 1e-9))
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(window=period).mean() / (atr + 1e-9))

    dx = 100 * (np.abs(plus_di - minus_di) / np.abs(plus_di + minus_di + 1e-9))
    adx = dx.rolling(window=period).mean()

    return pd.DataFrame({
        'adx': adx,
        'plus_di': plus_di,
        'minus_di': minus_di
    })
