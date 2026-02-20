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
