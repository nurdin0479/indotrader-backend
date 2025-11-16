# app/worker.py
import os
import time
import json
import requests
from datetime import datetime
from services.market_data import get_ohlcv_binance, convert_binance_orderbook_to_idr, get_indodax_orderbook, get_indodax_ticker
from detectors import detect_pump_dump, detect_stagnant, detect_sideway, detect_breakout, simple_support_resistance
from db import SessionLocal, Base, engine
from crud.crud_signal import Signal  # reuse model class
from sqlalchemy.orm import Session

# ENV
SYMBOLS = os.getenv("SYMBOLS", "BTC,ETH").split(",")  # e.g. BTC,ETH,SOL
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))  # seconds
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=6)
        r.raise_for_status()
    except Exception as e:
        print("Telegram send error:", e)

def save_signal(db: Session, symbol: str, signal_type: str, confidence: float):
    s = Signal(symbol=symbol, signal_type=signal_type, confidence=confidence)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def run_loop():
    print("Worker started. Poll interval:", POLL_INTERVAL, "symbols:", SYMBOLS)
    while True:
        try:
            for sym in SYMBOLS:
                sym = sym.strip().upper()
                # get ohlcv from Binance
                ohlcv_res = get_ohlcv_binance(sym, interval="1m", limit=200)
                if "error" in ohlcv_res:
                    print("OHLC error:", ohlcv_res)
                    continue
                ohlcv = ohlcv_res["ohlcv"]

                # detectors
                pumpdump = detect_pump_dump(ohlcv, pump_threshold=0.07, window=5)
                stagnant = detect_stagnant(ohlcv, threshold=0.02, window=30)
                sideway = detect_sideway(ohlcv, ma_window=20, std_threshold=0.008)
                breakout = detect_breakout(ohlcv, lookback=50, breakout_mult=0.01)
                sr = simple_support_resistance(ohlcv, window=50)

                messages = []
                if pumpdump.get("status") in ("pump", "dump"):
                    text = f"<b>{sym}</b> detected {pumpdump['status'].upper()} ({pumpdump['pct']*100:.2f}%)"
                    messages.append(text)
                if stagnant.get("status") == "stagnant":
                    messages.append(f"<b>{sym}</b> stagnant (range {stagnant.get('range_frac')*100:.2f}%)")
                if sideway.get("status") == "sideway":
                    messages.append(f"<b>{sym}</b> sideway (std {sideway.get('std'):.5f})")
                if breakout.get("status") == "breakout":
                    messages.append(f"<b>{sym}</b> breakout! last {breakout['last']}, prev_high {breakout['prev_high']}")
                if sr.get("support") and sr.get("resistance"):
                    messages.append(f"<b>{sym}</b> support {sr['support']:.0f}, resistance {sr['resistance']:.0f}")

                # Save & notify
                db = SessionLocal()
                try:
                    for m in messages:
                        # Save a signal row
                        # simple classification: use first word in message as signal_type
                        if "pump" in m.lower():
                            t = "pump"
                        elif "dump" in m.lower():
                            t = "dump"
                        elif "breakout" in m.lower():
                            t = "breakout"
                        elif "stagnant" in m.lower() or "sideway" in m.lower():
                            t = "stagnant/sideway"
                        else:
                            t = "info"
                        s = save_signal(db, sym, t, confidence=0.5)
                        send_telegram(f"{m}\nID: {s.id} time: {s.created_at}")
                finally:
                    db.close()

            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print("Worker loop error:", e)
            time.sleep(5)

if __name__ == "__main__":
    run_loop()
