import pandas as pd
from .atr import calculate_atr


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
    """Supertrend Indicator Calculation"""
    atr = calculate_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2

    basic_upper = hl2 + (multiplier * atr)
    basic_lower = hl2 - (multiplier * atr)

    final_upper = pd.Series(0.0, index=df.index)
    final_lower = pd.Series(0.0, index=df.index)
    supertrend = pd.Series(0.0, index=df.index)
    direction = pd.Series(1, index=df.index)

    for i in range(1, len(df)):
        if basic_upper.iloc[i] < final_upper.iloc[i - 1] or df['close'].iloc[i - 1] > final_upper.iloc[i - 1]:
            final_upper.iloc[i] = basic_upper.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        if basic_lower.iloc[i] > final_lower.iloc[i - 1] or df['close'].iloc[i - 1] < final_lower.iloc[i - 1]:
            final_lower.iloc[i] = basic_lower.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i - 1]

        if df['close'].iloc[i] > final_upper.iloc[i]:
            direction.iloc[i] = 1
        elif df['close'].iloc[i] < final_lower.iloc[i]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        supertrend.iloc[i] = final_lower.iloc[i] if direction.iloc[i] == 1 else final_upper.iloc[i]

    return pd.DataFrame({
        'supertrend': supertrend,
        'direction': direction
    })
