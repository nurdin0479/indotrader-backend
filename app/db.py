# app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Expect DATABASE_URL in environment (e.g. in .env used by docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://indotrader:trader123@db:5432/tradingdb")


# Use pool_pre_ping to avoid stale connections in dockerized env
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI dependency to provide DB session
def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()
