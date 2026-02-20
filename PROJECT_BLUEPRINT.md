# 🧠 ZEA Z ENTERPRISE PLATFORM — FULL BLUEPRINT

ด้านล่างคือ **FULL PROJECT BLUEPRINT (Enterprise-grade)** ในรูปแบบ **Markdown ทั้งหมด**
ออกแบบให้ใช้เป็น **Prompt / Spec / Architecture Doc / Implementation Guide** ได้ทันที
ครอบคลุมตั้งแต่ **แนวคิด → โครงสร้าง → อัลกอริทึม → Infra → Security → Ops**

> เอกสารนี้ตั้งใจให้เป็น **Single Source of Truth**
> ใช้ได้ทั้งกับ AI, ทีม Dev, Auditor, และ Infra

---

## 1. Vision & Scope

### 1.1 Goal

สร้างแพลตฟอร์ม **Enterprise FinTech + Web3** ที่:

- มี Wallet (Fiat + Crypto)
- รองรับ Payment จริง (Stripe / Omise / Crypto)
- มี Ledger ที่ Audit-ready (SOC2)
- รองรับ On-chain confirmation + reorg
- มี Admin Dashboard + RBAC
- ติดตั้งได้แบบ **One-click / Idempotent**
- รองรับ WSL / VM / Bare-metal / Cloud

---

## 2. High-Level Architecture

```text
┌──────────────┐
│ React Admin  │  ← RBAC / JWT
└──────┬───────┘
       │ HTTPS
┌──────▼──────────────────────────┐
│ FastAPI API (Gunicorn + Uvicorn) │
│ - Auth / RBAC                    │
│ - Wallet / Ledger                │
│ - Stripe Webhook                 │
│ - Admin APIs                     │
└──────┬───────────────┬───────────┘
       │               │
       │               │
┌──────▼───────┐   ┌───▼───────────┐
│ PostgreSQL   │   │ Chain Worker   │
│ - Ledger     │   │ - RPC          │
│ - Audit Log  │   │ - Confirm      │
└──────────────┘   └────────────────┘
```

---

## 3. Technology Stack

### 3.1 Backend

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Server:** Gunicorn + UvicornWorker
- **Auth:** JWT (HS256)
- **ORM:** SQLAlchemy (Core)
- **Migrations:** Safe-Init (idempotent)

### 3.2 Frontend (Admin)

- **Framework:** React
- **Admin:** React-Admin
- **Auth:** JWT
- **RBAC:** Role-based resource permission

### 3.3 Database

- **Engine:** PostgreSQL 16
- **Connection:**
  - Unix Socket (preferred)
  - TCP 127.0.0.1 fallback
- **Schema:** Ledger-centric (append-only)

### 3.4 Payments

- **Stripe:** Live mode ready
- **Webhook:** Signature verification
- **Idempotency:** Header-based

### 3.5 Blockchain

- **Network:** EVM compatible
- **RPC:** Configurable (Infura / Ankr / Alchemy)
- **Worker:** Background systemd service
- **Confirm Depth:** Configurable
- **Reorg Handling:** Finality check

### 3.6 Ops / Infra

- **Init:** Bash Meta Generator
- **Service:** systemd
- **Monitoring:** Prometheus (future)
- **Logging:** Structured + Audit

---

## 4. Repository / File Structure

```text
zeaz/
├── app/
│   ├── main.py               # API entry
│   ├── auth.py               # JWT + RBAC
│   ├── wallet.py             # Wallet logic
│   ├── ledger.py             # Ledger core
│   ├── stripe_webhook.py     # Stripe verify
│   ├── chain_worker.py       # On-chain worker
│   ├── db.py                 # DB engine
│   └── migrate.py            # Safe migration
│
├── ui/
│   └── admin/
│       ├── src/
│       └── authProvider.ts
│
├── infra/
│   ├── systemd/
│   │   ├── zeaz-api.service
│   │   └── zeaz-chain.service
│   └── nginx/
│
├── profiles/
│   └── prod.env
│
└── install.sh
```

---

## 5. Core Domain Models

### 5.1 User

```text
User
- id (string)
- role (admin | finance | user)
```

### 5.2 Ledger (Append-Only)

```text
LedgerEntry
- id (bigserial)
- user_id
- amount (+/-)
- currency
- reference (stripe_id | tx_hash)
- idempotency_key (unique)
- type (credit | debit | stripe | onchain)
- created_at
```

> ❗ ไม่มี UPDATE / DELETE → Audit-safe

---

## 6. Wallet Algorithm (Critical)

### 6.1 Credit / Debit (Idempotent)

```pseudo
function apply_entry(user, amount, currency, idem_key):
    if ledger.exists(idem_key):
        return OK (duplicate ignored)

    insert ledger(user, amount, currency, idem_key)
```

### 6.2 Balance Calculation

```sql
SELECT SUM(amount)
FROM ledger
WHERE user_id = :user
```

> ❗ ไม่มี balance column → ไม่มี drift

---

## 7. Stripe Payment Flow

### 7.1 Charge

1. Client → `/wallet/credit`
2. Create PaymentIntent (server)
3. Return client_secret

### 7.2 Webhook (Source of Truth)

```pseudo
verify stripe signature
if event == payment_intent.succeeded:
    ledger_add(+amount, currency, stripe_id)
```

> ❗ Ledger update **เฉพาะ webhook**
> ไม่เชื่อ client

---

## 8. On-Chain Flow

### 8.1 Worker Loop

```pseudo
while true:
    latest_block = rpc.block_number
    for tx in pending:
        if confirmations >= CONFIRM_DEPTH:
            ledger_add(+amount, tx_hash)
    sleep
```

### 8.2 Reorg Handling

- Confirm only after depth
- Ignore orphan blocks
- Idempotency via tx_hash

---

## 9. Auth & RBAC

### 9.1 JWT Payload

```json
{
  "sub": "user_id",
  "role": "admin",
  "exp": 9999999999
}
```

### 9.2 RBAC Matrix

| Role    | Wallet | Ledger | Admin |
| ------- | ------ | ------ | ----- |
| user    | read   | read   | ❌    |
| finance | write  | read   | ❌    |
| admin   | full   | full   | full  |

---

## 10. systemd Services

### 10.1 API

- Restart always
- Depends on PostgreSQL
- Health endpoint `/healthz`

### 10.2 Chain Worker

- Independent
- Restart always
- No HTTP exposure

---

## 11. Installer (Meta Generator Philosophy)

### 11.1 Principles

- Idempotent
- Detect > Decide > Apply
- No hard assumption
- Socket-aware DB

### 11.2 Flow

```text
Install packages
Ensure PG cluster
Detect socket/TCP
Write env
Create venv
Install deps
Run migration
Start services
Health check
```

---

## 12. Security & Compliance

### 12.1 SOC2 Mapping

- Ledger → CC1 / CC7
- Idempotency → Integrity
- Webhook verify → Trust boundary
- No mutable balances

### 12.2 Secrets

- ENV only
- Ready for Vault / KMS

---

## 13. Testing Strategy

### 13.1 E2E

- JWT login
- Wallet credit (idempotent)
- Stripe test webhook
- Chain confirmation

### 13.2 Failure Tests

- Duplicate webhook
- Reorg simulation
- DB reconnect

---

## 14. Upgrade Path

- Docker / K8s
- Terraform + Cloudflare
- Multi-region DB
- Prometheus / Grafana
- SOC2 Type II Report

---

## 15. Definition of “DONE”

- ✅ Ledger consistent
- ✅ Wallet idempotent
- ✅ Stripe reconciled
- ✅ Chain confirmed
- ✅ Admin controlled
- ✅ Installer rerunnable

---

### 🔚 END OF BLUEPRINT

ถ้าคุณต้องการ:

- แปลง Blueprint นี้เป็น **AI Prompt Template**
- แตกเป็น **Spec ต่อทีม (Backend / Frontend / Infra)**
- หรือ **SOC2 / Audit Document**

บอกผมได้เลยว่าจะ “แตกเอกสารระดับไหน” ต่อครับ
