def analyze_price_data(prices: list[float]) -> dict:
    if not prices:
        return {"signal": "neutral", "confidence": 0.0}
    last = prices[-1]
    avg = sum(prices[-5:]) / 5 if len(prices) >= 5 else sum(prices) / len(prices)
    if last > avg:
        return {"signal": "buy", "confidence": 0.7}
    elif last < avg:
        return {"signal": "sell", "confidence": 0.7}
    return {"signal": "neutral", "confidence": 0.5}
