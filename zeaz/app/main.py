from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator

from .auth import mint_jwt, require_role
from .ledger import user_balance
from .stripe_webhook import process_payment_intent_succeeded, verify_signature
from .tiktok_affiliate import (
    create_feed_product_form,
    create_product_video,
    get_job,
    list_jobs,
    upload_to_tiktok_affiliate,
)
from .wallet import credit_wallet, debit_wallet

app = FastAPI(title="ZEA Z Enterprise API")


class WalletRequestBase(BaseModel):
    user_id: str
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=16)
    reference: str
    idempotency_key: str

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.strip().upper()


class WalletCreditRequest(WalletRequestBase):
    pass


class WalletDebitRequest(WalletRequestBase):
    pass


class TokenRequest(BaseModel):
    user_id: str
    role: str = Field(pattern="^(admin|finance|user)$")


class FeedProductFormRequest(BaseModel):
    product_id: str
    title: str
    price: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=16)
    highlights: list[str] = Field(default_factory=list)


class ProductVideoRequest(BaseModel):
    product_id: str
    script_style: str = Field(default="conversion")
    duration_seconds: int = Field(default=20, ge=5, le=180)


class TiktokUploadRequest(BaseModel):
    job_reference: str
    shop_id: str
    creator_handle: str


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
    return {"user_id": user_id, "currency": currency.strip().upper(), "balance": user_balance(user_id, currency)}


@app.post("/wallet/credit")
def wallet_credit(
    payload: WalletCreditRequest,
    principal: dict = Depends(require_role("finance", "admin")),
) -> dict:
    _ = principal
    return credit_wallet(
        user_id=payload.user_id,
        amount=payload.amount,
        currency=payload.currency,
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
        currency=payload.currency,
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


@app.post("/tiktok/feed-product-form/generate")
def generate_feed_product_form(
    payload: FeedProductFormRequest,
    principal: dict = Depends(require_role("finance", "admin")),
) -> dict:
    _ = principal
    return create_feed_product_form(
        product_id=payload.product_id,
        title=payload.title,
        price=payload.price,
        currency=payload.currency,
        highlights=payload.highlights,
    )


@app.post("/tiktok/video/generate")
def generate_product_video(
    payload: ProductVideoRequest,
    principal: dict = Depends(require_role("finance", "admin")),
) -> dict:
    _ = principal
    return create_product_video(
        product_id=payload.product_id,
        script_style=payload.script_style,
        duration_seconds=payload.duration_seconds,
    )


@app.post("/tiktok/shop-affiliate/upload")
def upload_tiktok_shop_affiliate(
    payload: TiktokUploadRequest,
    principal: dict = Depends(require_role("finance", "admin")),
) -> dict:
    _ = principal
    return upload_to_tiktok_affiliate(
        job_reference=payload.job_reference,
        shop_id=payload.shop_id,
        creator_handle=payload.creator_handle,
    )


@app.get("/tiktok/jobs")
def get_tiktok_jobs(principal: dict = Depends(require_role("finance", "admin"))) -> dict:
    _ = principal
    return {"data": list_jobs()}


@app.get("/tiktok/jobs/{job_id}")
def get_tiktok_job(job_id: str, principal: dict = Depends(require_role("finance", "admin"))) -> dict:
    _ = principal
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job_not_found")
    return job


@app.get("/admin/control-panel")
def admin_control_panel(principal: dict = Depends(require_role("admin"))) -> dict:
    return {
        "id": "admin",
        "role": principal.get("role"),
        "status": "ok",
        "managed_features": [
            "wallet",
            "ledger",
            "tiktok_feed_form_generator",
            "tiktok_video_generator",
            "tiktok_shop_affiliate_upload",
        ],
        "job_count": len(list_jobs()),
    }


@app.get("/user/control-panel")
def user_control_panel(principal: dict = Depends(require_role("user", "finance", "admin"))) -> dict:
    return {
        "id": principal.get("sub", "user"),
        "role": principal.get("role"),
        "status": "ok",
        "available_actions": ["view_balance", "view_jobs"],
    }
