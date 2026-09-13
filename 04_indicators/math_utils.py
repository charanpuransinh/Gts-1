import math


def norm_pdf(x: float) -> float:
    """Standard Normal Probability Density Function (Pure Python)"""
    return math.exp(-0.5 * (x ** 2)) / math.sqrt(2.0 * math.pi)


def norm_cdf(x: float) -> float:
    """Standard Normal Cumulative Distribution Function (Pure Python)"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
