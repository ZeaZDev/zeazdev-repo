from __future__ import annotations

from fastapi import Depends, FastAPI, Header, Request
from pydantic import BaseModel, Field

from .auth import mint_jwt, require_role
from .ledger import user_balance
from .stripe_webhook import process_payment_intent_succeeded, verify_signature
from .wallet import credit_wallet, debit_wallet

app = FastAPI(title="ZEA Z Enterprise API")


class WalletCreditRequest(BaseModel):
    user_id: str
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=16)
    reference: str
    idempotency_key: str


class WalletDebitRequest(BaseModel):
    user_id: str
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=16)
    reference: str
    idempotency_key: str


class TokenRequest(BaseModel):
    user_id: str
    role: str = Field(pattern="^(admin|finance|user)$")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/auth/token")
def create_token(payload: TokenRequest) -> dict:
    return {"access_token": mint_jwt(payload.user_id, payload.role), "token_type": "bearer"}


@app.get("/wallet/balance/{user_id}/{currency}")
def wallet_balance(
    user_id: str,
    currency: str,
    principal: dict = Depends(require_role("user", "finance", "admin")),
) -> dict:
    _ = principal
    return {"user_id": user_id, "currency": currency.upper(), "balance": user_balance(user_id, currency)}


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


@app.post("/wallet/debit")
def wallet_debit(
    payload: WalletDebitRequest,
    principal: dict = Depends(require_role("finance", "admin")),
) -> dict:
    _ = principal
    return debit_wallet(
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
