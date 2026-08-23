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
