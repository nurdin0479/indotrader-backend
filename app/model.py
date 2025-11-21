# app/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from db import Base


class Admin(Base):
__tablename__ = "admins"


id = Column(Integer, primary_key=True, index=True)
email = Column(String(255), unique=True, index=True, nullable=False)
password = Column(String(255), nullable=False) # store hashed password
full_name = Column(String(255), nullable=True)
is_super = Column(Boolean, default=False)
created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
__tablename__ = "users"


id = Column(Integer, primary_key=True, index=True)
email = Column(String(255), unique=True, index=True, nullable=False)
password = Column(String(255), nullable=False) # store hashed password
full_name = Column(String(255), nullable=True)
telegram_token = Column(String(500), nullable=True)
telegram_enabled = Column(Boolean, default=False)
created_at = Column(DateTime, default=datetime.utcnow)


class Signal(Base):
__tablename__ = "signals"


id = Column(Integer, primary_key=True, index=True)
symbol = Column(String(64), index=True, nullable=False)
signal_type = Column(String(64), nullable=False)
confidence = Column(Float, nullable=True)
created_at = Column(DateTime, default=datetime.utcnow)
