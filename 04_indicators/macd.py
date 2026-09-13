import pandas as pd


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9,
                    column: str = 'close') -> pd.DataFrame:
    """MACD, Signal Line, and Histogram Calculation"""
    fast_ema = df[column].ewm(span=fast, adjust=False).mean()
    slow_ema = df[column].ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })
