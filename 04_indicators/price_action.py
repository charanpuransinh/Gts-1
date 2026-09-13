import pandas as pd


def detect_candlestick_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Price Action Candlestick Pattern Recognition"""
    patterns = pd.DataFrame(index=df.index)

    body = (df['close'] - df['open']).abs()
    upper_wick = df['high'] - df[['open', 'close']].max(axis=1)
    lower_wick = df[['open', 'close']].min(axis=1) - df['low']
    candle_range = df['high'] - df['low']

    patterns['hammer'] = (lower_wick >= 2 * body) & (upper_wick <= body * 0.5) & (candle_range > 0)
    patterns['doji'] = body <= (candle_range * 0.1)
    patterns['bullish_engulfing'] = (
        (df['close'].shift(1) < df['open'].shift(1)) &
        (df['close'] > df['open']) &
        (df['close'] >= df['open'].shift(1)) &
        (df['open'] <= df['close'].shift(1))
    )
    return patterns
