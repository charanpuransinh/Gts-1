import math
import random
import importlib

_mu = importlib.import_module("04_indicators.math_utils")
norm_pdf, norm_cdf = _mu.norm_pdf, _mu.norm_cdf


class OptionsPricingModels:
    """Black-Scholes-Merton, Binomial Tree (American) & Monte Carlo Engine — Pure Python"""

    @staticmethod
    def black_scholes_merton(spot, strike, time_to_expiry_years, rate, iv, dividend_yield=0.0, option_type='CE'):
        if time_to_expiry_years <= 0 or iv <= 0:
            return max(0.0, spot - strike) if option_type.upper() in ['CE', 'CALL'] else max(0.0, strike - spot)
        d1 = (math.log(spot / strike) + (rate - dividend_yield + 0.5 * iv ** 2) * time_to_expiry_years) / (iv * math.sqrt(time_to_expiry_years))
        d2 = d1 - iv * math.sqrt(time_to_expiry_years)
        if option_type.upper() in ['CE', 'CALL']:
            price = spot * math.exp(-dividend_yield * time_to_expiry_years) * norm_cdf(d1) - strike * math.exp(-rate * time_to_expiry_years) * norm_cdf(d2)
        else:
            price = strike * math.exp(-rate * time_to_expiry_years) * norm_cdf(-d2) - spot * math.exp(-dividend_yield * time_to_expiry_years) * norm_cdf(-d1)
        return float(round(price, 4))

    @staticmethod
    def binomial_tree_american(spot, strike, time_to_expiry_years, rate, iv, steps=50, option_type='CE'):
        dt = time_to_expiry_years / steps
        u = math.exp(iv * math.sqrt(dt)); d = 1.0 / u
        p = (math.exp(rate * dt) - d) / (u - d)
        discount = math.exp(-rate * dt)
        is_call = option_type.upper() in ['CE', 'CALL']
        prices = [spot * (u ** (steps - i)) * (d ** i) for i in range(steps + 1)]
        values = [max(0.0, pv - strike) if is_call else max(0.0, strike - pv) for pv in prices]
        optimal_exercise_step = steps
        for j in range(steps - 1, -1, -1):
            for i in range(j + 1):
                current_spot = spot * (u ** (j - i)) * (d ** i)
                continuation_val = discount * (p * values[i] + (1 - p) * values[i + 1])
                intrinsic_val = max(0.0, current_spot - strike) if is_call else max(0.0, strike - current_spot)
                if intrinsic_val > continuation_val:
                    values[i] = intrinsic_val
                    optimal_exercise_step = j
                else:
                    values[i] = continuation_val
        fugit_time_years = (optimal_exercise_step / steps) * time_to_expiry_years
        return {"american_price": float(round(values[0], 4)), "fugit_optimal_exercise_years": float(round(fugit_time_years, 4)), "optimal_step": optimal_exercise_step}

    @staticmethod
    def monte_carlo_simulation(spot, strike, time_to_expiry_years, rate, iv, num_simulations=5000, option_type='CE'):
        is_call = option_type.upper() in ['CE', 'CALL']
        drift = (rate - 0.5 * (iv ** 2)) * time_to_expiry_years
        vol_sqrt_t = iv * math.sqrt(time_to_expiry_years)
        payoffs = []; itm_count = 0
        for _ in range(num_simulations):
            z = random.gauss(0, 1)
            s_t = spot * math.exp(drift + vol_sqrt_t * z)
            payoff = max(0.0, s_t - strike) if is_call else max(0.0, strike - s_t)
            payoffs.append(payoff)
            if (is_call and s_t > strike) or (not is_call and s_t < strike):
                itm_count += 1
        mc_price = math.exp(-rate * time_to_expiry_years) * (sum(payoffs) / num_simulations)
        pop_pct = (itm_count / num_simulations) * 100.0
        return {"mc_price": float(round(mc_price, 4)), "probability_of_profit_pct": float(round(pop_pct, 2))}
