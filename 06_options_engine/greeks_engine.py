import math
import importlib

_mu = importlib.import_module("04_indicators.math_utils")
norm_pdf, norm_cdf = _mu.norm_pdf, _mu.norm_cdf


class AllGreeksEngine:
    """Calculates all 17+1 First, Second & Third-Order Option Greeks (Pure Python)"""

    @staticmethod
    def calculate_all_greeks(spot: float, strike: float, time_to_expiry_years: float,
                              rate: float, iv: float, dividend_yield: float = 0.0,
                              option_type: str = 'CE', option_price: float = 1.0) -> dict:

        if time_to_expiry_years <= 0 or iv <= 0 or spot <= 0 or strike <= 0:
            return {k: 0.0 for k in [
                "delta", "vega", "theta", "rho", "lambda_elasticity", "epsilon", "phi",
                "gamma", "vanna", "charm", "vomma", "veta", "vera",
                "speed", "zomma", "color", "ultima", "parmicharma"
            ]}

        S = float(spot); K = float(strike); T = float(time_to_expiry_years)
        r = float(rate); q = float(dividend_yield); sigma = float(iv)
        is_call = option_type.upper() in ['CE', 'CALL']

        sqrt_T = math.sqrt(T)
        d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
        d2 = d1 - sigma * sqrt_T

        pdf_d1 = norm_pdf(d1)
        cdf_d1 = norm_cdf(d1)
        cdf_d2 = norm_cdf(d2)
        cdf_minus_d1 = norm_cdf(-d1)
        cdf_minus_d2 = norm_cdf(-d2)

        exp_minus_qt = math.exp(-q * T)
        exp_minus_rt = math.exp(-r * T)

        delta = exp_minus_qt * cdf_d1 if is_call else -exp_minus_qt * cdf_minus_d1
        vega = (S * exp_minus_qt * pdf_d1 * sqrt_T) / 100.0

        if is_call:
            theta_annual = (- (S * exp_minus_qt * pdf_d1 * sigma) / (2 * sqrt_T)
                            + q * S * exp_minus_qt * cdf_d1
                            - r * K * exp_minus_rt * cdf_d2)
            rho = (K * T * exp_minus_rt * cdf_d2) / 100.0
            epsilon = (-T * S * exp_minus_qt * cdf_d1) / 100.0
            phi = (T * S * exp_minus_qt * cdf_d1) / 100.0
        else:
            theta_annual = (- (S * exp_minus_qt * pdf_d1 * sigma) / (2 * sqrt_T)
                            - q * S * exp_minus_qt * cdf_minus_d1
                            + r * K * exp_minus_rt * cdf_minus_d2)
            rho = (-K * T * exp_minus_rt * cdf_minus_d2) / 100.0
            epsilon = (T * S * exp_minus_qt * cdf_minus_d1) / 100.0
            phi = (-T * S * exp_minus_qt * cdf_minus_d1) / 100.0

        theta = theta_annual / 365.0
        lambda_elasticity = (delta * S) / (option_price + 1e-9)

        gamma = (exp_minus_qt * pdf_d1) / (S * sigma * sqrt_T)
        vanna = (-exp_minus_qt * pdf_d1 * d2 / sigma) / 100.0

        if is_call:
            charm_annual = (q * exp_minus_qt * cdf_d1
                            - exp_minus_qt * pdf_d1 * (2 * (r - q) * T - d2 * sigma * sqrt_T) / (2 * T * sigma * sqrt_T))
        else:
            charm_annual = (-q * exp_minus_qt * cdf_minus_d1
                            - exp_minus_qt * pdf_d1 * (2 * (r - q) * T - d2 * sigma * sqrt_T) / (2 * T * sigma * sqrt_T))
        charm = charm_annual / 365.0

        vomma = (vega * d1 * d2 / sigma)
        veta = (-S * exp_minus_qt * pdf_d1 * sqrt_T * (q + ((r - q) * d1) / (sigma * sqrt_T) - (1 + d1 * d2) / (2 * T))) / (365.0 * 100.0)
        vera = (-K * T * exp_minus_rt * cdf_d2 * d1 / sigma) if is_call else (K * T * exp_minus_rt * cdf_minus_d2 * d1 / sigma)

        speed = - (gamma / S) * ((d1 / (sigma * sqrt_T)) + 1.0)
        zomma = gamma * ((d1 * d2 - 1.0) / sigma)
        color = (-gamma * (q + ((r - q) * d1) / (sigma * sqrt_T) + (1.0 - d1 * d2) / (2.0 * T))) / 365.0
        ultima = (-vomma / (sigma ** 2)) * (d1 * d2 * (1.0 - d1 * d2) + d1 ** 2 + d2 ** 2)
        parmicharma = charm / 365.0

        return {
            "delta": round(delta, 4), "vega": round(vega, 4), "theta": round(theta, 4),
            "rho": round(rho, 4), "lambda_elasticity": round(lambda_elasticity, 4),
            "epsilon": round(epsilon, 4), "phi": round(phi, 4),
            "gamma": round(gamma, 6), "vanna": round(vanna, 6), "charm": round(charm, 6),
            "vomma": round(vomma, 6), "veta": round(veta, 6), "vera": round(vera, 6),
            "speed": round(speed, 8), "zomma": round(zomma, 6), "color": round(color, 6),
            "ultima": round(ultima, 6), "parmicharma": round(parmicharma, 8)
        }
