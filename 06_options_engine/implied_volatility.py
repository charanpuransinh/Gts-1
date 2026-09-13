import math


def calculate_implied_volatility(price: float, spot: float, strike: float, time_to_expiry_years: float,
                                   rate: float = 0.05, option_type: str = 'CE') -> float:
    """Fast Brenner-Subrahmanyam style IV approximation (best near ATM; used here as a quick
    Termux-friendly fallback rather than a full Newton-Raphson solve)."""
    if time_to_expiry_years <= 0 or price <= 0:
        return 0.0
    intrinsic = max(0.0, spot - strike) if option_type == 'CE' else max(0.0, strike - spot)
    time_val = price - intrinsic
    if time_val <= 0:
        return 0.05
    iv = (time_val / (spot * 0.398 * math.sqrt(time_to_expiry_years)))
    return max(0.01, min(iv, 5.0))
