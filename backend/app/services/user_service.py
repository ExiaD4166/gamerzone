from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_password, verify_password
from app.core.tokens import password_fingerprint, verify_password_reset_token
from app.models.user import User, UserCreate

# NOTE: raising HTTPException from the service layer is a pragmatic FastAPI-specific
# shortcut. The stricter pattern is to raise domain errors here and translate them to
# HTTP in the router / a global handler - planned for the error-handling phase.


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.exec(select(User).where(User.email == email))
    return result.first()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.exec(select(User).where(User.username == username))
    return result.first()


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """Return the user if these credentials are valid, otherwise None.

    Deliberately returns the same None for "no such email" and "wrong password".
    Telling them apart would let an attacker probe which emails are registered
    (user enumeration), so the caller reports one identical error for both.
    """
    user = await get_user_by_email(session, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def reset_password(session: AsyncSession, token: str, new_password: str) -> bool:
    """Apply a password reset. Returns False if the token isn't usable.

    Three things must hold: the token has to be genuine, unexpired and minted for this
    purpose; it has to name a real account; and its fingerprint has to still match that
    account's current password. The last check is what makes a token single-use -
    completing a reset changes the hash, so the fingerprint stops matching and neither
    this token nor any other outstanding one can be replayed.
    """
    result = verify_password_reset_token(token)
    if result is None:
        return False
    email, fingerprint = result

    user = await get_user_by_email(session, email)
    if user is None:
        return False

    if fingerprint != password_fingerprint(user.hashed_password):
        return False

    user.hashed_password = hash_password(new_password)
    # Recorded so get_current_user can refuse tokens issued before this instant,
    # signing the account out of every device.
    user.password_changed_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    return True


async def mark_email_verified(session: AsyncSession, user: User) -> User:
    """Flip the account to verified. Idempotent: clicking the link twice is harmless."""
    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    """Register a new account: reject duplicates, hash the password, store the user."""
    if await get_user_by_email(session, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    if await get_user_by_username(session, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken.",
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        # The checks above can still lose a race: two identical signups arriving at
        # the same moment both pass, then both insert. The UNIQUE constraint in
        # Postgres is the real guarantee, so we translate its error into the same
        # clean 409 rather than letting it surface as a 500.
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email or username already exists.",
        ) from None

    await session.refresh(user)
    return user
