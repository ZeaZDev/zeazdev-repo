from __future__ import annotations

from fastapi import Depends, FastAPI, Header, Request
from pydantic import BaseModel, Field

from .auth import require_role
from .stripe_webhook import process_payment_intent_succeeded, verify_signature
from .wallet import credit_wallet

app = FastAPI(title="ZEA Z Enterprise API")


class WalletCreditRequest(BaseModel):
    user_id: str
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=16)
    reference: str
    idempotency_key: str


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/wallet/credit")
def wallet_credit(
    payload: WalletCreditRequest,
    principal: dict = Depends(require_role("finance", "admin")),
) -> dict:
    _ = principal
    return credit_wallet(
        user_id=payload.user_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        reference=payload.reference,
        idempotency_key=payload.idempotency_key,
    )


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None, alias="Stripe-Signature")) -> dict:
    raw = await request.body()
    verify_signature(raw, stripe_signature)
    event = await request.json()

    inserted = False
    if event.get("type") == "payment_intent.succeeded":
        inserted = process_payment_intent_succeeded(event)

    return {"received": True, "inserted": inserted}
