from __future__ import annotations

import json
from pathlib import Path

from app.tiktok_affiliate import (
    create_feed_product_form,
    create_product_video,
    list_jobs,
    upload_to_tiktok_affiliate,
)


def generate_preview() -> dict:
    feed_job = create_feed_product_form(
        product_id="demo-sku-001",
        title="ZEA Z Smart Bottle",
        price=29.99,
        currency="usd",
        highlights=["24h cold", "Leak-proof", "Eco-friendly"],
    )
    video_job = create_product_video(
        product_id="demo-sku-001",
        script_style="conversion",
        duration_seconds=20,
    )
    upload_job = upload_to_tiktok_affiliate(
        job_reference=video_job["id"],
        shop_id="demo-shop-01",
        creator_handle="@zeaz_creator",
    )

    return {
        "project": "ZEA Z Enterprise API",
        "preview": {
            "automation_jobs": [feed_job, video_job, upload_job],
            "latest_jobs": list_jobs(),
            "api_endpoints": [
                "POST /auth/token",
                "GET /wallet/balance/{user_id}/{currency}",
                "POST /wallet/credit",
                "POST /wallet/debit",
                "POST /tiktok/feed-product-form/generate",
                "POST /tiktok/video/generate",
                "POST /tiktok/shop-affiliate/upload",
                "GET /tiktok/jobs",
                "GET /admin/control-panel",
                "GET /user/control-panel",
            ],
        },
    }


def main() -> None:
    preview = generate_preview()
    out_dir = Path("preview")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "project_preview.json"
    out_path.write_text(json.dumps(preview, indent=2))
    print(f"Preview generated: {out_path}")


if __name__ == "__main__":
    main()
