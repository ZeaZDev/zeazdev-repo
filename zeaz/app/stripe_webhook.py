from __future__ import annotations

import hmac
import os
from hashlib import sha256

from fastapi import HTTPException, status

from .ledger import LedgerEntryInput, append_entry

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec-change-me")


def verify_signature(payload: bytes, signature: str | None) -> None:
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe signature")
    expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), payload, sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature")


def process_payment_intent_succeeded(event: dict) -> bool:
    data = event["data"]["object"]
    amount = int(data["amount_received"])
    currency = str(data["currency"]).upper()
    stripe_id = str(data["id"])
    user_id = str(data.get("metadata", {}).get("user_id", "unknown"))

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
