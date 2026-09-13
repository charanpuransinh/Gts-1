class PremiumAnalysis:
    """Evaluates option decay rate (Theta vs Premium)"""

    def evaluate_decay_yield(self, premium: float, theta: float) -> float:
        if premium <= 0:
            return 0.0
        return round((abs(theta) / premium) * 100.0, 2)
