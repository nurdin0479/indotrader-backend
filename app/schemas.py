



from pydantic import BaseModel
from datetime import datetime

class SignalBase(BaseModel):
    symbol: str
    signal_type: str
    confidence: float

class SignalCreate(SignalBase):
    pass

class SignalResponse(SignalBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
