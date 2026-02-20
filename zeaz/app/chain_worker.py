from __future__ import annotations

import os
import time

from .ledger import LedgerEntryInput, append_entry

CONFIRM_DEPTH = int(os.getenv("CHAIN_CONFIRM_DEPTH", "12"))
POLL_INTERVAL_SECONDS = int(os.getenv("CHAIN_POLL_SECONDS", "10"))


def process_confirmed_tx(tx_hash: str, user_id: str, amount: int, currency: str) -> bool:
    return append_entry(
        LedgerEntryInput(
            user_id=user_id,
            amount=amount,
            currency=currency,
            reference=tx_hash,
            idempotency_key=f"chain:{tx_hash}",
            entry_type="onchain",
        )
    )


def run() -> None:
    while True:
        # Placeholder for RPC polling and confirmation-depth checks.
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
