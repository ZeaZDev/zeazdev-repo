from __future__ import annotations

from .ledger import LedgerEntryInput, append_entry, user_balance


def credit_wallet(
    user_id: str,
    amount: int,
    currency: str,
    reference: str,
    idempotency_key: str,
) -> dict:
    inserted = append_entry(
        LedgerEntryInput(
            user_id=user_id,
            amount=amount,
            currency=currency,
            reference=reference,
            idempotency_key=idempotency_key,
            entry_type="credit",
        )
    )
    return {
        "inserted": inserted,
        "balance": user_balance(user_id, currency),
    }


def debit_wallet(
    user_id: str,
    amount: int,
    currency: str,
    reference: str,
    idempotency_key: str,
) -> dict:
    current = user_balance(user_id, currency)
    if amount > current:
        return {"inserted": False, "balance": current, "error": "insufficient_funds"}

    inserted = append_entry(
        LedgerEntryInput(
            user_id=user_id,
            amount=-amount,
            currency=currency,
            reference=reference,
            idempotency_key=idempotency_key,
            entry_type="debit",
        )
    )
    return {
        "inserted": inserted,
        "balance": user_balance(user_id, currency),
    }
