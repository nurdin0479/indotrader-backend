from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Import internal modules
from db import get_db, Base, engine
from app.auth.auth import router as auth_router
from app.crud.crud_signal import create_signal, get_signals
from app.schemas import SignalCreate, SignalResponse
from services.market_data import (
    get_indodax_ticker,
    get_indodax_orderbook,
    convert_binance_orderbook_to_idr,
    get_ohlcv_binance,
)

# Init app terlebih dahulu
app = FastAPI(title="Server NBFSOFT", version="1.0")

# Register router
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Create DB tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Indotrader Server is running 🚀"}


# ORDERBOOK
@app.get("/orderbook/indodax/{symbol}")
def orderbook_indodax(symbol: str, limit: int = 50):
    return get_indodax_orderbook(f"{symbol.lower()}_idr", limit=limit)


@app.get("/orderbook/binance/{symbol}")
def orderbook_binance(symbol: str, limit: int = 50):
    return convert_binance_orderbook_to_idr(symbol.upper(), limit=limit)


# CHART
@app.get("/chart/binance/{symbol}")
def chart_binance(symbol: str, interval: str = "1m", limit: int = 500):
    return get_ohlcv_binance(symbol.upper(), interval=interval, limit=limit)


# SIGNAL
@app.post("/signal/", response_model=SignalResponse)
def create_signal_api(data: SignalCreate, db: Session = Depends(get_db)):
    return create_signal(db, data)


@app.get("/signal/", response_model=list[SignalResponse])
def get_signals_api(db: Session = Depends(get_db)):
    return get_signals(db)


# MARKET
@app.get("/market/{symbol}")
def get_market_data(symbol: str):
    indodax_data = get_indodax_ticker(f"{symbol.lower()}_idr")
    binance_data = convert_binance_orderbook_to_idr(symbol.upper(), limit=10)

    return {
        "symbol": symbol.upper(),
        "indodax": indodax_data,
        "binance": binance_data,
    }
