from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import database
from app.db import get_db, Base, engine

# Auth Router
from app.auth.auth import router as auth_router

# CRUD Signal
from app.crud.crud_signal import create_signal, get_signals

# Schemas
from app.schemas import SignalCreate, SignalResponse

# Services (Market Data)
from app.services.market_data import (
    get_indodax_ticker,
    get_indodax_orderbook,
    convert_binance_orderbook_to_idr,
    get_ohlcv_binance,
)

# Inisialisasi App
app = FastAPI(title="Server NBFSOFT", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Register Router
app.include_router(auth_router, prefix="/auth", tags=["Auth"])


# ───────────────────────────────────────────────
# ROUTES UTAMA
# ───────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Indotrader Server is running 🚀"}


# ORDERBOOK
@app.get("/orderbook/indodax/{symbol}")
def orderbook_indodax(symbol: str, limit: int = 50):
    pair = f"{symbol.lower()}_idr"
    return get_indodax_orderbook(pair, limit=limit)


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
    indodax = get_indodax_ticker(f"{symbol.lower()}_idr")
    binance = convert_binance_orderbook_to_idr(symbol.upper(), limit=10)

    return {
        "symbol": symbol.upper(),
        "indodax": indodax,
        "binance": binance,
    }
