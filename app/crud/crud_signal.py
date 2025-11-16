from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from db import Base
from schemas import SignalCreate

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    signal_type = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_signal(db: Session, data: SignalCreate):
    signal = Signal(**data.dict())
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal

def get_signals(db: Session):
    return db.query(Signal).order_by(Signal.created_at.desc()).limit(10).all()
