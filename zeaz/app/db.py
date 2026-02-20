from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
)

metadata = MetaData()

ledger = Table(
    "ledger",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("user_id", String(128), nullable=False, index=True),
    Column("amount", BigInteger, nullable=False),
    Column("currency", String(16), nullable=False),
    Column("reference", String(256), nullable=False),
    Column("idempotency_key", String(256), nullable=False, unique=True),
    Column("type", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

audit_log = Table(
    "audit_log",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("actor", String(128), nullable=False),
    Column("action", String(128), nullable=False),
    Column("details", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


def database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql+psycopg://zeaz:zeaz@127.0.0.1:5432/zeaz")


engine = create_engine(database_url(), pool_pre_ping=True)


@contextmanager
def db_connection():
    with engine.begin() as conn:
        yield conn
