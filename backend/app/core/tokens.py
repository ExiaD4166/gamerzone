import hashlib

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

# Reuses the app's SECRET_KEY, so these tokens are signed the same way JWTs are:
# readable by anyone, but impossible to forge or alter without the key.
_serializer = URLSafeTimedSerializer(settings.secret_key)

# The salt scopes a token to ONE purpose. A token minted for email verification will
# not validate when loaded with a different salt, so a future password-reset flow
# cannot be attacked by replaying a verification link (or the other way round).
# Each new token purpose gets its own salt constant here.
EMAIL_VERIFICATION_SALT = "email-verification"
PASSWORD_RESET_SALT = "password-reset"


def generate_email_verification_token(email: str) -> str:
    """Create the URL-safe token that goes in the verification link.

    "Timed" means the current time is baked into the token, which is how
    verify_email_verification_token can later reject one that's too old - no database
    record of issued tokens is needed.
    """
    return _serializer.dumps(email, salt=EMAIL_VERIFICATION_SALT)


def verify_email_verification_token(token: str) -> str | None:
    """Return the email a valid token was issued for, or None.

    Three separate failures all mean "don't trust this": the signature doesn't match
    (forged or tampered), the token is older than max_age (expired), or it was minted
    for a different purpose (wrong salt). Callers only need "valid" vs "not".
    """
    max_age = settings.email_verification_expire_hours * 3600
    try:
        email = _serializer.loads(token, salt=EMAIL_VERIFICATION_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return email if isinstance(email, str) else None


def password_fingerprint(hashed_password: str) -> str:
    """A short, one-way marker of a specific stored password.

    Reset tokens are readable by anyone who sees the URL, so the password hash itself
    must never go inside one. This digest reveals nothing about the hash, but changes
    completely the moment the password does - which is exactly what makes a used reset
    token stop working.
    """
    return hashlib.sha256(hashed_password.encode()).hexdigest()[:16]


def generate_password_reset_token(email: str, hashed_password: str) -> str:
    """Create the token for a password-reset link.

    Carries the fingerprint of the password it was issued against, so completing a
    reset silently invalidates this token (and any other outstanding one) without
    storing a record of issued tokens anywhere.
    """
    payload = {"email": email, "fp": password_fingerprint(hashed_password)}
    return _serializer.dumps(payload, salt=PASSWORD_RESET_SALT)


def verify_password_reset_token(token: str) -> tuple[str, str] | None:
    """Return (email, fingerprint) from a valid reset token, or None.

    Rejects a forged/tampered token, one older than max_age, and one minted for a
    different purpose (different salt). The caller still has to check the fingerprint
    against the user's current password - that check needs the database, so it lives
    in the service layer.
    """
    max_age = settings.password_reset_expire_minutes * 60
    try:
        payload = _serializer.loads(token, salt=PASSWORD_RESET_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None

    if not isinstance(payload, dict):
        return None
    email, fingerprint = payload.get("email"), payload.get("fp")
    if not isinstance(email, str) or not isinstance(fingerprint, str):
        return None
    return email, fingerprint
