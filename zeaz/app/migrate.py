from __future__ import annotations

from .db import engine, metadata


def migrate() -> None:
    metadata.create_all(bind=engine, checkfirst=True)


if __name__ == "__main__":
    migrate()
