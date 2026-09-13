import pandas as pd
import numpy as np

class MultiAssetStrategyEngine:
    """Strategy Logic for Oil, Gas, Commodities, Indian Indices (0DTE) & US Tech Stocks"""

    @staticmethod
    def natural_gas_mean_reversion(df: pd.DataFrame, atr_multiplier: float = 2.0) -> dict:
        if df.empty or len(df) < 20:
            return {"signal": "NEUTRAL", "reason": "Insufficient Data"}
        last_close = df['close'].iloc[-1]
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'] - df['low']).mean()
        upper_band = sma_20 + (atr * atr_multiplier)
        lower_band = sma_20 - (atr * atr_multiplier)
        if last_close <= lower_band:
            return {"signal": "BUY_CALL", "entry": last_close, "stop_loss": last_close - (1.5 * atr), "target": sma_20}
        elif last_close >= upper_band:
            return {"signal": "BUY_PUT", "entry": last_close, "stop_loss": last_close + (1.5 * atr), "target": sma_20}
        return {"signal": "NEUTRAL", "reason": "Price within ATR bands"}

    @staticmethod
    def crude_oil_vwap_breakout(df: pd.DataFrame, volume_multiplier: float = 1.5) -> dict:
        if df.empty or 'vwap' not in df.columns or 'volume' not in df.columns:
            return {"signal": "NEUTRAL", "reason": "Missing VWAP or Volume"}
        last = df.iloc[-1]
        vol_avg = df['volume'].rolling(20).mean().iloc[-1]
        if last['close'] > last['vwap'] and last['volume'] > (vol_avg * volume_multiplier):
            return {"signal": "BUY_BULLISH_BREAKOUT", "entry": last['close'], "stop_loss": last['vwap']}
        elif last['close'] < last['vwap'] and last['volume'] > (vol_avg * volume_multiplier):
            return {"signal": "SELL_BEARISH_BREAKOUT", "entry": last['close'], "stop_loss": last['vwap']}
        return {"signal": "NEUTRAL", "reason": "No Volume Breakout"}

    @staticmethod
    def gold_dxy_correlation_setup(gold_price: float, dxy_change_pct: float, fib_0618_level: float) -> dict:
        if dxy_change_pct <= -0.2 and abs(gold_price - fib_0618_level) / fib_0618_level <= 0.005:
            return {"signal": "STRONG_BUY", "asset": "GOLD/SILVER", "reason": "DXY Weakness + 0.618 Fib Support"}
        elif dxy_change_pct >= 0.2 and abs(gold_price - fib_0618_level) / fib_0618_level <= 0.005:
            return {"signal": "STRONG_SELL", "asset": "GOLD/SILVER", "reason": "DXY Strength + Resistance"}
        return {"signal": "NEUTRAL", "asset": "GOLD/SILVER", "reason": "No DXY Sync"}

    @staticmethod
    def index_0dte_gex_pinning(spot: float, gex_flip: float, max_pain: float, current_time_str: str) -> dict:
        if spot > gex_flip and current_time_str >= "13:30":
            return {"strategy": "IRON_FLY_SHORT_STRADDLE", "center_strike": max_pain, "bias": "DELTA_NEUTRAL_PINNING", "reason": "Post 1:30 PM Charm Squeeze & High Gamma Pinning"}
        elif spot < gex_flip:
            return {"strategy": "DIRECTIONAL_PUT", "bias": "BEARISH_VOLATILE", "reason": "Below Gamma Flip Zone"}
        return {"strategy": "WAIT", "reason": "Awaiting 1:30 PM Expiry Trigger"}

    @staticmethod
    def stock_fno_vsa_breakout(df: pd.DataFrame) -> dict:
        if len(df) < 10:
            return {"signal": "NEUTRAL"}
        high_10d = df['high'].iloc[-11:-1].max()
        last_close = df['close'].iloc[-1]
        last_vol = df['volume'].iloc[-1]
        vol_avg_20d = df['volume'].rolling(20).mean().iloc[-1]
        if last_close > high_10d and last_vol >= (1.8 * vol_avg_20d):
            return {"signal": "HIGH_CONVICTION_BUY", "breakout_level": high_10d, "volume_surge": round(last_vol / vol_avg_20d, 2)}
        return {"signal": "NO_BREAKOUT"}

    @staticmethod
    def us_earnings_iv_crush(iv_rank: float, expected_move_pct: float) -> dict:
        if iv_rank > 80.0:
            return {"strategy": "DELTA_NEUTRAL_STRANGLE_SELL", "action": "SELL_HIGH_IV", "expected_crush": "HIGH", "max_risk_pct": expected_move_pct * 1.5}
        return {"strategy": "AVOID", "reason": "IV Rank too low for Earnings Crush"}

    @staticmethod
    def us_index_dex_scalp(dex_value: float, iv_trend: str) -> dict:
        if dex_value > 0 and iv_trend.upper() == "FALLING":
            return {"signal": "BULLISH_VANNA_SQUEEZE_SCALP", "timeframe": "5MIN", "bias": "BUY_CALL"}
        elif dex_value < 0 and iv_trend.upper() == "RISING":
            return {"signal": "BEARISH_DELTA_HEDGE_SCALP", "timeframe": "5MIN", "bias": "BUY_PUT"}
        return {"signal": "NO_SCALP_SIGNAL"}
