from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_password, verify_password
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
