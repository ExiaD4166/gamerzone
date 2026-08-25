from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import decode_access_token
from app.db.redis import is_token_blacklisted
from app.db.session import get_session
from app.models.user import User

# Annotated[Type, Depends(...)] bundles "what you get" with "how to get it" into one
# reusable alias. Every endpoint that needs a database session just declares
# `session: SessionDep` instead of repeating Depends(get_session) everywhere.
# Shared dependencies live here so routers don't redefine them.
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Pulls the token out of the `Authorization: Bearer <token>` header, and returns 401
# automatically if the header is missing. tokenUrl doesn't affect that behaviour - it
# tells /docs which endpoint to call when you press "Authorize", so the Swagger UI can
# log in for you.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    """Resolve the caller's identity from their token.

    This is a chained dependency: FastAPI first resolves oauth2_scheme (header ->
    token string) and SessionDep (a database session), then runs this function with
    both. Any endpoint declaring CurrentUserDep gets that whole chain for free.

    The database lookup is not redundant: a token is a snapshot from up to 30 minutes
    ago, so the account it names may since have been deleted or deactivated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        # Required by the HTTP spec for 401s, and tells clients which scheme to use.
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    jti = payload.get("jti")
    if jti is None or await is_token_blacklisted(jti):
        # Signature and expiry are fine, but this token was explicitly revoked at
        # logout. Without this check a copied token would keep working until it
        # expired, because a JWT carries no server-side state of its own.
        raise credentials_exception

    try:
        user_id = int(payload.get("sub", ""))
    except ValueError:
        raise credentials_exception from None

    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    # A password change invalidates every session that predates it. The blacklist
    # revokes one token at a time; this revokes all of them at once, which is what a
    # password reset needs - it must not leave an intruder's session alive.
    issued_at = payload.get("iat")
    if user.password_changed_at is not None and issued_at is not None:
        if issued_at < user.password_changed_at.timestamp():
            raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_verified_user(current_user: CurrentUserDep) -> User:
    """Require a confirmed email address.

    Signing in is not enough for member content: anyone can type someone else's
    address at signup, so an unverified account hasn't actually proven it owns it.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address to access this content.",
        )
    return current_user


VerifiedUserDep = Annotated[User, Depends(get_current_verified_user)]


async def get_current_superuser(current_user: VerifiedUserDep) -> User:
    """Require an administrator.

    The last link in the chain: token -> active user -> verified email -> admin. By
    the time this runs everything else has been checked, so all that's left is the
    permission test. Building on VerifiedUserDep rather than CurrentUserDep keeps the
    levels strictly nested - an admin is always also a verified member.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires administrator privileges.",
        )
    return current_user


SuperUserDep = Annotated[User, Depends(get_current_superuser)]
