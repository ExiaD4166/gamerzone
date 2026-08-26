from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Keeping the algorithm behind this module means a future change to what counts as
# best practice touches only this file.
_password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str | int) -> str:
    """Build a signed JWT identifying `subject` (our user id).

    The payload is base64-encoded, not encrypted - anyone holding the token can read
    it, so nothing confidential goes in. The signature is what makes it trustworthy.

    `jti` identifies this individual token, so logout can revoke one session without
    touching the user's others; `iat` lets a password change invalidate every token
    issued before it in a single comparison.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Verify a token's signature and expiry, returning its claims, or None.

    A forged, tampered or expired token all raise PyJWTError, and all mean the same
    thing to a caller, so they collapse into None.
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
