from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Tambahkan path agar alembic bisa menemukan model.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from model import Base  # Base dari model.py

# ----------------------------------------------------
# Alembic Config
# ----------------------------------------------------
config = context.config

# If alembic.ini has sqlalchemy.url, use it
if config.get_main_option("sqlalchemy.url") is None:
    config.set_main_option(
        "sqlalchemy.url",
        os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/indotrader")
    )

# Interpret config file for Python logging.
fileConfig(config.config_file_name)

# Target Metadata – memastikan autogenerate migration membaca models
target_metadata = Base.metadata

# ----------------------------------------------------
# Run Migration Offline
# ----------------------------------------------------
def run_migrations_offline():
    """Run migrations without DB connection (offline mode)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ----------------------------------------------------
# Run Migration Online
# ----------------------------------------------------
def run_migrations_online():
    """Run migrations with DB connection (online mode)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,        # detect type changes
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# ----------------------------------------------------
# Entrypoint
# ----------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
