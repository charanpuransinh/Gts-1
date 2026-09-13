def calculate_pivot_points(high: float, low: float, close: float) -> dict:
    """Standard Floor Pivot Points Calculation"""
    p = (high + low + close) / 3.0
    r1 = (2 * p) - low
    s1 = (2 * p) - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    r3 = high + 2 * (p - low)
    s3 = low - 2 * (high - p)

    return {
        'P': p,
        'R1': r1, 'S1': s1,
        'R2': r2, 'S2': s2,
        'R3': r3, 'S3': s3
    }
