from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from db import Base  # <-- sesuai struktur /app/db.py
from model import Admin, User  # pastikan model terdaftar

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata
