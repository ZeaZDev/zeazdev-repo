from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGO = "HS256"


def mint_jwt(user_id: str, role: str, ttl_minutes: int = 60) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


AuthHeader = Annotated[str | None, Header(alias="Authorization")]


def current_principal(auth_header: AuthHeader = None) -> dict:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return decode_jwt(auth_header.removeprefix("Bearer "))


def require_role(*allowed_roles: str):
    def _dependency(principal: dict = Depends(current_principal)) -> dict:
        if principal.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return principal

    return _dependency
