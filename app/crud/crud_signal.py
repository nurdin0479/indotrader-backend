from sqlalchemy.orm import Session
from app.model import Signal
from app.schemas import SignalCreate

def create_signal(db: Session, data: SignalCreate):
    signal = Signal(**data.dict())
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal

def get_signals(db: Session):
    return db.query(Signal).order_by(Signal.created_at.desc()).limit(10).all()
