import pandas as pd


def calculate_ema(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """Exponential Moving Average (EMA) Calculation"""
    if column not in df.columns:
        raise ValueError(f"Column {column} not found in DataFrame")
    return df[column].ewm(span=period, adjust=False).mean()
