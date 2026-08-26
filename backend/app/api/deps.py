from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import decode_access_token
from app.db.redis import is_token_blacklisted
from app.db.session import get_session
from app.models.user import User

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# tokenUrl doesn't affect validation - it tells /docs which endpoint the Authorize
# button should call.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    """Resolve the caller's identity from their token.

    Checks run cheapest first: signature and expiry, then Redis, then the database.

    The database lookup is not redundant - a token is a snapshot from up to thirty
    minutes ago, and the account it names may since have been deleted or deactivated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Signature and expiry can both be fine on a token that was revoked at logout;
    # a JWT carries no server-side state of its own to say so.
    jti = payload.get("jti")
    if jti is None or await is_token_blacklisted(jti):
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

    # The blacklist revokes one token; this revokes every session predating a password
    # change at once, so a reset cannot leave an intruder signed in.
    issued_at = payload.get("iat")
    if user.password_changed_at is not None and issued_at is not None:
        if issued_at < user.password_changed_at.timestamp():
            raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_verified_user(current_user: CurrentUserDep) -> User:
    """Require a confirmed address: anyone can type someone else's at signup."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address to access this content.",
        )
    return current_user


VerifiedUserDep = Annotated[User, Depends(get_current_verified_user)]


async def get_current_superuser(current_user: VerifiedUserDep) -> User:
    """Require an administrator.

    Built on VerifiedUserDep rather than CurrentUserDep so the levels stay strictly
    nested: an admin is always also a verified member.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires administrator privileges.",
        )
    return current_user


SuperUserDep = Annotated[User, Depends(get_current_superuser)]
