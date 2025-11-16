# app/services/market_data.py

import requests
from typing import Dict, Any, List

# -------------------------------------------------------------------
# BASE URLs
# -------------------------------------------------------------------
INDODAX_BASE = "https://indodax.com/api"
BINANCE_BASE = "https://api.binance.com/api/v3"

# -------------------------------------------------------------------
# GLOBAL SESSION (lebih cepat)
# -------------------------------------------------------------------
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Indotrader/1.0"})


# -------------------------------------------------------------------
# INDODAX API
# -------------------------------------------------------------------
def get_indodax_ticker(symbol_idr: str) -> Dict[str, Any]:
    """symbol_idr example: 'btc_idr'"""
    try:
        res = SESSION.get(f"{INDODAX_BASE}/ticker/{symbol_idr}", timeout=6)
        res.raise_for_status()
        d = res.json()["ticker"]
        return {
            "exchange": "indodax",
            "symbol": symbol_idr,
            "last": float(d["last"]),
            "high": float(d["high"]),
            "low": float(d["low"]),
            "vol": float(d.get("vol_idr") or d.get("vol")),
            "raw": d,
        }
    except Exception as e:
        return {"error": str(e)}


def get_indodax_orderbook(symbol_idr: str, limit: int = 50) -> Dict[str, Any]:
    """Indodax depth API → returns asks/bids"""
    try:
        res = SESSION.get(f"{INDODAX_BASE}/{symbol_idr}/depth", timeout=6)
        res.raise_for_status()
        d = res.json()
        asks = d.get("asks", [])[:limit]
        bids = d.get("bids", [])[:limit]
        return {
            "exchange": "indodax",
            "symbol": symbol_idr,
            "asks": asks,
            "bids": bids,
        }
    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------------------------
# BINANCE API (USDT market)
# -------------------------------------------------------------------
def get_binance_ticker(symbol: str) -> Dict[str, Any]:
    """Get simple price ticker, e.g. BTCUSDT"""
    try:
        res = SESSION.get(f"{BINANCE_BASE}/ticker/price", params={"symbol": symbol}, timeout=6)
        res.raise_for_status()
        data = res.json()
        return {
            "exchange": "binance",
            "symbol": symbol,
            "price": float(data["price"]),
        }
    except Exception as e:
        return {"error": str(e)}


def get_binance_price_usdt(symbol: str) -> Dict[str, Any]:
    """Get price for {symbol}USDT (symbol example: 'BTC')"""
    return get_binance_ticker(f"{symbol}USDT")


def get_binance_orderbook_usdt(symbol: str, limit: int = 50) -> Dict[str, Any]:
    """Return orderbook for SYMBOL + USDT (e.g 'BTCUSDT')"""
    try:
        res = SESSION.get(
            f"{BINANCE_BASE}/depth",
            params={"symbol": f"{symbol}USDT", "limit": limit},
            timeout=6,
        )
        res.raise_for_status()
        data = res.json()
        return {
            "exchange": "binance",
            "symbol": symbol + "USDT",
            "asks": data.get("asks", []),
            "bids": data.get("bids", []),
        }
    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------------------------
# CONVERSION USDT → IDR
# -------------------------------------------------------------------
def get_usdt_idr_rate() -> float:
    """Get USDT → IDR rate from Indodax"""
    try:
        res = SESSION.get(f"{INDODAX_BASE}/ticker/usdt_idr", timeout=6)
        res.raise_for_status()
        data = res.json()["ticker"]
        return float(data["last"])
    except Exception:
        return 0.0  # fallback, lebih baik error ke client


def convert_binance_orderbook_to_idr(symbol: str, limit: int = 50) -> Dict[str, Any]:
    """Fetch binance orderbook then convert all prices from USDT → IDR"""
    ob = get_binance_orderbook_usdt(symbol, limit=limit)
    if "error" in ob:
        return ob

    rate = get_usdt_idr_rate()
    if not rate:
        return {"error": "failed to get USDT->IDR rate"}

    def convert(rows: List[List[str]]):
        return [[float(price) * rate, float(qty)] for price, qty in rows]

    return {
        "exchange": "binance",
        "symbol": f"{symbol}_idr",
        "asks": convert(ob["asks"]),
        "bids": convert(ob["bids"]),
    }


# -------------------------------------------------------------------
# OHLCV / KLINE
# -------------------------------------------------------------------
def get_ohlcv_binance(symbol: str, interval: str = "1m", limit: int = 500) -> Dict[str, Any]:
    """
    Get kline candles from Binance (e.g. BTCUSDT)
    Returns 2D-array: [ [open_time, open, high, low, close, volume, ...], ... ]
    """
    try:
        res = SESSION.get(
            f"{BINANCE_BASE}/klines",
            params={"symbol": f"{symbol}USDT", "interval": interval, "limit": limit},
            timeout=8,
        )
        res.raise_for_status()
        data = res.json()
        return {
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval,
            "ohlcv": data,
        }
    except Exception as e:
        return {"error": str(e)}
