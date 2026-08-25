from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# PasswordHash.recommended() picks the algorithm currently considered best practice
# (Argon2id). Keeping it behind this module means that when the recommendation
# changes, only this file changes - nothing else in the app knows or cares which
# algorithm is in use.
_password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Turn a plain password into a storable hash.

    The result is one-way: there is no function anywhere that converts it back.
    A random salt is generated per call and embedded in the returned string, so
    two users with the same password still get completely different hashes.
    """
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a login attempt against a stored hash.

    The stored hash carries its own salt and parameters, so this re-hashes the
    attempt the same way and compares - the original password is never recovered.
    """
    return _password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str | int) -> str:
    """Build a signed JWT identifying `subject` (our user id).

    The payload is only base64-encoded, NOT encrypted - anyone can read it. What
    makes it trustworthy is the signature, computed with SECRET_KEY: change a single
    character of the payload and the signature no longer matches, so the token is
    rejected. Never put anything confidential in here.

    `sub`, `exp`, `iat` and `jti` are registered JWT claims; `exp` is enforced by
    PyJWT itself. `jti` is a unique id for this individual token - it's what logout
    puts on the blacklist, so revoking one token doesn't touch the user's other
    sessions. `iat` records when the token was minted, which lets a password change
    invalidate every token issued before it in one comparison.
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

    jwt.decode() does the real work: it recomputes the signature with SECRET_KEY and
    rejects the token if it doesn't match (tampered/forged), and it also rejects an
    expired one. Both failures raise PyJWTError, which we turn into None so callers
    only have to handle "valid" vs "not valid".

    Returns the whole payload rather than just the subject, because callers now need
    `jti` (to check revocation) and `exp` (to size the blacklist entry) as well.
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
