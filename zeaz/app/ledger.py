from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from .db import audit_log, db_connection, ledger


@dataclass(frozen=True)
class LedgerEntryInput:
    user_id: str
    amount: int
    currency: str
    reference: str
    idempotency_key: str
    entry_type: str


def _normalize_currency(currency: str) -> str:
    normalized = currency.strip().upper()
    if len(normalized) < 3 or len(normalized) > 16:
        raise ValueError("currency must be between 3 and 16 characters")
    return normalized


def _write_audit(actor: str, action: str, details: str) -> None:
    with db_connection() as conn:
        conn.execute(audit_log.insert().values(actor=actor, action=action, details=details))


def append_entry(entry: LedgerEntryInput) -> bool:
    """Append a ledger row once. Returns True when inserted, False when duplicate."""
    if entry.amount == 0:
        raise ValueError("amount cannot be zero")

    normalized_currency = _normalize_currency(entry.currency)

    with db_connection() as conn:
        try:
            conn.execute(
                ledger.insert().values(
                    user_id=entry.user_id,
                    amount=entry.amount,
                    currency=normalized_currency,
                    reference=entry.reference,
                    idempotency_key=entry.idempotency_key,
                    type=entry.entry_type,
                )
            )
        except IntegrityError:
            return False

    _write_audit(
        actor=entry.user_id,
        action="ledger.append",
        details=f"type={entry.entry_type} amount={entry.amount} currency={normalized_currency} ref={entry.reference}",
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
