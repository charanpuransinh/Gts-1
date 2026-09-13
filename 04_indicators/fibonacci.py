def calculate_fibonacci_levels(high: float, low: float) -> dict:
    """Fibonacci Retracement and Extension Levels"""
    diff = high - low
    return {
        "0.0%": low,
        "23.6%": low + 0.236 * diff,
        "38.2%": low + 0.382 * diff,
        "50.0%": low + 0.500 * diff,
        "61.8%": low + 0.618 * diff,
        "78.6%": low + 0.786 * diff,
        "100.0%": high,
        "161.8%": high + 0.618 * diff
    }
