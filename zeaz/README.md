# ZEA Z Project Scaffold

This scaffold was generated from `PROJECT_BLUEPRINT.md` and mirrors the documented structure:

- `app/` FastAPI API, auth/RBAC, wallet/ledger, webhook, chain worker
- `ui/admin/` React-Admin placeholder with JWT auth provider
- `infra/systemd/` API and chain worker units
- `infra/nginx/` reverse-proxy example
- `profiles/prod.env` runtime environment template
- `install.sh` idempotent setup bootstrap

## Quick start

```bash
cd zeaz
./install.sh
```


## New automation APIs

- `POST /tiktok/feed-product-form/generate` — automated feed product form generation for TikTok Shop showcase.
- `POST /tiktok/video/generate` — automated product video generation job creation.
- `POST /tiktok/shop-affiliate/upload` — automated TikTok Shop affiliate upload job creation.
- `GET /tiktok/jobs` and `GET /tiktok/jobs/{job_id}` — inspect generated automation jobs.
- `GET /admin/control-panel` and `GET /user/control-panel` — admin/user control panel API data.

## Admin UI additions

The React-Admin app now includes:
- Admin Control Panel
- User Control Panel
- Generate Feed Product Form
- Generate Product Video
- Upload TikTok Shop Aff
- TikTok Jobs list
