import hashlib

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

_serializer = URLSafeTimedSerializer(settings.secret_key)

# The salt scopes a token to ONE purpose: a verification link cannot be replayed
# against password reset, or the other way round. Every new purpose gets its own.
EMAIL_VERIFICATION_SALT = "email-verification"
PASSWORD_RESET_SALT = "password-reset"


def generate_email_verification_token(email: str) -> str:
    return _serializer.dumps(email, salt=EMAIL_VERIFICATION_SALT)


def verify_email_verification_token(token: str) -> str | None:
    """Return the email a valid token was issued for, or None.

    Forged, expired and wrong-purpose tokens all mean "don't trust this", so they
    collapse into one answer.
    """
    max_age = settings.email_verification_expire_hours * 3600
    try:
        email = _serializer.loads(token, salt=EMAIL_VERIFICATION_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return email if isinstance(email, str) else None


def password_fingerprint(hashed_password: str) -> str:
    """A short, one-way marker of a specific stored password.

    Reset tokens are readable by anyone who sees the URL, so the hash itself must never
    go inside one. This digest reveals nothing but changes the moment the password does.
    """
    return hashlib.sha256(hashed_password.encode()).hexdigest()[:16]


def generate_password_reset_token(email: str, hashed_password: str) -> str:
    """Create the token for a password-reset link.

    Carrying the password's fingerprint is what makes the link single-use: completing a
    reset changes the hash, so this token - and any other outstanding one - stops
    matching, without a record of issued tokens being stored anywhere.
    """
    payload = {"email": email, "fp": password_fingerprint(hashed_password)}
    return _serializer.dumps(payload, salt=PASSWORD_RESET_SALT)


def verify_password_reset_token(token: str) -> tuple[str, str] | None:
    """Return (email, fingerprint) from a valid reset token, or None.

    The fingerprint still has to be checked against the user's current password; that
    needs the database, so it happens in the service layer.
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
