from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from threading import Lock

_job_counter = count(1)
_jobs: dict[str, dict] = {}
_lock = Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _create_job(job_type: str, payload: dict, status: str = "queued") -> dict:
    with _lock:
        job_id = f"job_{next(_job_counter)}"
        job = {
            "id": job_id,
            "type": job_type,
            "status": status,
            "payload": payload,
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
        }
        _jobs[job_id] = job
        return job


def create_feed_product_form(product_id: str, title: str, price: float, currency: str, highlights: list[str]) -> dict:
    form_payload = {
        "product_id": product_id,
        "title": title,
        "price": price,
        "currency": currency.strip().upper(),
        "highlights": highlights,
        "description": f"{title} | {', '.join(highlights[:3])}",
    }
    return _create_job("tiktok_feed_form", form_payload, status="generated")


def create_product_video(product_id: str, script_style: str, duration_seconds: int) -> dict:
    video_payload = {
        "product_id": product_id,
        "script_style": script_style,
        "duration_seconds": duration_seconds,
        "storyboard": [
            "Hook: show product in first 3 seconds",
            "Benefit: highlight top feature",
            "CTA: check TikTok Shop link",
        ],
    }
    return _create_job("tiktok_video", video_payload, status="rendering")


def upload_to_tiktok_affiliate(job_reference: str, shop_id: str, creator_handle: str) -> dict:
    upload_payload = {
        "job_reference": job_reference,
        "shop_id": shop_id,
        "creator_handle": creator_handle,
        "platform": "tiktok_shop_affiliate",
    }
    return _create_job("tiktok_upload", upload_payload, status="uploaded")


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def list_jobs() -> list[dict]:
    return sorted(_jobs.values(), key=lambda item: item["id"], reverse=True)
