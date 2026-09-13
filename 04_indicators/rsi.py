import pandas as pd
import numpy as np


def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """Relative Strength Index (RSI) Calculation"""
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / np.where(loss == 0, 1e-9, loss)
    rsi = 100 - (100 / (1 + rs))
    return rsi
