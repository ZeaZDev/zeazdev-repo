from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select

from .db import db_connection, ledger


@dataclass(frozen=True)
class LedgerEntryInput:
    user_id: str
    amount: int
    currency: str
    reference: str
    idempotency_key: str
    entry_type: str


def append_entry(entry: LedgerEntryInput) -> bool:
    """Append a ledger row once. Returns True when inserted, False when duplicate."""
    with db_connection() as conn:
        existing = conn.execute(
            select(ledger.c.id).where(ledger.c.idempotency_key == entry.idempotency_key)
        ).scalar_one_or_none()
        if existing is not None:
            return False

        conn.execute(
            ledger.insert().values(
                user_id=entry.user_id,
                amount=entry.amount,
                currency=entry.currency,
                reference=entry.reference,
                idempotency_key=entry.idempotency_key,
                type=entry.entry_type,
            )
        )
    return True


def user_balance(user_id: str, currency: str) -> int:
    with db_connection() as conn:
        total = conn.execute(
            select(func.coalesce(func.sum(ledger.c.amount), 0)).where(
                ledger.c.user_id == user_id,
                ledger.c.currency == currency,
            )
        ).scalar_one()
    return int(total)
