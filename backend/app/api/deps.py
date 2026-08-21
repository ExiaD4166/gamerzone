from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import decode_access_token
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

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exception

    try:
        user_id = int(subject)
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

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_superuser(current_user: CurrentUserDep) -> User:
    """Require an administrator.

    Another link in the chain: this depends on get_current_user, which itself depends
    on the token and the session. By the time this runs, the caller is already known
    to be authenticated and active - all that's left is the permission check.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires administrator privileges.",
        )
    return current_user


SuperUserDep = Annotated[User, Depends(get_current_superuser)]
