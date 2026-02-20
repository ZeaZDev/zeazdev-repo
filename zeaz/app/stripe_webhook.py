from __future__ import annotations

import hmac
import os
from hashlib import sha256

from fastapi import HTTPException, status

from .ledger import LedgerEntryInput, append_entry

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec-change-me")


def _extract_v1(signature: str) -> str:
    if "=" not in signature:
        return signature
    parts = [p.strip() for p in signature.split(",")]
    for part in parts:
        if part.startswith("v1="):
            return part.removeprefix("v1=")
    return ""


def verify_signature(payload: bytes, signature: str | None) -> None:
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe signature")

    expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), payload, sha256).hexdigest()
    provided = _extract_v1(signature)
    if not provided or not hmac.compare_digest(expected, provided):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature")


def process_payment_intent_succeeded(event: dict) -> bool:
    data = event.get("data", {}).get("object", {})
    stripe_id = str(data.get("id", "")).strip()
    currency = str(data.get("currency", "")).strip().upper()
    amount = int(data.get("amount_received", 0))
    user_id = str(data.get("metadata", {}).get("user_id", "unknown")).strip()

    if not stripe_id or not currency or amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment_intent payload")

    return append_entry(
        LedgerEntryInput(
            user_id=user_id,
            amount=amount,
            currency=currency,
            reference=stripe_id,
            idempotency_key=f"stripe:{stripe_id}",
            entry_type="stripe",
        )
    )
