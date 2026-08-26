from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import (
    AccountAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidTokenError,
    UsernameAlreadyTakenError,
)
from app.core.security import hash_password, verify_password
from app.core.tokens import password_fingerprint, verify_password_reset_token
from app.models.user import User, UserCreate

# This layer raises domain errors, never HTTPException, so it stays usable outside a web
# request (CLI, background jobs). main.py registers the handlers that map them to HTTP.


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.exec(select(User).where(User.email == email))
    return result.first()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.exec(select(User).where(User.username == username))
    return result.first()


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """Return the user if these credentials are valid, otherwise None.

    Deliberately identical for "no such email" and "wrong password": telling them
    apart would let an attacker probe which addresses are registered.
    """
    user = await get_user_by_email(session, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
    """Apply a password reset, or raise InvalidTokenError.

    The fingerprint check is what makes a link single-use: completing a reset changes
    the hash, so neither this token nor any other outstanding one still matches.

    All three failures raise the same error, so the response can't reveal which.
    """
    result = verify_password_reset_token(token)
    if result is None:
        raise InvalidTokenError()
    email, fingerprint = result

    user = await get_user_by_email(session, email)
    if user is None:
        raise InvalidTokenError()

    if fingerprint != password_fingerprint(user.hashed_password):
        raise InvalidTokenError()

    user.hashed_password = hash_password(new_password)
    # get_current_user refuses tokens issued before this instant, which signs the
    # account out of every device.
    user.password_changed_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()


async def mark_email_verified(session: AsyncSession, user: User) -> User:
    """Idempotent, so clicking the link twice is harmless."""
    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    """Register a new account: reject duplicates, hash the password, store the user."""
    if await get_user_by_email(session, user_in.email):
        raise EmailAlreadyExistsError()
    if await get_user_by_username(session, user_in.username):
        raise UsernameAlreadyTakenError()

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        # The checks above lose a race when two identical signups arrive together:
        # both pass, then both insert. The UNIQUE constraint is the real guarantee,
        # so its error becomes the same clean 409 rather than a 500.
        await session.rollback()
        raise AccountAlreadyExistsError() from None

    await session.refresh(user)
    return user
