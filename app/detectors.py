# app/detectors.py
from typing import List, Dict, Any
import statistics
import math

def moving_average(prices: List[float], window: int) -> List[float]:
    if len(prices) < window:
        return []
    ma = []
    for i in range(window - 1, len(prices)):
        ma.append(sum(prices[i-window+1:i+1]) / window)
    return ma

def detect_pump_dump(ohlcv: List[List[Any]], pump_threshold: float = 0.10, window: int = 5) -> Dict[str,Any]:
    """
    Detect pump/dump by % change over 'window' candles using close price.
    pump_threshold = 0.10 means 10% increase -> pump
    """
    if not ohlcv or len(ohlcv) < window+1:
        return {"status": "unknown", "reason": "not enough data"}
    closes = [float(candle[4]) for candle in ohlcv]
    start = closes[-(window+1)]
    end = closes[-1]
    pct = (end - start) / start if start else 0.0
    if pct >= pump_threshold:
        return {"status": "pump", "pct": pct}
    if pct <= -pump_threshold:
        return {"status": "dump", "pct": pct}
    return {"status": "none", "pct": pct}

def detect_stagnant(ohlcv: List[List[Any]], threshold: float = 0.02, window: int = 20) -> Dict[str,Any]:
    """If max-min over window is within threshold fraction, consider stagnant"""
    if not ohlcv or len(ohlcv) < window:
        return {"status": "unknown", "reason": "not enough data"}
    closes = [float(candle[4]) for candle in ohlcv[-window:]]
    maxi = max(closes); mini = min(closes)
    frac = (maxi-mini)/((maxi+mini)/2) if (maxi+mini) else 0.0
    if frac <= threshold:
        return {"status": "stagnant", "range_frac": frac}
    return {"status": "active", "range_frac": frac}

def detect_sideway(ohlcv: List[List[Any]], ma_window: int = 20, std_threshold: float = 0.01) -> Dict[str,Any]:
    """Sideway: small volatility around MA; check stddev of returns"""
    if not ohlcv or len(ohlcv) < ma_window:
        return {"status": "unknown", "reason": "not enough data"}
    closes = [float(c[4]) for c in ohlcv[-ma_window:]]
    returns = []
    for i in range(1, len(closes)):
        if closes[i-1]:
            returns.append((closes[i]-closes[i-1]) / closes[i-1])
    if not returns:
        return {"status": "unknown", "reason": "no returns"}
    std = statistics.pstdev(returns)
    if std <= std_threshold:
        return {"status": "sideway", "std": std}
    return {"status": "trend", "std": std}

def detect_breakout(ohlcv: List[List[Any]], lookback:int=50, breakout_mult:float=0.015) -> Dict[str,Any]:
    """Detect breakout if last close > previous high * (1 + breakout_mult)"""
    if not ohlcv or len(ohlcv) < lookback+1:
        return {"status": "unknown", "reason": "not enough data"}
    closes = [float(c[4]) for c in ohlcv]
    prev_high = max(closes[-(lookback+1):-1])
    last = closes[-1]
    if prev_high and last > prev_high * (1 + breakout_mult):
        return {"status": "breakout", "last": last, "prev_high": prev_high}
    if prev_high and last < prev_high * (1 - breakout_mult):
        return {"status": "below_resistance", "last": last, "prev_high": prev_high}
    return {"status": "no_breakout", "last": last, "prev_high": prev_high}

def simple_support_resistance(ohlcv: List[List[Any]], window:int=50) -> Dict[str,Any]:
    """
    Very simple SR detection:
    - support ~ local minima clusters
    - resistance ~ local maxima clusters
    Return top support and resistance as average of last few min/max.
    """
    if not ohlcv or len(ohlcv) < window:
        return {"reason": "not enough data"}
    closes = [float(c[4]) for c in ohlcv[-window:]]
    highs = [float(c[2]) for c in ohlcv[-window:]]
    lows = [float(c[3]) for c in ohlcv[-window:]]
    # support ~ average of lowest 3 closes
    supports = sorted(lows)[:3]
    resistances = sorted(highs, reverse=True)[:3]
    support = sum(supports)/len(supports)
    resistance = sum(resistances)/len(resistances)
    return {"support": support, "resistance": resistance}
